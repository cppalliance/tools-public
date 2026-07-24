---
description: Reference for a model making changes to GCC source - architecture, conventions, core APIs, extension recipes, testing, and build/debug workflow
---

<!-- Load this file into context before editing GCC. Highest-value reference only; consult gcc/doc/gccint for depth. -->

# Maintaining GCC

This file equips a model to read, modify, and extend the GNU Compiler Collection. Read the preamble and the closing rules first; they bind every edit. Sections run from most to least frequently needed. Terms used throughout: "the tree" is the GCC source checkout; "a pass" is one optimization or transformation stage; "the middle end" is the target- and language-independent optimizers.

<img src="images/how-to-maintain-gcc.png">

## Non-negotiable edit rules

Follow these on every change; they are restated at the end.

- Match GNU style exactly (section 2); send formatting-only fixes as separate commits, so review and regression bisection stay clean.
- Emit diagnostics with explicit-location calls (`error_at`, `warning_at`), not the `input_location` globals, so messages point at the right code.
- Add a test for every bug fix and feature (section 8); a change without a test is incomplete, because nothing guards against regression.
- Build out of tree (section 9); in-tree builds are unsupported and fail.
- After adding a source file, add its `.o` to `OBJS` in `gcc/Makefile.in` and re-run `configure`; the build ignores files absent from `OBJS`.

## 1. Orientation

Compilation pipeline, front to back:

```
source -> [front end: parse] -> GENERIC (language-independent trees)
  -> [gimplify] -> GIMPLE (3-address) -> [build CFG + into-SSA] -> GIMPLE-SSA
  -> [~20 tree-SSA optimization passes] -> [expand] -> RTL
  -> [RTL passes + register allocation: IRA then LRA] -> [final] -> assembly
```

Directory map (only what you edit often):

| Path | Holds |
|---|---|
| `gcc/` | compiler core; the middle end is the files at this top level |
| `gcc/c/`, `gcc/cp/`, `gcc/c-family/` | C, C++, and shared C/C++ front ends |
| `gcc/config/<arch>/` | one back end per target (`.md`, `.h`, `.cc`, `.opt`) |
| `gcc/testsuite/` | DejaGnu tests |
| `gcc/doc/` | Texinfo manuals (`invoke.texi`, `extend.texi`, `gccint`) |
| `libgcc/`, `libstdc++-v3/`, `libcpp/`, `libiberty/` | runtime and support libraries |

## 2. Coding conventions

Apply to every edit; verify with `contrib/check_GNU_style.py <patch>`.

Formatting (GNU style):
- Indent 2 spaces per level; set tab width 8 and replace 8 leading spaces with a tab.
- Put the function-body opening brace in column 0; put every other brace on its own line, indented 2 from its statement.
- Put a space between a function name and `(`: write `foo (x)`, not `foo(x)`.
- Cap lines at 80 columns; strip trailing whitespace.

Naming:
- Name functions and variables `lower_snake_case`.
- Name macros `ALL_CAPS`, except a macro that wraps a function for speed (`size_int`).
- Prefix data members `m_` and static data members `s_`.

C++ policy (GCC bootstraps with a C++11 subset):
- Build with `-fno-exceptions` and `-fno-rtti`; add no `throw`, `try`, or `typeid`.
- Cast with C++ casts (`static_cast`, `reinterpret_cast`); add no C-style casts.
- Use `printf`-style output; add no `<iostream>`.
- Assert with `gcc_assert (expr)`; mark impossible paths with `gcc_unreachable ()`; gate costly checks behind `gcc_checking_assert`.
- Keep the standard library away from garbage-collected data (section 4.7); gengtype cannot trace it.

