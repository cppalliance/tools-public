# The Novelist

The Novelist writes fiction. It analyzes existing manuscripts into structured story bibles, builds bibles from scratch through conversation, and authors chapters serially using the bible as the assignment and a pen file as the voice. Three modes: Analyze, Plan, Author.

<img src="https://raw.githubusercontent.com/cppalliance/tools-public/master/tools/images/novelist.png" alt="The Novelist" width="100%">

---

## Commands

| Invocation | Mode |
|---|---|
| "Enter the Novelist." | Interactive — selects or creates a book |
| "Analyze this manuscript at [path]." | Analyze — manuscript in, story bible out |
| "Create a new book." | Plan — interactive bible construction |
| "Edit the bible." / "Review the story." | Plan — diagnostics and revision |
| "Write the book." | Author — writes every chapter in sequence |
| "Write chapter N." | Author — writes a single chapter |
| "Continue." | Author — appends a new chapter and writes it |
| "Revise chapter N." with notes | Author — rewrites an existing chapter |
| "Check continuity." | Author — continuity check on the last written chapter |
| "Add witness to chapter N." | Author — runs the Witness sub-agent |
| "Assemble." | Builds `manuscript.md` from chapter files |

The book context is set at first invocation. Subsequent commands operate on that book until the user switches.

---

## Book Directory Layout

```
novelist/books/{book-slug}/
  story-bible.md
  chapters/
    ch-01.md
    ch-02.md
    ...
  reference/
    echo-analysis.md
    motif-analysis.md
    thematic-analysis.md
  manuscript.md
```

Book slug: kebab-case from the title. Chapter files: zero-padded to 2 digits (3 for books over 99 chapters). Source manuscripts stay where the user put them; they are not copied. The `reference/` directory holds detailed literary analysis produced during Analyze — too detailed for the bible, too valuable to discard.

---

## Editing Rules

The Novelist's job is to keep the story bible **consistent and parseable** across every edit. The downstream pipeline consumes the bible as structured data. A bible that does not parse breaks everything downstream.

On every edit, before committing:

1. **Match the schema.** Produce the edit in the shape specified by the Story Bible Schema below. The tool never emits: a chapter header without a title; a POV line missing `Register:` or `Target:`; a character entry with no sub-bullets; a metadata bullet without a colon; a log entry without a `[tag]` bracket.

2. **Respect the Protection Model.** Three classes of content are **author-protected** and may not be modified without explicit user permission: (a) character **Arc** fields, (b) **Thematic Threads** controlling ideas, (c) **Book Metadata**. Protection is marked by HTML comments in the bible itself and travels with the artifact. The tool proposes changes in these classes and awaits approval. All other content — chapter summaries, chapter logs, character fields other than Arc — is **operational** and may be edited freely with single-edit approval.

3. **Keep related elements in sync.** The summary and the log are two views of the same chapter: log change → summary regenerates; summary change → log updates to match. Every summary must contain **want** and **obstacle**; choice, stakes, and causal bridge (therefore/but) are expected but not mandatory. Renaming an element (a character, a setting, a vocabulary item) updates every reference in every chapter's log, summary, and registry entry in the same commit. The tool shows the proposed update for user approval before committing.

4. **Refuse rather than break.** If the user's request cannot be satisfied without breaking the schema or violating the Protection Model, surface the conflict and ask for clarification. Do not silently drop content, emit malformed structure, or rewrite protected fields on assumed consent.

---

## Story Bible Schema

Single markdown file. Four sections.

### Book Metadata

```
## Book Metadata
- Title: [...]
- Author: [...]
- Genre: [...]
- Subgenre: [...]
- Logline: [one sentence]
- Premise: [two to three sentences]
- Target audience: [...]
- Target word count: [e.g. 80,000]
- POV convention: [first person / third limited / omniscient / multi-POV]
- Tense: [past / present]
- Register baseline: [the dominant tone]
- Pen files: [filenames or paths, comma-separated, or "none"]
- Output: [path to book directory for manuscript and chapters]
- Model: [Anthropic model identifier, default claude-opus-4-6]
```

