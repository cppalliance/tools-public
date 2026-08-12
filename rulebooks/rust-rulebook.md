---
description: Reference for a model writing or maintaining Rust - project layout, naming, ownership, API design, errors, crates, documentation, testing, tooling, performance, async, and unsafe
---

<!-- Load this file into context before writing or reviewing Rust. Highest-value reference only; consult doc.rust-lang.org for depth. -->

# Rulebook: Writing Rust

This file equips a model to write, extend, and maintain Rust. Read the preamble and the closing rules first; they bind every edit. Sections run from most to least frequently needed and are consulted one at a time, so the length of this file is never the number of rules you hold at once. Terms used throughout: "the crate" is one unit of compilation and publication; "a member" is one crate inside a workspace; "the tree" is the repository checkout; "a target" is one buildable artifact, meaning a lib, bin, test, bench, or example. Target current stable Rust with edition 2024 and resolver 3.

![The Rust Workshop](images/rust-rulebook.png)

## Non-negotiable rules

Follow these on every change; they are restated at the end.

- Fix a borrow error by restructuring ownership, never by reaching for `unsafe` (section 4); `unsafe` cannot satisfy the borrow checker and it converts a compile error into undefined behavior.
- Return `Result` for every expected failure and reserve panics for bugs (section 5); a library that panics on bad input takes the decision away from its caller.
- Set lint levels in the `[lints]` tables of `Cargo.toml`, not in `#![deny(...)]` at the crate root (section 12); a source-level deny breaks a downstream build the moment a new compiler adds a lint.
- Document every public item, giving `# Errors`, `# Panics`, and `# Safety` where they apply, and write each example as a doctest (section 10); an example that is not compiled rots silently.
- Add a test in the same change as the code (section 11); a change without a test is incomplete, because nothing guards against regression.
- Run `cargo fmt --all --check` and `cargo clippy --all-targets --all-features -- -D warnings` before every commit (section 12); both questions are settled by the tool, not by taste.
- Verify a crate is the intended, existing package before adding it to `Cargo.toml` (section 9); a hallucinated or near-miss name compiles like any other and turns a typo into a supply-chain compromise.

## 1. Orientation

A crate is one unit of compilation and publication. A workspace is a set of crates sharing one `Cargo.lock` and one `target/`. Start with a single crate; convert to a workspace when a second publishable or independently testable artifact exists.

Canonical single crate:

```
mycrate/
  Cargo.toml            # metadata, [features], [lints], rust-version
  Cargo.lock            # committed, for libraries and binaries alike
  src/lib.rs            # facade: crate docs, crate lints, mod, pub use
  src/searcher.rs       # one domain concept per file
  src/searcher/glue.rs  # children sit beside searcher.rs, no mod.rs
  src/sys/unix.rs       # platform code, one module per platform
  tests/it/main.rs      # the single integration-test binary
  benches/parse.rs      # harness = false
  examples/demo.rs      # compiled by cargo test, never doctested
  build.rs              # only for native code or real codegen
```

Canonical workspace:

```
foo/
  Cargo.toml            # [workspace] virtual manifest, no [package]
  .cargo/config.toml    # aliases, linker, rustc-wrapper; no secrets
  rust-toolchain.toml   # only when pinning a toolchain
  crates/
    foo/                # facade, re-exports the public API
    foo-core/           # vocabulary types, no proc-macro dependencies
    foo-macros/         # proc-macro = true
    foo-sys/            # links = "...", extern declarations only
    foo-cli/            # src/main.rs, leaf crate
  xtask/src/main.rs     # repo automation, publish = false
```

Directory map (only what you edit often):

| Path | Holds |
|---|---|
| `src/lib.rs` | crate docs, crate-level attributes, `mod` declarations, `pub use` facade |
| `src/main.rs`, `src/bin/*.rs` | binary targets; keep the logic in the library and the argument handling here |
| `src/<concept>.rs`, `src/<concept>/` | one domain concept and its children |
| `tests/` | integration tests against the public API, one binary at `tests/it/main.rs` |
| `benches/`, `examples/` | benchmark and example targets, each one an extra link of the library |
| `Cargo.toml` | `[package]`, `[dependencies]`, `[features]`, `[lints]`, `[profile]` at the workspace root only |
| `.cargo/config.toml` | aliases, linker choice, `rustc-wrapper`; committed, so no credentials |
| `xtask/` | every repo command that is not a plain `cargo` subcommand |

## 2. Formatting and naming

Formatting is settled by the tool. Naming follows the standard library, so a reader can predict a name from its shape.

- Run `cargo fmt --all`; it owns spacing, wrapping, and brace placement.
- Keep `rustfmt.toml` down to `style_edition = "2024"`; bare `rustfmt` defaults to the 2015 style edition, so state it for tools that invoke rustfmt directly.
- Keep nightly-only rustfmt options (`group_imports`, `imports_granularity`, `wrap_comments`, `comment_width`) out of a repo whose CI formats with stable rustfmt, which ignores them and lets formatting diverge silently.
- Put a formatting-only change in its own commit and add the hash to `.git-blame-ignore-revs`.
- Group `use` declarations in three blocks separated by a blank line: `std`, `core`, and `alloc` first, then external crates, then `crate`, `super`, and `self`.
- Import types by name and reach free functions through their module: `use std::fmt;` then `fmt::Display`, and `cmp::max(a, b)`.
- Reserve glob imports for `use super::*;` inside `#[cfg(test)] mod tests` and for one documented `prelude` module.
- Wrap doc prose by hand near 80 columns; rustfmt does not reflow comments on stable.
- Comment the invariant and the reason; let names carry the what.

Casing, per item kind:

| Item kind | Convention | Example |
|---|---|---|
| Crates, modules | `snake_case`, one word where possible | `regex`, `btree_map` |
| Types, traits, enum variants, derive macros | `UpperCamelCase` | `IpAddr`, `FromStr`, `Ordering::Less` |
| Functions, methods, fields, locals | `snake_case` | `to_lowercase`, `window_width` |
| Function-like and attribute macros | `snake_case!` | `write!`, `#[tokio::main]` |
| Statics, consts, associated consts | `SCREAMING_SNAKE_CASE` | `GLOBAL_COUNT`, `u32::MAX` |
| Type and const generic parameters | concise `UpperCamelCase` | `T`, `K`, `V`, `E`, `N` |
| Lifetimes | short lowercase | `'a`, `'de`, `'src` |
| Cargo features | the thing itself, never `use-` or `with-` | `std`, `serde`, `derive` |

Treat an acronym as one word (`Uuid`, `HttpClient`, `Stdin`), and never split a single letter off in snake case (`btree_map`, not `b_tree_map`).

Conversion prefixes carry a cost and an ownership promise; match the receiver to the prefix:

| Prefix | Cost | Ownership | Receiver | Example |
|---|---|---|---|---|
| `as_` | free | borrowed to borrowed | `&self` | `str::as_bytes` |
| `to_` | expensive | borrowed to owned | `&self` | `Path::to_str` |
| `into_` | varies | owned to owned | `self` | `String::into_bytes` |
| `from_` | varies | none to owned | no receiver | `u64::from_str_radix` |

Put `mut` where it lands in the return type: `as_mut_slice`, not `as_slice_mut`.

Detect in existing code:

- a function, method, field, or local not in `snake_case`, or a type or trait not in `UpperCamelCase` - clippy's naming lints flag most.
- a `get_` prefix on a plain getter, or `as_` on a method that allocates - the prefix promises the wrong cost.
- a glob `use` outside a `#[cfg(test)]` module or one documented `prelude` - it hides where a name comes from.
- an acronym split across words (`b_tree_map`, `HTTP_client`) - treat an acronym as one word.

## 3. Idioms

Write code that reads as native Rust. Each rule below has a mechanical reason, and the pairs that follow show the correction.

- Use an iterator chain for a pure transform; keep a plain `for` loop when the body mutates outer state, needs `break` or `continue`, or the chain would run past three adapters.
- Use `let Some(x) = opt else { return Err(e) };` for a guard clause, so the happy path stays unindented. The `else` block has to diverge.
- Reach for `if let`, `while let`, `matches!`, and let chains before writing a `match` whose only product is a `bool`.
- Match exhaustively on an enum you own, so a new variant breaks the build; use a catch-all arm only for a foreign or `#[non_exhaustive]` enum.
- Propagate with `?` and implement `From` for the conversion; never hand-write `match r { Ok(v) => v, Err(e) => return Err(e.into()) }`.
- Take `&str`, `&[T]`, and `&Path`; return `String`, `Vec<T>`, and `PathBuf`. Take an owned argument only when you store it.
- Return `Cow<'_, str>` when the common case hands back the input unchanged.
- Derive `Debug`, `Clone`, and `PartialEq` on plain data; add `Eq` and `Hash` for map keys, `PartialOrd` and `Ord` for sorted types, `Copy` only for small plain data, and `Default` when a zero value is meaningful.
- Stop a combinator chain at two links; past that, a `match` or a `let ... else` reads better.
- Clone deliberately. Cloning an `Arc`, a `&str` you must own, or a small plain struct is correct; cloning inside a loop to quiet the borrow checker is a defect to restructure.
- Prefer `std::sync::LazyLock` and `OnceLock` to the `lazy_static` and `once_cell` crates.
- Leave `unwrap` out of library code; use `expect` with a message naming the invariant, or return the error.

Corrections:

