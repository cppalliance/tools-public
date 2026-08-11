---
description: Reference for a model writing or maintaining C++ - project layout, naming, headers, RAII, smart pointers, error handling, modern features, templates, concurrency, testing, tooling, and performance
---

<!-- Load this file into context before writing or reviewing C++. Highest-value reference only; consult cppreference.com for depth. -->

# Rulebook: Writing C++

This file equips a model to write, extend, and maintain C++. Read the preamble and the closing rules first; they bind every edit. Sections run from most to least frequently needed and are consulted one at a time, so the length of this file is never the number of rules you hold at once. Terms used throughout: "the project" is the repository, "a target" is one buildable artifact, "a translation unit" is one `.cpp` file after preprocessing. Target C++20 as the baseline, with C++23 and C++26 features noted where they improve safety or clarity.

![The C++ Workshop](images/cpp-rulebook.png)

## Non-negotiable rules

Follow these on every change; they are restated at the end.

- Always initialize every variable at the point of declaration (section 3); an uninitialized read is undefined behavior that the compiler may silently exploit.
- Never use raw `new`/`delete` in application code; use smart pointers and RAII wrappers (section 5); a manual delete is a leak, double-free, or exception-safety hole waiting to happen.
- Make ownership explicit in every API using `unique_ptr`, `shared_ptr`, references, and `span` (section 5); ambiguous ownership is the root cause of use-after-free, leaks, and data races.
- Mark every non-mutating member function `const` and every move operation `noexcept` (sections 4, 8); missing `const` cascades into callers, and a throwing move silently disables `std::vector` reallocation optimization.
- Run clang-format and clang-tidy before every commit (section 14); both questions are settled by the tool, not by taste.
- Run sanitizers (ASan + UBSan) in CI on every test run (section 14); undefined behavior that tests exercise but do not detect ships silently.
- Add a test in the same change as the code (section 14); a change without a test is incomplete, because nothing guards against regression.

## 1. Code organization and headers

A project layout that a reader can navigate in seconds removes friction from every later section.

- Use a standard project layout: `include/<project>/` for public headers, `src/` for sources and private headers, `tests/` for unit tests, `cmake/` for CMake modules.
- Place public headers in `include/<project>/header.h` so consumers write `#include <project/header.h>`; the namespace in the path prevents collisions.
- Keep private headers near implementation in `src/`; never let public headers include private ones.
- Use out-of-source builds; add `build/` to `.gitignore`.
- Break larger projects into logical modules mirroring directory structure; no circular dependencies between modules.
- Use `.cpp` for source files and `.h` for headers; `.h` is shareable with C, `.cpp` is unambiguous.
- Pair every `.cpp` with its `.h`; include the paired header first in the source file to catch hidden dependencies.
- Make headers self-contained: each header includes everything it needs to parse independently.
- Use `#pragma once` in all headers; note traditional `#define` guards as the portable alternative for library code targeting exotic compilers.
- Order includes in five groups separated by blank lines, alphabetical within each group: (1) paired header, (2) C system headers, (3) C++ standard headers, (4) other library headers, (5) project headers.
- Include what you use: every source file directly includes the headers providing symbols it uses; use the IWYU tool or clangd include-cleaner for enforcement.
- Use forward declarations to reduce compile times when only pointer or reference types are needed; never forward-declare from namespace `std`.
- Never place non-inline function definitions, non-const variable definitions, unnamed namespaces, or `using` directives in headers.
- Place all code in a project namespace; never `using namespace` at global scope in headers; terminate namespace closing braces with `// namespace name`.
- Give implementation-detail definitions in `.cpp` files internal linkage via unnamed namespace or `static`.
- Use lowercase filenames with underscores: `my_class.cpp`, `my_class.h`.

Project directory layout:

| Path | Contents |
|---|---|
| `include/<project>/` | public headers, installed with the library |
| `src/` | source files and private headers |
| `tests/` | unit tests and test utilities |
| `cmake/` | CMake modules and Find scripts |
| `docs/` | documentation |
| `build/` | out-of-source build directory (gitignored) |
| `CMakeLists.txt` | root build file |

Include ordering (all five groups in a `.cpp` file):

```cpp
// my_class.cpp
#include "project/my_class.h"    // 1. paired header

#include <sys/types.h>           // 2. C system headers

#include <string>                // 3. C++ standard headers
#include <vector>

#include <fmt/core.h>            // 4. other library headers

#include "project/config.h"      // 5. project headers
#include "project/utils.h"
```

Detect in existing code:

- a header missing `#pragma once` or include guard - compilation fails on double inclusion.
- `using namespace` at global scope in a header - pollutes every includer's namespace.
- a `.cpp` file that does not include its paired header first - hidden dependencies go undetected.
- a header that includes another header it does not directly need - over-inclusion slows builds.
- non-inline function definitions in a header - causes multiple-definition linker errors.

Corrections:

- `#include "myclass.h"` not first in `myclass.cpp` -> include paired header first - catches hidden dependencies.
- `using namespace std;` in header -> remove - pollutes every includer's namespace.
- header without `#pragma once` or include guard -> add `#pragma once`.
- forward declaration of `std::string` -> `#include <string>` - forward-declaring std is undefined behavior.
- file uses `std::vector` but does not include `<vector>` -> include directly - do not rely on transitive includes.

## 2. Naming and formatting

Naming follows the Google hybrid style. Formatting is settled by the tool.

- Use PascalCase for types (classes, structs, enums, concepts, typedefs): `MyClass`, `HttpClient`.
- Use PascalCase for functions and methods: `AddTableEntry()`, `GetSize()`.
- Use snake_case for variables, parameters, locals: `table_name`, `num_errors`.
- Class data members use snake_case with trailing underscore: `table_name_`; struct data members (no invariant) omit the underscore.
- Constants (constexpr or const with static storage duration) use leading `k` + PascalCase: `kDaysInAWeek`.
- Enumerators use `kEnumName` or PascalCase; never ALL_CAPS, which is reserved for macros.
- Macros use `ALL_CAPS_WITH_UNDERSCORES` with a project prefix: `MYPROJECT_ROUND(x)`.
- Never start a name with underscore followed by uppercase, or double underscore; these are reserved by the standard.
- Use descriptive names; make length proportional to scope; avoid abbreviations unfamiliar outside the project.
- Use lowercase filenames with underscores or dashes.
- Every project must have a `.clang-format` configuration file; pick a base style and never argue about formatting again.
- Use spaces only (no tabs); keep a consistent line limit (80 or 120 characters).
- Always use braces for control flow blocks, even single-statement bodies; missing braces cause dangling-else and misleading-indentation bugs.
- Use early exits and `continue` to reduce nesting.

| Item kind | Convention | Example |
|---|---|---|
| Types (classes, structs, enums, concepts) | `PascalCase` | `MyClass`, `HttpClient` |
| Functions and methods | `PascalCase` | `AddTableEntry()`, `GetSize()` |
| Variables, parameters, locals | `snake_case` | `table_name`, `num_errors` |
| Class data members | `snake_case_` (trailing underscore) | `table_name_`, `count_` |
| Struct data members (no invariant) | `snake_case` | `width`, `height` |
| Constants (constexpr/static const) | `k` + PascalCase | `kMaxRetries`, `kDaysInAWeek` |
| Enumerators | `k` + PascalCase or PascalCase | `kSuccess`, `kNotFound` |
| Macros | `ALL_CAPS` with project prefix | `MYPROJECT_ROUND(x)` |
| Namespaces | `snake_case` | `my_project` |
| Filenames | lowercase with underscores | `my_class.cpp` |

Detect in existing code:

