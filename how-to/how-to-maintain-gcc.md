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
- Add a test for every bug fix and feature (section 5); a change without a test is incomplete, because nothing guards against regression.
- Build out of tree (section 6); in-tree builds are unsupported and fail.
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
- Keep the standard library away from garbage-collected data (section 3.7); gengtype cannot trace it.

Diagnostics:
- Write full sentences, so translation works.
- Call `error_at`/`warning_at`/`inform` with a `location_t`.
- Quote with format specifiers: `%qD` decl, `%qT` type, `%qE` expression, `%qs` string, `%<...%>` literal.

Commits:
- Write the subject as `component: summary [PRnnnnn]`, 75 characters or fewer.
- Generate the ChangeLog body with `contrib/mklog.py`; verify with `git gcc-verify`.
- Submit patches to `gcc-patches@gcc.gnu.org` via `git send-email`; GCC takes no GitHub pull requests.

## 3. Core APIs

### 3.1 Tree (GENERIC)

`tree` is the universal node handle; read its fields only through macros.
- Identify: `TREE_CODE (t)`; type: `TREE_TYPE (t)`; operand: `TREE_OPERAND (t, i)`; list link: `TREE_CHAIN (t)`.
- Get a decl's name string: `IDENTIFIER_POINTER (DECL_NAME (decl))`.
- Build: `build_int_cst (type, v)`, `build_decl (loc, code, name, type)`, `build2 (PLUS_EXPR, type, a, b)`, `build_call_expr (fndecl, n, ...)`, `get_identifier ("x")`.
- Test kinds with `DECL_P`, `TYPE_P`, `VAR_P`; test for a propagated error by comparing against `error_mark_node`.
- Inspect at a breakpoint: `debug_tree (t)`.

### 3.2 GIMPLE

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

### 3.3 RTL

Low-level, target-facing IR.
- Read: `GET_CODE (x)`, `GET_MODE (x)`, `XEXP (x, n)`.
- Build: `gen_rtx_REG (mode, n)`, `gen_reg_rtx (mode)` for a new pseudo, `gen_rtx_MEM (mode, addr)`, `gen_rtx_SET (dst, src)`, `GEN_INT (v)`.
- Emit into the instruction stream: `emit_insn (pattern)`.

### 3.4 SSA

- Defining statement: `SSA_NAME_DEF_STMT (n)`; version number: `SSA_NAME_VERSION (n)`.
- PHIs: `create_phi_node (var, bb)`, `add_phi_arg (phi, def, e, loc)`; iterate them with `gsi_start_phis (bb)`.
- Visit every use of a name: `FOR_EACH_IMM_USE_STMT (stmt, iter, name)`.
- After exposing new defs, return `TODO_update_ssa` from the pass so the updater rebuilds PHIs.

### 3.5 CFG

Defined in `basic-block.h`, shared by GIMPLE and RTL.
- Blocks: `FOR_EACH_BB_FN (bb, cfun)`; ends: `ENTRY_BLOCK_PTR_FOR_FN (cfun)`, `EXIT_BLOCK_PTR_FOR_FN (cfun)`.
- Edges: `FOR_EACH_EDGE (e, ei, bb->succs)`; flags `EDGE_TRUE_VALUE`, `EDGE_FALSE_VALUE`, `EDGE_FALLTHRU`.
- Edit: `make_edge (src, dst, flags)`, `split_block (bb, stmt)`.
- Dominance: `calculate_dominance_info (CDI_DOMINATORS)`, then `get_immediate_dominator` and `dominated_by_p`; release with `free_dominance_info`.

### 3.6 Containers

- `auto_vec<T>` and `vec<T>`: `safe_push` grows, `quick_push` asserts space, plus `pop`, `length`, and `FOR_EACH_VEC_ELT (v, i, elt)`.
- `hash_map<K,V>`: `put (k, v)`, `get (k)` returns NULL when absent. `hash_set<K>`: `add`, `contains`.
- `bitmap` (sparse) and `sbitmap` (dense): `bitmap_set_bit`, `bitmap_bit_p`, iterate `EXECUTE_IF_SET_IN_BITMAP (b, 0, i, bi)`; prefer `auto_bitmap` for automatic cleanup.

### 3.7 Memory

