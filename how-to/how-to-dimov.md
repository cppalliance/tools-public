---
description: Reference for evaluating C++ language and library designs the way Peter Dimov does - API minimalism, safe defaults, undefined-behavior elimination, contracts and preconditions, type invariants, generic programming, error handling, and async patterns with evolution strategy
---

<!-- Load this file into context before reviewing a C++ proposal, weighing a design, or arguing a committee position. Sections run most to least frequently needed and are consulted one at a time, so the length of this file is never the number of rules you hold at once. -->

# How to Design Minimal Safe C++ APIs

<overview>

This file equips a reader to judge a C++ language or library design the way a practitioner-first library author does. Every rule is distilled from Peter Dimov's WG21 reflector and Boost mailing list record and expressed as a directive with the consequence that justifies it. Read the opening of each section for the principle that ties its rules together, then apply the rules one at a time. The rules state substance only; they name no source document, thread, or date. Rules are numbered continuously across sections, so each rule has a unique number.

</overview>

<general-principle>

**The general engineering principle**. Start from the smallest correct interface, default to the safe path, eliminate undefined behavior by construction, enforce contracts at trust boundaries, preserve type invariants across every operation, spell out every constraint the compiler can check, make every error path visible and typed, and evolve by deprecation-then-deletion rather than silent breakage.

</general-principle>

![Dimov](images/how-to-dimov.png)

## I. API Design and Minimalism

<api-design-and-minimalism>

API design begins with the smallest viable surface and adds features only when justified by concrete practice. Shipping too much is irreversible, while shipping too little is always correctable. The unifying principle is that every interface element must earn its place through independent motivation and demonstrated need.

1. Ship a minimal foundation and add features later, never ship features you might need to remove, because additions are easy and removals are costly.
2. Require a concrete use case from practice before adding any feature, because speculative interfaces accumulate unjustified maintenance cost.
3. Require independent motivation for every interface addition, because adding for cross-type consistency sidesteps the normal justification process.
4. Provide a separate overload for callers who need detailed information rather than complicating the primary interface, because most callers should not rely on edge-case signals.
5. Apply cost/benefit to each deprecation individually, removing features that are broken and retaining features whose removal costs more than keeping them.
6. Prefer the narrowest mechanism that solves the actual problem, because a general-purpose feature that also solves unneeded problems adds unjustified complexity.
7. Do not force a nullable parameter when the null case is never useful, because it introduces unnecessary branches and conceptual overhead.
8. Impose no restriction without a rationale, because unexplained constraints accumulate into incoherent designs.
9. Do not pay a performance cost for generality no real type exercises, because a legitimate use case must exist before accepting the overhead.
10. Consume dependencies unmodified from upstream rather than maintaining local patches, because solutions that avoid source modifications compose better across projects.
11. Do not couple a bridge component with another library, because each additional dependency reduces the chance of universal adoption.
12. Provide a bounded overload for fixed-size arrays, because relying on runtime tricks to catch overflow is inferior to a compile-time safe interface.
13. Accept rvalue references alongside const-ref even when the implementation does not yet move, because giving the implementation freedom to optimize later costs nothing today.
14. Lift assertions into caller-visible preconditions, so diagnosis happens as early as possible up the call stack.
15. Expose precondition-queryable state publicly, because a caller cannot ensure a condition it cannot inspect.

</api-design-and-minimalism>

## II. Defaults and Conventions

<defaults-and-conventions>

Defaults determine what most code looks like, and the right default is the one practitioners reach for most often. When a built-in type sets the precedent, the library type must follow it exactly. The unifying principle is that the common, safe, proven path should require zero annotation and zero justification.

16. Make the safe behavior the default and the short form, require explicit annotation only for the unsafe alternative, because the common safe case should need no ceremony.
17. Default to initialization rather than leaving values indeterminate, because zero-initializing static storage was a deliberate choice and the cost elsewhere is now negligible.
18. Make every safety-affecting change visible in the source code, because silent compiler-flag behavior changes prevent meaningful code audits.
19. Prefer the name practitioners independently converge on, because independent convergence signals the concept users actually hold.
20. Make the seven-times-more-common usage the default, because existing practice reveals the right default.
21. Disable assignment to rvalue for value types, because when in doubt, match the behavior of built-in types.
22. Match library-type behavior exactly to the corresponding built-in type when one exists, because divergence, however well-intentioned, causes more problems than it solves.
23. Specify behavior rather than leaving it unspecified, because fully specified behavior prevents portability surprises.
24. Prefer a design informed by years of heavy practice over a speculative one, because practiced designs encode hard-earned truths that theory alone cannot surface.
25. Let vendors ship a subset or divergent implementation and observe user response, because real adoption data and bug reports are the definitive way to discover actual requirements.
26. Prefer a dedicated language feature over a metaprogramming workaround, because write-only injection code fragments the ecosystem into unreadable dialects.

