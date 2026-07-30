---
description: Reference for evaluating C++ language and library designs the way Ville Voutilainen does - rationale, committee process, implementation experience, compatibility, language-design principles, library and API design, templates and constexpr, and safety and contracts
---

<!-- Load this file into context before reviewing a C++ proposal, weighing a design, or arguing a committee position. Sections run most to least frequently needed and are consulted one at a time, so the length of this file is never the number of rules you hold at once. -->

# Design-Evaluation Rulebook: Ville

<overview>

This file equips a reader to judge a C++ language or library design the way a seasoned evolution reviewer does. Every rule is distilled from Ville Voutilainen's WG21 reflector record and expressed as a directive with the consequence that justifies it. Read the opening of each section for the principle that ties its rules together, then apply the rules one at a time. The rules state substance only; they name no source document, thread, or date. Rules are numbered continuously across sections, so each rule has a unique number.

</overview>

<general-principle>

**The general engineering principle**. Judge a design on rationale, evidence, implementation experience, and compatibility, not on taste or urgency; extend the language only where the change costs nothing to those who opt out, helps the programmer rather than fights them, and generalizes rather than accretes.

</general-principle>

![Ville](images/how-to-ville.png)

## I. Rationale, Motivation, and Evidence

<rationale>

This section governs what a proposal must carry before it earns anyone's time: a reason, a cost, and evidence that a real user needs it. It matters because the committee's scarcest resource is attention, and a proposal that cannot justify itself burns that attention for everyone. The tie that binds: no design advances until its author states, in quantified terms, what problem it solves, what it costs, and what real-world use demands it.

1. State rationale that connects the design goals to the design decisions; a description that only lists the decisions leaves the reviewer unable to check whether they serve the goal.
2. Reject any argument grounded in feeling or preference; "I feel" spells lack of rationale by definition, so a claim you cannot quantify does not move the design.
3. Require every proposal to carry a substantial motivation and a cost/benefit analysis; if you cannot read the paper and come away knowing what changes, what it costs users and implementers, and what it buys, send it back until it can.
4. Demand real-world use cases, not just code that compiles; a proposal lacking widespread motivation gets a "no" until the motivation appears.
5. Explain why a facility should apply to a use case, not merely that it can; name the alternatives and say why the language needs a new one, or the use case argues for nothing.
6. Show how the API is used before comparing two designs; rationale and demonstrated usage decide which is better, not anecdote or strawman.
7. Prefer data over abstract debate; when a facility is contested, produce the patch, the error messages, and the numbers, because something concrete to talk about beats reflector philosophy.
8. Write the specification to find the design holes; drafting standardese reveals design issues in a way nothing else does, so unbaked material that skips it is a wishlist item, not a contribution.
9. Ask "why is it limited to one?" as hard as "why do you want many?"; the age of a rule or a paper grants it no priority, and status quo is a weak reason.
10. Treat a proposal with zero rationale as already answered; the default response to an unmotivated change is "no," and the burden sits with the proposer.

</rationale>

## II. Committee Process and Jurisdiction

<process>

This section governs where a decision belongs and how its trail is kept: design in the evolution groups, wording in the specification groups, and intent recorded in approved papers. It matters because a design decided in the wrong room, or remembered only as oral tradition, cannot be reviewed, reproduced, or defended later. The tie that binds: a design is only as real as the approved paper that records it, and every group must work its own jurisdiction rather than smuggle design through wording or memory.