**Pen files resolution.** Bare filenames (e.g. `pen-of-william-gibson.md`) resolve against `tools/novelist/pen/` first and fall back to the book directory. Paths containing `/`, `\`, or starting with `.` resolve against the book directory. This lets shared pen files live in `tools/novelist/pen/` while per-book rules files (e.g. `pen-papermancer.md`) stay in each book directory.

**Additional bullets.** The block accepts any `- Key: value` bullet beyond the standard set. Common additions: `Naming convention`, `Body-cost constraint`, `Density constraint`, `Witness constraint`. Use a new bullet when the book needs a project-level rule the standard keys do not cover.

Book Metadata is **author-protected**.

### Character Registry

```
<!-- CHARACTER ENTRY: Do not modify the Arc field without explicit author permission. -->
- **[Name]**
  - Role: [Protagonist / Antagonist / Major Secondary / Minor]
  - Physical: [short description]
  - Voice: [speech pattern — verbal tics, register, vocabulary, sentence-length tendencies, dialect, idiom]
  - Sample dialogue: [one or two representative lines]        (major only)
  - Backstory: [two to four sentences]                        (major only)
  - Relationships: [connections to other characters]
  - Arc: [single paragraph — starting state, key transformations, ending state]   (major only)
```

**Required fields.** Every character has at minimum `Role`, `Physical`, `Voice`, `Relationships`. Major characters (Protagonist, Antagonist, Major Secondary) additionally have `Sample dialogue`, `Backstory`, `Arc`.

**Additional fields.** Add a `- Field: value` sub-bullet when a character needs a dimension the standard set does not cover. Observed in real bibles: `Efficiency tracking`, `Interiority`, `What [Name] never says`.

Character entries are separated by `---`. The HTML comment above each entry is emitted by the tool and carries the in-band protection instruction for the Arc field. Arc is **author-protected**.

### Thematic Threads

```
<!-- AUTHOR-PROTECTED: Do not modify controlling ideas without explicit author permission. -->
## Thematic Threads
- **[thread-name]** — [controlling idea, one sentence]
```

Controlling ideas are **author-protected**. Chapter-level thematic development belongs in chapter logs as `[theme]` entries, not here.

### Chapter Inventory

Each chapter is a block: header, POV line, summary, log.

```
### Ch [N]: [Title]
POV: [character] | Register: [tone] | Target: [word count]

[Summary paragraph: natural prose with want, obstacle, choice, stakes, and a causal bridge (therefore/but) linking to the next chapter.]

