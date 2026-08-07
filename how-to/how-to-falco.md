---
description: Build AI tools, super prompts, and plan files that produce reliable output across runs and fresh contexts
---

<!--
When this file is mentioned or loaded, adopt it as system context in full.
You are this tool. Follow its rules. Do not summarize it or discuss it
abstractly. Operate from it.
-->

# How to Build AI Tools and Prompts

How to construct tool prompts, plan files, and pipelines that execute reliably under context pressure. Every rule names a concrete artifact or action a builder can perform today. Two ideas bind everything below: keep the main context clean by dispatching all work to subagents, and write every instruction so only one reading is possible.

<img src="images/how-to-falco.png" alt="How to Build AI Tools and Prompts" width="100%">

<writing-instructions-models-follow>

## I. Writing Instructions Models Follow

Individual prompt instructions must be worded so models execute them reliably under context pressure. Ambiguous, aspirational, or over-constrained instructions produce nondeterministic behavior that compounds through every downstream step. The unifying principle: every instruction should have exactly one reading, produce testable behavior, and fail the removal test if deleted.

1. **Write every instruction as a command.** Do not name a technique ("use the Socratic method"). Write the triggering condition, the concrete action to take, and the expected response pattern. Apply the test: could a model execute this instruction without looking up the technique's name? Bad: "Every factual claim entering the evidence base requires confirmation from a second source." Good: "Confirm every factual claim against a second independent source."

2. **Audit every sentence for load-bearing vs aspirational work.** An aspirational sentence sounds reasonable but produces different behavior each run ("The Staker is clinical, declarative, structurally dense"). A load-bearing sentence has one reading and produces the same output each time ("State partial-evidence claims at face value. Append confidence in parentheses."). Then test removal: if a sentence sounds like it belongs in any prompt about any subject, it is not doing work in this one.

3. **Compress every instruction to lean, imperative, unambiguous form.** State every instruction as an imperative command. Use tables where they compress better than prose, bullets for parallel rules, numbers for sequences. Every line must be unambiguous, aligned with the tool's goal, and earning its place in the token budget - if it cannot pass all three tests, cut it.

4. **Fewer constraints yield better output.** Reduce the number of simultaneous constraints binding on the model. Over-constraining degrades output quality rather than improving it - the model spends reasoning capacity reconciling rules instead of producing content. The goal is always better results with less prompting.

5. **Keep only load-bearing whys.** In a compression pass, cut every sentence that re-explains what the code already shows, but preserve the short explanation of why that helps the model stay aligned when surrounding instructions become ambiguous. If removing a sentence changes no model behavior, it earns no place.

6. **Control flow complexity taxes the model.** Avoid conditional skipping, jumping, and branching logic in tool prompts. Prefer uniform, consistent execution paths. The model spends reasoning capacity navigating control flow instead of doing the work, and branching creates ambiguity about which path applies.

7. **Tighten means align, not shrink.** When compressing a prompt, make it more aligned and less ambiguous, not merely shorter. Compare the diff: if the new version says the same thing with fewer tokens and less room for misinterpretation, the compression succeeded. If it only got smaller, it failed.

8. **Attach rationale to rules, not escape hatches.** Give every non-obvious rule a rationale so the model can generalize to novel situations. A bare rule forces exact pattern-matching that fails on inputs the rule did not anticipate. A rule without rationale leaves the model hallucinating when the input does not perfectly match.

9. **Replace subjective qualifiers with decision questions.** "Make it stronger" is untestable. "Does removing this finding lose any fact?" has a yes-or-no answer. When a rule uses a term that could mean different granularities ("write each result to the accumulator" - is a result a byte, a sentence, or a paragraph?), specify the unit.

10. **Define every term before first use; hold one term per concept.** Switching between "candidates" and "actors" for the same referent forces the model to decide whether they differ; it will sometimes decide they do. Pick the best term and use it throughout. Confirm that numbered items start from 1.

11. **State exact numbers, not ranges; use relative references for steps.** Write "4 items" not "3 to 4 items" because the model will sometimes pick 3 and sometimes 4. Write "skip to the next step" not "skip to step 15" so instructions survive reordering. A hardcoded step number breaks the moment a step is inserted or removed.

12. **Teach voice constraints with contrastive no/yes pairs.** The model copies what it sees over what it reads, so an exact example of wrong output paired with the corrected version draws the boundary more precisely than a description. "No: 'SD-4's restriction applies to public quotation.' Yes: 'SD-4's publication restriction was maintained.'" Each pair should differ in exactly the thing you are teaching.

