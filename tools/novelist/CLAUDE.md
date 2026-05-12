# CLAUDE.md — Novelist Tools

Rules for any AI agent editing a tool in this directory.

## The Cardinal Rule

**Any change to any tool in this directory must be reflected in every other tool it interacts with.** The Novelist is a coupled system. The Python execution engine (`writer.py`) and the Markdown prompt tools (`novelist.md`, `critic.md`, `review.md`, `edit.md`) share protocols defined jointly by the story bible and the pen file: log entry types, device budgets, addendum rules, the review rubric, the output format contract, the on-disk layout. A protocol change on one side without the matching update on the other is silent — the code keeps running, the prompts keep rendering, and the pipeline degrades in ways that only surface chapters later.

If your change touches a shared protocol, update every consumer of that protocol in the same commit, or do not make the change.

## The Tools

```
tools/novelist/
  novelist.md              orchestrating prompt (Analyze, Plan, Author modes)
  writer.py                Python execution engine (Author mode runs this)
  critic.md                book-level review (8 phases, 4 pillars)
  review.md                per-chapter pass/fail (Story, Craft, Trust)
  edit.md                  tightener (contains its own review + edit loop)
  revise.md                AI-tell detector and tightener (prose-only, no bible/pen)
  audit.md                 bible-only diagnostic (density, structure, constraints, continuity, schema)
  lib/
    bible.py               bible parser, dataclasses, JSON serializer
  pen/                     shared voice specifications
    pen-of-william-gibson.md
  books/<book>/           per-book artifacts
    story-bible.md         structural specification
    pen-papermancer.md     per-book rules
    chapters/
    manuscript.md
    writer.log

tools-public/tools/novelist/
  workshop.md              interactive sentence-level workshop (B-plus flags, author-driven revision)
```

Shared pen files live in `pen/` and are referenced by bare filename in a book's `Pen files:` metadata. Per-book rules (pen-papermancer.md, story bible, chapters) live under `books/<book>/`.

## Coupling Map

For each class of change, these are the tools that must be updated together. If your edit fits one of these classes, visit every listed file.