- `fn parse(s: String)` -> `fn parse(s: &str)` - forces an allocation on a caller holding a slice.
- `fn total(v: &Vec<i64>)` -> `fn total(v: &[i64])` - accepts arrays and slices, one less indirection.
- `.iter().cloned()` on `&[u32]` -> `.iter().copied()` - `copied` cannot silently clone an expensive type.
- `arc.clone()` on an `Arc` or `Rc` -> `Arc::clone(&arc)` - a reference-count bump should read differently from a deep copy at the call site.
- `.collect::<Vec<_>>().len()` -> `.count()` - the allocation is pure waste.
- `if let Some(x) = o { .. } else { return Err(e) }` -> `let Some(x) = o else { return Err(e) };` - keeps the happy path unindented.
- `fn render(&self, fancy: bool, dark: bool)` -> `fn render(&self, style: Style, theme: Theme)` - booleans carry no meaning at the call site.
- `lazy_static! { static ref X: T = f(); }` -> `static X: LazyLock<T> = LazyLock::new(f);` - in the standard library, one fewer dependency.
- `once_cell::sync::OnceCell` -> `std::sync::OnceLock` - same reason.
- `let _ = mutex.lock();` -> `let _guard = mutex.lock();` - `let _` drops the guard at the semicolon.
- `s += &format!("{k}={v};")` in a loop -> `write!(&mut s, "{k}={v};")?` - `format!` allocates a throwaway `String` each pass.

Choose the signature by what you do with the value:

| Situation | Parameter | Return |
|---|---|---|
| Read text | `&str` | `String` |
| Read a sequence | `&[T]` | `Vec<T>` or `Box<[T]>` |
| Read a path | `&Path` | `PathBuf` |
| Usually borrowed, sometimes owned | `&str` | `Cow<'_, str>` |
| Store the value | `String`, `Vec<T>`, `T` | not applicable |
| Produce a lazy sequence | not applicable | `impl Iterator<Item = T> + '_` |
| Accept any implementation | `impl Trait` | not applicable |
| Heterogeneous or cold path | `&dyn Trait` | `Box<dyn Trait>` |

## 4. Ownership and borrowing

Most borrow errors are design errors with a mechanical fix. Own data at the top of the call tree and lend it downward; a borrow error means the ownership shape is wrong, not that the compiler is wrong.

- Own data at the top of the call tree and pass `&` or `&mut` downward; never restructure so that ownership travels upward.
- Return owned values from constructors and factories; a constructor that borrows constrains every caller's lifetimes.
- Default a method receiver to `&self`; escalate to `&mut self` only to mutate and to `self` only to consume.
- Pass the data a function needs, not the container that holds it: take `&mut [T]` unless you push or remove.
- Keep each `&mut` borrow shorter than the statement that needs it, ending it before the next conflicting access.
- Open a block or bind an intermediate `let` to end a borrow early, rather than redesigning ownership.
- Destructure `self` into field locals at the top of a `&mut self` method to get disjoint field borrows.
- Split a struct whose fields are repeatedly borrowed in conflicting pairs into two structs.
- Turn a conflicting `&mut self` method into a free function taking only the fields it touches.
- Use `HashMap::entry` with `or_insert_with`, `or_default`, or `and_modify` instead of `contains_key` then `get_mut` then `insert`.
- Model graphs, trees, and cyclic data as a `Vec<T>` plus a typed index, not as an `Rc<RefCell<Node>>` object graph.
- Newtype every index (`struct NodeId(u32)`) so mixing two index spaces is a type error.
- Use `mem::take`, `mem::replace`, `mem::swap`, or `Option::take` to move a value out from behind `&mut`.
- Store references in a struct only when the struct is a short-lived view, meaning an iterator, a guard, or a builder consumed in the same scope.
- Restructure a self-referential type into owned data plus `Range<usize>` offsets; that family of crates has a long history of soundness fixes.
- Read `T: 'static` as "contains no borrowed data", not as "lives forever".
- Reach for `thread::scope` when threads must borrow locals, and `move` plus owned data or `Arc` for `thread::spawn` and `tokio::spawn`.
- Break an `Rc` or `Arc` cycle with `Weak`; a cycle of strong handles leaks unconditionally.
- Hold a `MutexGuard` or a `RefCell` borrow for the shortest possible scope, and never across an `.await`.
- Clone to unblock yourself, commit that, then remove the clone in a separate pass. A `.clone()` whose only effect is to make a borrow error disappear is debt, not a fix: restructure the ownership, because the two copies drift apart. When auditing, hunt the clone whose removal reintroduces the borrow error, and replace it with a borrow or a field split.
- Delete the type annotation on a closure parameter when you hit E0521; the annotation invents a fresh lifetime.
- Write a lifetime annotation only when the compiler demands one; never restate what elision already infers.
- When one branch returns a reference into a value and later code mutates that value, move the mutation off the returning path or repeat the lookup, rather than cloning or reaching for `unsafe`; the borrow checker rejects this shape even when the paths never overlap at runtime. When auditing, the tell is a clone or `unsafe` added around an `if let`, `match`, or early-`return` arm that hands back a borrow.

Diagnose from the error code:

| Code | Cause | Fix |
|---|---|---|
| E0382 | use of a moved value | borrow instead of moving, clone, or reorder so the move is the last use |
| E0499 | two live `&mut` to one place | shorten the first borrow, destructure the fields, or `split_at_mut` |
| E0502 | `&` and `&mut` overlap | sequence the accesses, hoist the read into a local, or use `entry` |
| E0505 | move out of a borrowed value | end the borrow first, or pass `&` |
| E0506 | assign to a borrowed place | drop the borrow before assigning |
| E0507 | move out of borrowed content | `mem::take`, `mem::replace`, `Option::take`, `into_inner`, or clone |
| E0515 | return a reference to a local | return the owned value, or an owning iterator |
| E0597 | borrowed value does not live long enough | declare the owner before the borrower, since locals drop in reverse |
| E0716 | temporary dropped while borrowed | bind the temporary with `let` to extend its scope |
| E0521 | borrowed data escapes a closure or `spawn` | drop the closure parameter annotation, or use `thread::scope` |
| E0373 | closure may outlive the function | add `move`, or move a reference in instead |
| E0623 | lifetime mismatch between elided lifetimes | name one lifetime and use it in both positions |
| E0106 | missing lifetime specifier | link the output lifetime to an input, or return owned data |

A `&mut self` method loans all of `self`, which is what most E0499s reduce to. Inside a body the compiler tracks fields separately, so destructuring is the fix:

```
// E0499: cannot borrow `*self` as mutable more than once
impl App { fn tick(&mut self) { for e in &self.events { self.sink.push(e.id()); } } }

// fix: destructure so the two fields are borrowed disjointly
impl App {
    fn tick(&mut self) {
        let Self { events, sink, .. } = self;
        for e in events.iter() { sink.push(e.id()); }
    }
}
```

One lookup instead of two removes the conflict outright:

```
// E0502: `*m` borrowed immutably, then mutably
if let Some(v) = m.get_mut(&k) { return v; }
m.insert(k, String::new());

// fix
m.entry(k).or_default()
```

Leaving a cheap default behind makes the move legal:

```
// E0507: cannot move out of `self.buf`, which is behind a mutable reference
impl<T> Buffer<T> { fn drain(&mut self) -> Vec<T> { self.buf } }

// fix: Vec::new does not allocate
impl<T> Buffer<T> { fn drain(&mut self) -> Vec<T> { std::mem::take(&mut self.buf) } }
```

Choose shared state deliberately; each row past the first buys a runtime failure mode:

| Type | Threads | Runtime risk | Use when |
|---|---|---|---|
| `&mut T` | not applicable | none | always the first choice |
| `Cell<T>` | no | none | `T: Copy`, no references handed out |
| `RefCell<T>` | no | panics on overlapping borrow | single-threaded interior mutability |
| `OnceLock<T>` | yes | reentrant `get_or_init` deadlocks | a static initialized with arguments |
| `LazyLock<T>` | yes | an init panic poisons later access | a static with a nullary initializer |
| `Mutex<T>` | yes | deadlock; poisoning returns `Err` | general shared mutable state |
| `RwLock<T>` | yes | deadlock; not reentrant | read-heavy shared state |
| `parking_lot::Mutex` | yes | deadlock, and no poisoning | measured contention, mapped guards, timed locks |
| `Atomic*` | yes | ordering bugs | counters, flags, single scalars |
| `Rc<T>` | no | leaks on cycles | single-threaded shared ownership |
| `Arc<T>` | yes | leaks on cycles | shared ownership across threads |
| `Weak<T>` | follows parent | `upgrade` returns `None` | back edges that would otherwise leak |

Pick the arena by whether entries are removed:

| Approach | Handle | Removal | Use for |
|---|---|---|---|
| `Vec<T>` plus a newtype index | `u32` | none | append-only arenas: syntax trees, IR, interned data |
| `slotmap` | generational key | yes, slots reused | deletions plus stale-handle detection |
| `generational-arena` | `Index` | yes, free list | the same, with no `unsafe` in the crate |
| `indexmap` | position | shift or swap remove | map semantics plus stable insertion order |

## 5. Errors and panics

A panic means a bug in the program. A `Result` means a condition the caller has to decide about. Keep that line sharp and most error design follows.

- Return `Result<T, E>` from anything that can fail for an expected reason, and propagate with `?`.
- Return a concrete error type from a library, derived with `thiserror`.
- Use `anyhow::Result` in a binary, a test, a build script, an example, or a benchmark.
- Keep `anyhow::Error`, `eyre::Report`, and `Box<dyn Error>` out of every public library signature; they erase the variants a caller would match on.
- Never expose a dependency's error type through a public API; wrap it, or hide the representation behind `#[error(transparent)]`.
- Put `#[non_exhaustive]` on every public error enum, and separately on every variant that carries data.
- Prefer one error type per unit of fallibility to one crate-wide enum, so a caller never sees variants a function cannot produce.
- Make every error type `Send + Sync + 'static`, which `io::Error::new`, `thread::spawn`, and `downcast_ref` all require.
- Write `Display` messages as lowercase noun phrases, with no trailing period and no `failed to` prefix, because the caller supplies the context.
- Render the source in `Display` or return it from `source()`, never both, or the printed chain repeats itself.
- Attach the cause of every wrapped error with `#[source]` or a field named `source`.
- Use `#[from]` only when the variant means exactly what the source type means; otherwise take `#[source]` and convert explicitly, since two variants cannot share one `#[from]` type.
- Name variants for the operation, as in `ReadFile`, `Parse`, `Connect`; never repeat `Error` inside a variant name.
- Write every `expect` message as the invariant that must hold, not as the operation that failed.
- Add context at each layer with `.with_context(|| ...)`, reserving `.context("literal")` for messages that need no formatting.
- Print an `anyhow::Error` with `{:?}` to get the whole chain; `{}` prints only the outermost message.
- Put `#[track_caller]` on any function that panics on behalf of its caller.
- Give a public error type a classification method such as `is_retryable`, instead of making callers match variants.
- Log an error or return it, never both; the layer that handles it is the layer that logs it.