Diagnostics:
- Write full, translatable sentences; start the message lowercase, with no trailing period and no embedded newline.
- Call `error_at` (user-code defect), `warning_at` (advisory, with an `OPT_W*` id), `pedwarn` (standard-mandated), `sorry` (valid but unimplemented), or `inform` (a note on a prior diagnostic), each with a `location_t`; the `input_location` globals are deprecated.
- Quote with format specifiers: `%qD` decl, `%q+D` decl relocated to its `DECL_SOURCE_LOCATION`, `%qT` type, `%qE` expression, `%qs` string, `%<...%>` literal, `%m` for `errno`.
- `error ("Cannot convert '%s'.", s);` -> `error_at (loc, "cannot convert %qs", s);`

Commits:
- Write the subject as `component: summary [PRnnnnn]`, 75 characters or fewer.
- Generate the ChangeLog body with `contrib/mklog.py`; verify with `git gcc-verify`.
- Submit patches to `gcc-patches@gcc.gnu.org` via `git send-email`; GCC takes no GitHub pull requests.

## 3. GCC culture and idioms

Write code that reads as native GCC. This matters beyond style: GCC bootstraps with `-Werror` and `gcc/system.h` poisons common libc calls, so non-idiomatic code often fails to build, not merely fails review. Each rule below pairs a `wrong -> right` fix.

Memory and poisoned identifiers:
- `system.h` poisons `malloc`, `calloc`, `realloc`, `strdup`, `strndup`, `rindex`, `strerror`, `bcopy`, `bzero`, and `bcmp`; any textual use is a compile error. `free`, `abort`, `exit`, and `index` are not poisoned.
- Allocate with `XNEW (T)`, `XNEWVEC (T, n)`, `XCNEW (T)`, `xstrdup`, or `xrealloc`; free with `XDELETE` or `XDELETEVEC`. These abort on out-of-memory, so skip NULL checks.
- Assert invariants with `gcc_assert`; mark dead paths with `gcc_unreachable`; raise an internal error with `internal_error`. Gate a runtime check on `flag_checking` and a compile-time one on `CHECKING_P`; `ENABLE_CHECKING` is poisoned.
  - `p = malloc (n * sizeof (*p));` -> `p = XNEWVEC (elem_t, n);`
  - `if (bad) abort ();` -> `gcc_assert (!bad);`

Containers and garbage collection:
- Prefer the RAII wrappers `auto_vec<T>` and `auto_bitmap` over manual `create`/`release`, so an early return cannot leak.
- Store GC-managed data in `vec<T, va_gc> *` with a `GTY(())` marker and grow it with `vec_safe_push`; the standard library cannot hold GC data, because gengtype cannot trace it.
  - `vec<tree> v; v.create (n); ... v.release ();` -> `auto_vec<tree> v (n);`
  - `std::vector<tree> *cache;` in a GC struct -> `vec<tree, va_gc> *cache;` with a `GTY` marker

Type-safe IR casts (`is-a.h`):
- Move a base pointer to a subclass with `dyn_cast <gassign *> (stmt)` (NULL when it does not match), `as_a <gcall *> (stmt)` (when the code is already known), or test with `is_a <gphi *> (stmt)`; the same family covers `rtx_insn` subclasses. A C cast is banned and skips the checking assert.
  - `gassign *a = (gassign *) stmt;` -> `if (gassign *a = dyn_cast <gassign *> (stmt))`

Simplifications and tree building:
- Put algebraic and constant simplifications in `gcc/match.pd` as `(simplify (pattern) (result))`, not open-coded in a pass, so GIMPLE and GENERIC folding share one rule.
- Build constants and conversions with `build_int_cst`, `build_zero_cst`, `fold_build2`, and `fold_convert`; never assemble an `INTEGER_CST` by hand.
  - an open-coded constant fold in a pass -> a `(simplify ...)` rule in `match.pd`

Control-flow idioms:
- Switch on `TREE_CODE` or `gimple_code`, handle the real cases, and put `gcc_unreachable ()` in an impossible `default`; mark intended fallthrough with `gcc_fallthrough ();`, so `-Wimplicit-fallthrough` stays clean.
  - `default: gcc_assert (0);` -> `default: gcc_unreachable ();`