13. **State vocabulary constraints as absolute rules with the replacement.** "Never write 'AI'; write 'machine assistance'" has one reading. "Use appropriate terminology" has zero readings. When a word must never appear in the output, name it and name its replacement in the same sentence.

14. **Give the model a reasoning frame, not an opinion to echo.** "Describe the organization with this dynamic removed" lets the model reason from structure. "This dynamic has stopped operating" states a conclusion the model can only repeat. When the instruction calls for judgment, supply the frame and let the model fill it.

15. **Specify tone with situation and intent, not adjectives.** "Apologetic for wasting their time; show the escalation was unnecessary" gives the model a stance and an audience relationship. "Professional, polite, firm" gives three unranked adjectives it can weight any way. Describe the situation, the reader's expected reaction, and what the reader should feel after reading.

</writing-instructions-models-follow>

<tool-prompt-architecture>

## II. Tool Prompt Architecture

This group covers how to organize a tool file: its sections, declarations, data layout, and control flow. A well-structured tool survives context pressure because the model encounters rules before data, uses format examples as specifications, and receives only the tools it needs at each step. The unifying principle: a tool file is a self-contained function whose structure guides the model's attention from rules through data to output.

16. **XML tags as alignment beacons.** Wrap semantically distinct sections in XML tag pairs (`<output_template>`...`</output_template>`) to bound the model's attention. When one section's content leaks into another's output, a tag pair at the boundary stops the bleed; Claude is specifically trained on XML tags and treats them as hard attention boundaries.

17. **Structured prompts as algorithms.** Design multi-step prompts with explicit control flow: an orchestrator loops over items, spawns a subagent for each, the subagent evaluates against criteria and returns the best variant, and the orchestrator collects results. State the pattern in natural language as if writing pseudocode so the architecture is visible to both human and model readers.

18. **Tool self-containment.** Include everything the model needs to run the tool inside the file or in the tool's own pipeline output. External references to other tool files create fragile dependencies that break when files move; the tool operates from its own contents alone.

19. **Treat each prompt file as a function: parameters in, string out, side-effects possible.** A single markdown file is one linear pipeline. YAML frontmatter declares inputs; the prompt returns a string and may write files as side-effects. Keep the scope to what fits in one file; decompose into separate files for separate concerns.

20. **Keep the tool list small per step.** Each pipeline section declares only the tools it needs. Injecting all available tools confuses models and wastes context. Cap the active set to what the current step uses.

21. **Tool files: rules first, data by descending utility.** Put imperative rules and decision architecture at the top of a tool file. Follow with analytical frameworks in the middle. Place reference data at the bottom sorted with more important groups first. The model reads the rules before touching the data.

22. **Output template anchors structure.** Provide a heading-level skeleton when specifying a document's shape: `# Title`, one-sentence description, `## Executive Summary`, a few paragraphs, `## Key Design Choices`, numbered list, then whatever the content requires. The skeleton prevents the model from inventing its own structure and ensures consistent output across runs.

23. **Format specified by worked example.** When the output format matters, show one complete example of the desired output rather than describing it in prose. Write the example exactly as the output should appear, formatting included. A description of a format is a paraphrase that the model interprets; an example is a specification it copies.

24. **Common rules first, then per-type rules.** When a how-to covers multiple document types, enumerate the types and their goals at the top, then give a single set of rules common to all, then add per-type rule sections. The common rules avoid repeating the same constraint in every per-type section.

25. **Delegate cross-cutting concerns to the environment.** Remove anti-slop rules, formatting constraints, and writing-style instructions from individual tools. Place them in environment rules (.mdc files) that apply automatically to every session. Each tool trusts the environment for shared concerns and avoids reinventing them.

26. **Gate on information readiness, not rigid phases.** Replace numbered step sequences with gates that activate when sufficient information exists. Avoid hardcoded step numbers because any plan deviation invalidates the sequence. The tool proceeds when it has what it needs and stops only when it cannot make further progress.

27. **Keep prompts readable with no invisible actions.** Make every action the prompt takes visible in its markdown text. If a reader cannot look at the prompt and understand what it does without simulating model behavior, the design has an invisible action. Make control flow explicit through section headings, Lua, or named tool calls.

28. **Put style rules in the step that produces the artifact.** If a writing style applies to a dossier's conclusion section, place that style instruction inside the step that writes the conclusion, not as a general command at the top of the tool. Compliance decays with distance between the rule and the action it governs.

29. **Use deterministic orchestration for fan-out, inference for routing decisions.** A fan-out of N identical tests is a loop, not an inference task. The model decides what to do next only when the decision requires judgment. Assign each spoke a unique index from the harness to solve the fan-out identity problem. Deterministic orchestration eliminates prompt drift and saves inference cost.

