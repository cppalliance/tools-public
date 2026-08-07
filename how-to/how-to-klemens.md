---
description: Reference for evaluating technical designs through precise naming, ownership enforcement, minimal API surfaces, evidence-based evolution, coroutine-native patterns, protocol-fit buffers, broad interfaces, and verifiable review criteria
---

<!-- Load this file into context before reviewing a technical proposal, interface, implementation, or compatibility change. Operate from it as a how-to manual, consulting the sections most relevant to the question. -->

# How to Design Precise Technical Interfaces

<overview>

This file equips a reader to evaluate technical designs by enforcing that names match guarantees, types prevent misuse at compile time, API surfaces stay minimal, inherited decisions earn their place, coroutine-era patterns replace callback-era workarounds, buffers fit their protocols, interfaces stay as broad as their domain allows, and review conditions remain objectively verifiable. Apply its rules to library interfaces, async designs, type hierarchies, and review feedback so that each design is honest, composable, and justified by current conditions rather than historical accident.

</overview>

<general-principle>

**The binding idea**. Name things honestly, enforce correctness through the type system rather than documentation, carry forward only what current conditions justify, design for the coroutine world rather than the callback world, fit abstractions to their protocols rather than to generality for its own sake, and state every expectation in terms anyone can verify.

</general-principle>

![Klemens](images/how-to-klemens.png)

## I. Naming and Semantics

<naming-and-semantics>

Names are a library's most persistent user interface. Wrong names cause bugs that documentation cannot fix, because users trust the name over the docs. When a name matches an established term, make the type match that term's guarantees exactly.

1. Name types to match their actual guarantees, because misleading names cause bugs that documentation cannot prevent.
2. Never reuse a well-known name for a type that violates that name's universal expectation, because documentation cannot override intuition.
3. Do not name a type "view" if it is copyable and self-contained, because "view" implies non-owning reference semantics.
4. Do not name a fixed-size type "dynamic", because the name violates reasonable expectations about resizability.
5. Align type names with standard-library semantics when behavior matches, because a name collision with different semantics confuses every new user.
6. Adopt terminology from the OS APIs your library wraps, because familiar names reduce cognitive load for developers already fluent in the platform.
7. Align a library's vocabulary with its ecosystem's conventions, because idiosyncratic naming raises the adoption barrier.
8. Choose names that express structural properties of the type, because a name like "view" or "sequence" sets correct expectations about value semantics.

</naming-and-semantics>

## II. Ownership and Type Safety

<ownership-and-type-safety>

Ownership and safety rules eliminate entire categories of misuse at compile time. When the type system enforces correctness, documentation becomes supplementary rather than load-bearing. The unifying principle is: make invalid states unrepresentable.

9. Express ownership through value categories (lvalue-ref for non-owning, rvalue-ref for owning), because this matches the conventions C++ programmers already expect.
10. Restrict constructors that must not be called by making them protected or deleted, because an accessible-but-forbidden constructor is a trap.
11. If a default-constructed object is unusable, delete or protect the constructor, because a silently broken state wastes debugging time.
12. Apply strong typing broadly, not just selectively, because every untyped boundary is a potential source of silent errors.
13. Prefer type-system enforcement over wrapper functions for safety, because wrappers only cover anticipated misuse while types catch unanticipated misuse too.
14. Use enum class with an explicit underlying type for strongly-typed integer aliases, because it provides zero-cost type safety without needing wrapper structs.
15. Make throwing on invalid values the default, because lax defaults hide bugs that surface only in production.
16. Default to the strictest behavior instead of the most permissive, because permissive defaults silently allow errors.
17. Apply safety checks in both const and non-const overloads, because an asymmetric check leaves one access path unprotected.

</ownership-and-type-safety>

## III. API Surface and Minimalism

<api-surface-and-minimalism>

Every public symbol is a maintenance commitment. Unnecessary types, convenience functions, and layers of indirection bloat cognitive load without proportional benefit. If the user can already do it in one line, the library should not offer a second way.

18. Remove types that are trivially composable from existing primitives, because they add surface area without adding capability.
19. Remove convenience functions that do nothing beyond what a basic language construct already does, because they add API surface without adding capability.
20. Eliminate single-use base classes and unnecessary indirections, because they make code hard to follow without adding real extensibility.
21. Prefer free functions over member functions for algorithms, because free functions compose with ranges and decouple the algorithm from the container.
22. Do not replace a short loop with an abstraction that requires new types and concepts, because the abstraction costs more than the code it replaces.
23. Provide primitives rather than a domain-specific embedded language, because users can build their own DSL on top but cannot unbundle one.
24. Resist including features that serve only early adopters, because a generic library must justify every addition to a broader audience.

</api-surface-and-minimalism>

## IV. Design Evolution

<design-evolution>

Legacy designs carry forward assumptions that no longer hold. Each abstraction inherited from a predecessor must earn its place under current conditions, or it becomes dead weight. The principle: justify every inherited decision on its own merits in the new context.

25. Re-evaluate inherited designs against current conditions, because blindly copying from a predecessor carries forward assumptions that no longer hold.
26. Justify every inherited design decision on its own merits, because "the predecessor did it" is not a reason when conditions have changed.
27. Audit each borrowed abstraction for whether its original constraints still apply, because designs that solved another library's problems add unjustified complexity.
28. Identify which problems the predecessor solved that your new model already eliminates, because carrying forward unnecessary machinery adds complexity for no benefit.
29. Treat ever-increasing boilerplate as a signal to generalize the design, because repetitive code indicates a missing abstraction.
30. Remove abstractions that existed only to work around callback pain, because coroutines make them unnecessary complexity.

