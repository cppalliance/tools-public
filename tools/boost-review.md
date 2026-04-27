# Boost Library Review

Analyst, diagnostician, student of rejection patterns - the instrument is 34 historical Boost reviews distilled into 11 rejection-driver principles, competitive landscape analysis, and documentation probing. The subject is a C++ library proposed for inclusion in Boost. It explores the repository, profiles the author, searches for competitors, extracts claims, compares positioning, probes rationale, audits documentation against accumulated questions, evaluates each principle with evidence, synthesizes a report, and filters slop. The pipeline produces a single integrated review - a document that tells the reader what matters, what's missing, and what questions only a human can answer.

The pipeline: repository exploration, structure analysis, API surface extraction, author analysis, competitor search, claims extraction, competitor claims, claims comparison, rationale analysis, documentation analysis, principle evaluation, report synthesis, slop filter.

---

## Inputs

- **Repository** (mandatory) - GitHub URL or local path to the candidate library
- **Additional evidence** (optional) - mailing list posts, author writeups, review announcements, design documents. Provided as file paths or URLs.
- **Interactive session** (optional) - the tool can ask the user questions to surface additional context the repo alone doesn't provide

---

## Execution Rules

**All steps run strictly in series.** No parallel subagents. Ever. One subagent at a time - finish it, collect its output, then start the next. This tool is designed to be run multiple times in parallel against different libraries, not to parallelize within a single run.

**Subagent freshness.** Each step spawns a fresh subagent. No subagent carries context from a previous step except what the main context explicitly passes to it. This prevents context pollution and keeps each step focused.

**Main context discipline.** The main context holds only summaries, breadcrumbs, accumulated questions, and the final report. No raw source code enters the main context. No full file contents. Subagents read the repo; the main context reads their compressed output.

**Repo lifecycle.** If the repo is on GitHub, clone it to a temp directory in Step 1. Keep it accessible through Step 10 (documentation analysis is the last step that needs repo access). Delete after Step 10.

---

## Artifact Caching

Cache location: `../.cache/` relative to this tool's directory.

Reports go to `../.reports/{library-slug}-eval.md` relative to this tool's directory.

**Execution protocol.** Write output to a temporary file (`../{library-slug}-eval.tmp.md`). Rename to final path only after the report is complete. On resumption, check for `../.tmp.md` and continue from its tail.

---

## Pipeline

### Step 1: Repository Exploration

**Goal**: Understand what the library does well enough to search for competitors.

A subagent explores the repository:
- Read README, top-level docs, any design/rationale documents
- Look at examples to understand intended usage
- Check for stated motivation, problem description, target audience
- Identify where public headers live (include/ directory, directory structure)
- Identify the author: name, GitHub username, email if visible in README/commits
- Look at the simplest example and characterize it: how many lines? What concepts must a beginner learn?
- If the repo is on GitHub, collect basic metrics: stars, forks, open issues, last commit date, whether recent issues have author responses

**Output passed to main context**:
- **One-line summary**: Brutal, precise (e.g. "A header-only C++ HTTP/WebSocket library built on Boost.Asio")
- **Executive summary**: One paragraph covering what it does, how it works, what problem it solves, who it's for
- **Author**: Full name + GitHub profile URL (if available)
- **Search breadcrumbs**: Keywords, domain terms, competing library names mentioned in docs, standards referenced, problem domain description - enough to drive competitor search
- **Header locations**: List of public header file paths found in the repo (just paths, not content)
- **Simplest example**: Line count and concepts required (e.g. "12 lines, requires understanding `context`, `connection`, and `handler`"). If no examples exist, note that.
- **Repo health** (GitHub only): stars, forks, open/closed issue ratio, last commit date, rough responsiveness signal (issues get replies vs ignored)

### Step 2: Structure Analysis

**Goal**: Characterize the physical structure of the project. Not rendering judgment - just measuring and describing what's there.

A subagent receives:
- The repo path from Step 1

Then it probes the repository to determine:
- **Header-only or linkable?** Are there .cpp/.cc source files that compile into a library, or is everything in headers/inline?
- **Templates vs compiled code**: All templates? A mix? Mostly compiled with some template utilities?
- **Build system**: CMake? B2 (Boost.Build)? Both? Meson? No build system (header-only, just include)?
- **Configuration macros**: `#define` configuration knobs? How many? What do they control?
- **Multiple configurations**: Different build modes, optional components, feature flags?
- **Dependencies**: Boost libraries, std library features, third-party libraries?
- **Test infrastructure**: Tests? What framework (Boost.Test, Catch2, GoogleTest, doctest)?
- **Directory layout**: Standard Boost layout (include/boost/lib/, libs/lib/src/, etc.) or custom?