- a type not in PascalCase, or a variable not in snake_case - naming inconsistency.
- an enumerator in ALL_CAPS - should be `kName` or PascalCase; ALL_CAPS is for macros.
- a name starting with underscore + uppercase or double underscore - reserved by the standard.
- a control flow block without braces - dangling-else and misleading-indentation bugs.
- no `.clang-format` file in the project root - formatting debates are unsettled.

Corrections:

- `int myVar` (camelCase variable) -> `int my_var` - snake_case for variables.
- `class my_class` (snake_case type) -> `class MyClass` - PascalCase for types.
- `enum Color { RED, GREEN, BLUE }` -> `enum class Color { kRed, kGreen, kBlue }` - scoped enum with proper naming.
- `void _helper()` (leading underscore) -> `void Helper()` or place in unnamed namespace.
- single-statement `if` without braces -> add braces.
- inconsistent formatting -> run clang-format.

## 3. Idioms and modern C++

Write code that reads as modern C++. Each rule below has a mechanical reason.

- Use `auto` by default for variable declarations (Almost Always Auto style); add qualifiers explicitly: `const auto&`, `auto*`, `auto&`.
- Use concepts to constrain `auto` in C++20: `std::integral auto count = Compute();`.
- Use `decltype(auto)` in forwarding code to preserve exact types and reference-ness.
- Use structured bindings for compound objects: `auto [key, value] = *it;`; use `const auto&` for read-only, `auto&` for mutation.
- Use `std::optional` when a value might be missing; prefer over null pointers and sentinel values.
- Use `std::variant` as type-safe replacement for unions; use `std::visit` for exhaustive processing.
- Use `std::string_view` for non-owning read-only string parameters; never store unless backing string persists.
- Use `std::span` for non-owning contiguous memory views; replaces pointer+size pairs.
- Use ranges and views for lazy, composable transformations; chain with the `|` pipe operator.
- Split long view chains (4+ adapters) into named views; be aware that `filter_view` caches `begin()`.
- Use concepts to constrain template parameters; prefer standard concepts from `<concepts>` before writing custom ones.
- Use `consteval` for values that must be computed at compile time; `constexpr` is permission, `consteval` is mandate.
- Use `constinit` for static/thread-local variables requiring compile-time initialization; eliminates the static initialization order fiasco.
- Use `if consteval` (C++23) instead of `std::is_constant_evaluated()`.
- Use `std::expected<T, E>` (C++23) for recoverable errors with a reason; zero overhead on the success path.
- Prefer `{}`-initialization; use `()` when `{}` would invoke an initializer_list constructor unexpectedly (e.g., `std::vector<int>{10}` creates a one-element vector).
- Always initialize at point of declaration; never introduce a variable before you have a value.
- Use immediately-invoked lambdas for complex initialization of `const` variables.
- Avoid macros: use `constexpr` for constants, inline/template functions for behavior, `enum class` for groups.
- Replace `NULL`/`0` with `nullptr`.
- Replace `typedef` with `using` alias declarations.

| Vocabulary type | Standard | Use when |
|---|---|---|
| `std::optional<T>` | C++17 | value might be absent, no error reason needed |
| `std::variant<Ts...>` | C++17 | type-safe union, exhaustive visitation |
| `std::string_view` | C++17 | non-owning read-only string parameter |
| `std::span<T>` | C++20 | non-owning contiguous memory view |
| `std::expected<T, E>` | C++23 | recoverable error with typed reason |
| `std::mdspan<T, Extents>` | C++23 | multidimensional non-owning view |

Structured bindings in range-for iteration:

```cpp
std::map<std::string, int> scores = GetScores();

for (const auto& [name, score] : scores) {
    fmt::print("{}: {}\n", name, score);
}

for (auto& [name, score] : scores) {
    score += 10;
}
```

Ranges pipeline:

```cpp
auto even_squares = numbers
    | std::views::filter([](int n) { return n % 2 == 0; })
    | std::views::transform([](int n) { return n * n; });

for (auto val : even_squares) {
    fmt::print("{}\n", val);
}
```

Immediately-invoked lambda for const initialization:

```cpp
const auto config = [&] {
    Config cfg;
    cfg.SetHost(host);
    cfg.SetPort(port);
    cfg.Validate();
    return cfg;
}();
```

Detect in existing code:

- `NULL` or `0` used as null pointer literal - use `nullptr`.
- `typedef` instead of `using` - `using` is clearer, especially with templates.
- `#define` for a constant or function-like macro where `constexpr`/inline would work.
- uninitialized variable followed by later assignment - initialize at declaration.
- `std::is_constant_evaluated()` instead of `if consteval` - use the C++23 syntax.
- raw pointer+size pair where `span` would work.
- `const std::string&` parameter where `std::string_view` would suffice.

Corrections:

- `int count = Compute();` -> `auto count = Compute();` or `std::integral auto count = Compute();`.
- `std::pair<std::string, int> p = ...;` -> `auto [key, value] = ...;` - structured binding.
- `const std::string& param` for non-owning read -> `std::string_view param`.
- `void Process(int* arr, size_t len)` -> `void Process(std::span<int> arr)`.
- `NULL` or `0` as null pointer -> `nullptr`.
- `typedef std::vector<int> IntVec;` -> `using IntVec = std::vector<int>;`.
- `#define PI 3.14159` -> `constexpr double kPi = 3.14159;`.
- `#define MAX(a, b) ((a) > (b) ? (a) : (b))` -> `constexpr auto Max(auto a, auto b) { return a > b ? a : b; }`.
- `int x; ... x = Compute();` -> `auto x = Compute();` - initialize at declaration.
- `if (std::is_constant_evaluated())` -> `if consteval` (C++23).
- raw for loop iterating a container -> range-based for or algorithm.

## 4. Functions and interfaces

A function is the primary unit of composition. Keep each one small, explicit, and honest about what it needs and what it returns.

- Package meaningful operations as named functions; factoring out common code makes it more readable and limits errors.
- Keep each function to a single logical operation; 1-5 lines is normal, roughly 60 lines is too long.
- Make interfaces explicit: don't control behavior through globals; avoid errno-style error reporting in new code.
- Use strong types instead of bare ints for distinct concepts; a `Width` and a `Height` cannot be accidentally swapped.
- State preconditions and postconditions; use C++26 contracts (`pre`/`post`/`contract_assert`) or GSL `Expects`/`Ensures`.
- Follow parameter passing conventions (see table below).
- Return values over output parameters; for multiple outputs, return a struct (preferred) or tuple.
- Keep function arguments to 4 or fewer; group related parameters into structs.
- Avoid adjacent parameters of the same type that can be swapped without a compiler warning.
- Use `std::span<T>` instead of pointer+size pairs.
- Declare functions `constexpr` when possible; it costs nothing at runtime and enables callers in constant expressions.
- Mark `noexcept` where appropriate: destructors, swap, move operations, default constructors.
- Prefer pure functions; they are easier to reason about, test, and parallelize.
- Use lambdas instead of `std::bind`; capture by reference for local use, by value for non-local use.
- Never return references or pointers to local objects; don't use `std::move` on a local return value, which inhibits RVO.
- Avoid `va_arg`; use variadic templates or `initializer_list`.
- Use `[[nodiscard]]` for important return values: error codes, resource handles, factory functions.
- For stable library ABI, consider the Pimpl idiom to decouple interface from implementation.

| Situation | Pass as | Example |
|---|---|---|
| Cheap to copy (int, double, pointer) | by value | `void Draw(Point p)` |
| Read-only, non-trivial type | `const T&` | `void Print(const std::string& s)` |
| In-out parameter | `T&` | `void Update(Widget& w)` |
| Will move from | `T&&` | `void Append(std::string&& s)` |
| Forwarding reference | `T&&` with `std::forward` | `template <typename T> void Wrap(T&& arg)` |

