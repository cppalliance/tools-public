---
description: Write or audit a prompt, plan, tool, or rule file for unambiguous instructions and efficient context management
---

<!-- When given a target file, or asked to write one, run the Protocol (section 1). -->

# Prompt Rulebook

Rules for writing instructions that language models follow reliably, and for managing the tokens those instructions run in. Read this document to learn the craft; give it to a model to apply the craft. It governs any document whose reader is a model: a prompt, a plan, a tool file, a rule file, a subagent task.

![The Prompt Architect](images/how-to-write-prompts.png)

Two rules bind everything below:

1. Write every instruction so that only one reading is possible.
2. Spend the smallest set of high-signal tokens that makes the desired outcome likely.

Terms hold one sense throughout. The **target** is the document under work. An **agent** is a model plus its loop. The **context** is the set of tokens passed to the model at one turn. An **emitted artifact** is a file a tool writes for a reader who invokes it later on its own. Three budgets stay distinct, and none is ever shortened to "budget": the **constraint budget** counts hard rules binding at once (section 6), the **effort budget** caps work before stopping (section 7), and the **attention budget** counts tokens (section 9).

Write the target against these rules, then audit it against them one at a time. The rules are staged, not simultaneous, so the rulebook's size does not collide with the constraint budget it prescribes.

## 1. Protocol

Execute these steps in order when given a target:

1. Read the whole target before changing anything; when no target exists yet, write a draft first.
2. Name the target's kind, which selects what applies. A plan takes sections 2 through 7. A target that defines tools, spawns subagents, or runs unattended adds sections 8 and 9. A target that emits artifacts for later standalone use adds section 10.
3. Audit the target against every rule in the sections its kind selects.
4. Rewrite each violation in place. Preserve the author's intent, domain content, and voice; change how instructions are expressed, not what they aim at.
5. Resolve the conflicts the target's own wording settles. Flag the rest for the author, quoting both readings; leave flagged text unchanged rather than guessing.
6. Apply this rulebook recursively to instruction text the target contains or generates: a plan that builds a tool governs the tool's prompt; a prompt that spawns subagents governs each subagent task; a tool that emits tools governs what those tools emit, by section 10.
7. Return the target, and a change list when you were given an existing one, one line per change, each line naming the rule behind it.
8. Before returning, run the Checklist on your own result and fix what fails.

## 2. Specify

- Quantify every quantity: "3-5 bullets", not "a few points"; "under 200 words", not "brief".
- Define each fuzzy term at first use: "irrelevant" is undefined until the target says "irrelevant means anything outside topics A and B".
- Replace vague qualifiers with decision rules. "Appropriately", "as needed", and "when relevant" hand the decision back to the model; write "If X, do Y; if unsure, do Z".
- Cut brittleness: where the target enumerates branches the model could infer, and each new situation would need a new branch, replace the branch list with the heuristic that generated it.
- Cut vagueness: where the target would read as sound advice for any task, replace it with the signals, formats, and decision boundaries specific to this one.
- State each rule's scope. Models read literally and stop at the stated reach: "apply this format to every section, not only the first".
- Define edge-case behavior: "if no rows match, return an empty array and no explanation".
- Give every hard rule an escape hatch, one defined action for when its precondition fails: "if the file is missing, name it and stop". A hard rule with no escape hatch produces fabrication when reality refuses to cooperate.
- Ask for above-baseline effort in words: "include edge cases, error handling, and input validation". An unstated wish gets the minimal reading.
- Acceptance bar: a colleague with no prior knowledge of this project could execute the target without asking a question. Where they would ask, the model guesses.

## 3. Structure

- Separate instructions from data with named containers, and say what each holds: "the report is in <report> tags".
- Pick one markup convention per target, headings or tags, and keep it throughout. One exception: a block meant to be found by name and dispatched to a subagent gets a tag, whatever the surrounding convention (section 8).
- Keep instructions in prose and lists; reserve JSON for data records. Instruction text buried in JSON escaping is the worst-performing wrapper.
- Put one testable constraint on each line.
- Use bullets for parallel rules and numbers for sequences; a numbered list promises order.
- Load the edges: the opening and the ending are the best-attended positions, and the middle of a long target is the worst.
- Restate the binding rule at the end of any target longer than a page. Section 9 gives the runtime twin: an agent that runs many turns takes the same restatement back into its context on a fixed interval.
- Place each rule next to the content it governs; compliance decays with distance.
- Cut or omit every line whose removal changes no behavior. Each token competes with every other for attention.
- Fix typos and grammar before shipping; an error in a load-bearing keyword corrupts the output built on it.