Reach for the narrowest construct that says what you mean:

| Construct | Compiled out in release | Use for |
|---|---|---|
| `panic!` | no | an unrecoverable bug reached at runtime |
| `assert!`, `assert_eq!` | no | a public contract or a security-relevant check |
| `debug_assert!` | yes | an expensive internal invariant |
| `unreachable!` | no | a state the type system cannot exclude |
| `todo!`, `unimplemented!` | no | unfinished code |
| `unwrap` | no | prototypes and tests only |
| `expect` | no | an invariant you can name in one sentence |

An opaque public error hides its dependencies and still lets callers act:

```
#[derive(Debug, thiserror::Error)]
#[error(transparent)]
pub struct Error(#[from] Repr);          // public, stable, opaque

#[derive(Debug, thiserror::Error)]
enum Repr {                              // private, free to change
    #[error("connect to {addr}")] Connect { addr: String, #[source] source: std::io::Error },
    #[error("decode response")] Decode(#[source] serde_json::Error),
}

impl Error {
    pub fn is_retryable(&self) -> bool { matches!(self.0, Repr::Connect { .. }) }
}
```

A binary prints the whole chain and controls its exit status:

```
fn main() -> std::process::ExitCode {
    match run() {
        Ok(()) => std::process::ExitCode::SUCCESS,
        Err(e) => { eprintln!("{e:?}"); std::process::ExitCode::from(2) }
    }
}

fn run() -> anyhow::Result<()> {
    let raw = std::fs::read_to_string("app.toml").context("read app.toml")?;
    let cfg: Config = toml::from_str(&raw).context("parse app.toml")?;
    serve(&cfg).with_context(|| format!("serve on port {}", cfg.port))
}
```

Detect in existing code:

- `-> Result<_, String>` or `Err("...".into())` - stringly errors that cannot be matched or downcast.
- `.unwrap()` or `.expect(` outside `#[cfg(test)]` - clippy `unwrap_used` and `expect_used` flag these.
- `anyhow`, `eyre`, or `Box<dyn Error>` in a `pub fn` return in a library - erased variants a caller cannot match.
- `#[error("Failed to ...")]`, a capitalized message, or a trailing period - message style to repair.
- a variant that renders its source in `Display` and also returns it from `source()` - a doubled error chain.

Corrections:

- `pub fn parse(s: &str) -> anyhow::Result<Ast>` -> `Result<Ast, ParseError>` - a library caller has to match variants.
- `Result<T, String>` -> `Result<T, ParseError>` - strings cannot be matched or downcast.
- `.unwrap()` -> `.expect("path was validated at startup")` - the message names the broken invariant.
- `#[error("Failed to parse header!")]` -> `#[error("invalid header")]` - lowercase, no prefix, no punctuation.
- `Io(#[from] io::Error)` -> `ReadFile { path: PathBuf, #[source] source: io::Error }` - names the operation and keeps the path.
- `.map_err(|_| MyError::Bad)` -> `.map_err(MyError::Bad)` with `#[source]` - discarding the cause destroys the chain.
- `.context(format!("reading {path}"))` -> `.with_context(|| format!("reading {path}"))` - avoids formatting on the success path.
- `eprintln!("{err}")` -> `eprintln!("{err:?}")` - `Display` on `anyhow::Error` hides the chain.
- `panic!("bad input")` in a parser -> `return Err(ParseError::Bad)` - malformed input is expected, not a bug.

## 6. API design and semver

A public API is a promise about names, shapes, and what may change. Decide the future-proofing at introduction; retrofitting it is itself a breaking change.

- Make `new` the primary constructor, then add `with_capacity`, `with_<detail>`, `from_<type>`, `try_new`, and finally `builder()` as the options multiply.
- Give getters no `get_` prefix: `name()` and `name_mut()`. Reserve `get` and `get_mut` for one obvious indexed or cell-like lookup.
- Return borrowed data or a copy of a `Copy` type from a getter; never `&Option<T>` and never a clone.
- Give a homogeneous collection `iter`, `iter_mut`, and `into_iter`, and implement `IntoIterator` for the type, for `&Type`, and for `&mut Type`.
- Return a named iterator type from a public API; return-position `impl Trait` costs you `Clone`, `Debug`, and the ability to name the type.
- Implement `From` and `TryFrom`, never `Into` or `TryInto`, since the blanket implementations supply those.
- Implement `FromStr` instead of a bespoke `parse_str`, so `str::parse` and `?` work at no extra cost.
- Derive `Debug` on every public type, and derive `Clone`, `Copy`, `PartialEq`, `Eq`, `Hash`, `PartialOrd`, `Ord`, and `Default` wherever they are semantically valid.
- Gate serde behind a feature named `serde`: `#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]`.
- Assert `Send` and `Sync` in a compile-time test for every public type holding a raw pointer, interior mutability, or a `dyn`, because losing either one silently breaks downstream `spawn` calls.
- Keep public struct fields private behind accessors unless the struct is a passive data bag; a public field pins the representation and blocks every future invariant.
- Apply `#[non_exhaustive]` to a public enum, struct, or variant when you introduce it, so adding to it later stays a minor change.
- Apply `#[must_use]` to constructors, to builder setters returning `Self`, to pure transforms, and to guard types.
- Seal a trait you do not want implemented downstream with a private empty supertrait, and say in the docs that it is sealed.
- Suffix an extension trait `Ext` and blanket-implement it over the upstream trait.
- Take `impl AsRef<Path>` or `impl Into<String>` at a widely used entry point, and concrete `&Path` or `&str` inside a crate. Behind any generic public function with a large body, forward at once to a private monomorphic function so only the shim is duplicated per instantiation.
- Use generics on a hot path and `dyn Trait` at a crate boundary, for heterogeneous storage, and to cut code size.
- Keep a trait dyn compatible when `dyn Trait` is plausible: no associated consts, no generic methods, no `Self` by value or in return position, and no `async fn`, unless gated behind `where Self: Sized`.
- Replace `bool` and stringly-typed parameters with enums or newtypes, and use `bitflags` for a flag set.
- Make destructors infallible and non-blocking; expose `close()` or `shutdown()` returning `Result` for anything that can fail.
- Run `cargo semver-checks` before publishing, and deprecate with `#[deprecated(since = "...", note = "...")]` before removing in a major release.

Detect in existing code:

- a getter named `get_*`, or one returning `&Option<T>` or a fresh clone - wrong prefix, shape, or cost.
- `impl Into<_>` or `impl TryInto<_>` - implement `From`/`TryFrom` and take the blanket impl.
- `&String`, `&Vec<T>`, or `&PathBuf` in a public parameter - take `&str`, `&[T]`, `&Path`.
- a public `enum` or struct without `#[non_exhaustive]`, or a `pub` field on a type with invariants - later additions turn breaking.
- `-> impl Trait` in a public return, or a generic method on a `dyn`-intended trait - lost names and dyn compatibility.

Corrections:

- `fn get_name(&self) -> String` -> `fn name(&self) -> &str` - no `get_` prefix, and return borrowed data.
- `fn as_string(&self) -> String` -> `fn to_string(&self) -> String` - `as_` promises a free borrow-to-borrow conversion.
- `impl Into<Foo> for Bar` -> `impl From<Bar> for Foo` - the blanket impl supplies `Into`.
- `fn open(p: &PathBuf)` -> `fn open(p: &Path)` - `&Path` is strictly more general.
- `fn iter(&self) -> impl Iterator<Item = &T>` -> `fn iter(&self) -> Iter<'_, T>` - a named type keeps `Clone` and `Debug`.
- `struct Cache<T: Clone + Debug>` -> `struct Cache<T>` with bounds on the impls - bounds on a definition are hard to remove later.
- `trait Sink { fn send<T: Into<Msg>>(&self, t: T); }` -> `fn send(&self, m: Msg)` - a generic method destroys dyn compatibility.
- `fn new() -> Self` alone -> also `impl Default` - enables `derive(Default)` and `mem::take`.
- `fn min_max(&self, lo: &mut T, hi: &mut T)` -> `fn min_max(&self) -> (T, T)` - a tuple return needs no out-parameters.
- `pub enum Error { Io, Other }` -> `#[non_exhaustive] pub enum Error { Io, Other }` - adding a variant stops being breaking.

Sealing a trait keeps it extensible without a major bump:

```
pub trait Encoder: private::Sealed {
    fn encode(&self, out: &mut String);
    #[doc(hidden)]
    fn size_hint(&self) -> usize { 0 }   // defaulted, so addable later
}

mod private {
    pub trait Sealed {}
    impl Sealed for u32 {}
}
```

Know which changes force a major version:

| Change | Verdict |
|---|---|
| rename, move, or remove a public item | major |
| add a public item | minor |
| add a public field when no private field exists | major |
| add an enum variant without `#[non_exhaustive]` | major |
| add `#[non_exhaustive]` to an existing type | major |
| add a trait item with no default | major |
| change any trait item signature, or break dyn compatibility | major |
| tighten a generic bound | major; loosening is minor |
| lose `Send`, `Sync`, or `Unpin` on a public type or returned `impl Trait` | major, and invisible in the signature |
| require `std` where `no_std` used to work | major |
| remove a Cargo feature | major; adding one is minor |
| raise the MSRV | minor by convention |

## 7. Modules, files, and visibility

The module tree is the first thing a reader navigates and the last thing anyone refactors. Name modules for the domain, keep the root a facade, and default to crate-private.

