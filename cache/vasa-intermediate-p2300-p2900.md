# Vasa Intermediate - P2300R10 + P2900R14

## INPUT: p2300r10.md
Type: paper
Paper: P2300R10

### Extracted Content

**Core Design Choices and Rationale:**

1. **Three foundational abstractions** - schedulers, senders, receivers. Schedulers are lightweight handles to execution resources. Senders describe work (like deferred futures). Receivers are three-channel callbacks (value/error/stopped).

2. **Purely lazy execution model** - All sender factories and adaptors perform strictly lazy submission. No work is submitted until `connect` + `start`. Rationale: eager execution leads to detached work, complicates algorithms, incurs cancellation overhead, and prevents access to receiver context. The paper gives extensive justification for removing eager algorithms (R2 onwards).

3. **Completion schedulers** - Senders can advertise which scheduler their evaluation will complete on, via `get_completion_scheduler<Tag>` queries. This enables scheduler-specific algorithm customization (e.g., GPU kernels via `bulk`).

4. **Explicit execution resource transitions** - Running user code anywhere other than where defined must be considered a bug. Transitions require explicit `continues_on` / `starts_on` / `on`.

5. **Domain-based algorithm customization** - Sender algorithms create a default sender, query the child sender's domain, then dispatch to `transform_sender` for domain-specific transformation. This replaced earlier ADL-based approaches because the *scheduler* should control execution strategy, not the sender.

6. **Member function customization** (R9) - Replaced `tag_invoke` with named member functions (`connect`, `set_value`, `set_error`, `set_stopped`, `get_env`, `schedule`, `start`, `query`). Explicit concept opt-ins via `sender_concept = sender_t`, `receiver_concept = receiver_t`, `operation_state_concept = operation_state_t`.

7. **Cancellation via generalized stop tokens** - Extends C++20 `stop_token` with `stoppable_token` concept, adds `inplace_stop_source/token/callback` (efficient for structured concurrency), `never_stop_token` (statically elides cancellation overhead). Cancellation is optional on both sides.

8. **Dependently-typed senders** (R4) - Sender completion signatures can depend on the receiver's *environment* (not the receiver type directly, to avoid type cycles). Environments are bags of key/value pairs queried via CPOs.

9. **Removed ensure_started/start_detached** (R10) - Replaced by P3149's `async_scope` for safer, more structured APIs.

10. **Renamed transfer/on** (R10) - `transfer` -> `continues_on`, old `on` -> `starts_on`, new `on` = round-trip (`starts_on` + `continues_on` back).

11. **All senders are typed** - Must advertise completion signatures via `get_completion_signatures(sndr, env)`. No untyped senders.

12. **All awaitables are senders** - Transparent adaptation; coroutine types that don't know about senders still satisfy `sender`.

13. **Single-shot vs multi-shot** - rvalue-qualified `connect` for single-shot, lvalue-qualified for multi-shot. `split` converts single-shot to multi-shot.

14. **Pipeable syntax** - Most sender adaptors support `operator|` composition, analogous to C++ ranges. `starts_on` and `when_all` are explicitly NOT pipeable.

**API Surface - Key Types, Functions, Concepts:**

*Concepts:*
- `scheduler`, `sender`, `sender_in<Sndr, Env>`, `sender_to<Sndr, Rcvr>`, `receiver`, `receiver_of<Rcvr, Completions>`, `operation_state`, `stoppable_token`, `unstoppable_token`

*Core Operations:*
- `connect(sndr, rcvr)` -> `operation_state`
- `start(op_state)` - begins async operation
- `set_value(rcvr, vals...)`, `set_error(rcvr, err)`, `set_stopped(rcvr)` - completion functions
- `schedule(sch)` -> sender
- `get_env(obj)` -> environment/attributes

*Queries:*
- `get_scheduler`, `get_delegation_scheduler`, `get_stop_token`, `get_allocator`, `get_domain`, `get_completion_scheduler<Tag>`, `get_forward_progress_guarantee`, `forwarding_query`

*Sender Factories:*
- `schedule(sch)`, `just(vals...)`, `just_error(err)`, `just_stopped()`, `read_env(query)`

*Sender Adaptors:*
- `then`, `upon_error`, `upon_stopped`, `let_value`, `let_error`, `let_stopped`, `bulk`, `continues_on`, `starts_on`, `on` (two forms), `schedule_from`, `split`, `when_all`, `when_all_with_variant`, `into_variant`, `stopped_as_optional`, `stopped_as_error`

*Sender Consumers:*
- `this_thread::sync_wait(sndr)` -> `optional<tuple<Ts...>>`
- `this_thread::sync_wait_with_variant(sndr)` -> `optional<variant<tuple<Ts...>...>>`

*Key Types:*
- `completion_signatures<Fns...>`, `empty_env`, `run_loop`, `inplace_stop_source/token/callback`, `never_stop_token`, `forward_progress_guarantee` (enum), `default_domain`, `sender_adaptor_closure<D>`, `with_awaitable_senders<Promise>`

*Sender Transformation Machinery:*
- `transform_sender(domain, sndr, env...)`, `transform_env(domain, sndr, env)`, `apply_sender(domain, tag, sndr, args...)`

*Exposition-only but architecturally critical:*
- `basic-sender`, `basic-operation`, `basic-state`, `basic-receiver`, `impls-for<Tag>`, `default-impls`, `make-sender`, `product-type`, `FWD-ENV`, `MAKE-ENV`, `JOIN-ENV`, `SCHED-ATTRS`, `SCHED-ENV`, `write-env`

**Behavioral Guarantees:**

1. Exactly-once completion: a started operation completes exactly once with value, error, or stopped
2. Lazy submission: no work before connect + start
3. Completion scheduler fidelity: if advertised, the completion MUST happen on that scheduler's execution resource
4. Operation state lifetime: destroying during async lifetime is UB
5. Operation states are non-movable, non-copyable
6. Scheduler equality implies same execution resource
7. Forward progress guarantees honored per `get_forward_progress_guarantee`
8. Thread safety: scheduler copy/destroy/compare/swap/schedule don't introduce data races
9. `when_all` cancels siblings on first error/stop
10. `sync_wait` blocks current thread with forward progress delegation via internal `run_loop`
11. Stop tokens valid for duration of async operation
12. Cancellation is inherently racy - implementations must handle races between completion and stop requests
13. `run_loop` destructor terminates if still running or has pending work
14. Receiver types must not be `final` (to enable inheritance-based adaptors)

**Claimed Principles:**

1. Composable and generic across execution resources
2. Correct by construction
3. Support diversity of execution resources (GPUs, embedded, accelerators, thread pools)
4. Everything customizable but nothing required
5. Clear answers for where things execute
6. Errors propagated but not burdensome (three-channel model)
7. Cancellation is not an error (separate stopped channel)
8. Structured concurrency (no detached work, deterministic lifetime)
9. Zero-allocation possible (intrusive operation state storage, run_loop)
10. Laziness enables compiler optimization (sees full task graph, inlining, tail calls)
11. Scheduler controls execution strategy, not the sender

**Dependencies on Other Papers/Features:**

- C++20 coroutines (`co_await`, promise types, `coroutine_handle`)
- C++20 `stop_token`/`stop_source`/`stop_callback` (extended)
- C++20 concepts, ranges-style piping
- P3149R3 (`async_scope`) - replacement for removed `ensure_started`/`start_detached`
- P3175R3 - redesigned `on` algorithm
- P3303R1 - fixed lazy sender algorithm customization via `transform_sender`
- P2999R3 - sender algorithm customization framework
- P2855R1 - member customization points (replacing `tag_invoke`)
- P2175R0 - cancellation design (stop token generalization)