## 4. Examples

- Show the format; a description of a format is a paraphrase, an example is a specification.
- Match each example to the desired output exactly, formatting included. The model copies what it sees over what it reads.
- When the output format matters, give 3-5 examples, diverse in content and balanced across labels or cases, ordered so the list does not end in a same-label run; the last example pulls hardest.
- Keep examples consistent with the rules. When rules and examples disagree, the model follows the examples.
- Curate diverse canonical examples instead of enumerating edge cases in prose. An edge-case list grows without bound and is paid on every request, while examples generalize to the cases you did not list.
- Mark counter-examples as wrong where they stand, and put the corrected version beside them; an unlabeled bad pattern still teaches.
- Specify output as a schema plus one filled example.
- Name the failure modes you exclude: "output only the JSON object: no preamble, no code fences, no commentary after".
- Order schemas so reasoning fields precede answer fields; a model forced to answer first writes its justification after the fact.

## 5. Voice

- Write instructions in imperative second person, present tense: "Extract the dates", not "The dates should be extracted".
- One instruction per sentence.
- Keep list items grammatically parallel; start each with a verb.
- Delete hedges. "Try to", "if possible", and "you may want to" turn an instruction into a suggestion; state the instruction plainly or cut it.
- Write in a neutral register: no courtesy padding, no emotional stakes, no tips, no threats. They spend tokens and buy no compliance.
- Use a persona to set voice and audience: "write as a sysadmin explaining to sysadmins". Skip personas aimed at accuracy; "you are a world-class expert" changes the register, not the correctness.
- Phrase rules as the desired behavior, and pair every prohibition with its replacement: "no markdown" becomes "write plain prose paragraphs, no markdown formatting".
- Keep a needed prohibition short, plain, and adjacent to what it governs. A vivid description of forbidden content primes the model to produce it; let the replacement carry the weight.
- Attach the reason to every non-obvious rule; a model generalizes from the reason and pattern-matches a bare rule. "Avoid ellipses" holds as written; "the output feeds a text-to-speech engine, so avoid ellipses, which it cannot pronounce" also steers the model away from every other unpronounceable symbol, unprompted.
- Use one term per concept for the whole target. A synonym reads as a new referent: an "endpoint" that becomes a "route" and then a "URL" is three things to the model.

## 6. Budgets and conflicts

- Count the constraint budget, the hard constraints the target imposes at once. Past six, joint compliance collapses; per-constraint failure rates multiply.
- Bring the count down by staging: split constraints across passes, move format constraints into the example, and delete the ones nothing depends on.
- Reserve NEVER, ALWAYS, and MUST for invariants, rules whose single violation is unacceptable, and cap them at three per target. Plain imperatives bind; this rulebook issues none.
- Write judgment calls as decision rules instead of absolutes: "search again only while the answer still lacks a citation".
- Check every pair of rules for conflict, and state a priority where two legitimately collide: "when brevity and completeness conflict here, completeness wins". An unresolved contradiction costs quality and latency while the model reconciles it.
- Move guarantees prose cannot deliver into code: schema validation, linters, banned-string checks. A prompt caps out at best-effort.
- Apply the detectability test to each rule: name what a violation would look like. A rule whose violation is unobservable ("be thoughtful", "reason carefully") is decoration; rewrite it as observable behavior or cut it.

## 7. Outcomes over procedures

- State the goal, the success criteria, and the stop condition, then let the model choose the path. A step-by-step procedure narrows the search space and goes stale with every model upgrade.
- Prescribe exact steps only where the sequence itself is the requirement: fragile pipelines, compliance rituals, destructive operations.
- Set effort budgets wherever wandering is possible: "at most two search calls before answering", "stop exploring once you can name the file to change".
- Cut chain-of-thought triggers. "Think step by step" adds latency on models that reason internally; state the quality bar and raise the effort setting instead.
- Start minimal on the strongest model available, run the task, then add only the instructions and examples that observed failures demand.
- Name the failure mode before adding tokens for it. An addition whose purpose went unstated is never removed.
- End hard tasks with self-verification against named criteria: "before returning, check the output against the three success criteria above and fix what fails".

