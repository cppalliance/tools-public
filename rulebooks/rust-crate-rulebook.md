---
description: Reference for a model laying out, decomposing, building, testing, versioning, and publishing a large multi-crate Rust workspace
---

<!-- Load this file into context before restructuring a Rust workspace, splitting a crate, or adding crates to one. Highest-value reference only; consult doc.rust-lang.org/cargo for depth. -->

# Rulebook: Structuring a Multi-Crate Rust Workspace

This file equips a model to lay out and maintain a Rust project that has outgrown one crate. Terms used throughout: "the workspace" is the set of crates sharing one `Cargo.lock` and one `target/`; "a member" is one crate in the workspace; "the facade" is the one crate consumers depend on, which re-exports the rest; "a vocabulary crate" is a bottom-layer crate holding plain data types and traits with no implementation. Apply these rules once a project passes roughly 10,000 lines; below that, keep a single crate with modules. Target current stable Rust with edition 2024 and resolver 3.

![Robot Port](images/rust-crates-rulebook.jpg)

## 1. Workspace root

- Use exactly one workspace per repository; Cargo rejects nested workspaces.
- Make the root manifest virtual: a `[workspace]` table with no `[package]`, so no crate is special-cased and commands at the root operate on all members.
- Set `members = ["crates/*"]` so adding a crate is creating a directory, not editing a list.
- Set `resolver = "3"` explicitly; a virtual manifest defaults to resolver 1 even when every member is edition 2021 or later. If the MSRV is below 1.84, set `resolver = "2"` instead.
- Move shared fields into `workspace.package`, third-party versions into `workspace.dependencies`, and lint levels into `workspace.lints`; inherit in each member with `workspace = true`, so a version or lint changes in exactly one place.
- Add only `optional` and `features` when inheriting a dependency; a `workspace.dependencies` entry itself is never `optional`.
- Keep the dependency graph acyclic, dev-dependency cycles included; a dev-dependency cycle links two copies of a library into one test binary with incompatible types.

## 2. Layout

- Keep one flat `crates/` directory; a directory tree creates a second hierarchy beside Cargo's flat namespace, and the two drift apart.
- Name each member directory identically to its package name, so the path alone states the crate.
- Keep a `src/` directory even for a single-file crate, so every member has the same shape.
- Mark every crate that will never be published with `publish = false` or `version = "0.0.0"`, so an accidental `cargo publish` fails instead of releasing internals.
- Keep semver-published libraries in a separate directory such as `lib/`, so the publishable set is visible from `ls` alone.
- Set `default-members` when the full workspace is not the everyday build, so a bare `cargo build` stays fast.

## 3. Dependency graph shape

- Shape the graph as a wide diamond: a few slow-changing vocabulary crates at the bottom, independent feature crates fanning out in the middle, one thin binary or facade fanning in on top. A chain compiles serially and rebuilds everything downstream of any edit; a wide graph compiles in parallel and isolates rebuilds.
- Keep proc-macro and serialization dependencies in leaf crates; a `syn` dependency near the foundation stalls every crate above it, because rustc must run proc macros before it can compute metadata.
- Keep crate interfaces concrete; generic code at a crate boundary is monomorphized once per consuming crate, which multiplies compile time across the workspace.
- Put each proc macro in its own crate; the compiler forbids using a procedural macro from the crate that defines it.
- Expect the orphan rule to forbid an `impl` once a trait and a type land in different crates; place both in a shared lower crate, or add a third crate that both depend on.
- Run `cargo build --timings` before splitting anything for speed, and split the crate the chart shows serializing the build.
- Accept that a crate boundary forces items `pub` that a module boundary kept private; treat that cost as part of the split decision.

## 4. Naming and crate roles

- Prefix every crate name with the project name, so workspace crates are recognizable in `Cargo.lock`, build output, and crates.io.
- Never use `-rs` or `-rust` as a prefix or suffix; the ecosystem already knows the crate is Rust.
- Name an FFI crate `<name>-sys`; it links the native library and exposes raw declarations only, with the safe API in the companion crate.
- Name a minimal, slow-changing primitives crate `<name>-core`, so dependents that need stability can pin the stable surface.
- Name a proc-macro crate `<name>-macros` or `<name>-derive`, and re-export it from the main crate so users depend on one name.
- Name a plain-data-and-traits crate `<name>-types`, with the interface in `<name>-client` and the implementation in `<name>`.
- Publish through one facade crate that re-exports the subcrates, so consumers take a single dependency.
- Treat a major version bump of any re-exported subcrate as a major bump of the facade; a public dependency's version is part of the facade's own API.

