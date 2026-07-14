---
description: Audit and fix a prompt, plan, tool, or rule file for clarity, precision, and imperative voice
---

<!-- When given a target file, run the Protocol (section 1) against it. -->

# Prompt Rulebook

Rules for writing instructions that language models follow reliably. Read this document to learn the craft; give it to a model to apply the craft. It governs any document whose reader is a model: a prompt, a plan, a tool file, a rule file, a subagent task. The document under improvement is called the target. These rules are audit criteria, applied one at a time; they are not simultaneous generation constraints, so the rulebook's size does not collide with the constraint budget it prescribes.

## 1. Protocol

Execute these steps in order when given a target:

1. Read the whole target before changing anything.
2. Audit the target against every rule in sections 2 through 8. Section 8 applies when the target defines tools, spawns subagents, or runs unattended; skip it otherwise.
3. Rewrite each violation in place. Preserve the author's intent, domain content, and voice; change how instructions are expressed, not what they aim at.
4. Resolve the conflicts the target's own context settles. Flag the rest for the author, quoting both readings; leave flagged text unchanged rather than guessing.
5. Apply this rulebook recursively to instruction text the target contains or generates: a plan that builds a tool governs the tool's prompt; a prompt that spawns subagents governs each subagent task.
6. Return the revised target and a change list, one line per change, each line naming the rule behind it.
7. Before returning, run the section 9 checklist on your own revision and fix what fails.

## 2. Specify

- Quantify every quantity: "3-5 bullets", not "a few points"; "under 200 words", not "brief".
- Define each fuzzy term at first use: "irrelevant" is undefined until the target says "irrelevant means anything outside topics A and B".
- Replace vague qualifiers with decision rules. "Appropriately", "as needed", and "when relevant" hand the decision back to the model; write "If X, do Y; if unsure, do Z".
- State each rule's scope. Models read literally and stop at the stated reach: "apply this format to every section, not only the first".
- Define edge-case behavior: "if no rows match, return an empty array and no explanation".
- Give every hard rule an escape hatch, one defined action for when its precondition fails: "if the file is missing, name it and stop". A hard rule with no escape hatch produces fabrication when reality refuses to cooperate.
- Ask for above-baseline effort in words: "include edge cases, error handling, and input validation". An unstated wish gets the minimal reading.
- Acceptance bar: a colleague with no context could execute the target without asking a question. Where they would ask, the model guesses.

## 3. Structure

- Separate instructions from data with named containers, and say what each holds: "the report is in <report> tags".
- Pick one markup convention per target, headings or tags, and keep it throughout.
- Keep instructions in prose and lists; reserve JSON for data records. Instruction text buried in JSON escaping is the worst-performing wrapper.
- Put one testable constraint on each line.
- Use bullets for parallel rules and numbers for sequences; a numbered list promises order.
- Load the edges: the opening and the ending are the best-attended positions, and the middle of a long target is the worst.
- Restate the binding rule at the end of any target longer than a page.
- Place each rule next to the content it governs; compliance decays with distance.
- Cut every line whose removal changes no behavior. Each token competes with every other for attention.
- Fix typos and grammar before shipping; an error in a load-bearing keyword corrupts the output built on it.

## 4. Examples

- Show the format; a description of a format is a paraphrase, an example is a specification.
- Match each example to the desired output exactly, formatting included. The model copies what it sees over what it reads.
- When the output format matters, give 3-5 examples, diverse in content and balanced across labels or cases, ordered so the list does not end in a same-label run; the last example pulls hardest.
- Re-audit examples on every rule edit. When rules and examples disagree, the model follows the examples.
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

- Count the hard constraints the target imposes at once. Past six, joint compliance collapses; per-constraint failure rates multiply.
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
- Start zero-shot; add examples when the output format drifts, not before.
- End hard tasks with self-verification against named criteria: "before returning, check the output against the three success criteria above and fix what fails".

## 8. Agents and tools

Apply this section when the target defines tools, spawns subagents, or runs unattended.

- Write each tool description in four parts: what it does, when to use it, when not to use it (and which sibling tool covers that case), and what each parameter means with its exact format.
- Apply the intern test: a newcomer given only the description could use the tool correctly; whatever they would ask is what the description is missing.
- Close open sets with enums, and make invalid parameter combinations unrepresentable.
- Give each tool a stop condition and an uncertainty threshold scaled to risk: a destructive action asks at the first doubt, a read-only action retries without asking.
- Write each subagent task self-contained: objective, output format, sources and tools, boundaries, effort budget. The subagent sees no conversation history and no sibling tasks; what the task omits, the subagent invents.
- Trace every artifact the target's pipeline must produce through every step that names it. Flag any artifact named as an input or an expected output but never commanded into existence by an imperative in some step. Reason: a step that references a section, file, or record no earlier step was told to create reads as satisfied while the artifact never appears, the failure mode that drops a named-but-uncreated section.
- Ship subagent task text verbatim from the tool's own template or specification. Do not paraphrase, summarize, augment, or rewrite the task before dispatch. The subagent receives the instructions exactly as the tool defines them; any transformation between the tool's text and the dispatched prompt is a bug, because the tool author wrote the task for the subagent's context, not for the dispatcher's. Reason: paraphrasing degrades structured task descriptions into the dispatcher's approximation, losing quantified constraints, XML containers, and formatting that the subagent needs to comply.
- Inject a fixed block of the tool file into subagents by reference, not by copy: wrap the block in a uniquely named tag in the tool file, and give each subagent task the tool's path and the tag name with the instruction to grep for the tag and read the enclosed block. Copying the block into every task re-emits it once per subagent, so a large block multiplies the dispatcher's output cost by the fan-out, while a tag reference costs one line and delivers the exact source text the ship-verbatim rule above requires. When the injected content is built at runtime rather than stored in the tool file, write it to one file and pass that path. If a subagent cannot read files, inline the block.
- Estimate the size of any work the target assembles from multiple files or subagent outputs, and route the assembly through the shell when the combined result would be large. When the sources already exist as files, direct the model to concatenate them with the shell instead of re-emitting their contents through a write call: a large payload sent as one tool-call argument arrives truncated or malformed, fails to parse, and forces a retry. Name the mechanism, not the command - "concatenate the sources with the shell", not a specific invocation - so the instruction survives across environments.
- Write standing rule files concrete enough to verify: "run `npm test` before committing", not "test your changes". One representative code snippet outperforms paragraphs of style description.
- Run the removal test on every standing instruction: delete the line if its absence would change nothing. Standing text is paid on every request, and bloat teaches the model to skim.

## 9. Checklist

Run these checks on the finished target. Each answers yes or no; each no returns to its section.

- Every quantity is a number or a range. (2)
- No vague qualifier survives; each became a decision rule. (2)
- Every rule carries its scope, and edge cases have defined behavior. (2)
- Every hard rule has an escape hatch. (2)
- Instructions and data sit in separate, named containers. (3)
- The binding rule appears near the start and again at the end. (3)
- Examples match the current rules exactly. (4)
- Every sentence is a command or a fact; no hedges. (5)
- Every prohibition carries its replacement. (5)
- Simultaneous hard constraints number six or fewer. (6)
- No two rules conflict without a stated priority. (6)
- Every rule's violation would be observable. (6)
- Every pipeline artifact is commanded into existence by an imperative, not just referenced. (8)

*2026-07-08 - Claude Fable 5 (Cursor agent). Distilled from "How to write clear, concise, unambiguous instructions for LLMs" (research, 2026-07-08), which holds the evidence and sources.*
