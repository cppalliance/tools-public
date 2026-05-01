# Corosio and Capy: A Coroutine-First Redesign of C++ Networking I/O

**A two-layer library stack that replaces twenty years of callback-based async patterns with a concept-driven, coroutine-native design - and lands cleanly across nearly every measured dimension.**

April 2026, by Vinnie Falco

---

## 1. Executive Summary

Boost.Corosio and Boost.Capy together represent the most structurally disciplined C++ networking submission this review has examined. Capy provides the coroutine I/O foundation - executor model, task types, buffer sequences, cancellation, stream abstractions - while Corosio provides the networking layer: TCP/UDP sockets, TLS streams, DNS resolution, timers, signals, and file I/O. The dependency direction is clean: Corosio depends on Capy; Capy depends on nothing but the C++20 standard library.

Thirty-eight diagnostic tests across nine structural categories produced one surviving finding at low-medium confidence: undocumented exception safety guarantees. Four additional candidate findings were challenged and killed - including the initial P2300 interoperability concern, which was resolved when user testimony revealed bidirectional sender/receiver bridges (`await_sender`, `as_sender`, `split_ec`) already exist in the examples alongside published papers on a universal continuation model. No compound dynamics emerged. The coupling map is empty.

The competitive position is strong. Against six surveyed competitors - including the incumbent Boost.Asio, Boost.Cobalt, cppcoro, libunifex, async_simple, and Async++ - Corosio+Capy hold nine unique differentiators (including the P2300 bridge) while carrying one gap: no io_uring backend (planned). A derivatives exchange is actively porting its production stack to Corosio<sup>12</sup>. The design is Promising - a sound core on clear trajectory toward production-grade, with the single surviving finding addressable as documentation work.

---

## 2. The Project

Boost.Capy<sup>2</sup> is a C++20 coroutine I/O foundation library created by the C++ Alliance. It provides the IoAwaitable protocol for automatic executor affinity propagation<sup>5</sup>, task types (`task<T>`, `io_task`), 15 concepts constraining streams, buffers, executors, and I/O patterns, execution infrastructure (`execution_context`, `thread_pool`, `strand`, `async_mutex`, `async_event`), a 14-header buffer type hierarchy, 9 type-erased `any_*` wrappers, composition primitives (`when_all`, `when_any`, `delay`, `timeout`), a frame allocator with thread-local recycling pool, bidirectional P2300 sender/receiver bridges (`await_sender`, `as_sender`, `split_ec`)<sup>12</sup>, and a testing toolkit (`fuse`, `bufgrind`, mock streams)<sup>2</sup>. Approximately 200 public symbols across 85 headers.

Boost.Corosio<sup>1</sup> is the networking layer built exclusively on Capy. It provides `tcp_socket`, `tcp_acceptor`, `tcp_server`, `udp_socket`, `timer`, `resolver`, `signal_set`, endpoint/address types, `tls_context` with portable TLS abstraction over OpenSSL and wolfSSL backends, `random_access_file`, `stream_file`, Unix domain sockets, and `io_context` aliased to the platform-appropriate backend: IOCP on Windows, epoll on Linux, kqueue on macOS/FreeBSD, select as fallback<sup>1</sup>. Approximately 60 public symbols across 30 headers.

The libraries originate from Peter Dimov's observation that "an API designed from the ground up to use C++20 coroutines can achieve performance and ergonomics which cannot otherwise be obtained"<sup>3</sup>. They are positioned as the successor to Boost.Asio<sup>4</sup> and target WG21 standardization through a 14-paper series split into two stages - P4100R1 ("The Network Endeavor")<sup>12</sup>. Stage One (Papers 1-7) proposes pure C++20 abstractions with no platform dependency: IoAwaitable protocol, task types, executor utilities, buffer ranges, dynamic buffers, stream concepts, and combinators. Stage Two (Papers 8-14) proposes platform I/O: timers, signals, files, TCP, DNS, UDP, and TLS. Key papers are published: P4003R1 (IoAwaitable)<sup>5</sup>, P4172R0 (design rationale), P4088R0 (what coroutines buy), P4007R0 (senders and coroutines), P4092R0 (consuming senders from coroutine-native code), P4093R0 (producing senders from coroutine-native code), P4126R0 (a universal continuation model, with Klemens Morgenstern), and P4125R0 (field report from a derivatives exchange)<sup>14</sup>.

