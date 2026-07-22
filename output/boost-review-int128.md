# Boost Review: Int128

A portable, exactly-16-byte 128-bit integer that behaves like a built-in and runs on the platforms the compilers forgot.

Boost.Int128 provides two concrete types, `int128_t` and `uint128_t`, fixed at `sizeof == 16` on every platform as two 64-bit limbs. It forwards to native `__int128` or MSVC intrinsics where they exist and drops to an optimized software path where they do not (MSVC, 32-bit, GPU SPIR), so the same code compiles and runs across CPU and CUDA/SYCL device targets. Around the two types it layers the standard-library facilities a built-in integer already participates in: `numeric_limits`, `<bit>`, `<charconv>`, `std::hash`, `std::format`, `<numeric>`, iostream, and user-defined literals. The audience is anyone who needs a dependable 128-bit scalar - 64x64 products, decimal and fixed-point money, UUID/IPv6, crypto, wide PRNG state - and cannot rely on `__int128` because their target set includes Windows, 32-bit, or a GPU.

## About Matt Borland

Matt Borland is a Staff Engineer at The C++ Alliance, a role he has held since January 2023 and full-time since mid-2024. His body of work sits squarely in the numerics corner of Boost: he is the author of Boost.Charconv (accepted, Boost 1.85), co-author with Christopher Kormanyos of Boost.Decimal (accepted after two review cycles, Boost 1.91), and a maintainer of Boost.Math and Boost.Multiprecision. Int128 is therefore the fourth numerics library he has shepherded through the Boost ecosystem, and the domain overlap is direct: he already maintains the library (Multiprecision) whose fixed-width 128-bit backend Int128 competes with, and he authored the decimal library that consumes Int128 as its arithmetic engine.

He also works the other side of the review table. He is a recurring Boost review manager (he managed the Boost.Multi review in 2026), so he arrives at his own review knowing what the process rewards and punishes. Open Hub records roughly 3,300 Boost commits since 2020, and the Int128 repository shows about 1,756 of his commits with the most recent landing the day before this review opened.

Two negatives are worth stating plainly. No WG21 papers appear under his name, and no CppCon or C++Now talks surfaced in search. His reputation is built through shipped, accepted libraries rather than the committee-and-conference circuit, and his personal following is modest. That is a builder's profile, not a public figure's. His co-author on Decimal, Christopher Kormanyos, contributes the differential fuzzing harness here; Kormanyos wrote the Springer text "Real-Time C++" and the `wide-integer` library, and is a domain-appropriate second set of eyes even though he is not listed as an Int128 author.

## Structure

Header-only, with zero `.cpp` files under `include/`: 15 public headers in `include/boost/int128/`, 16 detail headers, and the umbrella `include/boost/int128.hpp`. The core is two hand-written concrete structs rather than a template, with templates confined to mixed-type conversion and the optional integrations. The library builds with both CMake (an `INTERFACE` target pinned to `cxx_std_14`) and B2, ships a C++20 named module (`module/int128.cppm`), and carries vcpkg port files. The core umbrella has no Boost dependencies and pulls only `<cstdint>`, `<cstring>`, `<cassert>`, and platform intrinsics; the heavier headers opt into Boost.Charconv, Boost.Core, boost::random traits, and `{fmt}` only when included. Tests use Boost.Core `lightweight_test` plus custom CUDA/SYCL harnesses, driven through CI on GitHub Actions (ci, codecov, fuzz, qemu) and Drone. Five user-facing configuration macros gate CUDA, SYCL, the software fallback, exception suppression, and the module build; all default off or auto. The layout is standard Boost plus the expected extensions for a GPU-aware, module-shipping library.

## API