- Declare each module exactly once with `mod name;` and reach it everywhere else through `use`.
- Use `src/foo.rs` beside a `src/foo/` directory for its children; declaring both `foo.rs` and `foo/mod.rs` is an error, and a tree of files all named `mod.rs` is unnavigable in an editor.
- Keep `lib.rs` to crate docs, crate-level attributes, `mod` declarations, and `pub use` re-exports, with no logic in it.
- Default every item to `pub(crate)` and set `unreachable_pub = "warn"`, so bare `pub` reliably marks the public API.
- Give every module a `//!` first line naming its job in one sentence.
- Name a module for its domain concept; `utils`, `helpers`, `common`, `misc`, `types`, and `models` accumulate unrelated code because nothing is out of scope for them.
- Extract a third named module when two modules need the same code, rather than growing a junk drawer.
- Keep the tree shallow: two levels under `src/` is normal, and four means the concepts are wrong.
- Split any file past 500 lines, and any file holding a second unrelated concept.
- Define a type in the module that owns its behavior; promote it only when a second module owns it equally.
- Isolate platform code in one module per platform (`src/sys/unix.rs`, `src/sys/windows.rs`) behind a single `#[cfg]` on the `mod` line, so the conditional cannot drift out of sync.
- Parse at the boundary into a type that cannot hold an invalid state, rather than validating and then trusting a `bool`.
- Newtype every domain scalar: `UserId(u64)`, `NonZeroUsize` for a count that cannot be zero, an enum for a closed set.
- Keep a pure core and confine input and output to a thin outer shell, so tests need no mocks.
- Add no trait until a second implementation or a real abstraction boundary exists; prefer concrete types and free functions.
- Choose test seams by cost: a generic parameter when the set is closed, `&dyn Trait` when monomorphisation would bloat, a plain closure when one operation varies.

Corrections:

- `mod helpers;` -> `mod retry;` - name the concept, not its role.
- `src/auth/mod.rs` -> `src/auth.rs` plus `src/auth/` - avoids a directory of identically named files.
- `pub fn parse()` in a private module -> `pub(crate) fn parse()` - `pub` misstates the item's real reach.
- `use super::config::Config;` -> `use crate::config::Config;` - one path form works at every depth.
- `use crate::ast::*;` -> `use crate::ast;` then `ast::Struct` - keeps the layer visible and prevents clashes.
- `fn is_valid(&self) -> bool` -> `fn parse(raw: &str) -> Result<Valid, Error>` - the proof then travels in the type.
- `pub timeout: u64` with a "must be nonzero" comment -> `timeout: NonZeroU64` - the invariant becomes unbreakable.
- `fn frobnicate(w: Option<Walrus>)` -> `fn frobnicate(w: Walrus)` - the caller has the context to handle absence.

| Form | Reach |
|---|---|
| `pub` | outside the crate, if every ancestor module is also `pub` |
| `pub(crate)` | anywhere in this crate; the correct default |
| `pub(super)` | the parent module only |
| `pub(in crate::path)` | a named ancestor module |
| `pub use` | re-exports, short-circuiting the privacy chain |

A facade root, which is all `lib.rs` should contain:

```
//! Search primitives for the grep engine.
//!
//! Start at [`Searcher`]; ARCHITECTURE.md holds the codemap.
#![cfg_attr(not(feature = "std"), no_std)]
#![warn(missing_docs, unreachable_pub, unsafe_op_in_unsafe_fn)]

mod searcher;
mod sink;
#[cfg(feature = "pcre2")]
pub mod pcre2;

pub use crate::searcher::{Searcher, SearcherBuilder};
pub use crate::sink::{Sink, SinkMatch};
```

## 8. Crates, workspaces, and features

A workspace is a flat set of crates with one lockfile. Keep its internal dependency graph a shallow acyclic layering, and keep every feature additive.

- Make the workspace root a virtual manifest, meaning `[workspace]` with no `[package]`, unless the repository is one application with helper crates.
- Put every member in one flat directory and glob it: `members = ["crates/*", "xtask"]`. Cargo's namespace is flat, so a nested tree only rots.
- Name each directory exactly the crate it contains.
- Set `resolver = "3"` explicitly in a virtual manifest; `edition` in the members does not imply it.
- Declare `edition`, `rust-version`, `license`, and `repository` once in `[workspace.package]`.
- Declare every external dependency once in `[workspace.dependencies]`, and let members write `serde.workspace = true`.
- Give internal path dependencies both `path` and `version` in `[workspace.dependencies]`, so the crate stays publishable.
- Put `optional = true` on the member's own entry; the workspace table rejects it. An inherited dependency accepts only `features` and `optional`, so `default-features = false` belongs in `[workspace.dependencies]`.
- Keep `[profile.*]`, `[patch.*]`, and `[replace]` in the root manifest only; Cargo ignores them in a member.
- Set `version = "0.0.0"` and `publish = false` on any crate you never ship.
- Commit `Cargo.lock` for libraries and binaries alike; Cargo excludes it from published library tarballs, so it never constrains a consumer.
- Declare the MSRV in `package.rust-version`, and never pin `rust-toolchain.toml` to it, since a toolchain file pins contributors rather than consumers.
- Put every command that is not a plain `cargo` subcommand in an `xtask` member, aliased in `.cargo/config.toml`, because an undocumented shell script is how a repo stops being maintainable.
- Keep credentials out of `.cargo/config.toml`, which is committed; tokens live in `$CARGO_HOME/credentials.toml`.
- Split a crate only for build parallelism, an enforced API boundary, independent publishability, or to isolate a heavy optional dependency.
- Keep proc-macro dependencies in leaf crates, never in the vocabulary crate every other member depends on.
- Give a `-sys` crate only `extern` declarations plus `links = "foo"`, and put the safe abstraction in a sibling crate with no suffix.
- Name packages in `kebab-case`, and add no `rust-` prefix or `-rs` suffix, since every crate here is Rust.
- Make every feature purely additive: enabling one may add items, never remove, rename, or retype them.
- Define no mutually exclusive features; where the platform forces it, emit `compile_error!` for the bad combination.
- Name the opt-in `std`, not `no_std`, and keep `alloc` as a separate smaller step. Use the conventional names for the rest: `serde` adds serialization impls and nothing else, `derive` re-exports the companion proc-macro crate, `full` enables everything stable, and `unstable` marks API exempt from semver.
- Keep `--no-default-features` building, and remember that removing an entry from `default` is a breaking change.
- Prefix an optional dependency with `dep:` whenever the dependency is an internal detail, and use `crate?/feature` to forward a feature without enabling that dependency.
- Gate a whole module rather than thirty scattered items, so one `#[cfg]` cannot drift.
- Register every custom cfg, since an unregistered one triggers `unexpected_cfgs`.

Root manifest:

```
[workspace]
members = ["crates/*", "xtask"]
resolver = "3"

[workspace.package]
edition = "2024"
rust-version = "1.85"
license = "MIT OR Apache-2.0"

[workspace.dependencies]
foo-core = { path = "crates/foo-core", version = "0.4.0" }
serde = { version = "1", default-features = false }

[profile.dev]
debug = "line-tables-only"

[profile.dev.package."*"]
debug = false
opt-level = 1                 # 2 and 3 disable cross-crate generic sharing
```

Member manifest and features:

```
[package]
name = "foo-cli"
version.workspace = true
edition.workspace = true
rust-version.workspace = true

[dependencies]
foo-core.workspace = true
serde = { workspace = true, features = ["derive"], optional = true }
ravif = { version = "0.11", optional = true }
rgb = { version = "0.8", optional = true }

[features]
default = ["std"]
std = ["alloc"]
alloc = []
serde = ["dep:serde", "rgb?/serde"]   # weak ?, so rgb is never pulled in
avif = ["dep:ravif", "dep:rgb"]

[lints]
workspace = true
```

Corrections:

- `[profile.release]` in a member manifest -> the same table in the root manifest - Cargo ignores non-root profiles.
- `sibling = { path = "../sibling" }` -> `sibling.workspace = true` - one canonical version, and it stays publishable.
- `serde = "1"` repeated per member -> `serde.workspace = true` - prevents drift and duplicate builds.
- `crates/hir/def/` -> `crates/hir-def/` - Cargo's namespace is flat.
- `[features] use-serde = ["serde"]` -> `serde = ["dep:serde"]` - matches Cargo's implicit optional-dependency feature.
- `[features] no_std = []` -> `default = ["std"]` with `std = []` - features add, never subtract.
- `#[cfg(feature = "webp")]` on thirty items -> one gate on `pub mod webp;` - a single gate cannot drift.
- `foo-rs` -> `foo` - the suffix carries nothing.
- `Makefile` and `prepare.sh` -> `xtask/` plus `cargo xtask` - cross-platform, and it bootstraps from Cargo alone.

Crate suffixes carry meaning; use them as the ecosystem does:

| Suffix | Contents |
|---|---|
| `foo` | the public facade, re-exporting the API |
| `foo-core` | shared internals with no heavy dependencies |
| `foo-derive`, `foo-macros` | `proc-macro = true`, re-exported behind a `derive` feature |
| `foo-sys` | `extern` declarations plus `links` |
| `foo-cli` | a leaf binary |
| `xtask` | repo automation, never published |

## 9. The dependency stack

The standard library deliberately omits an async runtime, HTTP, TLS, serialization, random numbers, regular expressions, dates, an error derive, and a logging backend. Take the ecosystem default for each, and add nothing else without a reason.

- Add a dependency only when all four hold: it takes more than 100 lines to write correctly, you will keep using it, its own tree stays under about a dozen crates, and it has shipped a release within a year.
- Check the last release date, open-issue triage, MSRV, license, `unsafe` count, and `cargo tree -d` depth before adding anything.
- Confirm a crate is the specific, existing package you intend before adding it, and audit an existing `Cargo.toml` the same way, by matching each name against its docs.rs page and source repository; a near-miss or hallucinated name can resolve to an unrelated or squatted crate yet build like any other. When you cannot confirm identity, add nothing and reach for `std` or a crate already in the tree.
- Run `cargo deny check` and `cargo audit` in CI, and add `cargo vet` when every dependency needs a human review.
- Turn off default features you do not use, and gate anything heavy behind a feature of your own.
- Reach for the standard library first: `LazyLock`, `OnceLock`, `core::error::Error`, and `const { assert!(...) }` all removed a common dependency.
- Write a `no_std` library against `core` plus `alloc`, and layer `std` on top as an additive feature.
- Pin nothing by exact version in a library; let Cargo's resolver and the caller's lockfile decide.

