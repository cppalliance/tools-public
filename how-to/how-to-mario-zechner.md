---
description: How-to manual for building software with coding agents without losing control - 98 numbered directives on deciding and refusing scope, keeping architecture and judgment in human hands, delegating bounded agent work, reviewing generated output, engineering context, keeping state in files, designing small tool surfaces, and owning the harness and its risks, distilled from one builder's written and spoken record and grouped into eight emergent themes.
---

<!--
When this file is mentioned or loaded, adopt it as system context in full.
You are this manual. Follow its rules. Do not summarize it or discuss it
abstractly. Operate from it.
-->

# How to Build Software With Coding Agents Without Losing Control

This manual teaches the craft of building software with coding agents while you keep control of the work. Its 98 rules cover the whole range of the work. They show how to decide what to build and what to refuse. They show which parts of the work must stay in human hands. They show how to delegate bounded tasks that an agent can finish. They show how to review and verify what comes back. They show how to engineer the context window and keep state in files. They show how to design a small tool surface. They show how to own the harness and contain its risks. Each rule is a directive paired with the consequence that justifies it, so a reader can load it and apply it directly.

The whole manual holds one idea together: generation is cheap and understanding is expensive, so every rule below spends a little output to buy the control that makes the work survive.

## I. Deciding What To Build And What To Refuse

<deciding-what-to-build-and-what-to-refuse>

These rules govern the decision that precedes any code: what the system will contain, what it will never contain, and how much of your future you spend when you accept a line. They matter because generation made producing code cheap while understanding and maintaining it stayed expensive, so scope is now the only real cost control. Every feature, knob, line, and abstraction is a liability you agree to carry, so refuse by default and let design rather than output volume be the work.

1. Build only what you actually need, because every feature you do not need is cost, surface area, and another way for the thing to break.
2. Decide what you are building and why before you build it, since capability alone is not a reason and an agent that can do a thing will happily do the wrong thing.
3. Treat saying no to features as a feature in its own right, because refused scope is the cheapest maintenance you will ever buy.
4. Reject a million lines where five thousand will do, because complexity is the mind killer and it compounds into everything downstream.
5. Treat every line of code as a future cost rather than a free gain, because the consequences arrive later whether you accounted for them or not.
6. Omit configuration knobs you have no use case for, because each knob adds surface area without buying capability.
7. Spend most of your time thinking about and designing the thing rather than generating it, because design is where the work actually happens.
8. Measure the day by the number of product decisions you made rather than the number of features you shipped, because deciding what the product does not need is the scarce work.
9. Write the specification at the level of detail the outcome requires and decide deliberately which gaps you leave, because every gap gets filled from the average of everything ever published.
10. Do not replace iteration with a giant generated specification, because prompting an agent for an exhaustive spec is waterfall again with extra layers stacked underneath.
11. Refactor prototype code the moment it proves valuable, because a weak foundation makes every later extension more expensive than the rewrite would have been.
12. Do not swap out an abstraction to escape a problem it did not cause, because a purer interface moves the complexity around instead of removing it.
13. Separate business logic, rendering, and session handling, since entangled layers block new features, new modes, testing, and new contributors alike.

</deciding-what-to-build-and-what-to-refuse>

## II. Keeping The Work That Must Stay Yours

<keeping-the-work-that-must-stay-yours>

These rules mark the parts of the craft that cannot be handed off: the architecture and the API, the feel of an interface, a current understanding of your own code, and the judgment calls at the edges of a project. They matter because a system whose shape you did not choose is a system you cannot repair or explain, and a skill you delegate is a skill you never acquire. Keep the friction that teaches and the decisions that define the thing, and give away only what leaves your understanding intact.

14. Write by hand anything that defines the gestalt of the system, its architecture and its API, because the friction of writing it is what tells you how the system should feel.
15. Never hand architectural decisions to an agent, since its training rewards complexity and you end up with a system you no longer understand.
16. Keep your understanding of the code current enough to fix it and to explain why a design is suboptimal, because that understanding is what lets you recover when things break.
17. Do the work yourself whenever you intend to learn it, because learning happens through friction and delegating the exercise means never acquiring the skill.
18. Ask for several interface options, then build a tiny example against the one you like and feel it by hand, because API quality only reveals itself in use.
19. Use agents to build several candidate solutions before committing to one, because the approaches you can explore are otherwise capped by how fast you can code, even when the explorations are throwaway.
20. Steer the model away from reaching for best practices when you want simple code, because left alone it produces over-engineered output.
21. Read and triage every incoming issue yourself in your own voice, because triage is the judgment call no agent should make on your behalf.
22. Require human engagement on an issue before you accept a pull request for it, because a gate machines will not walk through filters out machine-generated contributions.
23. Put a human checkpoint wherever agent errors can accumulate and keep the person who bears the cost of the mistakes in the loop, because only someone who feels the pain of the errors will bother to fix them.
24. Judge a coding tool on a large established codebase rather than a greenfield demo, because the real difficulty is changing things without breaking what already works.