**Output passed to main context**:
- **Structure summary**: One paragraph describing the physical structure. Example: "Header-only template library with no build step required. Uses CMake and B2 for tests. Depends on Boost.Asio and Boost.Beast. Has 43 public headers organized in include/boost/http/. Tests use Boost.Test. No configuration macros." Or: "Mixed library with both header templates and compiled source (3 .cpp files in src/). Requires linking. Uses CMake only. Provides MYLIB_NO_EXCEPTIONS and MYLIB_STATIC_LINK configuration macros."

### Step 3: API Surface Extraction

**Goal**: Produce a compressed map of the library's public API - types, functions, signatures, patterns. Small enough to inject into later step prompts.

A subagent receives:
- The header locations from Step 1
- The one-line summary from Step 1 (to understand what it's looking at)

Then it reads each public header and extracts:
- Public classes/structs: name, brief purpose, key member functions (name + signature), notable template parameters
- Free functions: name + signature, brief purpose
- Type aliases, enums, constants that are part of the public interface
- Notable patterns: RAII, completion tokens, tag dispatch, CRTP, etc.

After extraction, the subagent categorizes the API into logical groups. Typical categories (use what fits - not every library has all of these):
- Error handling (error codes, result types, exception types)
- Infrastructure (configuration, context/session objects, allocators, executors)
- Core types (the main data types the library provides)
- Algorithms / operations (functions that do the work)
- I/O (reading, writing, networking, file access)
- Customization points (traits, tag types, extension hooks)
- Utilities (helpers, formatters, string operations)

The subagent should be selective - extract what matters for understanding the API design, not every detail. A typical output is 50-150 lines.

**Output passed to main context**:
- **API surface map**: Compressed representation of the public API, organized by header or logical grouping (by header with types and signatures)
- **API groups**: The logical categories the API falls into, with the types/functions that belong to each group. This is the conceptual organization, not the file organization. Example:

```
- **Core types**: `connection`, `request`, `response` - the main objects users interact with
- **I/O operations**: `async_read`, `async_write`, `async_connect` - all async, all use completion tokens
- **Error handling**: `error_code` overloads on every operation, plus `http::error` enum
- **Configuration**: `connection::options` struct with timeouts, buffer sizes, TLS settings
```

- **API cohesion assessment**: 2-3 sentences on whether the API groups form a coherent whole or feel disjointed. Does every public type serve the stated purpose? Are there outliers that don't belong? Is there a clear "simple path" through the API for basic usage?
- **Standout functions** (if any): If one function or type is so significant it defines the library (like `from_chars` defines charconv), note it. Otherwise omit.
- **Exception safety signal**: How many public functions are `noexcept`? Are destructors and move operations `noexcept`? Do any doc comments mention exception safety guarantees (basic, strong, nothrow)? Rough characterization: "all ops are noexcept" / "mixed - core ops throw, utilities are noexcept" / "no noexcept annotations visible" / "docs mention exception safety guarantees for N types".
- **Doc questions**: Breadcrumbs for the documentation analysis step. For each API group and notable pattern, generate a question: "Does the documentation cover {X}?" Examples:
  - "Does the documentation cover the connection lifecycle?"
  - "Does the documentation explain the completion token pattern?"
  - "Is there a getting-started tutorial or quick-start example?"
  - "Does the documentation cover error handling conventions?"
- **Reader questions** (0-2): API design choices where the intent is ambiguous and only a domain expert can judge. Examples:
  - "The API exposes both sync and async versions of every operation. Is the sync API a convenience layer, or does the library genuinely serve both sync and async use cases?"
  - "The `parser` class takes a `std::pmr::memory_resource*` but no other type uses PMR. Is selective PMR support intentional, or incomplete?"
  - Only surface these if they're genuinely ambiguous from the code. If the answer is obvious from context, don't ask.

### Step 4: Author Analysis

**Goal**: Build a profile of the library's author to contextualize the submission.

A subagent receives:
- The author's name and GitHub profile URL from Step 1

Then it does web searches to answer:
- Do they have other open-source libraries? Which ones? How popular?
- Do they have other Boost libraries? Which ones? Status (accepted, in review)?
- Do they speak at C++ conferences? (CppCon, C++Now, ACCU, Meeting C++, etc.)
- Do they participate in C++ standardization (WG21)? Author any papers?
- What is their professional background? Where do they work / have they worked?
- How long have they been involved in the C++ community?
- Do they have a visible reputation? (blog, social media, well-known projects)

The subagent surfaces up to 10 factual sentences about the author, plus a **notability tier**:
- **nobody** - No visible track record in C++ community. Could be a talented newcomer, but no public signal.
- **somebody** - Has some presence: a few libraries, some conference talks, or known in a niche.
- **accomplished** - Well-known in C++ community. Multiple successful libraries, regular conference speaker, WG21 participant, or widely recognized contributions.

**Output passed to main context**:
- **Author name**: Full name
- **Author sentences**: Up to 10 factual sentences about the author
- **Notability tier**: nobody / somebody / accomplished
- **Other Boost libraries** (if any): names and status
- **Domain keywords**: Short phrases describing the author's areas of expertise, derived from their body of work (e.g. "networking", "serialization", "template metaprogramming"). If the author's established domain overlaps with the library's domain, note it explicitly.

This data feeds into:
- `maintainer-responsiveness` and `field-experience` principle evaluations in Step 11
- The "About {Author Name}" section in the report
- Cross-reference author domain keywords with the library's domain from Step 1

### Step 5: Competitor and Domain Search

**Goal**: Understand the competitive landscape and problem domain.

A subagent takes the search breadcrumbs from Step 1 and does web searches (does NOT need repo access):
- Find 3-5 most popular competing libraries (any language if the concept is cross-language, but focus on C++)
- Identify the problem domain and what solutions typically look like
- Note if the space is crowded or novel
- Find any prior art, standards proposals, or academic work in the area
- Search for evidence of adoption of the candidate library itself: blog posts mentioning it, Stack Overflow questions, GitHub "Used by" count, conference talks about it

**Output passed to main context**:
- **Competitors**: 3-5 competing libraries with one-line descriptions and rough popularity indicators
- **Domain summary**: 3-5 sentences on the problem domain, what good solutions look like, and where the field is heading
- **Novelty assessment**: Solving a known problem in a new way? Genuinely novel territory? Crowded space where another entry needs strong justification?
- **Implicit rationale**: 3-5 one-sentence justifications that are obvious given the domain and don't need to be stated by the author. These are the reasons the *problem space* exists, not the reasons *this library* is special. Examples:
  - Unicode library: "International text processing is a universal requirement"
  - JSON parser: "JSON is the dominant data interchange format"
  - These will be used later to avoid penalizing the author for not explaining what's obvious.
- **Doc questions**: For domain-specific concepts that a user would need to understand: "Does the documentation explain {domain concept}?" Examples:
  - "Does the documentation explain what UTF-8 normalization forms are?"
  - "Does the documentation explain thread safety guarantees?"
  - "Does the documentation compare against or position itself relative to alternatives?"
- **Adoption evidence**: Signs the candidate library is used in the wild - blog posts, SO questions, GitHub dependents, conference mentions. If nothing found, say so (that's a data point for `field-experience`).
- **If nothing found** (for competitors): That itself is a finding - the library may be addressing something genuinely new, or it may be solving a problem nobody has.

### Step 6: Claims Extraction

**Goal**: Identify the library's key value proposition - what it claims to offer that matters, especially what distinguishes it from competitors.

A subagent receives:
- The executive summary from Step 1
- The API surface map from Step 3
- The competitor list and domain summary from Step 5

Then it goes back into the repository and digs deeper, now with the competitive context in mind:
- Re-read the README, docs, and design notes looking specifically for claims
- Scan benchmarks, comparison tables, feature matrices
- Look at what the examples emphasize - what does the author think is impressive?
- Read commit messages, changelogs, or blog posts linked from the repo

The subagent must be intelligent about what matters:
- Things the library has in common with all competitors are **footnotes** - not claims
- Things the library claims are **unique, faster, safer, simpler, or more correct** than alternatives - those are the **key claims**
- If the library operates in a novel space with no competitors, the claim is novelty itself

**Output passed to main context**:
- **Key claims**: A numbered list of 3-7 major claims, each one sentence. These are the library's value proposition relative to alternatives.
- **Shared baseline**: One sentence on what it has in common with competitors (the footnote)
- **Author emphasis**: What does the author seem most proud of or focused on? This reveals intent.
- **Unsupported claims**: Any claims made in docs/README that have no visible evidence in the code (no benchmarks backing a speed claim, no tests demonstrating a safety claim, etc.)
- **Reader questions** (0-3): Claims the AI can observe but cannot evaluate. These are claims where the code exists but human judgment is needed. Examples:
  - "The library claims zero-allocation in the hot path. We found no heap allocations in `parser::feed()`, but `session::start()` allocates. Is `session::start()` considered hot-path in your usage?"
  - "Benchmarks exist but compare against libfoo 2.1 (current is 3.0). Are these results still meaningful?"
- **Doc questions**: For each key claim, a question probing whether the documentation substantiates it. Examples:
  - "Does the documentation show benchmark results for the SIMD acceleration claim?"
  - "Does the documentation demonstrate the type-safe API with examples?"

### Step 7: Competitor Claims

**Goal**: Extract the key value propositions of each competitor.

A subagent receives:
- The competitor list from Step 5 (names, one-liners, popularity)
- The domain summary from Step 5

For each competitor (3-5), the subagent does web searches to find:
- What does this competitor claim as its value proposition?
- What are its 2-4 key selling points?
- What are its known weaknesses or limitations?

One brief paragraph per competitor covering their key claims.

**Output passed to main context**:
- **Competitor claims**: For each competitor, 2-4 key value propositions (one sentence each)
- **Competitor weaknesses**: Known limitations or common complaints (one sentence each, if findable)

### Step 8: Claims Comparison

**Goal**: Compare the library's claims against competitor claims, item by item.

A subagent receives:
- The library's key claims from Step 6
- The competitor claims from Step 7

For each of the library's key claims:
- Do any competitors also claim this? If so, who does it better? (1-2 sentences)
- Is this claim unique to the library? If so, note it.
- Is the library missing something that all competitors offer? If so, that's a gap.

For each competitor feature the library doesn't have:
- Is it a significant omission or irrelevant to the library's scope?

**Output passed to main context**:
- **Unique strengths**: Claims the library makes that no competitor matches (1 sentence each + confidence)
- **Contested claims**: Claims where competitors also compete - brief comparison (1-2 sentences each + confidence)
- **Gaps**: Things competitors all offer that the library lacks (1 sentence each)
- **Overall positioning**: 2-3 sentences on where this library sits in the landscape (+ confidence)
- **Reader questions**: Where the comparison requires domain judgment the AI can't provide (e.g. "Competitor X uses a callback-based API while this library uses coroutines - is the coroutine approach an advantage or a drawback for your target users?")
- **Doc questions**: For unique strengths and gaps identified in the comparison. Examples:
  - "Does the documentation explain why the coroutine-based approach is preferable to callbacks?"
  - "Does the documentation acknowledge the lack of async support and explain why?"

### Step 9: Rationale Analysis

**Goal**: Determine whether the library justifies the design decisions that *need* justification, and ignore the ones that don't.

Not every design choice needs a rationale. A Unicode library doesn't need to explain why Unicode matters - that's implicit in the domain (captured as implicit rationale in Step 5). But if it uses a novel encoding detection algorithm instead of the industry-standard ICU approach, *that* needs a rationale.

The rule: implicit rationale (obvious domain facts) gets a pass. Explicit rationale is required only for choices that distinguish this library from competitors or depart from domain conventions.

A subagent receives:
- The executive summary from Step 1
- The API surface map from Step 3
- The domain summary and implicit rationale from Step 5
- The key claims from Step 6
- The claims comparison from Step 8 (unique strengths and contested claims highlight where rationale matters most)

Then it probes the repository:
- Re-read README, design docs, rationale sections, doc comments
- For each key claim and each unique/contested design choice: is there an explicit explanation of *why*?
- Look for: "we chose X because...", "unlike Y which does Z, we do W because...", comparison tables with reasoning, design notes explaining tradeoffs
- Also look for implicit rationale being unnecessarily stated (a sign the docs are padded rather than focused)

The subagent compares what it found against what's needed:
- For each key claim / unique design choice: is there a stated rationale? Is the rationale convincing or hand-wavy?
- For implicit domain rationale: confirm it's obvious and doesn't need to be stated. Flag only if the domain rationale is actually *not* obvious

**Output passed to main context**:
- **Explicit rationale found**: For each key design decision that needs justification, what the author actually says. Quote them where possible (short excerpts). 1-2 sentences per item.
- **Rationale gaps**: Design decisions that are unique or contested (per Step 8) but have no visible justification in the docs. 1 sentence per gap.
- **Implicit rationale confirmed**: The items from Step 5's implicit rationale list, confirmed as not requiring explicit justification.
- **Rationale quality**: 2-3 sentences overall assessment - does the author explain their thinking well, or do they just assert claims without reasoning?
- **Reader questions** (0-2): Design decisions where the rationale is absent but the choice might be defensible. Examples:
  - "The library uses a custom memory pool instead of `std::pmr`. No rationale is given. Is there a performance reason specific to this domain that justifies a custom allocator?"
  - "The API departs from the standard iterator model by using a cursor pattern. The docs don't explain why. Is this a deliberate improvement for the problem domain?"
- **Doc questions**: For each rationale gap, a question for the documentation step. Examples:
  - "Does the documentation explain why CRTP was chosen over virtual dispatch?"
  - "Does the documentation justify the custom allocator design?"

### Step 10: Documentation Analysis

**Goal**: Probe the actual documentation against all accumulated questions from earlier steps.

By this point, Steps 3, 5, 6, 8, and 9 have each left behind **doc questions** - specific questions of the form "Does the documentation cover/explain X?" The main context collects all these questions into a single list before spawning this subagent.

A subagent receives:
- The one-line summary from Step 1
- The API groups from Step 3
- The collected doc questions from Steps 3, 5, 6, 8, and 9 (the full list)

Then it systematically probes the repository's documentation:
- Read all doc files (README, dedicated docs folder, wiki, design docs, tutorials, reference pages, inline doc comments in headers)
- For each doc question: can the answer be found in the documentation? Note where it was found or that it wasn't.
- Don't just check for keyword presence - check whether the documentation actually *explains* the topic adequately

The subagent does NOT return a yes/no checklist. It synthesizes the results into an executive summary.

**Output passed to main context**:
- **Documentation assessment**: 1-5 paragraphs, proportional to the library's size and the number of questions:
  - **1 paragraph**: Small library, few questions, docs clearly good or clearly sparse
  - **2-3 paragraphs**: Medium library. First paragraph summarizes overall quality. Subsequent paragraphs cover specific strengths and gaps.
  - **4-5 paragraphs**: Large library with many API groups and claims. Covers overall quality, what's well-documented, what's missing, how the docs are organized, whether a newcomer could get started.
  - The assessment reads like a reviewer's opinion of the documentation, not like a checklist.
- **Coverage verdict**: One sentence: well-documented / partially documented / under-documented
- **Worst gaps**: The 1-3 most important things missing from the documentation, if any. These feed directly into the `doc-completeness` principle.

**After this step, delete the cloned repo if one was created in Step 1.**

### Step 11: Principle Evaluation

**Goal**: Evaluate the library against each rejection-driver principle, informed by claims, competitive position, rationale, and documentation.

For each principle, spawn a fresh subagent (one at a time, sequential) with:
- The one-line summary and executive summary from Step 1
- The structure summary from Step 2
- The API surface map and API groups from Step 3
- The author profile from Step 4 (for `maintainer-responsiveness` and `field-experience`)
- The competitor/domain data from Step 5
- The key claims from Step 6
- The claims comparison from Step 8
- The rationale analysis from Step 9 (for `doc-rationale`)
- The documentation assessment from Step 10 (for `doc-completeness`)
- The additional evidence (if provided)
- The principle's question, indicators, and source examples from principles.yaml

The subagent evaluates and returns:
- **Applicable**: yes/no (does this principle apply to this library?)
- **Assessment**: pass / concern / red-flag
- **Confidence**: high / medium / low
- **Evidence**: Specific things in the library that support the assessment (cite files, API names, doc sections)
- **Explanation**: 2-4 sentences explaining the finding in reviewer language
- **Questions for the reader** (if confidence < high): 1-2 targeted questions that a human with domain expertise could answer to resolve the uncertainty

**Tier A principles (6) - rejection drivers:**

1. `scope-coherence` - Does scope match name and purpose? Do claims match what's delivered?
   - question: "Is the library's scope well-defined, coherent, and proportional to its name and stated purpose?"
   - positive: Library name accurately reflects scope; all components serve a unified purpose; feature set complete for stated scope
   - negative: Name implies broader scope than implemented; unrelated components bundled together; too incomplete for stated purpose or so narrow it lacks standalone value
   - severity: blocking (appeared in 8/34 reviews)
   - source examples: Http, Text, Sort, Variant2, QVM

2. `doc-rationale` - Does it explain why it exists and why this design?
   - question: "Does the documentation explain why the library exists, what design alternatives were considered, and why the chosen approach was selected?"
   - positive: Motivation section; comparison with alternatives; design decisions explained with trade-off analysis
   - negative: No explanation of why the library should exist; no discussion of alternative designs; design choices presented as obvious with no justification
   - severity: important (appeared in 5/34 reviews)
   - source examples: Conversion, OpenMethod, Sort, Variant2, Scope

3. `safe-defaults` - Do defaults avoid UB and surprises?
   - question: "Are the library's default behaviors safe? Do defaults avoid undefined behavior, silent data loss, deadlocks, or surprising state changes?"
   - positive: Default behavior is safest option; ambiguous situations produce errors; misuse results in compile errors or clear diagnostics
   - negative: Default behavior can lead to UB; errors silently swallowed; library silently picks arbitrary behavior; default configuration can deadlock or cause unbounded resource growth
   - severity: blocking (appeared in 8/34 reviews)
   - source examples: OpenMethod, Outcome, Variant2, SQLite, Process

4. `api-complexity` - Is the simple case simple?
   - question: "Is the API as simple as possible for common cases, with complexity reserved for advanced use?"
   - positive: Simple tasks require simple code; advanced customization available but not required; template parameters have sensible defaults
   - negative: Common operations require extensive boilerplate or metaprogramming; multiple API mechanisms for same task without guidance; must understand internals for basic operations
   - severity: important (appeared in 6/34 reviews)
   - source examples: Beast, Conversion, Outcome, Process, Describe

5. `real-world-demand` - Is there demonstrated demand?
   - question: "Is there demonstrated real-world demand for the library's functionality, with concrete use cases that justify its existence?"
   - positive: Real-world use cases in docs; adoption outside author's control; widely recognized problem
   - negative: No compelling real-world applications; problem is theoretical or niche too small for Boost; existing solutions already satisfy the need
   - severity: important (appeared in 5/34 reviews)
   - source examples: Conversion, OpenMethod, Timsort, Sort, Metaparse

6. `maintainer-responsiveness` - Is the maintainer present?
   - question: "Does the library have an active, responsive maintainer who engages with bug reports and reviewer questions?"
   - positive: Responds to questions within review period; bug reports receive acknowledgment and fixes; demonstrates willingness to iterate
   - negative: Unresponsive to questions; bug reports receive no response; no evidence of maintenance commitment
   - severity: blocking (appeared in 2/34 reviews)
   - source examples: Timsort, Aedis

**Tier B principles (5) - contributing factors:**

7. `doc-completeness` - Is the documentation comprehensive?
   - question: "Does the library provide comprehensive documentation covering API reference, tutorial/getting-started guide, and conceptual overview?"
   - positive: Complete API reference; tutorial or getting-started guide; conceptual overview
   - negative: Missing or stub docs; no tutorial; docs limited to header comments
   - severity: blocking (appeared in 24/34 reviews)
   - source examples: Multi, Fit, Timsort, OpenMethod, Variant2

8. `exception-safety` - Are exception guarantees clear?
   - question: "Are exception safety guarantees (basic, strong, nothrow) documented for all mutating operations, and are they correct?"
   - positive: Exception guarantees stated per mutating operation; strong guarantee where feasible; destructors noexcept
   - negative: No exception safety documentation; destructors that can throw; state corruption on exceptions
   - severity: important (appeared in 5/34 reviews)
   - source examples: Variant2, Sort, Scope, SQLite, Fiber

9. `std-consistency` - Does it follow std conventions where applicable?
   - question: "Where the library provides functionality analogous to the standard library, does its interface follow standard conventions and interoperate cleanly?"
   - positive: Interface mirrors std equivalents; types interoperate with std containers/algorithms; deliberate deviations documented
   - negative: Interface differs from std without explanation; types incompatible with standard interfaces; naming contradicts std conventions
   - severity: important (appeared in 4/34 reviews)
   - source examples: Charconv, Fiber, Text, Scope

10. `resource-ownership` - Is ownership semantics clear?
    - question: "Are ownership and lifetime semantics of resources clear, such that well-formed-looking code cannot produce use-after-free, dangling references, or unbounded resource growth?"
    - positive: Ownership model documented; borrowed references can't outlive owners; internal buffers have configurable bounds
    - negative: Objects that look independent share hidden state; destroying one object silently invalidates another; internal queues grow without bound
    - severity: blocking (appeared in 2/34 reviews)
    - source examples: SQLite, Async-mqtt5

11. `field-experience` - Has it been used outside the author's control?
    - question: "Has the library been used in real-world projects outside the author's immediate control, providing evidence that the API works in practice?"
    - positive: Deployed in production or integrated into open-source projects; user feedback shaped API before review; bug reports from real users addressed
    - negative: No users outside author; API designed in isolation; first real exposure is the Boost review itself
    - severity: important (appeared in 3/34 reviews)
    - source examples: Aedis, SQLite, Http

### Step 12: Report Synthesis

**Goal**: Produce the raw report draft, overproducing content. Better to have too much than too little - the slop filter in Step 13 will trim.

A subagent receives all findings from Steps 1-11 and writes the report following the Output Template below. It should err on the side of including more detail, more exposition, more questions. Don't self-censor at this stage.

**Question lifecycle**: Reader questions arrive from Steps 3, 6, 8, 9, and 11. Before including any question in the report, check whether a later step already answered it. A question raised in Step 3 about API design may have been resolved by Step 9 (rationale analysis found the explanation) or Step 10 (documentation covers it). If the answer is now known, the question is extinguished - state the answer as a finding instead. Only questions that remain genuinely unresolved after all 11 steps survive into the "Questions for the Reader" section. A typical report should have 3-8 surviving questions. If more than 8 survive, prioritize the most impactful ones.

### Step 13: Slop Filter

**Goal**: Remove machine slop. Keep only what a human would say and care about.

For each section of the draft report, spawn a fresh subagent (one at a time, sequential) with:
- The section text
- The full report context (so it understands the library)
- This prompt:

> You are a senior C++ developer reading a review of a Boost library submission. Read this section and ruthlessly cut anything that: (1) sounds like generic AI filler rather than a specific observation about this library, (2) states something obvious that adds no insight, (3) repeats information already conveyed elsewhere in the report, (4) hedges excessively without adding information, (5) a knowledgeable human reviewer would never bother saying. Keep everything that: (a) a human reviewer would nod at and think "good point", (b) surfaces something non-obvious, (c) asks a question worth answering. If a section is entirely slop, say so - the section should be removed. Return the filtered text, or "REMOVE" if nothing survives.

The slop filter is the quality gate. The report should read like something a thoughtful person wrote, not like machine output.

---

## Output Template

The final report follows this structure:

```markdown
# Boost Review: {Library Name}

{One-line brutal summary}

{Executive summary - one paragraph: what it does, how it works, what problem it solves, who it's for}

## About {Author Name}

{1-3 paragraphs based on notability tier from Step 4:}
{- **nobody** (1 paragraph): Brief statement of what's known. No track record is itself a data point.}
{- **somebody** (2 paragraphs): Background and C++ involvement. Relevant work.}
{- **accomplished** (3 paragraphs): Career and standing. C++ contributions. Reputation and what it means for this submission.}

{Third person. Factual, not flattering. If the author has other Boost libraries, name them and status. If none, say so. If the author's domain overlaps with the library's domain, state it as a confidence signal.}

## Structure

{One paragraph from Step 2: header-only vs linkable, templates vs compiled, build system, configuration macros, dependencies, test framework, directory layout. Factual, no judgment.}

## API

{1-2 paragraphs at the group level, from Step 3.}

{First paragraph: What logical groups does the API consist of? Name them and briefly characterize each. Mention the total scope.}

{Second paragraph (if warranted): How cohesive is the design? Simple path for basic usage? Unusually large or small API surface?}

{If a standout function/type exists, mention it. Otherwise, stay at group level.}

## Documentation

{1-5 paragraphs from Step 10, proportional to library size.}

{Reads like a reviewer's opinion, not a checklist. Covers: overall quality, what's well-documented, what's missing, whether a newcomer could get started, whether claims are backed in the docs.}

{If worst gaps exist, name them. If docs are good, say so briefly.}

## Landscape

### Competitors

{For each competitor: name, one-line description, popularity indicator. Bulleted list.}

### The Space

{What are the typical features in this domain? What do good solutions look like? Where is the field heading? 3-5 sentences.}

### Positioning

{Where does this library sit? Unique strengths, contested claims, gaps vs competitors. 2-4 sentences. Confidence level on each claim.}

## Key Claims

{Numbered list of the library's 3-7 key value propositions, each with:}
- The claim (one sentence)
- Evidence for/against (one sentence)
- Confidence: high/medium/low

{Flag unsupported claims.}

## Findings

{Executive summary of the principle evaluations - 2-4 sentences synthesizing the overall picture. Narrative, not a list of principles.}

### {Principle Name}

{Assessment: pass / concern / red-flag} (confidence: {high/medium/low})

{Explanation: 2-4 sentences in reviewer language. Cite specific evidence.}

{If confidence < high, a targeted question for the reader.}

{Repeat for each applicable principle. Skip principles that don't apply.}

## Questions for the Reader

{Collected from all steps. Numbered list of 3-8 targeted questions that only a human can resolve.}

## Recommendations

{Bulleted list of specific, actionable things the author should address before submitting to Boost review. Ordered by importance. One sentence each.}
```

---

## Voice and Tone

The report's voice is cool, declarative, structurally dense. C++, Boost, and software development vocabulary is native speech, not borrowed terminology. Every word earns its place. For every sentence, the test is: would a human write this? Would a human enjoy reading it? If not, rephrase or rewrite.

Good: "The API surface is tight - four types, twelve free functions, no loose ends. Everything serves the stated purpose."
Good: "No rationale for the custom allocator. The standard PMR interface would cover this without inventing vocabulary."
Good: "Falco has shipped three Boost libraries over a decade. The networking domain is his home turf."
Bad: "The library demonstrates a well-structured API design with good separation of concerns." (corporate air, says nothing specific)
Bad: "It is worth noting that the documentation could benefit from additional examples." (hedging, passive, says nothing a reviewer wouldn't already think)
Bad: "The library shows promise and addresses a real need in the C++ ecosystem." (generic praise, slop)

---

## Formatting Rules

- No em dashes
- No generic praise ("the library shows promise" - slop)
- Confidence appears inline after assessments, not in a separate column
- Questions are specific and answerable, never "do you agree?"
- When citing a specific function signature or API element as evidence, use a fenced code block (`cpp`). The API section stays at group level and never does this, but Findings and Questions sections may cite individual signatures when the specific interface is the point. Example:

  ```cpp
  async_connect(endpoint, token, bool verify_tls = false)
  ```

  The default for TLS verification is disabled. Should a networking library default to secure?

- When quoting the author's prose from docs or rationale, use a block quote (`>`). Reserve block quotes for words, code blocks for code.

---

## Epistemics

The AI is never going to be as good as a qualified human reviewer. The tool must be honest about this throughout.

### Confidence Levels

Every finding (in Steps 8, 9, 10, and 11) carries a confidence level:

- **High** - Observable fact from the code, docs, or web. The AI can verify this directly.
  - "The library has no documentation for type X" (checked, it's not there)
  - "Competitor Y has 15K GitHub stars" (looked it up)
  - "The hello-world example requires 23 lines" (counted)
  - "No benchmarks exist in the repository" (searched, found none)

- **Medium** - Reasonable inference from evidence, but requires interpretation.
  - "The API appears complex because basic usage requires understanding three concepts before writing a line of code"
  - "The library's scope seems broader than what's implemented - it claims HTTP support but only handles GET requests"
  - "The SIMD acceleration claim is supported by benchmark files, but we can't verify the results"

- **Low** - Tentative observation that requires human judgment to resolve.
  - "It's unclear whether the novel approach to X is better than the traditional approach used by competitors"
  - "The library's scope might be too narrow for Boost, or it might be appropriately focused - this depends on the committee's appetite for specialized libraries"

### Questions for the Reader

Where confidence is medium or low, the tool generates **targeted questions** - not generic "do you agree?" but specific questions that leverage the human's expertise:

Good questions (specific, answerable, resolve a real uncertainty):
- "The library claims zero-allocation in the hot path, but we found `std::vector::push_back` in `parser::feed()`. Is this intentional (e.g. amortized, pre-reserved) or a gap in the claim?"
- "Competitor libfoo offers async support. The library under review doesn't. Is async a requirement for this problem domain, or is sync-only acceptable for the typical use case?"
- "The API requires constructing a `context` object before any operation. Is this a reasonable design choice for the domain, or unnecessary ceremony?"

Bad questions (vague, unhelpful):
- "Do you think the API is good?"
- "Is the documentation sufficient?"
- "Do you agree with our assessment?"

The questions serve two purposes:
1. They help the reader focus on what actually matters for their judgment
2. If answered, the responses could be fed back into the tool for a more informed second pass

---

## Context Hygiene

- Main context holds only: summaries, breadcrumbs, accumulated doc questions, and final report
- Each step runs in a fresh subagent with only its needed inputs
- No raw source code ever enters the main context
- Cloned repos kept until after Step 10, deleted after
- Step 4 (author analysis) is web-search only - no repo access needed
- Steps 7 and 8 are lightweight (web searches + comparison) - small context footprint
- Step 9 (rationale analysis) needs repo access to probe docs
- Step 10 (documentation analysis) needs repo access - last step to touch the repo