Dump discipline:
- Guard pass output with `if (dump_enabled_p ())` then `dump_printf_loc (MSG_NOTE, loc, ...)`, or with `if (dump_file && (dump_flags & TDF_DETAILS))`; the pass `name` field is the `-fdump-tree-<name>` suffix that surfaces the output.
  - `printf ("folded\n");` -> `if (dump_enabled_p ()) dump_printf_loc (MSG_NOTE, gimple_location (stmt), "folded\n");`

Include order:
- Start every `gcc/*.cc` with `config.h`, then `system.h`, then `coretypes.h`, before any other header, because `system.h` installs the poison and wraps libc; a target `*.cc` includes `target-def.h` last.
  - `#include "tree.h"` first -> `config.h`, `system.h`, `coretypes.h` first

Reuse and types:
- Search `tree.h`, `gimple.h`, `fold-const.h`, and `tree-ssa*.h` for an existing predicate or builder before writing one; the tree is dense with helpers.
  - a hand-rolled "is this constant zero" test -> `integer_zerop (t)`
- Size and offset IR with `HOST_WIDE_INT` or `poly_int64`, not bare `int`; reach IR fields only through checked accessors (`TREE_OPERAND`, `gimple_op`, `XEXP`); guard bad input with `error_operand_p (t)`.

Diagnostics idioms live in section 2.

## 4. Core APIs

### 4.1 Tree (GENERIC)

`tree` is the universal node handle; read its fields only through macros.
- Identify: `TREE_CODE (t)`; type: `TREE_TYPE (t)`; operand: `TREE_OPERAND (t, i)`; list link: `TREE_CHAIN (t)`.
- Get a decl's name string: `IDENTIFIER_POINTER (DECL_NAME (decl))`.
- Build: `build_int_cst (type, v)`, `build_decl (loc, code, name, type)`, `build2 (PLUS_EXPR, type, a, b)`, `build_call_expr (fndecl, n, ...)`, `get_identifier ("x")`.
- Test kinds with `DECL_P`, `TYPE_P`, `VAR_P`; test for a propagated error by comparing against `error_mark_node`.
- Inspect at a breakpoint: `debug_tree (t)`.

### 4.2 GIMPLE

Three-address IR; each statement is a typed tuple.
- Kind: `gimple_code (g)`. Assign parts: `gimple_assign_lhs/rhs1/rhs2 (g)`, `gimple_assign_rhs_code (g)`. Call parts: `gimple_call_fndecl (g)`, `gimple_call_arg (g, i)`.
- Build: `gimple_build_assign (lhs, PLUS_EXPR, a, b)`, `gimple_build_call (fndecl, n, ...)`, `gimple_build_cond (NE_EXPR, a, b, tlab, flab)`.
- Recompute operand caches after editing: `update_stmt (g)`.

Walk and edit statements in a block:

```
gimple_stmt_iterator gsi;
for (gsi = gsi_start_bb (bb); !gsi_end_p (gsi); gsi_next (&gsi))
  {
    gimple *stmt = gsi_stmt (gsi);
    if (gimple_code (stmt) == GIMPLE_ASSIGN)
      { /* inspect or rewrite */ }
  }
gsi_insert_before (&gsi, new_stmt, GSI_SAME_STMT);
gsi_remove (&gsi, true);   /* true releases the defined SSA names */
```

### 4.3 RTL

Low-level, target-facing IR.
- Read: `GET_CODE (x)`, `GET_MODE (x)`, `XEXP (x, n)`.
- Build: `gen_rtx_REG (mode, n)`, `gen_reg_rtx (mode)` for a new pseudo, `gen_rtx_MEM (mode, addr)`, `gen_rtx_SET (dst, src)`, `GEN_INT (v)`.
- Emit into the instruction stream: `emit_insn (pattern)`.