The surface is coherent and small at its center. Two value types carry the full operator set - arithmetic, bitwise, comparison, shift, compound assignment, cross-type conversions - and everything is `constexpr noexcept HOST_DEVICE`. Around them sit thin, single-purpose headers that each mirror one standard facility: `bit.hpp` reproduces `<bit>` on `uint128_t` (`popcount`, `countl_zero`, `bit_width`, `rotl`, `byteswap`), `numeric.hpp` reproduces `<numeric>` including the C++26 saturating set and `saturate_cast`, `utilities.hpp` adds the C23 checked-arithmetic analogues (`ckd_add`/`ckd_sub`/`ckd_mul`) plus `powm`/`ipow`/`isqrt`, and `charconv`, `format`, `fmt_format`, `hash`, `iostream`, `limits`, and `literals` each wire the types into their respective standard machinery. The simple path is `#include <boost/int128.hpp>` and use the type like an `int`; the 39-line `examples/rollover.cpp` is representative.

The types are the standout: two POD-like structs whose entire design goal is to be indistinguishable from a built-in integer in generic code. The cohesion is real - no header is an outlier, and the umbrella deliberately excludes the three heaviest integrations (charconv, fmt_format, random) to keep the common include cheap.

## Documentation

The documentation is a mature Antora site, and it is better than most candidate libraries bring to review. It has all three pillars a reviewer checks for: a getting-started guide that covers umbrella-versus-opt-in headers and every build mode (CMake, B2, module, CUDA, SYCL); a reference with per-header feature pages and unusually deep per-type pages (`int128_t.adoc` and `uint128_t.adoc` document limb layout, the 32-bit x86 alignment exception, `INT128_MIN` negation, float-conversion edges, and the `numeric_limits` tables); and a conceptual layer in `overview.adoc`, `design.adoc`, and `comp_to_multiprecision.adoc`. The `examples.adoc` page is the strongest single asset - 15-plus runnable programs with expected output and pitfall notes - and functions as a tutorial rather than a symbol dump.

The gaps are specific and they cluster on behavior rather than coverage. Divide and modulo by zero return `{0,0}`, but that contract is stated only as a cross-reference from `powm`; a reader on the `operator/`, `operator%`, or `div()` pages never learns it. Narrowing conversions keep only the low 64 bits, and that silent truncation is nowhere spelled out, nor are the checked alternatives (`saturate_cast`, `ckd_*`) cross-linked as the safe path. The two-tier string and I/O story is invisible: nothing explains that `to_string`, streams, and `std::format` route through an internal mini-charconv while `charconv.adoc` documents the optional Boost.Charconv integration, so a user cannot tell which to reach for, at which bases, on which targets. And there is no positioning against `_BitInt(128)` or a future `std::int128_t`, and no Abseil contrast even though Abseil sits in the benchmark tables. Public headers carry essentially no inline doc comments and the README is a CI-badge stub, but the hosted site carries the weight, so neither hurts coverage. Verdict: well-documented on structure, partially documented on hazardous semantics.

## Landscape

### Competitors

- Compiler builtin `__int128` / `unsigned __int128` (GCC/Clang/ICC): native codegen, zero install, and the only option that is a true `is_integral` integral type. Absent on MSVC and all 32-bit targets.
- `absl::int128` / `absl::uint128` (Abseil): Google-scale adoption, portable class type across GCC/Clang/MSVC. Explicit-only conversions, no literals, `is_integral` is false, no GPU path, pulls the Abseil dependency.
- Boost.Multiprecision `int128_t` / `uint128_t`: ships in every Boost, mature, and the same backend scales past 128 bits. Sign-magnitude (so `min == -max`), `sizeof > 16`, and the benchmark loser on general-purpose overhead.
- ckormanyos `wide-integer` (`uintwide_t`): arbitrary width, fully `constexpr`, bare-metal friendly. Generic rather than tuned for exactly 128 bits, limited std interop, no CUDA focus.
- MSVC `std::_Signed128` / `_Unsigned128`: ships in the MSVC STL. Internal, undocumented, and the maintainers refuse trait specialization - not a public API to depend on.

### The Space