11. Separate design from wording, and route each to its group; whether a feature can be used one way or another is a design matter for evolution, not a wording tweak for the specification groups.
12. Keep design intent in approved papers, not in recollection; the specification groups act on papers, so "this is what we meant" without a paper fixes nothing and wastes their time.
13. Refuse design proposals that carry no wording; a design without a specification is no design at all, so the review groups should reject non-designs rather than complete them.
14. Hash design alternatives in the evolution group, not a study group; that is where they belong, and moving them keeps a later evolution review from being dismissed as rehashing.
15. Repeat the full rationale for every decision on the record; if the group cannot point to what was decided and why, it will relive the confusion that produced the earlier failed attempt.
16. Do not morph an approved design during wording; if the approved design does not work, toss it back to evolution rather than quietly changing it, because the group approved the paper, not the rewrite.
17. Prefer papers to issues for anything with design content; issues are removed from the design context and expensive to reload, so they are a poor tool for decisions that need the design-to-spec connection intact.
18. Hold post-deadline feature requests to a high bar; extending a feature is evolutionary even when phrased as an issue, so admit it late only when a real bug forces it, and otherwise defer to the next standard.
19. Let the specification groups raise design objections, not just check words; consistency, correctness, and integration with the rest of the language are theirs to flag, which lowers the chance of drama at plenary rather than raising it.

</process>

## III. Implementation and Deployment Experience

<implementation>

This section governs the evidence a feature must earn before it becomes permanent: someone has built it, shipped it, and reported back. It matters because an International Standard binds millions of programs, and a feature that has never met a compiler or a real user is a guess wearing a specification. The tie that binds: nothing enters the standard on promise alone, because only building and deploying a feature reveals what its design actually costs.

20. Do not advance a feature to the standard before it is implemented; shipping an unimplemented extension into an IS that billions rely on is a bet no rationale covers.
21. Require a library feature to be integrated into a standard library and to pass its regression tests before you trust the claim that it works; a facility demonstrated only by separate code on a repository is not yet a library facility.
22. Ask the implementation questions in the paper: portability across the implementations, limitations hit, regressions caused, and the vendor's feedback on the patch; put the answers in the paper so no one has to reconstruct them.
23. Weigh deployment experience above paper argument; coroutines, concepts, and modules were shaped by feedback from real use before they shipped, and the features that skipped it produced the nasty surprises.
24. Decline to review unimplemented overload sets and partial orderings; unimplemented, they are revision and re-review magnets, so ask whether it is implemented and, if not, defer it.
25. Treat "we discussed the implementation" as unproven until the code exists; gaining implementation experience has never been easier, so the absence of it is less and less excusable.
26. Do not mistake compiler hacking for black magic; it is learnable perspiration, not a draconian bar, so the lack of a compiler background is no reason to skip building the thing.

</implementation>

## IV. Compatibility, ABI, Portability, and Stability

<compatibility>

This section governs the properties that let serious software commit to C++ for decades: code keeps building, binaries keep linking, and programs keep meaning the same thing everywhere. It matters because these guarantees, not raw speed, are why large organizations invest in the language, and a break here costs money and trust far downstream. The tie that binds: performance is worthless if it is not portable and stable, so weigh every change against the compatibility that makes the language dependable.

27. Treat compatibility and stability as first-order strengths, not obstacles; they are why serious software houses commit to C++, so a split into a compatible and a less-compatible language needs very strong rationale.
28. Quantify the cost of an ABI break before proposing one; the cost is real and measurable to the dollar for affected companies, and hand-waving that it "appears overestimated" is not an argument against a figure built from facts.
29. Migrate an ABI by making the new version attractive, not by forcing a recompile; when new capability pulls users to rebuild, the migration hurts less, and tooling that explains link errors helps more.
30. Do not claim the language prioritizes performance above all else; it does not blindly outrank portability, compatibility, and stability, and the reason to use C++ is the whole package.
31. Judge performance as useless when it is not portable; a fast program you cannot ship everywhere buys you nothing, and compatibility and abstraction are themselves forms of portability.
32. Tell users to write to the language, not to a dialect; maintaining conditionally compiled implementations of the same thing against vendor extensions wastes their time and yields non-portable code.
33. Do not treat a vendor attribute as portable; by definition it is not, and features that change program semantics through it leave users less portable than promised, not more.
34. Price a compatibility break at its full cost: split codebases, unknown tool bugs, slower builds, and legacy systems that must keep running; the migration cost lands on every codebase, so budget it before adopting.
35. Expect the language to keep meaning what it meant; a fast-moving, often-breaking language loses the users who need a decades-long investment, as the languages that tried it discovered.

