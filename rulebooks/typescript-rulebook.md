---
description: Reference for a model writing, reviewing, or cleaning up TypeScript - configuration, type discipline, imports, errors, async, validation, naming, testing, linting, and publishing
---

<!-- Load this file into context before writing, reviewing, or cleaning up TypeScript. Sections are consulted one at a time; their combined length is never the constraint count. -->

# Rulebook: Writing TypeScript

This file equips a model to write, extend, and maintain TypeScript codebases. Read the non-negotiable rules and the closing restatement first; they bind every edit. Sections run from most to least frequently needed during cleanup and are consulted one at a time, so the file's length does not collide with the constraint budget. Target TypeScript 5.8+ with awareness of 6.0 defaults.

![The TypeScript Workshop](images/typescript-rulebook.png)

## Non-negotiable rules

Follow these on every change; they are restated at the end.

- Enable `strict: true`, `noUncheckedIndexedAccess`, and `verbatimModuleSyntax` in every tsconfig; a project missing any of these is incomplete.
- No `any` in application code; receive external data as `unknown` and validate through a schema library before use.
- No `enum`; use `as const` objects with derived union types.
- No barrel files (`index.ts` re-exports) in application code; reserve them for published library entry points only.
- Use `import type` for type-only imports; `verbatimModuleSyntax` enforces this.
- Write explicit return types on every exported function; internal functions rely on inference.

## 1. Configuration

### tsconfig.json baseline

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "noEmit": true,
    "incremental": true
  },
  "include": ["src"]
}
```

### Required flags

| Flag | Why |
|------|-----|
| `strict: true` | Activates eight core checks; the floor, not the ceiling |
| `noUncheckedIndexedAccess` | Makes `arr[i]` return `T \| undefined`; catches out-of-bounds access |
| `verbatimModuleSyntax` | Forces explicit `import type`; what you write is what gets emitted |
| `isolatedModules` | Ensures compatibility with single-file transpilers (esbuild, SWC) |
| `skipLibCheck` | Biggest single build-speed win; skips checking node_modules .d.ts |
| `forceConsistentCasingInFileNames` | Catches case-sensitive path bugs on case-insensitive file systems |

### Module resolution

- Frontend projects with a bundler: `moduleResolution: "Bundler"`
- Node.js without a bundler: `moduleResolution: "NodeNext"` paired with `module: "NodeNext"`
- Never use `"node"` (alias for `"node10"`) or `"classic"` - both deprecated in TS 6.0

### Path aliases

Configure in tsconfig via `paths`. TypeScript's `paths` only affects type checking - it does not rewrite import paths in emitted code. Sync the same aliases in your bundler separately (Vite: `resolve.tsconfigPaths: true`; webpack: `tsconfig-paths-webpack-plugin`).

Remove `baseUrl` (deprecated in TS 6.0). Prepend its value directly to each `paths` entry:

```diff
  {
    "compilerOptions": {
-     "baseUrl": "./src",
      "paths": {
-       "@app/*": ["app/*"],
+       "@app/*": ["./src/app/*"],
      }
    }
  }
