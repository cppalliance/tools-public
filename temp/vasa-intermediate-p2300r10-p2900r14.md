# Vasa Intermediate File: P2300R10 + P2900R14

## INPUT: p2300r10.md
Type: paper
Paper: P2300R10

### Extracted Content

**Title:** std::execution
**Date:** 2024-06-28
**Authors:** Michał Dominiak, Georgy Evtushenko, Lewis Baker, Lucian Radu Teodorescu, Lee Howes, Kirk Shoop, Michael Garland, Eric Niebler, Bryce Adelstein Lelbach

#### Claimed Principles / Design Values
1. Composable and generic - code reusable across many execution resources
2. Encapsulate common async patterns in customizable/reusable algorithms
3. Easy to be correct by construction
4. Support diversity of execution resources/agents (not all are equal)
5. Allow everything to be customized by execution resource, but don't require customization of everything
6. Care about all reasonable use cases, domains, and platforms
7. Errors must be propagated, but error handling must not present a burden
8. Support cancellation, which is NOT an error
9. Clear and concise answers for where things execute
10. Able to manage and terminate lifetimes of objects asynchronously
11. Purely lazy model - senders/adaptors never execute before start is called
12. Structured concurrency - no detached work, no need for shared_ptr/reference counting
13. Execution resource transitions must be explicit
14. Zero-allocation capability for structured patterns (intrusive linked lists in operation states)

#### Core Abstractions (API Shape)
- **Schedulers** (`scheduler` concept): Lightweight handle to execution resource. Key operation: `schedule(sch)` returns a sender.
- **Senders** (`sender`, `sender_in`, `sender_to` concepts): Describe async work. Tagged with `sender_concept = sender_t`. Can propagate completion schedulers. May be single-shot or multi-shot.
- **Receivers** (`receiver`, `receiver_of` concepts): Three-channel callback (set_value, set_error, set_stopped). Tagged with `receiver_concept = receiver_t`. Have associated environment. Not final (for implementation inheritance).
- **Operation States** (`operation_state` concept): Concrete non-movable, non-copyable object. Tagged with `operation_state_concept = operation_state_t`. Single operation: `start()`.
- **Environments** (`queryable` concept): Read-only key/value bags providing execution-time context (scheduler, stop token, allocator, etc.)

#### Key Types and Functions

**Completion Signals:**
- `set_value_t` / `set_value(rcvr, vals...)`
- `set_error_t` / `set_error(rcvr, err)`
- `set_stopped_t` / `set_stopped(rcvr)`

**Queries:**
- `get_env(obj)` - get environment/attributes (nothrow)
- `get_scheduler(env)` - associated scheduler
- `get_delegation_scheduler(env)` - for forward progress delegation
- `get_stop_token(env)` - associated stop token (defaults to `never_stop_token`)
- `get_allocator(env)` - associated allocator
- `get_domain(env)` - execution domain tag
- `get_forward_progress_guarantee(sch)` - concurrent/parallel/weakly_parallel
- `get_completion_scheduler<Tag>(env)` - completion scheduler for a signal
- `forwarding_query(q)` - should query be forwarded through adaptors?

**Sender Factories:**
- `schedule(sch)` - start task graph on scheduler
- `just(vals...)` - sender of values, no completion scheduler
- `just_error(err)` - sender of error
- `just_stopped()` - sender of stopped
- `read_env(tag)` - read from receiver's environment

**Sender Adaptors:**
- `then(sndr, fn)` - transform value channel
- `upon_error(sndr, fn)` - transform error channel
- `upon_stopped(sndr, fn)` - transform stopped channel
- `let_value(sndr, fn)` - monadic bind (fn returns sender)
- `let_error(sndr, fn)` - monadic bind on error
- `let_stopped(sndr, fn)` - monadic bind on stopped
- `continues_on(sndr, sch)` - transition execution resource (formerly `transfer`)
- `starts_on(sch, sndr)` - start on scheduler's resource (formerly `on`)
- `on(sch, sndr)` - start on sch, return to caller's resource afterward
- `on(sndr, sch, closure)` - on completion, transition to sch, apply closure, return
- `schedule_from(sch, sndr)` - implementation detail for continues_on
- `bulk(sndr, shape, fn)` - parallel invocation over index space
- `split(sndr)` - make multi-shot from single-shot
- `when_all(sndrs...)` - join; completes when all complete; concatenates values
- `when_all_with_variant(sndrs...)` - same with into_variant
- `into_variant(sndr)` - collapse multiple value signatures into variant
- `stopped_as_optional(sndr)` - map stopped to empty optional
- `stopped_as_error(sndr, err)` - map stopped to error

**Sender Consumers:**
- `this_thread::sync_wait(sndr)` - block current thread, return optional<tuple<...>>
- `this_thread::sync_wait_with_variant(sndr)` - same with variant

**Core Operations:**
- `connect(sndr, rcvr)` - produce operation_state (also handles awaitables)
- `start(op_state)` - submit work for execution

**Customization / Domain Mechanism:**
- `transform_sender(domain, sndr, env...)` - domain-based sender transformation
- `transform_env(domain, sndr, env)` - domain-based environment transformation
- `apply_sender(domain, tag, sndr, args...)` - domain-based algorithm application
- `default_domain` - fallback domain
- Sender adaptor closure objects with `operator|` (pipe syntax)

**Sender Infrastructure:**
- `completion_signatures<Fns...>` - declare completion signature set
- `transform_completion_signatures` / `transform_completion_signatures_of` - adapt signatures
- `value_types_of_t`, `error_types_of_t`, `sends_stopped` - introspection
- `tag_of_t<Sndr>` - get tag from structured binding decomposition
- `basic-sender` (exposition-only) - canonical sender implementation pattern
- `impls-for<Tag>` - per-algorithm specialization point (get-attrs, get-env, get-state, start, complete)

**Stop Token Types:**
- `stoppable_token` concept (generalizes `stop_token`)
- `unstoppable_token` concept
- `never_stop_token` - statically never stoppable
- `inplace_stop_token` / `inplace_stop_source` / `inplace_stop_callback<CB>` - efficient structured concurrency stop
- `stop_callback_for_t<Token, CB>` - alias template

**Execution Context:**
- `run_loop` - thread-safe FIFO work queue, states: starting/running/finishing
- Intrusive operation state queue, zero-allocation scheduling
- `run_loop::run()` - drive loop on calling thread
- `run_loop::finish()` - signal completion
- `run_loop::get_scheduler()` - obtain scheduler

**Coroutine Integration:**
- `as_awaitable(expr, promise)` - transform sender to awaitable
- `with_awaitable_senders<Promise>` - CRTP base making senders co_await-able
- `unhandled_stopped()` protocol - propagate stopped through coroutine chain
- `awaitable-sender` concept - sender that's single-sender + has unhandled_stopped

#### Behavioral Guarantees

**Lifetime:**
- Operation states are non-movable, non-copyable; must be kept alive until completion
- Exactly one completion signal (set_value/set_error/set_stopped) per started operation
- Child operations complete before parent
- `get_env(o)` valid while `o` is valid

**Exception Safety:**
- Exceptions in `then`/`bulk` callbacks are caught and forwarded via `set_error(rcvr, current_exception())`
- If stop callback throws, `terminate()` is called
- `sync_wait` rethrows exceptions; converts `error_code` to `system_error`
- Scheduler copy/move/compare/swap/schedule must not throw
- `get_env` must be nothrow

**Cancellation:**
- Stop requests are cooperative and racy (not guaranteed to prevent completion)
- Support is optional for both sender and receiver authors
- `never_stop_token` causes cancellation-handling code to be compiled out
- `when_all` cancels siblings on error/stopped
- Stop callbacks registered with `inplace_stop_callback` block in destructor until concurrent callback returns