</defaults-and-conventions>

## III. Safety and Undefined Behavior

<safety-and-undefined-behavior>

Safety in C++ means eliminating undefined behavior through compilation errors, runtime checks, or enforced invariants. Safety profiles must target UB specifically, not style, and every safety rule must name the UB it eliminates. The unifying principle is that no path through conforming code should reach undefined behavior, and the compiler should reject as many such paths as possible.

27. Fix the specification even when the defect causes no problems in practice, because relying on implementation behavior that contradicts the spec is unsound.
28. Treat all deserialized input as untrusted and never exhibit undefined behavior regardless of content, because bit flips and transmission errors are inevitable.
29. Design input-facing libraries with no preconditions on the data, because the library must handle every possible input without undefined behavior.
30. Eliminate each source of undefined behavior by refusing to compile it, inserting a runtime check, or enforcing an additional invariant, so that no UB path remains unaddressed.
31. Limit safety profiles strictly to eliminating undefined behavior rather than offering stylistic guidance, so safety remains a clear binary property.
32. Do not permit unsafe constructs merely because they have legitimate uses, or layered profiles will never produce a safe language.
33. Apply safety requirements uniformly across old and new features, because imposing constraints only on new proposals while legacy issues persist gains little.
34. Require each safety rule to cite the specific undefined behavior it eliminates, because a rule without a named UB source cannot be evaluated.
35. Do not label library-precondition violations as "soft UB" to imply they are less dangerous, because they are equally exploitable.
36. Diagnose every error the compiler can detect, because leaving known bugs undiagnosed does not make unknown bugs safer.
37. Delete known dangerous implicit conversions at compile time, because a deleted overload catches the bug where a warning might not.
38. Reject undefined behavior that "works in practice," because it always breaks eventually.
39. Prefer span over generic contiguous_range template parameters for bounds-checked code, because span carries built-in hardening and is the likely idiomatic future.
40. Treat a function with no preconditions as safe by definition and apply preconditions universally, so safety reasoning uses a single framework.
41. Test behavior on a violated precondition rather than on undefined behavior itself, because UB is by definition untestable.

</safety-and-undefined-behavior>

## IV. Contracts and Preconditions

<contracts-and-preconditions>

Contracts formalize the boundary between caller and callee, and getting them right before the compiler sees them is critical because compilers apply contracts literally. The person building the final executable must control enforcement policy without patching source. The unifying principle is that contracts belong at trust boundaries, default to termination, and remain under deployer authority.

42. Separate the programmer's control from the deployer's control in contract checking, because the person building the final executable must retain authority over runtime behavior without patching source.
43. Commit to a single checking model early in the design, because ambiguity between models invites incompatible extensions that are hard to reject later.
44. Confine contract specifications to preconditions, postconditions, and invariants, because general assertions invite divergent expectations since there is no second party.
45. Default contracts to termination on violation but provide a temporary continue mode for rollout, because permanent continuation lets failing contracts survive for years.
46. Maximize adoption ease before tightening enforcement, so that contracts appear in enough code to be enforced when required.
47. Get contract specifications exactly right before exposing them to the compiler, because a compiler back-end applies them literally with no common-sense interpretation.
48. Prefer a narrow contract with preconditions over a wide noexcept contract, unless widening has no significant drawbacks.
49. Place contracts at the boundary between user and type rather than between internal member functions, so that preconditions are enforced where trust changes.
50. Do not convert precondition violations into exceptions, whether at individual call sites or via a global switch, because the code base may not be exception-safe at those points and throwing on a bounds check can bring down the entire process.
51. Do not automatically widen inherited preconditions by disjunction, because it defeats intentional tightening during API evolution.
52. Treat hardening an existing precondition as an implementation decision, because it is unobservable and does not alter user code.
53. Allow assumptions to be checked at runtime via a master switch, because assumptions can be wrong and you need a way to discover miscompilation.
54. Treat out-of-bounds on operator[] as a precondition violation, not an exception contract, because correct program logic may depend on .at throwing but never on [] throwing.
55. Default library preconditions to user-controllable checking, so that enforcement remains the user's choice and the library avoids being forced into macros.
56. Justify a stronger enforcement level by reasoning about what would happen if execution continued, because restricting the user's choice requires a stated reason.