Fixed-width 128-bit integers are a long-standing, well-understood need with no portable standard type to fill it. The landscape is fragmented by platform: native `__int128` on 64-bit GCC/Clang, nothing usable on MSVC, and heavier library types everywhere else. Standardization is converging on C23's `_BitInt(N)`, which P3666 is carrying toward C++29, while the single-width `std::int_least128_t` proposal (P3140) was withdrawn. But `_BitInt` is deliberately kept out of most of the standard library, and MSVC supports neither `_BitInt` nor `__int128`, so a portable, std-integrated library type stays relevant for years. Peer languages already shipped the feature (Rust `i128`, C# `Int128`, Swift SE-0425), which is independent confirmation of demand.

### Positioning

Int128 owns a precise niche: the portable, exactly-16-byte, two's-complement, GPU-capable, fully std-integrated 128-bit class type. No single competitor covers that combination (high confidence). Its weakest flank is the platform where most C++ is written - 64-bit GCC/Clang, where `__int128` is already native and is a real integral type, shrinking Int128's marginal value to its I/O and std-integration helpers (high confidence). Its strongest case is MSVC, 32-bit, and GPU, plus service as a uniform cross-platform backend, which is exactly why Boost.Decimal adopted it (medium-high confidence).

## Key Claims

1. Exactly 16 bytes on every platform. Evidence: two-limb layout in `detail/uint128_imp.hpp`, contrasted in `design.adoc` with Multiprecision's extra bookkeeping word. Confidence: high.
2. Portable where `__int128` is absent (MSVC, 32-bit, GPU). Evidence: intrinsic-with-software-fallback documented in `design.adoc`, with the `BOOST_INT128_NO_BUILTIN_INT128` opt-out. Confidence: high.
3. Near-native performance on 64-bit hosts. Evidence: benchmark pages show `uint128_t` addition at 241336 us vs `__int128` at 242772 us over 20M ops on Linux x64. Confidence: medium (near-parity on basic ops; division and modulo often trail native, and Abseil/`__int128` win some ops).
4. Large wins over Boost.Multiprecision on native-less targets. Evidence: `u128_benchmarks.adoc` reports roughly 10x on Linux x86_32 addition and 22x on Windows x64; `i128_benchmarks.adoc` reports about 44x on Windows ARM64 multiplication. Confidence: high (measured, in-repo).
5. Broader std integration than `__int128` or Abseil. Evidence: `numeric_limits`, `<bit>`, `<charconv>`, `std::hash`, `std::format`, `<numeric>`, iostream, literals, and a C++20 module. Confidence: high.
6. CUDA/SYCL device support. Evidence: `BOOST_INT128_HOST_DEVICE` on the core surface plus `examples/cuda.cu` and `examples/sycl.cpp`; no surveyed competitor offers this. Confidence: high.

Flagged as unsupported in-repo: the "module weight 5 vs 25" figure is cited only via an external link, not measured here; "extremely lightweight" has no compile-time or object-size study; the docs title says "Performant" while the benchmarks show the builtin winning some operations on native platforms.

## Findings

Int128 is a strong candidate. Eight of eleven principles pass, three are concerns, and none is a red-flag. The passes are not marginal, and several carry high confidence. The three concerns are coherent rather than scattered - two of them (safe-defaults, doc-rationale) are the same underlying issue seen from two angles, namely that the library's most contested behaviors are both under-justified and under-documented, and the third (field-experience) is the familiar problem of a new library whose only serious consumer shares its author.

### Scope Coherence

Pass (confidence: high). The name maps exactly onto the deliverable - two types, `int128_t` and `uint128_t`, fixed at 16 bytes, nothing unrelated bundled. The feature headers are not scope creep; each mirrors a standard facility a built-in integer already participates in, unified by the documented "behave like a built-in integer" anchor, with the heaviest integrations kept opt-in and out of the umbrella. The two-type footprint clears the standalone-value bar on the strength of its use as the Boost.Decimal backend. The only residual is a missing "use Multiprecision beyond 128 bits" boundary note, which is a documentation nit.

### Documentation Rationale

