---
description: Reference for evaluating C++ language and library designs through evidence, user value, minimal scope, semantic interfaces, layering, generic composition, dependency control, measurable cost, and safety
---

<!-- Load this file into context before reviewing a C++ proposal, weighing a design, or arguing a committee position. Operate from it as a design-evaluation rulebook, consulting the sections most relevant to the question. -->

# Design-Evaluation Rulebook: Vinnie

<overview>

This file equips a reader to judge C++ language and library designs through evidence-first, user-centered engineering. Apply its rules to proposals, APIs, implementations, and standardization choices by testing claims against working use cases, preserving clear semantic boundaries, and accounting for permanent ecosystem costs. Rules are numbered continuously across sections so each rule has a unique reference.

</overview>

<general-principle>

**The binding idea**. Start from measurable user value, require working evidence, keep primitives narrow and layered, express semantics in types and interfaces, isolate dependencies, preserve composition, expose policy choices, and make every permanent cost and safety trade-off explicit.

</general-principle>

![Design-evaluation rulebook](images/how-to-vinnie.png)

## I. Evidence and Standardization

<evidence-and-standardization>

This group covers the evidence and value thresholds that proposals must meet before they become permanent shared infrastructure. It matters because standardization imposes lasting costs on implementers, users, and the ecosystem. Require demonstrated collective value to outweigh every irreversible obligation.

1. Evaluate a feature's collective benefit against its adoption and maintenance costs; technical feasibility alone does not justify standardization.
2. Publish and support a library before standardizing it; real users reveal design flaws and provide measurable evidence of demand.
3. Require diverse field use before standardizing a component; mature implementation experience removes surprises.
4. Reuse designs proven across implementations and platforms; accumulated practice is stronger evidence than committee invention.
5. Require a preponderance of evidence before imposing a permanent interface; standardization creates an enduring collective obligation.
6. Demand implementations and measurements before making permanent semantic choices; untested assumptions do not establish performance or compatibility.
7. Treat claims about a design's benefits as empirical questions; direct comparison reveals whether its promises hold.
8. Discount demand from people who will not bear a feature's costs; unpriced enthusiasm systematically overstates value.
9. Prefer the conservative reversible choice when evidence is incomplete; deployed freedoms cannot reliably be withdrawn.
10. Start with established models and switch only when evidence shows they cannot be salvaged; compatibility should yield to demonstrated need rather than novelty.
11. Require new frameworks to outperform battle-tested solutions in working common cases; novelty alone does not justify adoption.
12. Standardize shared surfaces that improve interoperability rather than private machinery; common vocabulary creates more value than uniform internals.
13. Standardize portable building blocks before prescribing policy; users can compose specialized solutions without surrendering flexibility or performance.

</evidence-and-standardization>

## II. Goals and User Validation

<goals-and-user-validation>

This group covers how to ground a design in explicit goals, working use cases, and understandable evidence. It matters because speculative abstractions and unclear explanations prevent reliable evaluation. Start from user-visible utility and make every design claim testable against it.

14. State the design goal clearly enough to weigh every choice against it; a list of possible uses cannot substitute for decision criteria.
15. Begin with the actual code users will write; the call site reveals whether the problem and abstraction are understood.
16. Implement a use case end to end before proposing its abstraction; working code separates demonstrated design from speculation.
17. Ship a complete usable vertical slice with new machinery; users need immediate value rather than scaffolding for future work.
18. Ship usable library types with new language machinery; machinery without an immediate surface inverts the delivery of user value.
19. Turn motivating use cases into examples and tutorials; a design driven by real usage should teach itself through that usage.
20. Give reviewers a stable revision while preserving later revision cycles; evaluation requires a known target without stopping improvement.
21. Lead an explanation with the smallest reproducible failure; a visible bug or cost makes the remedy concrete.
22. Build the learning path in small evidence-backed steps; readers should never need to accept the next claim on faith.
23. Put the burden of explanation on the expert; adoption depends on making invisible problems understandable to the intended audience.
24. Separate inherent problem complexity from incidental library complexity; users may reject the whole design when the two are confused.
25. Choose the design that serves users over the long term; sound judgment must resolve trade-offs that knowledge alone cannot.

</goals-and-user-validation>

## III. Simplicity and Scope

<simplicity-and-scope>

This group covers keeping abstractions focused, economical, and proportionate to their jobs. It matters because every extra feature creates permanent cognitive, maintenance, and interaction costs. Remove accidental complexity and retain only the smallest coherent solution.

