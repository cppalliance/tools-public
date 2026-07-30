---
description: Reference for a model making changes to Clang and LLVM source - architecture, conventions, core APIs, extension recipes, testing, and build/debug workflow
---

<!-- Load this file into context before editing Clang or LLVM. Highest-value reference only; consult llvm.org/docs for depth. -->

# Clang and LLVM Maintenance Rulebook

This file equips a model to read, modify, and extend Clang and LLVM. Read the preamble and the closing rules first; they bind every edit. Sections run from most to least frequently needed. Terms used throughout: "the tree" is the llvm-project checkout; "a pass" is one LLVM IR transformation or analysis; "the new pass manager" is the current PassBuilder-based pipeline; "the frontend" is Clang (Lex, Parse, Sema, AST, CodeGen). Target current LLVM built with assertions on.

![The Dragon Keepers](images/how-to-maintain-clang.png)

## Non-negotiable edit rules

Follow these on every change; they are restated at the end.

- Format with clang-format and follow the LLVM Coding Standards (section 2); layout is settled by the tool, not by taste.
- Prefer LLVM ADT and `StringRef`/`ArrayRef` over `std::` containers and string copies (section 3), because the codebase assumes them for size and speed.
- Cast with `isa`/`cast`/`dyn_cast`, and check every `Error` (section 3); RTTI is off and `Error` is `[[nodiscard]]`, so both fail to build otherwise.
- Add a lit/FileCheck or `-verify` test for every change (section 8); a change without a test is incomplete, because nothing guards against regression.
- Build with assertions on (section 9); many verifier checks and `-debug-only` flags depend on it.

## 1. Orientation

Compilation pipeline, front to back:

```
source -> [Clang: Lex + Preprocess] -> [Parse] -> [Sema] -> Clang AST
  -> [CodeGen] -> LLVM IR -> [IR passes: new pass manager] -> optimized IR
  -> [instruction selection: SelectionDAG or GlobalISel] -> MachineIR
  -> [register allocation] -> [MC layer] -> object or assembly
```

Directory map (only what you edit often):

| Path | Holds |
|---|---|
| `llvm/lib/` | LLVM libraries: `IR/`, `Analysis/`, `Transforms/`, `CodeGen/`, `Target/`, `MC/` |
| `llvm/include/llvm/` | public LLVM headers, mirroring `lib/` |
| `clang/lib/` | Clang stages: `Lex/`, `Parse/`, `Sema/`, `AST/`, `CodeGen/`, `Driver/` |
| `clang/include/clang/Basic/` | TableGen for diagnostics, builtins, and attributes |
| `clang-tools-extra/clang-tidy/` | clang-tidy checks |
| `llvm/test/`, `clang/test/`, `unittests/` | lit tests and gtest unit tests |

## 2. Coding conventions

Apply to every edit; clang-format enforces most layout.

- Run clang-format; it owns brace placement, wrapping, and spacing.
- Name types `UpperCamelCase`, functions `lowerCamelCase`, and variables `UpperCamelCase`; match the surrounding file when it differs.
- Build with no exceptions and no RTTI; use LLVM RTTI (`isa`/`cast`/`dyn_cast`), not `dynamic_cast` or `typeid`.
- Assert with a message: `assert(cond && "why")`; mark impossible paths with `llvm_unreachable("why")`.
- Order includes: the file's own header first, then other project headers, then `llvm/...` and `clang/...`, then system headers.
- Prefer early return over deep nesting; prefer `StringRef` and `ArrayRef` parameters over `const std::string&` and `const std::vector&`.
- Comment the why; let names carry the what. Put Doxygen `///` on public declarations.

## 3. LLVM and Clang culture and idioms

Write code that reads as native LLVM. This matters beyond style: LLVM ships its own containers, RTTI, and error types, builds with assertions and an IR verifier, and disables C++ RTTI and exceptions, so non-idiomatic code trips an assert or fails to compile. Each rule below pairs a `wrong -> right` fix.

Containers (`llvm/ADT`):
- Prefer `SmallVector<T, N>`, `DenseMap`, `DenseSet`, `StringMap`, `SetVector`, and `MapVector` over the `std::` equivalents; a custom `DenseMap` key needs a `DenseMapInfo`.
- Pass `StringRef` for strings and `ArrayRef<T>` for arrays; build concatenations with `Twine` and `SmallString`.
  - `std::vector<int> v;` -> `SmallVector<int> v;`
  - `const std::string &s` -> `StringRef s`
  - `const std::vector<T> &xs` -> `ArrayRef<T> xs`
  - `std::map<K, V> m;` -> `DenseMap<K, V> m;` (use `MapVector` when iteration order matters)