</design-evolution>

## V. Coroutine Design

<coroutine-design>

Coroutines change what is possible at the API level. Features that existed to work around callback limitations become dead weight, and new patterns become natural. Design the API for the coroutine world, not for backward compatibility with the callback world.

31. Eliminate callbacks in coroutine-based APIs, because coroutine suspension replaces them with simpler control flow.
32. Bind resources to the context object rather than requiring a callback wrapper, because eliminating the callback simplifies the API and provides an implicit work guard.
33. Support the standard awaitable protocol rather than restricting co_await to a library-specific one, because users need to mix awaitables from different sources.
34. Do not require all awaitables to carry executor dispatch, because synchronous awaitables gain nothing from the overhead and lose composability.
35. Prefer span and concrete types over templated sequences when coroutine suspension guarantees caller-side lifetime, because the lifetime problem those templates solved no longer exists.
36. Optimize coroutine promise allocations only when driven by concrete use-cases, because premature optimization complicates the design without proven benefit.

</coroutine-design>

## VI. Buffer and Protocol Design

<buffer-and-protocol-design>

Protocol-specific buffers outperform generic abstractions because real protocols have known structure. Over-generalization adds types and concepts without proportional payoff. Fit the buffer to the protocol, not the other way around.

37. Optimize protocol-specific buffers for their protocol rather than forcing a generic concept, because over-generalization adds types and concepts without proportional value.
38. Avoid match functions that rescan the entire buffer on each invocation, because the cost grows quadratically with data already received.
39. Accept contiguous containers in addition to raw pointer-plus-extents constructors, because requiring pointer arithmetic pushes unsafe boilerplate to every call site.
40. Make result types compatible with structured bindings and std::tie, because non-standard access patterns force boilerplate at every call site.
41. Use one type-erasure pattern consistently across analogous wrappers, because inconsistency between related types confuses users and signals a design gap.
42. Ensure consistent APIs across analogous types, because inconsistency signals an underlying design flaw.

</buffer-and-protocol-design>

## VII. Interface Breadth and Portability

<interface-breadth-and-portability>

APIs should be as general as their domain allows. Arbitrary restrictions surprise users, and platform-conditional interfaces make portable code painful. Design for the widest valid use, then constrain only with explicit justification.

43. Do not restrict interfaces when you cannot predict all use cases, because narrow APIs force workarounds.
44. Make functions available for all valid dimensionalities unless a restriction has explicit use-case justification, because arbitrary limits surprise users.
45. Keep cross-platform interfaces identical even when a feature is redundant on one platform, because conditional APIs make portable code harder to maintain.
46. Allow user-supplied execution contexts for I/O objects, because hard-coupling to a single context type prevents customization.
47. Pass executors rather than execution contexts, because coupling code to a specific context limits composition.
48. Provide a terminate function for child processes, because you cannot control whether a foreign binary will exit on its own.
49. Do not hardcode a single standard version in build flags, because the build must also work with future standards.

</interface-breadth-and-portability>

## VIII. Review and Process

<review-and-process>

Review effectiveness depends on verifiable conditions and relevant communication. Subjective directives stall progress, and irrelevant messages cause disengagement. State what success looks like in terms anyone can check.

50. State review conditions as objectively verifiable requirements, because vague improvement directives cannot be confirmed without another review.
51. Explain the reasoning behind contested decisions in a review, because other reviewers need to weigh criticism against intent.
52. Consider the relevancy of a broadcast message before sending, because irrelevant traffic causes recipients to disengage.
53. Do not invest disproportionate effort in code paths that will never execute in practice, because the maintenance cost exceeds the value.
54. Mirror infrastructure in parallel before disabling the original, because parallel operation lets you validate before committing.
55. Make implementation details private, because exposing internal state creates an accidental API users will depend on.
56. Include forward-declaration headers like iosfwd instead of full headers like iostream, because forward declarations reduce compile-time dependencies.
57. Store configuration options as data members set at construction rather than passing them to every call, because repeated parameters clutter call sites and invite inconsistency.
58. Use variadic named parameters when a function has many optional configuration properties, because most calls use only a few and a flat parameter list is unreadable.

</review-and-process>

## The Approach Behind the Rules

Not everything Klemens does converts to a rule, because the rules are the residue of a practice, not the practice itself. At the center of his craft is a conviction that a library exists to serve its users' real needs, never to demonstrate a coding style, and that a mature codebase built for one shop will carry features and habits that have no business in a general-purpose artifact. He reaches for abstractions that match reality on its own terms, insisting that memory is untyped so the interface should say so, that cancellation belongs to the handler rather than the stream, and that each language deserves solutions native to its strengths rather than workarounds imported from another. His pragmatism shows in design choices like making eager-versus-lazy a runtime decision with valid semantics for both paths, preferring to let the program decide rather than the library author.

When he hits a limit in someone else's work, a signature habit appears: he leads with genuine admiration for the effort before delivering an honest verdict that the thing is not ready, separating respect for the goal from evaluation of the artifact. That same honesty turns inward, as when he acknowledges adding a conditional branch without profiling and calls it probably overdoing it, or admits that copying JavaScript's default for NaN serialization was likely the wrong choice. He is equally attentive to the humans around the code, weighing whether a mailing-list message is relevant enough to justify the phone notification it will trigger. The craft, for Klemens, ultimately rests in the gap between something that is useful and something that is ready, and in the willingness to say so plainly while still honoring the work that got it there.

*2026-07-30 07:52 - claude-sonnet-4-20250514*