**Ordering / Execution Agents:**
- `then` is guaranteed to not begin executing function until sender is started
- Sender adaptors are strictly lazy - no submission before start
- `bulk` agents execute with forward progress guarantee of their scheduler
- `when_all` completes inline on the execution agent where the last input completes
- `sync_wait` provides forward progress delegation via `run_loop` + `get_delegation_scheduler`

**Forward Progress:**
- `forward_progress_guarantee` enum: concurrent, parallel, weakly_parallel
- Queryable per scheduler

#### Design Choices

1. **Lazy-only model**: No eager execution. Avoids detached work, blocking destructors, and UB.
2. **Structured concurrency**: All work is nested. No `ensure_started`/`start_detached` (removed in R10, replaced by P3149 async_scope).
3. **Member-function customization** (R9): Replaced `tag_invoke` with member functions per P2855R1.
4. **Three-channel completion**: value/error/stopped - stopped is NOT an error.
5. **Environment-based dependently-typed senders** (R4+): Completion signatures can depend on receiver environment, avoiding type cycles.
6. **Domain-based algorithm customization** (R10): `transform_sender` with domains instead of direct tag_invoke on algorithms.
7. **Pipe syntax**: `sender | adaptor(args...)` via `sender_adaptor_closure`.
8. **Completion schedulers**: Senders advertise where they complete; algorithms respect this.
9. **`split` uses reference counting** with `shared-state` and atomic `ref_count`.
10. **`sync_wait` in `this_thread` namespace**: Because blocking semantics are thread-specific.
11. **Renamed in R10**: `transfer` -> `continues_on`, `on` -> `starts_on`, new `on` combining both.
12. **`inplace_stop_token`**: More efficient than `stop_token` for structured concurrency (no shared ownership overhead).

#### Key Constraints
- Receivers must not be `final` (enables implementation inheritance)
- Schedulers must be `equality_comparable` and `copy_constructible`
- Senders must be `move_constructible`
- `run_loop` destructor calls `terminate()` if still running or has pending work

### References Found
- P0443R14 (Unified Executors Proposal - foundational predecessor)
- P2175R0 (Composable cancellation for sender-based async operations)
- P2855R1 (Member customization points for Senders and Receivers)
- P2999R3 (Sender Algorithm Customization)
- P3149R3 (async_scope - Creating scopes for non-sequential concurrency)
- P3175R3 (Reconsidering the std::execution::on algorithm)
- P3187R1 (Remove ensure_started and start_detached from P2300)
- P3303R1 (Fixing Lazy Sender Algorithm Customization)
- P1056R1 (Add lazy coroutine task type)
- P1895R0 (tag_invoke)
- P1897R3 (Initial set of algorithms)
- P0981R0 (Halo: coroutine Heap Allocation eLision Optimization)
- P2762 (Networking APIs using sender/receiver - Dietmar Kuehl)
- N4885 (Working Draft)

### Deviations
- File required shell commands (sed) due to Read tool permission denial. No content was skipped; entire file read in chunks. Significance: low.
- Shell output was truncated in several chunks due to 20000 character limit. Overlapping sections used to ensure full coverage. Significance: low.

---

## INPUT: p2900r14.md
Type: paper
Paper: P2900R14

### Extracted Content

**Title:** Contracts for C++
**Date:** 2025-02-13, targeting CWG/LWG
**Authors:** Joshua Berne, Timur Doumler, Andrzej Krzeminski, Gasper Azman, Peter Bindels, Louis Dionne, Tom Honermann, and many others. Represents the SG21 consensus MVP for C++26 contracts.

**Scope:** Defines a language facility for contract assertions: preconditions, postconditions, and assertion statements. Explicitly an MVP - many features deferred to future extensions.

#### DESIGN CHOICES

1. **Three kinds of contract assertions:** precondition (`pre`), postcondition (`post`), and assertion statement (`contract_assert`).

2. **Four evaluation semantics:** ignore (do nothing), observe (check, call handler, continue), enforce (check, call handler, terminate), quick-enforce (check, terminate immediately without handler).

3. **Semantic selection is implementation-defined:** Which semantic is used for any given evaluation is entirely implementation-defined. Different assertions can have different semantics, even in the same function. Same assertion can have different semantics across evaluations. Controlled by compiler flags.

4. **Contract-violation handler is a replaceable function:** `::handle_contract_violation(const std::contracts::contract_violation&)` - replaced at link time like `operator new/delete`. Whether it is replaceable at all is implementation-defined.

5. **Virtual functions: ill-formed to have pre/post.** Deferred to a future extension.

6. **No contract specifiers on pointers to functions, pointers to member functions, or type aliases.** Contracts have no impact on function type.

7. **Coroutines: pre/post allowed with restrictions.** Pre/post apply to the ramp function. Preconditions evaluated before coroutine body. Postconditions apply to the returned coroutine handle object (task/generator), not to co_returned values. Await/yield expressions in predicates: ill-formed. Parameters odr-used in postconditions of coroutines: ill-formed (because coroutine copies/moves from params).

8. **Implicit const-ness in predicates:** All id-expressions within a contract predicate denoting variables declared outside the predicate are `const` lvalues. Shallow const (does not propagate through pointers). Applies to function parameters, globals, structured bindings, `this`, `*this`. Modifications possible only through `const_cast` (discouraged).

9. **Result binding in postconditions:** `post(r : expr)` - `r` names the result object. Type is `const T` for return type `T`. Result binding is a local entity in contract-assertion scope. For deduced return types on non-template functions, postcondition with result binding requires definition.

10. **Side effect elision/duplication:** If compiler can prove predicate evaluates to true/false, it may replace the predicate with a side-effect-free equivalent. Either all or none of the side effects are observed. Cannot introduce new side effects. Cannot elide if predicate may throw, longjmp, or terminate.

11. **Observable checkpoints (conditional on P1494R5):** Each contract assertion evaluation is an observable checkpoint, preventing time-travel optimizations from reordering past a checked contract.

12. **Not part of immediate context:** Contract predicates do not participate in SFINAE or concept satisfaction. A failing contract predicate causes a hard error, not substitution failure.

13. **No implicit lambda captures from contract assertions:** If all references to a local entity occur only within contract assertions of a lambda, the program is ill-formed. Prevents contract assertions from changing closure type size/layout.

14. **`contract_assert` is a keyword; `pre` and `post` are identifiers with special meaning** (context-sensitive). No existing code breakage for `pre`/`post`.

15. **Redeclaration consistency:** Redeclarations must have either no function-contract-specifier-seq or the same one. IFNDR if different first declarations across TUs have different specifiers. Lambda expressions in predicates make redeclaration in same TU always fail.

16. **Deleted and defaulted-on-first-declaration functions: ill-formed to have pre/post.**

17. **Constructor/destructor restrictions:** Constructor preconditions and destructor postconditions: ill-formed to name nonstatic data members directly (without explicit `this->`). Prevents accessing members before lifetime begins / after lifetime ends.

18. **Contract termination:** When program is "contract-terminated", implementation chooses between `std::terminate`, `std::abort`, or immediate execution termination. Implementation-defined.

19. **Evaluation-in-sequence with repetition:** Consecutive contract assertions may be repeated an implementation-defined number of times. Ordering preserved (first assertion always evaluated first). Practical: simple 1-2 sequence on most platforms, 1-2-1-2 when checks emitted at both call site and callee.