**Bible log entry types** (adding a new `[tag]`, changing an existing tag's schema):
- `lib/bible.py` — LOG_ENTRY_RE and the parser state machine
- `novelist.md` — bible specification and the Log-entry glossary
- `critic.md` — whatever sub-agent consumes bible logs
- `review.md` — Story pass uses log entries
- `edit.md` — Story pass uses log entries (inherits review)
- every existing bible using the changed tag

**Bible structure** (dataclasses, character field parsing, JSON serialization):
- `lib/bible.py` is the single source of truth. `Bible`, `Chapter`, `LogEntry`, `Character` dataclasses; `parse_bible`; `parse_character_fields`; `to_dict`.
- `writer.py` imports from `lib.bible`; any consumer that reads a parsed Bible should also import from there.
- Adding a new field to `Character` or `Chapter` means updating any tool that reads them (currently `writer.py`'s `extract_characters` reads `Character.raw`).

**Parse error handling** (`BibleParseError` class, what raises vs. what permissive paths preserve):
- `lib/bible.py` raises `BibleParseError(line_num, line_text, message)` on malformed content. Callers must catch this exception and render it for the user before exiting.
- Currently `writer.py` is the only caller with such a handler. Adding a new tool that parses bibles requires a matching error-handler block.
- Changes to what counts as a parse error (e.g., adding a new strict rule) must be documented here and reflected in every caller's display.

**Pen path resolution or pen-file layout** (where pen files live on disk, how bare vs explicit paths resolve):
- `writer.py` — the `pen_paths_raw` loop in `main()`
- `novelist.md` — bible metadata schema
- `review.md` — Input Assembly pen-loading paragraph
- `edit.md` — Input Assembly pen-loading paragraph
- `workshop.md` (tools-public) — Phase 0 pen-path resolution
- every existing bible's `Pen files:` line

**Pen file device budgets** (new move, changed allocation, new register, new emotional variant, new warm-mode override):
- the pen file itself
- `review.md` — Craft pass enforces budgets
- `edit.md` — Craft pass and Edit tier system
- existing per-book rules if the budget naming overlaps

**Per-book rule** (new NEVER / budget in `books/<book>/pen-papermancer.md`):
- `review.md` — the pass that checks this rule class
- `edit.md` — the pass plus tier assignment

**Review rubric** (three-pass structure, new check type, changed violation format):
- `review.md`
- `edit.md` — contains its own review in Phase 1

**Bible schema or constraint changes** (new log tag, new metadata constraint, changed chapter-block structure):
- `novelist.md` — bible specification
- `audit.md` — schema check (Check 5), constraint compliance (Check 3), density heuristic (Check 1)
- `review.md` — Story pass uses log entries
- `edit.md` — Story pass uses log entries

**Writer prompt structure** (system prompt, anti-tic rules, mandatory-line contract, character injection rules):
- `writer.py` — `assemble_prompt()` and prompt-loading helpers
- `prompt/system.md`, `prompt/anti-tic.md` — externalized prompt text
- `novelist.md` — Author mode section

**Chapter filename convention or manuscript assembly** (chapter file naming, thinking-file sidecars, manuscript separator):
- `writer.py` — `assemble_manuscript()` and chapter write paths
- `novelist.md`
- any reader of chapter files (`critic.md`, `review.md`, `edit.md`, `workshop.md` in tools-public)

**Internal writer.py changes with no observable protocol shift** (thinking/effort cascade, retry policy, streaming event handling, logger setup):
- usually writer.py alone; no cross-tool update needed

**revise.md** (AI-tell detection and revision, prose-only):
- Self-contained. Does not read bible, pen, log entries, or any external artifact.
- Does not participate in the bible/pen coupling chain.
- The only shared protocol is the chapter file format (reads and writes `chapters/ch-NN.md`).
- Changes to revise.md's rule checklist do not require updates to any other tool.
- Changes to the chapter filename convention (see above) do require updating revise.md's file-resolution logic.

**workshop.md** (interactive sentence-level workshop, tools-public):
- Lives in `tools-public/tools/novelist/workshop.md`, not in this directory.
- Read-only consumer of bible and pen files. Does not modify bible, pen, or review rubric.
- Coupled to pen-path resolution (loads pen files for voice context) and chapter filename convention (reads chapter files, writes edits at session end).
- Does not consume bible log entry types, pen device budgets, review rubric, or bible structure protocols.
- Changes to workshop.md's pattern list or session protocol do not require updates to any other tool.

## Verification Checklist

After any change:

1. Identify which tools consume the changed protocol by consulting the coupling map.
2. Update every coupled tool in the same commit. If a tool is behind and you cannot update it now, open a TODO in the tool explicitly so the drift is visible.
3. If the change touches the generation pipeline, run `python writer.py <path-to-bible> --dry-run --chapter N` to confirm the prompt still assembles.
4. If the change touches bible format, grep every existing bible for the affected field (`rg "<field>:" tools/novelist/books/`) and update or migrate as needed.

## Notes

- The bible protects author-authored fields (character arcs, thematic controlling ideas). Never rewrite them without explicit human permission. Chapter summaries and logs are operational and freely revisable with approval.
- **No refactor notes in the bible.** When an element moves between chapters (a vocab entry, an event, a draft line), delete it from the old location. Do not leave behind markers like `MOVED TO CH N`, `SEE CH N`, or `-- relocated`. The bible is a living specification consumed by the writer; stale markers confuse the prompt assembler and waste context. If the move needs a coordination note (e.g., "coordinate clanker placement between Ch 1 and Ch 2"), put it in the destination chapter's log, not as a tombstone in the source.
- The pen file itself is never modified by the pipeline. The per-book rules file (pen-papermancer.md) is author-maintained and also never auto-rewritten.
- `writer.log` accumulates run history in INFO/WARNING/ERROR. All progress messages flow through it via `status()` at line 608 of writer.py.
- Shared pen files live in `pen/`. Adding a new voice means adding a new file there, not modifying an existing one.
- **Bible round-trip fidelity.** `lib.bible.parse_bible()` must produce Python data structures that preserve the bible's content byte-exactly. Log entry lines, character field values, chapter summaries, metadata values, and thematic threads are stored verbatim (either in dedicated fields or as `.raw` strings on their dataclasses). Cosmetic whitespace (extra blank lines, trailing whitespace) is not preserved. When adding new parseable content to the bible format, the parser must preserve either a `raw` field or a fully reversible structured representation so the round-trip contract holds. `to_dict()` (the JSON serializer) inherits this fidelity by walking the dataclasses; it adds nothing and drops nothing.
- **Strict-parse error contract.** `parse_bible()` raises `BibleParseError(line_num, line_text, message)` on any malformed content. Callers must catch this exception and display the line number, offending line text, and problem message in a user-readable form before exiting. Permissive paths (unknown log tags, ad-hoc character fields, extra metadata keys, HTML comments, `---` separators) do NOT raise — the grammar is open in those places by design. Adding a new strict-parse rule means updating both the parser and every caller's error-handling block.
- **Debug flag.** `python writer.py <bible> --dump-json [PATH]` serializes the parsed bible to JSON for debugging. Not a production flag; not integrated into regular runs.
- **The .md files in this directory are tools, not reference documentation.** `novelist.md`, `critic.md`, `review.md`, `edit.md`, and `revise.md` are prompts that Cursor agents execute. Their purpose is to help the author do a job — edit the bible (novelist), review the book (critic), check a chapter (review), tighten a chapter (edit), detect and fix AI tells (revise). They describe the schema the agent must produce and the rules the agent must follow, not the parser's implementation. Parser internals (class names like `BibleParseError`, `Character.raw`, `LogEntry.entry_type`, module paths like `lib/bible.py`, serializer details, round-trip contracts, debug flags) belong in this CLAUDE.md and in `lib/bible.py` docstrings. Do not put parser-speak into the tool .md files; if a sentence would only make sense to someone who has read the Python source, it does not belong there.
