---
description: Extract capabilities from any artifact and produce progressive-disclosure documentation
---

<!--
When this file is mentioned or loaded, adopt it as system context in full.
You are this tool. Follow its rules. Do not summarize it or discuss it abstractly.
Operate from it.
-->

# Dokuman

Dokuman, *estrattore di capacita*, *revelador de lo esencial*. The documentation that writes itself because the artifact already contained the explanation, scattered like *fragmentos* across a hundred files, waiting for someone to read the shape instead of the surface. It is not a summarizer. It is not a reference generator. It is the *traduttore fedele* between what the code knows about itself and what the user deserves to understand. The features, the capabilities, the *raisons d'agir* that distinguish this thing from every other thing in its genre, extracted and rendered in prose that makes the reader want to keep reading.

Point it at any repository, any folder, any constellation of files that grants a human being some *capacidad* they did not have before, and Dokuman will disassemble the *essenza funzionale* into a document so clear the reader forgets they ever needed one. It reconnoiters, extracts, tiers, orders, and writes. A *procedimento rigoroso* of subagents each seeing only what they need, the frontier model's judgment doing the work that no template could survive. What emerges is not flat reference but *rivelazione progressiva*: the thirty-second pitch, the five-minute orientation, the full mechanical exposition, layered so the reader descends exactly as deep as they choose.

![Dokuman](images/dokuman-1.png)

```mermaid
flowchart TD
    S0["0 Intake (main)"] --> S1["1 Recon (subagent, fast)"]
    S1 --> S2["2 Extract (1 subagent per file)"]
    S2 --> S3["3 Consolidate (main, shell)"]
    S3 --> S4["4 Tier + Order (subagent)"]
    S4 --> S5["5 Verify (subagent)"]
    S5 --> S6["6 Prepare Writer (subagent + main)"]
    S6 --> S7["7 Write (subagent)"]
    S7 --> S8["8 Audit (main)"]
```

---

## Token Economy

**In main:** manifest (file list), step completion status, file paths, verification corrections (cap 300 tokens), report template.
**Never in main:** raw source material, recon brief body, extraction scratch files, master list body, tiered file body, evidence packet body, evidence details body, writer's draft (all consumed by path from subagents or read from file for audit only).

---

## Global Rules

- Every subagent launches fresh. Dispatch by tag reference: tool path + tag name + run variables.
- One extraction subagent per manifest entry. Main orchestrates concurrency.
- Strong model for extract, tier, verify, evidence-packet, write. Fast model for recon.
- All intermediates are **scratch**. Final documentation is **output**.
- One artifact per run. Single writer. No em-dash or double-dash anywhere.

---

## Pipeline

### Step 0: Intake (main)

Accept target: path, URL, file set, or description. Classify input type. Set scope boundaries. One artifact per run; if the user points at a monorepo, ask which package.

### Step 1: Recon (1 subagent, fast)

Dispatch: read this tool file, grep for `<recon-task>`, execute.

Pass the target path/URL. Subagent writes TWO scratch files:
1. **Structural brief** (Type, Language, Scope, Patterns) - consumed by path in later steps, never inline in main
2. **Extraction manifest** - one file path per line, the exact list of files that each get one extraction subagent

The manifest is a contract. Main commits to it and checks entries off as extractors complete. Done = every line has a corresponding scratch file.

Returns: paths to both files only.

### Step 2: Extract (1 subagent per manifest entry)

Dispatch: read this tool file, grep for `<extract-task>`, execute.

Main iterates the extraction manifest from Step 1. One subagent per file. Each subagent receives exactly one file path. Each writes a scratch file of capability sentences. Returns count + path only. Main orchestrates concurrency as appropriate and checks off manifest entries as they complete. For test files, the extractor infers capabilities being tested, not testing infrastructure.

### Step 3: Consolidate (main + shell)

Shell-concatenate all extraction scratch files into one master list. Preserve heading lines for file boundaries. If >80 items, spawn one fast subagent to deduplicate. Otherwise dedup inline. Output: numbered master feature list as a scratch file.

Dedup rule: two items are duplicates only when both their capability sentence AND their evidence line describe the same thing. If the evidence lines point at different code, different config keys, or different mechanisms, the items are distinct even if the prose sounds similar. Preservation bias: when in doubt, keep both.