| Lambda context | Capture | Reason |
|---|---|---|
| Used locally, same scope | `[&]` | no lifetime risk, avoids copies |
| Stored, returned, or passed to another thread | `[=]` or named captures by value | outlives enclosing scope |
| Mixed | explicit captures: `[&local, shared_copy]` | clarity about what is borrowed vs owned |

Parameter passing - return struct vs output parameters:

```cpp
// bad: output parameters
void GetResult(int& out_x, int& out_y);

// good: return a struct
struct Point { int x; int y; };
Point GetResult();
```

Detect in existing code:

- output parameters where a return value would work.
- missing `noexcept` on destructors, swap, or move operations.
- `std::bind` usage - replace with lambda.
- `std::move` on a local variable in a return statement - inhibits RVO.
- function with more than 4 parameters - group into struct.
- adjacent parameters of the same type - easy to swap accidentally.

Corrections:

- `void Process(int* data, int count)` -> `void Process(std::span<int> data)`.
- `bool Configure(int a, int b, int c, int d, int e)` -> `bool Configure(const Config& cfg)`.
- `void GetResult(int& out_x, int& out_y)` -> `struct Point { int x, y; }; Point GetResult()`.
- `auto f = std::bind(&Foo::Bar, &foo, std::placeholders::_1)` -> `auto f = [&foo](auto x) { return foo.Bar(x); }`.
- `std::move(local_result)` in return statement -> return by value - move inhibits RVO.
- missing `[[nodiscard]]` on factory function or error-code-returning function -> add it.
- missing `noexcept` on move constructor/assignment -> add it.

## 5. Resource management

RAII is the foundation of C++ resource safety. Every resource - memory, files, sockets, locks, GPU buffers - is managed by an object whose destructor releases it.

- RAII: acquire in constructor, release in destructor; guarantees cleanup even when exceptions are thrown.
- Prefer scoped (stack) objects over heap allocation; use the heap only for dynamic lifetime, polymorphism, or objects too large for the stack.
- Never use raw `new`/`delete` in application code; immediately give explicit allocations to a smart pointer.
- Never use `malloc`/`free` in C++ code; they do not support construction/destruction.
- Use `std::unique_ptr` as the default smart pointer (zero overhead, exclusive ownership); create with `std::make_unique`.
- Use `std::shared_ptr` only for genuinely shared ownership; create with `std::make_shared`; never use for "I don't know who owns this."
- Use `std::weak_ptr` to break `shared_ptr` cycles; parent->child with `shared_ptr`, child->parent with `weak_ptr`.
- Pass smart pointers to functions only when the function participates in ownership; otherwise pass by reference or raw pointer.
- Pass `unique_ptr` by value to transfer ownership; pass `shared_ptr` by value to share ownership.
- Make ownership explicit in APIs: `unique_ptr` = exclusive, `shared_ptr` = shared, `T&` = borrowed non-nullable, `T*` = borrowed nullable, `span<T>` = viewing buffer.
- A raw pointer (`T*`) is non-owning by convention.
- Do not pass aliased smart pointer references into call trees that might reset them.

| Type | Ownership | Overhead | Use when |
|---|---|---|---|
| `std::unique_ptr<T>` | exclusive | zero vs raw pointer | default choice for heap allocation |
| `std::shared_ptr<T>` | shared (ref-counted) | atomic increment/decrement per copy | genuinely shared ownership |
| `std::weak_ptr<T>` | observing | lock() check before use | breaking cycles, optional back-references |
| raw `T*` | none (observer) | zero | non-owning nullable parameter |
| `T&` | none (observer) | zero | non-owning non-nullable parameter |

| Type in API | Meaning |
|---|---|
| `std::unique_ptr<T>` | caller transfers exclusive ownership |
| `std::shared_ptr<T>` | caller shares ownership |
| `T&` | borrowed, non-nullable, caller retains ownership |
| `T*` | borrowed, nullable, caller retains ownership |
| `std::span<T>` | borrowed view of contiguous buffer |
| `std::string_view` | borrowed view of string data |

RAII wrapper for a file handle:

```cpp
class FileHandle {
public:
    explicit FileHandle(const char* path)
        : handle_(std::fopen(path, "r")) {
        if (!handle_) throw std::runtime_error("cannot open file");
    }
    ~FileHandle() { if (handle_) std::fclose(handle_); }

    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;
    FileHandle(FileHandle&& other) noexcept : handle_(std::exchange(other.handle_, nullptr)) {}
    FileHandle& operator=(FileHandle&&) = delete;

    std::FILE* Get() const { return handle_; }
private:
    std::FILE* handle_;
};
```

Smart pointer parameter passing:

```cpp
// function participates in ownership - take smart pointer
void TakeOwnership(std::unique_ptr<Widget> w);
void ShareOwnership(std::shared_ptr<Widget> w);

// function just uses the object - take reference
void UseWidget(const Widget& w);
void MutateWidget(Widget& w);
```

Detect in existing code:

- raw `new` or `delete` in application code.
- `malloc`/`free` in C++ code.
- `shared_ptr` used where `unique_ptr` would suffice.
- smart pointer passed to function that doesn't participate in ownership.
- manual resource cleanup in multiple code paths instead of RAII.

Corrections:

- `Widget* w = new Widget();` -> `auto w = std::make_unique<Widget>();`.
- `delete ptr;` anywhere in application code -> use smart pointer instead.
- `void Process(std::shared_ptr<T> p)` when function just reads T -> `void Process(const T& t)`.
- `std::shared_ptr<T>` used for exclusive ownership -> `std::unique_ptr<T>`.
- `malloc`/`free` in C++ code -> smart pointers or containers.
- raw `new[]`/`delete[]` -> `std::vector<T>`.

## 6. Classes and object design

Use `struct` for passive data where all members vary independently; use `class` when there is an invariant to maintain.

- Use `struct` when all members vary independently (just data); use `class` when there is an invariant maintained by member functions.
- Make a function a member only if it needs direct access to the representation; prefer non-member non-friend functions.
- Minimize exposure: avoid trivial getters/setters that add no semantic value; avoid `protected` data.
- Rule of Zero: if your class does not directly manage a resource, declare no special member functions; compose from types like `unique_ptr`, `vector`, and `string`.
- Rule of Five: if you define or `=delete` any of copy/move/destructor, define or `=delete` them all; declaring a destructor suppresses implicit move generation.
- Constructors should create fully initialized objects (no two-phase init); throw if construction fails.
- Declare single-argument constructors `explicit` to prevent implicit conversions.
- Use in-class member initializers for constant initializers; prefer member initializer lists over assignment in constructor body.
- Initialize members in declaration order; the compiler initializes in declaration order regardless of the initializer list order.
- Base class destructor: public virtual or protected non-virtual; destructors must not throw.
- A copy should produce independent objects with same value; make move `noexcept`; handle self-assignment.
- Never call virtual functions in constructors or destructors; the call resolves to the current class, not the derived class.
- Use exactly one of `virtual`/`override`/`final` on virtual functions; prefer `override`.
- Use class hierarchies only for inherent hierarchy, not code reuse alone; prefer composition over inheritance.
- Suppress public copy/move on polymorphic classes to prevent slicing.
- Prefer `enum class` over plain `enum`; scoped enums prevent implicit conversions and namespace pollution.
- Avoid implicit conversion operators; use `explicit`.
- Objects with static storage duration should be trivially destructible or use `constexpr`/`constinit`.
- Avoid singletons (complicated globals in disguise); avoid non-const global variables (hidden dependencies, data races).
- Avoid God Objects (split responsibilities into focused classes); avoid Poltergeist classes (unnecessary intermediaries).

| Special member | Default when | Delete when | Implement when |
|---|---|---|---|
| Destructor | Rule of Zero (no resource) | never | class directly manages a resource |
| Copy constructor | Rule of Zero | move-only semantics needed | deep copy of managed resource |
| Copy assignment | Rule of Zero | move-only semantics needed | deep copy of managed resource |
| Move constructor | Rule of Zero | immovable type | resource transfer from managed resource |
| Move assignment | Rule of Zero | immovable type | resource transfer from managed resource |