RTTI and casting (`llvm/Support/Casting.h`):
- Test with `isa<T>(V)`, assert-and-cast with `cast<T>(V)`, test-and-cast with `dyn_cast<T>(V)`, and tolerate null with `dyn_cast_if_present<T>(V)`. A class opts in by defining a static `classof`.
  - `(Foo *) V` -> `cast<Foo>(V)` when known, or `if (auto *F = dyn_cast<Foo>(V))` when unsure
  - `dyn_cast_or_null<Foo>(V)` -> `dyn_cast_if_present<Foo>(V)`

Error handling (`llvm/Support/Error.h`):
- Return `Expected<T>` or `Error`; `Error` is `[[nodiscard]]`, so consume it with `handleAllErrors`, `consumeError`, or `cantFail`, or propagate it. Use `report_fatal_error` for unrecoverable input and `llvm_unreachable("why")` for impossible states.
  - a returned `Error` left unchecked -> propagate it, or `consumeError(std::move(Err))`
  - `assert(0 && "unreachable");` -> `llvm_unreachable("unreachable");`

Optionals and ownership:
- Use `std::optional<T>` and `std::nullopt`; `llvm::Optional` was removed in LLVM 17. Own heap objects with `std::unique_ptr<T>` created by `std::make_unique`.
  - `llvm::Optional<int> X = None;` -> `std::optional<int> X = std::nullopt;`
  - `T *P = new T(...); ... delete P;` -> `auto P = std::make_unique<T>(...);`

Debugging and statistics:
- Gate tracing on `LLVM_DEBUG(dbgs() << ...)` under a file-local `#define DEBUG_TYPE "name"`, shown with `-debug-only=name`; count events with `STATISTIC(NumX, "what it counts")`.
  - `printf("folded\n");` -> `LLVM_DEBUG(dbgs() << "folded\n");`

Generated tables:
- Declare diagnostics, driver options, intrinsics, attributes, and builtins in TableGen `.td` files; the build regenerates the `.inc` files. Do not hand-write what a `.td` owns.

## 4. Core APIs

### 4.1 LLVM IR

- Hierarchy: a `Module` holds `Function`s, a `Function` holds `BasicBlock`s, a `BasicBlock` holds `Instruction`s; every `Instruction` is a `Value` and a `User`.
- Def-use: `Value::users()`, `Value::uses()`, and `Instruction::replaceAllUsesWith` (RAUW).
- Types and constants come from an `LLVMContext`: `Type::getInt32Ty(Ctx)`, `FunctionType::get(...)`, `ConstantInt::get(...)`.
- Classify instructions with `dyn_cast`: `if (auto *LI = dyn_cast<LoadInst>(&I))`.
- Validate with `verifyFunction(F)` or `verifyModule(M)` after building IR.

Build IR with `IRBuilder`:

```
IRBuilder<> B(BB);                       // insert at end of BB
Value *Sum = B.CreateAdd(X, Y, "sum");
B.CreateStore(Sum, Ptr);
Value *R = B.CreateCall(Callee, {Sum});
B.CreateRet(R);
```

Walk a function:

```
for (BasicBlock &BB : F)
  for (Instruction &I : BB)
    if (auto *CI = dyn_cast<CallInst>(&I))
      handleCall(CI);
```

### 4.2 Clang AST

- Node families: `Decl` (declarations), `Stmt` (statements), and `Expr` (a `Stmt` subclass for expressions); `ASTContext` owns the nodes and interns each `QualType`.
- Source: a `SourceLocation` plus the `SourceManager` map a node to source; diagnostics take a `SourceLocation`.
- Traverse with `RecursiveASTVisitor<Derived>` (define `VisitCallExpr`, and so on) or an `ASTConsumer`; match declaratively with AST matchers, for example `callExpr(callee(functionDecl(hasName("malloc"))))`.
- AST nodes use LLVM RTTI: `dyn_cast<CXXRecordDecl>(D)`.
- Inspect a real AST with `clang -Xclang -ast-dump file.cpp`.

## 5. Extension recipes

Each recipe lists the files to edit in order, then the pattern.

### 5.1 Add a diagnostic or warning

1. Declare it in `clang/include/clang/Basic/Diagnostic<Area>Kinds.td` (prefix `err_`, `warn_`, `ext_`, or `note_`).
2. For a warning, attach it to a group in `clang/include/clang/Basic/DiagnosticGroups.td`.
3. Emit it where detected: `S.Diag(Loc, diag::warn_my_thing) << Arg;`.
4. Test with `-verify`: `// expected-warning {{my thing}}`.

