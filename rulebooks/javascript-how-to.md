---
description: Reference for a model writing, reviewing, or cleaning up modern JavaScript - language syntax, modules, async, errors, DOM and platform APIs, Node.js, security, testing, linting, and JSDoc typing
---

<!-- Load this file into context before writing, reviewing, or cleaning up JavaScript. Sections are consulted one at a time; their combined length is never the constraint count. -->

# JavaScript Coding Rulebook

This file equips a model to write, extend, and clean up modern JavaScript (ES2022+). Read the non-negotiable rules and the closing restatement first; they bind every edit. Sections run from most to least frequently needed during cleanup and are consulted one at a time, so the file's length does not collide with the constraint budget. Every rule is chosen to be mechanically detectable with a concrete bad -> good correction. Rules that change runtime behavior are marked as suggestions, not silent auto-fixes.

![The JavaScript Workshop](images/javascript-how-to.png)

## Non-negotiable rules

Follow these on every change; they are restated at the end.

- Use `const` by default, `let` when reassigned, never `var`; a `var` is always a cleanup target.
- Use `===`/`!==`, never `==`/`!=`; the sole sanctioned exception is `x == null` to test for null-or-undefined.
- Throw `Error` objects (or subclasses), never strings or plain values; a thrown string has no stack trace.
- Never leave a floating promise; `await` it, chain `.catch()`, or mark deliberate fire-and-forget with `void fn().catch(...)`.
- Never assign untrusted data to `innerHTML`, `eval`, or `new Function`; use `textContent` or sanitize with DOMPurify. (safety)
- Use ESM (`import`/`export`) for new code, with explicit file extensions and the `node:` prefix for built-ins.

## 1. Variables, equality, and coercion

### 1.1 `const`/`let`, never `var`

`const`/`let` are block-scoped; `var` is function-scoped, hoisted with an `undefined` initializer, and produces loop-closure bugs. Rewrite every `var` to `let`, then downgrade to `const` where never reassigned. See [MDN: let](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/let).

```js
// bad
var total = 0;
for (var i = 0; i < items.length; i++) { /* i leaks; closures share one i */ }
// good
let total = 0;
for (let i = 0; i < items.length; i++) { /* fresh binding per iteration */ }
```

### 1.2 Strict equality

