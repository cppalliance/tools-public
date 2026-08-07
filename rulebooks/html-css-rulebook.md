---
description: Reference for a model writing, reviewing, or cleaning up HTML and CSS - semantic markup, forms, media, modern layout, custom properties, cascade layers, accessibility, responsive design, performance, and tooling
---

<!-- Load this file into context before writing, reviewing, or cleaning up HTML or CSS. Sections are consulted one at a time; their combined length is never the constraint count. -->

# Rulebook: Writing HTML and CSS

This file equips a model to write, extend, and clean up modern HTML and CSS. Read the non-negotiable rules and the closing restatement first; they bind every edit. Sections run from most to least frequently needed during cleanup and are consulted one at a time, so the file's length does not collide with the constraint budget. Every rule is chosen to be mechanically detectable with a concrete bad -> good correction. Rules that change layout or behavior in ways needing review are flagged as suggestions, not silent auto-fixes.

![The Web Design Atelier](images/html-css-rulebook.png)

## Non-negotiable rules

Follow these on every change; they are restated at the end.

- Use semantic elements (`header`, `nav`, `main`, `article`, `section`, `aside`, `footer`) over `div` soup; reserve `div`/`span` for when no semantic element fits.
- Use one `<h1>` per page, no skipped heading levels, and a single `<main>`.
- Use `<button>` for actions and `<a href>` for navigation; never a `<div>`/`<span>` with `onclick` as a control. (safety)
- Give every `<img>` an `alt` (empty `alt=""` for decorative), every form control an associated `<label>`, and every image `width`/`height` to prevent layout shift.
- Never `outline: none` without a visible `:focus-visible` replacement; body text needs at least 4.5:1 contrast.
- Reach for native HTML before ARIA; the first rule of ARIA is do not use ARIA when a native element exists.

## 1. Document setup