```
def warn_my_thing : Warning<"my thing happened with %0">,
                    InGroup<MyThing>;   // Diagnostic<Area>Kinds.td
def MyThing : DiagGroup<"my-thing">;    // DiagnosticGroups.td
```

### 5.2 Add a clang-tidy check

1. Scaffold it: `clang-tools-extra/clang-tidy/add_new_check.py <module> <check-name>`.
2. Implement `registerMatchers(MatchFinder *)` and `check(const MatchFinder::MatchResult &)`.
3. Fill in the doc stub and the `clang-tools-extra/test/clang-tidy/` test the script created.

### 5.3 Add an LLVM pass (new pass manager)

1. Write the pass under `llvm/lib/Transforms/<Area>/` with a header in `llvm/include/llvm/Transforms/<Area>/`.
2. Register it in `llvm/lib/Passes/PassRegistry.def` and expose it through `PassBuilder`.
3. Run it: `opt -passes=my-pass in.ll -S`.

```
struct MyPass : PassInfoMixin<MyPass> {
  PreservedAnalyses run(Function &F, FunctionAnalysisManager &AM) {
    // transform F
    return PreservedAnalyses::none();
  }
};
```

### 5.4 Add an intrinsic

1. Declare it in `llvm/include/llvm/IR/Intrinsics*.td` with `Intrinsic<[returns], [args], [properties]>`.
2. Lower or fold it where it is consumed; add a test under `llvm/test/`.

### 5.5 Add a Clang builtin

1. Declare it in `clang/include/clang/Basic/Builtins.td`, or a target file such as `BuiltinsX86.td` with `X86Builtin<"proto">`.
2. Check arguments in `clang/lib/Sema/SemaChecking.cpp` and emit it in `clang/lib/CodeGen/CGBuiltin.cpp`.

### 5.6 Add a driver or compiler flag

1. Declare it in `clang/include/clang/Driver/Options.td` with its flags and help text.
2. Wire it through the driver and `CompilerInvocation`, and handle it in `-cc1`.

### 5.7 Add an attribute

1. Declare it in `clang/include/clang/Basic/Attr.td`.
2. Handle it in `clang/lib/Sema/SemaDeclAttr.cpp` and document it in `AttrDocs.td`.

## 6. Frontend (Clang)

Clang lexes and parses source into a typed AST, checks it in Sema, then lowers it to LLVM IR in CodeGen. Most frontend edits add a diagnostic, a semantic rule, or IR lowering.

- Lex (`clang/lib/Lex`): the `Preprocessor` produces `Token`s and expands macros.
- Parse (`clang/lib/Parse`): a hand-written recursive-descent `Parser` calls Sema `Act*` handlers to build the AST.
- Sema (`clang/lib/Sema`, `Sema*.cpp` by area): name lookup, overload resolution, type checking, and most diagnostics.
- AST (`clang/lib/AST`): the node classes, `ASTContext`, and `QualType`.
- CodeGen (`clang/lib/CodeGen`): `CodeGenModule` and `CodeGenFunction` lower the AST to IR through `IRBuilder` in `EmitStmt` and `EmitExpr`.
- Where a change goes: grammar in Parse; a semantic rule or diagnostic in Sema; IR lowering in CodeGen; a lint that needs no compiler change in clang-tidy.

## 7. Backend (LLVM)

The middle end optimizes LLVM IR; the backend turns IR into machine code for a target.

- IR passes run under the new pass manager; analyses come from an `AnalysisManager`; transforms live in `llvm/lib/Transforms` and analyses in `llvm/lib/Analysis`.
- CodeGen path: IR -> instruction selection (`SelectionDAG` by default, `GlobalISel` where enabled) -> `MachineInstr` -> register allocation -> MC -> object or assembly.
- A target lives in `llvm/lib/Target/<Arch>`: TableGen `.td` files define registers, instructions, and selection patterns; `TargetLowering` implements custom lowering and calling conventions.
- The MC layer (`llvm/lib/MC`) emits assembly and object files.
- Reproduce backend behavior with `llc in.ll -o out.s`; inspect a pass with `opt -passes=... -print-after-all`.

## 8. Testing

Tests run under lit; most check tool output with FileCheck, and Clang diagnostics use `-verify`.