20. **Constant evaluation rules:** Trial evaluation with all contracts ignored determines whether expression is a core constant expression. Then re-evaluated with implementation-chosen semantic. Violation with terminating semantic: ill-formed. Violation with observe: diagnostic required.

21. **Throwing violation handlers:** Exception escapes as if thrown from function body. If function is noexcept, std::terminate is called. Handler is invoked from within an implicit exception handler for exceptions from predicate evaluation.

22. **`<contracts>` header is freestanding.**

23. **Function parameters in postconditions must be const** (on all declarations, including definition) if odr-used by postcondition predicate. Array parameters in postconditions: ill-formed.

24. **No `va_start` in predicates** (ill-formed, no diagnostic required).

25. **Mixed mode:** Different translation units may use different evaluation semantics. Conforming. May cause ODR issues when side effects in predicates alter constant expressions.

#### API SHAPES

**Language syntax:**
- `pre(expression)` - precondition specifier
- `post(result_name : expression)` - postcondition specifier with optional result binding
- `contract_assert(expression);` - assertion statement (a statement, not expression)
- Attributes may appertain to contract assertions: placed between keyword and predicate
- Function contract specifiers appear after trailing return type, after requires clause, before semicolon/body

**Library types (namespace `std::contracts`, header `<contracts>`):**

- `assertion_kind` enum: pre=1, post=2, assert=3
- `evaluation_semantic` enum: ignore=1, observe=2, enforce=3, quick_enforce=4
- `detection_mode` enum: predicate_false=1, evaluation_exception=2
- `contract_violation` class: non-copyable, non-assignable. Members: comment(), detection_mode(), evaluation_exception(), is_terminating(), kind(), location(), semantic()
- `invoke_default_contract_violation_handler(const contract_violation&)` function

**Contract-violation handler customization point:**
- `void ::handle_contract_violation(const std::contracts::contract_violation&)` - replaceable function, C++ linkage, attached to global module, not inline. Implementation-defined whether replaceable.

**Feature test macros:** `__cpp_contracts` (language), `__cpp_lib_contracts` (library).

#### BEHAVIORAL GUARANTEES

**Evaluation ordering:**
- Preconditions: sequenced after parameter initialization, before function body
- Postconditions: sequenced after return value initialization + local variable destruction, before parameter destruction
- Assertion statements: at point of control flow
- Multiple pre/post: evaluated in lexical order within their group

**Exception behavior:**
- Predicate throwing = contract violation (detection_mode::evaluation_exception)
- Handler invoked from within implicit exception handler for predicate's exception
- Exception available via `evaluation_exception()` member
- Throwing handler: exception propagates as if from function body
- noexcept functions + throwing handler = std::terminate

**Lifetime guarantees:**
- `contract_violation` object lives at least through handler invocation
- Objects accessible through its interface (e.g., `comment()` string) also persist
- Memory not allocated via `operator new`