</compatibility>

## V. Language Design Principles

<language-design>

This section governs the shape of the language itself, ordered by the design principles a sound feature must satisfy: cost only its users, stay at the lowest useful level, make danger visible, prefer general mechanisms, and let the user say what they mean. It matters because a feature that violates these does lasting structural damage that no later fix fully undoes. The tie that binds: extend the language only through changes that cost nothing to those who opt out, help the programmer rather than fight them, and generalize rather than accrete.

36. Do not impose cost on programs that do not use a feature; a mandatory check, required metadata, or ABI overhead makes opt-out code pay for what it never uses, and that guarantee is why the language survives from wristwatches to server farms.
37. Read the zero-overhead principle for what it says; it never meant the language should skip what you dislike or refuse decisions you disagree with, so do not stretch it to veto features.
38. Keep the language at the lowest useful level above the hardware; requiring constructors where a bag of values suffices leaves room between C++ and the machine for another language, which the design has avoided since the start.
39. Make the language ask you to say what you mean in a weird situation; when a design is ambiguous, force explicit disambiguation rather than let the compiler guess and risk a silent, hard-to-trace behavior change.
40. Treat built-in and user-defined types uniformly; if a rule holds for class types it should hold for non-class types too, because uniform treatment is a fundamental design principle.
41. Keep attributes as hints, not semantics; the core language is extended through libraries, not through a loosely structured attribute mechanism, so express new semantics with a stronger construct than an attribute.
42. Refuse to let operator overloading become a semantic wild west; it exists to give generic programming a compact notation, so put complex semantics behind named library types and let a language construct lower to those calls.
43. Protect the large-scale guarantees of a closed overload set; once a facility becomes an open overload set, designers can no longer protect users across refactorings, and "users must be more careful" contradicts the promise to help write large programs.
44. Prefer a general mechanism to a pile of point features; reflection and injection let users write opt-in boilerplate generators, so reach for the wholesale facility before adding bells and whistles to the core.
45. Read a terse abstraction for the power it hides; a syntax simple enough to look like no abstraction can still be an immensely powerful one, so analyze before discarding it for something less abstract.
46. Do not require every language feature to appear in the standard library; the top features of C++11 have no need to be used in the library spec, so "the library does not use it" is not an argument against a feature.
47. Make the language help the programmer, not fight them; a change that turns the language into something you must struggle against fails regardless of its backward-compatibility story.
48. Weigh removing or undoing a settled decision as a possible cure worse than the disease; past decisions were often made deliberately with the consequences understood, so changing them needs strong rationale.

</language-design>

## VI. Library and API Design

<library-api>

This section governs the standard library: what belongs in it, how its interfaces are shaped, and how its changes are governed. It matters because a standard component is used by everyone, refactored for decades, and frozen once shipped, so a weak API is a permanent tax on the ecosystem. The tie that binds: design every library interface for its real use cases under design-group review, favoring general building blocks and existing practice over dogma, patchwork, or cleverness.