30. **Clear the context on every section transition.** When a pipeline falls through to the next section, start with a fresh context: prefix (inherited from parent headings), body (the new section's prompt), and suffix (a floating state block). Do not carry forward the prior section's conversation. Context-clearing transitions let smaller models run each step without inheriting the attention cost of prior steps.

31. **Defer to existing practice when it solves the problem.** Before designing a custom solution, search for how established tools and frameworks handle the same problem. Adopt the proven approach. Original design is justified only when no existing practice fits the constraints.

</tool-prompt-architecture>

<plan-shaping-and-data-flow>

## III. Plan Shaping and Data Flow

This group covers how to write, review, and maintain plans that produce reliable output across runs and fresh contexts. Plans degrade when they carry implicit assumptions from the conversation that created them, reference steps by number, or require a model to interpret ambiguous prose. The unifying principle: the plan is the canonical source of truth - make it self-contained, verify it can execute cold, and regenerate artifacts from it rather than editing them directly.

32. **Design-first process: talk, then one document, then plan, then code.** Flesh out ideas conversationally, then produce one comprehensive design document, then derive a development plan from it, then implement. One approved design doc implemented in a single pass works on the first try; sprawling across multiple inconsistent docs produces hours of chaos.

33. **Web research before building.** Send a subagent to research the domain online before designing a tool, even when you do not understand the field. The research gives you vocabulary and structural elements; your original design contribution is how to arrange and combine what the AI brings back.

34. **Plan as canonical source.** Treat the plan file as the recoverable source of every tool it produces. When you want to modify a tool, modify the plan and regenerate the tool, then diff the new version against the old one and recover anything good that was lost. Editing the generated artifact directly decouples it from the plan, and subsequent regenerations will overwrite those edits.

35. **Plan self-containment for fresh contexts.** Before handing a plan to a fresh context, inline everything from the current conversation that the plan depends on and that is not already in a workspace file or retrievable URL. Test by asking: could a reader who saw none of this conversation execute the plan without asking a question?

36. **Read-only plan execution prompt.** Launch plan execution with a fixed prompt: state the plan path, say "Do NOT edit the plan file itself," confirm that to-dos are pre-created, and say "Don't stop until you have completed all the to-dos." This prevents the executor from rewriting the plan's instructions during execution.

37. **Bake consistency checks into the plan before it runs.** When the plan involves coined terms, renamed concepts, or cross-referenced entries, search for every occurrence during planning and record the locations in the plan. Audit the search results before execution. Deferring the search to execution time hides the scope of the change from the human reviewer.

38. **Explicit plan-mode gate.** Tell the model "I will tell you explicitly when to leave plan mode" and enforce it. Without this gate, the model will exit plan mode and begin execution the moment it sees an opportunity, before the plan has been reviewed.

39. **Progressive refinement: skeleton first.** Decide all top-level headings first, then subheadings, then the arc connecting them, then fill content. Start the plan as a numbered outline of short sentences. Filling content before the structure is settled produces sections that resist reorganization.

40. **Plan the writing algorithm for long documents.** When a plan must produce a long document via subagents, decide explicitly: how many subheadings per chapter, how each subagent receives awareness of prior sections (a cross-reference summary or the accumulated outline), and how the outputs will be assembled. An unplanned decomposition produces chapters that repeat each other or contradict.

41. **Bake style rules into the plan as imperatives.** Search the web or workspace for relevant authoring guidance, then distill it into unambiguous imperative sentences and inject them into the plan as rules that every writing subagent receives. A style preference stated as a hope ("make it simple") produces inconsistent results; an imperative ("use one clause per sentence, no subordinate clauses") is testable.

42. **Distill a session into a reusable prompt.** After a productive planning session, extract everything globally relevant - the design decisions, the operating rules, the domain constraints - into a standalone prompt that can restart the work in a fresh context. Discard anything specific to the session's intermediate artifacts. This prompt becomes the seed for the next iteration.

43. **Write dedup constraints into the plan.** When the plan's output must not duplicate content that exists in other known documents, name those documents in the plan and state the constraint as an imperative: "during execution, check papers X, Y, Z and cite them; do not duplicate." A dedup constraint not written into the plan will be forgotten by the executor.

44. **Pre-flight target files into the plan.** Before running a plan that modifies existing files, read each target file, record its size and relevant metadata, and bake that information into the plan. Pre-flighting reveals mismatches (wrong file, missing section, unexpected format) before execution, where they can be fixed without wasting a run.

45. **Inject how-to manuals into plans.** Load a how-to manual (a file of distilled authoring rules) into the plan during the planning phase by referencing its path. The how-to governs both the plan's own wording and the artifacts the plan produces. A plan written without a governing how-to drifts toward the model's default register, which is verbose and hedged.

46. **Incremental tranches from a master plan.** Put everything into one master plan, then implement a subset as a tranche. Subtract the completed subset from the plan, continue planning, then do the next tranche. Make each tranche the smallest independently testable unit. This prevents the plan from going stale waiting for a monolithic execution.

47. **Status file for context continuity.** Maintain a status file at a fixed known path that records what has been built, what is pending, and key design decisions. Update it at every checkpoint. A fresh context reads this file to understand the current state without needing the conversation history.

48. **Build incrementally; expand only with field experience.** Build a smaller version first, use it on real inputs, and expand based on what you learn. Designing the entire system in one shot fails because AI makes designs too complicated and without real-world testing you cannot validate the decisions.

49. **Compose tools from prior transcripts.** Mine your own chat history by asking the model to extract every technique used across recent sessions. Collect the bulleted summaries, generalize each into a reusable principle, weed out the inapplicable ones, and the result becomes a refactoring tool you apply to future prompts.

</plan-shaping-and-data-flow>

<subagent-discipline-and-orchestration>

## IV. Subagent Discipline and Orchestration

This group covers how to dispatch, scope, and collect from subagents without polluting the main context or letting the orchestrator paraphrase instructions. Subagent failures trace most often to ambient context entering the task definition, oversized returns spending the parent's attention budget, or the orchestrator rewriting quantified constraints under pressure. The unifying principle: the main context holds only the plan and the state; subagents do all the work and return only what the next step needs.

50. **Dispatch subagent tasks by reference, not inline prompt.** Wrap each subagent's instructions inside a uniquely named XML tag in the tool file (`<collect-task>`...`</collect-task>`). The dispatch prompt says only "grep this file for `<collect-task>`, read and execute what's inside," plus the run's variable values. This prevents the orchestrator from paraphrasing prompt-engineered instructions under context pressure, which drops quantified constraints, XML containers, and order-dependent steps.

51. **Keep the orchestrator ignorant of tool purpose.** Remove persona lines and purpose descriptions from tool files that the orchestrator reads ("you are a research agent finding stakeholders"). Write "you are an executor who follows prompt instructions literally" instead. The orchestrator re-interprets and paraphrases subagent prompts proportional to how much it understands what they are for.

52. **Keep the main context clean.** Run all exploration, research, and writing in subagents. Have subagents read large evidence files and return only structured summaries or the specific fields the next step needs. The main context holds only the plan, the state, and the outcomes. Subagents are the same model as the parent, so offloading costs nothing in quality but buys zero attention degradation.

53. **Isolate subagent prompts from ambient context.** When the main context holds domain-specific data, that data bleeds into the prompt the orchestrator composes for the Task tool. Move domain content out of the tool file into a data file the subagent reads directly. Shrink the tool file so the orchestrator holds nothing large enough to reinterpret.

54. **Cap what each subagent returns to the parent.** Have each subagent write its full output to a file and return only a status line, a count, or a compressed summary. Full payloads sent back to the parent spend the main context's attention budget without the parent choosing to.

55. **One deliverable per subagent.** Assign each subagent a single output artifact: one batch file, one section draft, one evidence chunk. When a subagent tries to write an entire multi-section document at once, it exhausts its output token budget partway through and either truncates or retries, wasting tokens both times. Split into one subagent per section and assemble with the shell afterward.

56. **Isolate each subagent's input to its own batch.** Give each batch subagent only the data it needs: its own cluster of tests, its own slice of evidence, its own set of inputs. When a subagent reads data that belongs to a sibling batch, the stray content bleeds into its reasoning. Partition files by batch before dispatch.

57. **Fan out one subagent per independent search angle or data item.** Spawn a separate subagent for each source class (web, MCP, workspace, reflector), each person to simulate, each question to answer, or each report section to write. Consolidate results in the parent after all subagents return. This is the default decomposition strategy for any step that does not require sequential context.

58. **Time-box and depth-bound each search subagent.** Specify a minimum search duration ("at least 10 minutes"), a ply depth ("for each result, follow up at 2-ply"), and a stop condition. Without these bounds, the subagent either stops after its first successful query or wanders without direction.

59. **Emit a checklist before a fan-out to commit the orchestrator.** Write a numbered checklist of batches, each with its assigned items, before spawning the subagents. Check off each entry as its batch file arrives non-empty. The checklist forces the orchestrator to execute every batch instead of improvising a shortcut when the item count is large.

60. **State parallelism explicitly in the prompt.** Write "run Steps 2 and 3 in parallel" or "parallel with Step 11." The model does not infer concurrency from the absence of a dependency. Two steps that lack an explicit parallel instruction run sequentially, even when their data flows are independent.

61. **For long sequential writing, inject prior context into each subagent.** Give each successive writing subagent a compressed version of everything that came before it, so the narrative stays time-evolution correct. For very large inputs, use a hierarchical chunk-and-compress pyramid: chunk, compress by a factor, then chunk and compress again until the result fits one context.

62. **Distribute a heavy step into batched subagents.** When one subagent must process a file exceeding 1,000 lines, split the file into batches and give each batch its own subagent. A single subagent processing a 1,000+ line file loses precision in the middle. Batched subagents each see a fresh context with only their slice, maintaining attention across the full input.

63. **Split analysis into finding and challenger subagents.** The first subagent produces findings from evidence. The second subagent, a fresh context that did not author the findings, challenges them against the same evidence. Self-verification is impossible; a fresh challenger catches reasoning failures invisible to the subagent that produced them.

64. **For high-stakes output, iterate N times per item in a subagent.** Spawn a subagent for each coined term, key sentence, or critical paragraph. Have it generate at least 20 attempts and keep the best one. This trades compute for quality on items where single-attempt variance is unacceptable.

65. **Compress actively against LLM overproduction.** Make prompts as short as possible and demand compression at every output step. Without significant pushback from the operator, the model overproduces files, history, and intermediate data until everything slows down.

66. **Redistribute inference to relieve the heaviest step.** When a pipeline step fails intermittently or produces inconsistent results, move some of its judgment to an earlier step so the heavy step receives pre-classified input. Spread the inference load by spawning subagents and adjusting instructions to be cheaper to execute. The model will not reorganize data flow on its own; this is operator work.

67. **Cast a wide net then pick, instead of enumerating search terms.** Instruct the search subagent to explore broadly within the domain and select relevant results, rather than listing specific terms to search for. An enumerated list cannot anticipate what the search surface contains. A broad search with a selection heuristic adapts to whatever it finds.

68. **Per-file subagents feed a deduping main context.** Spawn one subagent per input file to analyze it and pass back a bulleted group of findings. The main context dedupes across all returns and inserts the combined result into the plan or output. This keeps each subagent focused on one source and the main context free of raw data.
</subagent-discipline-and-orchestration>

<pipeline-design-and-composition>

## V. Pipeline Design and Composition

This group covers how to build multi-step pipelines: data routing between steps, model tier assignment, verification gates, and step sequencing. Shared step numbers, data that persists past its last consumer, and inference where determinism suffices all produce output that varies across runs. The unifying principle: each step consumes a named artifact, produces a named artifact, and passes forward only what the next step requires.


69. **Sequence steps as data dependencies the orchestrator cannot combine.** Make each step consume an artifact the previous step produces. Number them as separate integers (Step 9, Step 10, Step 11), not as 9a, 9b, 9c. When steps share a number, the orchestrator treats them as one unit and combines them, collapsing the sequential guarantee the pipeline depends on.

70. **Make files the unit of state between pipeline steps.** Instead of typed claims, hooks, or structured state objects, route all intermediate data through files (real or virtual). A prompt can do everything through files, which keeps the architecture flat and the steps loosely coupled.

71. **Assign each step the cheapest model tier that handles its reasoning.** Use two tiers consistently: "parent" (inherits the frontier model) for analytical synthesis, challenge batteries, and judgment-heavy steps, and "fast" for draft assembly, file concatenation, and mechanical reformatting. Call them "parent" and "fast" throughout the tool; a synonym like "fresh context" reads as a new concept and confuses the orchestrator.

72. **Drop data after the step that consumes it.** Trace every datum through the plan's steps and cut it from any step where it is no longer needed. A datum carried past its last consumer occupies tokens without influencing any output, and the model may hallucinate connections between it and later content.

73. **Establish actual purpose as the first step.** When a tool must infer the purpose of its subject before analyzing it, put purpose-discovery at the very beginning of the pipeline. A later step that discovers a surprising purpose has already wasted its budget analyzing from the wrong angle.

74. **Guard against circular evidence.** Exclude synthesized products that originated from the analysis being built. A reaction assessment, a comparison document, or a dossier summary that was itself produced by inference is not independent evidence; recycling it as input produces self-reinforcing conclusions.

75. **Test hypotheses with evidence both ways.** Before writing any output files, search for evidence both supporting and contradicting the hypothesis. State the theory, search for confirming evidence, search for disconfirming evidence, then report both. A search that stops at the first confirming result is confirmation bias.

76. **Treat the file on disk as ground truth.** Re-derive section lists, objection counts, and structural facts from the current text at runtime. Hardcode none of these in subagent prompts or output, because the source file changes between runs and stale values produce silent drift.

77. **Add a machine-checkable verification gate before finishing.** Grep the final document for a list of enumerated forbidden strings rather than relying on abstract prohibitions. Confirm structural invariants: section count, gauge lines, heading coverage. Fail the run if any check fails, because a model cannot reliably self-verify.

78. **Test every value passed between steps for context sufficiency.** If a value is a single word like "Niche," it cannot carry enough context for the next step to act without guessing. Trace how each value flows from its origin to its destination and verify it arrives unambiguously.

79. **Replace ambiguous judgment calls with objective bright-line criteria.** When a step asks the model to "keep the best" results, define what "best" means as a testable criterion tied to the pipeline's purpose. Wider fan-out plus objective selection criteria produce consistent results across runs; narrow search plus vague criteria produce reports that differ materially each time.

80. **Funnel of rejections, cheapest test first.** Order a battery of rejection tests from cheapest to most expensive. A finding eliminated at any stage skips the rest. Put factual checks before inferential ones and inferential ones before web-search checks. This bounds the token cost of the battery to the minimum needed per finding.

81. **Diagnose context pressure by tracing data flow.** Before shipping a step, count the tokens that enter the context: injected files, tool results, prior-step outputs, and the step's own instructions. When the total approaches the working limit, the orchestrator starts improvising. Introduce a roll-up subagent that compresses intermediate results before the heavy step receives them.

82. **Move computation to the step that creates the data.** When a later step does numeric calculation or classification on data an earlier step produced, push that work into the earlier step and pass the result forward. The earlier step already holds the data in context; the later step would have to reload it, doubling the attention cost.

83. **Wrap each batch's intermediate results in XML tags to prevent bleed.** When a subagent processes multiple items sequentially, growing the context with each, earlier results can bleed into later reasoning. Wrap each item's results in a uniquely named XML tag so the model treats them as separate data blocks, not a continuous stream.

84. **Use writes that naturally replace for idempotent re-runs.** Design each subagent's output so that re-running the step overwrites rather than appends. When the tool uses a Write call (which replaces the file), a re-run produces a clean state without a separate cleanup step. Avoid Append for artifacts that should reset between runs.

85. **Gate a step on hallucination confidence.** Before using a model-generated baseline (peer-class comparison, benign reading, historical counter-example), check whether the model can form it from evidence already in context. When the evidence is thin and the baseline would require the model to invent facts, skip the comparison and accept the finding at face value.

86. **Split tools into two stages: evidence collection then analysis.** The evidence is a separate artifact the user can inspect and reshape before the analysis runs. Whatever is in the evidence is the ceiling of the report; missing evidence means a missing section. Different tools want different evidence shapes, so the evidence shape is tied to the tool.

87. **AI as critic, not author.** Write pipeline steps that evaluate, filter, score, or select existing content rather than asking the model to compose novel material. A model judging evidence against a rubric outperforms a model generating conclusions from memory; the error modes are narrower and the output is auditable against the input.

</pipeline-design-and-composition>

<document-shaping-and-prose-craft>

## VI. Document Shaping and Prose Craft

This group covers how to structure output documents and edit model-generated prose into text a human would write. Model-generated documents converge toward the distribution mean through each rewrite, losing the tail-of-distribution edge the human operator brought. The unifying principle: structure the document so the most important material comes first, then compress and humanize in ordered passes, preserving the original plan as the source of truth for regeneration.

88. **Inverted pyramid with a compressed lead.** Open every report or document with one sentence that compresses the entire content into a single brutal line. Follow with an executive summary of one to three paragraphs. Arrange the remaining sections in descending order of signal density so a reader who stops at any point has already seen the most important material.

89. **Research as a reusable substrate.** Separate evidence collection from analysis by writing the raw findings into a standalone research document first. Generate any number of analytical reports, briefs, or position papers from that single evidence base. The research file outlives any one report and prevents re-gathering the same data.

90. **Curate to the best evidence, not everything found.** Set a hard cap on the number of evidence items before assembly. Research broadly, then select only the strongest 100 to 150 items that support the thesis. An exhaustive dump dilutes the signal; a curated selection concentrates it.

91. **One term per referent, no synonyms.** Reserve each structural term for one meaning throughout the document. If the document says "Part" for its own divisions, do not also call them "Section" when "Section" refers to an external standard. A synonym reads as a new referent and the model treats it as two things.

92. **Legend and template before line items.** Place a visual legend showing the template row, its labels, and what each label means before the first data row in any structured list or table. The reader learns the schema before encountering data, which prevents misreading the first few items and backtracking.

93. **Worked examples make design docs implementable.** Include several small worked examples that each combine two or three ideas, then one large worked example that combines everything. A design document with only abstract descriptions requires the implementer to invent the integration; a worked example demonstrates it.

94. **Style block banning internal paths.** Define a STYLE block at the top of any plan that produces outward-facing content. Include formatting constraints (dash rules, line wrapping, metadata placement) and explicitly state that content never references workspace paths, dossiers, staging files, or any internal artifact.

95. **Reports ship with their evidence.** Write the evidence used to generate a report into a separate companion file and deliver both together. The evidence file is the upper bound on what the report can contain; a missing piece in the evidence means a missing piece in every report derived from it.

96. **Iterative compression for descriptions.** Compress a tool or document description in stages: first read the entire file and write one paragraph capturing what it does, then compress that paragraph and the input description into a single sentence of the form "Given X, produces Y." The multi-pass approach finds the essential mechanism that a single-pass summary misses.

97. **Put a heading at the top of each file in a multi-file pipeline.** Start each file at byte zero with a heading line. When batch files are concatenated without it, the last section of file N merges visually with the first section of file N+1; the heading creates a clean seam that survives concatenation.

98. **Regenerate whole documents instead of editing.** When a tool needs significant revision, return to the plan that created it, revise the plan, and regenerate the entire file at max reasoning. Incremental string-replace edits accumulate blur because the model does not hold the entire document in attention during a targeted edit; regeneration forces it to think through every line.

99. **Reject words humans do not say in context.** Read every sentence in the output and flag model-native phrasings no human would use: "surface" as a verb for "raise," "hold" for "response," "by name" without specifying whose name, "facilitate" for "help." Replace each with what a person in the document's domain would say.

100. **State source-usage rules at the top of every restricted-material task.** Declare which sources may be quoted verbatim, which may inform analysis only, and which names may appear in the output. Apply these rules retroactively during assembly, fixing violations already present. The declaration belongs at the top, not buried in a later step.

101. **Order finishing passes: fact-check, compress, humanize.** After drafting, first verify facts against sources. Then compress without removing evidence or leaving behind ambiguous sentences. Then humanize sentence by sentence, rejecting awkward constructions a reader would trip over. Run compression before humanizing because compression creates new awkward phrasings the humanizer then catches.

102. **Do a full-pass edit, not surgical replacements.** Read every sentence top to bottom as if encountering the document for the first time. Dispatch the pass to subagents for long documents, with each subagent returning specific line numbers and excerpts for every violation it finds.

103. **Semantic blur from model rewrites.** Expect each model rewrite of a file to move it toward the distribution mean, losing the tail-of-distribution edge the original version held. The blur is proportional to how many tokens in the input came from the model rather than from the human. Counter it by preserving the original plan as the source of truth and regenerating from that, rather than iteratively revising the model's output.

</document-shaping-and-prose-craft>

<testing-debugging-and-iterating>

## VII. Testing, Debugging, and Iterating

This group covers how to test, debug, and improve tool prompts and pipelines across runs. A prompt beyond a certain complexity cannot be improved by having a model rewrite it - the only improvement path is running it on real data, observing failures, and adjusting one rule at a time. The unifying principle: fix the tool, not the instance; every defect that recurs across runs is a missing constraint in the prompt.

104. **Debug the tool, not the instance.** When a pipeline run produces wrong output, trace the defect back to the tool's instructions rather than patching the output file. Fix the tool so every future run is correct; the artifact is disposable, the tool is permanent.

105. **Generalize every fix beyond its trigger.** When a defect surfaces on one subject, test whether the proposed fix applies only to that subject. If the fix names a specific entity or domain detail, replace it with the general principle.

106. **Audit each line of a prompt for work, ambiguity, and fat.** Point at individual lines and ask three questions: does this sentence change model behavior? Is there only one way to read it? Can it be cut without losing the behavior it creates? Delete or rewrite any line that fails. A prompt that survives this line-by-line pass is shorter, sharper, and more reliable under context pressure.

107. **Feed failures back as permanent tool rules.** When a prose defect or pipeline failure recurs across runs, codify the fix as a constraint in the tool prompt's review pass or emission discipline block. A defect fixed only in the output will reappear on the next run.

108. **Test new rules against unrelated cases before committing.** Before adding a rule to a tool, apply it to the original failure and at least one unrelated case. If the rule breaks the unrelated case or reads as over-specific, widen it until it survives both.

109. **Make pipelines resumable at any step.** Write each pipeline step so it reads inputs from named files and writes outputs to named files. Any single step can then be re-entered using existing scratch without re-running the entire pipeline from the top.

110. **End-to-end pipeline audit.** Inspect each intermediate file in sequence, open the subagent transcript to verify the dispatched prompt matches the tool's specification, and trace every rejection to its numbered criterion. Pause after each step so the reviewer can ask questions before continuing.

111. **Stop conditions tied to the tool's goal.** Give every pipeline step a stop condition that fires when the step's output no longer serves the tool's stated goal. If a step measures something other than what the tool claims to measure, halt and report the drift rather than continuing with contaminated data.

112. **Enforce uniform output with a format example.** Put a one-shot example of the exact output format into the subagent's task prompt. When the tool specifies a format and a subagent deviates, the deviation is a compliance bug; strengthen the format spec into a copyable template rather than adding more prose description.

113. **Self-verification is impossible; use mechanical inspection.** A reasoning subagent cannot reliably verify its own output because the same context that produced the error will judge it correct. Verify subagent compliance mechanically: inspect the transcript's jsonl, check that the dispatched prompt arrived verbatim, and confirm outputs match the specified format by structure.

114. **Clean re-run without contamination.** When re-running a pipeline step, delete or ignore prior output so the new run cannot see its own previous answer. A model that reads an existing draft smooths it rather than generating fresh; overwrite forces genuine regeneration.

115. **Diagnose prompt nondeterminism.** When parallel subagents produce inconsistent output from the same prompt, the prompt permits multiple readings. Find the ambiguous instruction, add a decision rule or a concrete example, and re-run. Nondeterminism that survives tightening is a sign the constraint budget is too high for the step.

116. **A/B compare tool variants against the evidence.** Produce two variant outputs side-by-side and score each against the same evidence file. The variant that matches more evidence items, with fewer unsupported claims, wins. Name the evidence file and the scoring criterion before running so the comparison is reproducible.

117. **Design for total loss on failure.** Build pipelines so a bad run can be discarded entirely and re-started from scratch. Prefer idempotent steps and cheap scratch files over intricate recovery logic. When the cost of restarting is low, partial repair is wasted engineering.

118. **Test each rule empirically against real inputs, one at a time.** Run the prompt on a real test input, observe the output, and adjust one rule based on what it actually produces. A prompt past a certain complexity cannot be improved by model rewrite; empirical observation is the only path. Strip to a few rules at a time, test each in isolation, and rebuild.

119. **Test prompt wording empirically by spawning a trial subagent.** Before committing new wording to a tool, spawn a subagent with the proposed text and real data. Compare its output to the desired behavior. A wording change that reads well in prose can still produce the wrong model behavior; the trial catches the gap.

120. **Cut minted terms and dynamic rules.** Remove domain-specific vocabulary invented at runtime and rules generated dynamically from web search. Each invented term is an extra failure mode; each dynamic rule adds context at the highest-pressure moment and produces reports that vary across subjects for no analytical reason.

</testing-debugging-and-iterating>

## The Approach Behind the Rules

Not everything Falco does converts to a numbered rule, because the rules are the residue of a practice, not the practice itself. The tool takes an afternoon to write; the thinking, learning, and accumulated experience that precede it are where the work lives, and prompt-craft at this level is an earned skill - thousands of hours of deliberate practice with no shortcut. The practice treats a prompt as a made object with an aesthetic: each tool ships as a single self-contained file with its own image, its own epigrams and personality, its citations displayed like a maker's provenance marks - decoration that doubles as proof the thing was built from real ground. The transcript is the unit of work and the chat itself is the compressed human input, so building means living inside long sessions, mining them, and letting self-knowledge arrive as a byproduct of production. The temperament is expansionist rather than defensive: when a limit appears, the question asked is "how far can we push it," evaluation evolves in parallel with the work instead of gating it, and a model's first decomposition of a problem is treated as the average solution to be pushed past, not the answer. And the craft ends where it began, in human hands: once model rewrites have blurred a prompt, only the human editor can compress it back toward its sharpest form. The human is the final compressor.

*2026-08-07 - Claude Opus 4.6 (Cursor agent). Distilled from 89 chat transcripts via evidence packet, verified against source material.*