- `<!DOCTYPE html>` as the first line (absence triggers quirks mode).
- `<html lang="en">` - sets language for assistive tech pronunciation and translation.
- `<meta charset="utf-8">` first in `<head>` (guarantees correct decoding of everything after it).
- `<meta name="viewport" content="width=device-width, initial-scale=1">` - required for responsive rendering. Never add `user-scalable=no` or `maximum-scale=1`; disabling zoom fails [WCAG SC 1.4.4](https://www.w3.org/WAI/WCAG21/Understanding/resize-text.html). (safety)
- Unique non-empty `<title>` per page (~50-60 chars) and a `<meta name="description">` (~150-160 chars).

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Account Settings - Acme</title>
  <meta name="description" content="Manage your Acme account preferences and security.">
</head>
```

### Corrections

- missing `<!DOCTYPE html>` -> add it as the first line.
- `<html>` -> `<html lang="en">`.
- `user-scalable=no` / `maximum-scale=1` -> remove; allow pinch-zoom. (safety)

## 2. Semantic HTML

Prefer elements chosen by meaning, not appearance. Semantic markup exposes landmarks and structure to browsers, assistive tech, and search engines. See [web.dev: Semantic HTML](https://web.dev/learn/html/semantic-html).

- `<header>` (banner), `<nav>` (navigation, label with `aria-label` when more than one), `<main>` (once, not nested in another landmark), `<article>` (self-contained), `<section>` (thematic group with a heading), `<aside>` (complementary), `<footer>` (contentinfo).
- One `<h1>` per page; no skipped heading levels (`h2` -> `h4` is a gap); heading level is structure, not size - use CSS for size.
- Use `<div>` (block) or `<span>` (inline) only when no semantic element fits.

```html
<!-- bad -->
<div class="header">...</div>
<div class="nav">...</div>
<div class="main">...</div>
<!-- good -->
<header>...</header>
<nav aria-label="Primary">...</nav>
<main>...</main>
```

### Corrections

- `<div class="header">` / `<div class="nav">` -> `<header>` / `<nav>`.
- `<div class="title" style="font-size:2rem">` -> `<h1>`.
- `<h1>` then `<h4>` (skipped level) -> `<h1>` then `<h2>`.

## 3. Forms

- Associate every control with a `<label>` via `for`/`id` (explicit is best supported). See [W3C WAI: Labeling controls](https://www.w3.org/WAI/tutorials/forms/labels/).
- Placeholder is not a label - it vanishes on input and has low contrast.
- Use specific `input` types (`email`, `tel`, `number`, `date`, `url`, `search`) for better mobile keyboards and native validation.
- Use validation attributes (`required`, `pattern`, `min`/`max`/`step`) and `autocomplete` tokens (`email`, `current-password`, etc.).
- Group related controls with `<fieldset>` + `<legend>` (radio/checkbox sets).
- Always set `type` on `<button>` in forms - the default is `submit`, so an unmarked button submits unexpectedly.
- Set `aria-invalid="true"` and link errors with `aria-describedby` only after validation fails; never signal errors by color alone. (safety)

```html
<!-- bad -->
<input type="text" placeholder="Email">
<form><button>Save</button></form>
<!-- good -->
<label for="email">Email</label>
<input type="email" id="email" name="email" autocomplete="email" required>
<form><button type="submit">Save</button></form>
```

### Corrections

- `<input placeholder="Email">` -> `<label for="email">` + `<input type="email" id="email">`.
- `<button>Save</button>` in a form -> `<button type="submit">Save</button>`.
- error `<p style="color:red">` -> `aria-invalid="true"` + `aria-describedby` pointing to the message. (safety)

## 4. Images and media

- Every `<img>` needs `alt`: descriptive for meaningful images, empty `alt=""` for decorative ones (so assistive tech skips them). Missing `alt` makes screen readers read the filename.
- Set `width` and `height` (intrinsic pixels) on every raster image to prevent Cumulative Layout Shift; CSS still controls rendered size.
- `loading="lazy"` for below-the-fold images only; never lazy-load the LCP/hero image, and never combine `loading="lazy"` with `fetchpriority="high"`.
- Serve AVIF then WebP with a legacy fallback via `<picture>`; order most-efficient first and always set `type`.
- Use `srcset` + `sizes` for resolution switching; `srcset` with `w` descriptors requires `sizes`.
- Add `decoding="async"` to avoid blocking rendering.

```html
<!-- bad -->
<img src="hero.jpg">
<!-- good -->
<picture>
  <source type="image/avif" srcset="hero.avif">
  <source type="image/webp" srcset="hero.webp">
  <img src="hero.jpg" alt="Team at a whiteboard" width="1200" height="630" fetchpriority="high">
</picture>
```

### Corrections

- `<img src="hero.jpg">` -> add `alt`, `width`, `height`.
- decorative `<img alt="decorative divider">` -> `alt=""`.
- hero `<img loading="lazy" fetchpriority="high">` -> drop `loading="lazy"`, keep `fetchpriority="high"`.
- WebP `<source>` before AVIF -> AVIF first, then WebP, with `type` on each.
- `srcset` without `sizes` -> add `sizes`.

## 5. Links, buttons, and tables

- `<a href>` navigates (Enter); `<button>` performs actions (Enter and Space). Match semantics to intent.
- Never a `<div>`/`<span>` with `onclick` as a control - not focusable or keyboard-operable. (safety)
- Links require a valid `href`; `<a>` without one is not focusable.
- Add `rel="noopener"` on `target="_blank"` (prevents reverse tabnabbing) and signal new-tab links to users.
- Tables: `<caption>` first, `<th scope="...">` for headers, `<thead>`/`<tbody>`, never tables for layout.

```html
<!-- bad -->
<div class="btn" onclick="save()">Save</div>
<a href="https://x.com" target="_blank">X</a>
<!-- good -->
<button type="button" onclick="save()">Save</button>
<a href="https://x.com" target="_blank" rel="noopener">X (opens in a new tab)</a>
```

### Corrections

- `<div onclick="save()">` -> `<button type="button">`. (safety)
- `<a href="#" onclick="openMenu()">` -> `<button type="button">`.
- `target="_blank"` without `rel` -> add `rel="noopener"`.
- data `<table>` with bare `<td>` headers -> `<caption>`, `<th scope="col">`, `<thead>`/`<tbody>`.

## 6. Deprecated features and HTML syntax

- Remove obsolete elements (`<center>`, `<font>`, `<big>`, `<tt>`, `<strike>`, `<marquee>`, `<frame>`, `<applet>`) - replace with CSS or semantic elements. See [WHATWG: Obsolete features](https://html.spec.whatwg.org/multipage/obsolete.html).
- Remove presentational attributes (`align`, `bgcolor`, `cellpadding`, `valign`, `border` for style) - use CSS. (`width`/`height` remain valid on `<img>`/`<video>`/`<iframe>`/`<canvas>`.)
- Boolean attributes take no value: `disabled`, not `disabled="true"` (`disabled="false"` is still true; omit to be false).
- Void elements take no end tag (`<br>`, not `</br>`); the trailing slash is allowed but unnecessary in HTML.
- Quote attribute values; lowercase element/attribute names; keep `id` values unique.

### Corrections

- `<center><font size="5">` -> semantic element + CSS.
- `<input checked="false" disabled="true">` -> `<input>` (omit checked) / `<input disabled>`.
- `<table border="1" cellpadding="4" bgcolor="#eee">` -> `<table class="data">` + CSS.

## 7. CSS layout: Flexbox and Grid

Flexbox is one-dimensional (a row or a column); Grid is two-dimensional (rows and columns). Heuristic: Grid for the page scaffold, Flexbox inside components. See [MDN: Grid vs other layout methods](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Relationship_of_grid_layout_with_other_layout_methods).

- Use the `flex` shorthand (`flex: 1`, `flex: 0 0 auto`), not separate longhands; do not set both `flex-basis` and `width`.
- Push one flex item with `margin-inline-start: auto`; guard long content with `min-inline-size: 0`.
- Responsive columns with no media queries: `grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))`.
- Use named areas (`grid-template-areas`) for self-documenting page layouts.
- Use `subgrid` (Baseline Sept 2023) to align nested grids to parent tracks.
- Replace float columns + clearfix with Grid; replace absolute-position centering with `place-items: center` (Grid) or `margin: auto` (Flexbox).

```css
/* bad: float columns + clearfix */
.col { float: left; width: 33.33%; }
.row::after { content: ""; display: table; clear: both; }
/* good */
.row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
```

### Corrections

- `float: left; width: 33.33%` + clearfix -> `display: grid; grid-template-columns: repeat(3, 1fr)`.
- `position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%)` -> `display: grid; place-items: center`.
- `flex-grow: 1; flex-shrink: 1; flex-basis: 0` -> `flex: 1`.
- media-query column stacks -> `repeat(auto-fit, minmax(250px, 1fr))`.

## 8. CSS spacing, sizing, and viewport

- Use `gap` for spacing between flex/grid items, not `margin` on children with `:last-child` exceptions.
- Use `aspect-ratio: 16 / 9` over the `padding-top` percentage hack.
- Use `clamp(MIN, PREFERRED, MAX)` for fluid type and widths; include a `rem` term in the preferred value so zoom still works.
- Use intrinsic sizing (`min-content`, `max-content`, `fit-content`) over arbitrary fixed values.
- Use logical properties (`margin-inline`, `padding-block`, `inset`) over physical for internationalization - but do not convert indiscriminately; keep physical where a value should not flip in RTL. *
- Use `dvh`/`svh`/`lvh` over `vh` on mobile; prefer `min-height: 100svh` with a `100vh` fallback.

```css
/* bad */
.list > * + * { margin-left: 16px; }
.box { position: relative; padding-top: 56.25%; }
h1 { font-size: 5vw; }
.hero { height: 100vh; }
/* good */
.list { display: flex; gap: 16px; }
.box { aspect-ratio: 16 / 9; }
h1 { font-size: clamp(1.75rem, 1rem + 2.5vw, 3rem); }
.hero { min-height: 100vh; min-height: 100svh; }
```

### Corrections

- `margin` spacing hacks with `:last-child` -> `gap`.
- `padding-top: 56.25%` -> `aspect-ratio: 16 / 9`.
- `margin-left: auto; margin-right: auto` -> `margin-inline: auto`. *
- pure `vw` font size -> `clamp()` with a `rem` term.
- `height: 100vh` -> `min-height: 100vh; min-height: 100svh`.

## 9. Modern CSS features

- Use custom properties (`--var` + `var()`) over Sass variables for anything themed, toggled, or read at runtime; always supply a fallback: `var(--gap, 1rem)`.
- Register animated custom properties with `@property` (typed, animatable; `syntax` and `inherits` are required).
- Use `@layer` to manage precedence so selectors stay low-specificity; layer order beats specificity. Import third-party CSS into a low layer.
- Use native CSS nesting (Baseline Dec 2023) over preprocessor nesting; cap depth at ~3 and use `&` explicitly for pseudo-classes.
- Use `:has()` for relational (parent) selection instead of JS class-toggling.
- Use `:where()` (zero specificity) for defaults/resets and `:is()` for grouping when you want the specificity.
- Prefer `oklch()` and `color-mix(in oklab, ...)` over hex/rgb/hsl for perceptually uniform palettes and clean mixing.

```css
:root { --brand: oklch(0.62 0.19 255); }
.btn { background: var(--brand); }
.btn:hover { background: oklch(from var(--brand) calc(l - 0.08) c h); }
:where(ul, ol) { margin: 0; padding: 0; }
.form-field:has(input:invalid) { border-color: oklch(0.6 0.2 25); }
```

### Corrections

- Sass `$brand: #0af` used at runtime -> `:root { --brand: ... }` + `var(--brand)`.
- `var(--space-m)` with no fallback -> `var(--space-m, 1rem)`.
- animated `--angle` string -> register with `@property { syntax: "<angle>"; ... }`.
- `h1 a, h2 a, h3 a` -> `:is(h1, h2, h3) a`.
- `darken(#0af, 10%)` / `rgba(...)` mixing -> `oklch(from ...)` / `color-mix(in oklab, ...)`. *