Three primary maintainers - Vinnie Falco (372 combined commits), Steve Gerbino (210), Michael Vandeberg (91) - with contributions from 10 additional developers<sup>10</sup><sup>11</sup>. Three independent Boost library authors have adopted the stack: Ruben Perez (Boost.MySQL, migrating to Corosio), Marcelo Zimbres Silva (Boost.Redis, experimental port completed), and the Boost.Postgres team (building on Corosio from day one)<sup>12</sup>. A derivatives exchange is porting production trading infrastructure to Corosio - P4125R0 documents qualitative findings<sup>14</sup>.

Both libraries are licensed under BSL-1.0 and built with dual CMake + B2 support.

---

## 3. The Domain

C++ asynchronous I/O and coroutine-based networking serves developers building networked applications, server software, and high-performance I/O systems - game servers, financial infrastructure, embedded networking, cloud-native proxies. For two decades, Boost.Asio has been the de facto standard, but its callback/completion-handler model pre-dates C++20 coroutines, and retrofitting coroutine support onto that foundation produces ergonomic and performance compromises.

Five stress points define what this domain demands:

1. **Coroutine lifetime safety.** Lambda coroutines with captures are the single most reported class of bug in C++ coroutine code. The library must make use-after-free from frame/lambda lifetime mismatches structurally impossible or compile-time diagnosable.

2. **Zero-overhead I/O.** Steady-state async operations must achieve throughput within single-digit percentage points of raw platform syscalls. Users measure per-operation overhead in nanoseconds. Zero steady-state heap allocations is the established expectation.

3. **Cross-platform backend abstraction.** A single API surface must abstract over IOCP, epoll, and kqueue without leaking platform-specific behavior. Every major competitor provides this as table stakes. Asio's io_uring backend has exposed how hard this is to get right.

4. **Structured cancellation propagation.** Stop tokens must flow uniformly from parent coroutines to all child operations and platform I/O calls without manual wiring. C++20 `std::stop_token` and C++26 `std::inplace_stop_token` establish the vocabulary.

5. **Compilation cost discipline.** The library must avoid the build-time penalty that made Boost.Asio a bottleneck. Separate compilation mode or equivalent template-instantiation control is required.

---

## 4. The Landscape

Six open source competitors were surveyed. The field splits into three tiers: the incumbent (Asio), coroutine-era entrants (Cobalt, cppcoro), and sender/receiver or lightweight alternatives (libunifex, async_simple, Async++).

1. **Boost.Asio** (BSL-1.0, ~21 years, 1,555 stars) - the defining library in this space. Multi-paradigm: callbacks, futures, coroutines via completion tokens. Supports IOCP, epoll, kqueue, io_uring, select. Extensive documentation refined over two decades. C++20 coroutine support is retrofitted via `use_awaitable` rather than native<sup>1</sup>.

2. **Boost.Cobalt** (BSL-1.0, ~2.5 years, 338 stars) - coroutine-first primitives (`task`, `promise`, `generator`, `channel`) layered on top of Asio's executor and I/O infrastructure. Clean coroutine API but inherits Asio's entire dependency graph.

3. **cppcoro** (MIT, ~9 years, 3,829 stars) - Lewis Baker's pioneering coroutine library. Task types, cancellation tokens, file I/O, TCP/UDP sockets. Effectively unmaintained since 2024. Windows-centric; Linux support was never completed.

4. **libunifex** (Apache-2.0, ~6.5 years, 1,689 stars) - Facebook's sender/receiver prototype implementing P2300. Schedulers, timers, io_uring file I/O, stop_token cancellation. No networking primitives.

5. **async_simple** (Apache-2.0, ~4 years, 2,161 stars) - Alibaba's lightweight async framework with Lazy (stackless) and Uthread (stackful) coroutines. Networking only through Asio integration.

6. **Async++** (MIT, ~4 years, 104 stars) - header-only coroutine building blocks with separate io_uring, curl, and gRPC wrappers.