**Assumptions about Interactions:**

1. Future papers will propose `time_scheduler`, file I/O scheduler, networking scheduler concepts extending `scheduler`
2. Future papers will propose `executing_on(scheduler, policy)` for parallel algorithm integration
3. Future papers will propose asynchronous parallel algorithms returning senders
4. A standard `task<T>` coroutine type (P1056) should implement `unhandled_stopped`
5. Runtimes with non-thread execution agents will provide their own `sync_wait` variants (e.g., `this_fiber::sync_wait`)
6. Type erasure facilities can be built on top (explicitly omitted)
7. Thread pool implementation is explicitly omitted per LEWG direction
8. `async_scope` (P3149) is the intended replacement for detached/eager work patterns
9. Sender adaptors that are "not pipeable" (`starts_on`, `when_all`) are so by deliberate design choice to avoid semantic confusion
10. The `query` member function mechanism for queryable objects allows forwarding an open/unknowable set of queries through adaptors

### References Found
- P0443R14 (predecessor executors proposal)
- P0981R0 (HALO coroutine optimization)
- P1056R1 (lazy coroutine task type)
- P1895R0 (tag_invoke, now replaced)
- P1897R3 (initial set of algorithms)
- P2175R0 (composable cancellation)
- P2762 (networking APIs using sender/receiver)
- P2855R1 (member customization points)
- P2999R3 (sender algorithm customization)
- P3149R3 (async_scope)
- P3175R3 (reconsidering on algorithm)
- P3187R1 (remove ensure_started/start_detached)
- P3303R1 (fixing lazy sender algorithm customization)
- N4885 (working draft base)
- No mention of P2900 (contracts)

### Deviations
- None significant. File read in segments due to size. All content covered.

---

## INPUT: p2900r14.md
Type: paper
Paper: P2900R14

### Extracted Content

**Identity:** P2900R14, "Contracts for C++", Revision 14, 2025-02-13, Audience: CWG/LWG. This is the MVP Contracts proposal for C++26, representing SG21 consensus per the plan in P2695R0.

**Core Design Choices and Rationale:**

1. **Three syntactic constructs:** `pre` (precondition specifier), `post` (postcondition specifier), `contract_assert` (assertion statement). `pre`/`post` are contextual keywords; `contract_assert` is a full keyword (needed for disambiguation from function call).

2. **Four evaluation semantics:** ignore, observe, enforce, quick-enforce. Observe/enforce/quick-enforce are "checking semantics." Enforce/quick-enforce are "terminating semantics."

3. **Semantic selection is implementation-defined.** Different assertions can have different semantics, even in the same function. Same assertion can have different semantics for different evaluations. No compile-time detection of which semantic is active (by design - Principle 5).

4. **Contract termination** is implementation-defined: one of std::terminate, std::abort, or immediate execution termination. May differ per assertion evaluation.

5. **Result binding** in postconditions: `post(r: r > 0)` - names the result object. Type is `const T`. Declared like a structured binding. Can only appear if return type is non-void.

6. **Implicit const** within predicates: All id-expressions referring to variables declared outside the contract predicate are const lvalues (shallow). Prevents accidental mutation. Modifiable via const_cast (discouraged).

7. **Virtual functions:** ill-formed to have pre/post (R14 reinstated this restriction).

8. **Deleted/defaulted functions:** ill-formed to have function contract specifiers.

9. **Coroutines supported:** Preconditions evaluated before ramp function operations. Postconditions evaluated on ramp function return (not suspension points). Odr-using a non-reference parameter in postcondition of a coroutine is ill-formed (parameter may be moved-from).

10. **Parameters in postconditions:** Non-reference parameters odr-used in post must be const on all declarations.

11. **Side effects may be elided or duplicated.** If compiler can prove predicate produces true/false without evaluation, it may skip all side effects. Contract assertions may be repeated (implementation-defined number of times) within a sequence of consecutive assertions.

12. **Observable checkpoints** (builds on P1494R5): Beginning of predicate evaluation and handler returning from observe semantic are observable checkpoints. Prevents time-travel optimizations from eliding checks due to later UB.

13. **No implicit lambda capture from contracts.** If all references to a local entity occur only within contract assertions, capture is ill-formed. Ensures zero overhead when contracts are ignored.

14. **Mixed mode (different TUs, different semantics):** Well-formed. Inline function may have different semantics when compiled in different TUs. No ODR violation from semantic differences alone.

15. **Constant evaluation:** Trial evaluation with all contracts ignored determines whether a variable is constant-initialized. If yes, full evaluation applies contracts with implementation-defined semantic. Contract violations at compile time: observe = warning, enforce/quick-enforce = ill-formed.

16. **Replaceable violation handler:** `::handle_contract_violation(const std::contracts::contract_violation&)`. Implementation-defined whether replaceable. Same mechanism as operator new replacement. No declaration provided by any header.

17. **No ABI break:** Adding contracts to existing function must be ABI-compatible.

18. **Exception in predicate = contract violation** with detection_mode::evaluation_exception. Exception available in handler.

19. **Handler throw = as if from function body.** If function is noexcept, std::terminate is called.

20. **Quick-enforce:** Skips handler entirely, immediately terminates. Minimizes code size impact.

21. **Not a drop-in replacement for assert macro.** Key differences: contract_assert is a statement (not expression), implicit const changes overload resolution, ignored contracts still parse (unlike NDEBUG-disabled assert).

22. **Pointers to function:** Contracts still evaluated when called through pointer. Cannot be checked at call site for indirect calls - must be checked inside function or via thunk.

23. **No function contract specifiers on type aliases or function types.**

24. **Redeclaration rules:** Function-contract-specifier-seq must appear on every first declaration. May be omitted on redeclarations. Must be equivalent when repeated. Contains lambda = ill-formed to redeclare in same TU.

25. **`<contracts>` is freestanding.**

**API Surface:**

- **Header:** `<contracts>`
- **Namespace:** `std::contracts`
- **Class `contract_violation`** (created only by implementation, not user-constructable):
  - `comment() -> const char*` (textual representation of predicate)
  - `detection_mode() -> contracts::detection_mode`
  - `evaluation_exception() -> exception_ptr`
  - `is_terminating() -> bool`
  - `kind() -> assertion_kind`
  - `location() -> source_location`
  - `semantic() -> evaluation_semantic`
- **Enum `evaluation_semantic`:** ignore, observe, enforce, quick_enforce
- **Enum `detection_mode`:** predicate_false, evaluation_exception
- **Enum `assertion_kind`:** pre, post, contract_assert
- **Function:** `invoke_default_contract_violation_handler(const contract_violation&)`
- **Violation handler:** `void ::handle_contract_violation(const std::contracts::contract_violation&)` (replaceable, global module, C++ linkage)
- **Feature test macros:** `__cpp_contracts`, `__cpp_lib_contracts`

**Behavioral Guarantees:**

- Ignored contracts have zero runtime effect (predicate not evaluated, still odr-uses entities)
- Observe: handler called, execution continues normally if handler returns
- Enforce: handler called, program contract-terminated if handler returns
- Quick-enforce: no handler, immediate contract termination
- Preconditions evaluated after parameter initialization, before function body
- Postconditions evaluated after return value initialization, after local variable destruction, before parameter destruction
- Contract-violation object lifetime persists through handler invocation
- Side effects of predicate: may occur 0, 1, or many times (no reliance permitted)
- Adding contracts to a function does not break existing correct client code