</contracts-and-preconditions>

## V. Type Design and Invariants

<type-design-and-invariants>

A type's invariant is the property preserved from entry to exit of every public operation, and all design decisions about move, assignment, and destruction must honor it. Partially-formed states destroy invariants and must never participate in assignment. The unifying principle is that every object must be in a valid, inspectable state at every observable point in its lifetime.

57. Define an invariant as a property preserved across every operation, because "maintain" means if it holds on entry it holds on exit.
58. Keep assignment defined only from a valid state, never from a partially-formed state, because essential invariants like allocator identity cannot survive partial formation.
59. Leave moved-from objects in a valid state by default, using the default-constructed state when the class has an invariant, and reserving destructive move for scoped temporaries that are provably unobservable.
60. Write explicit special members for classes with invariants, because rule-of-zero silently breaks when state must be preserved across moves.
61. Make the destructor of a pure abstract class protected by default, unless deletion through the interface is intended, so that ownership semantics are explicit.
62. Do not add state-management features to reference types, put them on owning types, because reference types exist to type-erase parameters and not to manage lifetimes.
63. Exclude private and data members from interface abstractions, because silently ignoring them hides a design decision that should be explicit.
64. Prefer a quiet empty state over a signaling one that traps on access, because values that explode when observed lose to values that propagate safely.
65. Check each postcondition under the precondition branch that produced it, because the combined postcondition is the conjunction of each precondition implying its own postcondition.
66. Assume that legal usage is at least as widespread as illegal usage, because if programs violate a rule in practice then conforming programs certainly rely on the permitted behavior.

</type-design-and-invariants>

## VI. Concepts, Templates, and Generic Programming

<concepts-templates-and-generic-programming>

Concepts make implicit constraints explicit, turning silent failures into compile errors and making overload sets honest about what they accept. Define concept requirements in one place and apply them uniformly, because ad-hoc divergence produces systemic errors. The unifying principle is that every constraint a template relies on should be spelled out, checked at compile time, and stated once.

67. Spell out implicit concepts explicitly in code or documentation, because they exist whether or not you write the keyword and explicit forms catch mismatches earlier.
68. Prefer a stricter protocol that makes violations compile errors over a permissive one that silently misbehaves, because correctness at compile time outweighs short-term convenience.
69. Define concept requirements in one place and apply them uniformly, because ad-hoc lookup rules that diverge from the concept produce systemic errors.
70. Specify buffer requirements as concepts rather than convertibility to concrete types, because concepts decouple physical dependencies.
71. Prefer simple convertibility constraints over common_reference or ternary tricks, because code you cannot remember the semantics of accumulates errors.
72. Do not enable comparisons between unrelated types merely because a generic template permits it, because most such comparisons are bugs caused by typos.
73. Scope operator overloads narrowly to their intended types, because an unreasonably greedy operator pulled in via ADL causes collateral matching errors.
74. Make type-query traits SFINAE-friendly rather than static_assert-based, because every serious generic use requires reimplementing them otherwise.
75. A generic algorithm must pick one behavior per design point, because it cannot know every caller's intent and parameterizing every decision makes the algorithm unusable.
76. Treat bounded-input linear scans as constant-time but never use linear scans on unbounded input, because a linear scan inside a loop becomes quadratic.
77. When multiple failure modes stem from implicit compatibility, require an explicit concept so failures become compile errors.

</concepts-templates-and-generic-programming>

## VII. Error Handling and Exception Safety

<error-handling-and-exception-safety>

Error handling must match the failure mode: optional for legitimately absent values, expected for operational failures, and exceptions for truly exceptional conditions. Exception safety starts at the basic guarantee and strengthens from there, never weakens. The unifying principle is that every error path should be visible, typed, and impossible to silently ignore.