## 8. Agents and tools

Apply this section when the target defines tools, spawns subagents, or runs unattended.

- Write each tool description in four parts: what it does, when to use it, when not to use it (and which sibling tool covers that case), and what each parameter means with its exact format.
- Apply the intern test: a newcomer given only the description could use the tool correctly; whatever they would ask is what the description is missing.
- Close open sets with enums, and make invalid parameter combinations unrepresentable.
- Give each tool a stop condition and an uncertainty threshold scaled to risk: a destructive action asks at the first doubt, a read-only action retries without asking.
- Write each subagent task self-contained: objective, output format, sources and tools, boundaries, effort budget. The subagent sees no conversation history and no sibling tasks; what the task omits, the subagent invents.
- Trace every artifact the target's pipeline must produce through every step that names it. Flag any artifact named as an input or an expected output but never commanded into existence by an imperative in some step. Reason: a step that references a section, file, or record no earlier step was told to create reads as satisfied while the artifact never appears, the failure mode that drops a named-but-uncreated section.
- Ship subagent task text verbatim from the tool's own template or specification. Do not paraphrase, summarize, augment, or rewrite the task before dispatch; any transformation between the tool's text and the dispatched prompt is a bug, because the tool author wrote the task for the subagent's context, not for the dispatcher's. The violation is usually involuntary: under context pressure the dispatcher compresses a large inline prompt, and the summary drops the quantified constraints, XML containers, and order-dependent numbered steps whose exact wording carries the task's analytical value. Reason: a prompt-engineered sequence breaks when reordered or shortened, so a task large enough to tempt compression must not travel in the prompt argument at all - the next rule moves it out.
- Inject a fixed block of the tool file into subagents by reference, not by copy: wrap the block in a uniquely named tag in the tool file, and give each subagent task the tool's path and the tag name with the instruction to grep for the tag and read the enclosed block. Keep the dispatched prompt small and fixed - the path, the tag name, and the run's few variable values - so the dispatcher holds nothing large enough to summarize; a prompt with no block in it cannot be compressed into one, a structural guarantee a "do not paraphrase" instruction cannot match. Copying the block into every task also re-emits it once per subagent, so a large block multiplies the dispatcher's output cost by the fan-out, while a tag reference costs one line and delivers the exact source text the ship-verbatim rule above requires. When the injected content is built at runtime rather than stored in the tool file, write it to one file and pass that path. If a subagent cannot read files, inline the block.
- Estimate the size of any work the target assembles from multiple files or subagent outputs, and route the assembly through the shell when the combined result would be large. When the sources already exist as files, direct the model to concatenate them with the shell instead of re-emitting their contents through a write call: a large payload sent as one tool-call argument arrives truncated or malformed, fails to parse, and forces a retry. Name the mechanism, not the command - "concatenate the sources with the shell", not a specific invocation - so the instruction survives across environments.
- Write standing rule files concrete enough to verify: "run `npm test` before committing", not "test your changes". One representative code snippet outperforms paragraphs of style description.
- Run the removal test on every standing instruction: delete or omit the line if its absence would change nothing. Standing text is paid on every request, and bloat teaches the model to skim.
- Budget the tool's return value, not only its description: return what the caller needs in order to act and omit the rest. A tool that hands back its full payload spends the caller's attention budget without the caller choosing to.
- Give the agent primitives that inspect large data without loading it: filtering, pagination, head and tail, targeted queries, and stored results.
- Apply the disambiguation test to the tool set: for each situation the agent faces, name the one correct tool. Where two tools both fit, merge them or state in each description which sibling covers that case. If a human engineer cannot definitively pick, the agent cannot do better.
- Cap the tool set at the minimum viable set, and remove any tool whose functionality another tool already covers. Every tool definition is paid on every turn, and a crowded set also creates the ambiguous decision points the test above catches.
- Cap each subagent's return at 1,000-2,000 tokens of distilled findings, however many tokens it consumed internally; when the findings do not compress that far, return the summary plus a path to the full text. This is the outbound half of the rule above: the dispatcher keeps its prompt small so it cannot compress the task, and the subagent returns small so the caller's context stays clean.

