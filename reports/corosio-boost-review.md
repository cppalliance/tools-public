# Boost Review: Corosio + Capy

A coroutine-native networking stack and its I/O foundation layer, submitted as a single unit.

Corosio and Capy are a two-library stack that replaces twenty years of callback-based async I/O with a coroutine-first design built on C++20 concepts. Capy provides the foundation - executor model, task types, IoAwaitable protocol, buffer sequences, stream abstractions, cancellation, composition primitives, and testing infrastructure - with zero external dependencies beyond the C++20 standard library. Corosio provides the networking layer - TCP/UDP sockets, TLS streams (OpenSSL + wolfSSL), DNS resolution, timers, signals, file I/O - built exclusively on Capy's abstractions. The dependency direction is strict and acyclic. The stack is positioned as the successor to Boost.Asio and targets WG21 standardization through a 14-paper series (P4100R1, "The Network Endeavor"). Three independent Boost library authors have adopted the stack (MySQL, Redis, Postgres), and a derivatives exchange is porting production trading infrastructure to it.

## About Vinnie Falco

Vinnie Falco is the author of Boost.Beast (HTTP/WebSocket, accepted 2018) and Boost.JSON (accepted 2020), both widely used Boost libraries in the networking and data interchange domains. He maintains both and is a regular contributor to the C++ Alliance's open-source efforts. His WG21 participation spans approximately 40 published papers across the April, May, and July 2026 mailings, covering IoAwaitable concepts (P4003R1), coroutine-native I/O design rationale (P4172R0), what coroutines buy the standard (P4088R0), sender/receiver bridges (P4092R0, P4093R0), universal continuation models (P4126R0, with Klemens Morgenstern), the Network Endeavor roadmap (P4100R1), and field experience from a derivatives exchange (P4125R0). Additional papers address coroutine executor semantics (P4096), networking claims surveys (P4098R0), the cost of sender unification (P4094R0), and combinators for I/O (P4124R0).

Falco's professional background is in financial technology, where he built the networking stack for a cryptocurrency exchange that ran Boost.Beast in production. The Corosio/Capy effort represents a ground-up redesign informed by that production experience and by Peter Dimov's observation that "an API designed from the ground up to use C++20 coroutines can achieve performance and ergonomics which cannot otherwise be obtained." The design rationale corpus (13 documents covering buffers, executors, combinators, continuations, and stream postconditions) records consensus decisions between Falco, Peter Dimov, and Andrzej Krzemienski.

Co-maintainers Steve Gerbino (210 commits) and Michael Vandeberg (91 commits) are active across both repositories. Ten additional contributors appear in the commit history.

## Structure

Capy is a header-only C++20 library with separately compilable source files. Approximately 85 public headers live under `include/boost/capy/`. The library uses dual build systems: CMake (with presets) and B2 (Jamfile). Tests use a custom lightweight test framework (`test_suite.hpp`). The only dependency is the C++20 standard library. Configuration macros are minimal.

Corosio is also header-only with separately compilable source files. Approximately 30 public headers live under `include/boost/corosio/`. It depends on Capy plus platform I/O APIs (IOCP on Windows, epoll on Linux, kqueue on macOS/FreeBSD, select as fallback). TLS support optionally depends on OpenSSL or wolfSSL. Both CMake and B2 are supported.

The directory layout follows standard Boost conventions: `include/boost/{lib}/`, `src/`, `test/`, `example/`, `doc/`, with Corosio adding `perf/bench/` and `perf/profile/` for benchmarks.

## API

### Capy - Foundation Layer (~200 public symbols, 85 headers)

The API organizes into seven groups:

- **Core protocol**: `IoAwaitable` concept, `io_result<Ts...>` structured result type (supports structured bindings), `continuation` type for zero-allocation executor queuing
- **Task types**: `task<T>` (the workhorse coroutine type, one template parameter), `io_task` (type-erased task), `quitter<T>` (cancellation-aware task)
- **Execution**: `execution_context`, `thread_pool`, `strand` (serializing executor with 211 pooled implementations), `async_mutex`, `async_event`, `executor_ref` (non-owning), `any_executor` (owning via shared_ptr), `work_guard<E>`
- **Buffers**: `mutable_buffer`, `const_buffer`, `buffer_array<N>`, `buffer_pair`, `buffer_param` (windowed iterator for virtual dispatch), `slice_of<T>`, plus four `DynamicBuffer` implementations. Eight slice operations, `buffer_copy`, `buffer_size`, `make_buffer` factory. Asio interop via `buffers/asio.hpp`
- **Stream concepts**: `ReadStream`, `WriteStream`, `BufferSource` (pull model), `BufferSink` (callee-owns-buffers). Type-erased wrappers: `any_stream`, `any_read_stream`, `any_write_stream`
- **Combinators**: `when_all` (returns `io_result<R1,...,Rn>` with flat destructuring), `when_any` (returns `variant<error_code, R1,...,Rn>`), `delay`, `timeout`, `run` (cross-executor dispatch with `transfer_to` for strand safety)
- **Testing toolkit**: `fuse` (controlled failure injection), `bufgrind` (adversarial buffer testing), `mocket`/`socket_pair` (mock streams)
- **Memory**: `recycling_memory_resource` (frame allocator with thread-local recycling pool, zero steady-state allocations after warmup)