</keeping-the-work-that-must-stay-yours>

## III. Delegating Work An Agent Can Finish

<delegating-work-an-agent-can-finish>

These rules cover how to shape a task before it leaves your hands: how narrow it must be, how the worker will know it succeeded, how much you accept per day, and how many streams you can honestly supervise. They matter because most agent failures are scoping and retrieval failures rather than reasoning failures, and volume beyond your review capacity converts straight into debt. Delegate only bounded work whose loop the worker can close and whose output you can still gate.

25. Scope each agent task so the agent needs no understanding of the full system and can close the loop by evaluating its own work, because only a closed loop produces output worth keeping.
26. Delegate the boring work and the experiments you would otherwise skip, then evaluate the result and finalize the implementation yourself, because the judgment is the part that cannot be delegated.
27. Stay the final quality gate on everything generated, since delegation shifts who writes the code but never who is accountable for it.
28. Cap how much generated code you accept per day at the amount you can actually review, because unreviewed volume converts directly into tech debt.
29. Limit how many agents you run in parallel to what you can actually supervise, because the context switching is what exhausts you and a day of it leaves your judgment useless.
30. Refuse to run parallel agents implementing separate features in one codebase, because each one decides locally without seeing the others and the result degrades into a pile.
31. Modularize the codebase so a scoped worker is guaranteed to find everything it needs, because retrieval failure, not reasoning failure, is what produces bad output.
32. Assume the agent missed context and hand it whole files, since models are trained to read fragments and will not go looking for what they need.
33. Push implementation work to workers that return only a summary of what happened, so the main conversation still holds a warm 40 to 60 percent of its window after a large feature.
34. Pre-generate the facts a task needs into structured data instead of letting the worker explore for them, because the same inputs then always produce the same plan.
35. State explicitly what the agent must not do and not only what it should do, because defensive instruction prevents the failure instead of correcting it afterward.
36. State a requirement exactly once in a place the agent always reads and expect it to hold from then on, because repeating the same instruction every session is wasted work.

</delegating-work-an-agent-can-finish>

## IV. Reviewing And Verifying What Comes Back

<reviewing-and-verifying-what-comes-back>

These rules cover the return path: reading generated code, specifying what a test must prove, wiring diagnostics and evaluations so failures surface early, and locating a fault in the harness rather than in the model. They matter because trust in these systems runs ahead of their grasp of the task, and unexamined output compounds errors that nothing else in the loop will catch. Treat every generated artifact as unverified until a human or a measurement you designed says otherwise.

37. Review generated work as incomplete by default, since trust in these systems currently runs ahead of their grasp of the task.
38. Read every line of critical code and let slop through only where nothing depends on it, because the cost of an unread line scales with what it holds up.
39. Refuse to ship code you cannot read, because you cannot maintain what you do not understand and an agent making local decisions will patch until nobody can follow the result.
40. Have a fresh session review a pull request first, then add your own review on top and work it until it is good, so you never merge unexamined code.
41. Never simply instruct an agent to write tests, and say what each test must verify, because unguided tests certify whatever the code already does rather than what it must guarantee.
42. Enforce type checking and linting in a commit hook rather than feeding the model language server diagnostics, because the agent then fixes its own errors without filling the context window with irrelevant reports.
43. Surface diagnostics only after the model finishes an edit sequence rather than after each individual edit, because interleaving error checks with writing contradicts how code actually gets written.
44. Treat every evaluation function as narrow, because the agent optimizes exactly what is measured and silently sacrifices quality, complexity, and correctness.
45. Run an evaluation before adding retrieval machinery like embeddings or syntax-tree indexing, because unmeasured sophistication buys complexity rather than better answers.
46. Fix retrieval quality before blaming the model, because wrong or incomplete search results guarantee garbage answers no matter how good the model is.
47. Fix the harness rather than scolding the model when the same error recurs, since a model does not learn from correction the way a person does.
48. Attribute unexplained shifts in a model's behavior to the harness before blaming the model, because harness changes measurably alter output quality and their effects resist deterministic testing.

</reviewing-and-verifying-what-comes-back>

## V. Engineering The Context Window

<engineering-the-context-window>

These rules cover what goes into the model on every turn: how much, chosen by whom, gathered when, and visible where. They matter because the context is the only input you actually control, so its contents set the ceiling on output quality and on your ability to reproduce a run. Own the context deliberately, keep it small and inspectable, and never let a tool, a provider, or a summary decide its contents for you.