- Put IR and codegen tests under `llvm/test/`, Clang tests under `clang/test/`, and gtest unit tests under `unittests/`.
- A lit test drives tools from `// RUN:` lines with substitutions such as `%clang`, `%clang_cc1`, `%s`, and `%t`.
- Match output with FileCheck: `CHECK`, `CHECK-NEXT`, `CHECK-SAME`, `CHECK-DAG`, `CHECK-LABEL`, `CHECK-NOT`, and `--check-prefix`.

```
; RUN: opt -passes=instcombine -S %s | FileCheck %s
define i32 @f(i32 %x) {
; CHECK-LABEL: @f(
; CHECK: ret i32 %x
  %a = add i32 %x, 0
  ret i32 %a
}
```

- Test Clang diagnostics with `-verify` and inline expectations: `// expected-warning {{...}}`, `// expected-error {{...}}`, `// expected-note {{...}}`.
- Regenerate CHECK lines instead of hand-editing: `llvm/utils/update_test_checks.py` for IR, `clang/utils/update_cc_test_checks.py` for Clang CodeGen.
- Run tests: `llvm-lit -v llvm/test/Transforms/InstCombine/foo.ll`, or a suite with `ninja check-llvm` or `ninja check-clang`.

## 9. Build and debug

Configure once with CMake and Ninja, then build the target you need:

```
cmake -G Ninja -S llvm -B build \
  -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra" \
  -DLLVM_TARGETS_TO_BUILD="X86;AArch64" \
  -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_ASSERTIONS=ON \
  -DLLVM_USE_LINKER=lld -DLLVM_CCACHE_BUILD=ON -DLLVM_OPTIMIZED_TABLEGEN=ON
ninja -C build clang        # or: ninja -C build opt llc
```

- Keep `LLVM_ENABLE_ASSERTIONS=ON` while developing; `-debug-only` and many verifier checks need it.
- Iterate by building one target (`ninja -C build opt`) rather than everything.
- Trace a pass: `LLVM_DEBUG(dbgs() << ...)` shown with `-debug-only=<DEBUG_TYPE>`; aggregate counters with `-stats`.
- Watch IR change through the pipeline: `opt -passes=... -print-after-all -print-changed in.ll`.
- Inspect the frontend: `clang -Xclang -ast-dump file.cpp`; see emitted IR with `clang -emit-llvm -S file.c -o -`.
- Ask why an optimization did or did not fire: `-Rpass=`, `-Rpass-missed=`, `-Rpass-analysis=`.
- Shrink a crash or miscompile to a minimal reproducer with `llvm-reduce`.

## 10. File index

| Concept | Files |
|---|---|
| LLVM IR | `llvm/include/llvm/IR/{Module,Function,BasicBlock,Instructions,IRBuilder}.h` |
| Passes and analysis | `llvm/lib/Transforms/`, `llvm/lib/Analysis/`, `llvm/lib/Passes/{PassBuilder.cpp,PassRegistry.def}` |
| ADT and Support | `llvm/include/llvm/ADT/{SmallVector,DenseMap,StringRef,ArrayRef}.h`, `llvm/include/llvm/Support/{Error,Casting,Debug}.h` |
| Clang stages | `clang/lib/{Lex,Parse,Sema,AST,CodeGen,Driver}/` |
| Clang TableGen | `clang/include/clang/Basic/{Diagnostic*Kinds.td,DiagnosticGroups.td,Builtins.td,Attr.td}`, `clang/include/clang/Driver/Options.td` |
| Intrinsics | `llvm/include/llvm/IR/Intrinsics*.td` |
| Targets | `llvm/lib/Target/<Arch>/` |
| clang-tidy | `clang-tools-extra/clang-tidy/` |
| Tools | `llvm/tools/{opt,llc}/`, `clang/tools/` |
| Tests | `llvm/test/`, `clang/test/`, `unittests/` |

## Binding rules (restated)

- Format with clang-format; follow the LLVM Coding Standards.
- Prefer LLVM ADT (`SmallVector`, `DenseMap`, `StringRef`, `ArrayRef`) over `std::` equivalents.
- Cast with `isa`/`cast`/`dyn_cast`, check every `Error`, and use `std::optional`.
- Author passes with the new pass manager and register them in `PassRegistry.def`.
- Add a lit/FileCheck or `-verify` test for every change; regenerate CHECK lines with the update scripts.
- Build with assertions on; reduce failures with `opt`, `llc`, and `llvm-reduce`.

*2026-07-24 - Opus 4.8 (Cursor agent). Distilled from web research on LLVM and Clang architecture, coding standards, testing, and workflow.*