| Condition | Use |
|---|---|
| All members vary independently, no invariant | `struct` with public members |
| Class maintains an invariant | `class` with private data and public interface |
| Polymorphic base | `class` with virtual destructor |

Rule of Zero - class composed from RAII types:

```cpp
class Document {
    std::string title_;
    std::vector<Page> pages_;
    std::unique_ptr<Metadata> meta_;
public:
    Document(std::string title, std::unique_ptr<Metadata> meta)
        : title_(std::move(title)), meta_(std::move(meta)) {}
    // No destructor, copy, or move declarations needed.
};
```

Rule of Five - class managing a raw resource:

```cpp
class Buffer {
    int* data_;
    size_t size_;
public:
    explicit Buffer(size_t n) : data_(new int[n]()), size_(n) {}
    ~Buffer() { delete[] data_; }
    Buffer(const Buffer& other) : data_(new int[other.size_]), size_(other.size_) {
        std::copy_n(other.data_, size_, data_);
    }
    Buffer& operator=(const Buffer& other) {
        Buffer tmp(other);
        swap(tmp);
        return *this;
    }
    Buffer(Buffer&& other) noexcept : data_(std::exchange(other.data_, nullptr)), size_(std::exchange(other.size_, 0)) {}
    Buffer& operator=(Buffer&& other) noexcept {
        Buffer tmp(std::move(other));
        swap(tmp);
        return *this;
    }
    void swap(Buffer& other) noexcept { std::swap(data_, other.data_); std::swap(size_, other.size_); }
};
```

Enum class with proper naming:

```cpp
enum class Color { kRed, kGreen, kBlue };
enum class HttpStatus { kOk = 200, kNotFound = 404, kServerError = 500 };
```

Detect in existing code:

- a class with a user-declared destructor but no copy/move declarations - apply Rule of Five.
- a single-argument constructor without `explicit` - allows implicit conversions.
- `virtual` combined with `override` on the same function - redundant, use only `override`.
- virtual function calls in constructors or destructors - resolves to current class, not derived.
- plain `enum` where `enum class` would work - leaks names into enclosing scope.
- a class with >10 member functions or >10 data members - potential God Object.

Corrections:

- class with destructor but no copy/move declarations -> apply Rule of Five (`=default` or `=delete` all).
- `Foo(int x)` without explicit -> `explicit Foo(int x)`.
- `virtual void Draw() override` -> `void Draw() override` - don't combine virtual and override.
- assignment in constructor body -> member initializer list.
- `enum Color { Red, Green, Blue }` -> `enum class Color { kRed, kGreen, kBlue }`.
- God object class doing everything -> split into focused classes with single responsibilities.

## 7. Error handling and exception safety

Develop an error-handling strategy early. Consistency within a module matters more than picking one mechanism globally.

- Develop an error-handling strategy early; consistency within a module matters most.
- Use exceptions for conditions that are rare, cannot be handled locally, or require stack unwinding.
- Exceptions are mandatory for constructor and operator failures; there is no return value to signal errors.
- Understand the three exception safety guarantee levels: nothrow (never throws), strong (commit-or-rollback), basic (valid state maintained).
- Every function should provide at least the basic guarantee.
- Throw by value, catch by `const` reference.
- Use purpose-designed exception hierarchies, not built-in types or strings.
- Don't catch every exception in every function; let them propagate; minimize explicit try/catch - RAII handles cleanup.
- Destructors, deallocation, swap, and exception-type copy/move must never throw; mark them `noexcept`.
- Use `std::expected<T, E>` (C++23) for expected/recoverable failures (parsing, I/O, validation).
- Use `std::optional` for "no value" cases where the caller doesn't need to know why.
- Avoid `errno` in new C++ code; use only when calling C library functions that require it.
- Use `std::error_code` for cross-library error propagation.
- Do not use dynamic exception specifications (deprecated, removed in C++20); use `noexcept`.
- Ensure all owned resources are RAII-managed before code that can throw.
- Contracts (C++26) are for precondition checking, not error handling; a violated precondition means a caller bug.
- Use `assert()` for programming errors, not error handling; never put side effects in assert.
- Document exception safety guarantees for public functions.

| Mechanism | Use when | Example |
|---|---|---|
| Exceptions | rare, cannot handle locally, stack unwinding needed | constructor failure, I/O error in deep call stack |
| `std::expected<T, E>` | expected/recoverable failure with typed reason | parsing, validation, I/O where caller must decide |
| `std::optional<T>` | value may be absent, no error reason needed | lookup, find, config with default |
| `assert()` / contracts | programming error (violated precondition) | null pointer that should never be null |
| `std::error_code` | cross-library or C-interop boundary | Asio-style APIs |

| Guarantee level | Promise | Examples |
|---|---|---|
| Nothrow | never throws | destructors, swap, move, deallocation |
| Strong | if exception thrown, state rolls back | copy-and-swap assignment, transactional operations |
| Basic | valid state maintained but may have changed | container operations after partial insertion |

Exception-safe function using RAII:

```cpp
void TransferData(const std::string& src_path, const std::string& dst_path) {
    auto data = ReadFile(src_path);    // RAII: string cleans up on throw
    auto conn = OpenConnection(dst_path); // RAII: connection closes on throw
    conn.Send(data);                   // if this throws, both clean up automatically
}
```

std::expected usage for a parse function:

```cpp
std::expected<Config, ParseError> ParseConfig(std::string_view input) {
    auto tokens = Tokenize(input);
    if (tokens.empty()) return std::unexpected(ParseError::kEmptyInput);
    return BuildConfig(tokens);
}

// caller
auto result = ParseConfig(raw_input);
if (!result) {
    Log("parse failed: {}", result.error());
    return;
}
UseConfig(*result);
```

Copy-and-swap idiom for strong guarantee:

```cpp
Widget& Widget::operator=(const Widget& other) {
    Widget tmp(other);   // copy: if this throws, *this is unchanged
    swap(tmp);           // swap: noexcept
    return *this;        // tmp destructor cleans up old data
}
```

Detect in existing code:

- throwing a string or int instead of an exception type - no stack trace, no hierarchy.
- catching by value instead of by reference - slices derived exception types.
- manual resource cleanup in catch blocks - should be RAII.
- missing `noexcept` on destructor, swap, or move operations.
- dynamic exception specification `throw(...)` instead of `noexcept`.
- `assert()` with side effects - evaluates to nothing in release builds.

Corrections:

- `throw "error message"` -> `throw std::runtime_error("error message")`.
- `catch (std::exception e)` (catch by value, slices) -> `catch (const std::exception& e)`.
- manual resource cleanup before throw -> use RAII instead.
- `catch (...) {}` silently swallowing -> at minimum log, or let propagate.
- `errno`-based error checking in new code -> use `std::expected` or exceptions.
- `throw()` dynamic exception specification -> `noexcept`.

## 8. Pointers, references, and value semantics

Default to value semantics. Objects behave like values, copied and destroyed deterministically, giving the strongest guarantees for correctness and composability.

- Default to value semantics: objects are copied, moved, and destroyed deterministically.
- Reserve reference semantics for unique identity, polymorphism, or objects too expensive to copy.
- Use `T&` for non-owning, non-nullable parameters and aliases; `T*` only for non-owning, nullable observers.
- Return by value; move semantics and RVO make this efficient.
- Use `const T&` for read-only parameters of non-trivial types.
- Value semantics are especially important in concurrent and coroutine code; references can dangle across suspension points.
- Mark every non-mutating member function `const` immediately; adding const later cascades into callers.
- Use `mutable` only for internal implementation details (caches, synchronization) that don't affect observable state.
- Prefer `constexpr` over `const` for compile-time constants; `constexpr` is guaranteed compile-time, `const` only prevents modification through that name.
- Do not return `const` values (e.g., `const Widget Make()`); it disables move semantics with no benefit.
- Use `std::as_const()` (C++17) for const references without casting.
- Prefer immutable data: use `const` and `constexpr` wherever mutation is neither intended nor required.