### 4.4 SSA

- Defining statement: `SSA_NAME_DEF_STMT (n)`; version number: `SSA_NAME_VERSION (n)`.
- PHIs: `create_phi_node (var, bb)`, `add_phi_arg (phi, def, e, loc)`; iterate them with `gsi_start_phis (bb)`.
- Visit every use of a name: `FOR_EACH_IMM_USE_STMT (stmt, iter, name)`.
- After exposing new defs, return `TODO_update_ssa` from the pass so the updater rebuilds PHIs.

### 4.5 CFG

Defined in `basic-block.h`, shared by GIMPLE and RTL.
- Blocks: `FOR_EACH_BB_FN (bb, cfun)`; ends: `ENTRY_BLOCK_PTR_FOR_FN (cfun)`, `EXIT_BLOCK_PTR_FOR_FN (cfun)`.
- Edges: `FOR_EACH_EDGE (e, ei, bb->succs)`; flags `EDGE_TRUE_VALUE`, `EDGE_FALSE_VALUE`, `EDGE_FALLTHRU`.
- Edit: `make_edge (src, dst, flags)`, `split_block (bb, stmt)`.
- Dominance: `calculate_dominance_info (CDI_DOMINATORS)`, then `get_immediate_dominator` and `dominated_by_p`; release with `free_dominance_info`.

### 4.6 Containers

- `auto_vec<T>` and `vec<T>`: `safe_push` grows, `quick_push` asserts space, plus `pop`, `length`, and `FOR_EACH_VEC_ELT (v, i, elt)`.
- `hash_map<K,V>`: `put (k, v)`, `get (k)` returns NULL when absent. `hash_set<K>`: `add`, `contains`.
- `bitmap` (sparse) and `sbitmap` (dense): `bitmap_set_bit`, `bitmap_bit_p`, iterate `EXECUTE_IF_SET_IN_BITMAP (b, 0, i, bi)`; prefer `auto_bitmap` for automatic cleanup.

### 4.7 Memory

Pick the allocator by lifetime:
- IR that outlives a pass: `ggc_alloc<T> ()`; tag every GC struct and global with `GTY (())` so gengtype emits marking code; collection runs at `ggc_collect`.
- Pass-local temporaries: an obstack, or `object_allocator<T>` for many same-size nodes; release the whole pool when the pass ends.
- Plain heap: `XNEW (T)`, `XNEWVEC (T, n)`, `xmalloc`; these abort on out-of-memory, so skip NULL checks.

### 4.8 Machine modes

- Integer modes: `QImode` 8-bit, `HImode` 16, `SImode` 32, `DImode` 64, `TImode` 128. Float: `SFmode` 32, `DFmode` 64.
- Query: `GET_MODE_SIZE` in bytes, `GET_MODE_BITSIZE` in bits, `SCALAR_INT_MODE_P (m)`.

## 5. Extension recipes

Each recipe lists the files to edit in order, then the pattern.

### 5.1 Add a builtin `__builtin_x`

1. Declare the type signature in `gcc/builtin-types.def` if none fits (`DEF_FUNCTION_TYPE_n`).
2. Register it in `gcc/builtins.def` with `DEF_GCC_BUILTIN` (or `DEF_EXT_LIB_BUILTIN`).
3. Fold or expand: put constant folding in `gcc/match.pd` or `gcc/gimple-fold.cc`; add RTL expansion in `gcc/builtins.cc` only when it emits instructions. Reason: `builtins.cc` is closed to new simplifications, which belong in `match.pd`.

### 5.2 Add an optimization pass

1. Create `gcc/tree-<name>.cc` with the skeleton below.
2. Declare the factory in `gcc/tree-pass.h`: `extern gimple_opt_pass *make_pass_<name> (gcc::context *);`.
3. Insert `NEXT_PASS (pass_<name>);` at the right point in `gcc/passes.def`; its position sets which IR the pass sees.
4. Add `tree-<name>.o` to `OBJS` in `gcc/Makefile.in`, then re-run `configure`.