**Competitive position.** Corosio+Capy hold nine features no competitor matches: the IoAwaitable concept protocol for automatic executor affinity, the two-layer architecture, built-in mock socket and test infrastructure, a type-erased stream hierarchy, a comprehensive concept-constrained buffer type system, a frame allocator with zero-steady-state-allocation recycling, dual TLS backends (OpenSSL + wolfSSL), zero external dependencies from the foundation layer, and bidirectional P2300 sender/receiver bridges (`await_sender` consumes senders inside Capy coroutines; `as_sender` presents IoAwaitables as P2300 senders)<sup>12</sup>.

One gap is visible: Corosio uses epoll on Linux while Asio, libunifex, and Async++ support io_uring - the kernel-batched I/O interface that reduces syscall overhead for high-connection-count servers. An io_uring backend is planned<sup>13</sup>. The platform backend abstraction was designed for exactly this kind of addition.

**Design pattern divergence.** The field's deepest split is between completion-token multi-paradigm (Asio), coroutine-native (Corosio+Capy, Cobalt, cppcoro), and sender/receiver (libunifex). Corosio+Capy take the strongest position of any entrant: coroutine-only with no callback or future API, concept-constrained rather than duck-typed, and structurally layered rather than monolithic. Where Asio accumulated twenty years of abstraction generality, Corosio+Capy make a single bet - coroutines - and optimize the entire stack for it.

---

## 5. Design Assessment

### 5.1 The Coroutine Contract

The defining design decision is the IoAwaitable protocol<sup>5</sup>. When a coroutine is launched with a designated executor, every child coroutine inherits that executor affinity automatically through `co_await` chains. The `task<T>` promise's `transform_awaitable` intercepts every `co_await` expression and injects the environment - executor reference, stop token, frame allocator - without the user writing dispatch or transfer code<sup>7</sup>.

This is structurally different from Asio's manual strand dispatch, Cobalt's inherited-from-Asio model, or libunifex's scheduler CPO queries. The protocol makes incorrect executor resumption a structural impossibility rather than a runtime bug to avoid. The concept-constrained API (15 concepts across IoAwaitable, Executor, ExecutionContext, ReadStream, WriteStream, and buffer families) ensures that any user-provided type that satisfies the syntactic and semantic requirements participates fully in executor propagation, cancellation, and frame allocation<sup>2</sup>.

The error model complements this. All I/O operations return `io_result<Ts...>` - a structured result carrying `std::error_code` plus operation-specific values, supporting structured bindings (`auto [ec, n] = co_await s.read_some(buf)`)<sup>2</sup>. Portable error conditions (`cond::eof`, `cond::canceled`, `cond::timeout`) map platform-specific codes to a uniform vocabulary<sup>2</sup>. Exceptions are reserved for programmer errors (precondition violations) and allocation failure, channeled through centralized `detail::throw_*` helpers. This dual-layer model is cleaner than Asio's dual error_code/exception API and avoids Cobalt's exception-on-co_await pattern (Abrahams 2001).

### 5.2 Layered Physical Design and Structural Type Erasure

The Capy/Corosio split is the most important architectural property. Capy is the foundation: executor model, task types, buffer sequences, stream abstractions, cancellation, composition, testing. Corosio is the networking layer: sockets, acceptors, TLS, DNS, timers, signals, file I/O<sup>1</sup><sup>2</sup>. The dependency direction is strict and acyclic: Corosio includes Capy headers; Capy includes nothing from Corosio.

This is a deliberate departure from Asio's monolithic design and Cobalt's parasitic layering (Lakos 1996). Capy is independently useful for non-networking I/O - Boost.Http compiles once against `any_stream&` and works with any transport without recompilation<sup>12</sup>. The standardization strategy follows: Capy's stable abstractions belong in the standard library; Corosio can evolve externally where networking implementations historically face consensus difficulty<sup>3</sup>.

Within Corosio, every I/O object exposes three API layers<sup>12</sup>. The abstract layer (`io_stream`, `io_read_stream`) provides protocol-agnostic virtual dispatch, separately compilable, with no platform headers. The concrete layer (`tcp_socket`, `timer`) provides the full protocol-specific API, still virtual dispatch, still separately compilable. The native layer (`native_tcp_socket<Backend>`) is templated on the platform backend with member function shadowing that eliminates the vtable for full inlining. The user chooses the layer. Libraries that accept `any_stream&` at the abstract layer achieve ABI stability - new transports plug in without recompilation. Hot paths that need zero overhead use the native layer.