49. Treat every library API change as a design matter for the design group, including consistency fixes and bug fixes; APIs need a paper trail, and the design group must know about changes rather than have them slip through as isolated issues.
50. Design an API for its expected use cases, not for a guideline you have yet to invent; cater to how the facility is actually used rather than conform dogmatically.
51. Provide general building blocks that express multiple semantics; deciding on a narrow subset denies users the genericity that a well-factored primitive would give them.
52. Follow the established standard-library pattern for allocators; a type is allocator-customizable by taking an allocator as a template and constructor argument, and a deleter or a memory resource is not an allocator API.
53. Standardize a type to serve many use cases and to let fields and companies communicate; users should not have to rewrite it or hunt for it in non-standard libraries.
54. Use concepts in a specification only where subsumption is needed; otherwise "Constraints:" says what is required without overspecifying an implementation strategy.
55. Prefer a wholesale solution to patchwork on individual APIs; per-API fixes catch only narrow, unconvincing cases, so weigh the cost/benefit before scattering them.
56. Take naming discussions offline and bring back at most two options with rationale; group bikeshedding produces worse names than anything else, so decrease the urgency rather than brainstorm live.
57. Do not bring PascalCase into the standard; the library has no such names, and the cost, hard to quantify, is not worth the apparent benefit.
58. Keep the library specification honest to real code; being over-clever with implicit qualification invites bugs in the spec and in implementations, so write what you mean.
59. Design a facility that supports a programming technique into the library where convenience matters most; a facility whose point is to promote a pattern belongs where it is convenient to reach.
60. Standardize existing practice for a mature domain, and reserve invent-as-you-go for genuinely novel facilities; ask for a library written close to standard-library style before adopting one designed on the fly.
61. Treat "recommended practice" and [[nodiscard]] as quality of implementation, grounded in what vendors actually do; the risk of getting a new API's nodiscard wrong is small and fixable, and the detail is better left to implementations that carry the expertise.
62. Do not let a design ship as "already approved" once it has changed; if the template parameters and facilities differ from what the group saw, it is a different design and needs review again.
63. Reject the claim that a builtin must exist because a library type would be slower; major vendors have applied intrinsic-backed library techniques for years, so base the builtin-versus-library call on facts, not on a hypothetical performance gap.

</library-api>

## VII. Templates, Concepts, Constexpr, and Reflection

<templates>

This section governs the generic and compile-time machinery: where constraints act, how concepts differ from the old tricks, and what constexpr and reflection are actually for. It matters because these mechanics decide overload resolution, error quality, and whether the same code runs at compile time and run time, and small misunderstandings here compound into unfixable interfaces. The tie that binds: constrain and compute at the point and time the language checks them, prefer the mechanism the language evaluates during overload resolution, and reach for a general facility before hand-rolling metaprogramming.

64. Put checks that gate overload resolution in Constraints and make them SFINAE-friendly, and put checks that fire on instantiation in Mandates; the trait query for a Constraints check answers truthfully, while a Mandates violation only renders the use ill-formed.
65. Use concepts where you need subsumption; concepts tie into overload resolution at the language level in a way legacy SFINAE cannot emulate, and subsumption is the difference.
66. Rely on concepts being checked at the call site during overload resolution; that timing suffers far less from type-completeness flips than a declaration-time trait trick like Eric's Trick, which runs the metaprogram too early.
67. Do not expect a concept evaluation to answer differently in two contexts; a concept is template-like, so relying on context-dependent answers is already ill-formed, and disallowing caching only makes such reliance easier to hit.
68. Reach for `if constexpr` to collapse a family of constrained overloads into one function; running a constexpr predicate in the constraints and forwarding once drops the constructor overload count of pair and tuple toward one.
69. Read `if constexpr` as an if-statement whose condition must be a constant expression, not as general constexpr evaluation; keep compile-time programming consistent with ordinary programming rather than requiring extra conversion fluff.
70. Fix overload resolution so simple things stay simple for non-experts; when two unrelated types are used precisely because they are unrelated, honor that as the disambiguating hint, even at the cost of a more complicated specification.
71. Pass a function object by forwarding reference or by value on purpose, not by habit; when performance matters you expose a template to the inliner anyway, and a by-value parameter imposes a real requirement on a move-only callable.
72. Accept that type erasure moves the copyability question to run time; a wrapper like any or function cannot know at the call site whether the erased type is copyable, so the run-time error is inherent to the design, not a defect.
73. Take the evolutionary step from SFINAE to raw requires-clauses to concepts as it suits the design; an ad-hoc boolean combination of traits is a legitimate stage, and you need not force it into a named concept.
74. Do not use a default argument's value to SFINAE; the type of a default argument is fine for it, its value is not, and other mechanisms exist for constraining an overload set.
75. Get out of the metaprogramming jungle when a straightforward, less generic solution will do; code three people grok on sight beats code only two can, and cleverness is not the goal.
76. Read constexpr as one design goal: the same code runs at compile time and run time; consteval is for code with no run-time meaning, and constinit requires constant initialization without producing a constant.
77. Make everything constexpr to fold whole computations away, not to invent compile-time algorithms; when the inputs are constants the code evaporates to a single value, and when they are run-time values the same code just runs.
78. Follow the reflection roadmap from introspection to injection to transformation, and prefer library metaprograms built on it to new point features; a rich enough reflection facility lets you write the code generators instead of baking each one into the language.