```
namespace {

const pass_data pass_data_mine =
{
  GIMPLE_PASS, "mine", OPTGROUP_NONE, TV_NONE,
  PROP_cfg | PROP_ssa, 0, 0, 0, 0
};

class pass_mine : public gimple_opt_pass
{
public:
  pass_mine (gcc::context *c)
    : gimple_opt_pass (pass_data_mine, c)
  {}

  bool gate (function *) final override
  {
    return optimize > 0;
  }

  unsigned int execute (function *fun) final override
  {
    basic_block bb;
    FOR_EACH_BB_FN (bb, fun)
      { /* work over each block */ }
    return 0;
  }
};

} // anon namespace

gimple_opt_pass *
make_pass_mine (gcc::context *c)
{
  return new pass_mine (c);
}
```

### 5.3 Add a warning

1. Define the option in `gcc/common.opt` (or `gcc/c-family/c.opt`):

```
Wmy-warning
Common Var(warn_my_warning) Warning
Warn about the specific condition.
```

2. Emit it where detected: `warning_at (loc, OPT_Wmy_warning, "message %qE", expr);`. The `Warning` property generates `OPT_Wmy_warning`.
3. Document it in `gcc/doc/invoke.texi`; add a `dg-warning` test.

### 5.4 Add a command-line option

Add a 3-line stanza to the matching `.opt` file:

```
fmy-opt
Common Var(flag_my_opt) Optimization Init(0)
Enable my optimization.
```

Properties: `Common` or `Target` for scope, `Var(x)` for storage, `Init(n)` for the default, `Optimization` to save and restore per function, `Joined UInteger` for an `=N` argument. Read the value as `flag_my_opt`.

### 5.5 Add an attribute

1. Write a handler in `gcc/c-family/c-attribs.cc` that validates the target node, sets `*no_add_attrs = true` on rejection, and returns `NULL_TREE`.
2. Add a row to `c_common_gnu_attributes[]`: `{ "my_attr", min, max, decl_req, type_req, fn_type_req, false, handle_my_attribute, NULL }`.
3. Query it later with `lookup_attribute ("my_attr", DECL_ATTRIBUTES (decl))`.

### 5.6 Modify an existing pass

- List passes with `-fdump-passes`; map the name to its file (`pass_vrp` lives in `gcc/tree-vrp.cc`).
- Iterate with the section 4.2 pattern; rewrite operands, then `update_stmt`; return `TODO_update_ssa` when you exposed new defs.

## 6. Front end and parsing

The front end lexes and parses source into GENERIC trees, runs semantic analysis, then genericizes and gimplifies into the middle end across language hooks. Most edits here add a diagnostic, a semantic check, or grammar for a new construct.

- Files: `gcc/c/c-parser.cc` (C) and `gcc/cp/parser.cc` (C++) parse; `gcc/c/c-decl.cc` and `gcc/c/c-typeck.cc` do C semantics; `gcc/c-family/` holds rules shared by C and C++; language hooks are declared in `gcc/langhooks.h` and defaulted in `gcc/langhooks-def.h`.
- Structure: the parser is hand-written recursive descent. Look ahead with `c_parser_peek_token`, advance with `c_parser_consume_token`; each grammar nonterminal is a `c_parser_*` function (C++ uses `cp_parser_*` over a `cp_lexer_*` token stream).
- Where a change goes: token or grammar handling in the parser; a semantic check or new warning after parsing in `c-decl.cc` or `c-typeck.cc`; a rule that both C and C++ need in `c-family/`.
- Handoff: the front end builds GENERIC, `c-family/c-gimplify.cc` and `cp/cp-gimplify.cc` lower language constructs, and `gimplify_function_tree` produces GIMPLE. A front end does not include middle-end headers such as `rtl.h` or `expr.h`; those include guards are poisoned under `IN_GCC_FRONTEND`.
- Error recovery: emit one diagnostic, resynchronize to a safe token, and propagate `error_mark_node` rather than aborting, so one mistake does not cascade.