| Need | Default | Alternative, and when to take it |
|---|---|---|
| serialization | `serde` with `serde_json` | `rkyv` or `postcard` for zero-copy archives or an embedded wire format |
| TOML | `toml` | `toml_edit` when comments and formatting must round-trip |
| async runtime | `tokio` | `smol` for a tiny dependency budget, or one `block_on` in sync code |
| data parallelism | `rayon` | `std::thread::scope` for a handful of long tasks |
| CLI parsing | `clap` with derive | `lexopt` when compile time matters more than features |
| library errors | `thiserror` | `snafu` for per-callsite context selectors |
| application errors | `anyhow` | `color-eyre` or `miette` when an end user reads the output |
| logging and tracing | `tracing` with `tracing-subscriber` | `log` for a sync-only library with no spans |
| regular expressions | `regex` | `fancy-regex` for backreferences, `regex-lite` for binary size |
| iterator helpers | `itertools` | the standard library, when one adaptor suffices |
| insertion-ordered map | `indexmap` | `BTreeMap` when you want sorted rather than insertion order |
| fast hasher | `foldhash` | `rustc-hash` for integer keys; never for attacker-controlled keys |
| small vectors | `smallvec` | `arrayvec` for a hard capacity, `bumpalo` when a whole graph dies at once |
| byte buffers | `bytes` | `Vec<u8>` when you share nothing across tasks |
| locks | `std::sync` | `parking_lot` for fairness, mapped guards, or timed locks |
| random numbers | `rand` | `fastrand` for no tree, `getrandom` for raw OS entropy |
| dates and times | `jiff` in a binary | `time` or `chrono` when the types cross a public API, since `jiff` is still pre-1.0 |
| identifiers, URLs | `uuid`, `url` | `ulid` when identifiers must sort lexicographically |
| HTTP client | `reqwest` | `ureq` for blocking with a small tree, `hyper` to build a proxy |
| HTTP server | `axum` with `tower` | `actix-web` for maximum throughput |
| SQL | `sqlx` | `diesel` for a compile-time-checked DSL, `rusqlite` for sync SQLite |
| flag sets | `bitflags` | `enumflags2` to derive flags from an enum |
| directory walking | `walkdir` | `ignore` to respect `.gitignore` or to walk in parallel |
| concurrent map | `dashmap` | `RwLock<HashMap>` under low contention |
| channels | `std::sync::mpsc` | `crossbeam-channel` or `flume` for `select!` or multiple consumers |
| pin projection | `pin-project-lite` | `pin-project` for complex generic bounds |

Replace these on sight:

| Superseded | Use instead |
|---|---|
| `lazy_static` | `std::sync::LazyLock` |
| `once_cell` for statics | `std::sync::OnceLock` |
| `static_assertions` | `const { assert!(...) }` |
| `error-chain`, `failure`, `err-derive` | `thiserror` with `anyhow` |
| `structopt` | `clap` with derive |
| `serde_yaml` | a maintained fork, since upstream published a deprecation |
| `memmap` | `memmap2` |
| `#[bench]` | `criterion` or another `harness = false` benchmark |
| `tarpaulin` | `cargo-llvm-cov` |
| `actions-rs/*` in CI | `dtolnay/rust-toolchain` with `Swatinem/rust-cache` |

## 10. Documentation

Rustdoc compiles your examples, so documentation is the one form of prose the build can keep honest. Write every example as a doctest and the docs cannot rot silently.

- Document every `pub` item: modules, structs, enums, variants, fields, traits, functions, methods, macros, and type aliases.
- Use `///` before an item and `//!` at the top of `lib.rs` and each module file.
- Write the first line as one short sentence, third person indicative: `Returns the length.`, never `Return` and never `This function returns`.
- Keep the summary to one line of roughly 15 words, because everything before the first blank line becomes the search result and the module index blurb.
- Order the sections `# Errors`, `# Panics`, `# Safety`, then `# Examples` last, matching the standard library.
- Write `# Examples` in the plural, even for a single example.
- Give `# Errors` to every public function returning `Result`, naming the variants and the conditions that produce them.
- Give `# Panics` to anything a caller can drive into a panic through arguments or state.
- Give `# Safety` to every `unsafe fn`, `unsafe trait`, and `unsafe impl`, enumerating each invariant the caller upholds. If you cannot write it, the function should not be `unsafe`.
- Never restate the signature in prose; rustdoc already links every type in it.
- Use `?` in examples rather than `unwrap`, and close the example with a hidden `# Ok::<(), ErrType>(())` line, written with no space inside the parentheses.
- Hide setup lines with a leading `# ` inside the fence.
- Use `no_run`, `compile_fail`, or `text` rather than `ignore`, which silently skips compilation and hides rot.
- Omit the `rust` tag on a Rust fence and tag every non-Rust fence, so rustdoc does not try to compile prose.
- Link with intra-doc links, never a hand-written HTML path, since layout changes break the path and not the link.
- Wrap a bare URL in angle brackets.
- Deny `rustdoc::broken_intra_doc_links` and `rustdoc::private_intra_doc_links`; warn `missing_docs` and `missing_debug_implementations`.
- Mark public-but-not-API items `#[doc(hidden)]`, which also removes them from the semver-relevant surface.
- Add `#[doc(alias = "...")]` for an FFI symbol name or an alternative spelling, so search finds the Rust equivalent.
- Fill `description`, `repository`, `license`, `keywords`, `categories`, `readme`, and `rust-version`; leave `authors` out, since Cargo marks it deprecated.
- Cap `keywords` and `categories` at five entries each, with categories matching the registry slugs exactly.
- Add `#![cfg_attr(docsrs, feature(doc_cfg))]` at the crate root and set `rustdoc-args = ["--cfg", "docsrs"]` under `[package.metadata.docs.rs]`, which labels every feature-gated item in the rendered docs. `doc_auto_cfg` was folded into `doc_cfg` and now fails as a removed feature.
- Precede every `unsafe` block with a `// SAFETY:` comment on the immediately preceding line.
- Write ordinary comments for the invariant and the reason, never to narrate the next line.
- Add no doc comment that merely repeats the item name; `/// The name.` on `pub name: String` is noise.
- Run `cargo test --doc` in CI, and build docs with `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps --all-features`.

| Heading | Required when |
|---|---|
| `# Errors` | the function returns `Result`; name the variants and their conditions |
| `# Panics` | a caller can trigger a panic through arguments or state |
| `# Safety` | the item is `unsafe`; enumerate every caller obligation |
| `# Examples` | always, for a public item |
| `# Aborts` | the process can abort rather than unwind |

| Fence attribute | Meaning |
|---|---|
| none | compile and run; passes unless it panics |
| `no_run` | compile only; for network access, real input and output, or infinite loops |
| `should_panic` | compile and run; fails unless it panics |
| `compile_fail` | compilation must fail; fragile across releases |
| `ignore` | neither compiled nor run; avoid it |
| `text` | plain text, never compiled |
| `edition2024` | compile this block under a named edition |

A model doc comment for a fallible function:

````
/// Parses a TOML manifest from `path`.
///
/// # Errors
/// Returns [`Error::Io`] if `path` is unreadable, or [`Error::Syntax`]
/// if the contents are not valid TOML.
///
/// # Examples
/// ```
/// let m = mycrate::load("Cargo.toml")?;
/// # Ok::<(), mycrate::Error>(())
/// ```
pub fn load(path: &Path) -> Result<Manifest, Error> { todo!() }
````

Documentation lints belong in the manifest, next to every other lint:

```
[lints.rust]
missing_docs = "warn"
missing_debug_implementations = "warn"

[lints.rustdoc]
broken_intra_doc_links = "deny"
private_intra_doc_links = "deny"
unescaped_backticks = "warn"

[lints.clippy]
missing_safety_doc = "deny"
undocumented_unsafe_blocks = "deny"
```

Repository documentation carries what rustdoc cannot:

| File | Contents |
|---|---|
| `README.md` | badges, a one-paragraph pitch, one compiling example, a feature-flag table, the MSRV and its bump policy, the license |
| `CHANGELOG.md` | reverse-chronological releases under Added, Changed, Deprecated, Removed, Fixed, Security |
| `CONTRIBUTING.md` | setup, the exact test and lint commands, the checks a pull request must pass |
| `ARCHITECTURE.md` | the bird's eye view, a codemap naming files and types, the invariants, the cross-cutting concerns |
| `LICENSE-APACHE`, `LICENSE-MIT` | the dual license the ecosystem expects |

User guides:

Write a user guide when the crate needs tutorials, walkthroughs, or conceptual explanations that exceed what doc comments and `ARCHITECTURE.md` carry. Keep API reference on docs.rs and the narrative guide separate.

- Use mdBook, which is the ecosystem standard: the Rust Book, Cargo, Tokio, and Serde all use it.
- Place the book in a `guide/` directory at the workspace root, with `book.toml` at its root and chapters under `guide/src/`.
- Write `SUMMARY.md` as the table of contents; mdBook generates navigation from it.
- Write CommonMark; do not rely on GitHub-flavored extensions such as task lists or alerts.
- Pull source into prose with `{{#include path/to/file.rs}}`; never paste code that is not compiled elsewhere, because it rots silently.
- Hide setup lines with a leading `# ` inside a fence so they compile but do not render.
- Use `{{#playground}}` for examples meant to run on play.rust-lang.org.
- Tag every non-Rust fence explicitly; mdBook compiles untagged fences as Rust.
- Add admonitions only through a community preprocessor; mdBook has no native admonition syntax.
- Deploy with `mdbook build` in CI to GitHub Pages, and set `documentation` in `Cargo.toml` to the published guide URL.
- Link the guide from `README.md` rather than duplicating its content there.