```

### TypeScript 6.0 default changes

| Option | TS 5.x Default | TS 6.0 Default |
|--------|----------------|----------------|
| `strict` | `false` | `true` |
| `module` | `commonjs` | `esnext` |
| `target` | `es3` | `es2025` |
| `moduleResolution` | `node10` | `bundler` |
| `esModuleInterop` | `false` | `true` |
| `types` | All `@types/*` | `[]` (empty) |

### Corrections

- `moduleResolution: "node"` -> `"Bundler"` or `"NodeNext"` - the old value is deprecated and misresolves package.json `exports`.
- `target: "ES5"` -> `"ES2022"` - ES5 emit is deprecated in TS 6.0 and adds unnecessary polyfills.
- Missing `noUncheckedIndexedAccess` -> add it - the flag most teams skip and the one that catches the most bugs.
- `baseUrl: "./src"` -> remove and prepend to `paths` entries - deprecated in TS 6.0.
- `importsNotUsedAsValues` or `preserveValueImports` -> remove and use `verbatimModuleSyntax` - the old flags are superseded.

---

## 2. Type annotations and inference

### Where to annotate

| Position | Annotate? | Reason |
|----------|-----------|--------|
| Exported function return | Yes | Documents intent, catches drift |
| Function parameters | Yes | The contract with callers |
| Public API boundaries | Yes, with `: Type` | Deliberate widening for stability |
| Local variables | No | Trust inference; avoids noise |
| Internal function returns | No | Inference is more precise than you are |
| Callback bodies | No | Contextual typing handles it |

### The `satisfies` / `: Type` / `as` decision

| Goal | Construct | Effect |
|------|-----------|--------|
| Validate without widening | `satisfies T` | Preserves literal types, autocomplete, exhaustiveness |
| Validate and widen | `: T` | Replaces inferred type with stated shape |
| Skip validation (escape hatch) | `as T` | Lies to the compiler; use only post-validation |

- Use `satisfies` for config objects, route tables, lookup maps, feature flags
- Use `: Type` for function parameters and public API return types
- Use `as` only for DOM operations and unavoidable post-validation casts
- Combine: `{ ... } as const satisfies Config` for validated, immutable, narrow structures

### Non-null assertions

Never write `value!.prop` without prior validation. Replace with narrowing:

```typescript
// Bad
const name = user!.name;

// Good
if (!user) throw new Error("user required after auth");
const name = user.name;
```

### Corrections

- `const users: User[] = getUsers()` -> `const users = getUsers()` - over-annotation; inference is already `User[]`.
- `JSON.parse(body) as User` -> `UserSchema.parse(JSON.parse(body))` - `as` on external data provides zero runtime protection.
- `result!.value` -> narrowing check before access - `!` hides a potential crash.
- `data as unknown as Target` -> restructure the types or validate - double assertion is always a design error.
- Missing return type on `export function fetchUsers()` -> add `export function fetchUsers(): Promise<User[]>` - exports need explicit returns.

---

## 3. Enums and constants

### The replacement pattern

Every `enum` becomes an `as const` object with a derived union type:

```typescript
// Before
enum Status {
  Pending = 'pending',
  Active = 'active',
  Closed = 'closed',
}

// After
const Status = {
  Pending: 'pending',
  Active: 'active',
  Closed: 'closed',
} as const;
type Status = typeof Status[keyof typeof Status];
```

### Why

- `enum` emits runtime objects that do not tree-shake
- `const enum` breaks bundlers, is invisible to JavaScript consumers, and fails under `isolatedModules`
- `as const` objects are plain JavaScript, tree-shake perfectly, need no import for the type, and work with `satisfies`

### Simple closed sets

When no runtime object is needed, a bare union suffices:

```typescript
type Direction = 'north' | 'south' | 'east' | 'west';
```

### Constants

- Module-scoped constants: `UPPER_SNAKE_CASE`
- Derive unions from const arrays: `const ROLES = ['admin', 'user', 'guest'] as const; type Role = typeof ROLES[number];`

### Corrections

- `enum Foo { ... }` -> `const Foo = { ... } as const` with derived type - enums are banned.
- `const enum Bar { ... }` -> same replacement - `const enum` breaks bundlers and `isolatedModules`.
- `type Status = 'a' | 'b'` duplicated alongside a runtime object -> single `as const` source of truth.

---

## 4. Imports and modules

### Import discipline

- Type-only imports: `import type { User } from './types'`
- Mixed imports: `import { type User, createUser } from './users'`
- `verbatimModuleSyntax` makes this mandatory - a value import without `type` is preserved in output; a type import without `type` is an error

### Barrel files

- No `index.ts` re-export files inside `src/`
- Barrel files force TypeScript, Jest, and bundlers to process the entire module subtree on any import
- Atlassian measured 75% faster builds after removing them
- Reserve barrel files only for the public entry point of a published package

### Module organization

- One concept per file; split past ~300 lines
- Feature-based grouping (`users/`, `products/`) over type-based (`controllers/`, `services/`)
- Prefer path aliases (`@/utils`) over deep relative paths (`../../../utils`)
- No circular imports - detect with `madge --circular` or `eslint-plugin-import`

### Corrections

- `import { User } from './types'` (where `User` is type-only) -> `import type { User } from './types'` - required by `verbatimModuleSyntax`.
- `export * from './foo'` in application code -> `export { specificThing } from './foo'` - wildcard re-exports defeat tree-shaking and hide dependency edges.
- `src/components/index.ts` re-exporting everything -> remove; import directly from source files.
- `import { something } from '../../../shared/utils'` -> `import { something } from '@/shared/utils'` - path alias is readable and refactor-safe.

---

## 5. Error handling

### The Result pattern

Use discriminated unions for expected failures that callers can recover from:

```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };
```

### When to use Result vs throw

| Situation | Mechanism |
|-----------|-----------|
| Expected business logic failure (not found, validation) | `Result<T, E>` |
| Unrecoverable programmer error (broken invariant) | `throw` |
| API boundary response | Typed error response with status code |

### Typed error unions

Enumerate possible errors for exhaustive handling:

```typescript
type AppError =
  | { code: 'NOT_FOUND'; id: string }
  | { code: 'VALIDATION'; field: string; message: string }
  | { code: 'UNAUTHORIZED' };
```

### Libraries

- `neverthrow` for chainable `Result` with `map`, `andThen`, `ResultAsync`
- `Effect` for full effect system with typed errors, DI, and concurrency

### Corrections

- `throw new Error('not found')` in domain logic -> return `{ ok: false, error: { code: 'NOT_FOUND', id } }` - expected failures belong in the return type.
- `catch (e: any)` -> `catch (e: unknown)` with narrowing - `useUnknownInCatchVariables` enforces this under strict mode.
- Empty `catch {}` -> at minimum `catch (e) { logger.error(e); }` - swallowed errors are invisible bugs.
- `throw` inside a function returning `Promise` without typed error -> return typed Result or define error response shape.

---

## 6. Async patterns

### Mandatory rules

- Every Promise must be awaited or explicitly detached: `void doWork().catch(logger.error)`
- Enable `@typescript-eslint/no-floating-promises` and `no-misused-promises`
- No `async void` functions; always return `Promise<void>`
- No `forEach` with async callbacks - it does not await. Use `for...of` or `Promise.all(items.map(...))`
- No mixing `.then()/.catch()` with `async/await` in the same function

### Promise combinators

| Combinator | Use when |
|------------|----------|
| `Promise.all` | All must succeed; fail-fast on first rejection |
| `Promise.allSettled` | Partial success is acceptable; always resolves |
| `Promise.any` | First success wins (racing mirrors, fallbacks) |
| `Promise.race` | First settlement wins (timeout patterns) |

### Cancellation

- One `AbortController` per logical operation (search, checkout, sync)
- `AbortSignal.timeout(ms)` for deadlines
- `AbortSignal.any([userCancel, timeout, routeChange])` to compose conditions
- Handle `AbortError` as expected control flow, not failure

### Corrections

- `items.forEach(async (item) => { await process(item); })` -> `for (const item of items) { await process(item); }` - forEach does not await.
- `async function handler(): void` -> `async function handler(): Promise<void>` - `async void` hides rejections.
- `fetch(url)` without await or void -> `await fetch(url)` or `void fetch(url).catch(...)` - floating promise.
- `.then(data => { ... }).catch(err => { ... })` inside an async function -> `try { const data = await ...; } catch (err) { ... }` - don't mix styles.

---

## 7. Runtime validation

### The boundary rule

Every trust boundary validates through a schema. TypeScript types are erased at runtime - external data is `unknown` regardless of compile-time annotations.

Trust boundaries:
- API responses (`fetch`, `axios`)
- `JSON.parse` output
- Environment variables (`process.env`)
- User input (forms, query params)
- File reads
- Third-party SDK returns

### Default: Zod v4

```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  role: z.enum(['admin', 'user']),
});

type User = z.infer<typeof UserSchema>;

// At the boundary:
const user = UserSchema.parse(await response.json());
```

### Alternatives

| Library | Use when |
|---------|----------|
| Zod v4 | Default choice; best ecosystem (tRPC, React Hook Form, Vercel AI) |
| Valibot | Bundle-sensitive (edge, Cloudflare Workers); ~1KB shipped |
| ArkType | Best inference; TypeScript expressions as schema |
| TypeBox | JSON Schema native; Fastify/OpenAPI |

### Environment variables

Use a validated config module. Never access `process.env` directly in application code:

```typescript
// env.ts - validated at import time, fails fast at startup
import { createEnv } from '@t3-oss/env-core';
import { z } from 'zod';

export const env = createEnv({
  server: {
    DATABASE_URL: z.string().url(),
    PORT: z.coerce.number().default(3000),
  },
});
```

### Branded types

Brand domain scalars that cross boundaries:

```typescript
declare const Brand: unique symbol;
type Branded<T, K extends string> = T & { readonly [Brand]: K };

type UserId = Branded<string, 'UserId'>;
type OrderId = Branded<string, 'OrderId'>;

function createUserId(raw: string): UserId {
  if (!isValidUuid(raw)) throw new Error('Invalid user ID');
  return raw as UserId;
}
```

### Corrections

- `JSON.parse(body) as User` -> `UserSchema.parse(JSON.parse(body))` - `as` on external data is a lie.
- `const port = process.env.PORT` -> `const port = env.PORT` via validated config - raw env access is `string | undefined` with no coercion.
- `const data: ApiResponse = await res.json()` -> `const data = ApiResponseSchema.parse(await res.json())` - annotation on runtime data is false confidence.

---

## 8. Naming and style

### Casing conventions

| Identifier | Convention | Example |
|------------|------------|---------|
| Variable, function, method | `camelCase` | `getUserData`, `isLoading` |
| Type, interface, class | `PascalCase` | `UserProfile`, `HttpClient` |
| Global constant | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT`, `API_BASE_URL` |
| Generic parameter | `T` or `TEntity` | `T`, `TData`, `TError` |
| File | `kebab-case` | `order-service.ts`, `use-auth.ts` |
| React component file | `PascalCase` | `UserCard.tsx` |

### Naming rules

- No `I` prefix on interfaces - modern TypeScript and IDEs make the distinction unnecessary
- Booleans: `is`, `has`, `should`, `can` prefixes
- Functions: verb-first (`calculate`, `fetch`, `validate`, `create`)
- Event handlers: `on` prefix (`onClick`, `onSubmit`)
- Hooks: `use` prefix (`useAuth`, `useFetch`)
- Types describing function shapes: suffixed with `Fn` or describe the action (`Comparator`, `Predicate`)

### File organization

- One concept per file
- Split files past ~300 lines
- Co-locate types with the code that uses them
- Separate `types.ts` only for types shared across 3+ files in the same feature

### Corrections

- `interface IUser` -> `interface User` - no I-prefix.
- `function data()` -> `function fetchData()` or `function getData()` - functions are verb-first.
- `const process = true` -> `const isProcessing = true` - booleans need their prefix.
- `user-profile.tsx` (React component) -> `UserProfile.tsx` - components use PascalCase filenames.

---

## 9. React patterns

Apply this section only to React/Preact codebases.

### Components

- No `React.FC` - use plain function components with typed props and explicit return type
- No `defaultProps` - use default parameter values in the destructured props
- Generic components use function declarations with trailing comma: `<T,>` in .tsx files

```typescript
// Preferred
function UserCard({ name, role = 'user' }: UserCardProps): React.ReactElement {
  return <div>{name} ({role})</div>;
}

// Generic component
function List<T,>({ items, renderItem }: ListProps<T>): React.ReactElement {
  return <ul>{items.map(renderItem)}</ul>;
}
```

### Props

- Use `ComponentPropsWithoutRef<'button'>` when wrapping HTML elements
- Prefer `React.ReactNode` for children types (explicit, not implicit via FC)
- Use discriminated unions for mutually exclusive props
- Use `satisfies` for context default values

### Corrections

- `const App: React.FC<Props> = (props) => { ... }` -> `function App(props: Props): React.ReactElement { ... }` - FC adds implicit children and complicates generics.
- `Component.defaultProps = { ... }` -> default values in destructuring - defaultProps is deprecated.
- `createContext<T>(undefined as any)` -> `createContext<T>(defaultValue satisfies T)` - no `as any` in context.

---

## 10. Testing

### Type-safe mocks (Vitest)

- Use `vi.fn<[Args], Return>()` with explicit type parameters
- Use `vi.mocked<T>()` to preserve interface contracts
- Use `satisfies` over `as` for test data (validates without widening)
- Mock at module boundaries, not internal functions
- Clean up: `afterEach(() => vi.restoreAllMocks())`

### Type-level testing

Built into Vitest via `expectTypeOf`:

```typescript
import { expectTypeOf } from 'vitest';

expectTypeOf(myFunc).returns.toBeString();
expectTypeOf(result).not.toBeAny();
expectTypeOf(config).toEqualTypeOf<AppConfig>();
```

Use `@ts-expect-error` to test that invalid usage correctly fails:

```typescript
// @ts-expect-error - string not assignable to number
createUser({ age: 'old' });
```

### Corrections

- `const mock = vi.fn() as any` -> `const mock = vi.fn<[string], Promise<User>>()` - typed mocks catch drift.
- `const testUser = { name: 'test' } as User` -> `const testUser = { name: 'test', id: '1', role: 'user' } satisfies User` - satisfies catches missing fields.
- No type assertions in tests -> use `expectTypeOf` for type-level assertions.

---

## 11. Linting

### ESLint configuration (flat config)

```javascript
import js from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  {
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
  }
);
```

### Why `strictTypeChecked` over `recommended`

The `recommended` config is intentionally weak - designed not to annoy beginners. `strictTypeChecked` uses type information to catch floating promises, unsafe returns, and misused thenables that `recommended` silently ignores.

### Non-negotiable rules

| Rule | Catches |
|------|---------|
| `no-floating-promises` | Unhandled async errors |
| `await-thenable` | Awaiting non-promises |
| `no-unsafe-return` | Unsafe `any` propagation |
| `no-explicit-any` | `any` in application code |
| `consistent-type-imports` | Missing `import type` |
| `restrict-template-expressions` | Implicit coercion in templates |
| `switch-exhaustiveness-check` | Missing branches on discriminated unions |

### Corrections

- `.eslintrc.json` -> `eslint.config.js` with flat config - the old format is deprecated.
- `tseslint.configs.recommended` -> `tseslint.configs.strictTypeChecked` - recommended is too weak for production.
- `parserOptions: { project: './tsconfig.json' }` -> `parserOptions: { projectService: true }` - projectService is the modern approach with less config.

---

## 12. Package publishing

Apply this section to npm-published libraries.

### package.json exports

The `types` condition must come first in every conditional block. Resolvers match top-down; if `import` comes before `types`, TypeScript resolves to the `.js` file and all types become `any`.

```json
{
  "name": "my-library",
  "type": "module",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js",
      "require": "./dist/index.cjs"
    }
  }
}
```

### Dual-mode types (ESM + CJS)

```json
{
  "exports": {
    ".": {
      "import": {
        "types": "./dist/index.d.mts",
        "default": "./dist/index.mjs"
      },
      "require": {
        "types": "./dist/index.d.cts",
        "default": "./dist/index.cjs"
      }
    }
  }
}
```

### Declaration generation

- `declaration: true` + `declarationMap: true` to generate .d.ts automatically
- `isolatedDeclarations` (TS 5.5+) for parallel generation by non-TypeScript tools
- Never hand-maintain .d.ts files for your own library code
- Use `emitDeclarationOnly: true` when a bundler handles JavaScript output

### Validation

Run before every publish:
- `publint` - checks package.json correctness
- `attw` (Are The Types Wrong) - checks types resolve correctly for consumers
- `cargo semver-checks` equivalent: compare .d.ts between versions

### Corrections

- `"import": ..., "types": ...` -> `"types": ..., "import": ...` - types must come first or consumers get `any`.
- Missing top-level `"types"` field -> add it - legacy resolvers ignore `exports` and read only the top-level field.
- Hand-maintained `.d.ts` alongside `.ts` source -> delete .d.ts, enable `declaration: true` - generated declarations stay in sync.

---

## 13. Build and performance

### Separation of concerns

- `tsc --noEmit` for type checking (CI, pre-commit hooks)
- esbuild / SWC / Vite for JavaScript output (10-20x faster than tsc emit)
- Both are required; neither replaces the other

### Build speed

| Flag | Impact |
|------|--------|
| `incremental: true` | 70-90% faster rebuilds via .tsbuildinfo |
| `skipLibCheck: true` | Skips checking node_modules .d.ts |
| `composite: true` | Per-package incrementals in monorepos |

Cache `.tsbuildinfo` in CI:

```yaml
- uses: actions/cache@v4
  with:
    path: .tsbuildinfo
    key: tsc-${{ hashFiles('tsconfig.json') }}-${{ hashFiles('src/**') }}
```

### Monorepos

- Every package: `composite: true` in tsconfig
- Root: empty `files: []` with `references` listing all packages
- Build with `tsc -b` (walks dependency graph, rebuilds only what changed)
- `noEmit` does not compose with `composite` - composite projects must emit declarations

### Profiling

```bash
tsc --noEmit --generateTrace ./trace
npx @typescript/analyze-trace ./trace
```

### Performance killers

- Barrel files (force full subtree compilation on every import)
- Deep conditional types in hot paths
- Unscoped `include` (compiling test files during production build)
- Missing `incremental` (full rebuild on every change)

---

## 14. Version-sensitive facts

These change with the toolchain. Verify against the current release before relying on one.

### Recent additions

| Feature | Minimum Version |
|---------|-----------------|
| `verbatimModuleSyntax` | 5.0 |
| `moduleResolution: "Bundler"` | 5.0 |
| `const` type parameters | 5.0 |
| `isolatedDeclarations` | 5.5 |
| `${configDir}` template variable | 5.5 |
| Inferred type predicates | 5.5 |
| `erasableSyntaxOnly` | 5.8 |
| `strict: true` as implicit default | 6.0 |
| `baseUrl` deprecated | 6.0 |

### `erasableSyntaxOnly` (TS 5.8)

Prohibits TypeScript constructs that emit runtime code (`enum`, `namespace` with runtime members, parameter properties). Required when using Node.js native type stripping (`--experimental-strip-types`). Pair with `verbatimModuleSyntax`.

### Inferred type predicates (TS 5.5)

Functions with a single return statement performing a runtime check no longer need explicit `value is Type` annotations - the compiler infers the predicate automatically. Write explicit predicates only when logic is too complex for inference.

---

## Binding rules (restated)

- Enable `strict: true`, `noUncheckedIndexedAccess`, and `verbatimModuleSyntax` in every tsconfig.
- No `any` in application code; validate external data through a schema library.
- No `enum`; use `as const` objects with derived union types.
- No barrel files in application code.
- Use `import type` for type-only imports.
- Write explicit return types on every exported function.

*2026-07-30 - Opus 4.6 (Cursor agent). Distilled from web research on TypeScript configuration, type discipline, tooling, and the ecosystem (2024-2026 sources).*