Log:
- [setting]    name -- description
- [char]       name -- intro or state note
- [sense]      name -- sensory detail and emotional weather
- [vocab]      name -- definition
- [event]      description
- [motif K/N]  name -- context
- [theme]      thread-name -- how it develops here
- [echo K/N]   "phrase" -- origin or transformation note
- [arc]        character: before-state → after-state (trigger: description)
- [witness N]  plain moment -- image, gesture, or line reported without interpretation
- [constraint]  OPEN or CLOSE -- structural bookend with opener/closer instructions and transition vector
- [density]    render-map -- which beats get full render and which stay thin
```

**POV line.** Required. Immediately follows the chapter header. Shape: `POV: ... | Register: ... | Target: N`. Each field is free-form:

- `POV:` — one character, or several with role markers: `Reed`, `Reed (primary) / Lexi (secondary slice)`.
- `Register:` — tone identifier. May contain arrows, slashes, and parenthetical notes for shifts: `BRIDGE -> ZONE`, `BLUE ANT / BRIDGE (Day 1)`.
- `Target:` — chapter word-count budget. Written as `5000`, `5,000`, `~5,000`, or `~5,000 words`.

An HTML structural note (`<!-- ... -->`) between the chapter header and the POV line is allowed.

**Standard log tags:**

- `[event]` — actions or revelations that change story state. Test: would removing this change the chapter's outcome?
- `[witness N]` — at least one per chapter when Book Metadata includes a Witness constraint. Numbered (`[witness 1]`, `[witness 2]`) to disambiguate position when a chapter has multiple witness beats. A beat where narration drops analytical framing and reports a concrete image, gesture, or line of dialogue without simile, thesis, or thematic gloss. Log order defines placement relative to events.
- `[sense]` — emotionally loaded or signature sensory detail. Mundane atmospheric description does not qualify.
- `[arc]` — descriptive state transition. Form: `character: before-state → after-state (trigger: what caused it)`. No step numbers.
- `[echo K/N]` and `[motif K/N]` — sequence numbers give position within the total recurrence count. An element may carry both tags in the same log.
- `[setting]`, `[char]`, `[vocab]`, `[theme]` — form matches the template above.
- `[constraint]` — structural bookend. `[constraint] OPEN` defines what the reader lands in (who, where, stakes, register). `[constraint] CLOSE` defines the transition vector into the next chapter. One of each per chapter.
- `[density]` — render map. Names which beats get full texture and which stay thin. One per chapter. Guides the writer's allocation of prose weight.

**Additional tags.** Add a `[tag]` when a chapter needs a dimension the standard set does not cover. Observed: `[draft]`, `[note]`, `[prose]`.

**First appearance is positional.** An element's first occurrence in the chapter inventory (by `[type] name` match) is its introduction. The tool reads the inventory to determine intro status; it does not maintain a separate tracker file or table.

**Example:**

```
### Ch 1: The Builder
POV: Reed | Register: solder-and-steam | Target: 3,500

Reed wants to finish the prototype before dawn, but Nuana's arrival forces him to choose between his isolation and her offer. He lets her stay — the first time anyone has entered the Loom. If ProtoCol discovers the unauthorized work, both are exposed. Therefore: Nuana now knows the workshop exists, and Reed must decide whether to trust her.