## 9. Context

Apply this section when the target defines tools, spawns subagents, or runs unattended. Sections 2 through 7 govern the words of one document; this section governs an agent's token state across a run.

**The attention budget.**

- Treat the context as an attention budget that depletes, not a container that fills. Recall accuracy falls as the token count rises, so a token added at position 100,000 weakens the model's grip on the token at position 500.
- Apply this to every model. Degradation rates differ; exemption does not exist.
- Test for the gradient rather than the cliff: measure retrieval precision and long-range reasoning as the context grows, instead of waiting for visible failure. Capability declines smoothly, so a design can be degraded and still look like it works.
- Build compaction, notes, or subagents now rather than waiting for a larger context window. Windows of every size stay subject to pollution and relevance decay.
- Extend the removal test of section 8 to the run: name the behavior each token source changes, and cut the source when you cannot name one. When you cannot tell, run the task once without it and compare.
- Keep a token the agent needs in order to act correctly, however long the result. Minimal does not mean short, and where brevity and sufficient specification conflict here, sufficient specification wins.

**The token economy.**

- Declare in the target what enters the main context and what never does, as two lists. The declaration is the artifact; without it, every rule below is a preference.
- Run a command in the main context only when the command bounds its own output independent of the state it reads. Dispatch everything whose output size depends on whether something went wrong. Tool output cannot be unread: a command returning two lines on success and four hundred on failure has already spent the attention budget by the time the caller learns which case it got.
- Recover rather than deny when a permitted command overruns anyway: finish the current step, record the state to a file, and start a fresh context that reads that record cold.

**Retrieval.**

- Keep identifiers in the context and payloads out: store paths, queries, and links, and load the contents through a tool at the moment of use.
- Pre-load a source when it is small, stable, and needed on every run; retrieve it just in time otherwise. When you cannot tell which it is, retrieve just in time and measure.
- Pre-load the instructions that bind every step, and retrieve only data just in time. An agent that loads on demand can otherwise act before it has read the rule governing the step.
- Prefer live navigation over a precomputed index when the underlying data changes between runs; an index goes stale and the agent cannot detect that it has.
- Name files and directories so the path alone states purpose. A `test_utils.py` in `tests/` implies something different from one in `src/core_logic/`, and the path costs nothing.
- Keep file sizes, names, and timestamps accurate. The agent infers complexity from size, purpose from name, and relevance from recency, so a misleading name misroutes it silently.
- Pair every grant of autonomy with heuristics and a stop condition. Without them the agent spends its attention budget misusing tools, chasing dead ends, and missing what mattered.

**Past one context window.**

- Compact when the context nears its limit: summarize, then restart from the summary. Name what survives, which is the decisions taken, the problems still open, and the working set of files, and name what does not.
- Give every compaction and truncation a quantified trigger, and clear consumed tool results first; a tool result already acted on is the cheapest thing to drop.
- Tune a compaction prompt on real traces: maximize recall first, then raise precision by cutting superfluous content. Where the two conflict here, recall wins, because dropped context is unrecoverable while superfluous content only costs tokens.
- Persist progress, decisions, and dependencies to a file outside the context at a fixed known path, and read it back after a reset. A path the agent has to search for is a path it will not find.
- Write every plan so a reader who did not see the conversation can execute it. A plan may cite a file path or a URL, because those resolve for any reader; it may not depend on anything said in the conversation that produced it. The violation is observable: hand the plan to a fresh context and count the questions it has to ask.
- Dispatch plan execution to a fresh context when the plan produces a large authored artifact, or when the conversation that produced the plan ran long. A context that wrote the plan covers its gaps from conversational memory instead of revealing them, so executing in place hides exactly the plan defects a fresh reader would surface.
- Restate the binding rules into the working context on a fixed step interval. This is the runtime form of loading the edges (section 3).
- Choose the technique by task shape: compaction for extended back-and-forth, notes for iterative work with clear milestones, subagents for exploration that parallelizes. They combine.
- Re-audit prescriptive scaffolding on every model upgrade and delete what the new model no longer needs. Yesterday's scaffolding is today's attention cost.