The structural novelty is how coroutines subsidize type erasure. When a coroutine calls `co_await stream.read_some(buf)`, the caller's frame persists across suspension. That frame is already allocated. `any_stream` type-erases without per-operation allocation because the operation state lives in the coroutine frame, not in a template<sup>15</sup>. `task<T>` has one template parameter because `coroutine_handle<>` erases the coroutine's type structurally - no allocator parameter, no executor parameter, no scheduler parameter. The IoAwaitable protocol propagates context through `await_suspend`, keeping the task type simple while the compiler provides the type erasure that template-based designs must build by hand. No competitor achieves ABI-stable byte-oriented I/O with zero per-operation allocation overhead.

Implementation hiding is thorough. Platform backends live in `native/detail/` with IOCP, epoll, kqueue, and select implementations fully hidden behind the `io_context` alias. Internal types live in `detail/` namespaces across both libraries. No leaked internals were detected in the reconnaissance<sup>7</sup><sup>8</sup>.

### 5.3 Resource Safety and Concurrency

RAII coverage is complete. `task<T>` and `quitter<T>` own coroutine frames, destroying them on destruction and exchanging on move. I/O objects (sockets, acceptors, timers) close and cancel pending operations in their destructors. `work_guard<E>` pairs work-started/finished calls with RAII. `async_mutex::lock_guard` auto-unlocks. Frame allocation uses a `recycling_memory_resource` that achieves zero steady-state allocations after warmup, with configurable per-deployment policy<sup>2</sup>.

Thread safety documentation is systematic. Every public class carries an explicit `@par Thread Safety` annotation with the pattern "Distinct objects: Safe. Shared objects: [Safe/Unsafe]" applied consistently across both libraries with per-type granularity<sup>7</sup><sup>8</sup>. The strand serializes coroutine execution through a pool of 211 implementations selected by hash. The async_mutex provides zero-allocation coroutine locking with intrusive FIFO wait queues and stop_token-based cancellation<sup>2</sup>.

Ownership is communicated through type distinctions: `executor_ref` (non-owning, lightweight) versus `any_executor` (owning via `shared_ptr`), non-copyable `task<T>` versus `shared_ptr`-backed `tls_context`<sup>2</sup>.

### 5.4 Verification Depth

The verification story is unusually strong for a pre-1.0 library. Capy has 88 unit test files mirroring the header structure. Corosio has approximately 30 test files covering all public types<sup>2</sup><sup>1</sup>. Both libraries include stress tests (`socket_stress.cpp`, `tls_stream_stress.cpp`), adversarial buffer testing (`bufgrind`), controlled failure injection (`fuse`), and mock sockets (`mocket`, `socket_pair`) as first-class library components<sup>2</sup>.

The CI matrix covers GCC 12-15, Clang 17-20, MSVC 14.34-14.42, Apple Clang (macOS 15 and 26), MinGW, and clang-cl across Linux, Windows, macOS, and FreeBSD<sup>6</sup>. Sanitizers (ASan, UBSan, TSan, Valgrind), clang-tidy warnings-as-errors, and code coverage (Codecov) run on every change. Both CMake and B2 build systems are tested, including `find_package` and `add_subdirectory` integration<sup>6</sup>.

Benchmark presence is strong. Ten comparative benchmarks against Asio - accept churn, fan-out, HTTP server, io_context throughput, local socket latency/throughput, TCP socket latency/throughput, and timer performance - run in both callback and coroutine Asio modes alongside Corosio's coroutine-only mode<sup>9</sup>. Profile benchmarks measure scheduler contention, queue depth, small-I/O overhead, and coroutine post cost<sup>9</sup>.