15 C++20 concepts constrain the API: `IoAwaitable`, `Executor`, `ExecutionContext`, `ReadStream`, `WriteStream`, `ConstBufferSequence`, `MutableBufferSequence`, `DynamicBuffer`, `DynamicBufferParam`, `BufferSource`, `BufferSink`, and buffer-specific refinements.

The standout abstraction is the IoAwaitable protocol. When a coroutine is launched with a designated executor, every child coroutine inherits executor affinity automatically through the `co_await` chain. The `task<T>` promise's `transform_awaitable` intercepts every `co_await` expression and injects the environment - executor reference, stop token, frame allocator - without user-written dispatch or transfer code. This makes incorrect executor resumption structurally impossible.

### Corosio - Networking Layer (~60 public symbols, 30 headers)

- **Sockets**: `tcp_socket`, `tcp_acceptor`, `tcp_server`, `udp_socket`, Unix domain sockets
- **TLS**: `tls_context`, `tls_stream` with portable abstraction over OpenSSL and wolfSSL backends
- **Infrastructure**: `timer`, `resolver`, `signal_set`, endpoint/address types (IPv4, IPv6)
- **File I/O**: `random_access_file`, `stream_file`
- **Execution context**: `io_context` (aliased to platform-appropriate backend)

Every I/O object exposes three API layers:

1. **Abstract** (`io_stream`, `io_read_stream`) - protocol-agnostic virtual dispatch, separately compilable, no platform headers
2. **Concrete** (`tcp_socket`, `timer`) - protocol-specific API, virtual dispatch, separately compilable
3. **Native** (`native_tcp_socket<Backend>`) - templated on platform backend, member function shadowing eliminates vtable

The simple case is simple:

```cpp
auto [ec, n] = co_await socket.read_some(buffer);
```

## Documentation

Both libraries ship Antora-based documentation sites with Javadoc-style API reference for all public types. Thread safety is documented per class with a systematic `@par Thread Safety` annotation applied consistently across both libraries.

The 13 design rationale documents in `capy/doc/` are unusually thorough. They cover buffer representation and ownership (tracing 25 years of Asio practice), buffer sequence theory, buffer passing conventions (recording ongoing Falco/Dimov debate), dynamic buffer lifetime semantics, combinator gap analysis (systematic comparison against P2300), combinator behavior specification (all 14 when_all and 10 when_any scenarios settled), continuation type design (why `continuation&` replaces raw `coroutine_handle<>`), executor transfer semantics (`transfer_to` for strand safety), `read_some` error postconditions (consensus between Dimov and Krzemienski on E2: error permits `n >= 0`), sender channel routing (the "I/O as complicated success" analysis for LEWG), system executor design options, and work-counting interface rationale. Each maps the design space, enumerates alternatives, records areas of agreement and disagreement, and states the chosen position.

The gap: exception safety guarantees (basic, strong, nothrow) are not documented per public operation. The thread safety model demonstrates the team's capacity for per-type documentation, but the exception safety equivalent is absent.

## Landscape

### Competitors

- **Boost.Asio** (BSL-1.0, ~21 years) - the incumbent. Multi-paradigm: callbacks, futures, coroutines via `use_awaitable`. C++20 coroutine support is retrofitted, not native.
- **Boost.Cobalt** (BSL-1.0, ~2.5 years) - coroutine-first primitives layered on Asio's executor and I/O infrastructure. Inherits Asio's dependency graph.
- **cppcoro** (MIT, ~9 years) - Lewis Baker's pioneering coroutine library. Effectively unmaintained since 2024. Windows-centric.
- **libunifex** (Apache-2.0, ~6.5 years) - Facebook's sender/receiver prototype. No networking.
- **async_simple** (Apache-2.0, ~4 years) - Alibaba's lightweight async framework. Networking only through Asio integration.
- **Async++** (MIT, ~4 years) - header-only coroutine building blocks with separate io_uring, curl, and gRPC wrappers.