`==` runs the [abstract equality algorithm](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Equality) and produces traps: `0 == ''`, `[] == ![]`, `null == undefined` all true; `NaN == NaN` false. Use `===`/`!==`. The one sanctioned exception is `x == null`, which is true for exactly `null` and `undefined` (matches ESLint [`eqeqeq`](https://eslint.org/docs/latest/rules/eqeqeq) smart mode).

```js
// bad
if (x == 5) { }
// good
if (x === 5) { }
// sanctioned exception - tests null OR undefined
if (value == null) return fallback;
```

For NaN-aware or signed-zero comparison use [`Object.is`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/is) or `Number.isNaN`, never `x === NaN` (always false).

### 1.3 Explicit coercion and truthiness

Make conversions explicit; `'5' + 1` is `'51'` but `'5' - 1` is `4`. The falsy values are exactly `false`, `0`, `-0`, `0n`, `''`, `null`, `undefined`, `NaN` - everything else, including `[]` and `{}`, is truthy. See [MDN: Type coercion](https://developer.mozilla.org/en-US/docs/Glossary/Type_coercion).

```js
// bad - '5' + count concatenates; if (arr) never detects empty
const total = '5' + count;
if (list) process(list);          // [] is truthy
// good
const total = Number('5') + count;
if (list.length > 0) process(list);
```

### 1.4 Nullish coalescing over `||` for defaults

`||` returns the right side for any falsy left side, discarding valid `0`/`''`/`false`. `??` triggers only on `null`/`undefined`. See [MDN: Nullish coalescing](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing).

```js
// bad - a volume of 0 becomes 1
const volume = settings.volume || 1;
// good
const volume = settings.volume ?? 1;
```

`??` cannot be mixed with `||`/`&&` without parentheses (`SyntaxError`): write `(a ?? b) || c`.

### Corrections

- `var x = 1` -> `const x = 1` / `let x = 1` - never `var`.
- `x == 5` -> `x === 5` - strict equality.
- `result === NaN` -> `Number.isNaN(result)` - NaN is never `===` itself.
- `+userInput` / `'5' + n` -> `Number(userInput)` - explicit coercion.
- `if (count) render()` -> `if (count != null) render()` - avoid the `0` falsy trap. *
- `config.port || 8080` -> `config.port ?? 8080` - preserve `0`/`''`/`false`. *

## 2. Modern syntax and APIs

### 2.1 Optional chaining and logical assignment

Collapse existing existence-guard chains with `?.`, and default-assignment idioms with `??=`/`||=`/`&&=`. See [MDN: Optional chaining](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining) and [V8: Logical assignment](https://v8.dev/features/logical-assignment).

```js
// bad
const city = user && user.address && user.address.city;
if (opts.timeout == null) opts.timeout = 3000;
// good
const city = user?.address?.city;
opts.timeout ??= 3000;
```

Only collapse chains that already have guards; do not rewrite `a.b.c` to `a?.b?.c` blindly - that masks real bugs.

### 2.2 Private class members and fields

Use `#name` for true language-enforced privacy and field declarations instead of constructor assignment plus `_name` convention. See [V8: Class fields](https://v8.dev/features/class-fields). This is behavior-changing; surface as a suggestion.

```js
// bad
class Counter { constructor() { this._count = 0; } _tick() { this._count++; } }
// good
class Counter { #count = 0; #tick() { this.#count++; } get value() { return this.#count; } }
```

### 2.3 Deep clone, destructuring, and array/object helpers

- Use [`structuredClone(x)`](https://developer.mozilla.org/en-US/docs/Web/API/Window/structuredClone) over `JSON.parse(JSON.stringify(x))`, which drops `undefined`/functions, mangles `Date`/`Map`/`Set`, and throws on cycles. (Cannot clone functions or DOM nodes; does not preserve class prototypes.)
- Use [`Object.hasOwn(obj, k)`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/hasOwn) over `obj.hasOwnProperty(k)`.
- Use `arr.at(-1)` over `arr[arr.length - 1]`, `arr.findLast(fn)` over `[...arr].reverse().find(fn)`, `nested.flat()` over `[].concat(...nested)`.
- Use non-mutating [`toSorted`/`toReversed`/`with`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/toSorted) (ES2023) when the original must not change: `data.sort()` mutates in place.
- Use `for...of` over `for...in` on arrays (`for...in` yields string keys and inherited props).
- Use rest parameters `(...args)` over the array-like `arguments` object.

### Corrections

- `a && a.b && a.b.c` -> `a?.b?.c` - collapse existing guard chains only.
- `cache[k] = cache[k] || f()` -> `cache[k] ||= f()` - short-circuits assignment.
- `JSON.parse(JSON.stringify(x))` -> `structuredClone(x)` - handles cycles, Map/Set/Date. *
- `obj.hasOwnProperty(k)` -> `Object.hasOwn(obj, k)`.
- `arr[arr.length - 1]` -> `arr.at(-1)`.
- `data.sort(cmp)` (unintended mutation) -> `data.toSorted(cmp)`. *
- `Array.prototype.slice.call(arguments)` -> `(...args)` rest parameters.
- `for (const i in arr)` -> `for (const item of arr)`. *

## 3. Modules and project configuration

### 3.1 ESM by default

Use `import`/`export`, not `require`/`module.exports`, for new code. ESM enables static analysis, tree-shaking, and top-level `await`. A file loaded as ESM has no `require`, `module.exports`, `__dirname`, or `__filename`. See [MDN: JavaScript modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules).

### 3.2 Explicit extensions, `node:` prefix, no directory imports

- ESM relative imports must include the file extension: `import './math.js'`, not `'./math'` (throws `ERR_MODULE_NOT_FOUND`).
- No implicit directory imports: point at `'./util/index.js'` explicitly.
- Prefix built-ins with `node:`: `import fs from 'node:fs'` - unambiguous, cannot be shadowed by an npm package.

### 3.3 package.json

- Declare `"type": "module"` so `.js` is ESM. Use `.cjs`/`.mjs` to force a format.
- Prefer the [`"exports"`](https://nodejs.org/api/packages.html) field over bare `"main"`; it defines explicit entry points and encapsulates internals.
- Order conditional export keys most-specific to least, ending with `"default"`; the first match wins, so a misplaced `"default"` shadows the rest.

### 3.4 Named exports and no barrel files

- Prefer named exports over a large `export default { ... }` object, which forces bundlers to keep the whole object. See [webpack: Tree Shaking](https://webpack.js.org/guides/tree-shaking/).
- Avoid wildcard barrel files (`export * from './x'`) in application code; they force the bundler to traverse the entire aggregation chain and defeat tree-shaking. Use named re-exports or direct imports.
- Declare [`"sideEffects": false`](https://webpack.js.org/guides/tree-shaking/) (or list exceptions like `["*.css"]`) to let bundlers drop unused pure modules.
- Detect and remove circular dependencies with `madge --circular` or ESLint `import/no-cycle`.

### Corrections

- `const { add } = require('./math.js')` -> `import { add } from './math.js'`.
- `import { add } from './math'` -> `import { add } from './math.js'` - ESM needs the extension.
- `import fs from 'fs'` -> `import fs from 'node:fs'`.
- `export default { formatDate, formatCurrency }` -> named `export function` declarations.
- `export * from './Button.js'` -> `export { Button } from './Button.js'` or direct import.
- `import _ from 'lodash'` -> `import debounce from 'lodash-es/debounce'` - subpath import.
- `{ "main": "index.js" }` -> `{ "type": "module", "exports": { ".": { "import": "./index.mjs", "require": "./index.cjs" } } }`.

## 4. Async and concurrency

### 4.1 Promise hygiene

- Never wrap an existing promise in `new Promise(...)`; return it directly. Reserve the constructor for adapting callback/event APIs, and never make the executor `async` (its thrown error is lost and the outer promise hangs).
- Do not mix `.then()` and `await` in the same function.
- Use [`Promise.withResolvers()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/withResolvers) instead of capturing `resolve`/`reject` in outer variables.

### 4.2 async/await pitfalls

- `await` inside `forEach` does nothing - `forEach` ignores the returned promise. Use `for...of` (sequential) or `Promise.all(items.map(...))` (parallel).
- Run independent awaits in parallel with `Promise.all`, not sequentially.
- Drop `return await p` outside `try` (redundant tick), but keep it inside `try/catch` so the `catch` can observe the rejection.
- No `async` array comparators/predicates (they return a truthy promise, breaking `sort`/`filter`).
- Bound unbounded concurrency: batch or use `p-limit` instead of `Promise.all(hugeArray.map(...))`.

```js
// bad
items.forEach(async (item) => { await processItem(item); });
const a = await fetchA(); const b = await fetchB();   // independent
// good
for (const item of items) await processItem(item);     // sequential
const [a, b] = await Promise.all([fetchA(), fetchB()]); // parallel
```

### 4.3 Combinators

| Combinator | Fulfills when | Use for |
|------------|---------------|---------|
| `Promise.all` | all fulfill (rejects on first failure) | dependent tasks; bail on first error |
| `Promise.allSettled` | all settle (never rejects) | independent tasks; need every outcome |
| `Promise.race` | first settles (fulfill or reject) | timeouts where a rejection should end it |
| `Promise.any` | first fulfillment | first success wins; tolerate failures |

Use `allSettled` when partial failure is acceptable (`all` discards good results on the first rejection). Use `any` for "first success", not `race` (a fast rejection wins a race).

### 4.4 Cancellation and the event loop

- Replace manual `setTimeout` + `abort()` with [`AbortSignal.timeout(ms)`](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static); compose reasons with `AbortSignal.any([...])`.
- Create a fresh `AbortController` per request - an aborted signal is permanently aborted.
- Distinguish `AbortError` (user cancel) from `TimeoutError`; do not surface a user abort as a real error.
- Use `queueMicrotask(fn)` to defer to the end of the current turn; use `setTimeout(fn, 0)` only when you deliberately want to yield to rendering.

### 4.5 Fire-and-forget and races

- Mark intentional fire-and-forget with `void fn().catch(...)`; never leave a bare floating call (an unhandled rejection crashes modern Node).
- Never swallow with empty `.catch(() => {})`; log at minimum.
- Guard async writes to shared state with a version counter or `AbortController` to avoid last-response-wins races.

### Corrections

- `arr.forEach(async x => { await f(x) })` -> `for (const x of arr) await f(x)` or `await Promise.all(arr.map(f))`.
- `new Promise((res, rej) => p.then(res, rej))` -> `return p`.
- `new Promise(async (res) => {...})` -> a plain `async function`.
- `doThing()` (floating) -> `void doThing().catch(logErr)`.
- `p.catch(() => {})` -> `p.catch(err => logger.warn(err))`.
- `Promise.all(...)` when partial failure is OK -> `Promise.allSettled(...)`. *
- `Promise.race(...)` for first success -> `Promise.any(...)`. *
- `setTimeout(() => c.abort(), ms)` + fetch -> `fetch(url, { signal: AbortSignal.timeout(ms) })`.

## 5. Error handling

- Throw `Error` objects, never strings (only `Error` instances carry a stack). ESLint [`no-throw-literal`](https://eslint.org/docs/latest/rules/no-throw-literal).
- Use custom `Error` subclasses for discriminable errors (`err instanceof DuplicateError`), and set `this.name` in the constructor.
- Preserve context when rethrowing with [`Error.cause`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error/cause): `throw new Error("failed", { cause: e })`. Subclasses must forward `options` to `super(message, options)` or `cause` is dropped.
- Use [`AggregateError`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/AggregateError) for multiple simultaneous failures instead of throwing only the first.
- Put cleanup in `finally`, never duplicated across success and catch paths; never `return`/`throw` from `finally` (ESLint `no-unsafe-finally`).
- Do not assume the caught value is an `Error`: guard with `e instanceof Error ? e.message : String(e)`.

```js
// bad
throw "user not found";
catch (e) { throw new Error("save failed"); }   // original error dropped
// good
throw new Error("user not found");
catch (e) { throw new Error("save failed", { cause: e }); }
```

### Corrections

- `throw "not found"` -> `throw new Error("not found")`.
- `err.message.includes("dup")` branching -> `err instanceof DuplicateError`.
- subclass with no `this.name` -> assign `this.name = "MyError"`.
- `catch (e) { throw new Error("failed") }` -> `throw new Error("failed", { cause: e })`.
- subclass `super(message)` -> `super(message, options)`.
- `throw errors[0]` -> `throw new AggregateError(errors, "...")`.
- `catch (e) { log(e.message) }` -> `e instanceof Error ? e.message : String(e)`.

## 6. DOM and events

- Prefer `querySelector`/`querySelectorAll` over `getElementById`/`getElementsBy*`; the latter return live `HTMLCollection`s that mutate mid-iteration. `querySelectorAll` returns a static `NodeList` - spread it (`[...nodes]`) before using array methods.
- Use `textContent` over `innerHTML` for plain text (XSS). (safety)
- Manage classes with `classList.add/remove/toggle`, not `className` string surgery.
- Use `element.dataset.userId` over `getAttribute('data-user-id')`.
- Use `e.target.closest(selector)` over manual `parentNode` walks.
- Use `addEventListener`, never inline `on*` attributes or `el.onclick =` (single-handler, CSP-blocked).
- Prefer event delegation (one listener on a stable parent + `closest()`) over one listener per item.
- Pass `{ passive: true }` for `scroll`/`touch`/`wheel` listeners to avoid scroll jank.
- Pass `{ signal }` from an `AbortController` for grouped listener teardown, and `{ once: true }` for one-shot listeners.

### Corrections

- `getElementById('x')` -> `querySelector('#x')`.
- `qsa('.x').map(...)` -> `[...qsa('.x')].map(...)`.
- `el.innerHTML = userText` -> `el.textContent = userText`. (safety)
- `el.className += ' active'` -> `el.classList.add('active')`.
- `el.getAttribute('data-user-id')` -> `el.dataset.userId`.
- `<button onclick="...">` / `el.onclick = fn` -> `el.addEventListener('click', fn)`.
- paired `add`/`removeEventListener` bookkeeping -> `{ signal }` + `controller.abort()`.

## 7. Observers and scheduling

- Replace `scroll` + `getBoundingClientRect()` visibility checks with [`IntersectionObserver`](https://developer.mozilla.org/en-US/docs/Web/API/IntersectionObserver) (lazy load, infinite scroll, impressions); `unobserve()` once handled.
- Replace `window.resize` + manual measurement with `ResizeObserver`; defer DOM writes to `requestAnimationFrame` to avoid the "ResizeObserver loop" error.
- Replace `setInterval` DOM polling with `MutationObserver`.
- Use `requestAnimationFrame` over `setTimeout`/`setInterval` for animation (vsync-aligned, auto-pauses in background tabs). Use `requestIdleCallback` for non-urgent background work.

### Corrections

- scroll + `getBoundingClientRect()` -> `IntersectionObserver` (+ `unobserve`).
- `window.resize` + manual measure -> `ResizeObserver`.
- `setInterval` DOM polling -> `MutationObserver`.
- `setInterval(anim, 16)` -> `requestAnimationFrame(step)`.

## 8. fetch

- Prefer `fetch` over `XMLHttpRequest`.
- `fetch` does NOT reject on 4xx/5xx - it only rejects on network failure. Check `response.ok` and throw yourself before parsing. This is the single most common fetch bug.
- Attach a timeout with `{ signal: AbortSignal.timeout(ms) }`; untimed fetches leak and cause races.
- Bodies are single-use `ReadableStream`s; call `res.clone()` before the first read if two consumers need it.

```js
// bad
const res = await fetch(url);
const data = await res.json();     // parses error pages as success
// good
const res = await fetch(url, { signal: AbortSignal.timeout(10_000) });
if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);
const data = await res.json();
```

### Corrections

- `new XMLHttpRequest()` -> `fetch()`.
- `await fetch(u); await res.json()` with no check -> check `if (!res.ok) throw ...` first.
- untimed `fetch(url)` -> `fetch(url, { signal: AbortSignal.timeout(ms) })`.
- reading a body twice -> `res.clone()` before the first read.

## 9. Security

- Never assign untrusted data to `innerHTML`/`outerHTML`/`document.write`/`insertAdjacentHTML` - these are DOM XSS sinks. Use `textContent` or safe DOM construction. (safety)
- If HTML is genuinely required, sanitize with a maintained library (`DOMPurify.sanitize(html)`), never a hand-rolled tag stripper. (safety)
- Never use `eval` or `new Function` with dynamic data, and never pass a string to `setTimeout`/`setInterval` (implicit eval). Use `JSON.parse` for data and an allowlist object for dynamic dispatch. (safety)
- Never store secrets or auth tokens in `localStorage` (readable by any script via XSS); use `HttpOnly` cookies. (safety)
- Deploy a Content Security Policy without `unsafe-inline`/`unsafe-eval` as defense in depth.

### Corrections

- `container.innerHTML = apiResponse.html` -> `container.textContent = ...` or `DOMPurify.sanitize(...)`. (safety)
- `eval('(' + jsonText + ')')` -> `JSON.parse(jsonText)`. (safety)
- `new Function('return ' + expr)` -> allowlisted dispatch object. (safety)
- `setTimeout('doThing()', 100)` -> `setTimeout(() => doThing(), 100)`.
- `localStorage.setItem('authToken', t)` -> `HttpOnly` cookie for tokens. (safety)

## 10. Node.js APIs

- Prefix all built-ins with `node:` (`node:fs/promises`, `node:path`, `node:crypto`).
- Prefer `node:fs/promises` with `await` over `*Sync` calls, which block the event loop (reserve sync for startup/CLI scripts).
- Build paths with `path.join`/`path.resolve`, never string concatenation (breaks cross-platform).
- In `child_process`, use `spawn`/`execFile` with an args array, never `exec` with interpolated user input (shell command-injection RCE). Passing an args array with `{ shell: true }` is deprecated (DEP0190). (safety)
- Use `node:crypto` (`randomUUID`, `randomBytes`, `randomInt`) for tokens/ids/salts, never `Math.random()` (predictable). (safety)
- In ESM, replace `__dirname`/`__filename` with `import.meta.dirname`/`import.meta.filename` (Node 20.11+), or derive from `import.meta.url` via `fileURLToPath`.
- `process.env` values are strings or `undefined`; coerce and default (`Number(process.env.PORT) || 3000`).
- Never use the deprecated `new Buffer(...)`; use `Buffer.from(...)` or `Buffer.alloc(n)`. (safety)
- Pipe large files with `stream/promises` `pipeline()` instead of buffering the whole payload.

```js
// bad
exec(`ping ${userHost}`);                          // command injection
const token = Math.random().toString(36).slice(2); // predictable
// good
execFile('ping', ['-c', '4', userHost]);
const token = crypto.randomBytes(32).toString('base64url');
```

### Corrections

- `import x from 'fs'` -> `import x from 'node:fs'`.
- `readFileSync(...)` in an async path -> `await readFile(...)` from `node:fs/promises`.
- `dir + '/' + name` -> `path.join(dir, name)`.
- `exec(\`cmd ${input}\`)` -> `execFile('cmd', [input])`. (safety)
- `Math.random()` for tokens/ids -> `crypto.randomBytes`/`crypto.randomUUID`. (safety)
- `__dirname` in ESM -> `import.meta.dirname`.
- `new Buffer(x)` -> `Buffer.from(x)` / `Buffer.alloc(n)`. (safety)

## 11. Testing

- Prefer Vitest as the default for new projects (Vite-native, ESM/TS out of the box, Jest-compatible API). Use `node:test` for dependency-free libraries; Jest for React Native or large existing Jest suites.
- Structure tests with `describe`/`it` and Arrange-Act-Assert; one behavior per test.
- Reset shared state in `beforeEach`; order-dependent tests are flaky.
- Use `vi.fn()` spies over hand-rolled `let called = false` flags; keep `vi.mock` at module scope (it is hoisted); use `importOriginal` for partial mocks.
- Mock at boundaries (network, filesystem, clock), never the unit under test.
- Use specific matchers: `toBe` (identity) vs `toEqual` (deep); never assert on `JSON.stringify` output.

### Corrections

- `expect(JSON.stringify(a)).toBe(...)` -> `expect(a).toEqual(b)`.
- module-level `let` mutated across tests -> reset in `beforeEach`.
- `let called = false` spy flag -> `vi.fn()` + `toHaveBeenCalled()`.
- `vi.mock` inside `it` expecting hoist -> `vi.mock` at module scope.

## 12. Linting, formatting, and JSDoc typing

### 12.1 ESLint flat config

ESLint v9 makes flat config (`eslint.config.js`) the default; `.eslintrc.*` is deprecated. Start from `js.configs.recommended`, and put `eslint-config-prettier` last so it wins the stylistic overrides.

```js
// eslint.config.js
import js from "@eslint/js";
import eslintConfigPrettier from "eslint-config-prettier/flat";

export default [
  js.configs.recommended,
  {
    languageOptions: { ecmaVersion: 2024, sourceType: "module" },
    rules: {
      "no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      eqeqeq: ["error", "always"],
      "prefer-const": "error",
      "no-var": "error",
      "no-throw-literal": "error",
    },
  },
  eslintConfigPrettier, // MUST be last
];
```

Core correctness rules: `no-unused-vars`, `no-undef`, `eqeqeq`, `no-var`, `prefer-const`, `no-throw-literal`, `no-unsafe-finally`, `no-debugger`.

### 12.2 Prettier and JSDoc

- Prettier formats; ESLint lints. Run them separately and bridge conflicts with `eslint-config-prettier`. Remove stylistic ESLint rules (`indent`, `quotes`, `semi`).
- For type safety in plain JS, add `// @ts-check` (or `checkJs`) and annotate with JSDoc `{Type}` syntax; a missing annotation defaults to `any`.
- Use `@ts-expect-error` (flags stale suppressions) over `@ts-ignore` (silent forever).
- Never commit `debugger;` statements; use `console.table`/`console.dir`/`console.trace` over bare `console.log`, and ship source maps.

### Corrections

- `.eslintrc.json` -> `eslint.config.js` (flat config).
- `eslint-config-prettier` not last -> make it the final array entry.
- `indent`/`quotes` ESLint rules + Prettier -> remove stylistic rules, use Prettier.
- JSDoc types with no `// @ts-check` -> add `// @ts-check` or `checkJs`.
- `// @ts-ignore` -> `// @ts-expect-error` (+ reason).
- committed `debugger;` -> remove (`no-debugger`).

## Binding rules (restated)

- Use `const`/`let`, never `var`.
- Use `===`/`!==`; the only exception is `x == null`.
- Throw `Error` objects, never strings.
- Never leave a floating promise; `await`, `.catch()`, or `void ... .catch()`.
- Never feed untrusted data to `innerHTML`, `eval`, or `new Function`. (safety)
- Use ESM with explicit extensions and the `node:` prefix for built-ins.

*2026-07-30 - Opus 4.8 (Cursor agent). Distilled from web research on modern JavaScript language, modules, async, errors, platform APIs, Node.js, security, testing, and tooling (2024-2026 sources).*