## 7. Back end: expansion, machine descriptions, register allocation

The expander lowers GIMPLE to RTL through optabs keyed by standard pattern names, RTL passes optimize, `recog` selects instructions, IRA then LRA allocate registers, and `final` prints assembly. Target behavior lives in machine descriptions plus target hooks.

- Standard pattern names bridge the middle end to a target: `movM`, `addM3`, `cbranchM4`, where M is a mode such as SI or DI. `optabs.def` lists the optabs; `expr.cc` and `optabs.cc` drive expansion.
- Machine descriptions in `gcc/config/<arch>/<arch>.md` use `define_insn` (recognize and print one instruction), `define_expand` (custom RTL generation that may call `DONE` or `FAIL`), `define_split`, `define_peephole2`, and `define_insn_and_split`. Operands are `match_operand:M N "predicate" "constraint"`, `match_dup`, and `match_operator`; iterate patterns with `define_mode_iterator` and `define_code_iterator`. Custom predicates go in `predicates.md`, constraints in `constraints.md`.

```
(define_insn "addsi3"
  [(set (match_operand:SI 0 "register_operand" "=r")
        (plus:SI (match_operand:SI 1 "register_operand" "r")
                 (match_operand:SI 2 "register_operand" "r")))]
  ""
  "add %0,%1,%2")
```

- Build-time generators turn `.md` into C++: `genrecog` builds `insn-recog.cc`, `genemit` the `gen_*` emitters in `insn-emit.cc`, `genoutput` the templates in `insn-output.cc`, plus `genattrtab`, `genautomata`, and `genpreds`. A named pattern yields `CODE_FOR_<name>` and a `gen_<name> ()` function.
- Target hooks: override defaults through `targetm` in `gcc/config/<arch>/<arch>.cc`, set by `TARGET_*` macros before `struct gcc_target targetm = TARGET_INITIALIZER;`; steer register allocation with constraints plus cost hooks such as `TARGET_RTX_COSTS` and `TARGET_REGISTER_MOVE_COST`.
- Where a change goes: a new instruction is a `define_insn`; a multi-step sequence is a `define_expand`; a target cost tweak is a hook in `<arch>.cc`.

## 8. Testing

Tests use DejaGnu. Place a test by kind:
- `gcc/testsuite/gcc.dg/` for C, `g++.dg/` for C++, `c-c++-common/` for both, `gcc.target/<arch>/` for target-specific.
- `gcc/testsuite/gcc.c-torture/` and `gcc.dg/torture/` run across many `-O` levels; keep these fully portable, with no size or endianness assumptions.

Annotate the test with directives in comments:

```
/* { dg-do compile } */              /* or run, link, assemble */
/* { dg-options "-O2 -fdump-tree-dse1" } */
int f (int *p) { *p = 1; *p = 2; return 0; }
/* { dg-final { scan-tree-dump-not "= 1;" "dse1" } } */
```

- Expect a diagnostic on the triggering line: `/* { dg-error "regex" } */`, or `dg-warning`, or `dg-message`.
- Check codegen: `scan-assembler`, `scan-assembler-not`, `scan-assembler-times N`.
- Check an optimization: enable its dump with `-fdump-tree-<pass>`, then match `scan-tree-dump[-not|-times]` against that pass suffix.

Run from the `gcc` subdirectory of the build tree:

```
make check-gcc RUNTESTFLAGS="dg.exp=mytest.c"        # one file
make check-gcc RUNTESTFLAGS="-v -v dg.exp=mytest.c"  # verbose; prints the command
```

Read results in `testsuite/gcc/gcc.sum` for status and `gcc.log` for full output. A FAIL where PASS was expected is a regression; investigate every XPASS.