| Situation | Use |
|---|---|
| Non-owning, non-nullable parameter | `T&` or `const T&` |
| Non-owning, nullable parameter | `T*` or `const T*` |
| Return a computed value | `T` (by value) |
| Read-only access to non-trivial data | `const T&` |
| Viewing contiguous buffer | `std::span<T>` |
| Viewing string data | `std::string_view` |

Const-correct member function:

```cpp
class Circle {
    double radius_;
public:
    explicit Circle(double r) : radius_(r) {}
    double Area() const { return 3.14159 * radius_ * radius_; }
    void Scale(double factor) { radius_ *= factor; }
};
```

Detect in existing code:

- a member function that doesn't modify `*this` but isn't const - add const.
- a const return value on a non-reference type - disables move semantics.
- a variable declared without const that is never modified - make const.
- `const` used for a compile-time constant where `constexpr` would work.

Corrections:

- `const Widget MakeWidget()` (const return value) -> `Widget MakeWidget()` - enables moves.
- function that only reads `*this` but isn't marked const -> mark const.
- `mutable` on a member that affects observable state -> redesign.
- `const int kMaxSize = 100;` -> `constexpr int kMaxSize = 100;` - compile-time constant.
- variable declared non-const but never modified -> make const.

## 9. Memory safety and undefined behavior

Undefined behavior means the compiler may do anything: optimize away your checks, corrupt unrelated data, or silently produce wrong results. Eliminate every source.

- Signed integer overflow is UB; use unsigned for overflow-safe arithmetic or check before operations.
- Buffer overflow and out-of-bounds access is UB; use `.at()` for checked access, `std::span` for bounds-safe views.
- Null pointer dereference is UB; prefer references (cannot be null) and `optional` for nullable semantics.
- Use-after-free and dangling references are UB; smart pointers and RAII prevent these; `string_view` and `span` can also dangle.
- Data races are UB; use `std::atomic` or `std::mutex`.
- Strict aliasing violations are UB; use `std::bit_cast` (C++20) or `memcpy` for type-punning.
- Reading uninitialized variables is UB; always initialize at declaration.
- Other common UB: not returning from non-void function, invalid bit shifts, division by zero, modifying a const object, `new[]`/`delete` mismatch.
- Operations on containers (`push_back`, etc.) may invalidate iterators/references; never hold references across mutating operations.
- Avoid C-style casts; use `static_cast`, `dynamic_cast`, `const_cast`, `reinterpret_cast`.
- Don't cast away `const`; it is UB if the object was originally declared const.
- Use unsigned for bit manipulation, signed for arithmetic; don't mix signed and unsigned in expressions.
- Fail fast: detect errors close to source and abort/throw immediately.
- Make invalid states unrepresentable via the type system; prefer strong types over raw ints.

| Category | Example | Fix |
|---|---|---|
| Signed overflow | `INT_MAX + 1` | check before, or use unsigned |
| Buffer overflow | `arr[n]` past end | `.at(n)` or `span` with bounds |
| Null dereference | `*p` when `p == nullptr` | reference, or check before use |
| Use-after-free | dereference after `delete` | smart pointer / RAII |
| Data race | two threads write same variable | `std::atomic` or `std::mutex` |
| Aliasing | `*(int*)&float_val` | `std::bit_cast<int>(float_val)` |
| Uninitialized read | `int x; return x;` | `int x = 0;` or `auto x = Compute();` |
| Missing return | non-void function falls off end | add return statement |
| `new[]`/`delete` mismatch | `delete p` on array | `delete[] p` or use `std::vector` |

| Cast | Use when |
|---|---|
| `static_cast` | well-defined conversions (numeric, up/downcast with known type) |
| `dynamic_cast` | safe downcast in polymorphic hierarchy (returns nullptr on failure) |
| `const_cast` | adding/removing const (only if original object is non-const) |
| `reinterpret_cast` | pointer-to-integer, unrelated pointer types (last resort) |

std::bit_cast for type punning:

```cpp
// bad: strict aliasing violation
float f = 3.14f;
int i = *reinterpret_cast<int*>(&f);  // UB

// good: bit_cast (C++20)
float f = 3.14f;
int i = std::bit_cast<int>(f);  // well-defined
```

Container invalidation danger:

```cpp
// bad: reference invalidated by push_back
std::vector<std::string> v = {"hello"};
const auto& ref = v[0];
v.push_back("world");  // may reallocate
Use(ref);               // UB: ref may dangle

// good: copy or re-index after mutation
auto copy = v[0];
v.push_back("world");
Use(copy);
```

Detect in existing code:

- C-style cast `(int)x` - use named casts.
- uninitialized variable - always initialize.
- raw pointer dereference without null check where pointer could be null.
- `reinterpret_cast` for type punning - use `bit_cast` instead.
- mixing signed and unsigned arithmetic in expressions.
- missing return statement in non-void function path.

Corrections:

- C-style cast `(int)x` -> `static_cast<int>(x)`.
- `array[i]` without bounds check in safety-critical code -> `array.at(i)` or span with bounds checking.
- uninitialized variable `int x;` -> `int x = 0;` or `auto x = Compute();`.
- `reinterpret_cast<int*>(&float_val)` -> `std::bit_cast<int>(float_val)` (C++20).
- `new[]` / `delete` mismatch -> `new[]` / `delete[]` or use `std::vector`.

## 10. STL containers and algorithms

Use `std::vector` as the default container. Contiguous memory is cache-friendly, and even mid-vector insertions with memmove beat linked list insertions for reasonable sizes.

- Use `std::vector` as the default container; contiguous, cache-friendly, fast random access.
- Use `std::array` for fixed-size collections; zero overhead over raw arrays with STL interface and bounds checking.
- Use `std::deque` for double-ended insertion with random access.
- Use `std::list`/`forward_list` only for stable iterators during frequent mid-sequence insertions; lists are expensive to traverse due to pointer chasing.
- Use unordered containers (`unordered_map`/`unordered_set`) for O(1) average lookup when sorted order is not needed.
- Use ordered containers (`map`/`set`) for range queries or sorted iteration.
- Use container adaptors (`stack`, `queue`, `priority_queue`) to signal restricted interface intent.
- Prefer algorithms over raw loops; prefer `std::ranges` algorithms (C++20) which accept range objects and offer projections.
- Use `std::erase`/`std::erase_if` (C++20) instead of the erase-remove idiom.
- Know algorithm complexity contracts; never use binary search on unsorted ranges.
- Use execution policies (C++17) only for CPU-bound work; make parallel callables thread-safe and `noexcept`.
- Use projections instead of transform views for sorting by field.
- Do not add to namespace `std`; it is undefined behavior.
- Use standard library in a type-safe manner: `string_view` over `char*`, `vector` over C arrays, `span` over pointer+length.

| Need | Container | Reason |
|---|---|---|
| General-purpose sequence | `std::vector` | contiguous, cache-friendly, fast random access |
| Fixed-size sequence | `std::array` | zero overhead, bounds checking |
| Double-ended queue | `std::deque` | efficient front/back insertion with random access |
| Stable iterators with frequent insertion | `std::list` | O(1) insert/delete at known position |
| Fast key lookup | `std::unordered_map` | O(1) average, hash-based |
| Sorted key access | `std::map` | O(log n), ordered iteration, range queries |
| Unique elements | `std::unordered_set` / `std::set` | hash or tree based |
| LIFO/FIFO/priority | `stack` / `queue` / `priority_queue` | restricted interface signals intent |