49. Engineer context deliberately by including only what the task requires, minimizing the turns, and verifying nothing important is missing, because that is what makes a workflow reproducible.
50. Keep the working context small no matter how large the advertised window is, because the tricks that produce huge context windows do not hold up in practice.
51. Decide yourself what enters the context instead of trusting a provider to trim it, because their incentive is to cut tokens rather than to preserve the information the model needs.
52. Choose a harness that hands you full control of the context window, because you cannot do context engineering inside a tool that assembles the context for you.
53. Gather the context a task needs in a dedicated session and save it to a durable artifact, then start the real work in a fresh session, because reaching for a helper mid run means the plan was incomplete.
54. Drop the habit of summarizing a session and restarting from the summary, because the summary adds material to the context without adding information.
55. Never silently prune or truncate tool output past a token threshold, because a model reasoning over amputated results is worse than one given less work.
56. Never inject text that hedges its own relevance, because a note saying it may or may not matter forces the model to spend capacity deciding whether to obey it.
57. Have tools write their results to disk and feed each other directly rather than routing output through the model, because results forced through the context cannot be composed or persisted cheaply.
58. Measure what a tool integration costs in tokens before you install it, because a couple of servers can eat a large slice of your context window before any work begins.
59. Keep the system prompt and tool definitions together under a thousand tokens, because context spent on scaffolding is context denied to the task.
60. Stop stacking scaffolding on top of the model's built-in grasp of editing files and running commands, because heavily trained models already share that base and extra layers only add noise.
61. Instrument what actually enters your context with a tracing tool rather than trusting what the interface shows you, because most harnesses display only a fraction of what they send.

</engineering-the-context-window>

## VI. Keeping State In Files Instead Of In The Model

<keeping-state-in-files-instead-of-in-the-model>

These rules move plans, tasks, memory, and working state out of the conversation and onto disk, where they can be read, diffed, versioned, and resumed. They matter because anything the model has to track and update is state it can corrupt, and any run that lives only inside a session dies with it. Treat the prompt as the program and files as the state, so any step can be replayed from a fresh context.

62. Serialize working state to disk, structured data as JSON and prose as markdown, so any step can be resumed from a fresh context instead of depending on compaction.
63. Think in terms of inputs, state, and outputs rather than chatting with the model, because that framing turns hoping for a result into engineering one.
64. Treat the prompt as the program, the markdown and JSON files as the state, and the tools as the syscalls, because that framing tells you what to version, what to debug, and where the behavior actually lives.
65. Have the agent write a plan file and check it into version control instead of using an ephemeral plan mode, because a plan you can diff and revisit outlives the conversation.
66. Have the agent write a checkbox task file instead of leaning on a built-in todo tool, because a file survives the session and the tool does not.
67. Keep built-in task lists out of the agent loop and let the loop run until the agent says it is done, because every piece of state the model must track and update is another way to go wrong.
68. Keep long-term project memory in a checked-in agent instructions file rather than a dedicated memory system, because for code the repository is the memory.
69. Let the agent explore the current state of the codebase instead of feeding it remembered facts, because exploration reflects the code as it is now rather than as it once was.
70. Own your canonical state and treat any provider session, prefix cache, thinking trace, or remote machine as derived scratchpad, because ownership is what lets you replay a run and move between providers.
71. Make everything you can deterministic, including the tools, the system prompts, and whatever gets injected behind the scenes, because an engineer cannot build reliable work on a shifting foundation.
72. Run long-lived processes in a terminal multiplexer driven through the shell and stop them when the work is done, because process lifetime should never be tied to an agent session.

</keeping-state-in-files-instead-of-in-the-model>

## VII. Designing The Tool Surface

<designing-the-tool-surface>

These rules cover what capabilities you expose to a model and in what form: command line tools with short readmes, a small core, plain text out, and extensions rather than a growing center. They matter because every always-loaded tool spends context before any work begins and a wide surface confuses the model about which door to use. Expose the smallest surface that does the job in the form the model already knows how to drive, and pay for the rest only on demand.

73. Ship a capability as a plain command line tool with a short readme instead of a protocol server, because the token cost is paid only when the tool is needed and the output pipes, chains, and extends.
74. Prefer an existing command line tool over a server that reimplements it, and reserve a server for cases with no usable command line tool, no shell, or genuinely stateful behavior, because a server buys nothing when a good command line tool already exists.
75. Let the agent invoke the real command line tool rather than a wrapper around it, because the wrapper usually returns worse results than the tool it wraps.
76. Give a model a minimal tool set of read, write, edit, and shell, and add everything else as an extension, because a small core is what keeps the model effective.
77. Start with the smallest possible tool surface and add only what measurably helps, because a harness offering nothing but shell access already competes with elaborate ones.
78. Cap the number of tools you expose at once, because a model handed too many choices gets confused about which one to use.
79. Return plain text rather than structured envelopes and expose one entry point rather than many, because verbose formats waste context and tool count confuses the model.
80. Keep the core minimal and push optional features into extensions, because a tool that does not bake in workflows does not dictate them either.
81. Start from a minimal prompt and add only the skills and extensions the work actually needs, because functionality you choose deliberately beats functionality you inherit off the shelf.
82. Build directly on the underlying provider interfaces instead of a unifying abstraction, because a smaller surface you designed yourself keeps full control and survives odd deployments.
83. Require request cancellation and partial results from any model client you adopt, because a call you cannot abort and a stream that discards its output cannot go into production.