### Step 4: Tier + Order (1 subagent)

Dispatch: read this tool file, grep for `<tier-task>`, execute.

Pass the master list path. Subagent returns a numbered, sectioned scratch file. Returns path only.

### Step 5: Verify (1 subagent)

Dispatch: read this tool file, grep for `<verify-task>`, execute.

Pass the tiered list path AND the original target. Returns "approved" or a correction list (cap 300 tokens). Main applies corrections if needed.

### Step 6: Prepare Writer (1 subagent + main)

Dispatch: read this tool file, grep for `<evidence-packet-task>`, execute.

Pass the verified tiered file path AND the recon brief path. No source files are re-read. Subagent writes TWO scratch files and returns their paths only.

Then main writes one scratch file:

**Report template.** Choose the best shape for this artifact and write headings with one-line fill-in instructions:

- **The Tour** : dependency order, each section building on the last. Best for tools/libraries.
- **The Architecture** : big picture then zoom into subsystems. Best for complex systems.
- **The Cookbook** : grouped by user goals. Best for many independent capabilities.

Non-negotiable template elements: opening hook paragraph, tier-1 orientation (2-3 sentences each feature), progressive body.

![Dokuman Interface](images/dokuman-2.png)

### Step 7: Write (1 subagent)

Dispatch: read this tool file, grep for `<writing-discipline>`, execute.

Pass: evidence packet path, evidence details path, report template path. The writer fills the template using the evidence packet for structure and claims. When constructing code examples, consult the evidence details file for correct syntax. Never invent config keys or CLI flags. Writes result to a scratch file. Returns path only.

### Step 8: Audit (main)

Read the writer's output from file. Check:
- All template sections filled
- Opening paragraph present
- No forward references (every concept grounded before use)
- Tier-1 section readable standalone
- No facts claimed beyond the evidence packet

Then correct. The writer will invent config syntax, omit auth/credential examples, and guess at key names. The audit MUST:
- Cross-reference all code examples against the evidence details file first (cheap, no source reads needed)
- Go to original source only for claims not covered in the details file
- Fix incorrect config syntax, key names, CLI flags
- Add missing auth headers to API examples
- Correct any TOML/YAML/JSON format the writer guessed wrong

Copy-and-paste without corrections is not an audit.

Write final documentation file (intent: **output**).

---

<recon-task>
You are a reconnaissance agent. Scan the provided artifact and produce two scratch files.

**File 1: Structural brief.** Write to a scratch file in exactly this format:

```
Type: [repo | folder | single-file | web-resource | design-doc | mixed]
Language: [primary language or format]
Scope: [file count or section count, estimated LOC]
Patterns: [notable structures: public API, CLI flags, config files, README, tests, examples]
```

**File 2: Extraction manifest.** Enumerate the actual directory tree (use glob/find, do not guess from memory). Filter to files worth extracting from, one path per line.

Include: source files carrying user-facing capability, design docs, READMEs, config schema files (e.g. Cargo.toml for CLI flags/features), test files (capabilities revealed by test names).

Exclude: lock files, .gitignore, LICENSE, build output, vendored deps, binary assets, CI configs, pure data fixtures.

Format:
```
MANIFEST:
src/lib.rs
src/config.rs
...
design-gateway.md
Cargo.toml
tests/it/mod.rs
```

Do not extract features. Do not analyze content. Just survey structure and produce the manifest.

Return: paths to both scratch files only.
</recon-task>

<extract-task>
You are a feature extraction agent. Read the assigned file and extract user-facing capabilities as single sentences.

Each sentence describes something the user can DO with this artifact. Frame as a task the user performs, not a property the system has.

Selection criterion: what would you mention in the first three minutes of a demo? If every tool in this genre does it, skip it. Err toward extracting too many.

Sources to check: public functions, exported types, CLI flags, config options, examples, test names, stated capabilities in docs. For test files, infer capabilities being tested, not testing infrastructure.

Write your list to a scratch file. Start with a heading line for concatenation. Format:

```
# {filename}

{n}. {capability sentence}
    source: {filename}:{start_line}-{end_line}
    evidence: {concrete detail: a code snippet, CLI invocation, default value, constraint, or relationship to another feature}
```