### The Space

C++ asynchronous I/O and coroutine-based networking serves developers building server software, financial infrastructure, game servers, embedded networking, and cloud-native proxies. Five stress points define the domain: coroutine lifetime safety, zero-overhead I/O, cross-platform backend abstraction, structured cancellation propagation, and compilation cost discipline. Asio has been the de facto standard for twenty years, but its completion-handler model pre-dates C++20 coroutines.

### Positioning

Corosio+Capy hold nine features no surveyed competitor matches: the IoAwaitable concept protocol, the clean two-layer physical architecture, built-in mock socket and test infrastructure, a type-erased stream hierarchy with three API layers, a concept-constrained buffer type system with compile-time coroutine lifetime enforcement, a frame allocator achieving zero steady-state allocations, dual TLS backends, zero external dependencies from the foundation layer, and bidirectional P2300 sender/receiver bridges. (confidence: high)

One gap: Corosio uses epoll on Linux while Asio, libunifex, and Async++ support io_uring. An io_uring backend is planned. (confidence: high)

## Key Claims

1. **Coroutine-native, not retrofitted.** The entire stack is designed for C++20 coroutines from the ground up. No callback API, no completion tokens, no futures. Evidence: IoAwaitable protocol, `task<T>` with one template parameter, error_code-based return model. (confidence: high)

2. **Zero-dependency foundation.** Capy depends on nothing but the C++20 standard library. Evidence: verified - no Boost includes in Capy headers. (confidence: high)

3. **Structural type erasure with zero per-operation allocation.** Coroutine frames provide the type erasure that template-based designs build by hand. `any_stream` type-erases without per-operation allocation because operation state lives in the coroutine frame. Evidence: three-layer I/O object design, P4088R0. (confidence: high)

4. **Compile-time coroutine lifetime safety.** `DynamicBufferParam` prevents silent data loss from rvalue dynamic buffers in coroutines at compile time. Evidence: concept definition, buffer-rationale.md. (confidence: high)

5. **Bidirectional P2300 interoperability.** `await_sender()` consumes P2300 senders inside Capy coroutines; `as_sender()` presents IoAwaitables as P2300 senders; `split_ec()` adapts error_code returns for P2300's three-channel error model. Evidence: example implementations, three published WG21 papers (P4092R0, P4093R0, P4126R0). (confidence: high)

6. **Production adoption.** Three independent Boost library authors adopted the stack. A derivatives exchange is porting production infrastructure. Evidence: P4125R0, P4100R1. (confidence: high)

7. **Successor to Boost.Asio, targeting standardization.** 14-paper series spanning two stages. Stage One: pure C++20 abstractions with no platform dependency. Stage Two: platform I/O. Evidence: P4100R1, ~40 WG21 papers. (confidence: high)

## Findings

The library scores clean on ten of eleven principles. The single surviving concern - undocumented exception safety guarantees - is a documentation gap, not a design defect. The error_code-based I/O model structurally minimizes the exception surface. RAII coverage is complete. The testing infrastructure is unusually strong. The design rationale corpus is the most thorough this review has seen in a Boost submission.

### Scope Coherence

**pass** (confidence: high)

The two-library split is the key architectural property. Capy is the foundation; Corosio is the networking layer. The dependency direction is strict and acyclic. Every component serves a unified purpose. The 14-paper standardization strategy follows the same split. No unrelated components are bundled.

### Documentation Rationale

**pass** (confidence: high)

The 13 design rationale documents are the strongest rationale corpus this review has examined. Buffer representation (6 options analyzed), buffer passing conventions (live Falco/Dimov debate), DynamicBufferParam lifetime enforcement (3 options), buffer ownership models (3 options), continuation type (3 parameter-passing, 2 placement options), executor transfer semantics (`transfer_to` with 3 alternatives analyzed and rejected), read_some error postconditions (Dimov/Krzemienski consensus), combinator gap analysis (14+10 scenarios settled), sender channel routing for LEWG, system executor design, and work-counting interface. The ~40 published WG21 papers provide additional design justification.

### Safe Defaults

**pass** (confidence: high)

All I/O operations return `error_code` via `io_result`. `DynamicBufferParam` prevents silent data loss at compile time. `task<T>` automatically propagates executor affinity, stop tokens, and frame allocators. `work_guard<E>` pairs work-started/finished with RAII. RAII coverage is complete across both libraries. The `continuation` type eliminates raw `coroutine_handle<>` at the executor interface.

### API Complexity

**pass** (confidence: high)