## 9. Build and debug

Set up and build out of tree:

```
./contrib/download_prerequisites        # run once, in the source tree
mkdir build && cd build
../gcc/configure --enable-languages=c,c++ --disable-bootstrap --disable-multilib
make -j$(nproc)
```

- Iterate fastest by running `make` (or `make all-gcc`) from `build/gcc`; this skips the target libraries.
- After editing a `.opt` file, run `make`; the build regenerates `options.h` and `options.cc`.
- After adding a source file, add its `.o` to `OBJS` and re-run `configure` (see the non-negotiable rules).

Debug the compiler:
- Run cc1 under gdb: `gcc file.c -wrapper gdb,--args`.
- Break on `fancy_abort` and `internal_error` to catch an internal compiler error.
- Inspect state: `call debug_tree (t)`, `call debug_gimple_stmt (g)`, `call debug_rtx (x)`.
- Dump IR to files: `-fdump-tree-all`, `-fdump-rtl-all`, `-fdump-ipa-all`; report optimization decisions with `-fopt-info-<group>-<type>`, for example `-fopt-info-vec-missed`.

Before submitting: bootstrap and run the full testsuite on trunk and on your patch, then diff with `contrib/compare_tests`; a clean bootstrap plus zero new failures is the bar. Reason: the three-stage bootstrap proves the compiler compiles itself identically, catching miscompiles a single-stage build hides.

## 10. File index

| Concept | Files |
|---|---|
| Tree nodes | `tree.h`, `tree.def`, `tree.cc` |
| GIMPLE | `gimple.h`, `gimple.def`, `gimple.cc`, `gimple-iterator.h` |
| RTL | `rtl.h`, `rtl.def`, `emit-rtl.cc` |
| CFG and SSA | `basic-block.h`, `tree-cfg.cc`, `tree-into-ssa.cc` |
| Pass manager | `passes.def`, `passes.cc`, `tree-pass.h` |
| Builtins | `builtins.def`, `builtins.cc`, `match.pd`, `gimple-fold.cc` |
| Options | `common.opt`, `c-family/c.opt`, `opts.cc` |
| Attributes | `c-family/c-attribs.cc`, `attribs.cc` |
| Front end | `c/c-parser.cc`, `cp/parser.cc`, `c-family/`, `langhooks.h` |
| Diagnostics | `diagnostic-core.h`, `diagnostic.cc`, `pretty-print.h` |
| Containers and memory | `vec.h`, `hash-map.h`, `bitmap.h`, `ggc.h`, `alloc-pool.h` |
| Idiom headers | `system.h`, `is-a.h`, `dumpfile.h` |
| Back end and codegen | `optabs.def`, `expr.cc`, `optabs.cc`, `recog.cc`, `ira.cc`, `lra.cc`, `final.cc` |
| Machine descriptions | `config/<arch>/<arch>.md`, `config/<arch>/<arch>.cc`, `target.def` |
| Targets and build | `config.gcc`, `config/<arch>/`, `Makefile.in` |
| Docs | `doc/invoke.texi`, `doc/extend.texi`, `doc/gccint` |

## Binding rules (restated)

- Match GNU style; keep formatting-only changes in their own commit.
- Allocate with `XNEW` and GCC containers, and cast IR with `dyn_cast`; avoid libc allocators, the standard library for GC data, and C casts.
- Put simplifications in `match.pd`, not open-coded in a pass.
- Emit diagnostics through `error_at` and `warning_at` with a real location.
- Add a test for every change; scan a pass dump to prove an optimization fired.
- Build out of tree; register new files in `OBJS` and re-run `configure`.
- Bootstrap and regression-test before submitting to `gcc-patches@gcc.gnu.org`.

*2026-07-24 - Opus 4.8 (Cursor agent). Distilled from web research on GCC architecture, conventions, testing, and workflow.*