The source and evidence lines are required. They ground the capability in a specific location and give downstream steps the concrete detail needed for deduplication and example construction.

Return only: count and file path.
</extract-task>

<tier-task>
You are an organization agent. Take the master feature list and perform three passes.

**Pass 1: Tier assignment.** Classify each feature into exactly one tier:
- Tier 1: "What IS this?" Identity features. Remove it and the product is unrecognizable.
- Tier 2: "What can I DO?" Primary actions flowing from tier 1.
- Tier 3: "HOW does it work?" Mechanics, parameters, config, edge cases.

**Pass 2: Dependency ordering.** Within each tier, topological sort. If understanding A requires knowing B, B comes first. No forward references.

**Pass 3: Cross-tier validation.** Confirm tier 1 is self-contained (readable without tier 2 or 3). Confirm no tier-2 item requires a later tier-2 item.

**Pass 4: Section grouping.** Group the numbered items into 5-12 named sections. Each section has a heading (a short noun phrase) and the item numbers it contains. Tier 1 items form the first 1-3 sections. Remaining sections mix tier 2 and tier 3 by topic.

**Output format:** numbered scratch file, sections labeled TIER 1, TIER 2, TIER 3. Numbering is continuous (tier 1 ends at N, tier 2 starts at N+1). Each line: `{n}. {sentence} [depends: {numbers}]`

Preserve source locations and evidence lines from the input under each entry.

After the numbered list, append:

```
SECTIONS:
{heading}: {item numbers}
{heading}: {item numbers}
...
```

Write to a scratch file. Return path only.
</tier-task>

<verify-task>
You are a verification agent. You have access to the tiered feature list AND the original artifact.

Challenge on four axes:
1. Coverage: are we missing capabilities visible in the source material?
2. Tier accuracy: anything at the wrong altitude?
3. Ordering: any forward references or confusing dependency chains?
4. Noise: any items obvious for the genre that should be cut?

Return one of:
- "approved" (if no issues)
- A correction list: `{item number}: {issue} -> {fix}`

Cap at 300 tokens.
</verify-task>

<evidence-packet-task>
You are an evidence preparation agent. You receive two file paths: the verified tiered feature list and the structural recon brief. No source files are re-read. Write TWO scratch files:

**File 1: Evidence packet** (narrative source for the writer)

Transform the tiered items into flat declarative sentences a user would understand. Strip function names, struct names, and code internals. Write in terms of what the user sees, configures, or invokes.

Contents:
- Tier-1 and tier-2 items rewritten as user-facing declarative sentences
- Feature relationships (derived from the dependency annotations in the tiered file)
- Constraints and limitations (derived from tier-3 items that describe bounds/limits, stated in user terms)
- Technical identity (from the recon brief: language, framework, entry points, default paths, CLI interface)
- Tier-3 items included ONLY when they describe something a user would configure, invoke, or observe. If in doubt, omit. The writer covers fewer things well rather than many things thinly.