Concern (confidence: high). The core positioning is argued well - `design.adoc` defends the exact-16-byte layout against Multiprecision and the intrinsic-with-fallback strategy, and `comp_to_multiprecision.adoc` makes the purpose-built case. Rationale then degrades on exactly the decisions a reviewer probes. The `{0,0}` divide-by-zero result is justified only by cross-reference from `powm`. The implicit-conversion model is asserted as built-in parity with no engagement of Abseil's deliberate opposite choice, despite Abseil sitting in the benchmark tables. And there is no positioning against `_BitInt(128)` or a future `std::int128_t`. The anchor argument slides from reasoning into bare assertion at the edges.

### Safe Defaults

Concern (confidence: medium). Two defaults avoid undefined behavior but trade away error visibility. Division or modulo by zero returns a sentinel rather than trapping:

```cpp
int128_t{5} / int128_t{0};   // -> {0, 0}, no throw, no trap, no UB
```

That is safer than the builtin, where division by zero is UB and usually SIGFPE, but it silently swallows a logic error and is undocumented for `operator/`, `operator%`, and `div()`. Narrowing keeps only the low limb:

```cpp
static_cast<int64_t>(x);     // keeps x.low, drops x.high silently
```

which matches built-in conversion semantics but drops data without a diagnostic, while the checked routes (`saturate_cast`, `ckd_*`, `*_sat`) exist yet are opt-in and not cross-linked as the safe path. The wrap-on-overflow default is conventional and actually safer than built-in signed overflow, so the concern is scoped to the two silent-error paths, not the arithmetic model.

### API Complexity

Pass (confidence: medium). The common case is about as simple as the domain allows: two concrete types, no template parameters, built-in-integer semantics through implicit conversions, one umbrella header, and a 39-line worst-case example. Complexity is correctly reserved for advanced use behind default-off macros. The one place the "multiple mechanisms without guidance" indicator bites is string and I/O conversion, where `to_string`, streams, `std::format`, `{fmt}`, an internal mini-charconv, and optional Boost.Charconv overlap with no selection guidance.

### Real-World Demand