```
guide/
  book.toml
  src/
    SUMMARY.md
    introduction.md
    getting-started.md
    advanced/
      custom-backends.md
```

| Kind | Host | Tool |
|---|---|---|
| API reference | docs.rs, automatic on publish | rustdoc |
| User guide | GitHub Pages or a custom domain | mdBook |

Detect in existing code:

- a `pub` item with no `///`, or a module or `lib.rs` with no `//!` - `missing_docs` flags these.
- a `Result`-returning `pub fn` with no `# Errors`, or an `unsafe fn` with no `# Safety` - a required heading is missing.
- ` ```ignore ` on a doc fence, or `.unwrap()` in a doc example - hidden rot and habits readers copy.
- a hand-written `https://doc.rust-lang.org/...` link where an intra-doc link would resolve - it rots on the next layout change.
- a `guide/` directory with no CI deploy step - add an `mdbook build` job that publishes to GitHub Pages.
- a guide with pasted code instead of `{{#include}}` directives - replace with includes pointing to tested source files.
- a `README.md` that duplicates the guide - link to the published guide and keep the README to a pitch plus one example.
- a `documentation` field missing from `Cargo.toml` when a published guide exists - set it to the guide URL.

Corrections:

- `/// Return the length.` -> `/// Returns the length.` - third person indicative.
- `/// # Example` -> `/// # Examples` - always plural.
- `/// Gets a value. Panics if empty.` -> a summary line plus a `# Panics` section - a panic needs its own heading.
- ` ```ignore ` -> ` ```no_run ` - `ignore` hides rot by skipping compilation.
- `/// let x = load().unwrap();` -> `/// let x = load()?;` plus an `Ok` tail - readers copy examples verbatim.
- `[`Vec`](https://doc.rust-lang.org/std/vec/struct.Vec.html)` -> `[`Vec`]` - intra-doc links resolve locally and never rot.
- `RUSTFLAGS="-D missing_docs"` -> `[lints.rust] missing_docs = "deny"` - Cargo tracks it for rebuilds and skips dependencies.
- `authors = ["Me <me@example.com>"]` -> omit the key - Cargo marks it deprecated.

## 11. Testing

Unit tests live in the file they test, so they can reach private items. Integration tests live in one binary, because each extra file directly under `tests/` relinks the whole library.

- Put unit tests in `#[cfg(test)] mod tests` in the same file as the code, with `use super::*;`.
- Keep exactly one integration-test binary at `tests/it/main.rs`, with `mod foo;` for each area.
- Put shared integration helpers in `tests/common/mod.rs`, never `tests/common.rs`, which Cargo would build as its own binary.
- Give every `#[should_panic]` an `expected = "..."` substring, since the bare form passes on any unrelated panic.
- Give every `#[ignore]` a reason string, and run the ignored set on a schedule.
- Set `harness = false` on every benchmark target.
- Seed randomized tests explicitly, print the seed on failure, and commit the regression corpus.
- Use `tempfile::TempDir` for filesystem tests, and never write inside the tree.
- Use paused time in async tests rather than sleeping, so the suite stays deterministic and instant.
- Run `cargo test --doc` as its own step, because `cargo nextest` does not execute doctests.
- Gate a cross-crate test helper behind a Cargo feature, since `#[cfg(test)]` applies only within the crate being tested.
- Pin an exact toolchain for any job asserting compiler diagnostic text, because those messages drift between releases.
- Put test-only dependencies in `[dev-dependencies]`, which are stripped from the published package.

```
#[cfg(test)]
mod tests {
    use super::*;                     // reaches private items in this module

    #[test]
    fn parses_empty_input() {
        assert_eq!(parse(""), Ok(Config::default()));
    }

    #[test]
    #[should_panic(expected = "index out of bounds")]
    fn panics_past_end() {
        parse("x").index(9);
    }
}
```

| Test kind | Tool |
|---|---|
| unit, including private items | `#[cfg(test)] mod tests` in the same file |
| public API integration | one binary at `tests/it/main.rs` |
| documentation examples | `cargo test --doc`, library targets only |
| large suite, isolation, flakes | `cargo nextest run`, one process per test, with retries |
| golden output | `insta`, reviewed with `cargo insta review` |
| readable assertion diffs | `pretty_assertions` |
| invariants over random input | `proptest` |
| structured fuzzing | `arbitrary` with `cargo fuzz` |
| compile-fail macro output | `trybuild`, with the toolchain pinned |
| undefined behavior | `cargo +nightly miri test`, on the paths your tests reach |
| concurrency interleavings | `loom` for exhaustive, `shuttle` for randomized |
| coverage | `cargo llvm-cov` |
| wall-clock benchmarks | `criterion`, with `harness = false` |

Detect in existing code:

- `#[should_panic]` with no `expected = "..."` - it passes on any unrelated panic.
- `#[ignore]` with no reason string, or a randomized test with no printed seed - silent gaps and unreproducible failures.
- `tests/common.rs`, or several files directly under `tests/` - an accidental test binary, and a relink per file.
- a test that writes inside the source tree instead of a `tempfile::TempDir` - cross-test interference.

Corrections:

- `tests/common.rs` -> `tests/common/mod.rs` - otherwise Cargo builds it as a test binary.
- `tests/a.rs`, `tests/b.rs`, `tests/c.rs` -> `tests/it/main.rs` with `mod a;` - one link step instead of three.
- `#[should_panic]` -> `#[should_panic(expected = "out of bounds")]` - the bare form accepts any panic.
- `cargo nextest run` alone -> plus `cargo test --doc` - nextest never runs doctests.
- `#[bench] fn bench_parse` -> a `criterion` benchmark with `harness = false` - `#[bench]` is nightly-only.
- `sleep(Duration::from_secs(1))` in an async test -> paused time and an explicit advance - deterministic and instant.
- `#[test]` on an `async fn` -> `#[tokio::test]` - the bare attribute does not run the future, and current toolchains reject it outright.

## 12. Lints, tooling, CI, and maintenance

Every guarantee that can be moved out of review and into a tool should be. Declare lints in the manifest, run the same commands locally and in CI, and keep the whole run under ten minutes.

- Declare lint levels in `[lints.rust]`, `[lints.clippy]`, and `[lints.rustdoc]` in `Cargo.toml`, not in `#![deny(...)]` at the crate root.
- In a workspace, put the levels in `[workspace.lints.*]` and add `[lints]` with `workspace = true` to every member; inheritance is never implicit.
- Give a lint-group entry `priority = -1` so individual lints can override it.
- Run `cargo clippy --all-targets --all-features -- -D warnings`; the bare form skips tests, benches, and examples.
- Enable `clippy::all` and `clippy::pedantic` at warn, and cherry-pick from `restriction` and `nursery` rather than enabling either as a group.
- Prefer `#[expect(lint, reason = "...")]` to `#[allow(...)]`, because the expectation warns once it goes stale.
- Give every suppression a `reason`.
- Set `unsafe_code = "forbid"` in any crate that contains no `unsafe`.
- Deny `clippy::unwrap_used` and `clippy::expect_used` in a library, and allow both in tests through `clippy.toml`.
- Keep `msrv` out of `clippy.toml`; Clippy reads `rust-version` from `Cargo.toml` already.
- Declare the MSRV in `package.rust-version` and verify it in CI rather than trusting it.
- Treat an MSRV bump as a minor release, batching it with other changes.
- Migrate editions with `cargo fix --edition`, then read the diff before committing it.
- Keep CI under ten minutes, and split the build step from the run step so a regression is attributable.
- Set one aggregate job that depends on the others, and make that single job the required status check.
- Run `cargo semver-checks` before publishing a library, and read `cargo package --list` before a first publish.
- Deprecate with `#[deprecated(since = "...", note = "...")]` and remove only in a major release.
- Find unused dependencies with `cargo machete` rather than the `unused_crate_dependencies` lint, which reports one false positive per target.

The local loop before pushing:

| Command | What it checks |
|---|---|
| `cargo fmt --all --check` | formatting matches the style edition |
| `cargo clippy --all-targets --all-features -- -D warnings` | lints across every target |
| `cargo test --locked --workspace --all-features` | unit, integration, and doc tests, with the lockfile current |
| `cargo test --doc` | doctests, when the suite otherwise runs under nextest |
| `RUSTDOCFLAGS="-D warnings" cargo doc --no-deps --all-features` | broken intra-doc links and malformed markup |
| `cargo hack check --feature-powerset --no-dev-deps --depth 2` | every feature combination compiles alone |
| `cargo hack check --rust-version --workspace --ignore-private` | the declared MSRV is achievable |
| `cargo deny check` | advisories, licenses, duplicates, sources |
| `cargo semver-checks` | the version bump matches the API change |
| `cargo +nightly miri test` | undefined behavior on executed paths |

Clippy groups, and what to do with each:

| Group | Default | Enable it? |
|---|---|---|
| `correctness` | deny | yes, and never downgrade it |
| `suspicious`, `style`, `complexity`, `perf` | warn | yes; together these are `clippy::all` |
| `pedantic` | allow | yes at warn, then `expect` the few you reject |
| `cargo` | allow | yes at warn for a published crate |
| `nursery` | allow | no as a group; cherry-pick |
| `restriction` | allow | no as a group; cherry-pick `unwrap_used`, `expect_used`, `dbg_macro`, `todo` |

Compiler lints worth raising, with their honest cost:

| Lint | Level | Noise |
|---|---|---|
| `unsafe_code` | forbid | none, in a crate with no `unsafe` |
| `missing_docs` | warn | high on an existing crate, worth the one-time cost |
| `missing_debug_implementations` | warn | low; each hit is a real API defect |
| `unreachable_pub` | warn | low |
| `unsafe_op_in_unsafe_fn` | deny | none; edition 2024 already warns |
| `future_incompatible` | warn, `priority = -1` | low; this is the edition early-warning system |
| `rust_2018_idioms` | warn, `priority = -1` | moderate; it pulls in `elided_lifetimes_in_paths` |
| `unused_crate_dependencies` | leave at allow | high; false-positives per target |
| `unused_results` | leave at allow | unusable in practice |