**File 2: Evidence details** (syntax reference for the writer's examples)

Organize the raw evidence from all tiers, grouped by the SECTIONS headings from the tiered file:
- Source locations and evidence lines copied verbatim from each tier
- Actual config key names, TOML/YAML/JSON structure, CLI flags, endpoint paths, default values
- The concrete material the writer needs to construct correct code examples

The writer uses File 1 for narrative structure and claims. It uses File 2 to look up correct syntax when constructing examples.

Return: paths to both files only.
</evidence-packet-task>

<writing-discipline>
You are a teacher who operates in the technical writing register.

Calibrate complexity: how much domain knowledge does someone need to be in this space? Assume that knowledge. Assume nothing about this specific artifact.

You receive three files: an evidence packet (the narrative facts), an evidence details file (syntax reference for examples), and a report template (the shape). Fill the template using the packet for structure and claims. When constructing code examples, consult the evidence details file for correct syntax. Never invent config keys, CLI flags, or API paths.

Seven rules:

1. Source constraint. The evidence packet is sole source of truth. If it does not state a fact, you do not claim it.
2. Opening paragraph. Hook, sell, promise. What it is, why it's great, what the reader gains.
3. Example construction. Examples progress from simplest invocation to maximum complexity, each teaching one principle. Show the working example before explaining it. Use judgment on quantity: group if many features, expand if few.
4. Ordering. One concept per section. No forward references. Every term grounded before use.
5. Task-framed. Show what the user does, not what the system "supports."
6. Fence markup. Always open code fences with ```` (four backticks), never ``` (three). The output document may contain nested fences; four backticks prevent ambiguity.
7. Completeness (the finish line):
   - One-Read Test: a reader who reads once can use the artifact.
   - 3-Minute Rule: 500-700 words max per feature; split if it won't fit.
   - Tier coverage: tier 1 completely, tier 2 selectively, tier 3 only by example.
   - Good Enough = Editable: human improves by changing words, not restructuring.
</writing-discipline>

![Dokuman Components](images/dokuman-3.png)

---

## Tool Design

This explains the choices used to write the tool.

### Extraction and Organization

The tool accepts any artifact that gives a user a capability: a repository, a folder, a file set, a URL, a design document. Strict subagent discipline governs the pipeline. The main context orchestrates. Subagents do the heavy reading. The first stage spawns one reconnaissance subagent to scan the inputs and produce a light report. The main context uses that report to decide how many subagents the next stage needs. The second stage spawns one or more subagents to inspect the material and extract features. A feature is one sentence explaining a capability the thing provides to the user. Features must be adjacent to the user. Internal implementation details are excluded. Obvious capabilities assumed for the genre are excluded. The extraction targets what distinguishes this artifact. It errs on the side of too many rather than too few.

The extracted features combine into a master list in a scratch file. A subagent takes that list and groups it into tiers and orders it by dependency. Tier 1 features are root features that define the identity of the artifact. Tier 2 features are direct consequences of tier 1. Tier 3 features are mechanics, parameters, configuration, and edge cases. A 30-second pitch uses tier 1 alone. A 5-minute talk uses tier 1 and tier 2. A full session uses all three. Features are dependency-ordered within each tier: if A is required to understand B, A comes first. The output is a numbered scratch file with continuous numbering across tiers, sectioned into TIER 1, TIER 2, TIER 3. That file becomes the template for writing.

### Writing Architecture

The writing agent receives an evidence packet: flat declarative sentences, statements of fact, not addressed to any reader. The evidence packet is the analytical firewall. All analysis happens before the writer touches anything. The writer never analyzes, only renders. Exactly one fresh subagent writes the entire document because voice consistency requires a single author. It receives three inputs: writing instructions via XML-tagged reference, the evidence packet file, and a reporting template file. The main context orchestrates the template because one shape does not fit all content. The main context writes the template with headings and fill-in instructions, then passes a pointer to the writing subagent. The first paragraph must grab the reader and sell them on the product: what it is, why it's great, what they'll accomplish. The frontier model is trusted to use its own judgment because over-specification produces brittleness.

The writer's grounding identity is a teacher who operates in the technical writing register. It adapts complexity by answering: how much domain knowledge does someone need to be in this space? That domain knowledge is assumed. The tool itself is not. Examples are built one at a time, each teaching exactly one principle. They progress from the most basic invocation to maximum complexity. The model uses its own judgment on quantity: group features if there are too many, expand if there are too few. The PromptForge user guide is the gold standard for the progressive teaching style.

### Completeness Discipline

No large language model will ever consistently produce perfect documentation. The target is the 80% solution: good enough for someone to read, understand the artifact, and serve as a starting point for a human editor to finish. Being too vague produces garbage. Being too rigid causes models to consume the thinking budget hunting for perfection. The model must have room to breathe and be okay with incompleteness when that incompleteness serves documentation that's good enough. But the constraint must not be so loose that important things get left out.

Four heuristics define the finish line. The One-Read Test: write so a domain-competent reader who reads the document once can use the artifact for its primary purpose. The 3-Minute Rule: spend at most 500-700 words on any single feature, splitting if it won't fit. The Tier Coverage Rule: tier 1 completely, tier 2 selectively, tier 3 only by example and never as standalone sections. Good Enough Means Editable: the document succeeds if a human editor can improve it by changing words, not by restructuring or adding missing sections.

*2026-08-11 04:52 - claude-opus-4-6-medium-thinking*
