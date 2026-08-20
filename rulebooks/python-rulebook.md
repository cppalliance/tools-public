---
description: Write and maintain idiomatic, typed, well-tooled Python 3.12+ code
---

# Rulebook: Writing & Maintaining Python 3.12+

Rules for writing and maintaining Python targeting version 3.12 and newer. The reader is an AI coding agent that writes and edits Python code. Every rule is an imperative; every prohibition names the behavior that replaces it; every quantity is a number or a range. Each rule links to its official source (a PEP, docs.python.org, a tool's documentation, or the Python Packaging User Guide) so its authority is checkable.

Throughout this rulebook, PEP means [Python Enhancement Proposal](https://peps.python.org/pep-0001/), the numbered design documents that define the language and its ecosystem. Other acronyms are defined at their first use.

![The Python Workshop](images/python-rulebook.png)

## Applying these rules to an existing codebase

- Encode the modern generation of syntax and tooling described here; treat any older form marked legacy as something to replace, and name its replacement when you flag it.
- Match a settled local convention over the default here: where the project already fixes a value (line length, docstring style, import grouping), read that value from its config or existing code and follow it.
- Raise a proposed change with the human before switching a settled convention project-wide; do not reformat silently.
- Flag for the human any inconsistency you find, and any code that cannot follow a rule here for any reason, rather than rewriting it on your own judgment.
- When a rule below says to detect a value and the codebase is empty, mixed, or otherwise leaves it unclear, ask the human which value to use rather than guessing.


## 1. Style, Naming & Idioms

Sources for this section: [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/), [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/), the [Python glossary](https://docs.python.org/3/glossary.html), the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html), and the [Hitchhiker's Guide to Python: Code Style](https://docs.python-guide.org/writing/style/). Every rule below traces to one of these; grouped citations name the governing document per subsection.

### 1.1 Line length

Sources: [PEP 8 — Maximum Line Length](https://peps.python.org/pep-0008/#maximum-line-length), [Ruff formatter](https://docs.astral.sh/ruff/formatter/).

- Default to the formatter's configured width; do not pick a width per file.
- Cap code at 79 columns and cap docstrings and comments at 72 columns when following PEP 8 unaided, because narrow lines let editors show files side by side.
- Use 88 columns when the codebase uses Black or Ruff, since that is their default width.
- Detect the active width before writing: read `line-length` under `[tool.ruff]` or `line-length` under `[tool.black]` in `pyproject.toml`, and if neither exists, measure the longest lines already in the code and match that width.
- Flag the inconsistency to the human when files disagree on width rather than silently reformatting to one.

### 1.2 Indentation and continuation

Sources: [PEP 8 — Indentation](https://peps.python.org/pep-0008/#indentation), [PEP 8 — Tabs or Spaces](https://peps.python.org/pep-0008/#tabs-or-spaces).

- Indent 4 spaces per level.
- Use spaces exclusively; never use tabs, because mixing the two raises `TabError` in Python 3.
- Never mix tabs and spaces within a file.
- Break long lines by implicit continuation inside `()`, `[]`, or `{}` rather than a trailing backslash `\`, because a stray space after a backslash silently breaks the continuation.
- Align a continued line to the opening delimiter, or use a hanging indent of one extra 4-space level with no argument on the opening line.

### 1.3 Naming conventions

Sources: [PEP 8 — Naming Conventions](https://peps.python.org/pep-0008/#naming-conventions), [Google Python Style Guide — Naming](https://google.github.io/styleguide/pyguide.html#316-naming).

- Name functions, variables, methods, modules, and packages in `snake_case`.
- Name classes, exceptions, and type variables in `PascalCase` (also called CapWords).
- Name module-level constants in `UPPER_CASE` with underscores between words.
- Keep module and package names short and all-lowercase.

### 1.4 Underscores in names

Sources: [PEP 8 — Descriptive: Naming Styles](https://peps.python.org/pep-0008/#descriptive-naming-styles), [Python glossary — name mangling context](https://docs.python.org/3/glossary.html).

- Prefix a single leading underscore (`_name`) to mark an attribute or function as non-public API.
- Prefix a double leading underscore (`__name`) only to trigger class name-mangling that avoids clashes in subclasses; it is not a stronger privacy marker.
- Append a single trailing underscore (`name_`) to dodge a keyword clash, such as `class_` or `type_`, instead of misspelling the intended word.
- Never invent your own `__dunder__` names; the leading-and-trailing double-underscore namespace is reserved for the interpreter.

### 1.5 Single-character names, self, and cls

Sources: [PEP 8 — Names to Avoid](https://peps.python.org/pep-0008/#names-to-avoid), [PEP 8 — Function and Method Arguments](https://peps.python.org/pep-0008/#function-and-method-arguments).

- Never name a variable `l`, `O`, or `I` alone, because these characters are visually confusable with `1` and `0`; use a descriptive name instead.
- Name the first argument of an instance method `self`.
- Name the first argument of a class method `cls`.

### 1.6 Blank lines

Source: [PEP 8 — Blank Lines](https://peps.python.org/pep-0008/#blank-lines).

- Surround top-level function and class definitions with 2 blank lines.
- Separate method definitions inside a class with 1 blank line.
- Use single blank lines inside a function sparingly, only to separate logical steps.

### 1.7 Whitespace in expressions and statements

Source: [PEP 8 — Whitespace in Expressions and Statements](https://peps.python.org/pep-0008/#whitespace-in-expressions-and-statements).

- Put no space immediately inside `()`, `[]`, or `{}`: write `f(x)`, not `f( x )`.
- Put no space before `,`, `;`, or `:`, and exactly 1 space after each when more text follows on the line.
- Put 1 space on each side of binary operators, comparisons, booleans, and assignment `=`.
- Put no space around `=` for a keyword argument or a default value when the parameter is unannotated: write `f(x=1)`.
- Put 1 space on each side of `=` when the parameter is annotated: write `def f(x: int = 1)`.
- Treat a slice `:` as a binary operator with equal spacing on both sides, and omit spacing entirely for a simple slice like `ham[1:9]`.

### 1.8 Singleton comparisons and inline comments

Sources: [PEP 8 — Programming Recommendations](https://peps.python.org/pep-0008/#programming-recommendations), [PEP 8 — Comments](https://peps.python.org/pep-0008/#comments).

- Compare to the singletons `None`, `True`, and `False` with `is` or `is not`, never `==`, because identity is the correct test for a singleton: write `if x is None`.
- Separate an inline comment from its statement by at least 2 spaces, then start the comment with `# ` and a space before the text.
- Write comments that explain why the code does something, not what it does.

### 1.9 def over named lambda

Source: [PEP 8 — Programming Recommendations](https://peps.python.org/pep-0008/#programming-recommendations).

- Bind a name with `def` rather than assigning a `lambda` to that name, because a `def` gives the object a real `__name__` for tracebacks and introspection.

```python
def f(x):          # do this
    return 2 * x

f = lambda x: 2 * x  # not this
```

### 1.10 Zen of Python as rules

Source: [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/).

- Prefer explicit code over implicit behavior.
- Prefer simple constructions over complex ones.
- Prefer flat structure over deeply nested structure.
- Optimize for readability, because code is read far more often than it is written.
- Never let errors pass silently unless you silence them explicitly and deliberately.
- Provide one obvious way to do a thing rather than several competing ways.
- Treat an implementation that is hard to explain as a bad idea, and one that is easy to explain as a possibly good one.

### 1.11 EAFP versus LBYL

Sources: [Python glossary — EAFP](https://docs.python.org/3/glossary.html#term-EAFP), [Python glossary — LBYL](https://docs.python.org/3/glossary.html#term-LBYL).

- LBYL ("Look Before You Leap") tests preconditions before acting: `if key in d: x = d[key]`.
- EAFP ("Easier to Ask Forgiveness than Permission") assumes success and catches the failure: `try: x = d[key]` then `except KeyError: ...`.
- Prefer EAFP, because it reads cleaner and avoids a TOCTOU ("Time-Of-Check to Time-Of-Use") race where shared state changes between the check and the use.

```python
# EAFP — preferred
try:
    x = d[key]
except KeyError:
    x = default

# LBYL — use only per the escape hatch below
if key in d:
    x = d[key]
else:
    x = default
```

- Escape hatch: use LBYL when the failure raises no exception (for example a value that is merely falsy) or when the check is cheaper than setting up the `try` block.

### 1.12 Pythonic idioms

Sources: [Hitchhiker's Guide — Idioms](https://docs.python-guide.org/writing/style/), [PEP 8 — Programming Recommendations](https://peps.python.org/pep-0008/#programming-recommendations), [PEP 20](https://peps.python.org/pep-0020/).

- Test a sequence for emptiness by its truthiness: write `if seq:` for non-empty and `if not seq:` for empty, rather than comparing its length to `0`.
- Test with `if x is None:` instead of truthiness when `None` must be distinguished from other falsy values such as `0`, `""`, or `[]`.
- Iterate index and value with `enumerate(items)`, never `range(len(items))`, because `enumerate` yields both directly.

```python
for i, item in enumerate(items):
    print(i, item)
```

- Manage every external resource with a `with` context manager, because it guarantees cleanup even when an exception is raised.

```python
with open(path) as fh:
    data = fh.read()
```

- Build a collection with a comprehension when you need the whole result at once.
- Use a generator expression `(...)` instead of a list comprehension for a large or lazy stream, because it produces items on demand rather than materializing them all.

```python
squares = [n * n for n in range(10)]        # comprehension
total = sum(n * n for n in range(1_000_000))  # generator expression
```

- Assemble a string from parts with `''.join(parts)`, never repeated `+=` in a loop, because repeated concatenation reallocates and copies in O(n^2) time.
- Test type membership with `isinstance(x, T)`, never `type(x) == T`, because `isinstance` respects subclasses.
- Swap values with tuple unpacking: `a, b = b, a`.
- Combine range tests with chained comparisons: write `if 0 < x < 10:` rather than `if 0 < x and x < 10:`.
- Read a dict with a fallback using `dict.get(k, default)` instead of a manual key-presence check.
- Initialize-and-append in one step with `dict.setdefault(k, []).append(v)` or a `collections.defaultdict(list)` instead of testing whether the key exists first.

```python
from collections import defaultdict

groups = defaultdict(list)
for key, value in pairs:
    groups[key].append(value)
```

Restated for this section: match the codebase's existing width, spacing, and naming; write explicit, flat, readable code; prefer EAFP with an LBYL escape hatch; and reach for the idiom the standard library already provides. Flag any code that cannot follow a rule here to the human rather than silently reformatting it.


## 2. Typing

Encode modern static typing for Python 3.12+; every rule here supersedes the legacy `typing` imports. A PEP is a [Python Enhancement Proposal](https://peps.python.org/pep-0001/).

### Generics: prefer builtin and standard collections

- Subscript builtin collections directly; never import `typing.List`, `typing.Dict`, `typing.Set`, `typing.Tuple`, or `typing.Type`, because [PEP 585](https://peps.python.org/pep-0585/) made the builtins subscriptable and the `typing` aliases are deprecated.
- Write `list[int]`, `dict[str, int]`, `set[str]`, `tuple[int, ...]` (homogeneous variable-length), and `type[MyClass]` (a class object, not an instance).
- Import abstract container and callable types from `collections.abc`, not `typing`: write `collections.abc.Sequence[int]` and `collections.abc.Callable[[int], str]`, because the `typing` equivalents are deprecated aliases of these ([PEP 585](https://peps.python.org/pep-0585/), [typing docs](https://docs.python.org/3/library/typing.html)).

### Unions: prefer the `|` operator

- Write unions with `|`: `int | str` for a value of either type, and `str | None` for an optional value, because [PEP 604](https://peps.python.org/pep-0604/) makes `|` the current syntax and retires `Union`/`Optional`.
- Replace `Optional[X]` with `X | None`; `Optional[X]` means `X | None` (a value that may be `None`), and it never means "this argument may be omitted."
- A default value does not add `None` to the type; annotate an omittable-and-nullable parameter explicitly as `def f(x: int | None = None)`, because the default and the type are independent.
- Use `isinstance(x, int | str)` for runtime type checks; the `|` union works as the second argument to `isinstance` on 3.12 ([PEP 604](https://peps.python.org/pep-0604/)).

### Native generics: prefer PEP 695 syntax over `TypeVar`

- Declare type parameters with the [PEP 695](https://peps.python.org/pep-0695/) bracket syntax on classes, functions, and aliases; reach for an explicit `typing.TypeVar` only to control variance (`covariant=`/`contravariant=`) or when a legacy codebase forces it, because the bracket syntax scopes the parameter automatically and needs no separate declaration.
- Declare type aliases with the `type` statement so they are recognized as aliases by static checkers.
- Follow this form:

```python
class Stack[T]:
    def push(self, item: T) -> None: ...
def first[T](xs: list[T]) -> T:
    return xs[0]
def bounded[T: Number](x: T) -> T: ...       # upper bound
def constrained[T: (int, str)](x: T) -> T: ...  # constraints
type Vector = list[float]                     # alias statement
type Pair[T] = tuple[T, T]                     # generic alias
```

### Hints are not enforced at runtime

- Treat annotations as information for static checkers (mypy/pyright), editors, and documentation, not as runtime guards; a wrong type never raises from the annotation itself ([PEP 484](https://peps.python.org/pep-0484/)).
- Add explicit runtime checks (`isinstance`, validation, or a library like pydantic) whenever a wrong type must be rejected at runtime, because the interpreter ignores the hint.

### Construct reference

Use each typing construct for its stated case ([typing docs](https://docs.python.org/3/library/typing.html)):

- `Callable[[Arg], Ret]` from `collections.abc`: annotate a parameter or return that is itself a function, e.g. a callback taking an `int` and returning a `str`.
- `ParamSpec` via the `[**P]` bracket form: forward a wrapped callable's full parameter list through a decorator so the wrapper keeps the original signature.
- `Self`: annotate a method that returns its own instance, such as a fluent builder method or an alternative constructor (`@classmethod`), instead of naming the class.
- `Final` and `@final`: mark a module constant that must not be reassigned (`TIMEOUT: Final = 30`), a class that must not be subclassed (`@final class X`), or a method that must not be overridden.
- `Literal["r", "w"]`: restrict a parameter to a fixed set of constant values instead of a broad `str`.
- `TypedDict`: type a dict with fixed string keys and a distinct type per key; mark optional keys with `NotRequired[...]` or set `total=False` to make all keys optional.
- `overload`: declare several precise input/output type signatures for one function whose return type depends on argument types.
- `cast`: assert a value's type to the checker when you know more than it can infer; it performs no runtime check.
- `Annotated`: attach metadata (validators, units, framework hints) to a type without changing the type itself.
- `NewType`: create a distinct type from an existing one (`UserId = NewType("UserId", int)`) to stop mixing semantically different values with the same base type.
- `TypeGuard`/`TypeIs`: annotate a boolean-returning function that narrows a type, so the checker refines the argument's type inside the guarded branch.

### Decorator forwarding with ParamSpec

- Forward a callable's full signature through a decorator with `[**P, R]`:

```python
def logged[**P, R](f: Callable[P, R]) -> Callable[P, R]:
    def w(*a: P.args, **k: P.kwargs) -> R:
        return f(*a, **k)
    return w
```

### `from __future__ import annotations`

- Place any `from __future__` import as the first statement of the module, directly after the module docstring, because the interpreter rejects it elsewhere.
- Know that `from __future__ import annotations` makes every annotation in the module a lazily evaluated string, which lets you reference not-yet-defined names and break annotation-only import cycles, and skips the runtime cost of evaluating annotations.
- Do not add the future import for syntax reasons; the modern forms above (`list[int]`, `X | None`, [PEP 695](https://peps.python.org/pep-0695/) generics) already work on 3.12 without it, so add it only to defer evaluation or break an import cycle.
- Weigh that the future import breaks libraries that read annotations at runtime: `dataclasses` edge cases, `pydantic`, and `typing.get_type_hints` (which then needs the module globals to resolve the strings).
- Prefer quoting a single forward reference (`def f(x: "LaterClass") -> None`) over the module-wide future import when only one annotation needs deferring, because the local quote leaves every other annotation eagerly evaluated for the runtime readers.

Related: [PEP 484](https://peps.python.org/pep-0484/) (type hints), [PEP 544](https://peps.python.org/pep-0544/) (protocols, applied in Section 4).


## 3. Errors & Exceptions

Handle failures narrowly, explicitly, and loudly; errors should never pass silently unless explicitly silenced ([PEP 20](https://peps.python.org/pep-0020/)).

### Logging

- Emit every diagnostic through the stdlib [`logging`](https://docs.python.org/3/library/logging.html) module, never `print`, because `logging` carries levels, timestamps, and routing that `print` discards.
- Get a module-scoped logger with `log = logging.getLogger(__name__)`, so log records name their origin module for filtering ([logging docs](https://docs.python.org/3/library/logging.html#logger-objects)).
- Add no handlers in a library; leave handler and level configuration to the application, so importing your code does not hijack the root logger ([logging docs](https://docs.python.org/3/library/logging.html#configuring-logging-for-a-library)).
- Pass log arguments as `%`-style lazy args, `log.info("x=%s", x)`, not an f-string, because `logging` interpolates only when the record is actually emitted, saving the formatting cost at suppressed levels ([logging docs](https://docs.python.org/3/library/logging.html#logging.Logger.debug)).

### Custom exception classes

- Derive every custom exception from `Exception`, never from `BaseException`, because `BaseException` is reserved for the interpreter-signal exceptions `SystemExit`, `KeyboardInterrupt`, and `GeneratorExit` that normal `except` handlers must not swallow ([Built-in Exceptions](https://docs.python.org/3/library/exceptions.html#BaseException)).
- Group a package's exceptions under one base class so callers can catch the whole package broadly or one error narrowly ([Built-in Exceptions](https://docs.python.org/3/library/exceptions.html#Exception)).

```python
class AppError(Exception): ...
class ConfigError(AppError): ...
class NetworkError(AppError): ...
```

### Catching exceptions

- Catch specific exception types ordered narrow-to-broad, placing `except FileNotFoundError:` before `except OSError:`, because Python runs the first matching handler and a broad clause first would mask the specific one ([Built-in Exceptions](https://docs.python.org/3/library/exceptions.html#OSError)).
- Never write a bare `except:`; it also catches `KeyboardInterrupt` and `SystemExit` and traps the process ([Built-in Exceptions](https://docs.python.org/3/library/exceptions.html#KeyboardInterrupt)).
- When you genuinely need breadth, write `except Exception:` and then log the error or re-raise it; never write `except ...: pass`, because a silent pass hides the failure ([PEP 20](https://peps.python.org/pep-0020/)).

### Chaining

- Chain causes with `raise NewError(...) from original` to preserve the original traceback as the cause ([Built-in Exceptions](https://docs.python.org/3/library/exceptions.html#exception-context)).
- Append `from None` to deliberately suppress the original context when it is noise rather than signal ([Built-in Exceptions](https://docs.python.org/3/library/exceptions.html#exception-context)).

```python
raise ConfigError("bad config") from e
```

### Reuse standard built-ins

- Reuse the standard built-in exceptions instead of inventing equivalents, because callers already know their meaning ([Built-in Exceptions](https://docs.python.org/3/library/exceptions.html)):
  - Raise `ValueError` for a value of the right type but an unacceptable value.
  - Raise `TypeError` for a wrong type or an unsupported operation on a type.
  - Raise `KeyError` for a missing mapping key and `IndexError` for an out-of-range sequence index; catch both together as `LookupError`.
  - Raise `AttributeError` for a missing attribute.
  - Raise from the `OSError` family for system errors, using the specific subclass: `FileNotFoundError`, `PermissionError`, or `TimeoutError`.
  - Raise `NotImplementedError` when an abstract method is not overridden; do not confuse it with the `NotImplemented` singleton, which a binary special method returns to signal "try the reflected operation" ([Built-in Exceptions](https://docs.python.org/3/library/exceptions.html#NotImplementedError), [Built-in Constants](https://docs.python.org/3/library/constants.html#NotImplemented)).
  - Raise `RuntimeError` as the generic fallback when no more specific class fits.
  - Raise `ArithmeticError` for arithmetic faults and `ZeroDivisionError` for division by zero.

### Concurrent exceptions and context

- Raise an `ExceptionGroup` and handle it with `except*` (3.11+) when multiple exceptions surface concurrently, for example from an `asyncio.TaskGroup` ([Built-in Exceptions](https://docs.python.org/3/library/exceptions.html#ExceptionGroup)).
- Attach context to an in-flight exception with `e.add_note("...")` (3.11+) so the traceback carries the extra detail ([Built-in Exceptions](https://docs.python.org/3/library/exceptions.html#BaseException.add_note)).

### Structure

- Keep each `try` block small, wrapping only the statements that can raise, so the handler catches the intended failure and not an unrelated one ([Built-in Exceptions](https://docs.python.org/3/library/exceptions.html)).
- Prefer raising an exception over returning an error sentinel, because an unchecked sentinel propagates as bad data while an exception halts the path ([PEP 20](https://peps.python.org/pep-0020/)).
- Release resources with `finally` or a context manager, so cleanup runs whether or not an exception propagates ([Built-in Exceptions](https://docs.python.org/3/library/exceptions.html)).


## 4. API Design

Design interfaces around shape, data carriers, and a minimal public surface. This section defines ABC (Abstract Base Class, [`abc` docs](https://docs.python.org/3/library/abc.html)) at first use below.

### Boundary interfaces: Protocol vs ABC

- Prefer `typing.Protocol` for duck-typed interfaces at boundaries, because a class conforms by shape (its methods and attributes) with no inheritance or registration required ([PEP 544](https://peps.python.org/pep-0544/)).
  ```python
  from typing import Protocol
  class Readable(Protocol):
      def read(self, n: int) -> bytes: ...
  def consume(src: Readable) -> bytes:
    return src.read(10)
  ```
- Choose `Protocol` when you cannot modify the implementing classes, when you want library-agnostic interfaces, or when you need only static checking, because structural typing binds unrelated types without touching their definitions ([PEP 544](https://peps.python.org/pep-0544/)).
- Choose an ABC (Abstract Base Class) when you control the hierarchy and want shared implementation, an explicit `register()` call, or runtime enforcement of the contract, because an ABC gives inherited method bodies and raises `TypeError` on instantiation of an incomplete subclass ([`abc` docs](https://docs.python.org/3/library/abc.html)).
- Add `@runtime_checkable` to a Protocol only when you need `isinstance` against it, and know it checks member presence only, not method signatures, so a matching name with a wrong signature still passes ([PEP 544](https://peps.python.org/pep-0544/)).

### Data carriers

- Prefer `@dataclasses.dataclass` for plain records, because it generates `__init__`, `__repr__`, and `__eq__` from annotated fields instead of hand-written boilerplate ([`dataclasses` docs](https://docs.python.org/3/library/dataclasses.html)).
- Pass `frozen=True` for immutable value objects, because it blocks attribute reassignment and makes instances hashable ([`dataclasses` docs](https://docs.python.org/3/library/dataclasses.html)).
- Pass `slots=True` to cut per-instance memory and forbid stray attributes, because `__slots__` removes the instance `__dict__` and rejects any name not declared as a field ([`dataclasses` docs](https://docs.python.org/3/library/dataclasses.html)).
- Pass `kw_only=True` for wide constructors, because keyword-only fields remove positional-argument ambiguity when a class has many fields ([`dataclasses` docs](https://docs.python.org/3/library/dataclasses.html)).
- Never write a mutable default such as `field: list = []`; use `field: list = dataclasses.field(default_factory=list)`, because one shared default is created at class-definition time and every instance would mutate the same object ([`dataclasses` docs](https://docs.python.org/3/library/dataclasses.html)).
  ```python
  import dataclasses

  @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
  class Point:
      x: float
      y: float
      tags: list[str] = dataclasses.field(default_factory=list)
  ```
- Reach for third-party carriers when the stdlib is not enough: use [`attrs`](https://www.attrs.org/) for richer field features, and use [`pydantic`](https://docs.pydantic.dev/) when you need validation and serialization at external boundaries, because pydantic coerces and validates input data that a dataclass accepts unchecked.

### Public surface

- Expose the minimum, and mark every internal module, class, function, or attribute with a single leading underscore, because a leading underscore signals non-public to readers and tools ([PEP 8](https://peps.python.org/pep-0008/#descriptive-naming-styles)).
- Declare the intended public API with `__all__` in every module that has one, because `__all__` names the exports a wildcard import re-exports and documents the supported surface ([`import` reference](https://docs.python.org/3/reference/import.html#the-import-system)).
- Keep parameter lists small, and place optional flags after a bare `*` to force keyword-only arguments, because keyword-only flags prevent call sites from passing them positionally in the wrong order.
  ```python
  def render(text: str, *, wrap: bool = False, indent: int = 0) -> str: ...
  ```

### Return types

- Return one type per function where practical, because a single return type lets callers and static checkers reason without branching on the result's shape.
- Prefer raising an exception over returning a sentinel such as `None` or `-1` on failure, because a sentinel silently propagates until it corrupts unrelated code, while an exception stops at the fault (see Section 3).
- Make illegal states unrepresentable with `Literal` or `enum.Enum` instead of free strings, because a fixed set of values lets the type checker reject a typo that a bare `str` would accept ([`typing.Literal`](https://docs.python.org/3/library/typing.html#typing.Literal), [`enum` docs](https://docs.python.org/3/library/enum.html)).
  ```python
  from typing import Literal
  def open_mode(mode: Literal["r", "w", "a"]) -> None: ...
  ```

### functools idioms

- Apply `@functools.cache` or `@functools.lru_cache` to pure, expensive calls, because they memoize results by arguments and skip recomputation; use `cache` for an unbounded store and `lru_cache(maxsize=N)` to cap it ([`functools` docs](https://docs.python.org/3/library/functools.html#functools.cache)).
- Apply `@functools.cached_property` to a lazy per-instance value, because it computes once on first access and stores the result on the instance ([`functools` docs](https://docs.python.org/3/library/functools.html#functools.cached_property)).
- Use `functools.partial` instead of a trivial wrapper lambda to pre-bind arguments, because `partial` carries a name and is picklable where a lambda is neither ([`functools` docs](https://docs.python.org/3/library/functools.html#functools.partial)).
- Apply `@functools.wraps` inside every decorator, because it copies `__name__`, `__doc__`, and `__wrapped__` from the wrapped function so introspection and tooling see the original ([`functools` docs](https://docs.python.org/3/library/functools.html#functools.wraps)).
  ```python
  import functools

  def logged(f):
      @functools.wraps(f)
      def wrapper(*args, **kwargs):
          return f(*args, **kwargs)
      return wrapper
  ```
- Use `functools.singledispatch` for a function whose behavior varies by the type of its first argument, because it dispatches on registered types instead of an `isinstance` ladder ([`functools` docs](https://docs.python.org/3/library/functools.html#functools.singledispatch)).


## 5. Project Layout & Packaging

Configure the whole project in one `pyproject.toml`; put build config, metadata, dev dependencies, and tool settings there so a single file drives packaging (PyPUG — [Python Packaging User Guide](https://packaging.python.org/) — [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)).

- Include `[build-system]` (the PEP 517/PEP 518 build interface) with `requires` (build-time dependencies) and `build-backend` (the backend import path) in every distributable package; omit it only from a pure application managed by uv that is never built or published, since nothing consumes the build interface there ([PEP 517](https://peps.python.org/pep-0517/), [PEP 518](https://peps.python.org/pep-0518/)).
- Declare project metadata in `[project]` (PEP 621): set `name`, `version` (or list it under `dynamic`), `description`, `readme`, `requires-python`, `license`, `authors`, and `dependencies` so tools and indexes read a standard, tool-agnostic table ([PEP 621](https://peps.python.org/pep-0621/)).
- Declare install-time extras under `[project.optional-dependencies]`, console entry points under `[project.scripts]`, and project links under `[project.urls]`, keeping each concern in its named PEP 621 table ([PEP 621](https://peps.python.org/pep-0621/)).
- Put dev-only dependencies in `[dependency-groups]` (PEP 735), not in `[project.optional-dependencies]`, because dependency groups are local dev tooling that is never published as installable extras ([PEP 735](https://peps.python.org/pep-0735/)).
- Place every tool's configuration under its own `[tool.*]` namespace so tool settings live beside the project without colliding ([PEP 518](https://peps.python.org/pep-0518/)).
- Select a build backend by need: use hatchling (`"hatchling.build"`), the modern PyPA — Python Packaging Authority — default; use setuptools (`"setuptools.build_meta"`, `requires = ["setuptools>=61"]`) for the legacy ecosystem; use flit-core for minimal pure-Python packages; use pdm-backend for the PDM workflow ([Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)).
- Build artifacts with `python -m build`, which is backend-agnostic and emits both an sdist (`.tar.gz`) and a wheel (`.whl`) into `dist/`, instead of calling a backend directly ([Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)).
- Use src-layout for anything distributed or seriously tested, moving import packages under `src/`; this forces an install before import so tests run against the installed copy ([src vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)).
- Never use flat layout for a distributed or tested package; the current directory is first on the import path, so a flat layout can silently import the in-tree copy instead of the installed one and hide packaging errors — use src-layout to catch them ([src vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)).
- Reserve flat layout for tiny scripts that are never installed, where no install step exists to diverge from ([src vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)).

EXAMPLE src-layout tree:

```
myproject/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── mypkg/
│       ├── __init__.py
│       └── core.py
└── tests/
    └── test_core.py
```

EXAMPLE minimal `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "mypkg"
version = "0.1.0"
description = "Short summary."
readme = "README.md"
requires-python = ">=3.12"
license = "MIT"
authors = [{ name = "Your Name", email = "you@example.com" }]
dependencies = ["httpx>=0.27"]

[project.optional-dependencies]
cli = ["typer>=0.12"]

[project.scripts]
mypkg = "mypkg.cli:main"

[dependency-groups]
dev = ["pytest>=8", "ruff>=0.6", "mypy>=1.13"]
```


## 6. Dependencies & Environments

- Manage dependencies with uv, the lockfile-based tool, because it resolves, locks, and syncs from one interface; see [uv projects](https://docs.astral.sh/uv/concepts/projects/).
- Commit the `uv.lock` file to version control, because a committed lock is what makes an environment reproducible across machines and in CI (Continuous Integration, the automated build-and-test pipeline that runs on every push).
- Declare project metadata and dependencies in `pyproject.toml`, and let uv record the resolved graph in a committed `uv.lock`; uv's universal resolution produces one cross-platform lock that resolves for every supported platform, not just the current one.
- Add a dependency with `uv add <pkg>`, which edits `pyproject.toml`, updates `uv.lock`, and syncs `.venv` in one step, instead of hand-editing `pyproject.toml` and re-locking separately.
- Remove a dependency with `uv remove <pkg>`, which reverses `uv add` by editing metadata, updating the lock, and syncing `.venv`.
- Run `uv sync` to make `.venv` match `uv.lock` exactly, adding missing packages and removing extras, when you need the environment to mirror the committed lock.
- Run `uv lock` to re-resolve the dependency graph and refresh `uv.lock` when you want new versions without changing declared dependencies.
- Run commands with `uv run <cmd>` to execute in the synced environment, because it guarantees the command sees exactly the locked dependencies rather than whatever is globally installed.
- Let uv manage `.venv` and download the required interpreter automatically; do not create the virtual environment or install Python by hand.
- Omit `[build-system]` only in a pure application managed by uv that is never built or published, because nothing is built or published there.
- Include `[build-system]` in every distributable package and use src-layout, then build and publish with `uv build` and `uv publish`; see Section 5 for the src-layout tree.
- Declare development and test dependencies under `[dependency-groups]` and add them with `uv add --dev`, because these tools must not ship to runtime consumers.
- Pin `requires-python = ">=3.12"` in `[project]`, because the rules and syntax in this rulebook target Python 3.12 and newer.
- Keep development and test dependencies out of the runtime `dependencies` array and in `[dependency-groups]` instead, because a consumer installing your package must not pull in `pytest`, `ruff`, or `mypy`.
- Run a dependency audit in CI against the committed lockfile, using `pip-audit` (see [pip-audit](https://pypi.org/project/pip-audit/)) or uv's audit tooling, because auditing the lock checks the exact versions that will be installed.
- Keep the lock current with scheduled updates (re-run `uv lock` on a fixed interval such as weekly), because a stale lock accumulates unpatched vulnerabilities between releases.


## 7. Imports

- Prefer absolute imports (`from mypkg.core import x`); they survive module moves and renames, and they name the origin package explicitly so a reader traces any symbol to its source. See the [import system reference](https://docs.python.org/3/reference/import.html).
- Use explicit relative imports only for intra-package references (`from . import util`, `from .core import x`); reserve them for siblings within the same package, and switch to an absolute import for anything outside it. See [PEP 328](https://peps.python.org/pep-0328/).
- Never write implicit relative imports (`import util` expecting a sibling module); they do not exist in Python 3, so a bare `import util` resolves only against the top-level path and fails for a package member. Write `from . import util` instead. See [PEP 328](https://peps.python.org/pep-0328/).
- Write one import per line for `import x` statements (`import os` then `import sys` on separate lines, never `import os, sys`); one name per line keeps diffs minimal and each import independently greppable. Combining names with `from pkg import a, b` on one line stays acceptable.
- Group imports into 3 blocks in this order: standard library, third-party, then local; separate the blocks with 1 blank line and alphabetize the entries within each block; place every import at the top of the module after the docstring and any `from __future__` import. Ruff's `I` rules automate this grouping and ordering. See the [import system reference](https://docs.python.org/3/reference/import.html).
  - EXAMPLE:
    ```python
    """Module docstring."""

    import os
    import sys

    import httpx

    from mypkg.core import x
    ```
- Never use wildcard imports (`from x import *`); they hide which names enter the namespace and let a source silently shadow locals, so import each name explicitly (`from x import a, b`). The one accepted use is deliberate re-export in a package `__init__.py` paired with an explicit `__all__` that lists the public names. See the [import system reference](https://docs.python.org/3/reference/import.html).
- Keep `__init__.py` light: run minimal side effects at import time and place heavy logic in submodules, because every importer of the package pays the cost of `__init__.py` and import-time work slows startup and creates cycles.
- Break an import cycle by moving the shared code into a lower-level module that both sides import, restructuring the ownership so the dependency runs one direction, or deferring the import into the function that needs it (a local `import` inside the function body runs at call time, after both modules finish loading). Prefer moving or restructuring; use a deferred import when the other two are impractical. See the [import system reference](https://docs.python.org/3/reference/import.html).
- Add an `__init__.py` to make a directory a normal (regular) package; omit it only when a namespace package is intended, because a directory without `__init__.py` becomes an implicit namespace package (PEP 420) whose contents may span multiple directories or distributions. Choose a namespace package deliberately to split one import package across separate installable pieces; otherwise ship the `__init__.py`. See [PEP 420](https://peps.python.org/pep-0420/).


## 8. Documentation

Encode docstring form, convention detection, and comment intent. Sources: PEP 257 ([Docstring Conventions](https://peps.python.org/pep-0257/)); Ruff [pydocstyle `D` rules](https://docs.astral.sh/ruff/rules/#pydocstyle-d); Sphinx [napoleon](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html).

- Write a docstring as a string literal placed as the first statement of a module, class, or function; a string in any later position is a bare expression, not a docstring, and tools will not read it as one.
- Use triple double-quotes `"""..."""` for every docstring including one-liners, never single quotes or `'''`, so quotes and apostrophes inside the text need no escaping and the form stays uniform.
- Write the summary line in the imperative mood ("Return the sum", not "Returns the sum"), ending with a period, because PEP 257 prescribes the imperative and the trailing period marks a complete sentence.
- Write a one-liner with opening and closing quotes on the same line and no blank line before or after it: `"""Return the sum of a and b."""`.
- Write a multi-line docstring as the summary line, then one blank line, then the body, then the closing `"""` on its own line, so the summary stays extractable by tools that read only the first line.
- Document every public module, class, and function with a docstring; leave undocumented only names with a single leading underscore, which are non-public.
- Enforce docstring presence and form with Ruff's `D` rule family; if a public name cannot carry a docstring for a stated reason, suppress it narrowly with `# noqa: D<code>` rather than disabling the family.
- Deduce the docstring convention from the existing code and match it; the three Ruff conventions are `google`, `numpy`, and `pep257`, and imposing a new one fragments the codebase and breaks Sphinx rendering.
- If the existing code is empty, mixed, or otherwise leaves the convention unclear, ask the human which of `google`/`numpy`/`pep257` to use rather than guessing, and set that value under `[tool.ruff.lint.pydocstyle]` once chosen.
- Write structured `Args:`/`Returns:`/`Raises:` sections in Google style or their NumPy equivalents; Sphinx `napoleon` parses both into reference documentation, so the same source serves the reader and the docs build.
- EXAMPLE (Google style):
  ```python
  def fetch(url: str, timeout: float = 5.0) -> bytes:
      """Fetch a URL and return its body.

      Args:
          url: Absolute HTTP(S) URL.
          timeout: Seconds before giving up.

      Returns:
          Raw response bytes.

      Raises:
          TimeoutError: If the request exceeds ``timeout``.
      """
  ```
- Write comments that explain why the code does what it does, not what it does; the code already states the what, so a restating comment adds tokens and no information.
- Update every comment in the same edit that changes the code it describes; a stale comment that contradicts the code misleads the next reader more than no comment would.


## 9. Testing

- Write tests with pytest and plain `assert`; pytest rewrites `assert` to show operand values on failure, so drop `unittest` boilerplate (`TestCase`, `self.assertEqual`, `self.assertTrue`) in favor of `assert x == y`. See the [pytest docs](https://docs.pytest.org/en/stable/).
- Follow pytest's discovery defaults so tests are collected without extra config: name files `test_*.py` or `*_test.py`, name test functions `test_*`, and name test classes `Test*` with no `__init__` method (a constructor blocks collection of that class).
- Use `@pytest.fixture` for setup, and request a fixture by naming it as a test-function parameter; this makes each test's dependencies explicit and reusable.
- Choose the narrowest fixture scope that works, widening only when a test needs it: `function` (the default, fresh per test, best isolation), then `class`, `module`, `package`, `session`; a wider scope shares state across tests and trades isolation for speed, so widen only to amortize expensive setup.
- Use `yield` in a fixture to separate setup from teardown: code before `yield` sets up, code after `yield` tears down and runs even when the test fails.
- Put fixtures shared across multiple test files in `conftest.py`; pytest auto-discovers it per directory, so never import it.
- Use `@pytest.mark.parametrize` for table-driven cases; one parametrized function replaces many near-duplicate tests and reports each case separately.
  - EXAMPLE:
    ```python
    @pytest.mark.parametrize("n, expected", [(2, 4), (3, 9), (4, 16)])
    def test_square(n, expected):
        assert square(n) == expected
    ```
- Measure coverage with pytest-cov and fail the run below a fixed threshold: `pytest --cov=pkg --cov-fail-under=90` exits non-zero under 90% coverage, turning coverage into a CI (Continuous Integration) gate. See [pytest-cov](https://pytest-cov.readthedocs.io/).
- Run the test suite across multiple Python versions with [tox](https://tox.wiki/) or [nox](https://nox.thea.codes/), which build isolated per-version environments; use them to prove support for every version in `requires-python`.
- Keep each test fast, isolated, and deterministic: assert one behavior per test, depend on no other test's ordering or leftover state, and remove sources of nondeterminism (fix clocks, seed randomness, stub network calls) so a green run means the same thing every time.
- Test the installed package, not the in-tree source, by pairing tests with the src-layout from Section 5; src-layout forces an install before import, so the suite exercises the copy users receive rather than the working directory.


## 10. Tooling

Use [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting; it replaces Flake8, isort, pydocstyle, pyupgrade, and Black, so one tool and one config cover the whole toolchain instead of five.

- Run `ruff check --fix` to lint and auto-fix, and run `ruff format` to format; these two commands supersede Flake8, isort, pydocstyle, pyupgrade, and Black entirely.
- Gate CI (Continuous Integration) with `ruff check` and `ruff format --check`; the `--check` flag reports formatting drift without rewriting files, so CI fails on unformatted code instead of silently reformatting it.
- Configure Ruff under `[tool.ruff]` in `pyproject.toml`; keeping config in one file matches the single-config packaging convention.
- Select rule families by prefix under `[tool.ruff.lint]`: `E`/`W` (pycodestyle), `F` (Pyflakes), `I` (isort), `D` (pydocstyle), `UP` (pyupgrade), `B` (bugbear), `N` (naming), `SIM`, `C4`, `PT`; each prefix opts into a whole family, so pick families rather than listing individual codes.
- Suppress a violation narrowly with an inline `# noqa: E501` naming the exact code, or with `per-file-ignores` for a path pattern; never use a bare `# noqa`, which silences every rule on the line and hides new violations.

  ```toml
  [tool.ruff]
  target-version = "py312"
  line-length = 88  # Black/Ruff default; match the codebase's existing width instead
  [tool.ruff.lint]
  select = ["E", "F", "I", "D", "UP", "B", "SIM"]
  [tool.ruff.lint.pydocstyle]
  convention = "google"  # match the codebase's existing docstring convention instead (see Section 8)
  [tool.ruff.lint.per-file-ignores]
  "tests/*" = ["D"]
  ```

Use [mypy](https://mypy.readthedocs.io/en/stable/) as a CI gate so type errors fail the build rather than reaching runtime.

- Configure `[tool.mypy]` with `strict = true`; strict mode turns on the full set of strictness flags at once, so you inherit new checks as mypy adds them.
- Adopt mypy incrementally by loosening individual modules with `[[tool.mypy.overrides]]` rather than lowering the global setting; this keeps strictness everywhere except the legacy modules you name.
- Install `types-*` stub packages for typed dependencies that ship their hints separately, so mypy sees real signatures instead of `Any`.
- Silence untyped third-party libraries with `ignore_missing_imports` scoped to those modules; this suppresses the missing-stub error only for libraries with no types, not for your own code.

  ```toml
  [tool.mypy]
  python_version = "3.12"
  strict = true  # already enables warn_unused_ignores and other strict flags
  [[tool.mypy.overrides]]
  module = ["legacy.*"]
  disallow_untyped_defs = false
  ```

Wire [pre-commit](https://pre-commit.com/) so the same checks run before every commit and again in CI, making local results equal CI results.

- Define hooks in `.pre-commit-config.yaml` and pin each repo by `rev`; a pinned `rev` makes every machine run the identical hook version, so results are reproducible.
- Run `pre-commit install` once per clone to set the git hook, so the checks run automatically on `git commit`.
- Run the same config in CI with `pre-commit run --all-files`; running one shared config in both places keeps local equal to CI instead of drifting apart.
- Run `pre-commit autoupdate` to bump each `rev` to the latest release; schedule it deliberately rather than editing revs by hand, so pins stay both current and explicit.
- Use the official mirrors `astral-sh/ruff-pre-commit`, `pre-commit/mirrors-mypy`, and `pre-commit/pre-commit-hooks` (the last for whitespace, end-of-file, and YAML hooks); the official mirrors track upstream releases, so hooks match the tools you run directly.

  ```yaml
  repos:
    - repo: https://github.com/pre-commit/pre-commit-hooks
      rev: v5.0.0
      hooks:
        - id: trailing-whitespace
        - id: end-of-file-fixer
        - id: check-yaml
    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v0.8.0
      hooks:
        - id: ruff
          args: [--fix]
        - id: ruff-format
    - repo: https://github.com/pre-commit/mirrors-mypy
      rev: v1.13.0
      hooks:
        - id: mypy
  ```


## 11. Performance

- Profile before optimizing; find hot spots with [`cProfile`](https://docs.python.org/3/library/profile.html) and microbenchmark candidate changes with [`timeit`](https://docs.python.org/3/library/timeit.html), because measured cost, not intuition, locates the code worth changing.
- Never optimize on a guess; run `cProfile` first and change only the functions the profile ranks highest.
- Hoist repeated global, attribute, or method lookups into locals inside tight loops, because local names resolve faster than global or attribute lookups on every iteration.
  - EXAMPLE:
    ```python
    append = result.append          # bind the method once, outside the loop
    for x in data:
        append(f(x))                # local lookup each iteration, not result.append
    ```
- Prefer generators and generator expressions over building an intermediate list when the whole sequence is not needed at once, because a generator yields one item at a time and holds only the current one in memory.
  - EXAMPLE:
    ```python
    total = sum(x * x for x in data)   # streams; no intermediate list allocated
    ```
- Build strings with `''.join(parts)`, never repeated `+=` in a loop, because `+=` reallocates and copies the whole string each time, making assembly O(n^2), while `join` is O(n).
  - EXAMPLE:
    ```python
    parts = [render(row) for row in rows]
    text = ''.join(parts)              # O(n); not `s += render(row)` in a loop
    ```
- Prefer built-ins and comprehensions over hand-written Python loops for the same work, because their loops run in C rather than in interpreted Python.
  - EXAMPLE:
    ```python
    squares = [x * x for x in data]    # C-level loop, not an append loop
    biggest = max(data)                # built-in, not a manual running maximum
    ```
- Let readability win until a profile proves a given line sits on a hot path; keep any micro-optimization local to that line and add a comment stating the reason and the profile finding that justified it, so a later reader does not "clean up" the ugliness back into a slow form.
- Source: [Programming FAQ](https://docs.python.org/3/faq/programming.html).


## 12. Concurrency

- Choose the concurrency model by workload: waiting on I/O -> threads or asyncio; computing on CPU -> processes.
- Reach for `ThreadPoolExecutor` when the work is I/O-bound with few or simple tasks.
- Reach for asyncio when the work is I/O-bound with massive concurrency (thousands of simultaneous waits).
- Reach for `ProcessPoolExecutor`/`multiprocessing` when the work is CPU-bound, to get true parallelism across cores.
- For mixed workloads, run I/O on asyncio and offload CPU chunks to processes.
- Define GIL as the [Global Interpreter Lock](https://docs.python.org/3/glossary.html#term-global-interpreter-lock), the mutex that lets only one thread execute Python bytecode at a time, so pure-Python threads never run in parallel.
- Define IPC as Inter-Process Communication, the mechanisms (pipes, queues, shared memory) that move data between separate processes.

### asyncio

- Use [asyncio](https://docs.python.org/3/library/asyncio.html) for single-threaded cooperative concurrency on I/O; expect no CPU speedup, because all coroutines share one thread.
- Start the event loop once with `asyncio.run(main())`, never by manually creating and closing loops.
- Never call `time.sleep`, blocking I/O, or heavy CPU inside a coroutine; use `await asyncio.sleep(...)` and async libraries instead, because a blocking call freezes every task on the single loop thread.
- Offload unavoidable blocking work with `await asyncio.to_thread(fn, ...)` or `loop.run_in_executor(...)`, which move it off the loop thread and keep other tasks running.
- Run coroutines concurrently with `asyncio.TaskGroup` (3.11+); prefer it, because it is structured and cancels sibling tasks when one fails.
- Use `asyncio.gather` only when you need its flat result list and do not need structured cancellation.
- Keep a reference to every `asyncio.create_task(...)` result (e.g. in a set) until it completes, because the loop holds only a weak reference and an unreferenced task can be garbage-collected mid-run.

### concurrent.futures

- Use [concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html) for one swappable `Executor` API across threads and processes.
- Use `ThreadPoolExecutor` for I/O-bound work: the GIL is released during blocking I/O so threads overlap, arguments need no pickling, and workers share memory.
- Use `ProcessPoolExecutor` for CPU-bound work: it gives true parallelism, but arguments and results are pickled and it carries higher startup and IPC cost.
- Manage every executor with `with Executor() as ex:`, which shuts down and joins workers on exit.
- Submit work with `ex.map(fn, iterable)` for ordered results or `ex.submit(fn, *args)` for individual futures.
- Iterate `as_completed(futures)` to consume results in finish order rather than submission order.
- Call `fut.result()` to retrieve a value, knowing it re-raises any exception the worker raised.

### multiprocessing

- Use [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) for real CPU parallelism, because each process has its own interpreter and its own GIL.
- Move data between processes through `Queue` or `Pipe` (values are pickled) or through shared memory (`Value`, `Array`, `shared_memory`) to avoid copying large buffers.
- Know the start methods: `spawn` (default on Windows and macOS) launches a fresh interpreter that is safe but slower, while `fork` is fast but unsafe when the parent holds threads or locks.
- Prefer `spawn` when the parent uses threads or locks, because a forked child can deadlock on a lock copied in a held state.
- Always guard the process entry point so a re-imported child does not re-run startup code and spawn processes recursively.
  - EXAMPLE:
    ```python
    if __name__ == "__main__":
        main()
    ```

### PEP 703 free-threaded build

- Treat the [PEP 703](https://peps.python.org/pep-0703/) free-threaded, no-GIL CPython as experimental; it ships opt-in in 3.13 as the `python3.13t` interpreter.
- Expect true parallel pure-Python threads on that build, but weigh its single-thread overhead and its C-extension compatibility risk.
- Choose processes for CPU parallelism in portable code today, because the free-threaded build is not yet the default and not every extension supports it.


## 13. Gotchas & Anti-patterns

- Never write a mutable default argument; a default is evaluated once at definition time and shared across every call, so appends accumulate between callers.
- Default a mutable parameter to `None`, then build the real value inside the body, so each call gets a fresh object.
  ```python
  def f(items=[]):        # BUG: same list every call
      items.append(1); return items
  def f(items=None):      # FIX: sentinel
      if items is None: items = []
      items.append(1); return items
  ```
- Never capture a loop variable by free reference in a closure; a late-binding closure looks up the variable when it runs, not when it is defined, so every closure sees the loop's final value.
- Bind the loop variable per iteration with a default argument, so each closure captures its own value.
  ```python
  fns = [lambda: i for i in range(3)]      # BUG: all return 2
  fns = [lambda i=i: i for i in range(3)]  # FIX: bind per iteration
  ```
- Never write a bare `except:` or a silent `except ...: pass`; a bare clause also swallows `KeyboardInterrupt` and `SystemExit`, and a silent pass hides the failure entirely — catch the specific exception and log it or re-raise (Section 3).
- Never keep broad module-level mutable global state; it couples callers through hidden shared state and defeats testing — pass the value in as an argument, inject the dependency, or hold it on a class instance. Module-level constants are fine.
- Never import `typing.List`, `Optional`, or `Union`; they are legacy aliases superseded on Python 3.12 — write `list`, `X | None`, and `X | Y` (Section 2).
- Never use a wildcard import (`from x import *`) except as a deliberate re-export in a package `__init__.py` paired with `__all__`; it pollutes the namespace and hides a symbol's origin — list the names you use explicitly (Section 7).
- Never compare types with `type(x) == T`; it rejects valid subclasses — use `isinstance(x, T)`, which respects the subtype relationship.
- Never build a string with repeated `+=` in a loop; each concatenation reallocates and copies, giving O(n²) work — collect the parts and call `''.join(...)` for a single O(n) pass.
- Never ship a distributed package in a flat layout; the current directory sits first on the import path, so tests silently import the in-tree copy instead of the installed one — use src-layout to force an install before import (Section 5).
- Never make a blocking call inside a coroutine; blocking I/O, `time.sleep`, or heavy CPU freezes the entire event loop and every other task — offload it with `await asyncio.to_thread(fn, ...)` or `loop.run_in_executor(...)` (Section 12).

Sources: [Programming FAQ](https://docs.python.org/3/faq/programming.html); [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