Pick the allocator by lifetime:
- IR that outlives a pass: `ggc_alloc<T> ()`; tag every GC struct and global with `GTY (())` so gengtype emits marking code; collection runs at `ggc_collect`.
- Pass-local temporaries: an obstack, or `object_allocator<T>` for many same-size nodes; release the whole pool when the pass ends.
- Plain heap: `XNEW (T)`, `XNEWVEC (T, n)`, `xmalloc`; these abort on out-of-memory, so skip NULL checks.

### 3.8 Machine modes

- Integer modes: `QImode` 8-bit, `HImode` 16, `SImode` 32, `DImode` 64, `TImode` 128. Float: `SFmode` 32, `DFmode` 64.
- Query: `GET_MODE_SIZE` in bytes, `GET_MODE_BITSIZE` in bits, `SCALAR_INT_MODE_P (m)`.

## 4. Extension recipes

Each recipe lists the files to edit in order, then the pattern.

### 4.1 Add a builtin `__builtin_x`

1. Declare the type signature in `gcc/builtin-types.def` if none fits (`DEF_FUNCTION_TYPE_n`).
2. Register it in `gcc/builtins.def` with `DEF_GCC_BUILTIN` (or `DEF_EXT_LIB_BUILTIN`).
3. Fold or expand: put constant folding in `gcc/match.pd` or `gcc/gimple-fold.cc`; add RTL expansion in `gcc/builtins.cc` only when it emits instructions. Reason: `builtins.cc` is closed to new simplifications, which belong in `match.pd`.

### 4.2 Add an optimization pass

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

### 4.3 Add a warning

1. Define the option in `gcc/common.opt` (or `gcc/c-family/c.opt`):

```
Wmy-warning
Common Var(warn_my_warning) Warning
Warn about the specific condition.
```

2. Emit it where detected: `warning_at (loc, OPT_Wmy_warning, "message %qE", expr);`. The `Warning` property generates `OPT_Wmy_warning`.
3. Document it in `gcc/doc/invoke.texi`; add a `dg-warning` test.

### 4.4 Add a command-line option

Add a 3-line stanza to the matching `.opt` file:

```
fmy-opt
Common Var(flag_my_opt) Optimization Init(0)
Enable my optimization.
```

Properties: `Common` or `Target` for scope, `Var(x)` for storage, `Init(n)` for the default, `Optimization` to save and restore per function, `Joined UInteger` for an `=N` argument. Read the value as `flag_my_opt`.

### 4.5 Add an attribute

1. Write a handler in `gcc/c-family/c-attribs.cc` that validates the target node, sets `*no_add_attrs = true` on rejection, and returns `NULL_TREE`.
2. Add a row to `c_common_gnu_attributes[]`: `{ "my_attr", min, max, decl_req, type_req, fn_type_req, false, handle_my_attribute, NULL }`.
3. Query it later with `lookup_attribute ("my_attr", DECL_ATTRIBUTES (decl))`.

### 4.6 Modify an existing pass

- List passes with `-fdump-passes`; map the name to its file (`pass_vrp` lives in `gcc/tree-vrp.cc`).
- Iterate with the section 3.2 pattern; rewrite operands, then `update_stmt`; return `TODO_update_ssa` when you exposed new defs.

## 5. Testing

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

## 6. Build and debug

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

## 7. File index

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
| Diagnostics | `diagnostic-core.h`, `diagnostic.cc`, `pretty-print.h` |
| Containers and memory | `vec.h`, `hash-map.h`, `bitmap.h`, `ggc.h`, `alloc-pool.h` |
| Targets and build | `config.gcc`, `config/<arch>/`, `Makefile.in` |
| Docs | `doc/invoke.texi`, `doc/extend.texi`, `doc/gccint` |

## Binding rules (restated)

- Match GNU style; keep formatting-only changes in their own commit.
- Emit diagnostics through `error_at` and `warning_at` with a real location.
- Add a test for every change; scan a pass dump to prove an optimization fired.
- Build out of tree; register new files in `OBJS` and re-run `configure`.
- Bootstrap and regression-test before submitting to `gcc-patches@gcc.gnu.org`.

*2026-07-24 - Opus 4.8 (Cursor agent). Distilled from web research on GCC architecture, conventions, testing, and workflow.*