**Claimed Principles (16 Principles):**

1. **Prime Directive:** Presence/evaluation of contract assertions shall not alter program correctness
2. **Redundancy Principle:** In correct programs, contracts are redundant; removing any subset doesn't alter correctness
3. **Concepts Do Not See Contracts:** Presence doesn't change concept satisfiability, SFINAE, if constexpr, noexcept operator
4. **Zero Overhead:** Ignored contracts have no observable behavioral impact
5. **Independence from Chosen Semantic:** Which semantic is active should not be detectable at compile time
6. **No Destructive Side Effects:** Predicates that change correctness are not supported
7. **Completeness of Contract Assertions:** Each assertion encapsulates a complete check
8. **Independence of Contract Assertions:** One assertion's result never affects another's
9. **Independence of Contract-Assertion Evaluations:** One evaluation's result never affects subsequent evaluations of same assertion
10. **Contract Assertions Check a Plain-Language Contract:** Must verify the contract of the function they're attached to
11. **Function Contract Assertions Serve Both Caller and Callee:** Part of both interface and implementation
12. **Contract Assertions Are Not Flow Control:** No guaranteed runtime behavior
13. **Explicitly Define All New Behavior:** Never explicitly introduce new UB
14. **Choose Ill-Formed to Enable Flexible Evolution:** Leave unsolved problems ill-formed, not UB
15. **No Client-Side Language Break:** Adding contracts to existing function doesn't break callers
16. **No ABI Break:** Implementation should guarantee ABI backward-compatibility

**Dependencies on Other Papers/Features:**

- **P1494R5** (Partial program correctness) - provides observable checkpoint mechanism; P2900 builds on it
- **N4993** (C++26 working draft) - base document for wording
- **P2695R0** (Plan for contracts in C++) - the roadmap this MVP fulfills
- **P2053R1** (Defensive Checks Versus Input Validation) - cited for error-handling/contracts distinction
- **P2899R1** (Contracts for C++ - Rationale) - companion rationale paper
- **CWG2841** (When do const objects start being const?) - related to result binding semantics
- **C++ Coroutines** - specific interaction rules defined
- **std::execution** - mentioned in std::terminate conditions list ([exec.run.loop], [exec.with.awaitable.senders])

**Assumptions About Interaction With Other Features:**

- Standard Library implementations may use contracts on their functions but are not mandated to
- Compiler + library cooperation required for meaningful contract checks on stdlib functions that currently have UB-on-violation
- Template instantiation: contracts are instantiated when function is odr-used or defined, NOT during overload resolution/SFINAE
- Works with structured bindings, explicit object parameters (deducing this), pointers to member functions
- Future proposals may add: assertion levels, invariants, procedural interfaces, exception postconditions, unevaluable predicates, per-assertion semantic control

**Explicit "Not In Scope" Items:**

- Per-assertion semantic specification
- Assertion levels
- Postconditions for exception exits
- Unevaluable predicates
- Stateful contracts
- Class invariants
- Procedural interfaces

### References Found
- P1494R5 (observable checkpoints - direct dependency)
- P2695R0 (plan for contracts)
- P2053R1 (defensive checks vs input validation)
- P2899R1 (rationale companion)
- CWG2841 (const object lifetime)
- N4993 (C++26 working draft)
- std::execution references: [exec.run.loop], [exec.with.awaitable.senders] in terminate conditions (interaction with P2300)

### Deviations
- None.

---

## ARTIFACTS