## 10. CSS specificity and architecture

- Never style by ID; use a class. If an ID must stay in markup, `[id="x"]` has class-level specificity.
- Do not over-qualify (`ul.nav` -> `.nav`) or deep-nest (`.card .body .title` -> `.card__title`); cap descendant depth at ~3.
- Replace `!important` override stacks and specificity hacks (`.btn.btn.btn`) with a cascade layer of overrides. See [web.dev: Specificity](https://web.dev/learn/css/specificity).
- Use a minimal, intentional reset (Josh Comeau / Andy Bell) in a low-priority `@layer reset`, not a legacy mega-reset or normalize.css.
- Prefer native CSS for new work; reach for Sass only for build-time token generation, parametric mixins, or selector-name interpolation.

```css
@layer reset, base, components, utilities;
@layer reset {
  *, *::before, *::after { box-sizing: border-box; }
  * { margin: 0; }
  body { line-height: 1.5; }
  img, picture, video, svg { display: block; max-width: 100%; }
  input, button, textarea, select { font: inherit; }
}
```

### Corrections

- `#submit-btn { ... }` -> `.submit-btn { ... }` (or `[id="submit-btn"]`).
- `ul.nav` / `.header .header-nav` -> `.nav` / `.header-nav`.
- `.alert { color: red !important }` -> put it in a later `@layer`.
- `.btn.btn.btn` specificity hack -> a later cascade layer.
- Eric-Meyer nuclear reset -> minimal reset in `@layer reset`.

## 11. Accessibility

Target [WCAG 2.2 AA](https://www.w3.org/TR/WCAG22/). Semantic HTML (section 2) is the foundation; ARIA is a last resort.

- Contrast: body text at least 4.5:1, large text 3:1, non-text UI (borders, focus rings, icons) 3:1. Ratios are thresholds, not rounded (`#777` = 4.47:1 fails). (safety)
- Never `outline: none` without a replacement; use `:focus-visible` with at least 3:1 indicator contrast.
- Focus order must follow DOM/reading order; provide a "Skip to main content" link.
- Never use positive `tabindex` (`tabindex="1"`); only `0` or `-1`.
- Every interactive element needs an accessible name (visible text > `aria-labelledby` > `aria-label`); icon-only buttons need `aria-label`.
- Do not add `role="button"` to a `<div>` (adds no keyboard behavior); use `<button>`.
- Screen-reader-only text uses a `.visually-hidden` clip utility, never `display:none` (which removes it from the accessibility tree).
- No auto-playing audio/video with sound; provide controls. (safety)

```css
/* bad */
button:focus { outline: none; }
/* good */
button:focus-visible { outline: 3px solid #0066cc; outline-offset: 2px; }
@supports not selector(:focus-visible) {
  button:focus { outline: 3px solid #0066cc; }
}
```

### Corrections

- `outline: none` -> `:focus-visible` styles.
- `<div role="button">` -> `<button type="button">`.
- `<button><svg>...</svg></button>` -> add `aria-label`.
- positive `tabindex` -> `0`/`-1` and fix DOM order.
- `.sr-only { display: none }` -> clip-based `.visually-hidden`.
- `<video autoplay>` -> `<video controls>`. (safety)

## 12. Responsive and preference-aware design

- Write mobile-first: base styles for small screens, enhance up with `min-width` queries.
- Use container queries (`@container`) for component-level responsiveness; reserve media queries for page-level layout.
- Wrap non-essential motion in `@media (prefers-reduced-motion: reduce)`. (safety)
- Respect `prefers-color-scheme`; drive theming through custom properties.
- Make tap targets at least 24x24 CSS px (prefer 44x44 for primary touch controls).

```css
/* good: component owns its responsiveness */
.wrap { container-type: inline-size; }
@container (min-width: 400px) { .card { grid-template-columns: 1fr 2fr; } }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Corrections

- desktop-first `max-width` queries -> mobile-first `min-width`.
- viewport-keyed `@media` for a component -> `@container`.
- animation with no fallback -> wrap in `prefers-reduced-motion`.
- `.icon-button { width: 16px }` -> `min-width: 44px; min-height: 44px`.

## 13. Performance

Core Web Vitals thresholds (75th percentile): LCP <= 2.5s, INP <= 200ms, CLS <= 0.1.

- Set `width`/`height` (or `aspect-ratio`) on all images/video/iframes, and reserve space for injected content (ads, banners) with `min-height` - the top CLS fix.
- Inline critical above-the-fold CSS (<~14KB); load the rest non-blocking with `media="print" onload="this.media='all'"` + `<noscript>` fallback.
- Add `defer` to render-blocking scripts (`async` for independent third-party); module scripts defer automatically (no redundant `defer`).
- Fonts: `font-display: swap` with a metric-adjusted fallback (`size-adjust`); preload critical fonts with `crossorigin`; prefer a system font stack when brand type is not required.
- Use `content-visibility: auto` + `contain-intrinsic-size` for large off-screen sections.
- Animate only `transform`/`opacity` (compositor-safe); do not put `will-change` in static rules for many elements.
- Serve AVIF/WebP responsive images; minify, enable Brotli, and remove unused CSS (PurgeCSS, safelisting dynamic classes).
- Never ship CSS `@import` (serial request chain); use `<link>` tags or bundle at build time.

```html
<!-- bad -->
<script src="/app.js"></script>
<link rel="stylesheet" href="/non-critical.css">
<!-- good -->
<script src="/app.js" defer></script>
<link rel="stylesheet" href="/non-critical.css" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="/non-critical.css"></noscript>
```

### Corrections

- `<img>` without dimensions -> add `width`/`height`.
- `<script src>` (parser-blocking) -> `<script src defer>`.
- `<script type="module" defer>` -> drop redundant `defer`.
- `@font-face` without `font-display` -> add `font-display: swap`.
- font preload without `crossorigin` -> add `crossorigin`.
- `.card { will-change: transform }` (static/broad) -> rely on the browser; animate `transform`.
- `transition: left, width` -> `transition: transform`.
- shipped `@import url(...)` -> `<link rel="stylesheet">`.

## 14. Tooling

- Lint CSS with [Stylelint](https://stylelint.io/) (`--fix` auto-fixes many issues) in the editor and CI.
- Format with Prettier; Stylelint dropped stylistic rules, so pair the two (Prettier formats, Stylelint lints).
- Validate HTML with the [W3C Nu HTML Checker](https://validator.w3.org/nu/) in CI.
- For new work, prefer zero-runtime styling (native CSS + `@layer`, CSS Modules, Tailwind v4, or a zero-runtime CSS-in-JS tool); runtime CSS-in-JS hurts INP and is incompatible with React Server Components.
- Pipeline order: format (Prettier) -> lint (Stylelint) -> purge unused (PurgeCSS) -> minify (cssnano/Lightning CSS).

## Binding rules (restated)

- Use semantic elements over `div` soup.
- One `<h1>`, no skipped heading levels, single `<main>`.
- `<button>` for actions, `<a href>` for navigation; never a `<div>` with `onclick`. (safety)
- Every `<img>` has `alt`, every control has a `<label>`, every image has `width`/`height`.
- Never `outline: none` without a `:focus-visible` replacement; 4.5:1 text contrast.
- Native HTML before ARIA.

*2026-07-30 - Opus 4.8 (Cursor agent). Distilled from web research on modern HTML semantics, CSS layout and features, accessibility (WCAG 2.2), responsive design, performance (Core Web Vitals), and tooling (2024-2026 sources).*