| Algorithm | Complexity |
|---|---|
| `std::sort` | O(n log n) average and worst |
| `std::partial_sort` | O(n log k) |
| `std::nth_element` | O(n) average |
| `std::stable_sort` | O(n log n) with memory, O(n log^2 n) without |
| `std::binary_search` | O(log n) - input must be sorted |
| `std::find` | O(n) |
| `std::ranges::sort` | O(n log n) with projection support |

Ranges pipeline with projection:

```cpp
struct Person { std::string name; int age; };
std::vector<Person> people = GetPeople();

// sort by age using projection (no temporary transform)
std::ranges::sort(people, {}, &Person::age);

// filter and transform
auto names_of_adults = people
    | std::views::filter([](const Person& p) { return p.age >= 18; })
    | std::views::transform(&Person::name);
```

Detect in existing code:

- `std::list` or `std::deque` where `std::vector` would suffice.
- raw loop where an algorithm exists.
- erase-remove idiom in C++20 code - use `std::erase_if`.
- adding definitions to namespace `std`.
- using `char*` where `string` or `string_view` would work.

Corrections:

- `std::list` used for general-purpose sequential access -> `std::vector`.
- raw loop that transforms a container -> `std::transform` or range adaptor.
- `v.erase(std::remove_if(...), v.end())` -> `std::erase_if(v, predicate)` (C++20).
- `std::sort(v.begin(), v.end(), [](const auto& a, const auto& b) { return a.name < b.name; })` -> `std::ranges::sort(v, {}, &Person::name)` - projection.
- `char*` string manipulation -> `std::string` or `std::string_view`.

## 11. Templates and generic programming

Use templates to raise the abstraction level for algorithms and containers. Constrain every template parameter with concepts.

- Use templates to raise abstraction level for algorithms and containers.
- Specify concepts for all template parameters (C++20); use standard concepts from `<concepts>` and `<iterator>` first.
- Use template aliases (`using`) rather than `typedef` for templates.
- Do not specialize function templates; use overloading instead.
- Let the compiler deduce template arguments; use `{}` within templates to avoid parsing ambiguities.
- Prefer `typename` over `class` for type parameters.
- Qualify non-member calls in templates unless intended as ADL customization points (two-phase lookup).
- Use function objects (lambdas) for algorithms, not function pointers; lambdas carry their own type and can be inlined.
- Use TMP sparingly; prefer `constexpr`, concepts, `if constexpr` before resorting to recursive templates.
- Use fold expressions and variadic expansions instead of recursive template instantiations.
- Understand reference collapsing rules for forwarding references: any combination containing at least one `&` yields `&`, while `&& &&` yields `&&`.
- Inside forwarding templates, always use `std::forward<T>(x)`, never `std::move(x)`; never use `std::forward` outside a forwarding-reference context.

Concept-constrained template function:

```cpp
template <std::integral T>
T Gcd(T a, T b) {
    while (b != 0) {
        auto tmp = b;
        b = a % b;
        a = tmp;
    }
    return a;
}
```

Perfect forwarding with std::forward:

```cpp
template <typename... Args>
auto MakeWidget(Args&&... args) {
    return std::make_unique<Widget>(std::forward<Args>(args)...);
}
```

Fold expression replacing recursive TMP:

```cpp
// bad: recursive template
template <typename T> T Sum(T v) { return v; }
template <typename T, typename... Args> T Sum(T first, Args... rest) { return first + Sum(rest...); }

// good: fold expression
template <typename... Args>
auto Sum(Args... args) { return (args + ...); }
```

Detect in existing code:

- SFINAE/`enable_if` where concepts would work.
- `std::move` used in a forwarding-reference context instead of `std::forward`.
- recursive template instantiation where a fold expression would suffice.
- function pointer passed to algorithm where a lambda would inline.

Corrections:

- SFINAE-based `enable_if` -> concepts constraint.
- `template <class T>` -> `template <typename T>` - prefer typename.
- recursive template metafunction -> fold expression or `constexpr` function.
- `std::move` in a forwarding context -> `std::forward<T>`.
- function pointer passed to algorithm -> lambda or function object.

## 12. Concurrency and thread safety

Design for thread safety from the start. If there is no shared mutable state, there can be no data races.

- Design for thread safety from the start; avoid shared mutable state whenever possible.
- Use RAII for locking: `std::lock_guard` or `std::unique_lock`, never manual `lock()`/`unlock()`.
- Always name lock guards; an unnamed guard unlocks immediately: `std::lock_guard<std::mutex> (m);` is a no-op.
- Use `std::scoped_lock` (C++17) for acquiring multiple mutexes atomically with deadlock avoidance.
- Minimize critical sections: don't do I/O, allocation, or complex computation under a lock.
- Never call unknown code (callbacks, virtual functions) while holding a lock; it may deadlock.
- Use `std::atomic` for simple scalar operations (counters, flags); 10-100x faster than mutex for single operations.
- Do not use `volatile` for thread synchronization; it provides no atomicity or memory ordering guarantees.
- Always supply a predicate to `condition_variable::wait()`; spurious wakeups are guaranteed by the standard.
- Minimize thread creation; use thread pools for many short tasks.
- Avoid lock-free programming unless profiling proves mutex contention is a bottleneck.
- Use `alignas(64)` to prevent false sharing on cache lines.
- Prefer `std::jthread` (C++20) over `std::thread`; `jthread` auto-joins on destruction and supports `stop_token`.
- Design data structures and access patterns to be race-free by construction; prefer message passing and futures.

| Primitive | Thread-safe | Risk | Use when |
|---|---|---|---|
| `std::mutex` | yes | deadlock if misused | general shared mutable state |
| `std::lock_guard` | yes | none (RAII) | single mutex, simple scope |
| `std::scoped_lock` | yes | none (RAII) | multiple mutexes, deadlock-free |
| `std::unique_lock` | yes | none (RAII) | condition variables, deferred locking |
| `std::atomic<T>` | yes | ordering bugs | counters, flags, single scalars |
| `std::condition_variable` | yes | spurious wakeups | waiting for a condition |
| `std::jthread` | yes | none (auto-joins) | managed thread with stop_token |

| Question | Use |
|---|---|
| Single scalar, simple increment/flag | `std::atomic` |
| Protecting complex data structure | `std::mutex` with lock guard |
| Multiple mutexes at once | `std::scoped_lock` |
| Wait for condition | `std::condition_variable` with predicate |

RAII locking with scoped_lock for multiple mutexes:

```cpp
void Transfer(Account& from, Account& to, int amount) {
    std::scoped_lock lock(from.mutex_, to.mutex_);
    from.balance_ -= amount;
    to.balance_ += amount;
}
```

Condition variable with predicate:

```cpp
std::mutex mtx;
std::condition_variable cv;
bool ready = false;

// producer
{
    std::lock_guard lock(mtx);
    ready = true;
}
cv.notify_one();

// consumer
std::unique_lock lock(mtx);
cv.wait(lock, [&] { return ready; });  // predicate handles spurious wakeups
```

Detect in existing code:

- manual `lock()`/`unlock()` without RAII - exception between them leaves mutex locked.
- `volatile` used for thread synchronization - use `std::atomic`.
- condition variable wait without predicate - spurious wakeups cause bugs.
- unnamed lock guard - unlocks immediately, protecting nothing.
- `std::thread` without join or detach, or where `std::jthread` would auto-join.

Corrections:

- `m.lock(); ... m.unlock();` -> `std::lock_guard<std::mutex> lock(m);`.
- `std::lock_guard<std::mutex> (m);` (unnamed, unlocks immediately) -> `std::lock_guard<std::mutex> lock(m);`.
- `volatile bool running = true;` for thread flag -> `std::atomic<bool> running{true};`.
- `cv.wait(lock);` without predicate -> `cv.wait(lock, [&]{ return ready; });`.
- `std::thread t(f); t.join();` -> `std::jthread t(f);` - auto-joins on destruction.