`task<T>` has one template parameter. The three-layer I/O object design lets users choose complexity: `any_stream&` for simplicity, `tcp_socket` for the common case, `native_tcp_socket<Backend>` for zero overhead. Combinator return types are natural: `when_all` returns `io_result<R1,...,Rn>` with flat destructuring, `when_any` returns `variant<error_code, R1,...,Rn>`.

### Real-World Demand

**pass** (confidence: high)

Three independent Boost library authors adopted the stack (MySQL, Redis, Postgres). A derivatives exchange is porting production infrastructure (P4125R0). The SG4 networking mandate produced zero facilities in three years - demand for a working coroutine-native networking stack is well-documented.

### Maintainer Responsiveness

**pass** (confidence: high)

Three active maintainers (Falco 372, Gerbino 210, Vandeberg 91 combined commits). Ten additional contributors. CI covers GCC 12-15, Clang 17-20, MSVC 14.34-14.42, Apple Clang, MinGW, clang-cl across four platforms. Sanitizers, clang-tidy, and code coverage on every change.

### Documentation Completeness

**concern** (confidence: medium)

Extensive documentation (Antora sites, Javadoc API reference, 13 rationale documents, per-type thread safety annotations) but exception safety guarantees are not documented per public operation. The fix is documentation work, not redesign.

### Exception Safety

**concern** (confidence: low-medium)

Exception safety guarantees not documented per public mutating operation. The design structurally minimizes exceptions (error_code for I/O, exceptions only for precondition violations and allocation failure, centralized `detail::throw_*`). Practical posture appears sound but unverifiable without documentation. Does the team plan to add annotations before formal review?

### Standard Consistency

**pass** (confidence: high)

Integrates with `std::stop_token`, `std::error_code`/`std::error_condition`, `std::pmr::memory_resource`, tuple protocol for structured bindings. Asio buffer bridge exists. Where the library departs from Asio conventions (coroutine-only, no completion tokens), the departure is deliberate and justified.

### Resource Ownership

**pass** (confidence: high)

RAII coverage complete. `task<T>` and `quitter<T>` own coroutine frames. I/O objects close and cancel in destructors. Ownership communicated through type distinctions: `executor_ref` (non-owning) vs `any_executor` (owning). `continuation` documents its address-stability invariant.

### Field Experience

**pass** (confidence: high)

Three independent Boost library authors adopted the stack. Derivatives exchange porting production infrastructure (P4125R0). Peter Dimov co-designed the buffer system, combinator return types, and error postconditions. Design rationale documents record consensus from real deliberation.

## Questions for the Reader

1. The exception safety documentation gap is the single surviving concern. Is it serious enough to block acceptance, or is a commitment to add annotations before 1.0 sufficient?

2. `DynamicBufferParam` introduces a second concept to enforce compile-time lifetime safety. Peter Dimov has expressed discomfort with the two-concept split. Is the compile-time safety worth the additional concept?

3. The `tag_invoke` customization mechanism for buffer operations mirrors the P2300 ecosystem but WG21 has moved toward successor proposals. Is `tag_invoke` acceptable, or does it need replacement before standardization?

4. Peter Dimov's position on buffer slicing (in `buffers-peter.md`) proposes pushing offset/length parameters into `read_some`/`write_some`. The current design uses `buffer_param` and `consuming_buffers`. Does the committee have a preference?

5. The `read_some` error postcondition (E2: error permits `n >= 0`) departs from POSIX's deferred-error model. The rationale is thorough (Dimov/Krzemienski consensus). Is this the right choice for the standard?

6. The io_uring backend is planned but not implemented. Is this gap acceptable for Boost review given the clean platform backend abstraction?

7. The sender channels analysis argues I/O completions are "complicated success" and two of three P2300 channels are unused for I/O. The bidirectional bridges exist but the library is coroutine-native, not sender-native. Is this positioning acceptable?

## Recommendations

- Document exception safety guarantees per public mutating operation, following the thread safety annotation pattern. (high priority)
- Implement the io_uring backend for Linux before formal review. (high priority)
- Resolve the `DynamicBufferParam` two-concept question with Peter Dimov before submission. (medium priority)
- Consider replacing `tag_invoke` with a more modern customization mechanism before WG21 standardization. (medium priority)
- Publish benchmark results comparing Corosio against Asio. The 10 comparative benchmarks exist; making results publicly accessible strengthens the performance claim. (medium priority)
- Add a migration guide from Boost.Asio to Corosio. (low priority)

---

*April 2026 - Generated following the boost-review pipeline. Sources: both GitHub repositories, 13 design rationale documents, existing library review, ~40 WG21 papers from wg21-papers/source, user-provided context (io_uring planned, P2300 bridges in examples, production adoption).*