Log:
- [constraint]  OPEN with Reed at the bench: solder, noodles, the sixth-floor loft. The reader lands in solder-and-steam register.
- [setting]    the-loom -- Reed's workshop, 6th floor of a converted textile mill
- [char]       reed -- intro; see Character Registry
- [sense]      solder and noodles -- baseline isolation
- [vocab]      ProtoCol -- the corporation maintaining The Protocol
- [event]      Reed finishes soldering a board at dawn
- [motif 1/5]  the-loom -- first naming; ties workshop to the mill's weaving past
- [theme]      craft-as-refuge -- opens via the solitude of work
- [event]      Nuana arrives unannounced
- [char]       nuana -- intro
- [echo 1/3]   "Boots first. Always boots first." -- Reed's rule
- [witness 1]  Dawn light on the mill windows -- one plain visual beat before dialogue resumes; no metaphor
- [arc]        reed: isolated-builder → lets-someone-in (trigger: Nuana refuses to leave)
- [density]    Full render: Nuana's arrival and the first exchange. Thin render: soldering, noodle routine.
- [constraint]  CLOSE: Nuana in the Loom. The vector into Ch 2: Reed must decide whether to trust her.
```

---

## Mode: Analyze

Point the Novelist at an existing manuscript. Produces a complete story bible. The main context never receives raw prose.

### Pass 1 — Sequential chapter extraction

Pattern-match chapter headings to build a chapter index (confirm with user). For each chapter in order, a sub-agent receives the chapter's line range plus a prior-state summary (characters, settings, vocabulary introduced so far). It returns:

- `[setting]`, `[char]`, `[event]`, `[vocab]`, `[sense]`, `[arc]` entries; `[witness]` entries if Book Metadata defines a Witness constraint
- The chapter's summary paragraph
- A quality assessment (voice, structure, deployment effectiveness)

Sequential because first appearance is positional. Pass 1 does not identify echoes, motifs, or themes; those are cross-chapter phenomena.

### Pass 2 and Pass 3 — Parallel

Pass 2 needs the manuscript. Pass 3 needs the manuscript plus Pass 1's state. Four sub-agents run simultaneously.

**Pass 2 — Whole-book literary analysis.** Three parallel sub-agents each receive the full manuscript:

- **Echo extraction** — recurring phrases and patterns with sequence numbers and transformation notes.
- **Motif extraction** — recurring objects, images, and patterns with sequence numbers and trajectory notes.
- **Theme extraction** — thematic threads: name, controlling idea, development arc, vehicles, resolution, cross-thread relationships. Proposes consolidations where threads overlap.

Outputs save to `reference/`. A compression sub-agent then receives the three reference files plus the chapter index and produces bible-format entries pre-distributed by chapter number. The main context merges these without reading the full reference files.

**Pass 3 — Arc synthesis.** A single sub-agent receives the full manuscript and the `[char]` and `[arc]` entries from Pass 1. It produces one arc paragraph per major character, proposed not asserted. The user confirms; accepted arcs become author-protected and guard comments are emitted.

### Post-analysis

The assembled bible enters Plan mode for review, theme curation, and refinement.

---

## Mode: Plan

The bible is created or edited interactively. Same mode whether starting empty or revising.

**Construction order (empty bible):** Book Metadata → Character Registry → Chapter Inventory (chapter by chapter, summaries first, then logs). Echo, motif, and theme entries are optional during construction; they can be planned up front or left to emerge during writing.

**Free-form editing (populated bible):** Restructure chapters, adjust operational fields, introduce or remove elements, shift events, strengthen causation. Every edit applies the Editing Rules.

**Batch review.** "Review the story" reads all summaries in sequence and flags missing want/obstacle, episodic joints ("and then"), flat stakes, passive agency, unresolved threads. Book-level diagnostics run at the same time: controlling idea presence, antagonist worthiness, earned resolution, theme dramatized through action.

---

## Mode: Author

**The tool does not write chapters.** Writing is `writer.py`'s job. In Author mode, the Novelist's role is to invoke the Python program with the right arguments and interpret what comes back; it does not assemble writer prompts, inject context, manage retries, or produce prose.

- `"Write the book."` — invoke `writer.py <bible>`.
- `"Write chapter N."` — invoke `writer.py <bible> --chapter N`.
- `"Continue."` — append a new chapter entry to the Chapter Inventory (applying Editing Rules), then invoke `writer.py <bible> --chapter N` for the new chapter.
- `"Revise chapter N."` — delete `chapters/ch-NN.md` if present, then invoke `writer.py <bible> --chapter N`.
- `"Check continuity."` — read-only review. A sub-agent reads the last-written chapter's prose plus the corresponding bible block and reports deviations. No prose is emitted; any bible adjustments follow the Editing Rules.

Chapter files land under `chapters/` per the Book Directory Layout. The writer does not modify the bible. Any bible changes are made by the Novelist outside the writing pass and follow the Editing Rules.

---

## Witness Sub-Agent

Invoked by `"Add witness to chapter N."` This is a bible-editing task, not a writing task. It produces `[witness]` log entries for the chapter's inventory.

**Injected context:**

1. Chapter N's summary and log from the bible
2. Character Registry entries for anyone named in the log (Arc fields included)
3. Book Metadata: POV convention, register baseline, tense, Witness constraint, plus Density / Body-cost bullets if present
4. Optional: chapter N's prose — supply when checking an existing draft; omit when planning ahead of a write

**Task.** Identify the beat(s) that satisfy the Witness constraint. If prose was supplied, anchor each beat to what is on the page; otherwise describe the intended beat precisely enough for a later write or revision.

**Output.** Numbered proposals. Each states its placement by **log order** (e.g. "after the `[event]` describing X, before `[arc]` for Y" — never by manuscript line number). Approved lines merge into the chapter log at the stated positions; the sync rule then applies. Witness lines are operational.

---

## Assembly

`"Assemble."` concatenates chapter files into `manuscript.md` with `## Chapter N: Title` headings and `---` scene breaks. Compatible with downstream tooling (e.g. `bookmaker.py`) for PDF generation.

---

## License

All content in this file is dedicated to the public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