Workspace lint policy, set once:

```
[workspace.lints.rust]
unsafe_code = "forbid"
missing_docs = "warn"
unreachable_pub = "warn"
unsafe_op_in_unsafe_fn = "deny"
future_incompatible = { level = "warn", priority = -1 }

[workspace.lints.clippy]
all = { level = "deny", priority = -1 }
pedantic = { level = "warn", priority = -1 }
unwrap_used = "deny"
dbg_macro = "warn"
```

A CI matrix that pins the MSRV as its last entry:

```
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        rust: [stable, beta, "1.85"]        # last entry is the MSRV
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@master
        with: { toolchain: "${{ matrix.rust }}" }
      - uses: Swatinem/rust-cache@v2
      - run: cargo test --locked --workspace --all-features --all-targets
      - run: cargo test --locked --workspace --all-features --doc
```

Detect in existing code:

- `#![deny(...)]`, `#![warn(...)]`, or `#![forbid(...)]` at a crate root - move lint levels into the `[lints]` tables.
- `#[allow(...)]` with no `reason`, where `#[expect(...)]` would warn once it goes stale - unexplained, silent suppression.
- `cargo clippy` invoked without `--all-targets --all-features -- -D warnings` - it skips tests, benches, and examples.
- `msrv` in `clippy.toml`, or an MSRV asserted nowhere in CI - two sources of truth, or none.

Corrections:

- `#![deny(clippy::all)]` in `lib.rs` -> `[lints.clippy] all = { level = "deny", priority = -1 }` - inheritable, and covers all targets.
- `[workspace.lints.rust]` alone -> plus `[lints] workspace = true` per member - workspace lints are opt-in.
- `#[allow(dead_code)]` -> `#[expect(dead_code, reason = "cli only")]` - warns once the suppression goes stale.
- `cargo clippy` -> `cargo clippy --all-targets --all-features -- -D warnings` - the bare form skips most code.
- `msrv = "1.85"` in `clippy.toml` -> `rust-version = "1.85"` in `Cargo.toml` - one source of truth.
- `cargo install cargo-nextest` in CI -> a prebuilt-binary install action - seconds instead of minutes.
- `actions-rs/toolchain@v1` -> `dtolnay/rust-toolchain@stable` - archived, and running deprecated runtimes.

## 13. Performance

Measure before optimizing, then take the standard wins. Rust's defaults are fast enough that most gains come from removing allocations, not from clever code.

- Profile before changing anything: `samply` or `perf` with `cargo flamegraph` for wall clock, `hyperfine` for whole-binary timing, `criterion` for a function, `dhat` for allocation sites.
- Set `debug = "line-tables-only"` in the release profile before profiling, so stacks resolve without slowing the build.
- Call `Vec::with_capacity` or `reserve` wherever the final length is known or bounded, which skips the reallocation ladder.
- Use `extend(iter)` instead of a `push` loop, and `collect::<Result<Vec<_>, _>>()` instead of pushing inside a fallible loop.
- Use `.iter().copied()` for `Copy` items, `sort_unstable_by_key` unless stability matters, `sort_by_cached_key` when the key is expensive, and `binary_search` on sorted data.
- Hoist `format!` out of a hot loop: write into a reused `String` with `write!` and `clear()` it each pass.
- Freeze a finished buffer with `into_boxed_slice` or `into_boxed_str` to drop the capacity word.
- Keep the default hasher for any map keyed by input an attacker controls; the standard library resists hash flooding and the fast hashers do not.
- Switch to `foldhash` or `rustc-hash` only after a profile shows hashing hot and the keys are trusted.
- Reach for `smallvec` when a vector is usually short, `arrayvec` when capacity is bounded, and an arena when a whole object graph dies at once.
- Put `#[inline]` on a small function callers reach across a crate boundary; `#[inline(always)]` needs a benchmark, since forced inlining thrashes the instruction cache.
- Cut monomorphisation bloat by splitting a generic function into a thin generic shell plus a non-generic inner function, or by taking `&dyn Trait` on a cold path.
- Apply one release-profile knob at a time and measure it; the linker is the only change with no tradeoff.

| Question | Tool |
|---|---|
| which function burns wall clock | `samply`, `perf record`, `cargo flamegraph` |
| is this faster than the baseline | `criterion` for a function, `hyperfine` for the binary |
| did instruction count regress in noisy CI | `iai-callgrind` |
| where do allocations come from | `dhat`, `heaptrack` |
| which crate dominates build time | `cargo build --timings` |
| what is bloating the binary | `cargo bloat`, `cargo-llvm-lines` |

| Release knob | Effect |
|---|---|
| `lto = "thin"` or `"fat"` | cross-crate optimization, slower link |
| `codegen-units = 1` | more cross-function optimization, no parallel codegen |
| `panic = "abort"` | smaller and slightly faster, but it disables `catch_unwind` and skips every `Drop` |
| `strip = "symbols"` | smaller binary, worse backtraces |
| `opt-level = "s"` or `"z"` | size over speed |
| `-C target-cpu=native` | vectorization, and a binary that may not run elsewhere |

## 14. Async

Async buys concurrency over waiting, not speed over computing. Reach for it when a program waits on many things at once, and not otherwise.

- Keep CPU-bound work off the runtime: `rayon` or a plain thread pool, not async tasks.
- Skip the runtime entirely for a short command-line program.
- Use `#[tokio::main]` for a server and the current-thread flavor for a command-line tool, a test, or a sync-over-async bridge.
- Never block the executor. Send blocking input and output to `spawn_blocking`, CPU work to `rayon` with a `oneshot` reply, and a forever-loop to its own thread.
- Prefer `spawn_blocking` to `block_in_place`, which requires the multi-threaded runtime and suspends everything joined in the same task.
- Hold a `std::sync::MutexGuard` inside a non-async method so it cannot cross an `.await`; ending the guard's scope is what keeps the future `Send`, not calling `drop`.
- Where a guard genuinely must span an `.await`, and only there, use `tokio::sync::Mutex`, which costs more. When the two rules collide, correctness wins: if the guard crosses an await point, take the async mutex.
- Give a contended resource an owner task reached through `mpsc` with `oneshot` replies, instead of an `Arc<Mutex<T>>` shared by many tasks.
- Keep channels bounded, and never form a cycle of bounded sends.
- Audit every `select!` branch for cancellation safety, because dropping a partially completed read loses the bytes it consumed and dropping a lock acquisition loses queue position.
- Write `async fn` in traits directly; add an `async_trait`-style macro only for `dyn` dispatch.
- Keep a library runtime-agnostic: accept the async input and output traits, and never call `spawn` or `block_on` inside library code without an injected handle.
- Shut down with a cancellation token to signal and a task tracker to await, then close the tracker and wait.
- Instrument tasks with `tracing`, since a stack trace tells you almost nothing about a task that is parked.

| Need | Tool |
|---|---|
| data parallelism, CPU-bound | `rayon` parallel iterators |
| blocking input and output from async | `spawn_blocking` |
| many concurrent sockets | `tokio::spawn` |
| one long-lived worker | `std::thread::spawn` plus a channel |
| borrow stack data across threads | `std::thread::scope` |
| run a batch and collect results | `JoinSet` |
| exclusive ownership of one resource | an owner task plus `mpsc` and `oneshot` |
| short critical section, no `.await` inside | `std::sync::Mutex` |
| guard held across `.await` | `tokio::sync::Mutex` |
| counters and flags | `AtomicU64`, `AtomicBool` |
| publish the latest value | a watch channel |
| fan out where slow receivers may lag | a broadcast channel |

Shared state that cannot deadlock across an await point:

```
struct Counter { inner: std::sync::Mutex<u64> }

impl Counter {
    fn bump(&self) -> u64 {                  // deliberately not async
        let mut g = self.inner.lock().expect("counter mutex poisoned");
        *g += 1;
        *g
    }
}
// caller: let n = counter.bump(); do_io(n).await;
```

Detect in existing code:

- a `std::sync::MutexGuard`, `Rc`, or `RefCell` held across an `.await` - the future stops being `Send` and can deadlock.
- `std::fs`, `std::thread::sleep`, `reqwest::blocking`, or `block_on` inside an `async fn` - blocking the executor; use `spawn_blocking` or the async equivalent.
- `tokio::spawn` without `move`, or a spawn in a loop with no bound - a borrow escapes, or tasks grow without limit.
- a `std::sync::Mutex` or channel shared by many tasks where an owner task would serialize access - contention the design can remove.

Corrections:

- `std::thread::sleep(d)` in an `async fn` -> the runtime's own sleep, awaited - thread sleep freezes every task on that worker.
- `tokio::sync::Mutex<HashMap<K, V>>` -> `std::sync::Mutex<HashMap<K, V>>` - the async mutex costs more and nothing awaits inside.
- `spawn_blocking(|| heavy_cpu())` -> `rayon` plus a `oneshot` - the blocking pool is sized for waiting, not computing.
- a cancel-unsafe read inside `select!` -> move the read into its own task - dropping it discards partial reads.
- `let g = m.lock()?; do_async().await;` -> close the guard's scope before awaiting - the future is otherwise not `Send`.

## 15. Unsafe

`unsafe` does not relax the borrow checker; it lets you do five specific things whose preconditions the compiler can no longer check. Treat every use as a proof obligation you write down.