Pass (confidence: medium). The underlying need is real and peer-validated (Rust, C#, Swift all shipped it), and genuine unmet demand is concentrated in the portability gap on MSVC, 32-bit, and GPU. On the dominant 64-bit GCC/Clang platform, `__int128` already satisfies most of the need, and demonstrated pull toward this specific library is thin: external adoption is near-zero and the one demanding consumer, Boost.Decimal, is same-org. The demand for the functionality is established; the demand for a new Boost library rests on the portability niche rather than observed independent uptake.

### Maintainer Responsiveness

Pass (confidence: high). A paid full-time C++ Alliance maintainer with sub-day issue turnaround, a near-empty backlog (1 open issue), and active hardening in the days before the review satisfies every positive indicator. Issues like "Module support has rotted" and "Add SYCL support" were opened and closed within a day. The single-human bus factor is the only structural caveat, partially offset by institutional backing, and the review period being concurrent means window responsiveness cannot yet be observed directly.

### Documentation Completeness

Pass (confidence: high). All three pillars - reference, tutorial, conceptual overview - are present and above the level that sank historical rejections like Multi, Fit, and Timsort. The "partially documented" verdict is driven by behavior-specification gaps (div-by-zero, narrowing) and one real navigation gap (which string/IO path to use), not by any missing section.

### Exception Safety

Pass (confidence: high). The value types are trivially destructible with no owned resources, and every mutating operation is `constexpr noexcept`, so the nothrow guarantee holds by construction and no exception can corrupt state. The throwing surface is narrow and mostly non-umbrella: `to_string` allocation, stream extraction, and the formatters on a bad spec. The only shortfall is documentary - guarantees live in the `noexcept` specifiers rather than being stated per operation, which one sentence would close.

### Std Consistency

Pass (confidence: high). The library mirrors an unusually broad slice of the standard library using conforming names and the correct customization points - `numeric_limits`, `<bit>`, `<charconv>`, `std::hash`, `std::formatter`, the C++26 saturating set, C23 checked arithmetic, iostream, and UDLs - so the types drop into unordered containers, `std::format`, and generic numeric code without adaptation. The one real deviation, that a class type cannot make `std::is_integral` true while builtin `__int128` can, is a hard language constraint shared by every class-type competitor, not a design fault. It is, however, undocumented.

### Resource Ownership

Pass (confidence: high). Not really applicable: `int128_t` and `uint128_t` are two-limb value types with no pointers, handles, or heap, so use-after-free, dangling, and unbounded-growth modes structurally cannot arise. The only allocation is `to_string` returning a `std::string` by value; charconv writes into caller-owned buffers. No instance shares hidden state with another.

### Field Experience

Concern (confidence: medium). The only substantial consumer is Boost.Decimal, which uses Int128 as its arithmetic backend and reportedly surfaced bugs, drove performance work, and forced a 256-bit spinoff - real exercise of the API, but same author and same organization, so it is in-house dogfooding rather than independent field experience. Third-party signals are effectively nil: roughly a dozen stars, no external dependents, blog posts, or talks, and the wide-integer fuzzing is a test harness, not deployment. The library arrives at review with strong dogfooding and no evidence of use outside the author's orbit.

## Questions for the Reader

1. Is returning `{0,0}` from `operator/`, `operator%`, and `div()` on a zero divisor the right contract for a Boost integer type? It trades the builtin's loud failure (UB, usually SIGFPE) for a silent, plausible-looking zero. If the motivation is keeping operators total on `constexpr` and `HOST_DEVICE` paths where throw and trap are unavailable, is that trade-off worth making the default, and why is it documented only for `powm`?

2. Should the default narrowing conversion, which keeps only the low 64 bits, be diagnosable or steer users toward `saturate_cast` / `ckd_*`? A `static_cast<int64_t>(x)` that drops a nonzero high limb without a diagnostic is built-in parity, but is that the right choice for a library that otherwise markets safety.

3. On 64-bit GCC/Clang, where `__int128` is native and is a true `is_integral` type, is Int128's std-integration and exact-layout bundle enough to justify adoption over the builtin plus a few helpers? How large is the MSVC/32-bit/GPU segment where Int128 is uniquely needed, relative to that majority?

4. Beyond same-org Boost.Decimal, is there any external or committed-adopter demand - users blocked today on the MSVC/32-bit/GPU gap who are waiting on Boost acceptance? Did the Boost.Decimal integration involve any contributors outside the author's immediate team?

5. Is fixed-exactly-128 the right scope, or should the library document a path to 256-bit (already spun off privately for Decimal) and a clear boundary for when to graduate to Multiprecision?

6. How much should a Boost integer library's evaluation weight CUDA/SYCL support, and does device-side 128-bit performance matter in practice beyond the correctness demos in `examples/cuda.cu`?

7. Given C23 `_BitInt(N)` and P3666 heading toward C++29, how should the library position itself against a future standard type, and what is the migration story if `std::int128_t` arrives?

## Recommendations

- Document the divide/modulo-by-zero `{0,0}` contract on the `operator/`, `operator%`, and `div()` reference pages, and state the rationale (total-function semantics for constexpr/GPU) in `design.adoc`.
- Document silent low-limb narrowing on the conversion pages and cross-link `saturate_cast` and `ckd_*` as the checked path.
- Add a short "which string/IO path" guide covering `to_string` vs streams vs `std::format` vs `{fmt}` vs Boost.Charconv, with supported bases and GPU availability.
- Add positioning against `_BitInt(128)` / future `std::int128_t` and an Abseil explicit-conversion contrast, since both already appear implicitly (P3666-era direction; Abseil in the benchmarks).
- State a scope boundary: when values may exceed 128 bits, direct users to Multiprecision, and note whether a 256-bit type is on the roadmap.
- State exception-safety guarantees in one place, enumerating the throwing operations, to convert an implicit `noexcept`-by-signature story into a documented one.
- Surface any independent adopters during the review; the functionality's demand is established, but this library's field experience outside the C++ Alliance is the thinnest part of the case.

*2026-07-22 - Boost Review pipeline (boost-review.md), synthesis model claude-opus-4.8*
