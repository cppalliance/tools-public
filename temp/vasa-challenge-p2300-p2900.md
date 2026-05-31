# Vasa Step 4: Challenge Results - P2300R10 + P2900R14

## CHALLENGE RESULTS

### SURVIVING

#### S-1: Contract enforcement overhead on P2300 hot paths
Principle: Rule 1 (Zero Overhead), Rule 3 (Leave No Room Below), Rule 18 (Manual Control)
Severity: high
Confidence: high
Artifacts: A-9, A-13 (A-13 weakened)

Finding: Enforce/observe semantics on P2300 hot-path customization points (set_value, start, connect, scheduler operations) reintroduce runtime checks at precisely the points P2300 eliminated overhead through lazy composition and intrusive storage. Observable checkpoints from contract evaluation act as optimization barriers, constraining reordering of cancellation-related code. The overhead is not opt-in at the composition boundary; it is inherited transitively through the sender algebra. P3166R0 independently identifies this concern: "One place where having accurate exception specifications is when using std::execution... An unnecessarily conservative noexcept(false) can result in additional overhead that the compiler cannot inline away."

Note: A-13's checkpoint concern is partially mitigated by P2900's own elision rules - if the compiler can prove a predicate true without evaluation, no evaluation occurs and no checkpoint is established. The core A-9 overhead of evaluating non-trivially-provable predicates remains intact.

Materiality example:
```cpp
struct validating_receiver {
    void set_value(int val) noexcept
        pre(val >= 0 && val < limit_)
    { buffer_[pos_++] = val; }
    int limit_;
    int* buffer_;
    int pos_ = 0;
};
// In a pipeline: just(42) | bulk(sch, 1'000'000, work) | ...
// Under enforce: predicate evaluated per-completion-signal.
// P2300 optimized away per-stage overhead; contracts reintroduce it.
```

Resolution questions:
1. Does P2300's bulk call set_value per-item or only on final completion? - Per-item calls go to the user function; set_value fires once per stage. But in deep pipelines (then|then|then|...), set_value fires per-stage-per-operation. (source: evidence)
2. Can compilers optimize away trivially-true contracts under enforce? - Yes per P2900 design choice #11, but only when statically provable. Runtime-dependent predicates must be evaluated. (source: evidence)
3. Does P2900 allow per-function semantic selection? - No. Semantic selection is implementation-defined and potentially global. No per-site opt-out. (source: evidence)
4. Could a quality implementation avoid checkpoint overhead for proven predicates? - Yes. If evaluation is skipped entirely (proven result), there is no "beginning of evaluation" and no checkpoint. This weakens A-13's contribution but not A-9's direct overhead. (source: evidence)
5. What is the expected deployment model for contracts on P2300 code? - P2900 Principle 5 says semantic should not be detectable at compile time. Libraries cannot defensively assume "ignore." (source: evidence)

Searched: yes (P3166R0 confirms committee awareness of contracts+P2300 noexcept/performance interaction)

---

#### S-2: Postcondition const blocks value-channel moves
Principle: Rule 1 (Zero Overhead), Rule 3 (Leave No Room Below), Rule 6 (Type Equality), Rule 9 (Features Over Prevention), Rule 14 (Independent Composition), Rule 21 (Safe Easy, Unsafe Possible), Rule 24 (Integration)
Severity: medium
Confidence: high
Artifacts: A-14