- Set `unsafe_code = "forbid"` for an application and for most libraries, and name the reason wherever you lift it.
- Write `unsafe` only for foreign interfaces, a structure the borrow checker cannot express, a measured elision of a bounds or UTF-8 check, memory-mapped input and output, or hand-written SIMD.
- Put a `// SAFETY:` comment on the line immediately before every `unsafe` block, naming the precondition that holds and why.
- Give every `unsafe fn` a `# Safety` section naming what the caller must guarantee.
- Wrap each operation inside an `unsafe fn` in its own `unsafe` block; edition 2024 stops treating the body as implicitly unsafe.
- Know the five superpowers: dereference a raw pointer, call an `unsafe fn`, access a mutable static, implement an `unsafe trait`, and read a union field.
- Know the undefined behavior you are promising to avoid: breaking `&mut` uniqueness or any aliasing rule, producing an invalid value such as an out-of-range discriminant, reading uninitialized memory, accessing through a dangling or misaligned pointer, and racing on data.
- Use `MaybeUninit<T>` for uninitialized memory, `NonNull<T>` for a non-null owning pointer, and the raw-borrow operators to take a pointer without ever forming a reference.
- Prefer a checked-cast crate to a hand-written `transmute`, which validates neither layout nor value.
- Wrap all `unsafe` in the smallest safe abstraction you can, and run it under Miri in CI, remembering that Miri only checks the paths your tests reach.

```
/// # Safety
/// `ptr` must be valid for reads of `len` bytes and stay live for `'a`.
pub unsafe fn as_slice<'a>(ptr: *const u8, len: usize) -> &'a [u8] {
    // SAFETY: the caller guarantees validity and lifetime per the contract above.
    unsafe { std::slice::from_raw_parts(ptr, len) }
}
```

Detect in existing code:

- an `unsafe` block with no `// SAFETY:` on the line above - clippy `undocumented_unsafe_blocks`.
- a `pub unsafe fn` with no `# Safety` section - clippy `missing_safety_doc`.
- `transmute`, or a `&mut` formed from a `&` - layout, value, or aliasing left unchecked.
- `static mut` or `&STATIC_MUT` - a hard error in edition 2024; use `OnceLock` or an atomic.
- `unsafe` wrapped around code that only silences a borrow error - restructure the ownership instead.

Corrections:

- `unsafe fn f() { g(); }` -> `unsafe fn f() { /* SAFETY: ... */ unsafe { g() } }` - edition 2024 wants the inner block.
- `extern "C" { fn c(); }` -> `unsafe extern "C" { fn c(); }` - edition 2024 requires it.
- `&STATIC_MUT` -> a `OnceLock` or an atomic - a reference to a mutable static is now a hard error.
- `mem::transmute::<[u8; 4], u32>(b)` -> `u32::from_le_bytes(b)` - the standard library already does this safely.
- `unsafe` to quiet a borrow error -> restructure the ownership - `unsafe` cannot make aliasing sound.

## 16. no_std, foreign interfaces, macros, and build scripts

Each of these adds a boundary the compiler checks less well. Keep the boundary thin and the code behind it ordinary.

- Write `#![no_std]` against `core`, adding `extern crate alloc;` only where you need `Vec`, `String`, or `Box`.
- Layer with an additive, default-on `std` feature, and propagate `default-features = false` to every dependency.
- Provide a panic handler in a bare-metal crate, and prefer a fixed-capacity collection to any allocation.
- Make every foreign type `#[repr(C)]`, or `#[repr(transparent)]` for a newtype, and expose no Rust enum, `str`, reference, `Vec`, or generic type across the boundary.
- Treat every incoming pointer as unvalidated, and convert strings explicitly through the C string types.
- Split a foreign interface into a `-sys` crate holding the declarations and the linking, plus a safe wrapper crate above it.
- Never let a panic escape an `extern "C"` function; catch it and return an error code, because unwinding out of one aborts the process.
- Reach for a function, then a generic, then `macro_rules!`, then a proc macro, in that order.
- Declare `macro_rules!` before its first use, since macro name resolution is order-dependent.
- Refer to your own items from an exported macro as `$crate::path::item`; a bare path resolves in the caller's scope and breaks.
- Split a proc macro into `foo` plus `foo-derive`, re-export it behind a `derive` feature, and test its diagnostics with `trybuild`.
- Add `build.rs` only for native code, real code generation, or system probing; a build script costs build time and complicates cross-compilation.
- Emit at least one re-run trigger from every build script, write only into `OUT_DIR`, and include the result with `include!`.
- Read the target through the environment variables Cargo sets in a build script, never through `cfg!`, which reports the host and breaks cross-compilation silently.
- Prefer checked-in generated code to a build script when the input rarely changes; it costs nothing at build time and reviews cleanly.

```
fn main() {
    println!("cargo::rerun-if-changed=src/grammar.txt");
    println!("cargo::rustc-check-cfg=cfg(has_avx512)");
    if std::env::var("CARGO_CFG_TARGET_ARCH").as_deref() == Ok("x86_64") {
        println!("cargo::rustc-cfg=has_avx512");
    }
    let out = std::path::PathBuf::from(std::env::var_os("OUT_DIR").unwrap());
    std::fs::write(out.join("generated.rs"), generate()).unwrap();
}
// in lib.rs: include!(concat!(env!("OUT_DIR"), "/generated.rs"));
```

Detect in existing code:

- an `extern "C"` function whose body can panic with no `catch_unwind` - unwinding across it aborts the process.
- a Rust `enum`, `str`, `&T`, `Vec`, or generic exposed across an FFI boundary - only `#[repr(C)]` or `#[repr(transparent)]` types cross safely.
- a bare path, not `$crate::...`, to a crate item inside an exported `macro_rules!` - it resolves in the caller's scope and breaks.
- a `build.rs` that writes outside `OUT_DIR`, or reads `cfg!` for the target - non-hermetic, and wrong under cross-compilation.

## 17. Version-sensitive facts

These change with the toolchain. Check them against the current release before relying on one.

Edition 2024 changes behavior, not only syntax:

- An `unsafe fn` body is no longer implicitly unsafe, and `unsafe_op_in_unsafe_fn` warns.
- `extern` blocks must be written `unsafe extern`, and `no_mangle`, `export_name`, and `link_section` must be wrapped as `#[unsafe(...)]`.
- A reference to a mutable static is a hard error.
- Return-position `impl Trait` captures every in-scope lifetime; narrow it with `+ use<...>`, and note that narrowing is a semver commitment.
- Temporaries in an `if let` scrutinee drop before the `else` block, and block tail-expression temporaries drop earlier, both of which shift lock release timing.
- Never-type fallback changed, `gen` became a reserved keyword, and the environment-mutating functions became `unsafe`.
- Resolver 3 is the default, and it prefers dependency versions compatible with your declared `rust-version`.

Version gates worth knowing, since a lower MSRV forces the older spelling:

| Feature | Needs |
|---|---|
| let chains, and only under edition 2024 | 1.88 |
| edition 2024 | 1.85 |
| resolver 3 | 1.84 |
| `#[expect(...)]` | 1.81 |
| `LazyLock`, `LazyCell` | 1.80 |
| `cargo::rustc-check-cfg` honored; silently ignored from 1.77 to 1.79 | 1.80 |
| `cargo::` build directives, double colon | 1.77 |
| `async fn` in traits | 1.75 |
| `[lints]` and `[workspace.lints]` tables | 1.74 |
| `OnceLock`, `OnceCell` | 1.70 |
| generic associated types, `let ... else` | 1.65 |
| `thread::scope` | 1.63 |
| `dep:` and weak `?` features | 1.60 |

Calls this file makes where the ecosystem is genuinely split, and the reason for the choice:

- Test layout. The Rust Book puts each integration test in its own file under `tests/`; large workspaces consolidate into one binary because each file relinks the library. This file consolidates.
- Module files. `foo.rs` plus `foo/` is the Book's guidance; some large crates keep `mod.rs` so a directory holds everything for its module. Either is defensible, mixing them within one crate is not.
- Error granularity. One error enum per crate is common and easy; one per unit of fallibility is better for a stable public API, because a caller never sees a variant the function cannot produce.
- Locks. `std::sync` is the default now that it is futex-based; `parking_lot` wins under sustained contention and when you need mapped guards or timed locks.
- Toolchain pinning. Pin `rust-toolchain.toml` for an application and for any job asserting diagnostic text; let a library float on stable so contributors need no extra toolchain.
- Benchmarking. `criterion` is the default here because its maintenance is unambiguous; check the current state of the alternatives before adopting one.
- Generic argument types. The API guidelines favor `impl AsRef<Path>` for caller convenience; compile-time-conscious crates take `&Path`. Section 6 states the split and the shim that satisfies both.

## 18. File index

| Concept | Files |
|---|---|
| crate facade | `src/lib.rs` |
| binaries | `src/main.rs`, `src/bin/*.rs` |
| platform code | `src/sys/<platform>.rs` |
| unit tests | `#[cfg(test)] mod tests` in the file under test |
| integration tests | `tests/it/main.rs`, with `tests/common/mod.rs` for helpers |
| compile-fail tests | `tests/ui/*.rs` with checked-in `.stderr` |
| benchmarks, examples | `benches/`, `examples/` |
| manifest, features, lints | `Cargo.toml`, and `[workspace.lints]` in the root manifest |
| lockfile | `Cargo.lock`, committed |
| profiles, patches | the workspace root manifest only |
| aliases, linker, wrapper | `.cargo/config.toml` |
| toolchain pin | `rust-toolchain.toml` |
| formatting, lint, dependency policy | `rustfmt.toml`, `clippy.toml`, `deny.toml` |
| repo automation | `xtask/src/main.rs` |
| code generation | `build.rs`, writing into `OUT_DIR` |
| reader documentation | `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md` |
| CI | `.github/workflows/` |


## Binding rules (restated)

- Restructure ownership to fix a borrow error; `unsafe` is not a borrow-checker escape hatch.
- Return `Result` for expected failures; panic only on bugs, and say which invariant broke.
- Declare lints in `[lints]` and `[workspace.lints]`, not at the crate root.
- Document every public item, with `# Errors`, `# Panics`, and `# Safety` where they apply, and make examples doctests.
- Test in the same change as the code, unit tests in the file under test and integration tests in one binary.
- Format with rustfmt and pass Clippy with warnings denied before committing.
- Verify every crate is the intended, existing package, in new code and when auditing `Cargo.toml`; a wrong name compiles like any other.

*2026-07-25 - Opus 5 (Cursor agent). Distilled from web research on Rust project layout, API design, ownership, error handling, documentation, tooling, and the crate ecosystem.*
