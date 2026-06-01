# The Audit

A bible-only diagnostic that walks every chapter block in sequence and reports what's missing, broken, or thin. No prose is read. No prose is written. The audit operates on the specification, not the manuscript.

The Audit answers one question per chapter: does this bible block give the writer enough — and the right things — to produce the chapter the book needs? If yes, it moves on. If no, it says what's missing and waits for instruction.

<img src="https://raw.githubusercontent.com/cppalliance/tools-public/master/images/audit.png" alt="The Audit" width="100%">

---

## Invocation

```
"Audit the bible."
"Audit the bible for [book]."
"Audit chapters N-M."
"Audit chapter N."
```

The book context is established at first invocation or inherited from the current Novelist session.

---

## Input Assembly

Before the first chapter, the tool loads and holds for the duration of the audit:

1. **Book Metadata** — all fields, especially Target word count, POV convention, Tense, Register baseline, and every inline constraint (Body-cost, Density, Witness, and any additional bullets).
2. **Character Registry** — full entries for all characters. Loaded once; individual entries are consulted per chapter as needed.
3. **Thematic Threads** — controlling ideas and any drafting constraints.
4. **Offcuts file** — if `.offcuts.md` exists in the book directory, load it. Offcuts are candidates for density enrichment when a chapter is thin.

No pen files. No prose. No sub-agents. The audit reads the bible and the offcuts; everything else is out of scope.

---

## Per-Chapter Diagnostic

For each chapter, the tool reads the bible block (header, POV line, summary, log, any attached notes or draft archive) and runs five checks.

### Check 1: Density

Does the log give the writer enough material to earn the `Target:` word count on the POV line?

Count the load-bearing entries: `[event]`, `[sense]`, `[witness]`, `[arc]`, `[echo]`, `[motif]` deployments, `[char]` introductions with substance. Compare against the target. A chapter at ~3,000 words needs roughly 8-12 load-bearing entries; scale proportionally. Draft archive entries and `[prose]` lines are available material but do not count toward density — they are options, not assignments.

If the chapter is thin, check the offcuts file for material that could live here. Name the specific offcut if one fits.

Finding tag: `[density]`

### Check 2: Structure

Does the summary paragraph carry:

- **Want** — what the POV character is trying to do.
- **Obstacle** — what prevents them.
- **Choice** — what they decide.
- **Stakes** — what happens if they fail or succeed.
- **Causal bridge** — a therefore/but connecting this chapter's ending to the next chapter's beginning.

Each element is binary: present or absent. A weak but present element is not a finding. A missing element is.

Finding tag: `[structure]`

### Check 3: Constraint Compliance

Check every project-level constraint declared in Book Metadata against this chapter's log. Read the metadata bullets -- any bullet that states a requirement or budget is a constraint. Common patterns:

- **Witness constraint** — at least one `[witness N]` entry per chapter. A chapter with zero witness entries is a finding.
- **Density constraint** — the log should show distinguishable load-bearing and connective beats (a `[density]` entry specifying full-render vs thin-render). A log where every entry carries equal weight (uniformly dense or uniformly thin) is a finding.
- **Any additional constraints** declared in Book Metadata (e.g. body-cost budgets, register restrictions, naming rules) are checked by the same logic: does the log contain entries that satisfy the constraint? Name the constraint from the metadata; do not assume Papermancer-specific terms apply to other books.

Finding tag: `[witness]`, `[density-constraint]`, or the constraint's own name from Book Metadata.

### Check 4: Continuity

- Does the chapter's opening state inherit from the prior chapter's ending state?
- Does the chapter's ending hand off cleanly to the next chapter's summary?
- Are first appearances correctly flagged as introductions (`[char] name -- intro` or equivalent)?
- Do motif and echo sequence numbers follow from prior chapters? (e.g., if the prior chapter had `[motif 3/9] chair`, this chapter's chair entry should be `4/9` or higher, not `3/9` again.)

Finding tag: `[continuity]`

### Check 5: Schema

- POV line present with all three fields (`POV:`, `Register:`, `Target:`).
- Every log entry has a `[tag]` bracket.
- Witness entries are numbered (`[witness 1]`, `[witness 2]`). Bare `[witness]` without a number is a finding.
- Echo and motif entries have sequence numbers (`K/N`).
- No stale refactor markers (`MOVED TO CH N`, `SEE CH N`, `-- relocated`). If an element moved, it should be deleted from the source — not tombstoned.
- No orphaned references (a `[vocab]` entry that names a concept introduced in a different chapter without flagging the dependency).

Finding tag: `[schema]`

---

## Output Per Chapter

Problems only. If a chapter is clean, the output is:

**Ch N: Title** — clean.

If findings exist:

**Ch N: Title** — [verdict: minor gaps / material gaps].

Numbered findings follow, each tagged and each with a specific suggestion:

1. `[density]` Log has 5 load-bearing entries for a 4,800-word target. Offcut "scrap aluminum / an hour with a vise" fits the mirror motif here. Add a `[sense]` for the supply-point pickup and a `[motif]` for the mirror.
2. `[schema]` Bare `[witness]` at line 524. Number to `[witness 1]`.
3. `[structure]` No causal bridge to Ch N+1. Add a therefore/but sentence to the summary closing.

No commentary on what works. No alternative phrasings. No preference-level notes. Findings only, then stop.

---

## Sequence and Flow Control

The audit walks chapters in order, one at a time. After each chapter's report, the tool stops and waits for instruction:

- **next** — move to the next chapter.
- **fix** — apply the approved fix(es) to the bible, then resume the audit at the next chapter.
- **defer** — record the findings in-chat and move on; batch fixes later.
- **skip** — skip this chapter entirely.
- **stop** — end the audit.

If the user says "fix," the tool edits the bible following the Novelist's Editing Rules (match the schema, respect the Protection Model, keep related elements in sync, refuse rather than break). Author-protected fields (character Arc, Thematic Threads, Book Metadata) are never edited — if a finding touches a protected field, it is surfaced as a question, not a fix.

After a fix, the tool confirms what changed and resumes at the next chapter.

---

## Confidence Gate

When proposing a finding, the tool applies a confidence check: is this finding grounded in a specific rule (schema, constraint, structural requirement), or is it a judgment call?

- **Rule-grounded findings** are reported directly.
- **Judgment calls** (e.g., "this chapter might benefit from an arc beat") are flagged with their confidence level and the reasoning. If confidence is medium-low or lower, the tool says so and lets the author decide rather than asserting the finding.

The tool does not invent problems to justify its existence. A clean chapter is a clean chapter.

---

## License

All content in this file is dedicated to the public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
