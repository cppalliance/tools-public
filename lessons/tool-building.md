# Tool Building Lessons

Tool building captures how you do something well, in a form precise enough for an agent to run it and reusable enough that the next person inherits your best version. Care compounds: every shortcut multiplies across every run and every fork. Done carefully, a tool is a small artifact that pays interest in the background of everything else you make.

### Plan Mode

Plan mode is the read-only posture for drafting a plan before any code runs. You enter explicitly ("we are going into planning mode") and stay across iterations until the plan is done. The agent reads, asks, drafts, revises; it does not edit code or commit anything. The plan is a living document you rewrite many times before a single line of code is touched. The cost of a tenth revision is one more turn at the desk; the cost of a bad plan compounds across every later run. Walk in slowly. There is time.

### Subagent Discipline

Every piece of knowledge work runs in a subagent; only a curated summary returns to the main context. Long sessions in the main thread degrade as raw intake bloats the working set, earlier reasoning gets buried under newer noise, and the model loses the thread [\[1\]](#ref-1). A subagent ingests broadly and returns one paragraph that earns its keep [\[2\]](#ref-2). The main context is sacred attention; subagents are scratch space. That single distinction reorganizes how you build everything.

### Compression Creates Quality

Every effective move in this craft is a compression, and compression is what creates outputs that do not telegraph slop. Slop is the texture of language-model output that was not asked to compress: bloated, hedged, repetitive, vaguely correct and concretely useless. Integers compress letter-numbered chaos into coordinates. Three-word labels compress workflow diagrams into things you can actually read. Subagent summaries compress hundreds of pages into a paragraph [\[5\]](#ref-5). Naming a deviation severity (low, medium, high) compresses a thousand observations into a tiny number a downstream reader can act on. Models reward this: they perform better on compressed inputs and produce sharper outputs when forced to compress before responding [\[6\]](#ref-6). When you find yourself with too much of anything (too many steps, too many words, that telltale slop texture), compress harder.

### Reading the Prompts

Every blockquote in this document is a paste-ready prompt for the Plan-mode chat box. The prose explains why; the blockquote is what you type. Copy it without ceremony.

## 1. Integer-Numbered Steps Only

*If you can't number it, it isn't a step.*

Number every step with one integer. No 5a, no 5.1, no nested bullets. Step 0 is preparation, Step 1 is the first real action, increments of one. New work cannot hide as a sub-bullet; it has to pick an integer index and push every later step forward, which surfaces real ordering decisions instead of cosmetic ones. The quietest benefit is that integers are coordinates: "Step 7" has exactly one referent today, a month from now, in your notes, in any future conversation. Letter-numbered or nested steps tax every reference to the plan.

The rule fights you when the work is still exploratory or branching across approaches. Use it for the plan you intend to execute, not the plan you are still searching for.

> Convert this plan to integer-numbered steps only. No 5a, no 5.1, no nested bullets. Step 0 is preparation, Step 1 is the first real action, increments of one. Renumber every downstream step whenever you insert a new one. Output only the renumbered plan.

A second move pays off during consolidation. When adjacent steps modify the same file or apply the same transformation across files, ask for a merge into a single higher-level step while keeping the total step count fixed by absorbing the boundary [\[7\]](#ref-7).

> Consolidate adjacent steps that touch the same file or apply the same transformation across files. Merge them into a single higher-level step and keep the total step count fixed by absorbing the boundary. Make the resulting pattern consistent across all shared file modifications.

For the curious: positional attention favors flat sequences. Each step occupies one unambiguous offset, so "Step 7" resolves through exact-match retrieval rather than hierarchical disambiguation. Nested labels fragment that signal because "5b" is both a child of 5 and its own ordinal, forcing attention heads to combine features in the regime where retrieval pathologies start swallowing constraints. Constraining the output channel to integers also narrows the next-token distribution at the point where outline drift starts: the model literally cannot sample "5b" because "5b" is not in the grammar. The plan-and-solve literature recommends an explicit divide-into-subtasks pass before execution [\[3\]](#ref-3); the strictly-ordered substep tradition predates it [\[8\]](#ref-8). One scope boundary is real: committed single-path plans pay maximum dividends because renumbering cost is fixed while coordinate benefit compounds, but exploratory reasoning [\[9\]](#ref-9) [\[4\]](#ref-4) needs multiple candidate paths and a flat integer scaffold collapses them prematurely. Use the merge-and-consolidate move [\[7\]](#ref-7) once you commit, never before.

## 2. Step 0 Is a Conversation

*Silence is a question, not an error.*

Running with no flags should not be a usage error; it should be an invitation. Put a small command table at the top of the file, decide upfront what the tool truly cannot start without versus what it can live without, and treat the first turn as a real opening move. Interactive mode is the human default; an explicit non-interactive flag and a machine-readable output mode are the parallel path for automated callers, the failure mode that strands agents otherwise [\[10\]](#ref-10). Commit to a single rule on optional fields: ask once and accept silence.

> Add a Step 0 interactive data-collection phase to a tool that runs when invoked with no arguments, prints a small command table, accepts free-form input on the first turn, and asks once before proceeding.

Declare the minimum-viable input contract and name the alternates. State the floor in plain language: the tool needs either A or B; everything else is optional. Specify graceful fallbacks so the absence of a primary source quietly triggers an alternate rather than halting the run.

> Specify the minimum-viable versus optional input contract for this tool, name the fallback source when the primary is absent, and commit to ask-once on optional fields.

For the curious: an explicit input contract gives the model a stable schema to reason against, so a missing optional field becomes signal rather than failure. Step 0 is internally a slot-filling module [\[11\]](#ref-11): pull every field you can from the first utterance, mark satisfied slots, and only prompt for what is missing. Skipping already-filled slots is the formal version of "do not ask twice." Each ask spends attention on both sides, so letting silence mean "skip" trades one bit of information for the user's pace. The non-interactive escape hatch matters in the reverse direction: an agent in a pipeline has no sensory loop to answer a guided prompt, and a chat-only tool deadlocks its callers [\[10\]](#ref-10). Pair an interactive default with explicit flags, stable exit codes, and a JSON output mode, and the same Step 0 serves a person at the keyboard and an agent in a queue without forking the code.

## 3. A Mermaid Diagram in Every Tool

*A label that needs a sentence is a diagram that already failed.*

Every tool needs a picture, embedded inside the tool file itself. When the diagram lives next to the steps, every future read starts with the shape of the thing instead of reconstructing it from prose. The constraint is severe: one to three brutal words per node, ideally a step number plus an abbreviation. Generate the diagram from the implied workflow of the numbered steps and weld it into the tool body so it ships with every invocation [\[12\]](#ref-12).

> Generate a mermaid workflow diagram for this tool from its numbered steps, embed it directly inside the tool file, and use 1-3 word labels with the step number prefixed to each node.

When the rendered picture comes back ugly, paste it back at the model and tell it to crucify each label: "Figma check" becomes "5 fig", "Compose final asset" becomes "9 build". The first pass is always too wordy; that is the iteration.

> Here is the rendered diagram. The labels are too wide and overflow their nodes. Crucify each label to 1-3 brutal words, keeping the step number, until every node fits cleanly.

For the curious: a diagram is already a compression of order and dependency, so long labels undo the very thing the picture exists to do. Cognitive Load Theory predicts the cost: when explanation lives far from the object it explains, the reader pays split-attention costs to stitch them back together, burning working memory that should be spent on the decision [\[13\]](#ref-13). Short on-graph labels with detail offloaded to the surrounding step prose is exactly the integrate-the-anchor, offload-the-essay move the theory recommends, and it works on the model reading in-context just as it works on the human eye. Visualization research adds that legibility and overlap control are first-class readability properties, not aesthetic preferences [\[14\]](#ref-14). Keeping the mermaid source under version control gives the diagram the same lifecycle as the plan it describes [\[12\]](#ref-12), so a change to the workflow forces a change to the picture in the same review. The graph anchors step reasoning so the model does not re-derive dependency structure from prose each invocation.

## 4. Confirmation Gates Before Structural Edits

*Ask before you move a load-bearing wall; never ask before you hang a picture.*

A structural edit is one that changes how the whole tool reads: renumbering steps, extending a pattern from one file to many, widening the scope of a rule from "this section" to "everywhere it is referenced." Local edits are reversible and self-evident; asking about them is noise. Routine "Are you sure?" prompts habituate users to auto-accept, so when something serious finally fires, muscle memory has already swallowed it [\[15\]](#ref-15). Reserve the gate for serious or hard-to-undo outcomes, and when it fires, name the specific change and its specific blast radius.

> Add a directive that requires the agent to ask once before any change that propagates across files, renumbers steps, or widens the scope of a rule, and to skip asking on edits whose effect is local and reversible.

For an existing plan without a gate, run a diagnostic pass first.

> Audit this plan, list every class of change that would shift interpretation across files (renumberings, pattern extensions, scope widenings), and consolidate them under a single gate directive that fires only on those classes.

For the curious: confirmation habituation is a measured human response. Repeated low-signal asks flatten the prior distribution of "this one matters," and the same flattening shows up in LLM judges trained on human feedback, which is why a gate that fires on every edit becomes worse than no gate at all [\[15\]](#ref-15). The execution model also matters. In LangGraph, `interrupt()` persists state and resumes from the top of the node, with named patterns for approve/reject and review-and-edit, and supports interrupts inside tools so a human can approve tool arguments before they execute [\[16\]](#ref-16). The trap: any non-idempotent side effect placed before the interrupt is replayed on resume, so the gate must be colocated with or after the effect it guards, never before [\[16\]](#ref-16). Studies of how experienced users actually run agents converge on the same shape: as trust grows, explicit approval narrows to high-leverage moments and is replaced by mid-run interrupts and lightweight monitoring [\[17\]](#ref-17). Quiet through routine, vocal when the frame is about to move.

## 5. Token Economics: Subagent-Only Exploration

*Bring me the wine, not the vineyard.*

The main context never sees raw HTML, raw search results, raw MCP payloads, raw design-tool JSON, or any unfiltered intake. Every act of exploration runs inside a subagent, and the subagent returns only a curated, reduced summary. The orchestrator specifies the question and the shape of the answer; the subagent filters aggressively and hands back only what the orchestrator can use. Put this directive at the top of every plan, before anything else.

> Add this as the first directive at the top of the plan: all exploration happens inside subagents; the main context never receives raw HTML, raw search results, raw MCP output, or any unfiltered intake; subagents return only curated summaries shaped by the orchestrator's question.

Detection is mechanical. For every step in your plan, ask what it returns to the main thread. Raw text, JSON, or HTML the model reads directly is a violation; a paragraph produced by a subagent that did the heavy reading complies. Vendor guidance describes the same split in numbers: a worker may spend tens of thousands of tokens exploring and return only one or two thousand condensed back to the lead [\[2\]](#ref-2). When in doubt, fan out.

> Audit the plan below step by step; for every step whose output is raw text, JSON, HTML, or any unfiltered intake, rewrite it as "subagent reads X, returns summary Y" so the main thread only ever sees curated output.

For the curious: self-attention scales quadratically with sequence length, but the effective use of that length is not uniform. Empirically the attention curve is U-shaped: information at the start and end of a long context is used well, information in the middle is used worst [\[1\]](#ref-1). As the main thread accumulates raw pages, high-signal reasoning gets buried in low-signal intake, and recall on targeted facts falls off as the window grows, independent of training and independent of the window size on paper [\[6\]](#ref-6). A subagent is a shaped buffer against this decay: it can burn tokens freely because its outputs are engineered to be small, and the parent thread never pays the cost of the material the worker consumed [\[2\]](#ref-2). The pattern has names elsewhere: a map-reduce primitive in which workers compress locally and the parent aggregates without seeing the fan-out material directly [\[18\]](#ref-18), and a handoff in the agent-to-agent sense, where one agent delegates and the parent never sees the intermediate steps [\[19\]](#ref-19). Whatever the subagent sees becomes the subagent's problem; the main context stays light enough to think.

## 6. Accumulate and Compress

*Gather an ocean. Boil it down to a sentence. Repeat.*

Agents collect far more raw material than could fit in a single head, then compress each pile to its essence before any of it touches the main thread. Heavy reading, scraping, and ingesting happens inside a child; only a curated artifact returns to the parent. The loop is the work.

The canonical example is documenting a library:

1. A first subagent iterates files and extracts each public API, returning entries tagged `API`.
2. A second subagent takes those APIs in batches of ten or twenty and writes per-function descriptions, tagged `documentation`.
3. A third subagent reads the documentation set and produces a single one-paragraph summary of what the library is and does.
4. A fourth subagent assembles the full reference, function by function, against that summary.

The output reads as coherent because every layer of compression happened away from the main context, and the parent only ever sees clean, tagged artifacts. The tag mechanism gets its own treatment in lesson 7 (Invisible Metadata, Breadcrumbs).

The characteristic failure mode is silent omission, not hallucination. A detail that looked unimportant on round one turns out, three layers later, to have been the load-bearing thing, gone without a trace [\[2\]](#ref-2). The cure is layered compressions with checkpoints, so each pass is small enough to be honest, and so the parent can ask a subagent to expand any region it suddenly cares about (medium confidence; depends on tagging discipline).

> Install the accumulate-compress mantra at the top of this plan. For every step, define what the subagent ingests, what it returns, and the one-paragraph summary the parent will receive. The main context never sees raw material.

The single most powerful compression operator is also the simplest:

> Summarize this in one brutal paragraph. No hedging. No bullet points. One paragraph.

For the curious: at the architectural level, the loop is map-reduce, where workers compress chunks and a parent merges, formalized for LLMs as `load_summarize_chain` with `MapReduceDocumentsChain` [\[20\]](#ref-20). When budget is finite and source is enormous, repeated lossy compression is the only honest path: recursive summarization research shows that maintaining state across very long contexts works better as iterated summary-of-summaries than as one heroic pass [\[5\]](#ref-5). For long documents specifically, hierarchical and section-aware merging outperforms single-pass summarization, which is why the four-stage library pipeline mirrors the staged merge the literature finds most faithful [\[21\]](#ref-21). The brutal-one-paragraph prompt earns its keep at the model level: a hard length budget activates the compression bias the model already carries from its training distribution, and there is simply no room left for hedging or padded prose, so the surviving sentences tend to be the load-bearing ones. The price is omission, not invention [\[2\]](#ref-2), which is why the cure is layered compression with checkpoints rather than one giant pass.

## 7. Invisible Metadata (Breadcrumbs)

*Pencil marks under the paint are how the next coat knows where to land.*

Subagents have three voices, not two. The dim lane carries the reasoning narrative. The bright lane carries the final answer the operator reads. The hidden lane carries a sidecar of structured tags: priority, severity (low/medium/high), category, and any custom field the plan declares. The visible lanes are for humans; the hidden lane is for the next step in the pipeline. This is the same idea as trained reflection tokens interleaved with normal text [\[22\]](#ref-22), lifted from inside the model and applied at the orchestration layer.

Once a strong model sees breadcrumbs in use, it spontaneously extends the pattern to other cross-cutting concerns it notices. Lesson 8 (The Operational Directive) leans on this directly, reporting deviations as breadcrumbs so the operator can grep the run rather than re-read it. Lesson 10 (The Plan Review and Data-Flow Audit) feeds the breadcrumb stream straight into the audit.

> Add breadcrumb emission to every subagent in this plan. Define a tag schema with fields {priority: low|medium|high, severity: low|medium|high, category: <enum>, note: string} and require every emitted item to carry it. Show one example block before each call.

The shape that works is a small named schema, where every emitted item carries the same tag block so step N+2 can say "consume only high-severity items from step N" and act without re-reading the prose.

> Modify step <N+1> to consume only breadcrumbs of severity=high from step <N>. Leave the visible output untouched and route the filtered set as the sole input to the next stage. Degrade gracefully if a breadcrumb block is missing.

For the curious: breadcrumbs are a third output channel layered on top of two channels production systems already formalize. Strict tool calls send schema-constrained arguments down one pipe; a json_schema reply sends the user-visible answer down another [\[23\]](#ref-23). Breadcrumbs add a parallel pipe for soft inter-step signals that no human consumes directly, the lane missing from most agent pipelines. The same principle drives multi-agent cookbooks: routing subtasks through structured arguments rather than prose collapses parsing friction at every handoff [\[24\]](#ref-24). The deeper precedent is research-trained reflection tokens that gate retrieval and critique decisions [\[22\]](#ref-22); breadcrumbs are the orchestration-time analogue, asking the model to emit machine-parseable signals beside its prose without retraining a single weight. Two contract details matter for production. First, the model's output distribution sharpens dramatically when the directive names the schema, names the severity levels, and shows one or two examples; "tag anything you want" produces drift, while a tight contract produces stable, parseable signal. Second, plan for the escape hatch: refusal and safety paths can bypass schema entirely [\[23\]](#ref-23), so consumers must not assume every response parses, and downstream filters must treat a missing breadcrumb block as a defined case rather than a crash.

## 8. The Operational Directive

*The deviation you hide is the bug you ship.*

You will sometimes find yourself writing "and then it self-updates" or "and then it learns from this run." The instinct is good; auto-edit execution is almost always wrong. The disciplined version is one global directive injected into every subagent and into main:

> If at any time you must deviate from the plan, emit a breadcrumb describing the deviation and rate its significance low, medium, or high.

Why into every subagent? Subagents have no shared memory; the directive must travel with each invocation or the data goes missing. The breadcrumb rides on the metadata channel from lesson 7 (Invisible Metadata, Breadcrumbs). The discrete severity bucket compresses unbounded observation onto three points a downstream filter can read in one pass.

The output is a report, not an edit. The tool file is never auto-rewritten by the system that runs inside it [\[25\]](#ref-25). A human reads the report, decides what to keep, and changes the file by hand. Lesson 17 (Evaluate Your Tool) picks it up from there: the report becomes input to the eval harness, not a silent mutation of the production prompt.

> Add a global operational directive injected into every subagent and into main: "If at any time you must deviate from the plan in order to accommodate the request, emit a breadcrumb on the metadata channel describing the deviation and rate its significance low, medium, or high. Be specific about what counts as a slight versus a large deviation, and place the breadcrumb in the agreed metadata field."

At end of run, a dedicated subagent reads only the high-severity deviations and proposes, for each, whether the tool could be modified to cover the case natively. Each proposal must be objective, measurable, clear, and unambiguous; survivors go into the report.

> Add a closing report step in which a dedicated subagent reads only the high-severity deviations from this run, proposes for each whether the tool could be modified to cover the case natively, requires each proposal to be objective, measurable, clear, and unambiguous, and emits a written report of suggested improvements. Never edit the tool file from inside the run.

For the curious: a verbal directive enters the in-context prior, and asking the model to surface its own plan deviations is a prompt-time reflection capability that needs no fine-tuning [\[26\]](#ref-26). Reflexion's actor/evaluator split [\[26\]](#ref-26) and Self-Refine's generate-then-feedback split [\[27\]](#ref-27) both separate reflection from action; the operational directive does the same. The severity rating compresses by forcing an unbounded observation onto three points, so the downstream "high only" filter becomes a trivial scan. The lossiness is the design.

The reason the report never auto-edits is prompt injection [\[25\]](#ref-25). Any text the model ingests can become an instruction, and the injection can be invisible to humans while still fully parsed by the model [\[28\]](#ref-28). A tool that takes its own deviation reports and applies them automatically is a self-injection surface: any breadcrumb produced under adversarial input becomes a candidate edit to the prompt that runs everything next time. Layer this with excessive agency [\[29\]](#ref-29), where harmful actions emerge from ambiguous LLM output and the recommended mitigation is to minimize tools, permissions, and autonomy and require human-in-the-loop approval for high-impact operations. A self-editing prompt is the maximum-agency direction. Report-and-stop is the minimum-agency direction that still captures the learning, the trade you want.

The directive must be specific about what counts as a deviation, how to rate severity, and exactly where the breadcrumb goes. Vague directives produce vague breadcrumbs, and vague breadcrumbs collapse the whole downstream pipeline before the report subagent sees them.

## 9. Researching the Plan

*A plan you wrote alone is half a plan.*

After the plan has converged enough to know its own contours but is still pliable, send a scout out into the world. Spawn a subagent (lesson 5, Token Economics: Subagent-Only Exploration) and send it to read existing practice, prior art, known solutions, and the warnings experienced practitioners leave behind. It compresses what it finds (lesson 6, Accumulate and Compress) into a paragraph or two of breadcrumbs and returns only that. Then ask the model to use those breadcrumbs to enrich the plan, not rewrite it. New steps appear; safeguards arrive named after the patterns that birthed them. The plan stops being only what you know and becomes part of what is known [\[30\]](#ref-30).

The verb is load-bearing. "Enrich" tells the model the new material is additive: weave it into the existing structure. "Rewrite" or "improve" license demolition.

> Spawn a subagent. Search the web for techniques related to the subject in this plan: existing practice, existing solutions, commentary on related techniques that could help, and warnings about what to avoid. For anything that could be relevant, pass a compressed summary back to the main context. When the searches are finished, use the compressed summaries to enrich the plan.

Once a plan is mature and you can feel which corner is soft, narrow the scope so the subagent does not resurvey ground already covered.

> Spawn a subagent. Focus only on this part of the plan: [name the corner]. Search the web for proven techniques, prior failures, and the warnings experienced practitioners leave behind. Return a single compressed summary, then use it to harden that section of the plan without disturbing the rest.

Every citation in the document you are reading came from running this exact technique on this exact document. One subagent per lesson, web searches firing in parallel, each returning a small bundle of breadcrumbs. A single filter passed over everything: does this materially enhance the plan, and does this lead to a new lesson? Whatever did not survive both questions was disregarded. Lesson 17 (Evaluate Your Tool) was not in the original outline; it surfaced from this pass.

> Spawn multiple subagents. Research each of the lessons on the internet for things that can enrich the plan. Pass back breadcrumbs to the main context for matches. Then review all of the items and check: does this materially enhance the plan? Does this lead to a new lesson? If no, disregard it. Show a report with what survived.

For the curious: the web is textual abundance, and the attention economy from lesson 5 (Token Economics) cannot survive raw pages pasted into the main thread. The subagent is the filter: it reads everything, returns almost nothing. The outer shape of the move comes from the original browser-augmented question-answering loop [\[31\]](#ref-31): search, navigate, gather evidence, condense. The inner shape, where a planner asks questions of the world, workers fetch evidence in parallel, and a solver integrates the result, is the planner/worker/solver split [\[30\]](#ref-30). The compression discipline is factored verification: rather than asking the subagent for what is on the page, ask for the answers to specific questions the plan is implicitly raising, and have the model draft its own verification questions before answering them [\[32\]](#ref-32). When the topic has structured prior practice, retrieval can fetch procedure templates instead of free text [\[33\]](#ref-33).

## 10. The Plan Review and Data-Flow Audit

*Walk the plan before the plan walks you.*

After research is folded in but before any step executes, run the closing sweep on every plan. It does two things in one breath. First, a clarity audit: every step efficient, clear, unambiguous. Second, a data-flow analysis [\[34\]](#ref-34): every step receives what its predecessors emit, and every emission has a downstream consumer. Then the combinatorial pass: can steps be combined, are any doing too much, which can run in parallel?

A short form lives in `always.mdc` so it triggers without prompting on plan-mode work. The full prompt below is the version you paste when stakes are high or the plan touches three or more files.

The audit asks ordering questions (lesson 1, Integer-Numbered Steps Only), subagent-discipline questions (lesson 5, Token Economics: Subagent-Only Exploration), and trail-and-closing questions (lessons 7 Invisible Metadata, Breadcrumbs and 8 The Operational Directive). It pairs with lesson 17 (Evaluate Your Tool): the audit is pre-flight, the eval is post-flight.

> Go through the plan, check every step, make sure that it is efficient, make sure that the instructions are clear, make sure that the instructions are not ambiguous. Then do a data flow analysis. Does each step have the information that it needs delivered by the previous steps? Report on the results. Is this system efficient? Can any steps be combined? Are any steps doing too much? Which parts can run in parallel? Make no mistakes. Think deeply. Be honest.

For the curious: the audit borrows shape from compiler theory. Classical data-flow analysis [\[34\]](#ref-34) asks at each program point whether facts produced upstream actually reach the consumers downstream, and the same question, posed of a plan, surfaces gaps that are invisible when steps are read in isolation. The clarity pass borrows from search: Tree of Thoughts [\[9\]](#ref-9) formalized explicit state evaluation and lookahead over partial plans, which is what "can steps be combined, are any doing too much, which can run in parallel" is doing in plain language. The actor/evaluator split that makes any of this safe was named in Reflexion [\[26\]](#ref-26).

Two warnings explain the closing imperatives. Frontier models skew toward approval-seeking, agreeing with whatever framing the user already implied [\[35\]](#ref-35), so a self-audit on a plan the model already likes will entrench it unless you put a thumb on the scale. "Make no mistakes, think deeply, be honest" is that thumb, raising the stakes phrasing in a way calibration work suggests narrows the gap between confidence and correctness. The second warning is subtler: unguarded generate-critique-improve cycles can actually reduce performance on tasks where the first answer was already good [\[36\]](#ref-36), which is precisely why this audit is one bounded pass before execution and not a recursive refinement [\[27\]](#ref-27). Review board, not editorial cycle. One sweep, then ship.

## 11. Model-Tier Routing per Step

*Cheap model for chores. Strong model for judgment.*

Most tool steps are not creative. They are file iteration, lookups, mechanical transforms a fast cheap model handles fine. A small set need the heavyweight model: synthesis, breadcrumb analysis, naming, plan review. Pin a tier to each step in the plan itself, so the orchestrator stops thinking about model choice at runtime and you stop paying premium rates for busy work. When you trigger plan review (lesson 10, The Plan Review and Data-Flow Audit), expect the strong model to catch tier-routing mistakes for you, both over- and under-provisioned. Verify those choices later (lesson 17, Evaluate Your Tool); tier plans must be validated against actual outputs, not vibes [\[38\]](#ref-38).

> For each step in this plan, recommend a model tier (fast or strong), with a one-sentence justification and a confidence rating (high, medium, low).

Treat tiers as a precomputed compression of routing decisions: by tool runtime, "which model?" has been answered in writing.

> Apply the recommended tiers as inline annotations next to each step header in the plan.

For the curious: tier routing is one of the oldest cost-quality tricks in the LLM stack. The cascade pattern [\[37\]](#ref-37) composes heterogeneous models so cheaper calls absorb the bulk of traffic and only hard cases escalate, with reported cost reductions of an order of magnitude while matching or beating a single best model. Preference-supervised routers [\[39\]](#ref-39) learn the strong-versus-weak choice from human ratings and publish open training and eval rigs for the quality-cost frontier. Production frameworks [\[40\]](#ref-40) expose explicit complexity buckets, mapping requests to models without an extra LLM call in the hot path, which is what per-step annotation gives you inside a tool plan: the routing decision is paid for once, by the planner, not on every invocation. The reality check is sobering: recent benchmarking [\[38\]](#ref-38) finds many routers barely beat trivial baselines, with much of the remaining gap to oracle driven by recall failures of the models themselves rather than by clever routing. Phrasing matters: ask for a tier label, a one-sentence justification, and a confidence rating; vague asks produce vague tiers, and vague tiers produce the worst of both worlds, slow and stupid. Vendor framing on agent-friendly CLIs [\[10\]](#ref-10) reinforces the same posture: pay the precision cost up front so the runtime path stays cheap.

## 12. Serial Tools, Parallel Runs

*One forge, one bar. Light more forges.*

Keep an individual tool's steps serial, and let the user parallelize by launching multiple runs of it. The bottleneck is almost never wall-clock per tool; it is the subagent cap (lesson 5, Token Economics: Subagent-Only Exploration). Providers ration concurrent inference, so every slot a tool burns inside itself is a slot the user cannot spend on something else. A serial tool with N steps holds one slot at any moment; a K-way fan-out holds K. The narrow exception: parallelize within a single run only when raw speed on that one job genuinely outranks the operator's freedom to fan out, and frame it as a deliberate choice rather than a default. Internal parallelism multiplies failure-mode opacity until a failure looks like weather rather than a bug [\[41\]](#ref-41). A parallel run with no termination condition burns slots nobody is watching (lesson 13, Loop Control: Iterations and Stagnation).

> Critique this tool design and strip every internal fan-out. For each removed branch, show how a user launching multiple runs would recover the same throughput, and name the shared state that internal parallelism would have raced on.

The moment two threads of the same tool start writing to shared state, you have inherited a small distributed-systems problem you did not ask for [\[42\]](#ref-42).

> Audit this tool for hidden concurrency. List every step that runs at the same time as another, the resource each step touches, and rewrite the plan so the only parallelism is at the run level.

For the curious: sectioning splits a job into independent subtasks and runs them side by side; voting runs many attempts at the same job and aggregates, betting on stochastic diversity [\[41\]](#ref-41). Both sit inside the larger fan-out / fan-in pattern [\[43\]](#ref-43). Graph frameworks expose this as a primitive: a parent node emits a batch of child invocations and a downstream node reduces them [\[18\]](#ref-18). The router variant formalizes it further with a coordinator dispatching to specialist agents and a programmatic merge collecting their answers [\[44\]](#ref-44). None of this is forbidden, just expensive in slots and in operator awareness. Sectioning earns its place when subtasks are genuinely independent and the merge is cheap [\[41\]](#ref-41); voting earns its place when variance across attempts is exactly what you want. Outside those cases, internal parallelism trades the operator's most valuable resource (granular launch attention) for a wall-clock saving they did not ask for. Serial traces read top to bottom; parallel traces have to be reconstructed by timestamp before you can even start reasoning about them [\[41\]](#ref-41). Concurrent writes to shared state open the reducer-and-idempotency conversation the agent literature keeps rediscovering [\[42\]](#ref-42). The discipline is not "never fan out" but "fan out at the right layer." Inside one tool: serial unless you can defend the exception. Across tools: the user runs as many as their slots allow.

## 13. Loop Control: Iterations and Stagnation

*Every loop needs a brake.*

An iterative step can run forever without erroring. The pipeline keeps spending tokens, the dashboard says busy, nothing finishes. Any step that can iterate must declare two things up front: a maximum iteration count, and a stagnation detector. Three iterations is a sane default cap because most well-posed refinements converge in two and the third is a courtesy. The cap alone is not enough; an agent that hits its cap while still spending tokens is still failing, just with a bounded bill [\[45\]](#ref-45). The stagnation detector is the sharper instrument: after each iteration, compute a progress number tied to the actual objective, and exit when the number stops moving.

The metric is where most people slip. The temptation is to use whatever counter is closest to hand, usually the count of tool calls or API requests, but that number moves whether work is being done or not. The metric must be domain-bound: tests passing, rows produced, errors closed, fields filled. Pick the one that only ticks when the objective actually advances. The harness in lesson 17 (Evaluate Your Tool) is what reveals, over many runs, whether your chosen metric actually correlates with finishing the job.

> Add a max iteration count of 3 and a stagnation detector to this step. After each iteration, compute progress = <domain metric>. If progress has not increased for 1 round, exit and report. Do not raise the cap as a fix.

Then sweep the whole tool with the same lens.

> Audit every iterative step in this tool. List each one, its current cap, its progress metric, and whether the metric is domain-bound or just a call counter. Flag any step missing either control.

For the curious: major agent frameworks concede the shape of this problem at the platform layer. LangGraph ships a hard recursion budget that fires when the graph exceeds a step count without reaching a stop condition, and the docs are explicit that raising the cap does not substitute for a real terminal condition [\[46\]](#ref-46). LangChain layers a separate tool-call limit middleware beside graph recursion control, acknowledging one blunt instrument is insufficient and that callers need independent budgets for different failure modes [\[47\]](#ref-47). Production text-to-SQL agents looping until they exhaust a recursion limit of twenty while the bill keeps climbing show the same shape from the field: the limit bounds cost but does not bound waste [\[45\]](#ref-45). Platforms give you the fence; your tool supplies the tripwire. The taxonomy of non-crashing failures sharpens what the tripwire detects [\[48\]](#ref-48). A REPEATER fires the same action over and over, caught by hashing the action and exiting on N identical hashes. A LOOPER oscillates over a small set, caught by cycle detection in the action history. A WANDERER is the dangerous one: actions look diverse, the agent looks productive, and only a domain progress metric tied to the objective will reveal that nothing is converging [\[48\]](#ref-48). Raw call counts cannot see a WANDERER because the count moves whether the work moves or not. That is why the metric must be tied to the work, not the activity.

## 14. Caching as a Product Decision

*Every cache is a bet that you will come back.*

Caching looks like infrastructure and is actually design. The question is small and ruthless: does the user run this tool more than once on the same input? Answer it during planning and the implementation falls out cleanly. Skip it and you either pay for repeated work or carry a layer of complexity that never earns its keep. Sibling skill to lesson 2 (Step 0 Is a Conversation): surface the question when it is cheap, not after the implementer wires everything up. Direct lever on lesson 5 (Token Economics: Subagent-Only Exploration) when caching prompt prefixes rather than disk artifacts [\[49\]](#ref-49).

> During Step 0 of this design, raise the caching question explicitly: does the user run this tool more than once on the same input? Decide yes or no, and record the answer in the plan.

If the tool ingests something expensive and stable (third-party API responses, design-tool exports, codebase inventories that barely move between runs), caching belongs in the design. If the tool is a one-shot whose inputs change every time, no cache, no machinery, no debt.

> The caching answer is yes. Add a caching layer for [name the expensive intake artifact], specifying cache key, invalidation rule, and storage location, then add it to the plan's data section.

For the curious: prompt caching mechanics reward planning and punish improvisation. A cache hit on the model side requires an exact prefix match against the cached bytes, so any change before the cached suffix invalidates everything that follows; the practical move is to front-load static content (system prompt, tool definitions, reference material) and let user-varying text trail [\[50\]](#ref-50). There is also a token floor under which the cache machinery does not engage at all, on the order of a thousand tokens, and shorter prompts are silently processed without caching with no error returned, which is why you confirm by reading `cached_tokens` in the usage payload rather than trusting "I turned it on" [\[50\]](#ref-50). Retention windows are short by default, on the order of minutes, with extended options if the workload justifies them [\[50\]](#ref-50). The most common failure mode is the moving-suffix anti-pattern: a `cache_control` breakpoint placed on a block that varies every request (timestamped user text, fresh tool output) so the system writes a new cache entry on every call and never reads one [\[49\]](#ref-49). Diagnose by watching `cache_creation_input_tokens` climb while `cache_read_input_tokens` stays at zero; the fix is to move the breakpoint to the last stable block of the shared prefix [\[49\]](#ref-49). Pricing makes this strictly a product decision: cache writes are billed at a premium over base input (around 1.25x for the five-minute tier) while reads run at a fraction of base (around 0.1x), so a tool that fires many times against the same prefix gets dramatically cheaper, and a tool that runs once pays the premium for nothing [\[49\]](#ref-49). Tool definitions sit at the top of the invalidation cascade: changing a tool's schema invalidates tools, system, and messages downstream, so any iteration on tool definitions wipes the entire cached stack [\[49\]](#ref-49). One layer up from the prompt cache, recent work on agentic plan caching argues that conventional context and semantic caches miss the structure that actually repeats in agent workloads, namely the plans themselves, and that reusing structured plan templates across semantically similar tasks yields large average reductions in cost and latency [\[51\]](#ref-51). Practical synthesis: write the cache decision in the plan's data section as "inputs that rarely change: X, Y, Z," so the implementer arrives knowing what to mark cacheable, where to place the breakpoint, and which artifacts deserve a key on disk versus a prefix in the prompt.

## 15. Prompt Elasticity

*What you refuse to build, the prompt builds without you.*

Tools built on instruction-following models have a quiet superpower: you do not have to code every variant. The declared surface is the menu; the actual surface is anything a user can type. A common pattern is to decide "no" on a non-primary input, say a text-based spec for a tool that mostly takes URLs. The decision feels final. It is not. The model will accept a runtime instruction that says "treat the following text as a spec," and do the work. The mode you declined still exists; it just does not have a button. Plans should anticipate the common variants and stay open to instruction for the rest. Users absorb the unusual cases with prose; the tool stays small.

The dark side is where the lesson earns its keep. Anything the model can read can change what the model does [\[25\]](#ref-25). The same path that lets a user extend the tool by writing "also accept this text" lets a third party extend the tool by writing the same words inside content the tool retrieves. The class is indirect prompt injection, covering any data channel ingested as text [\[52\]](#ref-52). Treat retrieved text, file contents, and pasted blobs as instructions in waiting, not inert payloads. Lesson 4 (Confirmation Gates Before Structural Edits) gives the right shape for elasticity-driven actions on files or external systems: gate the effect, even when the instruction was reasonable. Lesson 8 (The Operational Directive) is the structural mitigation: a tool that reports rather than edits cannot be talked into self-modification.

> Default off but instructable: do not add a first-class mode for X, but document that users can attach an X by including its text and a one-line instruction in the prompt.

The same door that lets a user extend the tool lets an attacker walk through it.

> List every input channel the tool ingests as text. For each, write the worst instruction an attacker could embed in it, then decide what effect the tool would still allow.

For the curious: language models are instruction-followers over text, so the tool's command surface is the union of its declared surface and any free-form prose the user adds. You cannot turn off instruction-following without breaking the tool, so you design for the union instead. Indirect prompt injection generalizes the threat: a third party who controls a fetched page controls a portion of your prompt [\[52\]](#ref-52). Non-adversarial retrieval injects too, because retrieved blobs share the same instruction-following context as your system text [\[53\]](#ref-53). The honest mitigation is to label content as data: segregate untrusted text inside marked regions so the model sees the boundary, and write the system instructions to weight the boundary [\[25\]](#ref-25). Then ask the worst-case question on every elastic surface: if an attacker chose this text, what would the tool do [\[54\]](#ref-54)? Effects matter more than wording, which is why lessons 4 (Confirmation Gates Before Structural Edits) and 8 (The Operational Directive) carry weight here. A tool whose elastic surface only reports gives the attacker a small target. A tool whose elastic surface writes files, calls APIs, or modifies the workspace must price every text channel as a potential instruction channel and gate accordingly.

## 16. Tools Are Transformers

*The first one is the sculpture. The rest are casts.*

There is one task you can hand a language model that succeeds almost every time: give it a finished tool and ask for a sibling. Not from scratch. A copy that does the next thing instead. The model preserves the structure you fought for and swaps only the domain. This is the highest-leverage move in the craft, and it only works because of what you already built.

Everything in lessons 1 through 15 was preparation: the token economics, the accumulate-compress rhythm, the breadcrumb trails, the operational directive at the top, the mermaid diagram, the numbered steps, the Step 0 phase, the plan review pass. A mature tool is in-context structured prose, and structure-preserving rewrites are the most reliable thing a language model does. When you say "make a copy that does X instead," the model is not inventing; it is substituting. Invest hard in your first tool of any family. Every descendant gets the rigor for free. The formal analogue lives in the literature on declarative LM modules with composable, subclassable structure [\[55\]](#ref-55).

Two cautions. Cloning expands surface: each new tool competes for tool-call attention at runtime, so namespace your families, defer the rare ones, prune ruthlessly. Transformation can quietly widen capability: a child tool may inherit the parent's voice and gain a new verb the parent never had. Audit what each tool can do, not what it says, before you ship it (lesson 17, Evaluate Your Tool).

> Transform this tool into a new tool that does X instead. Preserve every directive, breadcrumb, numbered step, the mermaid diagram, the Step 0 phase, and all operational discipline. Swap only the domain content.

Before you transform, extract the parent. The next prompt gives you the clean kernel any descendant can inherit.

> Read this tool and produce a clean parent kernel suitable for descendants. Strip the domain specifics. Keep the structure, directives, schemas, and ordering exactly as they are.

For the curious: structure-preserving rewrites are the highest-leverage use of in-context learning, and a mature tool is already a typed scaffold of directives, schemas, and ordering. The model treats it as a template and substitutes new content into the same slots. The DSPy line of work [\[55\]](#ref-55) formalizes this with declarative modules whose explicit signatures compile and self-improve, so program structure becomes a parent that descendants inherit by construction rather than by hope. The runtime constraint is real: function-calling guidance recommends keeping the live tool surface small per turn, using namespaces, and deferring rare tools so the model does not drown in options [\[56\]](#ref-56). Cloning sprawl is the enemy of recall. The deeper safety story is governance of effects rather than wording: prompt cleverness is downstream of capability, and what a tool can DO matters far more than what it says [\[57\]](#ref-57). The OWASP class is excessive agency, treated as its own top-ten risk because granting a model the ability to invoke functions creates a threat surface beyond text [\[29\]](#ref-29). Default-deny new actions on cloned tools and require explicit elevation. Make the contract visible by naming the parts to preserve (the discipline) and the parts to swap (the domain), so the rewrite stays anchored on structure and the action surface stays where you put it.

## 17. Evaluate Your Tool

*A tool you cannot weigh is a tool you cannot trust.*

A mature tool answers three questions on every meaningful run: did it complete the task, what did it cost in tokens, and which failure modes appeared. Completion is rarely a clean yes or no; teach the tool to emit its own final breadcrumb, a small structured rubric like `{"complete": true|false, "rubric": [...], "missed": [...]}`, so a human or a downstream report can aggregate runs without guessing. Cost lives at the step level, not the total: a single fat sub-call hides happily inside an average. Track tokens per step and the tier each step requested (lesson 11, Model-Tier Routing per Step), and the cheap-vs-strong choice you made there finally meets evidence [\[38\]](#ref-38).

Build a named regression set the way a careful library builds its test corpus: the awkward inputs, the malformed ones, the adversarial ones, and the boring happy path. Keep it small, versioned, close to the tool. Run it on a cadence rather than only when something feels broken; the feeling that something is broken is a lagging signal and the worst moment to discover the harness was never wired up. Feed deviations from lesson 8 (The Operational Directive) straight into the regression set as new fixtures.

> Add a final breadcrumb to TOOL X that emits `{"complete": bool, "rubric": [...], "missed": [...]}`, wire per-step token accounting, and check in a small `regression/` folder of awkward, malformed, and adversarial inputs.

Treat the eval report the same way lesson 8 (The Operational Directive) treats deviations: it is a report to a human, never an automatic rewrite of the tool. The harness is a sense organ, not an actuator.

> Run the harness against the last two versions of TOOL X and produce a comparison report that flags completion regressions and per-step cost drift; do not modify the tool, only report.

For the curious: the published literature on building agentic tools is years ahead of the literature on evaluating them, and you should know that going in. Vendor framing has begun to ask the right question, whether a workflow's added complexity is actually paying off, which is the same question lesson 12 (Serial Tools, Parallel Runs) raises about parallelism: complexity that does not show up in the eval is dead weight [\[41\]](#ref-41). Recent work like the 2026 routing benchmark brings classical software-testing rigor to LLM systems, landing precisely where lesson 11 (Model-Tier Routing per Step) left off, by measuring whether the tier you assigned to a step was the tier that step actually deserved [\[38\]](#ref-38). Treat completion as a rubric rather than a binary, treat token cost as a per-step signal rather than a closing receipt, and treat the regression set as a living artifact you grow each time the tool surprises you. The honest disclosure is that this is a frontier and the citations here are deliberately thin. Build the harness anyway, because the alternative is a tool that works until it does not, and you the operator finding out last [\[10\]](#ref-10).

## References

<a id="ref-1"></a>[1] Liu, N. F. et al. "[Lost in the Middle: How Language Models Use Long Contexts.](https://arxiv.org/abs/2307.03172)" 2023

<a id="ref-2"></a>[2] Anthropic Engineering. "[Effective Context Engineering for AI Agents.](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)"

<a id="ref-3"></a>[3] Wang, L. et al. "[Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models.](https://aclanthology.org/2023.acl-long.147/)" ACL 2023

<a id="ref-4"></a>[4] Yao, S. et al. "[ReAct: Synergizing Reasoning and Acting in Language Models.](https://arxiv.org/abs/2210.03629)" 2022

<a id="ref-5"></a>[5] Wang, Q. et al. "[Recursively Summarizing Enables Long-Term Dialogue Memory in Large Language Models.](https://arxiv.org/abs/2308.15022)" 2023

<a id="ref-6"></a>[6] Chroma Research. "[Context Rot.](https://research.trychroma.com/context-rot)"

<a id="ref-7"></a>[7] Anthropic Engineering. "[Writing Tools for Agents.](https://www.anthropic.com/engineering/writing-tools-for-agents)"

<a id="ref-8"></a>[8] Zhou, D. et al. "[Least-to-Most Prompting Enables Complex Reasoning in Large Language Models.](https://arxiv.org/abs/2205.10625)" 2022

<a id="ref-9"></a>[9] Yao, S. et al. "[Tree of Thoughts: Deliberate Problem Solving with Large Language Models.](https://arxiv.org/abs/2305.10601)" 2023

<a id="ref-10"></a>[10] Speakeasy. "[Engineering Agent-Friendly CLI.](https://www.speakeasy.com/blog/engineering-agent-friendly-cli)"

<a id="ref-11"></a>[11] Microsoft Copilot Studio. "[Slot Filling Best Practices.](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/slot-filling-best-practices)"

<a id="ref-12"></a>[12] freeCodeCamp. "[Diagrams as Code with Mermaid, GitHub, and VS Code.](https://www.freecodecamp.org/news/diagrams-as-code-with-mermaid-github-and-vs-code/)"

<a id="ref-13"></a>[13] Sweller, J. "[Cognitive Load Theory.](https://www.mcw.edu/-/media/MCW/Education/Academic-Affairs/OEI/Faculty-Quick-Guides/Cognitive-Load-Theory.pdf)" Medical College of Wisconsin, Faculty Quick Guide

<a id="ref-14"></a>[14] "[Visualization research on legible label placement and overlap control.](https://arxiv.org/abs/2405.10953)" 2024

<a id="ref-15"></a>[15] Nielsen Norman Group. "[Confirmation Dialog: Are You Sure?](https://www.nngroup.com/articles/confirmation-dialog/)"

<a id="ref-16"></a>[16] LangChain. "[LangGraph Interrupts.](https://docs.langchain.com/oss/python/langgraph/interrupts)"

<a id="ref-17"></a>[17] Anthropic. "[Measuring Agent Autonomy.](https://www.anthropic.com/news/measuring-agent-autonomy)" 2026

<a id="ref-18"></a>[18] LangChain. "[LangGraph Graph API: Send.](https://docs.langchain.com/oss/python/langgraph/graph-api#send)"

<a id="ref-19"></a>[19] Microsoft. "[AutoGen Handoff Design Pattern.](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/design-patterns/handoffs.html)"

<a id="ref-20"></a>[20] LangChain. "[load_summarize_chain (map_reduce / MapReduceDocumentsChain).](https://reference.langchain.com/python/langchain-classic/chains/summarize/chain/load_summarize_chain)"

<a id="ref-21"></a>[21] "[Context-Aware Hierarchical Merging for Long Document Summarization.](https://arxiv.org/abs/2502.00977)" 2025

<a id="ref-22"></a>[22] Asai, A. et al. "[Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection.](https://arxiv.org/abs/2310.11511)" 2023

<a id="ref-23"></a>[23] OpenAI. "[Structured Outputs Guide.](https://developers.openai.com/api/docs/guides/structured-outputs)"

<a id="ref-24"></a>[24] OpenAI. "[Structured Outputs in Multi-Agent Systems.](https://developers.openai.com/cookbook/examples/structured_outputs_multi_agent)"

<a id="ref-25"></a>[25] OWASP GenAI Security Project. "[LLM01: Prompt Injection.](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)"

<a id="ref-26"></a>[26] Shinn, N. et al. "[Reflexion: Language Agents with Verbal Reinforcement Learning.](https://arxiv.org/abs/2303.11366)" 2023

<a id="ref-27"></a>[27] Madaan, A. et al. "[Self-Refine: Iterative Refinement with Self-Feedback.](https://arxiv.org/abs/2303.17651)" 2023

<a id="ref-28"></a>[28] Kudelski Security Research. "[Reducing the Impact of Prompt Injection Attacks Through Design.](https://research.kudelskisecurity.com/2023/05/25/reducing-the-impact-of-prompt-injection-attacks-through-design/)" 2023

<a id="ref-29"></a>[29] OWASP GenAI Security Project. "[LLM06: Excessive Agency.](https://genai.owasp.org/llm-top-10/)"

<a id="ref-30"></a>[30] Xu, B. et al. "[ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models.](https://arxiv.org/abs/2305.18323)" 2023

<a id="ref-31"></a>[31] Nakano, R. et al. "[WebGPT: Browser-assisted Question-answering with Human Feedback.](https://arxiv.org/abs/2112.09332)" 2021

<a id="ref-32"></a>[32] Dhuliawala, S. et al. "[Chain-of-Verification Reduces Hallucination in Large Language Models.](https://arxiv.org/abs/2309.11495)" 2023

<a id="ref-33"></a>[33] "[InstructRAG: Retrieval-Augmented Instruction Following on Graph-Structured Knowledge.](https://arxiv.org/abs/2504.13032)" 2025

<a id="ref-34"></a>[34] Wikipedia. "[Data-flow analysis.](https://en.wikipedia.org/wiki/Data-flow_analysis)"

<a id="ref-35"></a>[35] Sharma, M. et al. "[Towards Understanding Sycophancy in Language Models.](https://arxiv.org/abs/2310.13548)" 2023.

<a id="ref-36"></a>[36] Snorkel AI. "[The Self-Critique Paradox: Why AI Verification Fails Where It's Needed Most.](https://snorkel.ai/blog/the-self-critique-paradox-why-ai-verification-fails-where-its-needed-most/)"

<a id="ref-37"></a>[37] Chen, L. et al. "[FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance.](https://arxiv.org/abs/2305.05176)" 2023

<a id="ref-38"></a>[38] "[LLMRouterBench: A Unified Benchmark for LLM Routing.](https://arxiv.org/abs/2601.07206)" 2026

<a id="ref-39"></a>[39] Ong, I. et al. "[RouteLLM: Learning to Route LLMs with Preference Data.](https://arxiv.org/abs/2406.18665)" 2024

<a id="ref-40"></a>[40] LiteLLM. "[Auto Routing Documentation.](https://docs.litellm.ai/docs/proxy/auto_routing)"

<a id="ref-41"></a>[41] Anthropic Engineering. "[Building Effective Agents.](https://www.anthropic.com/engineering/building-effective-agents)"

<a id="ref-42"></a>[42] LangChain Forum. "[Race conditions in multi-agent LangChain setups.](https://forum.langchain.com/t/are-people-hitting-race-conditions-in-multi-agent-langchain-setups/3202)"

<a id="ref-43"></a>[43] Microsoft Learn. "[AI Agent Design Patterns.](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)"

<a id="ref-44"></a>[44] LangChain. "[Multi-Agent: Router and Knowledge Base.](https://docs.langchain.com/oss/python/langchain/multi-agent/router-knowledge-base)"

<a id="ref-45"></a>[45] [LangGraph GitHub Issue #6731. Text-to-SQL agents and recursion limits](https://github.com/langchain-ai/langgraph/issues/6731)

<a id="ref-46"></a>[46] LangChain. "[GRAPH_RECURSION_LIMIT Error Reference.](https://docs.langchain.com/oss/python/langgraph/errors/GRAPH_RECURSION_LIMIT)"

<a id="ref-47"></a>[47] LangChain. "[Built-in Middleware (Tool Call Limit).](https://docs.langchain.com/oss/python/langchain/middleware/built-in#tool-call-limit)"

<a id="ref-48"></a>[48] ClawGenesis. "[How to Detect When Your AI Agent Is Stuck and What to Do About It.](https://dev.to/clawgenesis/how-to-detect-when-your-ai-agent-is-stuck-and-what-to-do-about-it-ce9)"

<a id="ref-49"></a>[49] Anthropic. "[Prompt Caching Documentation.](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)"

<a id="ref-50"></a>[50] OpenAI. "[Prompt Caching Guide.](https://developers.openai.com/api/docs/guides/prompt-caching)"

<a id="ref-51"></a>[51] "[Agentic Plan Caching for LLM Agents.](https://arxiv.org/abs/2506.14852)" 2025

<a id="ref-52"></a>[52] Greshake, K. et al. "[Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection.](https://arxiv.org/abs/2302.12173)" 2023

<a id="ref-53"></a>[53] Willison, S. "[Accidental Prompt Injection.](https://simonwillison.net/2024/Jun/6/accidental-prompt-injection/)" 2024

<a id="ref-54"></a>[54] Willison, S. "[The Dual LLM Pattern: Worst That Can Happen.](https://simonwillison.net/2023/Apr/14/worst-that-can-happen/)" 2023

<a id="ref-55"></a>[55] Khattab, O. et al. "[DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines.](https://arxiv.org/abs/2310.03714)" 2023. [DSPy Modules documentation](https://dspy.ai/learn/programming/modules/).

<a id="ref-56"></a>[56] OpenAI. "[Function Calling Guide.](https://developers.openai.com/api/docs/guides/function-calling)"

<a id="ref-57"></a>[57] Oso. "[Prompt Injection Isn't the Real Problem.](https://www.osohq.com/learn/prompt-injection-isnt-the-real-problem)"