26. Pursue simplicity as a reliability requirement; designs survive transmission only when others can understand and reproduce them.
27. Prefer global simplicity over local familiarity; a familiar local choice can multiply complexity across the system.
28. Make abstractions reduce the code users must write; added ceremony defeats their purpose.
29. Keep each abstraction narrow around one essential property; all-powerful interfaces lose semantic meaning.
30. Prefer the thinnest sufficient primitive; minimal foundational change limits interaction risk, specification growth, and maintenance cost.
31. Keep language and foundational library primitives thin; permanent features compound interaction, specification, and maintenance risk.
32. Remove every feature that does not serve the user; each inclusion creates lasting learning, maintenance, and failure costs.
33. Reduce accidental complexity while preserving essential complexity; good design removes tool-created difficulty without pretending the problem is simple.
34. Keep each library focused on one task it performs well; narrow scope reduces duplication and preserves composability.
35. Separate use cases whose optimized implementations share little machinery; forcing them into one library creates false coupling.
36. Keep policy abstractions narrowly defined; expanding them into schedulers or event loops destroys their distinct role.
37. Seek a universal primitive only when its user-facing complexity is justified; theoretical unification can cost more than multiple strategies.
38. Seek designs that preserve theoretical coherence and practical utility; treating them as alternatives discards achievable value.

</simplicity-and-scope>

## IV. Semantic Interface Design

<semantic-interface-design>

This group covers expressing the right meaning, invariants, ownership, and behavior in an interface. It matters because representational accidents and vague contracts create incorrect mental models. Make every interface state its semantic claim and expose its obligations precisely.

39. Use types to express the semantic claim of an interface; representational convenience must not narrow the operation's meaning.
40. Name interfaces by semantic role rather than incidental representation; accurate names remain valid across conforming implementations.
41. Define a vocabulary type by the invariant and capabilities it preserves; representational fidelity establishes why it deserves first-class status.
42. Specify ownership distinctions explicitly; owning and non-owning models have different behavior that users and implementers must understand.
43. Treat invariants of non-owning types as explicit caller obligations; the type cannot enforce what ownership would guarantee.
44. Make unsafe construction conspicuous, searchable, and consistent with established conventions; reviewers must be able to find every escape from safety.
45. Make every operation predictable about behavior and cost; the programmer's mental model must remain accurate.
46. Absorb implementation constraints inside the design; users should receive capability rather than inherit machinery.
47. Make constraints enable legitimate operations; requirements that reject well-formed intent turn abstraction into obstruction.
48. Preserve proven interfaces unless an alternative solves real problems without worse consequences; superficial consistency does not justify disruption.
49. Prefer proven utility over superficial consistency; replacing working interfaces with uniform ones can introduce new types and problems.
50. Prefer stable data containers over standardized parsers when parsers remain implementation details; public representations create the interoperability.
51. Prefer explicit failure over silent corruption; detectable faults are safer than plausible but damaged results.

</semantic-interface-design>

## V. Layers, Policy, and Extension

<layers-policy-and-extension>

This group covers layering facilities, locating policy, and creating controlled paths for extension. It matters because collapsed layers and hidden defaults force unrelated users to pay for choices they did not make. Keep foundations primitive, policies caller-controlled, and extension points focused.

52. Expose complexity through progressive disclosure; beginners need a simple surface while experts retain access to clean machinery.
53. Build interfaces in layers with common operations on top and reusable mechanisms below; ordinary use stays easy while specialized use remains possible.
54. Keep low-level abstractions close to the operating system and layer usable interfaces above them; middleware can add convenience without hiding inherent costs.
55. Preserve abstraction layers and build higher-level conveniences on lower-level primitives; conflating layers delays foundations and restricts control.
56. Choose interfaces according to their abstraction layer and constraints; neither concrete nor generic forms are universally correct.
57. Leave consequential policy choices to callers through focused customization points; libraries should not make arbitrary decisions on users' behalf.
58. Charge users only for buffering, synchronization, allocation, or other facilities they request; mandatory policy makes unrelated callers pay for unused behavior.
59. Require callers to provide execution resources such as threads when practical; hidden resource creation removes control over scheduling and cost.
60. Provide constrained safe defaults with explicit escape hatches; trusted boundaries need safety while zero-cost composition sometimes requires broader control.
61. Design basis operations with extension points that absorb future use cases; extensibility avoids redesigning the foundation.
62. Design extension points that let new types supply behavior once; centralized type knowledge and repeated algorithm variants create unsustainable dependencies.
63. Distinguish how work is invoked from the form its continuation takes; orthogonal customization points preserve independent composition.
64. Place unavoidable complexity in infrastructure handled once by experts; moving it into an interface makes every user pay repeatedly.

</layers-policy-and-extension>

## VI. Genericity and Composition

<genericity-and-composition>

This group covers selecting generic models, preserving heterogeneous composition, and separating valid computation strategies. It matters because convenient concrete choices often block composition or impose hidden costs elsewhere. Generalize around required capabilities while preserving meaningful model distinctions.