Beneath the tests and benchmarks sits a design rationale corpus of 13 documents<sup>17</sup> covering buffer representation and ownership, buffer sequence theory (tracing 25 years of Asio practice), buffer passing conventions, dynamic buffer semantics, combinator gap analysis (systematic comparison against P2300's model), combinator specification, continuation type design, executor transfer semantics, `read_some` error postconditions (consensus between Peter Dimov and Andrzej Krzemienski), sender channel routing, system executor design, and executor work-counting. Several are written for LEWG consumption. Each document maps the design space, enumerates alternatives, records trade-offs, and states the chosen position with rationale. This level of written design deliberation is rare in library submissions and provides reviewers with direct access to the reasoning behind every architectural decision.

### 5.5 The Exception Safety Documentation Gap

The one documentation gap that survived challenge: exception safety guarantees (basic, strong, nothrow) are not documented per public operation<sup>7</sup><sup>8</sup>. The thread safety documentation model (`@par Thread Safety` on every class) demonstrates the team's commitment to per-type guarantees, but the exception safety equivalent is absent. While the error_code-based I/O model minimizes the exception surface - only precondition violations (`std::logic_error`) and allocation failure (`std::bad_alloc`) throw - a Boost submission is expected to document these guarantees explicitly (Abrahams 2001, Sutter 1999). The fix is documentation work, not redesign. (low-medium)

### 5.6 The Standardization Bridge

The library integrates with C++ standard vocabulary types: `std::stop_token` for cancellation, `std::error_code`/`std::error_condition` for errors, `std::pmr::memory_resource` for allocation, and the tuple protocol for structured bindings<sup>2</sup>. An Asio buffer bridge header (`buffers/asio.hpp`) exists<sup>2</sup>.

Bidirectional bridges to P2300 (`std::execution` / sender-receiver) are provided in the examples and documented in three published WG21 papers<sup>16</sup>. P4092R0 ("Consuming Senders from Coroutine-Native Code") bridges the sender-to-awaitable direction: `await_sender()` consumes a P2300 sender inside a Capy coroutine with inline operation state, correct stop propagation, and automatic executor dispatch-back. P4093R0 ("Producing Senders from Coroutine-Native Code") bridges the reverse: `as_sender()` presents any IoAwaitable as a P2300 sender, with `split_ec()` adapting error_code-returning operations for P2300's three-channel error model. P4126R0 ("A Universal Continuation Model", with Klemens Morgenstern) explores zero-allocation sender-to-awaitable interop by giving senders direct access to the IoAwaitable protocol without a coroutine frame. Complete implementations are in the paper appendices and the Capy examples<sup>12</sup>. No other surveyed competitor provides bidirectional sender/awaitable interoperability at this level of rigor or with published committee papers documenting the design.

---

## 6. Design Maturity

The design is **Promising**. Thirty-four of thirty-eight diagnostic tests produce clean results. One surviving finding at low-medium confidence - undocumented exception safety guarantees - is a documentation gap, not a structural defect. No compound dynamics emerged; the coupling map is empty.

The structural picture is coherent. The IoAwaitable protocol, the two-layer physical architecture, the three-layer I/O object design (abstract/concrete/native), the concept-constrained API, the error_code-based error model, the systematic RAII coverage, the per-type thread safety documentation, the separate compilation model, the zero-dependency foundation, the structural type erasure that gives C++ ABI-stable byte I/O with zero per-operation allocation, the bidirectional P2300 bridges documented in three published WG21 papers, and the verification infrastructure all point in the same direction: a disciplined ground-up reimagining of C++ networking I/O. Where Asio accumulated twenty years of multi-paradigm generality, Corosio+Capy make a focused bet on coroutines and invest the design budget in getting that single model right. Three independent Boost library authors have adopted the stack, and a derivatives exchange is porting production infrastructure<sup>12</sup><sup>14</sup>.

The closest design parallel is Ranges-v3 - a concept-heavy C++ library designed explicitly as a reference implementation for eventual standardization, with clean physical modularity, extensive testing, and a clear separation between foundation abstractions and concrete algorithms. Like Ranges-v3 before its absorption into C++20, Corosio+Capy are at the stage where the design is proven but broad adoption and standardization feedback have not yet pressure-tested it at scale.

One gap separates the library from production-grade: the exception safety documentation is a mechanical fix. The io_uring backend (the remaining competitive gap on Linux) is planned and requires no architectural change - the platform backend abstraction was designed for exactly this kind of addition.

---

## 7. Audit Trail

**Sources:** GitHub API metadata, full source code read of both repositories (all public headers, source files, tests, CI configs, build files, documentation), web research for domain context and competitive landscape.

**Cache:** Fresh collection, 2026-04-30. No prior report exists.

**Supplementary imports:** None provided.

**Challenge outcomes:**
- Test 7 (lambda capture hazards): KILLED - competitors share weakness, subject handles better via DynamicBufferParam
- Test 11 (exception safety docs): SURVIVED at low-medium
- Test 24 (P2300 interop): KILLED - bidirectional bridges exist (`await_sender`, `as_sender`, `split_ec`) with published papers on the universal continuation model; reconnaissance missed example-directory evidence
- Test 36 (WolfSSL GPLv2): KILLED - survivorship bias, generic concern
- Test 37 (no security policy): KILLED - competitors share at this maturity level

**Coupling analysis:** No compound dynamics. Empty coupling map.

**Resolved assumptions (Phase 6, post-publication):**
- io_uring backend: planned, on the roadmap
- Sender/receiver interop: bidirectional bridges already exist in examples plus published papers on universal continuation model
- Specification assessment: skipped - D4003 is self-authored
- Production users: a derivatives exchange is porting its production stack to Corosio; published paper covers it

**Deviations:** None. All phases executed per pipeline specification.

---

## 8. References

### Primary Sources

1. GitHub: cppalliance/corosio - repository metadata, README, source code, CI configuration. https://github.com/cppalliance/corosio
2. GitHub: cppalliance/capy - repository metadata, README, source code, CI configuration, documentation. https://github.com/cppalliance/capy
3. Capy README: Peter Dimov quotation on coroutine-native API design.
4. Corosio README: project description and positioning statement.
5. D4003: IoAwaitable concepts paper. https://github.com/cppalliance/wg21-papers/blob/master/source/d4003-io-awaitables.md
6. CI compiler matrices: `.github/compilers.json` from both repositories.
7. Capy Antora documentation and Javadoc API reference.
8. Corosio Antora documentation and Javadoc API reference.
9. Corosio benchmark suite: `perf/bench/` (10 comparative benchmarks vs Asio) and `perf/profile/` (5 profiling benchmarks).
10. Corosio commit history: 7 contributors, 265 commits from vinniefalco, 162 from sgerbino, 42 from mvandeberg. Most recent commit: 2026-04-30.
11. Capy commit history: 10 contributors, 307 commits from vinniefalco, 49 from mvandeberg, 48 from sgerbino. Most recent commit: 2026-04-30.
12. P4100R1: "Coroutine-Native I/O for C++29 (The Network Endeavor)" (Vinnie Falco, Steve Gerbino, Michael Vandeberg, Mungo Gill, Mohammad Nejati, 2026). https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2026/p4100r0.pdf - Documents the 14-paper series, three-layer architecture, independent adopters (MySQL, Redis, Postgres), and derivatives exchange field experience.
13. User testimony: io_uring backend is planned. 2026-04-30.
14. P4125R0: "Field Report: Coroutine-Native I/O at a Derivatives Exchange" (Vinnie Falco, 2026). https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2026/p4125r0.pdf
15. P4088R0: "What C++20 Coroutines Already Buy The Standard" (Vinnie Falco, 2026). https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2026/p4088r0.pdf - Traces the five coroutine properties that enable structural type erasure, zero per-operation allocation, and ABI-stable I/O.
16. P4092R0: "Consuming Senders from Coroutine-Native Code" (Vinnie Falco, Steve Gerbino, 2026); P4093R0: "Producing Senders from Coroutine-Native Code" (Vinnie Falco, Steve Gerbino, 2026); P4126R0: "A Universal Continuation Model" (Vinnie Falco, Klemens Morgenstern, 2026). Three published WG21 papers documenting the bidirectional IoAwaitable/sender bridge.
17. Capy design rationale corpus: 13 documents in `doc/` covering buffer representation, buffer sequences, buffer passing, combinator gap analysis, combinator specification, continuation type, executor transfer, read_some postconditions, sender channels, system executor, and work counting. Documents record consensus decisions between Vinnie Falco, Peter Dimov, and Andrzej Krzemienski, with several targeting LEWG review.

---

### Design Theory

Abrahams, D. "Exception Safety in Generic Components." In *Generic Programming: International Seminar on Generic Programming*, Dagstuhl Castle, Germany, 2001.

Lakos, J. *Large-Scale C++ Software Design.* Addison-Wesley, 1996.

Sutter, H. *Exceptional C++: 47 Engineering Puzzles, Programming Problems, and Solutions.* Addison-Wesley, 1999.

---

*April 2026 - claude-4.6-opus*