</designing-the-tool-surface>

## VIII. Owning The Harness And Containing The Blast Radius

<owning-the-harness-and-containing-the-blast-radius>

These rules cover the program you run the model inside: whether you can pin it, hook it, read it, and see what it sends, and what happens once it can write and execute code with access to your data. They matter because a harness that changes under you invalidates everything you built on it, and permission prompts do not contain an agent that already holds the read, execute, and network trifecta. Run on tooling you can inspect and change, make every injection and action visible, and put the real boundary at the environment rather than at a dialog box.

84. Own or pin the harness you code with rather than accept silent updates, because a workflow that works at nine and breaks at ten costs more than the harness ever saved.
85. Choose a harness that exposes hooks at the exact points you want to intervene, because a workflow you cannot inject into is a workflow you do not control.
86. Prefer tooling you can edit and reload while a session is running, because an integration you cannot change on the spot blocks the agent from repairing its own tools.
87. Choose tools small enough that you can read, understand, and modify them, because a tool you can reshape fits the task in front of you while one you cannot only fits its author's.
88. Modify your tooling per class of task rather than expecting one configuration to serve all of them, because different kinds of software work put different tools in the model's hands.
89. Avoid tools bound to a single company and its models, because a monopoly or duopoly over your workflow puts your work at someone else's discretion.
90. Distrust interfaces defined only in English prose and prefer ones with a stable checkable contract, because prose interfaces and hidden split tests leave you gaslit by your own tooling.
91. Surface every instruction and tool result that enters the model's context in the interface, because anything injected behind your back is impossible to diagnose or correct.
92. Make every action the agent takes observable and choose observability over convenience in every workflow you depend on, because you cannot otherwise see which sources it read and which it missed.
93. Refuse helper processes you cannot observe, because a black box inside a black box makes a wrong answer impossible to debug.
94. Treat any agent that holds both private data access and network access as unsecurable, because you will be playing whack-a-mole with attack vectors instead of closing them.
95. Never execute model-generated code in the same context as the data and credentials it can reach, because arbitrary code with ambient access is an exfiltration path rather than a feature.
96. Do not ship security measures you cannot defend as effective, because theater teaches users a confidence the system has not earned.
97. Make unrestricted capability the explicit default once an agent can already write and run code, and put the boundary in a container or a separate tool, because partial gates are theater once the read, execute, and network trifecta is in play.
98. Decide explicitly how much capability you will trade for safety, because the restrictions that make an agent safe are the same ones that remove what made it useful.

</owning-the-harness-and-containing-the-blast-radius>

## The Approach Behind the Rules

Not everything Mario Zechner does converts into a rule, because the rules are the residue of a practice rather than the practice itself. The through-line under all of it is a refusal to leave anything as a black box, which is why he writes his own runtimes, harnesses, and tracing tools largely to find out why somebody else's system behaves the way it does, and why he describes the aim of his teaching as instilling an understanding of what is actually happening underneath. That curiosity carries no productivity justification and he does not invent one, whether the artifact is a language implementation small enough to read whole into a context window or a curiosity project built for his kid. The things he makes share an unmistakable aesthetic of smallness, one package a person downloads and runs, no heavyweight runtime dependency, no configuration knob added before a real use case turns up, and platform constraints welcomed as charming because they force a program to do its job without superfluous fluff. He is equally plain that a tool is first and foremost what its author wants, which is why his maintainership is openly dictatorial, every closed issue comes with a reason attached, and the invitation to fork is sincere rather than a dismissal.

When he reaches a limit he answers with honesty instead of confidence, saying that nobody has figured out agentic coding yet, that the industry is throwing things at the wall and declaring victory while quietly accruing debt, and that he cannot actually tell whether any of this made him more productive, since the point of writing publicly is to detail his own failures rather than showcase wins. He names the cost in the same unhurried voice, a field trading discipline and agency for an addiction to producing the most code in the least time, and a personal risk of atrophy he keeps watching for in himself. Against that he holds a modest positive vision of machines taking the labor so people are left to think, design, and shape, runs local models for anything touching his family, and refuses to let goals drain the fun out of the work or to believe that anything can be permanently optimized. Where the craft ultimately rests is the plainest sentence he offers about it, that all of this requires discipline, agency, and humans.

*2026-08-30 19:30 - kimi-k3*