</templates>

## VIII. Safety, Correctness, and Contracts

<safety>

This section governs correctness and the contracts facility: what a precondition is, how it differs from a predicate, when continuation is safe, and who a contract serves. It matters because safety claims are easy to assert and hard to keep, and a facility that conflates logging with continuation or bug-finding with error-handling can wreck the correctness it promises to improve. The tie that binds: treat correctness as orthogonal to undefined behavior, keep the safe path the default and the dangerous path visible, and design contracts for the caller who relies on them.

79. Accept that safe-by-default sometimes costs performance or changes meaning silently; when the goal is safety by default, pay that price where warranted and expect experts to cope, as the language already has elsewhere.
80. Keep safety tools simple and let implementers fill in the finer details; carving out a category like erroneous behavior works precisely because the standard does not overspecify every consequence.
81. Do not claim a facility "absolutely" improves safety; contracts improve correctness only when the contracts are themselves correct, so an incorrect contract can reduce safety rather than raise it.
82. Do not assume termination is the safe response; in some domains it is overkill for a recoverable state, and in others it is the least safe and outright forbidden option, so it was never the only outcome to a violation.
83. Do not teach "checked means checked" as a safety net; checks are elided under many combinations and conditions, so relying on them as a guarantee is dangerous in safety-critical code.
84. Distinguish library undefined behavior from language undefined behavior; a library defines its own out-of-contract behavior, which is why a precondition violation need not be abstract-machine UB, and the term Wrong Behavior covers the full range without the baggage.
85. Read a precondition as a documented assumption, not a check; the annotation records the assumption the implementation already makes and creates a check for it, so a precondition exists whether or not it is annotated.
86. Separate predicates from preconditions; violating a predicate need not hurt you and it is assumed by nothing, while violating a precondition puts you in uncharted territory because assumptions elsewhere depend on it.
87. Treat correctness and undefined behavior as orthogonal; a function can have a precondition and no UB, and a program can be well-defined yet incorrect, so do not tie one to the other.
88. Model a class invariant as a precondition of each public member function; postconditions alone cannot guarantee it, since a friend or protected operation can break it between calls.
89. Assert your assumptions as preconditions and your guarantees as postconditions, then enforce them; if the violation handler returns normally you have a predicate, not a precondition, and the two are different beasts.
90. Use a throwing violation handler to make detected bugs recoverable when your domain needs it; treating correct and incorrect programs the same way lets a program fail gracefully instead of crashing, and thirty years of Java shows this is not disqualifying.
91. Design contracts for the caller, not the library author; the control knobs and their granularity exist for the benefit of the user who relies on the contract.
92. Preserve the deliberate flexibility of contracts to mean different things under different semantics; source code whose meaning is chosen outside it is the bedrock of the design, so do not collapse it into a single fixed behavior.
93. Make simple things simple; if a common task like finding a substring is not simple, take even drastic measures to make it so rather than push users to generic algorithms they do not need.
94. Guard against a change that makes simple things no longer simple; a feature you cannot tell was opted into, and cannot turn off with good diagnostics, springs trapdoors under code that never asked for the flexibility.
95. Separate breaking programming from breaking engineering; you can cope with broken code, but broken expectations that design choices were built on cost far more, so weigh the engineering break, not just the source break.

</safety>

*2026-07-29 06:35 - claude-4.6-opus-medium-thinking*