## 13. Documentation

Document the contract, not the implementation. Self-documenting code first, then comments for why.

- Use Doxygen with `/** ... */` or `///` for doc comments; use `@` commands (`@brief`, `@param`, `@return`, `@throws`).
- Place documentation in header files at the point of declaration.
- Document all public and protected types, methods, functions, and constants.
- Use `@param[in]`, `@param[out]`, `@param[in,out]` to indicate parameter direction.
- Self-documenting code first: use descriptive names, then add comments for why, not what.
- Document classes with purpose, usage, and synchronization assumptions.
- Make function argument meaning clear: prefer named constants, enums, or options structs over inline comments.
- Use TODO comments with bug IDs or person identifiers and target dates.
- Document exception safety guarantees (nothrow, strong, basic) for public functions.
- Write comments as English prose with proper capitalization and punctuation.

| Command | Usage |
|---|---|
| `@brief` | one-sentence summary |
| `@param[in]` | input parameter description |
| `@param[out]` | output parameter description |
| `@param[in,out]` | modified parameter description |
| `@return` | return value description |
| `@throws` | exception condition |
| `@pre` | precondition |
| `@post` | postcondition |
| `@note` | additional information |
| `@see` | cross-reference |

Model Doxygen comment for a public function:

```cpp
/**
 * @brief Parses a configuration file from the given path.
 *
 * @param[in] path  Filesystem path to the configuration file.
 * @param[in] strict  If true, unknown keys cause an error.
 * @return The parsed configuration.
 * @throws std::runtime_error if the file is unreadable.
 * @throws ParseError if the contents are malformed.
 *
 * Exception safety: strong guarantee.
 */
Config ParseConfig(std::string_view path, bool strict = false);
```

Detect in existing code:

- public function/class without documentation comment.
- comment that literally restates what the code does ("increment i") - remove or replace with why.
- `@param` without direction annotation - add `[in]`, `[out]`, or `[in,out]`.
- TODO without bug ID or owner.

Corrections:

- undocumented public API function -> add Doxygen comment.
- comment that restates the code -> remove or replace with why-comment.
- missing `@param` direction -> add `[in]`, `[out]`, or `[in,out]`.
- boolean parameter with no clarity -> replace with enum or named constant.

## 14. Testing and quality assurance

Testing is not optional. Code without tests is legacy code from the moment it is written.

- Testing is not optional; code without tests is legacy code.
- Use GoogleTest for large/enterprise projects; Catch2 for smaller projects; doctest for compilation-speed-sensitive projects.
- Use descriptive test names explaining the scenario.
- Keep tests independent with no shared mutable state between test cases.
- Test behavior, not implementation details; mock only external dependencies.
- Use constexpr testing: evaluate with `static_assert` for UB detection at compile time.
- Write characterization tests before refactoring to capture current behavior.
- Run ASan + UBSan in all regular test runs; TSan in a dedicated CI lane (incompatible with ASan); MSan for uninitialized reads.
- Combine sanitizers with fuzzing (libFuzzer, AFL++).
- Use clang-tidy for style/modernization, cppcheck for UB detection; enable Core Guidelines checks.
- Enable `-Wall -Wextra -Wpedantic -Wshadow`; treat as errors in CI (`-Werror`); build with multiple compilers.
- Integrate tests via CMake with FetchContent; use `ctest --output-on-failure`.

| Sanitizer | Flags | Detects | Constraints |
|---|---|---|---|
| AddressSanitizer (ASan) | `-fsanitize=address` | buffer overflow, use-after-free, leaks | incompatible with TSan and MSan |
| UndefinedBehaviorSanitizer (UBSan) | `-fsanitize=undefined` | signed overflow, null deref, shifts | combinable with ASan |
| ThreadSanitizer (TSan) | `-fsanitize=thread` | data races, lock-order inversions | dedicated CI lane, incompatible with ASan |
| MemorySanitizer (MSan) | `-fsanitize=memory` | uninitialized reads | Clang-only, all deps must be instrumented |

| Tool | Purpose |
|---|---|
| clang-tidy | style violations, modernization, interface misuse |
| cppcheck | UB detection with few false positives |
| PVS-Studio / Coverity | code smells and potential bugs |
| clang-format | automated formatting enforcement |

GoogleTest test case structure:

```cpp
#include <gtest/gtest.h>
#include "project/parser.h"

TEST(ParserTest, ParsesEmptyInput) {
    auto result = Parse("");
    EXPECT_TRUE(result.has_value());
    EXPECT_EQ(result->size(), 0);
}

TEST(ParserTest, RejectsInvalidSyntax) {
    auto result = Parse("{invalid");
    EXPECT_FALSE(result.has_value());
}
```

CMake FetchContent integration for GoogleTest:

```cmake
include(FetchContent)
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG        v1.15.2
)
FetchContent_MakeAvailable(googletest)

add_executable(my_tests tests/parser_test.cpp)
target_link_libraries(my_tests PRIVATE GTest::gtest_main project_lib)

include(GoogleTest)
gtest_discover_tests(my_tests)
```

Detect in existing code:

- code without corresponding tests.
- CI pipeline without sanitizers.
- tests that depend on execution order.
- missing `-Wall` or `-Werror` in build configuration.

Corrections:

- no tests for a module -> add tests.
- tests with shared mutable state between test cases -> isolate state per test.
- CI without sanitizers -> add `-fsanitize=address,undefined`.
- CI without `-Werror` -> add it.

## 15. Performance and optimization

Measure before optimizing. Most gains come from algorithmic improvements and cache-friendly data layout, not clever code.

- Never optimize without measurement; use profilers (VTune, perf, Coz) for actual bottlenecks.
- Fix algorithmic complexity first, data layout second, micro-tuning last.
- Be CPU cache aware: 64-byte cache lines, cache miss costs 50-200x an L1 hit; design for spatial locality.
- Know SoA vs AoS tradeoffs: SoA for SIMD and field-specific iteration, AoS for whole-object access.
- Separate hot and cold fields in structs; declare the most-used member first.
- Prefer flat, contiguous containers (`vector`) over node-based containers (`list`) to avoid pointer chasing.
- Minimize allocations on hot paths: use `reserve()` for vectors, pool allocators for frequent small allocations.
- Use move semantics to avoid copies; rely on NRVO and mandatory copy elision (C++17).
- Know compiler optimization flags: `-O2` for production, `-flto=thin` for cross-module optimization, PGO for hot paths.
- Avoid context switches on critical path: minimize kernel calls and mutex contention.
- Small habits: use `'\n'` not `std::endl` (endl forces flush), prefer `++i`, use char literals for single characters.
- Design to enable optimization: clean interfaces, compact data, zero-overhead abstractions.

| Question | Tool |
|---|---|
| Which function burns wall clock? | VTune, perf, Coz, flamegraph |
| Is this faster than baseline? | Google Benchmark, Catch2 benchmark |
| Where do allocations come from? | heaptrack, Massif |
| What dominates build time? | `cmake --build . --timings`, ninja `-d stats` |

| Flag | Effect |
|---|---|
| `-O2` | standard production optimization |
| `-O3` | aggressive optimization (may increase code size) |
| `-flto=thin` | cross-module optimization, moderate link time |
| `-flto` | full LTO, slower link but better optimization |
| `-fprofile-generate` / `-fprofile-use` | profile-guided optimization |
| `-march=native` | use all available CPU instructions |
| `-DNDEBUG` | disable assert() in production |

Detect in existing code:

- `std::endl` where `'\n'` would suffice - endl forces a flush.
- vector without `reserve` when final size is known or bounded.
- heap allocation inside a tight loop.
- node-based container (list/map) used for sequential iteration.

Corrections:

- `std::endl` -> `'\n'` - endl forces flush.
- `i++` in a loop -> `++i` - avoids temporary for non-trivial iterators.
- `std::list` for general sequence -> `std::vector` - cache-friendly.
- missing `reserve()` on vector with known final size -> add `v.reserve(n)`.
- string concatenation in loop with `+` -> use `std::ostringstream` or pre-reserve.

## 16. Build systems and dependencies

Express requirements through target properties, not global variables. CMake is the de facto standard.

- Express requirements through target properties, not global variables.
- Use `target_link_libraries`, `target_include_directories`, `target_compile_features` per target.
- Specify C++ standard explicitly: `target_compile_features(mylib PUBLIC cxx_std_20)`.
- Use CMakePresets.json for shared build configurations across developers and CI.
- Use vcpkg or Conan for external dependencies; manifest mode with pinned versions.
- Prefer target-based linking: `target_link_libraries(myapp PRIVATE pkg::target)`.
- Minimize dependencies; audit regularly.
- Use binary caching in CI (vcpkg binary cache, Conan remotes) to avoid recompiling.
- Optimize build times: forward declarations, minimal includes, precompiled headers for stable headers, build caching (ccache/sccache).
- Production flags: `-O2 -DNDEBUG -Wall -Werror`; use LTO for cross-module optimization.

| Don't | Do instead |
|---|---|
| `set(CMAKE_CXX_FLAGS "-std=c++20")` | `target_compile_features(mylib PUBLIC cxx_std_20)` |
| `include_directories(...)` (global) | `target_include_directories(mylib PRIVATE ...)` |
| `set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall")` | `target_compile_options(mylib PRIVATE -Wall)` |
| `link_libraries(...)` (global) | `target_link_libraries(mylib PRIVATE ...)` |
| `add_definitions(...)` (global) | `target_compile_definitions(mylib PRIVATE ...)` |
| Manual dependency download scripts | vcpkg/Conan with manifest mode |

Modern CMakeLists.txt skeleton:

```cmake
cmake_minimum_required(VERSION 3.21)
project(myproject LANGUAGES CXX)

# Library
add_library(mylib
    src/parser.cpp
    src/config.cpp
)
target_include_directories(mylib PUBLIC include PRIVATE src)
target_compile_features(mylib PUBLIC cxx_std_20)
target_compile_options(mylib PRIVATE
    $<$<CXX_COMPILER_ID:GNU,Clang>:-Wall -Wextra -Wpedantic -Wshadow>
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
)

# Executable
add_executable(myapp src/main.cpp)
target_link_libraries(myapp PRIVATE mylib)

# Tests
option(BUILD_TESTING "Build tests" ON)
if(BUILD_TESTING)
    enable_testing()
    include(FetchContent)
    FetchContent_Declare(googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG v1.15.2
    )
    FetchContent_MakeAvailable(googletest)

    add_executable(mylib_tests tests/parser_test.cpp)
    target_link_libraries(mylib_tests PRIVATE mylib GTest::gtest_main)
    include(GoogleTest)
    gtest_discover_tests(mylib_tests)
endif()
```

Detect in existing code:

- global CMake variables (`CMAKE_CXX_FLAGS`, `include_directories`) instead of target-based.
- missing C++ standard specification.
- manual dependency management instead of package manager.

Corrections:

- `set(CMAKE_CXX_FLAGS "-std=c++20")` -> `target_compile_features(mylib PUBLIC cxx_std_20)`.
- `include_directories(...)` (global) -> `target_include_directories(... PRIVATE ...)`.
- manual dependency download scripts -> vcpkg/Conan with manifest mode.

## 17. Refactoring

Work in small steps. Compile and test after each transformation. Commit frequently.

- Work in small steps; compile and test after each transformation; commit frequently.
- Have tests before refactoring; add characterization tests if none exist.
- Separate refactoring from feature work; commit refactorings separately.
- Extract Function: move a code block with a specific purpose into a named function.
- Rename for clarity: use IDE-based rename, not find-and-replace.
- Introduce Parameter Object: group 3+ related parameters into a struct.
- Replace Conditional with Polymorphism: replace type-code switch/if-else with virtual dispatch.
- Decompose Conditional: extract condition and branches into named functions.
- Separate Query from Modifier (CQS): split a function that both returns a value and has side effects.
- Remove Flag Argument: replace bool parameter with separate named functions.
- Replace raw pointers with smart pointers.
- Replace C-style arrays with `std::vector`/`std::array`/`std::span`.
- Replace C-strings with `std::string`/`std::string_view`.
- Modernize loops to range-based for.
- Replace macros with modern alternatives (`constexpr`, inline, `if constexpr`).
- Strangler Fig Pattern: wrap legacy behind modern interface, migrate incrementally.
- Refactor leaf nodes first (fewest dependents); map dependencies before starting.
- Focus on interfaces first, then implementations.
- Use Sprout (new tested function called from legacy) and Wrap (rename + wrapper) techniques for modifying untested code.
- Know when NOT to refactor: ugly code that doesn't need to change, aesthetic reasons alone, or when rewrite would be easier.

| Smell | Refactoring | clang-tidy check |
|---|---|---|
| Long method (>60 lines) | Extract Function | readability-function-size |
| Data clumps (same 3+ params repeated) | Introduce Parameter Object | - |
| Boolean flag controlling logic path | Remove Flag Argument | - |
| Primitive obsession (bare ints for distinct concepts) | Introduce wrapper class | - |
| Feature envy (method uses another class's data) | Move method | - |
| Duplicated code | Extract and share | - |
| God object (>10 responsibilities) | Extract class | - |

| Legacy pattern | Modern replacement | Tool |
|---|---|---|
| `NULL` / `0` | `nullptr` | modernize-use-nullptr |
| `typedef` | `using` | modernize-use-using |
| Raw `new`/`delete` | Smart pointers | - |
| C arrays | `std::vector`/`std::array` | modernize-avoid-c-arrays |
| `strcpy`/`strcat` | `std::string` | - |
| Index-based for (element access only) | Range-based for | modernize-loop-convert |
| `enum` | `enum class` | modernize-use-scoped-enums (custom) |
| `#define` constant | `constexpr` | - |
| `override` missing | Add `override` | modernize-use-override |

Detect in existing code:

- functions longer than 60 lines.
- same group of parameters repeated in multiple function signatures.
- boolean parameter controlling which code path to take.
- C-style string functions (`strcpy`, `strcat`, `strlen`) in C++ code.
- raw C arrays where containers would work.
- index-based loops used only for element access.

Corrections:

- long function (>60 lines) -> extract functions.
- data clumps (same 3+ params in multiple signatures) -> introduce parameter object.
- boolean flag parameter controlling logic path -> separate named functions.
- `strcpy`/`strcat`/`strlen` -> `std::string` operations.
- raw C array -> `std::vector` or `std::array`.
- index-based for loop used only for element access -> range-based for.

## Binding rules (restated)

- Initialize every variable at declaration; uninitialized reads are undefined behavior.
- Never use raw `new`/`delete` in application code; use smart pointers and RAII.
- Make ownership explicit in every API with `unique_ptr`, `shared_ptr`, references, and `span`.
- Mark every non-mutating member function `const` and every move operation `noexcept`.
- Run clang-format and clang-tidy before every commit.
- Run sanitizers (ASan + UBSan) in CI on every test run.
- Add a test in the same change as the code.

*2026-08-11 - Opus 4.6 (Cursor agent). Distilled from web research on C++ Core Guidelines, Google Style Guide, LLVM Coding Standards, modern C++ features, error handling, resource management, templates, concurrency, testing, and tooling.*