## 10. Propagation

Apply this section when the target emits an artifact meant to be invoked later on its own.

This rulebook is a build-time input, never a runtime dependency. Nothing it shapes cites it.

- Choose how a block travels by whether its reader shares this run and this filesystem. A subagent does, so dispatch its block by reference, the path and the tag name, per section 8. An emitted artifact does not, so write the rules into it as substance; a path does not resolve for a reader nobody handed it.
- Strip provenance from every emitted artifact: state the rule, name no source document for it.
- Carry the kernel below into every emitted artifact, adapted to that artifact's subject and vocabulary. Copy its substance, not its wording.
- Give every tool that emits artifacts a named emission-discipline block listing the constraints it applies before writing, and a generation checklist that verifies them. Put one line in that checklist confirming no emitted file names a source document for its rules.
- Carry this section too when an emitted artifact emits artifacts of its own. An artifact that emits nothing carries the kernel and stops there.

<propagation-kernel>
Wording:
- Write every rule as an imperative; one instruction per sentence.
- State every quantity as a number or a range.
- Give every hard rule one defined action for when its precondition fails.
- Pair every prohibition with the behavior that replaces it.
- Define what happens on the empty, missing, and malformed case.

Context:
- Declare what enters the main context and what never does.
- Run exploration in subagents; the main context holds the plan, the state, and the outcomes.
- Say what each subagent returns, and cap its size.
- Persist state outside the context at a fixed known path.
- Give every compaction a quantified trigger.
- Give every loop a stop condition and a progress test.
</propagation-kernel>

An emission-discipline block takes this shape:

```
## Emission Discipline

Every {artifact} passes these constraints before it is written. The
generated file never refers to any source document for these rules;
they appear only by their substance.

- Subagent-only exploration. The {artifact} never searches from its
  main context; its sideband subagent does.
- Bounded state. The {state record} is the sole sanctioned write, one
  line, compressed at 80 characters.
- Every check unambiguous, every quantity a number, every loop capped.
```

## Checklist

Run these checks on the finished target. Each answers yes or no; each no returns to its section.

- Every quantity is a number or a range. (2)
- No vague qualifier survives; each became a decision rule. (2)
- Every rule carries its scope, and edge cases have defined behavior. (2)
- Every hard rule has an escape hatch. (2)
- Instructions and data sit in separate, named containers. (3)
- Both binding rules appear near the start and again at the end. (3)
- Examples match the current rules exactly. (4)
- Every sentence is a command or a fact; no hedges. (5)
- Every prohibition carries its replacement. (5)
- Simultaneous hard constraints number six or fewer. (6)
- No two rules conflict without a stated priority. (6)
- Every rule's violation would be observable. (6)
- Every pipeline artifact is commanded into existence by an imperative, not just referenced. (8)
- Every large fixed subagent block is dispatched by tag-reference, and the dispatched prompt holds no summarizable block. (8)
- Every subagent return is capped and specified. (8)
- Every token source names a behavior it changes. (9)
- The target declares what enters the main context and what never does. (9)
- Every plan is executable by a reader who did not see the conversation that produced it. (9)
- Every command run in the main context bounds its own output. (9)
- Every compaction has a quantified trigger, and every loop has a stop condition. (9)
- No emitted artifact names a source document for its rules. (10)
- Every emitting tool carries an emission-discipline block and a generation checklist. (10)

Restated: write every instruction so that only one reading is possible, and spend the smallest set of high-signal tokens that makes the desired outcome likely.

*2026-07-08 - Claude Fable 5 (Cursor agent). Distilled from "How to write clear, concise, unambiguous instructions for LLMs" (research, 2026-07-08), which holds the evidence and sources.*

*2026-07-25 - Claude Opus 5 (Cursor agent). Sections 9 and 10 added from "Effective context engineering for AI agents" (Anthropic, 2025-09-29) and from the context rules recurring in this workspace's tool designs.*