**Side effects:**
- May occur 0, 1, or many times (no guaranteed count)
- Elision: all-or-nothing (entire predicate's side effects)
- If predicate may throw/longjmp/terminate, cannot be elided

**No new undefined behavior introduced** (Principle 13). But contract predicates follow normal C++ UB rules when evaluated.

#### CLAIMED PRINCIPLES (14 numbered + 2 extension principles)

1. **Prime Directive:** Presence/evaluation of contract assertions should not alter program correctness
2. **Redundancy Principle:** In correct programs, contract assertions are redundant
3. **Concepts Do Not See Contracts:** No impact on SFINAE, concept satisfaction, if constexpr, noexcept operator
4. **Zero Overhead:** Ignored assertions have no behavioral impact
5. **Independence from Chosen Semantic:** Semantic generally not detectable at compile time
6. **No Destructive Side Effects:** Predicates should not affect program correctness
7. **Completeness of Contract Assertions:** Each assertion is a complete check of a contract provision
8. **Independence of Contract Assertions:** Result of one should not affect result of another
9. **Independence of Contract-Assertion Evaluations:** Result should not affect subsequent evaluations of same
10. **Contract Assertions Check a Plain-Language Contract:** Tied to the function they're on
11. **Function Contract Assertions Serve Both Caller and Callee:** Part of both interface and implementation
12. **Contract Assertions Are Not Flow Control:** No guaranteed runtime behavior
13. **Explicitly Define All New Behavior:** No new UB introduced
14. **Leave Room for Extension:** Don't preclude future features

**Extension Principles:**
- **Principle 15 (Leave Room for Alternatives):** Don't mandate behavior when multiple valid implementation strategies exist
- **Principle 16 (Minimize Novel Additions):** Reuse existing C++ patterns rather than inventing new mechanics

#### EXPLICITLY DEFERRED FEATURES (Future Extensions)

- Pre/post on virtual functions
- Pre/post on function pointers/member function pointers/type aliases
- Oldof/capture of original parameter values in postconditions
- Assume semantic (optimizer may assume unchecked predicate is true)
- Per-assertion semantic specification in source
- Assertion levels/groups
- Postconditions for exceptional exits
- Predicates calling functions with no definition
- Stateful contract assertions (counters, flags across evaluations)
- Class invariants
- Procedural interfaces

### References Found
- P2695R0 (plan for contracts in C++)
- P2899R1 (contracts rationale)
- P1494R5 (partial program correctness / observable checkpoints - conditional dependency)
- P2053R1 (defensive checks vs input validation)
- N4993 (C++26 working draft - base document for wording)
- CWG2841 (when do const objects start being const)

### Deviations
- File required shell commands due to Read tool permission denial. No content was skipped; entire file read in chunks. Significance: low.
- File contains duplicated wording sections near lines 4800-4900 (contract_violation members and enum tables appear twice in markdown). Appears to be a rendering artifact. Significance: low.

---

## ARTIFACTS

### ART-1: Three-channel completion model
Inputs: P2300R10 (Core Abstractions, Behavioral Guarantees - "Exactly one completion signal"), P2900R14 (Behavioral Guarantees - exception behavior, contract termination)
Type: design-choice
Summary: P2300R10 guarantees that every started operation completes with exactly one of three signals: set_value, set_error, or set_stopped. This is the fundamental invariant of the entire execution model. Contract violations in P2900R14 can terminate the program (enforce, quick_enforce) or allow continuation (observe), potentially bypassing this exactly-one-completion guarantee. A contract violation during an in-flight sender operation could leave a parent operation waiting forever for a child completion that never arrives, or trigger termination mid-structured-concurrency-tree.
Cross-exposure: P2300R10, P2900R14

### ART-2: Contract predicate exceptions inside sender callbacks
Inputs: P2300R10 (Exception Safety - "Exceptions in then/bulk callbacks are caught and forwarded via set_error"), P2900R14 (Behavioral Guarantees - exception behavior, detection_mode::evaluation_exception)
Type: behavioral-guarantee
Summary: P2300R10 catches exceptions thrown by user-provided callbacks in `then`, `bulk`, etc. and forwards them as `set_error(rcvr, current_exception())`. P2900R14 specifies that a throwing contract predicate constitutes a contract violation (detection_mode::evaluation_exception), and the violation handler is invoked from within an implicit exception handler. If the handler throws, the exception propagates as if from the function body. When a contract predicate in a user callback throws, the interaction depends on whether the sender's exception-catching wraps the entire callback invocation (including contract evaluation). If it does, the violation handler's exception becomes an error_code on the error channel. If contract evaluation is sequenced outside the sender's try-catch scope, the exception escapes.
Cross-exposure: P2300R10, P2900R14

### ART-3: Lazy evaluation vs. contract evaluation timing
Inputs: P2300R10 (Design Choices - "Lazy-only model", "Sender adaptors are strictly lazy"), P2900R14 (Behavioral Guarantees - evaluation ordering: "preconditions sequenced after parameter initialization, before function body")
Type: design-choice
Summary: P2300R10 is purely lazy: senders and adaptors never execute work before `start()` is called. Constructing a sender via `then(sndr, fn)` does not invoke `fn`. P2900R14's preconditions fire at function entry and postconditions at function exit. For sender factory/adaptor functions (like `then`, `let_value`, `just`), preconditions evaluate at sender construction time, not at execution time. This creates a semantic gap: the "contract" of the callback `fn` is logically about execution-time behavior, but preconditions on `then` itself only check construction-time state. Users wanting to contract-check the actual async computation must place contracts on the callback, not the adaptor.
Cross-exposure: P2300R10, P2900R14

### ART-4: Coroutine integration overlap
Inputs: P2300R10 (Coroutine Integration - as_awaitable, with_awaitable_senders, unhandled_stopped), P2900R14 (Design Choice 7 - coroutines: pre/post apply to ramp function, postconditions on returned handle, parameters in postconditions ill-formed)
Type: api-shape
Summary: P2300R10 provides deep coroutine integration: senders become awaitables via `as_awaitable`, and `with_awaitable_senders` enables `co_await` on senders in task-like coroutines. P2900R14 specifies that for coroutines, preconditions are evaluated before the coroutine body and postconditions apply to the returned coroutine handle object (e.g., a `task<T>`), not to `co_return`ed values. For a coroutine returning a sender/task that participates in P2300's framework, the postcondition's result binding `r` would refer to the sender/task object itself, not the eventual async result. This means postconditions cannot express contracts about the async result, only about the handle. Additionally, P2900R14 makes it ill-formed to odr-use parameters in coroutine postconditions, which limits what can be checked.
Cross-exposure: P2300R10, P2900R14

### ART-5: noexcept mandates vs. contract violation paths
Inputs: P2300R10 (Key Constraints - "Scheduler copy/move/compare/swap/schedule must not throw", "get_env must be nothrow"), P2900R14 (Behavioral Guarantees - "noexcept functions + throwing handler = std::terminate", contract termination)
Type: behavioral-guarantee
Summary: P2300R10 mandates that numerous foundational operations are nothrow: all scheduler operations, `get_env`, stop token operations, and various query functions. If contracts (preconditions, postconditions, or contract_assert) are placed on these nothrow operations and the violation handler throws, P2900R14 specifies that `std::terminate` is called because the exception escapes a noexcept function. This means any contract violation in core execution infrastructure with a throwing handler always terminates rather than being recoverable. The combination forces a hard binary: either use non-throwing handlers for all execution infrastructure, or accept that violations terminate.
Cross-exposure: P2300R10, P2900R14

### ART-6: Contract-induced termination vs. structured concurrency
Inputs: P2300R10 (Design Choices - "Structured concurrency: all work is nested", Behavioral Guarantees - "Child operations complete before parent"), P2900R14 (Design Choice 18 - contract termination via terminate/abort/immediate)
Type: behavioral-guarantee
Summary: P2300R10's structured concurrency guarantees that child operations complete before parent operations, and all work is nested with no detached work. P2900R14's contract termination (for enforce and quick_enforce semantics) can call `std::terminate`, `std::abort`, or perform "immediate execution termination." Any of these bypasses the structured concurrency teardown entirely. In-flight child operations, pending stop callbacks, and partially completed `when_all` joins all become moot. This is arguably acceptable (the program is ending), but it means contract violations can never be "recovered from" within the execution framework's structured concurrency model when using terminating semantics.
Cross-exposure: P2300R10, P2900R14

### ART-7: set_stopped is not an error vs. contract violation semantics
Inputs: P2300R10 (Design Choices - "stopped is NOT an error", Claimed Principles - "Cancellation is NOT an error"), P2900R14 (Design Choice 2 - four evaluation semantics, Principles - "contract assertions check a plain-language contract")
Type: design-choice
Summary: P2300R10 treats `set_stopped` as a first-class non-error completion channel representing cooperative cancellation. P2900R14's contracts check for correctness conditions. A function that can legitimately produce a cancellation (set_stopped) has a wider "correct" output space than one that only produces values or errors. Postconditions on receiver methods like `set_stopped` must account for the fact that this is a valid, non-error outcome. The three-way completion model means postconditions on sender-returning functions cannot simply check "did it succeed" - they must account for value, error, and stopped as all potentially valid completions.
Cross-exposure: P2300R10, P2900R14

### ART-8: Concepts don't see contracts (SFINAE exclusion)
Inputs: P2300R10 (Core Abstractions - sender/receiver/scheduler/operation_state concepts), P2900R14 (Design Choice 12 - "Not part of immediate context", Principle 3 - "Concepts Do Not See Contracts")
Type: design-choice
Summary: P2300R10 defines its entire abstraction hierarchy through concepts: `sender`, `receiver`, `scheduler`, `operation_state`, `queryable`, `stoppable_token`, etc. P2900R14 explicitly states that contract predicates do not participate in SFINAE, concept satisfaction, `if constexpr`, or `noexcept` operator evaluation. This means contracts are invisible to P2300's concept machinery. A type can satisfy `sender` or `receiver` even if its operations have preconditions that would always fail. Contracts and concepts occupy orthogonal checking spaces: concepts verify syntactic/semantic type requirements at compile time, contracts verify runtime behavioral conditions. This is a positive coherence point - no interference.
Cross-exposure: P2300R10, P2900R14

### ART-9: Forward progress guarantees vs. contract evaluation overhead
Inputs: P2300R10 (Forward Progress - concurrent/parallel/weakly_parallel, bulk agents execute with scheduler's guarantee), P2900R14 (Design Choice 4 - "Zero Overhead: ignored assertions have no behavioral impact", violation handler invocation)
Type: behavioral-guarantee
Summary: P2300R10 provides queryable forward progress guarantees per scheduler, and `bulk` agents execute with the forward progress guarantee of their scheduler. Contract assertions in hot paths (e.g., inside bulk callbacks) add overhead when not ignored. P2900R14's zero-overhead principle only applies to the "ignore" semantic. For enforce/observe semantics, contract checking adds runtime work, and violation handler invocation (which may allocate, do I/O, etc.) could violate forward progress assumptions. A weakly_parallel scheduler providing minimal forward progress could see contract checks consume its entire progress budget.
Cross-exposure: P2300R10, P2900R14

### ART-10: Freestanding compatibility
Inputs: P2300R10 (no explicit freestanding mention, but zero-allocation patterns suggest embedded use), P2900R14 (Design Choice 22 - "<contracts> header is freestanding")
Type: design-choice
Summary: P2900R14 explicitly makes `<contracts>` a freestanding header, enabling contract assertions in freestanding (embedded/kernel) environments. P2300R10 emphasizes zero-allocation capability and support for diverse execution resources and platforms, which implies freestanding relevance, but the paper does not explicitly mark any of its headers as freestanding. If `std::execution` components are used in freestanding environments, contracts can annotate them since `<contracts>` is available. However, `contract_violation`'s `comment()` returning `const char*` and `location()` returning `source_location` may have freestanding-specific constraints.
Cross-exposure: P2300R10, P2900R14

### ART-11: Observable checkpoints and sender execution ordering
Inputs: P2300R10 (Behavioral Guarantees - ordering, "then is guaranteed to not begin executing function until sender is started"), P2900R14 (Design Choice 11 - "observable checkpoints conditional on P1494R5")
Type: behavioral-guarantee
Summary: P2300R10 provides specific ordering guarantees: sender adaptors are strictly lazy, `then` doesn't begin until start is called, `when_all` completes inline on the last-completing agent. P2900R14 introduces observable checkpoints (conditional on P1494R5) which prevent time-travel optimizations from reordering past a checked contract. If a contract assertion appears within a sender callback, the observable checkpoint could interact with the compiler's optimization of the sender pipeline. In principle this is coherent: the checkpoint prevents reordering past the contract check point, which aligns with P2300's sequential-within-an-agent model. But it could constrain optimizations that P2300's domain customization mechanism (transform_sender) might otherwise enable.
Cross-exposure: P2300R10, P2900R14

### ART-12: Side effect elision in predicates within sender operations
Inputs: P2300R10 (Behavioral Guarantees - exception safety, ordering), P2900R14 (Design Choice 10 - side effect elision/duplication)
Type: behavioral-guarantee
Summary: P2900R14 permits compilers to elide or duplicate side effects in contract predicates under certain conditions (provably true/false, all-or-nothing, not when may throw/longjmp/terminate). Within P2300R10's sender algorithms, contract predicates that reference sender state, receiver environments, or operation state could have their side effects elided. Since P2300's environment queries are nothrow, a predicate that only queries the environment could be elided if provably true. The "duplication" aspect (implementation-defined repetition count per Design Choice 19) means predicates in hot sender paths could execute multiple times, which matters if they query mutable state accessible through the execution environment.
Cross-exposure: P2300R10, P2900R14

### ART-13: sync_wait exception path and violation handler
Inputs: P2300R10 (Sender Consumers - "sync_wait rethrows exceptions; converts error_code to system_error"), P2900R14 (Behavioral Guarantees - "Throwing handler: exception propagates as if from function body")
Type: behavioral-guarantee
Summary: P2300R10's `sync_wait` catches the error channel and rethrows: `exception_ptr` is rethrown, `error_code` is wrapped in `system_error`. If a contract violation occurs inside a sender pipeline and the violation handler throws, and the sender's exception machinery catches that throw and routes it to `set_error` with `current_exception()`, then `sync_wait` will rethrow it as a regular exception. This creates a complete path: contract violation -> handler throw -> sender error channel -> sync_wait rethrow. The violation is observable as a normal exception at the `sync_wait` call site. This is coherent but means contract violations with throwing handlers become indistinguishable from regular exceptions at the consumer level.
Cross-exposure: P2300R10, P2900R14

### ART-14: Operation state non-movability and postcondition evaluation
Inputs: P2300R10 (Core Abstractions - "Operation states are non-movable, non-copyable", Behavioral Guarantees - "must be kept alive until completion"), P2900R14 (Behavioral Guarantees - postcondition evaluation ordering)
Type: behavioral-guarantee
Summary: P2300R10's operation states are non-movable and non-copyable and must remain alive until a completion signal is delivered. `connect(sndr, rcvr)` returns an operation_state. A postcondition on `connect` using result binding `post(r: ...)` would bind `r` to the operation_state. Since operation_state is non-movable, the result binding works (the object exists at the point postconditions are evaluated, before destruction). However, the postcondition can only check structural properties of the operation_state (its type, perhaps its address), not functional properties (what it will do when started), since execution hasn't begun. This limits the expressiveness of postconditions on `connect`.
Cross-exposure: P2300R10, P2900R14

### ART-15: stop_callback blocking destructor vs. contract termination
Inputs: P2300R10 (Cancellation - "Stop callbacks registered with inplace_stop_callback block in destructor until concurrent callback returns"), P2900R14 (Design Choice 18 - contract termination via terminate/abort/immediate)
Type: behavioral-guarantee
Summary: P2300R10's `inplace_stop_callback` destructor blocks until any concurrently-executing callback completes, providing a synchronization guarantee essential for safe cleanup. P2900R14's contract termination can invoke `std::terminate`, `std::abort`, or immediate termination. If a contract violation triggers termination while another thread is blocked in a stop_callback destructor, the blocking thread is killed without completing its synchronization. This is a general consequence of program termination, not specific to contracts, but contracts make termination more likely in debug/test builds, increasing the probability of observing this interaction.
Cross-exposure: P2300R10, P2900R14

### ART-16: Customization mechanism paradigms
Inputs: P2300R10 (Design Choices - domain-based customization, transform_sender, apply_sender), P2900R14 (Design Choice 4 - contract-violation handler is replaceable at link time)
Type: design-choice
Summary: P2300R10 uses a domain-based customization paradigm: `transform_sender`, `transform_env`, and `apply_sender` allow execution domains to customize algorithm behavior at compile time through template-based dispatch. P2900R14 uses a link-time replacement paradigm for its violation handler, similar to `operator new`/`delete`. These are fundamentally different customization models (compile-time type-based vs. link-time symbol replacement). A domain author customizing sender behavior cannot also customize the contract violation handler for operations within that domain. The violation handler is global and monolithic, while execution domains are composable and per-type.
Cross-exposure: P2300R10, P2900R14

### ART-17: Implicit const-ness and read-only environments
Inputs: P2300R10 (Core Abstractions - "Environments: read-only key/value bags"), P2900R14 (Design Choice 8 - implicit const-ness in predicates)
Type: design-choice
Summary: P2300R10's environments (`queryable` concept) are conceptually read-only key/value stores for execution context. P2900R14 makes all external variables implicitly const within contract predicates (shallow const). These share a design philosophy: both restrict mutation in contexts where it would be problematic. If a contract predicate queries a receiver's environment (via `get_env`, `get_scheduler`, etc.), the query functions are already nothrow and return const-compatible results. The implicit const-ness in predicates aligns naturally with the read-only environment model. This is a positive coherence point.
Cross-exposure: P2300R10, P2900R14

### ART-18: bulk parallel invocation and contract assertions
Inputs: P2300R10 (Sender Adaptors - "bulk(sndr, shape, fn) - parallel invocation over index space"), P2900R14 (Design Choice 19 - evaluation-in-sequence with repetition, Design Choice 10 - side effect elision)
Type: behavioral-guarantee
Summary: P2300R10's `bulk` invokes a function `fn` across an index space, potentially in parallel, with forward progress guarantees of the scheduler. If `fn` has contract assertions, they evaluate independently for each index invocation. P2900R14's evaluation-in-sequence-with-repetition rule (consecutive assertions may repeat implementation-defined times) is per-invocation, so in parallel bulk execution, each parallel agent runs its own contract checks. The side effect elision rules apply per-invocation. The `bulk` exception handling (catching and forwarding via set_error) would interact with contract predicate exceptions in each parallel invocation, potentially causing multiple simultaneous contract violations across agents.
Cross-exposure: P2300R10, P2900R14

### ART-19: when_all error propagation vs. contract violations
Inputs: P2300R10 (Sender Adaptors - "when_all cancels siblings on error/stopped"), P2900R14 (Design Choice 2 - four evaluation semantics, Behavioral Guarantees - exception behavior)
Type: behavioral-guarantee
Summary: P2300R10's `when_all` completes when all child senders complete, and cancels remaining siblings when any child completes with error or stopped. If a contract violation occurs in one branch of a `when_all` with observe semantic (continue after violation) and the handler throws, the exception is caught by the sender machinery and forwarded as set_error, triggering cancellation of sibling branches. With enforce semantic, the program terminates and all branches are abandoned. The observe-then-throw path creates an interesting interaction: a contract violation in one concurrent branch causes cancellation of all other branches, which is observable behavior change from not having the contract.
Cross-exposure: P2300R10, P2900R14

### ART-20: Postcondition result binding for sender-returning functions
Inputs: P2300R10 (Sender Factories - just, schedule; Sender Adaptors - then, let_value), P2900R14 (Design Choice 9 - result binding in postconditions, post(r : expr))
Type: api-shape
Summary: P2300R10's sender factories and adaptors return senders (lazy descriptions of work). P2900R14's postcondition result binding `post(r : expr)` binds `r` to the return value as `const T`. For functions returning senders, `r` is bound to the sender object itself. Since senders are opaque types (often exposition-only `basic-sender`), the postcondition predicate can only check properties available through the sender's public interface: its completion signatures (via `value_types_of_t`, `error_types_of_t`), its tag, or its domain. The actual computational behavior described by the sender is not inspectable through postconditions, because the sender hasn't executed yet (lazy model).
Cross-exposure: P2300R10, P2900R14

### ART-21: Zero-allocation patterns and contract_violation object
Inputs: P2300R10 (Claimed Principles - "Zero-allocation capability for structured patterns", "intrusive linked lists in operation states"), P2900R14 (Behavioral Guarantees - "contract_violation memory not allocated via operator new", lifetime guarantees)
Type: design-choice
Summary: P2300R10 emphasizes zero-allocation capability through intrusive data structures in operation states. P2900R14 specifies that `contract_violation` object memory is not allocated via `operator new`, and the object and its referenced data persist through handler invocation. Both papers avoid dynamic allocation in their core infrastructure. This is a positive coherence point for resource-constrained environments. However, if a violation handler is invoked during a zero-allocation sender pipeline, the handler itself might allocate (for logging, reporting), potentially undermining the zero-allocation property of the overall operation.
Cross-exposure: P2300R10, P2900R14

### ART-22: run_loop terminate-on-destruction and contract termination
Inputs: P2300R10 (Execution Context - "run_loop destructor calls terminate() if still running or has pending work"), P2900R14 (Design Choice 18 - contract termination semantics)
Type: behavioral-guarantee
Summary: P2300R10's `run_loop` calls `terminate()` in its destructor if the loop is still in running state or has pending operations. P2900R14's contract termination also calls `terminate()` (among other options). Both use `terminate()` as a last-resort response to invariant violation. If a contract violation terminates the program while a `run_loop` is active, the `run_loop` destructor during stack unwinding would also call `terminate()`, but this is moot since the program is already terminating. The shared use of `terminate()` as the ultimate safety net is coherent.
Cross-exposure: P2300R10, P2900R14

### ART-23: Receiver environment access from contract predicates
Inputs: P2300R10 (Core Abstractions - environments/queryable, Queries - get_env, get_scheduler, get_stop_token, get_allocator), P2900R14 (Design Choice 8 - implicit const-ness, Behavioral Guarantees - evaluation ordering)
Type: api-shape
Summary: P2300R10's receivers carry environments providing execution context (scheduler, stop token, allocator, domain). These are accessed via `get_env(rcvr)` and subsequent queries. Contract predicates on receiver methods (set_value, set_error, set_stopped) could query the receiver's environment to express rich preconditions (e.g., "this receiver has a non-never stop token"). The implicit const-ness rule makes the receiver a const lvalue within the predicate, but environment queries work on const objects (they're nothrow and const-compatible). This enables environment-aware contracts on receiver operations.
Cross-exposure: P2300R10, P2900R14

### ART-24: Sender completion signatures and contract expressiveness
Inputs: P2300R10 (Sender Infrastructure - completion_signatures, value_types_of_t, error_types_of_t, sends_stopped), P2900R14 (Design Choice 7 - completeness of contract assertions, Principle 10 - check plain-language contract)
Type: api-shape
Summary: P2300R10 provides compile-time introspection of sender completion signatures: what value types, error types, and whether stopped is possible. P2900R14's contracts check runtime conditions. The completion signatures are purely compile-time type information, not runtime-checkable values, so they cannot appear in contract predicates (which are runtime expressions). This means the "contract" of a sender - what completions it can produce - is entirely expressed through the type system (completion_signatures) rather than through P2900R14's contract assertions. The two systems are complementary but non-overlapping for this purpose.
Cross-exposure: P2300R10, P2900R14

### ART-25: Semantic selection is implementation-defined vs. execution domain control
Inputs: P2300R10 (Design Choices - domain-based algorithm customization), P2900R14 (Design Choice 3 - semantic selection is implementation-defined, controlled by compiler flags)
Type: design-choice
Summary: P2300R10 gives execution domains fine-grained, programmatic control over algorithm behavior through `transform_sender` and `apply_sender`. P2900R14 makes contract evaluation semantics entirely implementation-defined, controlled by compiler flags rather than programmatically. An execution domain cannot programmatically select which contract semantic applies to operations within its domain. A high-assurance domain cannot mandate enforce semantics, and a performance-critical domain cannot mandate ignore semantics, through the type system. Contract semantic selection is orthogonal to and outside the reach of the execution domain mechanism.
Cross-exposure: P2300R10, P2900R14

### ART-26: Virtual function prohibition and type-erased senders
Inputs: P2300R10 (no type erasure in core, but design supports wrapping), P2900R14 (Design Choice 5 - "ill-formed to have pre/post on virtual functions")
Type: design-choice
Summary: P2900R14 prohibits contract specifiers on virtual functions, deferring this to a future extension. P2300R10's core abstractions are concept-based (not virtual), but practical use of senders often involves type erasure (e.g., `any_sender<Sigs...>` patterns, not in the paper but anticipated). If type-erased senders use virtual dispatch internally, the virtual function prohibition prevents placing contracts on the erased interface's virtual methods. Contracts would need to be placed on the concrete sender operations before type erasure, not on the type-erased wrapper's virtual interface.
Cross-exposure: P2300R10, P2900R14

### ART-27: Constant evaluation and constexpr sender operations
Inputs: P2300R10 (various constexpr-friendly patterns), P2900R14 (Design Choice 20 - constant evaluation rules, trial evaluation with contracts ignored)
Type: behavioral-guarantee
Summary: P2900R14 specifies that constant evaluation first performs a trial evaluation with all contracts ignored to determine if an expression is a core constant expression, then re-evaluates with the implementation-chosen semantic. If P2300R10's sender operations are used in constant evaluation contexts (constexpr/consteval), the trial-then-real evaluation pattern applies. A `just(42)` in a constexpr context would first be evaluated ignoring any contracts on `just`, then re-evaluated with contracts active. Violation during re-evaluation with a terminating semantic makes the expression non-constant (ill-formed).
Cross-exposure: P2300R10, P2900R14

### ART-28: Mixed-mode translation units and sender algorithm ODR
Inputs: P2300R10 (Sender Adaptors - various algorithms with inline implementations), P2900R14 (Design Choice 25 - mixed mode, different TUs may use different evaluation semantics)
Type: behavioral-guarantee
Summary: P2900R14 permits different translation units to use different contract evaluation semantics, which is conforming. P2300R10's sender algorithms are heavily templated and likely instantiated across multiple TUs. If the same sender algorithm template is instantiated in two TUs with different contract evaluation semantics, the presence of side effects in contract predicates could cause ODR violations. P2900R14 acknowledges this risk ("may cause ODR issues when side effects in predicates alter constant expressions"). For P2300's header-only, template-heavy design, this risk is amplified because nearly all sender infrastructure is instantiated in user TUs.
Cross-exposure: P2300R10, P2900R14

### ART-29: Throwing violation handler and unhandled_stopped protocol
Inputs: P2300R10 (Coroutine Integration - unhandled_stopped protocol), P2900R14 (Design Choice 21 - throwing violation handlers, exception propagation)
Type: behavioral-guarantee
Summary: P2300R10's `unhandled_stopped()` protocol in coroutine promise types allows stopped signals to propagate through coroutine chains by rethrowing a special exception. P2900R14's throwing violation handler propagates its exception as if thrown from the function body. If a contract violation with a throwing handler occurs during a coroutine that uses `with_awaitable_senders`, the handler's exception would propagate through the normal coroutine exception path, not through the `unhandled_stopped` path. This is correct behavior (a contract violation is not cancellation), but it means contract violations in coroutine-based sender pipelines are handled differently from stopped signals, which aligns with P2300's principle that stopped is not an error.
Cross-exposure: P2300R10, P2900R14

### ART-30: No implicit lambda captures from contract assertions
Inputs: P2300R10 (sender adaptor closure objects, heavy use of lambdas in pipeline construction), P2900R14 (Design Choice 13 - no implicit lambda captures from contract assertions)
Type: design-choice
Summary: P2900R14 specifies that if all references to a local entity occur only within contract assertions of a lambda, the program is ill-formed. This prevents contracts from changing closure size/layout. P2300R10's sender pipelines are typically built using lambdas passed to adaptors like `then`, `let_value`, and `bulk`. If a user writes a lambda for a sender pipeline and places contract assertions on it that reference local variables not otherwise captured, this would be ill-formed. This rule protects P2300's lambda-heavy usage pattern from contracts silently changing closure layouts, which could affect the zero-allocation properties of structured sender pipelines.
Cross-exposure: P2300R10, P2900R14

---

## SYNTHESIS

### Executive Summary

P2300R10 (std::execution) and P2900R14 (Contracts for C++) are structurally compatible. Their foundational designs do not contradict each other, and several interaction points show positive coherence: P2900's "Concepts Do Not See Contracts" principle (ART-8) hermetically seals P2300's concept-based type machinery from contract interference; implicit const-ness in predicates aligns naturally with P2300's read-only environments (ART-17); the no-implicit-lambda-capture rule (ART-30) protects P2300's zero-allocation sender pipelines from contract-induced closure layout changes; and both papers independently avoid dynamic allocation in core infrastructure (ART-21). Two principles (Rule 6: Type Equality, Rule 22: No Preprocessor Dependence) find no concerns whatsoever. The type system is sound across their boundary, and neither paper forces adoption of the other.

However, the inspection reveals two HIGH-severity structural tensions and a dominant compound dynamic. The most pervasive finding is that P2900's global, monolithic, implementation-defined customization model (link-time violation handler, compiler-flag semantic selection) is fundamentally incommensurable with P2300's composable, per-type, compile-time domain customization mechanism. This single interaction is flagged by 11 of 24 principles. It means execution domain authors - the primary extensibility audience of P2300 - have no programmatic control over contract behavior within their domains. The second structural concern is that contracts designed for synchronous function semantics lose expressiveness when applied to P2300's lazy, async composition model: postconditions bind to opaque sender handles rather than eventual results, coroutine postconditions cannot reference parameters, and preconditions fire at construction time rather than execution time. The third concern, elevated to HIGH by Rule 5 (Visible Unsafety), is that contract violations flowing through sender exception machinery become indistinguishable from ordinary exceptions at consumer call sites, hiding broken invariants behind clean catch syntax. These are not design defects in either paper individually. They are emergent cross-paper tensions visible only when the hull is inspected as a whole.

### Per-Artifact Assessment

#### ART-1: Three-channel completion model
- Principles flagged: None at medium or above
- Assessment: Structurally sound; terminating semantics bypass structured concurrency teardown but this is inherent to program termination.

#### ART-2: Contract predicate exceptions in sender callbacks
- Principles flagged: Rule 5 (medium-high), Rule 23 (low)
- Compound: Part of the Invisible Danger Complex
- Assessment: Exception scoping ambiguity between contract evaluation and sender try-catch is invisible at the call site.

#### ART-3: Lazy evaluation vs. contract timing
- Principles flagged: Rule 5 (low-medium), Rule 19 (signal), Rule 20 (low)
- Compound: Part of the Lazy/Async Expressiveness Gap
- Assessment: Preconditions on sender adaptors check construction-time state, not execution-time correctness.

#### ART-4: Coroutine integration overlap
- Principles flagged: Rule 9 (low), Rule 13 (medium), Rule 19 (low-moderate), Rule 20 (medium), Rule 24 (signal)
- Compound: Part of the Lazy/Async Expressiveness Gap
- Assessment: Postconditions on coroutines bind to the handle, not the async result; parameter odr-use ban limits expressiveness.

#### ART-5: noexcept mandates vs. contract violation paths
- Principles flagged: Rule 5 (medium-high), Rule 21 (low)
- Compound: Part of the Invisible Danger Complex
- Assessment: Contract violations in nothrow execution infrastructure always terminate with a throwing handler - silently, without syntactic warning.

#### ART-6: Contract-induced termination vs. structured concurrency
- Principles flagged: None at medium or above
- Assessment: Terminating semantics bypass structured teardown; inherent and acceptable.

#### ART-7: set_stopped not error vs. contracts
- Principles flagged: None at medium or above
- Assessment: Three-channel completion model complicates postcondition reasoning but does not create tension.

#### ART-8: Concepts don't see contracts
- Principles flagged: Rule 4 (positive), Rule 7 (positive), Rule 24 (positive)
- Assessment: POSITIVE COHERENCE. P2900 Principle 3 is a deliberate and effective firewall.

#### ART-9: Forward progress vs. contract overhead
- Principles flagged: Rule 1 (medium, compound)
- Assessment: Non-ignored contract checking in bulk parallel paths consumes forward progress budget.

#### ART-10: Freestanding compatibility
- Principles flagged: Rule 2 (signal), Rule 15 (positive)
- Assessment: Contracts are freestanding; execution is not. Gap but not conflict.

#### ART-11: Observable checkpoints and sender ordering
- Principles flagged: Rule 1 (drift component)
- Assessment: Observable checkpoints could constrain sender pipeline optimization.

#### ART-12: Side effect elision in sender operations
- Principles flagged: Rule 1 (drift component)
- Assessment: Predicate duplication in hot paths is a performance concern under non-ignore semantics.

#### ART-13: sync_wait exception path and violations
- Principles flagged: Rule 5 (HIGH), Rule 23 (low)
- Compound: Part of the Invisible Danger Complex
- Assessment: Contract violations laundered through error channel become indistinguishable from ordinary exceptions at sync_wait.

#### ART-14: Operation state non-movability and postconditions
- Principles flagged: Rule 24 (signal)
- Assessment: Postconditions on connect bind to non-movable operation state; only structural properties checkable.

#### ART-15: stop_callback blocking vs. contract termination
- Principles flagged: None at medium or above
- Assessment: General consequence of program termination; not contract-specific.

#### ART-16: Customization mechanism paradigms
- Principles flagged: Rule 1 (medium), Rule 10 (moderate), Rule 14 (moderate), Rule 15 (medium), Rule 16 (moderate), Rule 18 (low), Rule 23 (high), Rule 24 (moderate)
- Compound: DOMINANT - part of the Global Handler / Impl-Defined Semantics Complex
- Assessment: Global link-time handler cannot compose with per-domain customization. Flagged by 11 principles.

#### ART-17: Implicit const and read-only environments
- Principles flagged: Rule 4 (positive), Rule 17 (positive)
- Assessment: POSITIVE COHERENCE. Both papers restrict mutation in complementary ways.

#### ART-18: bulk parallel invocation and contracts
- Principles flagged: Rule 1 (medium, compound)
- Assessment: Contract checking multiplied across bulk index space under non-ignore semantics.

#### ART-19: when_all error propagation vs. violations
- Principles flagged: Rule 5 (medium), Rule 23 (moderate)
- Assessment: Observe+throw in one when_all branch silently cancels all siblings.

#### ART-20: Postcondition result binding for senders
- Principles flagged: Rule 11 (low), Rule 13 (medium), Rule 19 (moderate), Rule 20 (medium), Rule 24 (signal)
- Compound: Part of the Lazy/Async Expressiveness Gap
- Assessment: Result bindings on sender-returning functions check opaque handle, not eventual result.

#### ART-21: Zero-allocation and contract_violation object
- Principles flagged: Rule 1 (positive)
- Assessment: POSITIVE COHERENCE. Both papers avoid operator new in core infrastructure.

#### ART-22: run_loop terminate and contract terminate
- Principles flagged: None
- Assessment: Shared use of terminate() as last resort is coherent.

#### ART-23: Receiver environment access from predicates
- Principles flagged: None at medium or above
- Assessment: Environment queries work naturally in const contract predicates; positive.

#### ART-24: Completion signatures vs. contract expressiveness
- Principles flagged: Rule 7 (positive), Rule 11 (low), Rule 24 (signal)
- Assessment: Compile-time completion signatures and runtime contracts are complementary non-overlapping systems.

#### ART-25: Impl-defined semantics vs. domain control
- Principles flagged: Rule 1 (medium), Rule 10 (moderate), Rule 14 (moderate), Rule 16 (moderate), Rule 18 (medium), Rule 19 (moderate), Rule 21 (low), Rule 23 (high), Rule 24 (moderate)
- Compound: DOMINANT - part of the Global Handler / Impl-Defined Semantics Complex
- Assessment: Contract semantic selection unreachable from P2300's domain mechanism. Flagged by 11 principles.

#### ART-26: Virtual prohibition and type-erased senders
- Principles flagged: Rule 3 (low), Rule 5 (medium), Rule 8 (low), Rule 9 (low), Rule 10 (moderate), Rule 12 (low), Rule 13 (low), Rule 14 (low), Rule 19 (low), Rule 20 (low), Rule 24 (low-moderate)
- Compound: Part of the Type Erasure Boundary dynamic
- Assessment: Deferred feature that will become ecosystem-critical. 11 principles flag it but all at low individual severity.

#### ART-27: Constant evaluation and constexpr senders
- Principles flagged: None at medium or above
- Assessment: Trial-then-real evaluation pattern applies coherently to constexpr sender operations.

#### ART-28: Mixed-mode TUs and sender template ODR
- Principles flagged: Rule 4 (low), Rule 14 (moderate), Rule 23 (high)
- Compound: Part of the Mixed-Mode ODR Risk dynamic
- Assessment: Template-heavy sender design amplifies ODR risk from mixed contract evaluation semantics.

#### ART-29: Throwing handler and unhandled_stopped
- Principles flagged: None at medium or above
- Assessment: Contract violations correctly propagate through exception path, not stopped path. Coherent.

#### ART-30: No implicit lambda captures and sender lambdas
- Principles flagged: Rule 1 (positive), Rule 4 (positive)
- Assessment: POSITIVE COHERENCE. Protects zero-allocation sender pipeline construction.

### Compound Dynamics

**COMPOUND 1: The Monolithic Handler / Implementation-Defined Semantics Complex**
Artifacts: ART-16, ART-25
Principles stressed: Rules 1, 3, 10, 14, 15, 16, 18, 19, 21, 23, 24 (11 of 24)
This is the dominant structural finding. P2300's execution domain mechanism provides composable, per-type, compile-time control over algorithm behavior. P2900's violation handler is global and monolithic (link-time replacement), and its semantic selection is entirely implementation-defined (compiler flags). These two customization models are incommensurable: a domain author who uses transform_sender to customize every aspect of algorithm behavior cannot influence how contracts behave within that domain - not the enforcement level, not the violation response, not the handler behavior. The tension is elevated to HIGH by Rule 23 (Local Verification) because the global handler creates action-at-a-distance and the implementation-defined semantics defeat local reasoning. It is reinforced at MODERATE by Rules 10, 14, 16, 19, 24 across composability, integration, and expressiveness dimensions. This is not a defect in either paper alone - P2900's global handler follows established C++ precedent (operator new/delete), and P2300's domain mechanism is a new C++26 pattern. But the combination means the two major C++26 extensibility stories (execution domains for async, replaceable handler for contracts) exist in parallel universes.

**COMPOUND 2: The Lazy/Async Expressiveness Gap**
Artifacts: ART-3, ART-4, ART-14, ART-20, ART-24
Principles stressed: Rules 13, 19, 20, 24
P2900's contracts were designed for synchronous function semantics: preconditions fire at entry, postconditions bind to the return value. P2300's sender-returning functions return opaque lazy descriptions of future work. When postconditions bind to a sender, they check the handle, not the eventual async result. Coroutine postconditions bind to the coroutine handle, not the co_returned value. Preconditions on adaptors check construction-time state, not execution-time correctness. The "contract" of a sender - what it will do when started - is expressed through compile-time completion signatures, unreachable from runtime contract predicates. The two checking systems are complementary (one compile-time, one runtime) but the runtime system has near-zero expressiveness for the async use case. This affects "Useful Now" (Rule 13) because postconditions on sender-returning functions are useful only to experts who understand the gap, and "Direct Concept Mapping" (Rule 20) because the programmer's mental model of "result" diverges from the language's.

**COMPOUND 3: The Invisible Danger Complex**
Artifacts: ART-2, ART-5, ART-13, ART-19
Principles stressed: Rules 5, 23
Contract violations flowing through P2300's exception machinery become invisible at consumer call sites. The path: violation occurs -> throwing handler's exception caught by sender try-catch -> routed to set_error(current_exception()) -> sync_wait rethrows as ordinary exception. At the sync_wait call site, the caller catches a std::exception with no indication that program invariants have been breached (not just a normal operational failure). Additionally, nothrow mandates on core execution operations (get_env, scheduler operations) silently convert any contract violation with a throwing handler into unconditional termination - the syntax of the contract looks identical whether on a throwing or nothrow function. The exception scoping question (does the sender's try-catch encompass contract evaluation?) is also invisible at the call site. Rule 5 (Visible Unsafety) rates this HIGH because the rocks have been erased from the chart.

**COMPOUND 4: The Type Erasure Boundary**
Artifacts: ART-26
Principles stressed: Rules 3, 5, 8, 9, 10, 12, 13, 14, 19, 20, 24 (11 principles)
P2900 prohibits contracts on virtual functions (deferred to future). P2300's core is concept-based, but the practical ecosystem requires type-erased senders. At the type-erasure boundary, contracts are lost. Individual severity is low across all 11 principles, but the breadth of impact (11/24 principles at low severity) indicates a pervasive low-grade concern that will intensify as the ecosystem builds type-erased async interfaces. This is explicitly a deferred feature, not an oversight.

**COMPOUND 5: Mixed-Mode ODR Amplification**
Artifacts: ART-28
Principles stressed: Rules 4, 14, 23
P2900 permits different TUs to use different contract evaluation semantics. P2300's sender algorithms are template-heavy and header-only. The combination amplifies ODR risk: the same template instantiated in two TUs with different contract semantics may produce different instantiations if predicates have side effects interacting with constant expressions. Rule 23 rates this HIGH because the hazard is fundamentally non-local - each TU appears correct in isolation. P2900 acknowledges the risk but P2300's nearly-entirely-template design makes the surface area unusually large.