## 5. Testing

- Give each published crate exactly one integration test binary at `tests/it/main.rs`, split into modules; every file under `tests/` compiles and links as its own crate, so many files multiply compile time and disk use.
- Keep unit tests inside internal crates and set `[lib] doctest = false` there; each doctest links as a separate binary.
- Put shared test fixtures in a `publish = false` test-utils crate, and keep its dependencies minimal because every test binary waits on it.
- Run the suite with `cargo-nextest`, which builds test binaries once and runs each test in its own process in parallel; keep doctests runnable by `cargo test --doc` because nextest skips them.

## 6. Versioning and publishing

- Decide the versioning model in writing before the first publish.
- Version in lockstep with `version.workspace = true` when the crates ship as one product; version independently when consumers depend on the crates separately.
- When versioning independently, declare each intra-workspace dependency at the oldest version the crate works with, so downstream resolves are not forced forward without cause.
- Declare every intra-workspace dependency with both `path` and `version`; crates.io rejects a published package whose dependencies point outside the registry, and `path` alone does not publish.
- Publish with `cargo publish --workspace` (Rust 1.90 or later), which releases members in dependency order; plan for partial failure, because the publishes are not atomic.
- Drive releases with `cargo-release` or `release-plz` so version bumps, changelogs, and tags stay mechanical, and run `cargo-semver-checks` on published crates before each release.
- Use `[patch]` only in the root manifest; it is ignored anywhere else.

## 7. Shared configuration

- Commit `Cargo.lock`, `rust-toolchain.toml`, `rustfmt.toml`, `clippy.toml`, and `.cargo/config.toml` at the workspace root; the first four are discovered by walking up the tree, so one copy serves every member.
- Commit `Cargo.lock` for libraries and binaries alike; current Cargo guidance drops the old library exemption.
- Set `rust-version` in `workspace.package` and state the MSRV policy beside it, for example "no newer than stable minus 2"; resolver 3 then prefers dependency versions compatible with the MSRV.
- Allow a whole clippy group at negative priority and re-enable selected lints, so a new compiler release adds lints without breaking the build.
- Duplicate the lint table in a member that needs a relaxed lint, because a member cannot override an inherited lint level.

## 8. Build performance

- Measure before restructuring: run `cargo build --timings` and read the critical path; split a crate only when the chart shows it serializing the build.
- Add a `workspace-hack` crate through `cargo-hakari` only after `-p` versus `--workspace` builds show repeated third-party rebuilds; feature unification between per-package and whole-workspace builds is the disease, and the hack is the cure, not a default.
- Set `debug = "line-tables-only"` in the dev profile; full debuginfo costs up to a fifth of dev build time and line tables keep backtraces.
- Set `[profile.dev.package."*"] opt-level = 3` to optimize dependencies while keeping members fast to compile.
- In CI, set `CARGO_INCREMENTAL=0`, disable debuginfo, cache dependencies but not workspace crates, and run `cargo test --no-run` as a separate step from the test run.

## 9. Tooling

- Adopt `cargo-nextest`, `cargo-deny` with a root `deny.toml`, `cargo-hack` for per-member feature checks, and `cargo-semver-checks` for published crates from the start; retrofitting them onto a large workspace costs more than running them from day one.
- Put every repo command that is not a plain `cargo` subcommand into an `xtask` crate with a `.cargo/config.toml` alias, so automation is cross-platform Rust that bootstraps from cargo alone.
- Stay on Cargo unless the build graph must span non-Rust artifacts with remote execution; Bazel and Buck2 cost `cargo check`, IDE integration, and the publish path, and no Rust-only workspace gains from them.

## 10. Architecture document

- Write an `ARCHITECTURE.md` at the root with a code map that answers "where is the thing that does X?", the named invariants, and the list of API-boundary crates; finding where to change code costs more than changing it, and this document is what closes that gap.
- Mark each boundary crate in the document, because rules at a boundary are stricter than rules inside the graph.
- Revisit the document twice a year rather than on every change; a roughly right map beats a stale one that pretends to be exact.
- Give each published crate a README and include it as the crate documentation with `#![doc = include_str!("../README.md")]`, so one file serves the repository and docs.rs.

Restated: one virtual-root workspace, a flat `crates/` where directory equals package, a wide diamond graph with concrete interfaces, one integration test binary per published crate, and every shared setting inherited from the root.

*2026-09-17 - kimi-k3 (Cursor agent). Distilled from "Structuring a Large Multi-Crate Rust Project" (master report, 2026-09-17), which holds the evidence and sources.*