Finding: P2300's completion functions move values through channels: set_value(rcvr, vals...) typically moves value arguments into the receiver. P2900 requires that non-reference parameters odr-used in postconditions must be declared const on all declarations. If a sender adaptor's completion function has a postcondition referencing delivered values (to verify what was delivered), those parameters must be const - which prevents moving them. Either the postcondition cannot reference the delivered values (limiting what can be checked), or the values cannot be moved (violating P2300's efficiency model). The tension scales with type cost: int is unaffected, vector<T> pays a full copy.

Materiality example:
```cpp
struct forwarding_adaptor {
    void set_value(const std::vector<int> data) noexcept
        post(!data.empty())  // requires const parameter
    {
        // Cannot move from const - forces copy to next stage
        next_.set_value(data);  // copy, not move
    }
    // Without postcondition: zero-copy pass-through
    // With postcondition: O(n) copy penalty per stage
};
```

Resolution questions:
1. Can reference parameters avoid this? - P2300's set_value takes by value for move optimization. Changing to reference changes the API contract and prevents the callee from consuming. (source: evidence)
2. Could a postcondition reference a local copy? - No. P2900 postconditions reference parameters and result only, not locals. (source: evidence)
3. Is contract_assert in the function body a workaround? - Yes: `contract_assert(!data.empty()); next_.set_value(std::move(data));` works. But this loses the declarative postcondition semantics and caller-side checking option. (source: evidence)
4. Does P2300 code typically need postconditions on set_value? - set_value is a customization point; verifying "I forwarded correctly" is the natural postcondition use case for adaptors. (source: evidence)
5. Is there a future proposal for non-const postcondition observation? - Not identified. P2900 "future work" does not list this. (source: unanswered)

Searched: no

---

#### S-3: Virtual prohibition at type-erasure boundary
Principle: Rule 4 (Static Type Safety), Rule 5 (Visible Unsafety), Rule 8 (No Single Style), Rule 10 (Hybrid Styles), Rule 12 (Transition Path), Rule 14 (Independent Composition), Rule 21 (Safe Easy), Rule 24 (Integration)
Severity: medium
Confidence: medium
Artifacts: A-5

Finding: P2300 explicitly acknowledges type erasure facilities will be built on top (assumption #6, e.g., any_sender<Sigs...>). Type-erased sender/receiver implementations use virtual dispatch internally. P2900 makes it ill-formed to place pre/post on virtual functions. The virtual interface layer of type-erased execution primitives cannot carry declarative contracts. Contracts can exist on concrete implementations or non-virtual public wrappers (via NVI), but the virtual dispatch boundary itself is contract-free.

Mitigations identified:
- NVI pattern: non-virtual public method carries contract, delegates to private virtual. This is an established C++ idiom.
- contract_assert in virtual function bodies is permitted (prohibition is on pre/post specifiers only).
- P2900 Principle 14 explicitly leaves this "ill-formed to enable flexible evolution" - the limitation is temporal.

These mitigations reduce severity from high to medium. The residual tension is: existing non-NVI virtual interfaces (which are common in type-erasure libraries) cannot be annotated without restructuring.

Materiality example:
```cpp
// Existing pattern (cannot add contracts):
struct any_sender_vtable {
    virtual void start_impl() = 0;  // no pre/post allowed
};
// Required restructuring (NVI, works):
struct any_sender_vtable {
    void start() pre(/* valid state */) { start_impl(); }
private:
    virtual void start_impl() = 0;
};
// contract_assert workaround (works, less declarative):
void start_impl() override {
    contract_assert(/* valid state */);
    // ... implementation
}
```

Resolution questions:
1. Does the NVI pattern fully resolve this? - For new code, yes. For existing virtual interfaces in libraries (libunifex, stdexec), restructuring is required. (source: evidence)
2. Is virtual function contract support on the P2900 roadmap? - Listed as "feature not proposed" for the MVP. Explicitly left for future proposals. (source: evidence - P2900 Section 2.3)
3. Do existing type-erasure implementations use NVI? - Mixed. stdexec uses tag_invoke/concepts, not virtual. Future any_sender would likely be designed post-P2900, so NVI is viable. (source: evidence)
4. Is contract_assert in the body semantically equivalent? - No. Body assertions are callee-side only, cannot be checked at call site, and are not part of the interface declaration. (source: evidence)
5. How do existing libraries handle contract checking at virtual boundaries today? - Via assert() in function bodies. contract_assert provides an equivalent path. (source: evidence)

Searched: no

---

#### S-4: Noexcept receiver contracts create latent terminate (safety inversion)
Principle: Rule 5 (Visible Unsafety), Rule 8 (No Single Style), Rule 10 (Hybrid Styles), Rule 14 (Independent Composition), Rule 21 (Safe Easy, Unsafe Possible), Rule 23 (Local Verification), Rule 24 (Integration)
Severity: high
Confidence: high
Artifacts: A-3

Finding: P2300's receiver completion functions (set_value, set_error, set_stopped) are noexcept as a protocol requirement - not a user choice. If a contract precondition on a receiver's set_value has a predicate that throws during evaluation (e.g., calls a function that throws, dereferences something that triggers an exception), P2900 treats this as a contract violation with detection_mode::evaluation_exception. Under enforce/quick-enforce: program terminates. Under observe: handler called, and if handler returns normally, execution continues - BUT the original exception from the predicate is consumed by the contract machinery, not propagated. This creates a safety inversion: adding a contract (the "safe" thing) introduces a terminate path that did not exist before (making the code MORE dangerous). The programmer's intent was to add safety checking; the effect is latent process death from any predicate that can throw.

P3166R0 independently identifies this category of concern: "whether a function with a deduced exception specification that evaluates a contract_assert should be considered potentially-throwing" is called out as an open question affecting P2300 pipelines specifically.

Materiality example:
```cpp
struct my_receiver {
    void set_value(auto val) noexcept
        pre(registry_.contains(val.id))  // map lookup: might throw
    { process(val); }
    std::map<int, bool> registry_;
    // If registry_ is in a bad state (moved-from, corrupted),
    // .contains() might throw -> contract violation ->
    // under enforce: terminate. The contract CAUSED the death.
    // Without the contract: set_value executes, possibly incorrectly
    // but program stays alive for diagnosis.
};
```

Resolution questions:
1. Can P2300 implementations make receivers non-noexcept? - No. Many sender adaptors (when_all, let_value internals) require noexcept completion functions for correctness. It is a protocol requirement. (source: evidence - P2300 spec)
2. Can predicates be constrained to noexcept expressions? - Not by P2900's design. Predicates are arbitrary boolean expressions. The evaluation_exception mechanism exists precisely because predicates CAN throw. (source: evidence)
3. Does the observe semantic mitigate this? - Partially. Under observe, if handler returns, execution continues. The predicate's exception is consumed (not propagated out of the noexcept function). But the program state may be inconsistent. (source: evidence)
4. Can static analysis catch potentially-throwing predicates? - Possible but not required by the standard. Quality implementations might warn. (source: unanswered)
5. Is there a pattern to write provably-noexcept predicates? - Yes: use only noexcept operations in predicates on noexcept functions. But this is undocumented guidance and easy to violate accidentally. No enforcement mechanism exists. (source: evidence)

Searched: yes (P3166R0 confirms committee awareness; amplifies finding)

---

#### S-5: Freestanding handler mechanism on GPU/accelerator targets
Principle: Rule 3 (Leave No Room Below), Rule 18 (Manual Control)
Severity: low
Confidence: low
Artifacts: A-12

Finding: P2900's `<contracts>` header is freestanding (available on constrained implementations). P2300 explicitly targets GPUs, embedded systems, and accelerators. The violation handler (replaceable global function with function-pointer-like semantics) may not be meaningful on GPU execution contexts where global state, function pointers, and dynamic dispatch behave differently from CPU contexts. Quick-enforce (immediate termination, no handler) is the only viable semantic on many accelerators, but no standard mechanism mandates quick-enforce for specific execution domains.

The practical tension is narrow: quick-enforce resolves the GPU case. The residual issue is governance - a domain cannot mandate its own semantic within source code. This is an instance of the broader "no per-domain semantic control" limitation, which P2900 intentionally defers.

Materiality example:
```cpp
// GPU-scheduled bulk work via P2300:
auto gpu_work = starts_on(gpu_scheduler) | bulk(1024*1024,
    [](int idx, auto& state)
        pre(idx < state.size())  // Under enforce: handler call on GPU?
    { state[idx] = compute(idx); }
);
// Quick-enforce: works (trap instruction, GPU kernel abort)
// Enforce with handler: handler is a global CPU function -
//   what execution context does it run in? Unspecified.
```

Resolution questions:
1. Does quick-enforce fully resolve the GPU case? - Yes, for termination. A GPU kernel abort is the natural behavior. (source: evidence)
2. Can implementations mandate quick-enforce on GPU targets? - Yes, via implementation-defined semantic selection. The standard allows this. But user code cannot mandate it. (source: evidence)
3. Do existing GPU assertion models provide a handler? - CUDA's __assert_fail on device triggers a host-side error after kernel completion. Not a synchronous handler. (source: evidence)
4. Is per-domain semantic selection on the roadmap? - Not in MVP. "Per-assertion semantic specification" is listed as future work. (source: evidence)
5. Would a GPU execution domain simply ignore contracts? - Viable under the "ignore" semantic. But this defeats the purpose of contracts on GPU code. (source: evidence)

Searched: no

---

### TOMBSTONED

#### K-1: Operation state lifetime UB unexpressible via contracts
Principle: Rule 17, 19, 21, 23, 24, 4, 6, 7, 9
Killed by: Materiality
Reason: The finding's core claim - that P2900's implicit const prevents expressing the "do not destroy while in flight" invariant - is factually incorrect. Implicit const makes id-expressions within predicates into const lvalues, which prevents *modification* but not *reading*. A destructor precondition `~op_state() pre(!started_ || completed_)` reads bool members through const access, which is perfectly valid. Furthermore, destructors (when user-declared and not defaulted) CAN carry pre/post specifiers; only deleted/defaulted functions and virtual functions are prohibited. The invariant IS expressible in P2900's vocabulary if the type exposes readable state. The gap is that P2300's exposition-only types don't currently provide such accessors - a P2300 API design choice, not a P2900 mechanical barrier.
Original finding: "P2300's most critical lifetime invariant - do not destroy operation_state while the async operation is in flight - is expressed as UB. This is exactly the kind of semantic requirement that contracts should express. However, the 'in flight' state is internal to the operation, and P2900's implicit const in predicates prevents reading mutable members. Furthermore, operation_state's deleted copy/move constructors cannot carry contracts. This invariant remains unexpressible via contracts."

---

#### K-2: Contract termination vs exactly-once completion / structured concurrency
Principle: Rule 1, 5, 10, 14, 17, 24
Killed by: Precedent
Reason: The C++ standard already contains this exact pattern: std::terminate from any source (noexcept violation, unhandled exception in thread, condition_variable destruction during wait, failed dynamic_cast on reference) bypasses ALL error propagation models. std::thread + std::terminate exhibits the identical structure: a structured concurrency primitive (join-on-destruct) whose error channel (exception propagation) is bypassed by terminate. P2300's structured concurrency model is no different from std::thread in this regard - both rely on error channels that terminate circumvents. Contract termination is simply another source of terminate, identical in effect to a noexcept function that throws. The committee has accepted this pattern since C++11.
Original finding: "P2300 guarantees exactly-once completion. P2900's contract termination bypasses all three channels - the operation never 'completes' in P2300's sense. Structured concurrency invariants (parent notification, sibling cancellation) are bypassed."

---

#### K-3: Coroutine postconditions check ramp return, not async result
Principle: Rule 5, 7, 10, 12, 13, 14, 19, 20, 24
Killed by: Scope
Reason: The coroutine postcondition timing issue (postcondition evaluates on ramp function return, not at eventual value delivery) applies identically to ALL coroutine frameworks - std::future, folly::Task, cppcoro::task, libunifex - not specifically to P2300 senders. Any coroutine returning a handle/future/sender has this property. P2900 itself acknowledges this limitation (P4208R0's Advocatus filed this charge and dismissed it under Confessio - P2900 Section 3.5.2 explicitly states the timing). The finding exists examining P2900 alone without reference to P2300.
Original finding: "When a P2300-integrated coroutine has contracts: the postcondition fires when the coroutine handle returns to the caller, not when the async value is eventually delivered. Postconditions on async coroutines check the sender-return, not the eventual completion value."

---

#### K-4: Handler throw unspecified for sender context
Principle: Rule 1, 5, 14, 24
Killed by: Materiality
Reason: The finding claims "There is no specification of how violation-handler exceptions interact with the sender/receiver error channel." This is false. P2900 design choice #19 specifies: "Handler throw = as if from function body." P2300's sender adaptor implementations catch exceptions thrown from user code within sender operations and route them to set_error. The "as if from function body" rule means handler exceptions ARE caught by the same try/catch mechanism. The interaction IS fully specified by composition of both papers' rules. The dangerous case (exception in noexcept receiver) is fully subsumed by finding S-4 (A-3). No distinct tension remains.
Original finding: "There is no specification of how violation-handler exceptions interact with the sender/receiver error channel. If the violation occurs in a sender's operation, the exception could be caught and channeled through set_error - but only if the implementation wraps contract-violation exceptions the same way it wraps other exceptions."

---

#### K-5: Concepts don't see contracts (semantic enforcement gap)
Principle: Rule 4, 5, 7, 19, 20
Killed by: Scope
Reason: "Concepts check syntax, not semantics" is a fundamental and universal limitation of C++ concepts that predates both P2300 and P2900. Every concept in the standard - std::regular (requires equality-preserving copy), std::sortable (requires strict weak order), std::ranges::range (requires valid iteration semantics) - has semantic requirements that escape compile-time verification. The finding that P2300's concepts (scheduler, sender, receiver) have semantic requirements unchecked by concepts is identical to this universal pattern. You do not need P2900 to observe it. Contracts not closing this gap is a restatement of "contracts check values at runtime, concepts check syntax at compile time" - which is by design (P2900 Principle 3).
Original finding: "Contracts cannot serve as a mechanism to statically reject types that fail to meet semantic requirements beyond syntactic ones. A type that models sender syntactically but violates a semantic invariant will still satisfy the concept regardless of contracts."

---

#### K-6: Side effect elision makes contract observation unreliable
Principle: Rule 19, 23
Killed by: Materiality
Reason: Under checking semantics (enforce/observe), predicates that read runtime-dependent state ARE evaluated - the compiler can only skip evaluation when it can prove the result statically. For a predicate like `pre(submitted_flag_)` where `submitted_flag_` depends on runtime execution (set by `connect`), the compiler cannot prove the result without evaluation, so the predicate MUST be evaluated. The "unreliable observation" concern only applies under the "ignore" semantic, where zero evaluation is the explicit design intent (P2900 Principle 4). Under any checking semantic, observation of runtime state is reliable. The finding conflates "ignore means no checking" (which is by design) with "checking is unreliable" (which is false).
Original finding: "If a contract predicate probes whether work has been submitted, the compiler may elide or duplicate that check, making it unreliable as a diagnostic tool. Contracts cannot be used to implement or enforce P2300's laziness guarantee."

---

#### K-7: Terminate paths indistinguishable diagnostically
Principle: Rule 5, 23, 24
Killed by: Precedent
Reason: std::terminate called from ANY source (noexcept violation, unhandled exception, thread::~thread on joinable, condition_variable destruction during wait, lock destruction while held) is diagnostically indistinguishable without external tooling. This has been an accepted property of C++ since C++11. The standard provides mitigation: std::set_terminate allows a custom handler that can log context, and std::current_exception() in the terminate handler provides some information. Contract termination adding a third source to P2300's existing two terminate paths does not create a novel diagnostic challenge - it is the same challenge that exists for all terminate sources.
Original finding: "Distinguishing between 'terminate because operation_state lifetime was violated,' 'terminate because run_loop was destroyed too early,' and 'terminate because a contract was violated' requires post-mortem analysis. The terminate paths compose but do not compose diagnostically."

---

#### K-8: Global violation handler as system state
Principle: Rule 15, 23
Killed by: Precedent
Reason: Replaceable global functions are an established C++ pattern: `operator new`/`operator delete` (global, cannot be scoped per library/domain), `std::set_terminate` (global), `std::set_new_handler` (global). P2900's violation handler uses "Same mechanism as operator new replacement" (design choice #16 - the paper itself names the precedent). P2300's composable domain mechanism operating at a different granularity than the global handler is structurally identical to P2300's composable allocator mechanism operating at a different granularity than global operator new. This tension is not novel - it is the accepted cost of the global-replaceable-function pattern.
Original finding: "Global violation handler creates process-wide system state. An execution domain cannot scope violation handling. P2300's composable domain mechanism is fundamentally different from the single global handler."

---

#### K-9: Build-system semantic selection defeats source control
Principle: Rule 15, 18
Killed by: Scope
Reason: Build-system-level semantic selection is a P2900 design choice (Principle 5: "Which semantic is active should not be detectable at compile time"; design choice #3: "Semantic selection is implementation-defined") that exists independently of P2300. The concern - that source code cannot locally determine which semantic applies - requires only P2900 to identify. P2300's template-heavy code is no different from any other template-heavy library (Boost.Asio, ranges-v3, Eigen) in this regard. The finding is internal to P2900's design philosophy.
Original finding: "Build-system-level semantic selection defeats source-level local reasoning. No per-facility opt-in/opt-out in source."

---

#### K-10: Rule 18 manual control tensions (per-site override)
Principle: Rule 18
Killed by: Scope
Reason: "Contract semantic selection entirely implementation-defined with no per-site override" and "No per-domain, per-function, or per-TU granularity for semantic control in source" are P2900-internal design observations. These concerns exist examining P2900 alone and do not require P2300's execution model to identify. The P2300-specific aspect (hot-path functions cannot opt out) is already captured by S-1 (the surviving overhead finding).
Original finding: "P2300 hot-path functions cannot opt out of checking. No per-domain, per-function, or per-TU granularity for semantic control in source."

---

## BREADCRUMB

```
BREADCRUMB: {step: 4, findings_challenged: 15, survived: 5, tombstoned: 10, searches_performed: 1, highest_surviving_severity: "high", tombstone_summary: "3 killed by Scope (coroutine/concepts/build-system are single-source findings), 3 killed by Precedent (terminate-bypasses-error-model and global-handler are accepted C++ patterns), 3 killed by Materiality (handler-throw IS specified, side-effect elision IS reliable under checking, operation-state IS expressible), 1 killed by Scope (manual-control is P2900-internal)"}
```