### A-1: Exactly-once completion vs contract termination
Inputs: [P2300 behavioral guarantee #1 (exactly-once completion); P2900 design choice #4 (contract termination is implementation-defined: terminate/abort/immediate)]
Type: behavioral-guarantee
Summary: P2300 guarantees that a started operation completes exactly once via one of three channels (value/error/stopped). P2900's contract termination (triggered by enforce/quick-enforce violation) is implementation-defined and bypasses all three channels - the operation never "completes" in P2300's sense. If a contract violation fires inside a sender adaptor's implementation mid-operation, the exactly-once guarantee is vacuously satisfied (program ceases to exist), but structured concurrency invariants (parent notification, sibling cancellation) are bypassed. This creates a semantic gap: P2300 code cannot defensively handle contract termination because it occurs outside the error model.
Cross-exposure: [P2300, P2900]

### A-2: Three-channel error model vs violation handler throw
Inputs: [P2300 design choice #1 (three channels: value/error/stopped); P2900 design choice #19 (handler throw = as if from function body)]
Type: behavioral-guarantee
Summary: When a contract violation handler throws (under observe/enforce semantics), the exception propagates as if thrown from the function body. In P2300's model, exceptions thrown during sender execution should be caught and delivered via `set_error`. But if the violation occurs in a receiver's completion function (which is typically noexcept), the throw triggers std::terminate. If it occurs in a sender's operation, the exception could be caught and channeled through set_error - but only if the implementation wraps contract-violation exceptions the same way it wraps other exceptions. There is no specification of how violation-handler exceptions interact with the sender/receiver error channel.
Cross-exposure: [P2300, P2900]

### A-3: Receiver noexcept requirements vs exception-from-predicate
Inputs: [P2300 behavioral guarantee #14 (receiver types inherit-based adaptors) + API (set_value/set_error/set_stopped on receivers); P2900 design choice #18 (exception in predicate = contract violation with evaluation_exception) + #19 (handler throw in noexcept = terminate)]
Type: behavioral-guarantee
Summary: P2300's receiver completion functions (`set_value`, `set_error`, `set_stopped`) are commonly noexcept (required by many adaptors). If a contract precondition on a receiver's `set_value` throws during predicate evaluation, P2900 treats this as a contract violation with detection_mode::evaluation_exception. If the violation handler then throws (or if the predicate throw itself propagates), and the function is noexcept, std::terminate is called. This makes contracts on receiver completion functions particularly dangerous - any predicate that could throw (e.g., dereferencing a pointer, calling a user-defined comparison) becomes a latent terminate path that bypasses P2300's error channel entirely.
Cross-exposure: [P2300, P2900]

### A-4: Concepts do not see contracts vs P2300 concept taxonomy
Inputs: [P2900 Principle 3 (concepts do not see contracts - no SFINAE, no noexcept operator, no if constexpr interaction); P2300 concepts (scheduler, sender, receiver, operation_state, stoppable_token)]
Type: design-choice
Summary: P2300 defines a rich concept hierarchy that gates template instantiation and algorithm selection. P2900's Principle 3 guarantees that adding contracts to member functions (connect, start, set_value, schedule, etc.) cannot change whether a type satisfies these concepts. This is coherent but has a consequence: contracts cannot serve as a mechanism to statically reject types that fail to meet semantic requirements beyond syntactic ones. A type that models `sender` syntactically but violates a semantic invariant (e.g., does not actually complete exactly once) will still satisfy the concept regardless of contracts. The contracts become purely runtime checks, never compile-time gates.
Cross-exposure: [P2300, P2900]

### A-5: Virtual function contract prohibition vs type-erased senders
Inputs: [P2900 design choice #7 (ill-formed to have pre/post on virtual functions); P2300 assumption #6 (type erasure facilities can be built on top)]
Type: design-choice
Summary: P2300 explicitly omits type erasure but acknowledges it will be built on top (e.g., `any_sender<Sigs...>`). Type-erased sender/receiver implementations typically use virtual dispatch internally. P2900 makes it ill-formed to place pre/post on virtual functions. This means the virtual interface layer of type-erased execution primitives cannot carry contracts. Contracts can only exist on the concrete implementations or the non-virtual public wrappers, creating a gap in the contract checking chain at the type-erasure boundary. Any semantic guarantee that should hold across type erasure (e.g., "this sender completes exactly once") cannot be expressed as a contract on the virtual dispatch.
Cross-exposure: [P2300, P2900]

### A-6: Operation state lifetime UB vs contract expressibility
Inputs: [P2300 behavioral guarantee #4 (destroying operation_state during async = UB) + #5 (non-movable, non-copyable); P2900's precondition mechanism; P2900 design choice #6 (implicit const in predicates)]
Type: behavioral-guarantee
Summary: P2300's most critical lifetime invariant - "do not destroy operation_state while the async operation is in flight" - is expressed as UB. This is exactly the kind of semantic requirement that contracts should express (`pre(/* not in flight */)`). However, the "in flight" state is internal to the operation (set by `start`, cleared by completion signal delivery). A precondition on the destructor would need to observe mutable internal state, but P2900's implicit const in predicates prevents reading mutable members. Furthermore, operation_state's deleted copy/move constructors cannot carry contracts (P2900 design choice #8). This invariant remains unexpressible via contracts.
Cross-exposure: [P2300, P2900]

### A-7: Coroutine integration overlap
Inputs: [P2300 API (with_awaitable_senders<Promise>, all awaitables are senders); P2900 design choice #9 (coroutine rules: preconditions before ramp, postconditions on ramp return, odr-using non-ref param in post of coroutine = ill-formed)]
Type: behavioral-guarantee
Summary: P2300 deeply integrates with coroutines via `with_awaitable_senders<Promise>`, making all awaitables into senders and providing `unhandled_stopped` handling. P2900 specifies that coroutine preconditions evaluate before ramp function operations and postconditions evaluate on ramp function return (not at suspension points). When a P2300-integrated coroutine (`task<T>` using with_awaitable_senders) has contracts: the precondition fires before the coroutine frame is allocated and the promise constructed, and the postcondition fires when the coroutine handle returns to the caller (not when the async value is eventually delivered). This means postconditions on async coroutines check the sender-return, not the eventual completion value - the postcondition cannot verify the async result.
Cross-exposure: [P2300, P2900]

### A-8: Dual std::terminate convergence
Inputs: [P2300 behavioral guarantee #13 (run_loop destructor terminates if running/pending); P2300 reference in P2900 ([exec.run.loop], [exec.with.awaitable.senders] in terminate conditions); P2900 design choice #4 (contract termination may be std::terminate)]
Type: behavioral-guarantee
Summary: Both papers independently produce std::terminate calls. P2300 uses it in run_loop's destructor (if the loop is still running or has pending work) and in with_awaitable_senders (if unhandled_stopped cannot handle the stopped signal). P2900 explicitly cross-references these sections ([exec.run.loop], [exec.with.awaitable.senders]) in its list of existing terminate conditions. Contract termination (one implementation-defined option) adds a third terminate trigger. In a running system, distinguishing between "terminate because operation_state lifetime was violated," "terminate because run_loop was destroyed too early," and "terminate because a contract was violated" requires post-mortem analysis. The terminate paths compose but do not compose diagnostically.
Cross-exposure: [P2300, P2900]

### A-9: Zero-overhead claims under composition
Inputs: [P2300 claimed principle #9 (zero-allocation possible) + #10 (laziness enables compiler optimization); P2900 Principle 4 (zero overhead - ignored contracts have no observable behavioral impact) + design choice #13 (no implicit lambda capture from contracts)]
Type: direction-signal
Summary: Both papers make zero-overhead claims. P2300 achieves it via intrusive operation_state storage, lazy evaluation enabling inlining/tail-calls, and compile-time sender type composition. P2900 achieves it by ensuring ignored contracts have literally no runtime effect and no capture overhead. When composed: adding contracts to P2300's hot-path functions (connect, start, set_value) with "ignore" semantics preserves zero overhead per P2900's guarantee. However, under "enforce" or "observe" semantics, contract checking on every completion signal delivery (set_value is called once per operation but may be in a tight loop via bulk) introduces overhead that P2300's design specifically optimized away. The tension is not in the papers' claims but in deployment: you cannot simultaneously have checked contracts AND zero-overhead execution.
Cross-exposure: [P2300, P2900]

### A-10: Contract termination vs structured concurrency cleanup
Inputs: [P2300 claimed principle #8 (structured concurrency - no detached work, deterministic lifetime) + behavioral guarantee #9 (when_all cancels siblings on first error/stop); P2900 design choice #4 (contract termination = terminate/abort/immediate)]
Type: behavioral-guarantee
Summary: P2300's structured concurrency model guarantees that when a child operation fails, siblings are cancelled via stop tokens and the parent receives a deterministic completion. This relies on the error/stopped channels functioning. Contract termination (terminate/abort) happens below the sender/receiver protocol - it does not deliver a stopped signal, does not trigger sibling cancellation through stop tokens, and does not allow parent operations to clean up. In the interval between contract termination being triggered and the process actually dying, other threads running sibling operations may observe inconsistent state. This is "fine" in the sense that terminate kills everything, but it means contracts cannot be used as a graceful degradation mechanism within structured concurrency.
Cross-exposure: [P2300, P2900]

### A-11: Side effect elision vs lazy sender observation
Inputs: [P2900 design choice #11 (side effects in predicates may be elided or duplicated); P2300 design choice #2 (purely lazy execution - no work before connect+start)]
Type: behavioral-guarantee
Summary: P2900 allows compilers to elide or duplicate all side effects of contract predicates if the result can be proven statically. P2300's lazy model means that observable state transitions (work submission, execution resource acquisition) happen only at connect+start. If a contract predicate on a sender factory or adaptor probes whether work has been submitted (e.g., checking a flag that connect sets), the compiler may elide or duplicate that check, making it unreliable as a diagnostic tool. More importantly: because contracts cannot have relied-upon side effects, they cannot be used to implement or enforce P2300's laziness guarantee - they can only observe it (unreliably).
Cross-exposure: [P2300, P2900]

### A-12: Freestanding contracts header vs embedded execution resources
Inputs: [P2900 design choice #25 (`<contracts>` is freestanding); P2300 claimed principle #3 (support diversity of execution resources - GPUs, embedded, accelerators)]
Type: direction-signal
Summary: P2900's `<contracts>` header is freestanding, meaning it is available on freestanding implementations targeting embedded systems, accelerators, and minimal environments. P2300 explicitly targets these same environments (GPUs, embedded, accelerators). This creates positive alignment: contracts can be used to annotate sender/receiver implementations on constrained platforms without requiring a hosted implementation. However, the violation handler mechanism (replaceable global function) may not be suitable for GPU execution contexts where global state and function pointers behave differently. Quick-enforce (immediate termination, no handler) is the only viable semantic on many accelerators.
Cross-exposure: [P2300, P2900]

### A-13: Cancellation races vs observable checkpoints
Inputs: [P2300 behavioral guarantee #12 (cancellation is inherently racy - must handle races between completion and stop); P2900 design choice #12 (observable checkpoints prevent time-travel optimizations)]
Type: behavioral-guarantee
Summary: P2300 explicitly acknowledges that cancellation is racy: a completion signal and a stop request may race, and implementations must handle both orderings correctly. P2900's observable checkpoints (beginning of predicate evaluation) prevent compilers from reordering or eliminating code based on UB that occurs later. When a contract check is placed at a cancellation race point (e.g., a precondition on set_stopped that checks a "not already completed" flag), the observable checkpoint may constrain compiler optimizations that P2300 implementations rely on for efficient cancellation handling. The checkpoint prevents the compiler from proving the precondition true by assuming no data race (even if the operation's internal protocol guarantees ordering).
Cross-exposure: [P2300, P2900]

### A-14: Parameter move semantics vs postcondition const constraint
Inputs: [P2900 design choice #10 (non-reference parameters odr-used in post must be const on all declarations); P2300 API (set_value(rcvr, vals...) - values moved through channels)]
Type: api-shape
Summary: P2300's completion functions move values through channels: `set_value(rcvr, vals...)` typically moves its value arguments into the receiver. P2900 requires that non-reference parameters odr-used in postconditions must be declared const on all declarations. If a sender adaptor's completion function has a postcondition that references the delivered values (to verify what was delivered), those parameters must be const - which prevents moving them into the next stage. This creates a tension: either the postcondition cannot reference the delivered values (limiting what can be checked), or the values cannot be moved (violating P2300's efficiency model). The workaround is to only check via const-ref parameters, but P2300's value channel often passes by value for move optimization.
Cross-exposure: [P2300, P2900]

---

## PRINCIPLE 1: Zero Overhead

### Findings
- TENSION [high]: A-9 + A-13 jointly violate this principle.
  Enforce/observe semantics on P2300 hot-path customization points (set_value, start, scheduler operations) reintroduce runtime checks at precisely the points P2300 eliminated them. Observable checkpoints from contract evaluation act as optimization barriers, preventing reordering/eliding cancellation-related code. Together, one room's contract decisions impose both direct check overhead and indirect optimization-barrier overhead on sender chains - even when downstream code neither authored nor requested those contracts. The overhead is not opt-in at the composition boundary; it is inherited transitively through the sender algebra.

- TENSION [medium]: A-14 + A-9 jointly violate this principle.
  Postconditions require parameters to be const-observable, preventing move from completion arguments. If a library author adds postconditions to a sender adaptor's completion operation, downstream receivers pay copy overhead on completion values. Code that does not use contracts but composes with contracted adaptors inherits the cost.

- DRIFT [medium]: A-2, A-9, A-13 collectively move away from this principle.
  Contract mechanism, when applied anywhere in a sender/receiver chain, imposes costs on the entire composed expression. Violation handler throws introduce exception paths into noexcept-optimized chains. Contract evaluation points fragment whole-program reasoning about sender expressions by introducing opaque observation points the optimizer cannot see through.

- DRIFT [low]: A-10, A-1 impose cognitive overhead on structured concurrency code.
  Code relying on P2300's three-channel guarantee for resource safety must account for contract-triggered termination that bypasses the stopped channel.

- SIGNAL [positive]: A-4 + A-12 reinforce this principle.
  Contracts invisible to concepts means compile-time type checking pays zero cost; both papers targeting freestanding confirms shared intent toward minimal-overhead environments.

### Not implicated: A-3, A-5, A-6, A-7, A-8, A-11

---

## PRINCIPLE 2: Affordable Hardware

### Findings
- SIGNAL [low]: A-12 - Freestanding contracts align with embedded. Violation handler may narrow on GPU targets to quick-enforce only.
- SIGNAL [low]: A-9 - Enforcement cost accumulates proportionally more on lower-end hardware.

### Not implicated: A-1, A-2, A-3, A-4, A-5, A-6, A-7, A-8, A-10, A-11, A-13, A-14

---

## PRINCIPLE 3: Leave No Room Below

### Findings
- TENSION [high]: A-9 - Contract enforcement in P2300 hot paths adds overhead a lower-level language avoids.
- TENSION [medium]: A-14 - Postcondition const blocks zero-cost moves that C achieves trivially.
- TENSION [medium]: A-12 - Handler model may not reach GPU/embedded targets where P2300 operates.
- SIGNAL [medium]: A-13 - Checkpoints limit fusion optimizations.
- SIGNAL [low]: A-5 - Type erasure gap prevents contracts reaching virtual dispatch layer.

### Not implicated: A-1, A-2, A-3, A-4, A-6, A-7, A-8, A-10, A-11

---

## PRINCIPLE 4: Static Type Safety

### Findings
- TENSION [high]: A-5 - Type-erased sender boundary loses static type safety guarantees that contracts on concrete types provide. The virtual dispatch layer is a type-safety hole.
- TENSION [medium]: A-4 - Concepts and contracts operate on disjoint planes. Semantic type violations pass through concepts unchecked; contracts cannot close the gap statically.
- TENSION [medium]: A-6 - Lifetime invariant (operation_state in-flight) is a type-safety property that escapes all enforcement.
- SIGNAL [positive]: A-9 - Composition preserves types.
- SIGNAL [positive]: A-14 - Const enforcement is shallow but correct.

### Not implicated: A-1, A-2, A-3, A-7, A-8, A-10, A-11, A-12, A-13

---

## PRINCIPLE 5: Visible Unsafety

### Findings
- TENSION [high]: A-1 - Contract termination is invisible to P2300 code. No syntax at the composition site reveals that a child operation's contract violation will kill the process.
- TENSION [high]: A-3 - Contracts on noexcept receivers create latent terminate paths. The `pre` keyword looks innocuous but conceals process death when predicate throws.
- TENSION [high]: A-10 - Structured concurrency cleanup bypassed by contract termination. Parent operations cannot see or defend against this.
- TENSION [medium]: A-2 - Violation handler throw behavior unspecified in sender context. Clean-looking contracted function may throw into noexcept boundary.
- TENSION [medium]: A-5 - Type-erasure boundary silently drops contract coverage. Users crossing the boundary cannot see contracts disappeared.
- TENSION [medium]: A-7 - Postconditions on coroutines appear to check the result but actually check the ramp return. Syntactically misleading.
- DRIFT [medium]: A-4, A-6, A-9, A-11 - Pattern of invisible degradation: contracts invisible to concepts, lifetime UB invisible to contracts, overhead invisible at composition sites, elision invisible to diagnostic assertions.
- SIGNAL [positive]: A-8 - Multiple terminate paths are at least uniformly lethal (visible in the sense that death is death).

### Not implicated: A-12, A-13, A-14

---

## PRINCIPLE 6: Type Equality

### Findings
- TENSION [high]: A-14 - Postcondition const is costless for fundamental types but imposes copy-vs-move penalty on class types. Same annotation has different cost profiles for int vs vector<T>.
- TENSION [medium]: A-6 - Contract expressibility degrades for complex class types with deleted members and mutable lifetime state. Fundamental types get full support; RAII handles get none.
- SIGNAL [low]: A-5 - Virtual prohibition asymmetrically affects polymorphic user-defined types.
- SIGNAL [low]: A-4 - Concept-contract invisibility constrains user-defined type expressibility only.

### Not implicated: A-1, A-2, A-3, A-7, A-8, A-9, A-10, A-11, A-12, A-13

---

## PRINCIPLE 7: Compile-Time Checking

### Findings
- TENSION [high]: A-4 + A-6 - P2900's "concepts don't see contracts" combined with P2300's semantic-beyond-syntactic requirements means the most dangerous invariant violations (operation_state lifetime, exactly-once completion) escape ALL checking - neither compile-time concepts nor compile-time contract evaluation can catch them.
- TENSION [high]: A-5 - Virtual prohibition strips contracts at type-erasure boundaries, losing compile-time checkability at precisely the composition point where errors compound.
- TENSION [high]: A-7 - Coroutine postcondition fires at compile-time-determinable ramp return but cannot check the runtime async result. The compile-time mechanism reaches the wrong semantic moment.
- DRIFT [medium]: A-11 - Laziness guarantee cannot be checked at compile time or runtime via contracts.
- SIGNAL [positive]: A-4 - Contracts not affecting concept satisfaction preserves existing compile-time checks.
- SIGNAL [positive]: A-12 - Freestanding availability means constexpr contract checking available everywhere.

### Not implicated: A-1, A-2, A-3, A-8, A-9, A-10, A-13, A-14

---

## PRINCIPLE 8: No Single Style

### Findings
- TENSION [high]: A-5 - Virtual prohibition forces concepts/type-erasure as sole polymorphism path for contracted execution code. OOP style (virtual dispatch) cannot carry contracts, mandating a monostyle constraint.
- TENSION [medium]: A-3 - Noexcept receivers mandate value-channel-only error handling when contracts are present. Exception-based error styles become lethal.
- DRIFT [low]: A-12 - Freestanding narrows to enforce-only style on accelerators.
- SIGNAL [positive]: A-9 - Zero-overhead/ignore preserves style freedom.
- SIGNAL [positive]: A-7 - Coroutine constraints are narrow, not monostyle.

### Not implicated: A-1, A-2, A-4, A-6, A-8, A-10, A-11, A-13, A-14

---

## PRINCIPLE 9: Features Over Prevention

### Findings
- DRIFT [high]: A-5 - Virtual function contract prohibition removes capability entirely. The feature is technically feasible but blocked because inheritance semantics are complex. ALL uses prevented because SOME patterns are tricky.
- DRIFT [medium]: A-14 - Postcondition const blocks useful move-only validation patterns. Prevention of mutation blocks legitimate non-destructive observation.
- TENSION [medium]: A-7 - Coroutine parameter postcondition restriction broader than the underlying hazard. Blanket prohibition where narrower restriction would serve.
- TENSION [medium]: A-6 - Implicit const prevents observing legitimate mutable state in operation state postconditions. Conflates "must not mutate" with "must not observe mutation."

### Not implicated: A-1, A-2, A-3, A-4, A-8, A-9, A-10, A-11, A-12, A-13

---

## PRINCIPLE 10: Hybrid Styles

### Findings
- TENSION [high]: A-5 - Virtual prohibition severs OOP type-erasure from contract-annotated generic code. any_sender loses all contract coverage.
- TENSION [high]: A-10 - Structured concurrency's cooperative error propagation is paradigm-locked against contract-termination's process-kill response. Two paradigms cannot compose.
- TENSION [medium]: A-7 - Coroutine+sender+contracts triple interaction: three paradigms that each work alone but degrade when combined.
- DRIFT [medium]: A-3 - Exception-based patterns cannot combine with contract-checking on noexcept receivers.
- DRIFT [low]: A-9 - Lazy composition style + contract checking style force overhead trade-off.
- SIGNAL [positive]: A-4 - Concepts and contracts orthogonal by design.
- SIGNAL [positive]: A-12 - Multiple deployment styles supported.
- SIGNAL [positive]: A-1 - Three-channel model and contract model serve different concerns.

### Not implicated: A-2, A-4, A-6, A-8, A-11, A-13, A-14

---

## PRINCIPLE 11: Real Problems

### Findings
- SIGNAL [positive]: All 14 artifacts arise from genuine mechanical conflicts between production-motivated design choices. Both proposals grounded in demonstrated deployment needs.

### Not implicated: A-1 through A-14 (no tensions or drifts)

---

## PRINCIPLE 12: Transition Path

### Findings
- TENSION [high]: A-5 - Virtual functions cannot have contracts, permanently splitting codebases between contract-checked and assert-checked preconditions at the type-erasure boundary.
- TENSION [high]: A-7 - Coroutine postconditions can't express result-given-inputs relationships, blocking contract adoption for all P2300-style async code that returns senders from coroutines.
- TENSION [medium]: A-3 - Existing defensive assert() on noexcept functions cannot be trivially replaced with contract_assert due to different exception semantics.
- DRIFT [medium]: Mixed-mode semantics offer no incremental migration strategy.
- DRIFT [low]: Standard library non-adoption provides no exemplar for transition.
- SIGNAL [positive]: P2900's "no client-side break" principle protects existing code.
- SIGNAL [positive]: Ignored semantics provide zero-cost coexistence.

### Not implicated: A-1, A-2, A-4, A-6, A-8, A-9, A-10, A-11, A-12, A-13, A-14

---

## PRINCIPLE 13: Useful Now

### Findings
- TENSION [medium]: A-7 - Postconditions on async coroutine code bind to opaque sender handles, not eventual results. Not useful for the most common case.
- TENSION [medium]: A-5 - Virtual function prohibition blocks contracts at type-erasure boundaries in use today.
- DRIFT [low]: P1494R5 conditional dependency.
- DRIFT [low]: Multi-paper knowledge barrier - understanding interactions requires reading both papers.
- SIGNAL [positive]: Synchronous contract usage on sender code works intuitively today.

### Not implicated: A-1, A-2, A-3, A-4, A-6, A-8, A-9, A-10, A-11, A-12, A-13, A-14

---

## PRINCIPLE 14: Independent Composition

### Findings
- TENSION [high]: A-1 + A-10 - Contract termination cannot be handled by P2300's structured concurrency. One system cannot compose with the other's failure mode without modification.
- TENSION [high]: A-5 - Virtual prohibition blocks contracts at type-erasure composition boundary. Components crossing this boundary lose contract coverage.
- TENSION [high]: A-3 - Noexcept receiver contracts create terminate paths. P2300 components with noexcept must be modified (removing contracts) to compose safely.
- TENSION [medium]: A-2 - Violation handler throw unspecified in sender composition context.
- TENSION [medium]: A-7 - Coroutine postconditions don't compose with async result delivery.
- TENSION [medium]: A-14 - Postcondition const prevents composing value-channel moves with verification.
- TENSION [low]: A-9 - Zero-overhead cost imposed when combining contracted and non-contracted components.
- SIGNAL [positive]: A-4 - Concept orthogonality enables independent development.
- SIGNAL [positive]: A-12 - Freestanding enables independent deployment.

### Not implicated: A-4, A-6, A-8, A-11, A-12, A-13

---

## PRINCIPLE 15: Language, Not System

### Findings
- TENSION [medium]: Global violation handler creates process-wide system state. An execution domain cannot scope violation handling. P2300's composable domain mechanism is fundamentally different from the single global handler.
- TENSION [low-medium]: Build-system-level semantic selection defeats source-level local reasoning. No per-facility opt-in/opt-out in source.
- DRIFT [low]: Mixed-mode TUs amplify system-level configuration leakage into template-heavy P2300 code.
- SIGNAL [positive]: Contracts are freestanding - no system dependency.
- SIGNAL [positive]: Concept orthogonality prevents forced adoption coupling.
- SIGNAL [positive]: No implicit lambda captures preserve independence.

### Not implicated: A-1, A-2, A-3, A-4, A-5, A-6, A-7, A-9, A-10, A-11, A-13, A-14

---

## PRINCIPLE 16: General Mechanisms

### Findings
- TENSION [medium]: A-9 - Four evaluation semantics as special-purpose complexity where one general mechanism with composable policies could suffice. Quick_enforce bypasses the general handler mechanism.
- TENSION [medium]: A-7/A-12 - Coroutine contracts restricted where general mechanism should apply uniformly. P2900's general mechanism cannot express contracts for P2300's coroutine-based senders.
- DRIFT [low]: A-11 - Behavioral guarantees expressed in prose rather than in the general contract mechanism. Missed opportunity to unify.
- SIGNAL [positive]: P2300 and P2900 are complementary (structural vs value-level correctness) not duplicative.
- SIGNAL [positive]: Each mechanism's generality appropriate to its domain.

### Not implicated: A-1, A-2, A-3, A-4, A-5, A-6, A-8, A-10, A-13, A-14

---

## PRINCIPLE 17: Deterministic Resources

### Findings
- TENSION [high]: A-1 - Contract termination bypasses RAII cleanup of operation states in structured concurrency. Operation state destructors (which encode cleanup logic) skipped entirely.
- TENSION [high]: A-6 - Operation state lifetime UB makes RAII's core invariant unenforceable via contracts. The single most important resource-safety property in the target domain is uncheckable.
- TENSION [medium]: A-10 - Contract termination in child operations prevents parent-scope RAII cleanup. Resources requiring orderly release (file handles, locks, connections) abandoned.
- DRIFT [medium]: A-8 - Every semantic that checks contracts is either compatible with RAII (no violation) or hostile to it (termination without unwinding). No "checked but gracefully recoverable" path.

### Not implicated: A-2, A-3, A-4, A-5, A-7, A-9, A-11, A-12, A-13, A-14

---

## PRINCIPLE 18: Manual Control

### Findings
- TENSION [high]: Contract semantic selection entirely implementation-defined with no per-site override. P2300 hot-path functions cannot opt out of checking.
- TENSION [medium]: GPU platforms only viable with quick-enforce but no standard mechanism to mandate it.
- TENSION [medium]: Observable checkpoints imposed automatically - cannot opt out when race is benign.
- TENSION [medium]: No per-domain, per-function, or per-TU granularity for semantic control in source.
- DRIFT [medium]: Build-system control is the antithesis of manual programmer control.
- DRIFT [low]: When implementation chooses wrong semantic for a context, no recourse.
- SIGNAL [positive]: ignore semantic provides one coarse manual control lever.

### Not implicated: A-1, A-2, A-4, A-5, A-6, A-7, A-10, A-11, A-14

---

## PRINCIPLE 19: Say What You Mean

### Findings
- TENSION [high]: A-6 - Operation state lifetime UB ("do not destroy while in flight") is unsayable. The type system could express it; P2900 cannot help due to implicit const and deleted functions.
- TENSION [high]: A-7 - Coroutine completion promise ("this coroutine eventually produces a valid T") is structurally inexpressible. Postcondition fires at wrong semantic moment.
- TENSION [high]: A-2/A-3 - Protocol sequencing ("connect then start, once") is a convention. Could be state types but remains documentation. Contracts cannot express "may only be called once."
- TENSION [medium]: A-3 - Completion signal exclusivity (exactly one of value/error/stopped) is undeclared in code. Pure documentation.
- DRIFT [high]: A-11 - Laziness guarantee is pure prose. No predicate can observe "has not yet executed."
- DRIFT [medium]: A-4 - Semantic requirements beyond syntax are systematically inexpressible. Concepts check shape, not behavior.
- DRIFT [medium]: A-1 - Concepts check syntax, mean semantics. sender_of<S,T> means "produces T" but checks "has machinery consistent with producing T."
- SIGNAL [low]: A-5, A-8, A-9, A-10, A-13 - Various protocol properties that live in documentation.

### Not implicated: A-12, A-14

---

## PRINCIPLE 20: Direct Concept Mapping

### Findings
- TENSION [medium]: A-7 - Coroutine postcondition "result" maps to handle not async value. Mental model mismatch.
- TENSION [medium]: A-6/A-11 - Lazy sender model forces indirection between "contract of computation" and "contract of constructor."
- DRIFT [low]: A-1/A-14 - Sender's full "contract" split across three non-unifiable mechanisms (concepts, pre/post, prose).
- DRIFT [low]: A-5 - Type erasure erases concept-level contracts.
- SIGNAL [positive]: Concepts and contracts each map directly within their native domains.

### Not implicated: A-2, A-3, A-4, A-8, A-9, A-10, A-12, A-13

---

## PRINCIPLE 21: Safe Easy, Unsafe Possible

### Findings
- TENSION [high]: A-3 - Adding contracts to noexcept receivers (the "safe" path) is MORE dangerous than omitting them (latent terminate). Safety inversion.
- TENSION [high]: A-6 - Expressing the lifetime invariant (safe) is impossible. Leaving it as UB documentation (unsafe) is the only option.
- TENSION [high]: A-5 - The safe thing (contracts on type-erased interface) is prohibited.
- TENSION [high]: A-14 - Expressing postconditions on value delivery (safe) requires const parameters (breaks efficiency). The unsafe path (no postcondition) is easier AND more efficient.
- SIGNAL [medium]: A-9 - Zero-overhead with ignore gives an easy unsafe-but-fast path.
- SIGNAL [medium]: A-12 - Quick-enforce provides safe-for-embedded without handler complexity.

### Not implicated: A-1, A-2, A-4, A-7, A-8, A-9, A-10, A-11, A-12, A-13

---

## PRINCIPLE 22: No Preprocessor Dependence

### Findings
- TENSION [medium]: Migration gap where assert() cannot trivially become contract_assert due to semantic differences (implicit const, ignored contracts still parse, not an expression).
- TENSION [low]: Feature-test macros (__cpp_contracts) for detection remain preprocessor-dependent.
- DRIFT [low]: Coexistence period entrenches dual mechanisms because P2900 defers author-controlled semantic selection.
- SIGNAL [positive]: contract_assert is a keyword not a macro - advances the principle.
- SIGNAL [positive]: P2300 API is fully macro-free.

### Not implicated: A-1 through A-14 (most artifacts not relevant to preprocessor)

---

## PRINCIPLE 23: Local Verification

### Findings
- TENSION [high]: A-2 - Global replaceable handler makes contract violation behavior non-locally determinable. Cannot locally verify what happens on violation in sender code.
- TENSION [high]: A-3 - Whether a contract on a receiver causes terminate depends on noexcept-ness determined by adaptor chain above (non-local composition decision).
- TENSION [high]: A-6 - Operation state "in flight" status is non-local. Depends on whether start() was called and completion hasn't been delivered - distributed temporal state.
- DRIFT [medium]: A-8 - Which terminate path fires depends on system-wide implementation-defined configuration.
- DRIFT [medium]: A-11 - Whether contract side effects occur depends on compiler optimization level (non-local decision).
- DRIFT [medium]: A-13 - Observable checkpoint effectiveness depends on global optimization analysis.
- SIGNAL [low]: A-1, A-10 - Terminate at least has locally-predictable outcome (death).
- SIGNAL [low]: A-4 - Concepts provide local syntactic verification.

### Not implicated: A-4, A-5, A-7, A-9, A-12, A-14

---

## PRINCIPLE 24: Integration, Not Isolation

### Findings
- TENSION [high]: A-1 + A-2 + A-3 - Contract termination and violation-handler throws operate entirely outside P2300's three-channel error model. No integration path between contract failure and structured completion.
- TENSION [high]: A-5 - Virtual prohibition eliminates contracts at the primary composition boundary (type erasure). Features isolated at integration point.
- TENSION [high]: A-6 - P2300's core protocol invariant (operation_state lifetime) is inexpressible in P2900's vocabulary. The two features cannot "support each other" on the most critical property.
- TENSION [high]: A-7 - Coroutine postcondition timing misaligns with async delivery. Integration incomplete at the coroutine seam.
- TENSION [medium]: A-10 - Structured concurrency cannot integrate with contract failure mode. Two sub-languages with incompatible error models.
- TENSION [medium]: A-14 - Move semantics don't integrate with postcondition verification. Efficiency model and correctness model are mutually exclusive.
- DRIFT [medium]: Pattern of isolation: P2900 and P2300 each work internally but create gaps, incompatibilities, and dead zones when composed. They do not "support each other" per D&E S6.4.4.
- SIGNAL [positive]: A-4 - Concepts and contracts are orthogonal by design (independent, non-interfering).

---

## CHALLENGE RESULTS

[See c:\Users\Vinnie\src\tools-public\temp\vasa-challenge-p2300-p2900.md for full content]

Findings challenged: 15 | Survived: 5 | Tombstoned: 10 | Searches: 1
Highest surviving severity: high
Tombstone summary: 3 Scope, 3 Precedent, 3 Materiality, 1 Scope

---

## SYNTHESIS

### Executive Summary

P2300R10 (std::execution) and P2900R14 (Contracts for C++) are independently well-designed proposals that both serve demonstrated production needs. Ten of fifteen initial cross-coherence concerns were eliminated by the Challenge phase - three because they applied to any library (not P2300 specifically), three because they restate accepted 30-year C++ patterns (terminate bypasses everything; global replaceable functions are global), and three because the original analysis contained factual errors about P2900's mechanics. This pattern is itself significant: it suggests the two papers' interaction surface is narrower than initial inspection implies. Most apparent tensions dissolve on closer examination because the papers occupy genuinely different domains (protocol-level async composition vs. assertion-level correctness checking).

The five surviving findings cluster around a single structural theme: P2300's protocol-level requirements (noexcept receivers, move-through-channel efficiency, lazy composition) create contexts where P2900's contract features interact with measurable friction. Two findings reach high severity - enforcement overhead on hot paths cannot be locally opted out of (S-1), and adding preconditions to noexcept receiver functions inverts the safety calculus by introducing terminate paths that didn't exist before (S-4). Both are confirmed by independent committee awareness (P3166R0). These are not design defects in either paper individually; they are emergent properties of their composition that the committee should address with guidance or future mechanism.

### Per-Artifact Assessment

#### A-9: Zero-overhead claims under composition
- Principles flagged: Rule 1 (high), Rule 3 (high), Rule 18 (high)
- Compound: Constituent of "Contract Adoption Penalty"
- Assessment: The most direct cross-coherence finding - enforcement on P2300 hot paths reintroduces overhead that lazy composition specifically eliminated.

#### A-14: Parameter move semantics vs postcondition const
- Principles flagged: Rule 1 (medium), Rule 6 (medium), Rule 9 (medium), Rule 21 (medium)
- Compound: Constituent of "Contract Adoption Penalty"
- Assessment: Postcondition const creates a type-equality gap (free for int, costly for vector<T>) that specifically penalizes P2300's value-channel move patterns.

#### A-3: Receiver noexcept vs exception-from-predicate
- Principles flagged: Rule 5 (high), Rule 21 (high), Rule 14 (high), Rule 23 (high)
- Compound: Constituent of "Contract Adoption Penalty" and "Type-Erasure Gap"
- Assessment: The safety inversion - adding a precondition makes noexcept code MORE dangerous - is the most actionable finding. Committee-acknowledged via P3166R0.

#### A-5: Virtual function prohibition vs type-erased senders
- Principles flagged: Rule 4 (medium), Rule 8 (medium), Rule 10 (medium), Rule 12 (medium)
- Compound: Constituent of "Type-Erasure Gap"
- Assessment: Mitigated by NVI pattern and contract_assert in body. Residual tension is that existing non-NVI interfaces require restructuring.

#### A-12: Freestanding contracts vs embedded execution
- Principles flagged: Rule 3 (low), Rule 18 (low)
- Compound: None
- Assessment: Narrow practical concern; quick-enforce resolves the GPU case. Governance gap (cannot mandate semantic) is P2900-internal.

### Compound Dynamics

#### Compound 1: "Contract Adoption Penalty" (S-1 + S-2 + S-4)
Three independently-surviving findings that interact when a developer attempts to annotate P2300 sender/receiver code with contracts:
- S-1 imposes evaluation overhead on hot-path completion signals
- S-2 prevents postconditions from observing values without forcing copies
- S-4 makes preconditions on noexcept receivers potentially lethal
Interaction mechanism: S-1's absence of per-site semantic control means S-4's danger cannot be selectively mitigated. S-2's copy overhead compounds S-1's evaluation overhead. Together they create a comprehensive disincentive to annotate P2300 code with contracts - exactly contrary to contracts' purpose.

#### Compound 2: "Type-Erasure Gap" (S-3 + S-4)
Virtual prohibition pushes contracts to non-virtual wrappers or body assertions. But receiver protocols are noexcept, so:
- S-3 forces contract checking behind the virtual interface
- S-4 means the concrete implementations (called through noexcept virtual dispatch) face terminate risk from contract_assert if predicate throws
Interaction mechanism: S-3's NVI workaround places the precondition on a non-virtual function that delegates to a virtual function. If the non-virtual wrapper is noexcept (as P2300 receivers must be), S-4 applies to it.

### Positive Coherence

- Both papers target freestanding environments (A-12 alignment)
- Contracts invisible to concepts preserves P2300's type system (A-4)
- "Ignore" semantic provides genuine zero-overhead coexistence
- P2900's "no ABI break" and "no client-side break" protect P2300 code from involuntary contract effects
- The tombstone pattern (3 by Precedent) confirms that many apparent tensions are simply restatements of accepted C++ properties - the papers do not create novel hazards beyond those already inherent in the language

---

## STRESS TEST RESULTS

### SURVIVING COMPOUNDS

#### Compound 1: "Contract Adoption Penalty" (S-1 + S-2 + S-4)
Severity: high
Interaction mechanisms:
- S-1 -> S-4: No per-site semantic disable means terminate risk cannot be mitigated locally
- S-2 -> S-1: Copy overhead from const params stacks on evaluation overhead in same code path
- S-4 -> S-1: Natural response ("accept overhead for safety") backfires - safety introduces danger
Navigated Precedent: Exceptions + noexcept + move semantics (C++11/17). Committee provided per-function opt-out (noexcept) and conditional move (move_if_noexcept). Key difference: contracts MVP has NO per-function semantic opt-out.

#### Compound 2: "Type-Erasure Gap" (S-3 + S-4)
Severity: high
Interaction mechanisms:
- S-3 -> S-4: Virtual prohibition forces contracts to noexcept NVI wrapper, directly triggering S-4's terminate risk
- S-4 -> S-3: NVI workaround (the "escape" from prohibition) enters S-4's danger zone
Navigated Precedent: Virtual destructors + noexcept (C++11). Committee accepted "don't throw in destructors" principle. Difference: destructor bodies are programmer-controlled; contract predicates can accidentally throw.

### TOMBSTONED COMPOUNDS
None.

### TRIMMED COMPOUNDS
None.