65. Design parameters around required operations rather than a favored concrete type; valid models should compose without overload proliferation.
66. Design against the relevant concept instead of one convenient model; accepting the capability preserves composition across representations.
67. Choose concrete types or concepts according to the abstraction boundary; flexibility has no value after type erasure and fixed dispatch costs.
68. Compose heterogeneous inputs without forcing homogenization; callers should avoid unnecessary conversion and allocation.
69. Unify recurring operations only when each form is fundamental and cannot efficiently express the other; common interfaces require irreducible shared structure.
70. Support distinct computation models as first-class choices when each serves a valid domain; differences inherent to a model are not defects.
71. Offer separate native and type-erased interfaces; users should choose between allocation-free specialization and ABI-stable separate compilation.
72. Implement each operation once behind bridges to multiple consumption models; shared mechanics prevent duplication while preserving distinct user abstractions.
73. Preserve move-only composition and optimize allocation directly; copying handlers breaks valid types without addressing the real performance cost.
74. Reuse established interface conventions when they fit; transferable skill lowers adoption cost and increases confidence.
75. Analyze any model that defines control flow, binding, errors, and iteration as a programming language; otherwise its semantic and teaching costs remain hidden.
76. Evaluate every abstraction as a set of trade-offs; lowering cost in one dimension necessarily gives up properties in another.

</genericity-and-composition>

## VII. Architecture and Dependencies

<architecture-and-dependencies>

This group covers component boundaries, dependency direction, packaging, and compilation isolation. It matters because structural coupling multiplies build, test, review, and maintenance costs across a codebase. Separate information and abstraction levels so changes propagate only where they belong.

77. Separate components that encapsulate different information, dependencies, or reasons to change; physical boundaries preserve testability, reuse, and build performance.
78. Keep each component primitive and single-purpose, moving derivable behavior into free functions; flat dependency levels are easier to reason about and test.
79. Remove unnecessary dependencies early; small couplings accumulate into expensive test matrices and become difficult to reverse.
80. Eliminate dependency cycles and organize components into successive levels; one-way dependencies make software easier to isolate and reason about.
81. Package components at different abstraction levels separately; merging them forces low-level users to pay unrelated build, test, and cognitive costs.
82. Separate modules that hide different information; independent boundaries preserve the reasons each implementation can change.
83. Preserve established abstraction boundaries; collapsing distinct layers couples responsibilities that have proven independently useful.
84. Preserve separate compilation where large codebases need it; exposed implementation bodies turn internal changes into downstream rebuilds.
85. Count template-exposed implementation bodies as public-surface cost; downstream instantiations turn private changes into maintenance obligations.
86. Prefer native boundaries when type erasure has already fixed flexibility and dispatch costs; unnecessary templates increase compilation exposure without user benefit.
87. Separate abstractions that serve different layers; each layer must preserve its own responsibilities and constraints.
88. Remove centralized type knowledge from architecture; teaching each type its behavior once prevents repeated algorithm variants and dependency growth.

</architecture-and-dependencies>

## VIII. Cost, Performance, and Safety

<cost-performance-and-safety>

This group covers deployability, optimization evidence, failure behavior, and operational risk. It matters because elegant designs fail when their measured costs or unsafe semantics make them unusable. Make cost and safety claims concrete before fixing them into permanent behavior.

89. Measure abstractions by compile time, binary size, stack use, allocation, and runtime cost; theoretical elegance has no value when overhead blocks deployment.
90. Test compositional abstractions against deployment costs; composition that cannot be shipped has failed.
91. Optimize only measured bottlenecks that matter; intuition cannot identify the consequential minority of costs.
92. Judge zero overhead by whether used abstraction can reasonably be implemented more efficiently by hand; zero overhead does not mean zero inherent cost.
93. Design low-level abstractions for portability, flexibility, and performance; convenient interfaces can be layered above without constraining the foundation.
94. Require substantial quantitative evidence for permanent design choices; measurements expose costs that preference and theory conceal.
95. Demand performance data before changing failure semantics; untested choices can impose invisible runtime and compatibility costs.
96. Prevent untrusted inputs from repeatedly triggering exceptions; adversarial nondeterminism can degrade server performance unpredictably.
97. Choose reversible constraints before irreversible freedoms; a design can be loosened later but cannot reliably retract deployed behavior.
98. Preserve allocation-free specialization where it matters; mandatory type erasure can impose costs that low-level users cannot recover.
99. Make safety boundaries explicit and auditable; hidden escape paths defeat review and operational trust.
100. Prefer failure modes that preserve diagnosis and containment; silent continuation can turn a local fault into corrupted system state.

</cost-performance-and-safety>

## The Approach Behind the Rules

Not everything Vinnie does converts to a rule, because the rules are the residue of a practice, not the practice itself. What runs beneath his C++ library work is a conviction that design is the durable artifact and implementation is only its temporary proof of life, a thing that can be rewritten next year while the interface shape compounds forever. He treats the absence of fast, objective feedback on design quality not as an excuse but as a defining condition of the craft, one that demands a slower and more deliberate eye than implementation review typically provides. He is deeply suspicious of implementation skill that papers over a confused interface, because he has watched talented contributors mask leaks and awkward boundaries with clever code, leaving the underlying design debt invisible until integration time.

This suspicion feeds a recurring question he brings to every review: are we accumulating features that each work in isolation but resist fitting together? Vinnie also insists that where a person stands relative to an abstraction boundary changes what they see, which means sound judgment about an interface requires deliberately crossing to the other side before declaring it good. The craft, in the end, rests on accepting that a working program is temporary while its design consequences persist and compound, and building as though that were true.

*2026-07-29 21:25 - gpt-5.6-sol*