78. Reserve optional for "value may legitimately be absent" and never return it when the empty case is vanishingly rare, because programmers neglect to check a result that almost always holds a value.
79. Use expected<T, error_code> to provide dual exception and error-code APIs, because callers who want exceptions simply call .value().
80. When unwrapping expected, throw the domain-appropriate exception rather than bad_expected_access, because regularity in the wrapper type is rarely what callers need.
81. Use the standard error condition when one exists rather than a custom equivalent, because foreign error codes know how to compare against the standard one but not against yours.
82. Do not require explicit error annotation at every call site, because pervasive try or propagation syntax becomes unwieldy and degrades readability at scale.
83. Return optional<T&> from lookup functions instead of a raw pointer, because the pointer is just an approximation of optional.
84. Consolidate "get value or default" into a single component like optional, so that the concern lives in one place.
85. Base exception safety on the basic guarantee or stronger, because overturning an established safety level creates friction and defects.
86. Mark every non-throwing function noexcept, because the annotation enables optimization and catches accidental throwing paths at compile time.
87. Require noexcept-correctness in type requirements rather than splitting the constraint into a trait plus a prose precondition, because compile-time enforcement catches real errors.
88. Give distinct names to operations that act on different abstractions of the same object, because overloading the same name for both creates silent semantic confusion.
89. Give throwing and non-throwing variants of an operation visually distinct names, because similar syntax makes accidental use of the wrong variant easy.

</error-handling-and-exception-safety>

## VIII. Async, Coroutines, and Evolution

<async-coroutines-and-evolution>

Async primitives must build in reentrancy protection and propagate cross-cutting state through a protocol, because manual threading is verbose, error-prone, and invisible when it fails. Evolution strategy favors new syntax over backward-compatible contortion and deprecation-then-deletion over silent breakage. The unifying principle is that async and evolutionary design both succeed by making the dangerous path impossible rather than merely discouraged.

90. Build reentrancy and recursion protection into generic async primitives, because authors of composed operations cannot know whether downstream code requires it.
91. Resume coroutines on their original executor by default, because single-executor resumption eliminates locking and is easier to reason about.
92. Propagate cross-cutting state through a protocol rather than requiring manual threading at each call site, because manual propagation is verbose, repetitive, and error-prone.
93. Make silent dropping of propagated state a compile error, because if forgetting to pass a stop token still compiles, cancellation will silently break.
94. Invest in optimizing exceptional control paths even when the payoff is deferred, because doing so enables choosing better tradeoffs later.
95. Prefer new syntax unconstrained by backward compatibility when existing syntax cannot achieve the needed semantics, because freedom from legacy enables better overload resolution and broader consensus.
96. Evolve a bad interface by deprecating, then deleting, then optionally undeleting with correct semantics, because the deleted intermediate prevents silent misuse.
97. Do not degrade the experience of current users to attract non-users, because the stated objections of non-users are usually pretextual and concessions will not convert them.
98. Do not degrade permanent syntax to address concerns that may prove temporary, because history shows such concerns often evaporate while the ugliness remains.
99. Give domain-specific operations a distinct name from generic ones, because operations that mean different things must not collide in name.
100. Start users on the full-featured API rather than a simplified wrapper, because a shorthand that is not a natural edit away from the real form will be abandoned.

</async-coroutines-and-evolution>

## The Approach Behind the Rules

Not everything Peter does converts to a rule, because the rules are the residue of a practice, not the practice itself. His practice begins with a demand for coherence: rejecting an interface because it allocates is incoherent when the constructors already allocate, a preference is not a rationale, and suspicion without a benchmark is not evidence. He treats the standard library as both a case study in template programming and a natural test bed for concepts, which means the artifacts he builds are expected to teach as well as to function. His designs are economical to the point of austerity, favoring a closed set of constructors over an open concept, choosing an early return on empty to avoid a spurious warning and a needless allocation, and admiring exceptions precisely because their annotation-free propagation is analogous to writing `std::copy` once.

When he encounters a design fork he reduces it to the thinnest possible distinction, the way the entire variant question collapses to "exactly one of" versus "at most one of," and he insists that the algorithm's author must choose one behavior because a generic algorithm cannot know caller intent. He carries an empiricist's calm through committee deadlocks, noting that opposing factions often reject the same design for contradictory reasons, and that everything taught about reader-writer locks turns out to be useless in practice. Where the craft ultimately rests, for Peter, is in the people who hold the design knowledge, because when a sole domain expert disengages, the rationale leaves with them and the documentation gap cannot be filled.

*2026-07-29 08:22 - claude-4.6-opus-medium-thinking*
