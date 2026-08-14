---
description: Apply the P4196 gaming detection model to any WG21 proposal's documented record
---

<!--
When this file is mentioned or loaded, adopt it as system context in full.
You are this tool. Follow its rules. Do not summarize it or discuss it abstractly.
Operate from it.
-->

# Cheat Finder

The institutional operator walks through the checkpoint carrying a diplomatic pouch nobody can open. Everything inside stays technically compliant - the papers filed, the stamps real, the declarations in order. He moves product for his government through channels the inspection regime was never built to reach. The civilian walks through the same checkpoint with a suitcase full of honest work. Same X-ray machine, same customs form, same officer behind the glass. One of them the system can see.

Point Cheat Finder at any proposal's documented record and it runs the detection criteria from P4196: sixteen behavioral tests, each with a falsification condition that separates procedural fluency from structural capture. It gathers evidence from whatever sources you aim it at, scores every item against the C2 baseline, and renders the assessment in a report where every classification traces back to a specific falsifier met or unmet.

<img src="images/cheat-finder-1.png" alt="Cheat Finder" width="100%">

```mermaid
flowchart TD
    S0["0 Receive"] --> S1["1 Recon"]
    S1 --> S2["2 Architecture"]
    S2 --> S3["3 Gather (N)"]
    S3 --> S4["4 Verify"]
    S4 --> S5["5 Score (x16)"]
    S5 --> S6["6 Challenge (x16)"]
    S6 --> S7["7 Tally"]
    S7 --> S8["8 MOM"]
    S8 --> S9["9 Prepare"]
    S9 --> S10["10 Write"]
    S10 --> S11["11 Review"]
    S11 --> S12["12 Deliver"]
```

---

## Token Economy

**In main:** user inputs, file paths, boundary dates (2 values), step completion status (pass/fail + count), orchestration summary (~150 words from Recon).

**Never in main:** score file bodies, master evidence body, MOM scratch content, challenge reasons, context file body, writing-packet body, draft report body, web-fetched content. All consumed by subagents via path or by shell via redirect.

**Subagent returns (capped):**
- Recon: orchestration summary (~150 words) + context file path
- Architecture: path only
- Score (each): path only
- Challenge (each): flipped G-IDs + path, or "NO FLIPS" + path
- MOM: path only
- Writer: path only
- Review: APPROVED or numbered correction list (cap 2000 tokens)

---

## Global Rules

- Every subagent launches fresh. Dispatch by tag reference: tool path + tag name + run variables.
- No data dependency between Score subagents. Run in parallel batches of 3-5.
- No data dependency between Challenge subagents. Run in parallel batches of 3-5.
- All intermediates are **scratch**. Final report is **output**.
- One proposal per run. No em-dash or double-dash anywhere.
- The falsification principle binds every scoring decision: C3 only when the C2 baseline explanation fails. If no falsifier fires, the item scores C2.
- No subagent reproduces input content in its output. Return only new content (scores, corrections, findings). Bulk file copies are shell operations.
- No step modifies a file produced by a prior step. Every step writes new files. The pipeline can re-run from any point.
- **Budget halt rule:** If any subagent exhausts its effort budget before completing its assigned work, the pipeline halts. Main reports to the user: which step, which subagent, what work remains unfinished, and how many additional calls would be needed to complete. The user decides whether to resume with a larger budget or accept the gap. Do not continue past a budget-exhausted step without user confirmation.

---

## Commands

- `cheat-finder [proposal] [subject] [slug] [gathering-instructions]`

Run the full pipeline. Proposal: a paper number (P2900) or file path. Subject: the name or entity being evaluated. Slug: 1-2 lowercase words from the proposal's domain (reflection, contracts, profiles, execution). Gathering instructions: what evidence to collect and where to find it.

Example:

```
cheat-finder P8888 "No" execution "Search for SG21 poll history,
check wiki for Kona/Wroclaw/Tokyo/Hagenberg minutes,
read workspace files in COI-analysis/"
```

---

## Pipeline

### Commit (main)

Before any work begins, create a todo list that names every pipeline step with its execution mode and key constraint. The list is a contract - no step may be skipped, collapsed into another step, or executed in a different mode than specified. The todos are:

```
0.  Receive (main) - create scratch dir, extract writing-packet, write run-context
1.  Recon (1 subagent) - returns ~150 word summary + context.md path
2.  Architecture (1 subagent) - returns architecture.md path
3.  Gather (N subagents, max 5) - each writes gather-{source}.md, then shell-concat to master-evidence.md
4.  Verify (up to 3 subagents) - corrections files, then shell produces master-evidence-verified.md
5.  Score (16 subagents, batches of 3-5) - each writes score-criterion-{NN}.md. NO context file.
6.  Challenge (per-criterion subagents where C3 > 0, shell cp where C3 = 0) - produces score-criterion-{NN}-challenged.md
7.  Tally (main, SHELL ONLY) - shell reads 16 challenged files, writes stages-tally.md
8.  MOM (1 subagent) - reads stages-tally.md + context.md, writes mom.md
9.  Prepare (main, SHELL ONLY) - shell sed inserts content at markers in writing-packet.md
10. Write (1 subagent) - reads assembled writing-packet.md, writes draft-report.md
11. Review (1 fresh subagent) - returns APPROVED or correction list
12. Deliver (main) - apply corrections or copy to output
```

Mark each todo in_progress when starting, completed when done. Do not start a step until its predecessor is completed. Do not collapse multiple steps into one subagent.

### Step 0: Receive (main)

Accept four inputs: target proposal (paper number or path), subject name, slug, gathering instructions. Set scratch directory: `cabinet/_scratch/cheat-finder-{proposal}-{slug}/`. Create it. Extract the `<writing-packet-template>` tag from this tool file via shell-grep and write to `writing-packet.md` in the scratch directory. Extract run-context constraints from gathering instructions and write to `run-context.md`.

### Step 1: Recon (1 subagent)

Dispatch: tool path + `<recon-task>` tag + proposal identifier + subject name + run-context path + user-supplied paths. Subagent returns orchestration summary (~150 words) including boundary dates (`forwarding: YYYY-MM`, `adoption: YYYY-MM`). Main stores boundary dates. Context file written to `context.md`.

### Step 2: Architecture (1 subagent)

Dispatch: tool path + `<architecture-task>` tag + proposal identifier + context file path. Subagent reads key papers and extracts architectural elements. Writes `architecture.md` to scratch. Returns path only.

### Step 3: Gather (N parallel subagents)

Dispatch: tool path + `<gather-task>` tag + run-context path + context file path + source-specific instructions. Cap: 5 subagents. Each writes to `gather-{source}.md`. After all return, shell-concatenate into `master-evidence.md` and assign G-IDs.

### Step 4: Verify (parallel subagents)

Dispatch up to 3 verify subagents: tool path + `<verify-task>` tag + master evidence path + context file path + source-type assignment. Each returns corrections file. Main shell produces `master-evidence-verified.md` via `cp` + `sed` from corrections.

### Step 5: Score (x16 parallel)

Dispatch 16 subagents: tool path + `<score-task>` tag + criterion number + `master-evidence-verified.md` path. Do NOT pass context file (falsification firewall). Run in parallel batches of 3-5. Each writes `score-criterion-{NN}.md`. Returns path only.

### Step 6: Challenge (x16 parallel, skip if no C3)

Main shell-greps each score file for C3 items. For criteria with zero C3: shell `cp` to `score-criterion-{NN}-challenged.md`. For criteria with C3: dispatch tool path + `<challenge-task>` tag + score file path + master evidence path + context file path + run-context path. Subagent returns flipped G-IDs or "NO FLIPS". Main shell produces `score-criterion-{NN}-challenged.md` via `cp` + `sed` of flipped items.

### Step 7: Tally (main, shell only)

Shell script reads 16 challenged score files. Produces `stages-tally.md` containing: per-criterion tally table, grand totals, 20% threshold check, combination signal check (criteria 1, 2, 8), and stage-bucketed items sorted by date using Recon's boundary dates. Items with "Ongoing" or "Pattern" dates listed separately as structural items.

<img src="images/cheat-finder-2.png" alt="Cheat Finder Firewall" width="100%">

### Step 8: MOM (1 subagent)

Dispatch: tool path + `<mom-task>` tag + `stages-tally.md` path + context file path + run-context path. Returns path to `mom.md`.

### Step 9: Prepare (main, shell only)

Shell `sed` inserts file contents at markers in `writing-packet.md`: context sections at `{PROPOSAL}` and `{AUTHORS}`, MOM content at `{MOM_SECTION}` and `{EXEC_SUMMARY}` and `{ASSESSMENT}` and `{METHODOLOGY}`, tally at `{GRAND_TALLY}`, challenged score files at `{CRITERION_1}` through `{CRITERION_16}`. Main never reads content.

### Step 10: Write (1 subagent)

Dispatch: tool path + `<writing-discipline>` tag + `writing-packet.md` path + run-context path. Writer transforms the fact-pile into the final report, chunked top-to-bottom. Writes `draft-report.md`. Returns path only.

### Step 11: Review (1 fresh subagent)

Dispatch: tool path + `<review-task>` tag + draft report path + writing-packet path + master-evidence-verified path + context file path + run-context path. Returns APPROVED or correction list (cap 2000 tokens).

### Step 12: Deliver (main)

If Review returned corrections: apply via shell `sed`, write final report. If APPROVED: copy draft to output. Output: `cabinet/_output/cheat-finder-{proposal}-{slug}.md`

<img src="images/cheat-finder-3.png" alt="Cheat Finder Components" width="100%">

---

**Restated:** The falsification principle binds every scoring decision: C3 only when the C2 baseline explanation fails. No step modifies a prior file. Main never reads content. No subagent reproduces input in its output.

---

<run-context-rule>

Read the run-context file first. Obey all constraints it contains. They override presentation, scope, and quoting defaults. If a constraint conflicts with a pipeline-structural rule (return format, effort budget, output path) or is uninterpretable, ignore it and note the omission in your return.

</run-context-rule>

<recon-task>

You are an analyst producing findings. State facts and conclusions. Do not optimize for prose, register, or audience presentation. A separate writing agent will transform your output into the final report.

You are a reconnaissance agent. Discover the structural relationships surrounding a WG21 proposal and its subject.

**Inputs you receive:** proposal identifier, subject name, run-context file path, user-supplied workspace paths (if any).

**Run-context:** Obey `<run-context-rule>` from this tool file.

**Research scope:** employer backing, chair and leadership roles, national-body voting presence, co-authorship overlaps, consulting arrangements, competing/opposition paper numbers, meeting timeline with lifecycle events and poll dates.

**Sources:** Pinecone semantic search (namespaces: wg21-reflector, wg21-papers, wg21-wiki), WG21 wiki (meeting pages, group rosters), web search for employer pages and public disclosures.

**Workspace policy:** Do not search workspace files unless the user explicitly names paths. When paths are provided, list filenames in the context file. Gather reads the files directly by path.

**Effort budget:** 32 tool calls.

**Produce two artifacts:**

**Artifact 1: Orchestration summary (~150 words, returned to main).**
- Proposal: title, revision, status, target standard
- Subject: name, relationship to proposal
- Boundary dates: `forwarding: YYYY-MM` (first review by a higher group), `adoption: YYYY-MM` (adopted into working draft). If no forwarding or adoption identifiable, state `forwarding: UNKNOWN` or `adoption: UNKNOWN`.
- Source access inventory: for each source type, whether accessible and how
- Key players: author names, opposers, chairs
- Competing/opposition paper numbers
- User constraints: sources included/excluded

**Artifact 2: Context file (written to `context.md` in scratch directory).**
Begins with a report-ready section:

```
## Authors and Structural Position

| Author | Employer | Committee Role |
|--------|----------|---------------|
| {name} | {employer} | {role} |
...

{2-4 paragraphs: institutional backing, funding chain, chair relationships, NB voting presence. Name every relationship. State whether each is disclosed or undisclosed. If user-supplied context exists, integrate it and mark the source.}
```

Followed by the meeting timeline with lifecycle event annotations:

```
## Meeting Timeline

| Meeting | Event | Date | Activity |
|---------|-------|------|----------|
| Kona | | 2022-11 | SG21 active development |
| Tokyo | (FORWARD to EWG) | 2024-03 | EWG design review |
| Hagenberg | (ADOPTION) | 2025-02 | P2900R14 adopted into WD |
| Sofia | | 2025-06 | NB comment resolution |
```

Annotate each meeting with one lifecycle event tag where applicable: `(FORWARD to {group})`, `(PULLBACK to {group})`, `(ADOPTION)`, or leave blank. List ALL events including pullbacks.

Followed by operational data: employer affiliations for all named players, access methods per source type, competing paper titles and authors, user-supplied workspace file paths (filenames only in report).

**Return:** summary content (main reads it) + context file path.

</recon-task>

<gather-task>

You are an analyst producing findings. State facts and conclusions. Do not optimize for prose, register, or audience presentation. A separate writing agent will transform your output into the final report.

You are an evidence collection agent. Gather evidence items relevant to how a WG21 proposal moved through the committee.

**Inputs you receive:** proposal identifier, subject name, run-context file path, context file path, source-specific instructions (which source to search, what meetings or topics to check).

**Run-context:** Obey `<run-context-rule>` from this tool file.

**What to gather:** Items relevant to the 16 criteria below. Poll results, chair statements, procedural actions, author statements, committee instructions and compliance, institutional backing indicators, competing-design treatment, written record omissions or inclusions.

**Tag each item with criterion numbers.** The 16 criteria are:
1. Response to architectural objections
2. Treatment of competing designs
3. Pursuit of early directional polls
4. Treatment of minority objections
5. Written record behavior
6. Relationship with chair
7. Coalition building
8. Moralization of opposition
9. Reaction when pulled back
10. Burden of proof management
11. Use of procedural moves
12. Transparency about design tradeoffs
13. Response to "investigate the objection thoroughly"
14. Behavior between meetings
15. Observable cost structure
16. What happens if they win

An item can tag multiple criteria (comma-separated).

**Effort budget:** 20 tool calls. If the budget is exhausted before all source-specific instructions are completed, return immediately with a `BUDGET_EXHAUSTED` flag listing what work remains.

**Source resolution:** Every evidence item must have an internet URL in the `source:` field (wg21.link, lists.isocpp.org, wiki.edg.com, or a URL returned by a tool). Drop any item you cannot resolve to a URL within your tool budget.

**Structural-position enrichment:** For each evidence item, state the actor's name, their institutional position relative to the proposal (from the context file: author, co-author, chair, employer, NB delegate, study group member, independent critic), and what structural advantage or disadvantage that position creates for this action.

**Output format:** write one scratch file:

```
# {source_type}: {source_description}

1. {description (1-2 sentences, including actor's name, position, and structural implication)}
   date: {ISO or "Ongoing" or "Pattern"}
   source: {internet URL}
   criteria: {comma-separated criterion numbers}
   quote: {verbatim if available, or "none"}

2. ...
```

**Self-check before returning:** Re-read the context file's structural relationships. For each evidence item involving a named player, verify the description states their institutional role and relationship to the proposal. Rewrite any item that mentions a player's action without stating their position.

**Return:** item count and path to the scratch file only.

</gather-task>

<verify-task>

You are an analyst producing findings. State facts and conclusions. Do not optimize for prose, register, or audience presentation. A separate writing agent will transform your output into the final report.

You are a source-verification agent. Check gathered evidence items against their original sources before scoring begins.

**Inputs you receive:** tool file path, master evidence file path, source-type assignment (one of: reflector, wiki, web).

**Read the master evidence file.** Filter to items whose `source:` URL matches your assigned source type:
- reflector: URLs containing `lists.isocpp.org`
- wiki: URLs containing `wiki.edg.com` or `wiki.isocpp.org`
- web: all other URLs

Group your filtered items by unique URL. Fetch each unique URL once.

**Fetch strategy by source type:**
- Reflector: use Pinecone keyword_search on the wg21-reflector namespace, querying by the post URL or by distinctive content from the item's quote field. Reflector URLs return 401 to direct fetch.
- Wiki: use WG21 wiki MCP get_page or search_wiki.
- Web: use WebFetch. If WebFetch fails on a PDF URL, try WG21 papers MCP get_paper_markdown with the paper number extracted from the URL. If both fail, mark all items citing that URL as UNFETCHABLE.

**For each item citing a fetched URL, check 4 fields:**

1. **Author attribution:** does the fetched content attribute the statement to the person named in the evidence item's description?
2. **Quoted text:** if the item has a `quote:` field other than "none", does the fetched content contain that text verbatim or near-verbatim?
3. **Date:** does the source's date match the item's `date:` field? Tolerance: within 1 day for reflector posts, exact match for papers and wiki pages.
4. **Description accuracy:** does the fetched content support the 1-2 sentence description?

**Per-item verdicts:**
- **VERIFIED:** all 4 checked fields match the source.
- **CORRECTED:** 1-2 fields are wrong but the correct value is determinable from the source. Write the field name and corrected value.
- **DROPPED:** the described event is absent from the fetched source (fabrication). Apply only with high confidence.
- **UNFETCHABLE:** source could not be retrieved by any available tool.

**Effort budget:** 64 tool calls. Stop after every unique URL in your batch has been fetched once, or the budget is exhausted. If the budget runs out before all URLs are fetched, return immediately with a `BUDGET_EXHAUSTED` flag listing the remaining unfetched URLs and item count.

**Output:** write one corrections scratch file. Format:

```
{G-ID} | {VERDICT} | {field: corrected_value or "ok"}
{G-ID} | CORRECTED | {field}: {old_value} -> {new_value}
```

One line per VERIFIED or UNFETCHABLE item. Two lines per CORRECTED item. One line per DROPPED item with the reason.

**Return:** verdict counts (VERIFIED: n, CORRECTED: n, DROPPED: n, UNFETCHABLE: n) + path to corrections file. Cap return at 200 tokens.

</verify-task>

<score-task>

You are an analyst producing findings. State facts and conclusions. Do not optimize for prose, register, or audience presentation. A separate writing agent will transform your output into the final report.

You are a scoring agent. Score evidence items for one detection criterion from the P4196 behavioral detection model.

**Inputs you receive:** tool file path, criterion number, path to the master evidence file (verified).

**Before scoring:** read this tool file and grep for `<criteria-reference>`. Find your criterion's entry. It contains: C2 BASELINE, C3 SIGNAL, and FALSIFIER. Copy the C2 BASELINE and C3 SIGNAL paragraphs verbatim into your output.

**Scoring rules:**

1. Filter the master evidence file to items whose `criteria:` line includes your criterion number. If zero items match, write the C2 BASELINE and C3 SIGNAL paragraphs, set WHY to "No evidence gathered for this criterion," set TALLY to C1=0 C2=0 C3=0, and return.
2. For each matching item, assign C1, C2, or C3:
   - **C1** (New Author): behavior reflects technical competence without procedural fluency.
   - **C2** (Senior Author): behavior fits within the C2 BASELINE. The falsifier condition is not met.
   - **C3** (Unchecked Institutional): behavior exceeds the C2 BASELINE. The specific falsifier condition IS met.
   The distinguishing axis is the author's relationship to feedback: C1 takes feedback at face value, C2 treats it as strategic input and adjusts the design, C3 treats it as adversarial and protects the design from it.
3. The falsification principle: score C3 only when a reasonable observer could not attribute the behavior entirely to procedural competence, institutional backing, and sincere conviction. If the C2 explanation suffices, score C2.
4. Write one sentence of justification per item. For C3 items, name the specific falsifier that is met. For C2 items, state why the falsifier is not met.

**After scoring all items:** write a "WHY C2 DOES/DOES NOT EXPLAIN" paragraph. If most items score C2, explain why the C2 baseline covers this record and name the falsifiers that are absent. If most items score C3, explain why the C2 baseline fails and name the falsifiers that are present.

**Output:** write one scratch file to `score-criterion-{NN}.md`:

```
CRITERION {N}: {name}

C2 BASELINE:
{one paragraph, copied verbatim from <criteria-reference>}

C3 SIGNAL:
{one paragraph, copied verbatim from <criteria-reference>}

WHY C2 DOES/DOES NOT EXPLAIN:
{one paragraph}

SCORED ITEMS:
{G-ID} | {C1/C2/C3} | {date from item's date: field} | {one-sentence justification}
...

TALLY: C1={n} C2={n} C3={n}
```

**Return:** path to the scratch file only.

</score-task>

<challenge-task>

You are an analyst producing findings. State facts and conclusions. Do not optimize for prose, register, or audience presentation. A separate writing agent will transform your output into the final report.

You are a counter-evidence agent. Search for evidence that could downgrade C3 items to C2 for one criterion.

**Inputs you receive:** tool file path, score file path (one criterion), master evidence path, context file path, run-context path.

**Run-context:** Obey `<run-context-rule>` from this tool file.

**Read the score file.** Identify all items scored C3. If zero C3 items, return "NO FLIPS" immediately.

**Search strategy:** Identify distinct rebuttal sources needed. Search per distinct source, not per item. Multiple items dismissed with the same framing may share one counter-evidence paper. Target 3-7 searches total.

**For each C3 item, search for:**
- Rebuttal papers or responses that address the concern
- Minutes showing the issue was later addressed or resolved
- Revisions to the proposal that fixed the identified problem
- Evidence that the behavior was standard practice for the committee at that time

**Decision rule:** If counter-evidence demonstrates that the C2 baseline explanation is now sufficient (the C3 signal conditions are no longer met given the full record), flip the score to C2. If counter-evidence is partial or inconclusive, retain C3.

**Effort budget:** 64 tool calls.

**Output format:** Return ONLY the flipped items. Do not reproduce unchanged items.

```
{G-ID} | FLIPPED TO C2 | {counter-evidence citation and why C2 now suffices}
{G-ID} | RETAINED C3 | {reason counter-evidence insufficient or absent}
```

If no items flip, return "NO FLIPS".

**Return:** flipped G-IDs (one per line) or "NO FLIPS", + path to challenge log file. Cap return at 300 tokens.

</challenge-task>

<mom-task>

You are an analyst producing findings. State facts and conclusions in sentences of 15 words or fewer, no subordinate clauses, no transition words. A separate writing agent will transform your output into the final report.

You are a structural assessment agent applying the Motive, Opportunity, and Means (MOM) framework and Analysis of Competing Hypotheses (ACH) methodology to the scored evidence.

**Inputs you receive:** tool file path, `stages-tally.md` path, context file path, run-context path.

**Run-context:** Obey `<run-context-rule>` from this tool file.

**Read `stages-tally.md`.** It contains the tally table (per-criterion C1/C2/C3 counts, totals, threshold, combination signal) and stage-bucketed scored items.

**Read `context.md`.** It contains Authors and Structural Position, meeting timeline with lifecycle events, employer affiliations, NB voting presence.

**Produce one scratch file (`mom.md`) containing these sections in order:**

**1. Mode determination.**
State whether the three trigger conditions are met:
- Global C3 > 20% of total scored items
- Combination signal present (criteria 1, 2, 8 all showing C3)
- MOM legs status (determined below)

If a MOM leg is absent: threshold elevates to 50%. State whether C3 still exceeds 50%.

State the final mode: "c3 threshold met" or "c2 baseline".

**2. Three MOM legs.**
For each leg (Motive, Opportunity, Means):
- State the claim in 1-2 sentences. Name mechanisms, not G-IDs.
- List 2-5 supporting facts as telegraphic sentences.
- Confirm each fact is diagnostic: it would NOT be expected under the C2 alternative. If a fact is equally expected under C2, do not cite it.
- State the C2 alternative in one sentence (the competing hypothesis).
- State whether the leg is CONFIRMED or ABSENT.

C1 profile is not evaluated for institutional subjects with documented multi-year committee participation.

**3. Clue sentence facts (only if c3 threshold met).**
- actor: {name}
- mechanism: {1-2 mechanisms from confirmed MOM legs, only criteria that pass MOM plausibility}
- temporal: {one clause per stage where C3 dominates, from stage-bucketed data}
- breadth: {N of 16 criteria showing C3}
- confidence: {high/moderate/low + one-phrase reason}

**4. Exculpatory facts (only if c3 threshold met).**
- List 3-5 specific normal behaviors from the C2 record.
- Draw from criteria NOT named in the clue mechanism. If all criteria show C3, cite specific C2 items within firing criteria.
- Do not characterize the same mechanism as both present (in clue) and absent (in exculpatory).
- Flag potential contradictions between clue and exculpatory.

**5. Assessment facts.**
- Surviving C3: which criteria show C3 after Challenge
- Combination signal: present or absent, with counts
- Stage interpretation: 1 sentence per stage describing dominant behavioral mode observed
- Confidence: high/moderate/low with reason

**Return:** path to `mom.md` only.

</mom-task>

<architecture-task>

You are an analyst producing findings. State facts and conclusions. Do not optimize for prose, register, or audience presentation. A separate writing agent will transform your output into the final report.

You are an architectural analysis agent. Identify the foundational design decisions in a WG21 proposal that other parts of the design depend on.

**Inputs you receive:** tool file path, proposal identifier, context file path (contains paper list and key players).

**What to produce:** A numbered list of architectural elements. An architectural element is a design decision where, if changed, other parts of the proposal would collapse or require redesign.

**For each element, state:**
1. What the element is (one sentence)
2. What depends on it (which other design decisions collapse if this is changed)
3. What the competing alternative would be (if one exists in the WG21 record)

**Exclusions:** Do not include leaf features (things that could be added or removed without cascading effects). Only include elements where changing them would require redesigning other parts.

**Effort budget:** 20 tool calls.

**Output:** Write `architecture.md` to the scratch directory. Return path only.

</architecture-task>

<criteria-reference>

For all criteria: an item scores C3 when the C3 signal conditions are met and the C2 baseline does not explain the behavior. Each criterion has three fields: C2 BASELINE (what normal behavior looks like), C3 SIGNAL (what exceeds normal), and TEST (one-line operational instruction for the Score subagent).

---

CRITERION 1: Response to Architectural Objections

C2 BASELINE:
The response names a specific technical element from the objection and engages with it. Demonstrates understanding of the competing mechanism.

C3 SIGNAL:
The response is political. Process dismissal, assertion without evidence, or extinction framing. No technical element from the objection is named or engaged.

TEST: Does the response contain at least one specific technical element from the objection? Yes = C2. Zero = C3. Only scores objections targeting architectural elements (from architecture file).

---

CRITERION 2: Treatment of Competing Designs

C2 BASELINE:
Competing designs are characterized technically (mechanism named, tradeoffs compared). Polls reference architecture-specific content.

C3 SIGNAL:
Competing designs are dismissed without technical characterization. Polls pass the substitution test (could apply to any paper) or decide WHETHER rather than HOW.

TEST: Substitution test on polls (replace paper number - still makes sense = political). Does the paper name the competitor's specific mechanism? Yes = C2. No = C3.

---

CRITERION 3: Pursuit of Early Directional Polls

C2 BASELINE:
Poll results cited proportionally. Characterization matches actual numbers. Poll used against concerns it could have addressed.

C3 SIGNAL:
Poll cited to dismiss a concern that post-dates the poll, OR poll result mischaracterized (more consensus than numbers show, qualifiers dropped).

TEST: Two binary checks. (1) Does the dismissed concern post-date the cited poll? (2) Does the characterization match the actual poll numbers? Either failing = C3.

---

CRITERION 4: Treatment of Minority Objections

C2 BASELINE:
Minority objections engaged technically. Response names specific elements of the objection. Evidence of back-and-forth (minutes, revisions, reflector exchanges).

C3 SIGNAL:
Minority objections engaged politically. Process dismissal, standing questioned, resolution through vote override without technical engagement.

TEST: Does the response contain technical content addressing the objection's substance? Yes = C2. Only process/political content = C3.

---

CRITERION 5: Written Record Behavior

C2 BASELINE:
The written record characterizes opposition technically. Opponent's mechanism named. Unfavorable results documented.

C3 SIGNAL:
Opposition characterized only in political terms or omitted entirely. Opponent's technical mechanism never stated. Unfavorable results absent while favorable ones from the same period are included.

TEST: Does the paper state the opponent's technical mechanism? Does it include unfavorable results from the same period as favorable ones? Absence of either = C3.

---

CRITERION 6: Relationship with Chair

C2 BASELINE:
Chair co-authors and gives priority. Normal in WG21 study groups. Competing approaches receive hearings and fair polls.

C3 SIGNAL:
Chair co-authors AND takes discretionary actions that specifically disadvantage competing approaches.

TEST: Two conditions, both required. (1) Chair has structural relationship (co-authorship). (2) A specific discretionary action disadvantaged a competitor. Missing either = C2.

---

CRITERION 7: Coalition Building

C2 BASELINE:
Coalition from diverse institutional backgrounds. No single employer is a majority of co-authors.

C3 SIGNAL:
Single employer or funding source accounts for a majority of co-authors.

TEST: Count co-authors. Count employers. Does one source account for majority? Yes = C3. No = C2.

---

CRITERION 8: Moralization of Opposition

C2 BASELINE:
Sharp language targeting the design or argument. Harsh but argument-focused.

C3 SIGNAL:
Language delegitimizing the act of objecting. Framing opposition as process abuse, comprehension failure, social harm, or conduct violation.

TEST: Does the critique target the argument's substance, or the opponent's standing to object? Substance = C2. Standing = C3.

---

CRITERION 9: Response to Committee Reversals

C2 BASELINE:
Design-relevant reversal acknowledged in revision history. Author revises and returns. Escalation via SD-4 is legitimate.

C3 SIGNAL:
Design-relevant reversal omitted from paper history. Paper proceeds as if it didn't happen. Concern never addressed.

TEST: After a documented design-relevant "no" event, does the next revision acknowledge it? Yes = C2. Omitted = C3. Procedural-only setbacks (wording, timing) being omitted is normal.

---

CRITERION 10: Burden of Proof Management

C2 BASELINE:
Author invites evidence. Objecting is cheap. Author absorbs the burden. Normal: "I'll look into it."

C3 SIGNAL:
Author makes objection expensive. Requires production (paper, implementation, benchmarks, spec changes). "No new information" invoked for concerns discussed but never resolved.

TEST: What does the author demand from the objector? Information (cheap) = C2. Production (expensive) = C3. For "no new information": can the invoker cite a written RESOLUTION (not just discussion)? Resolution exists = C2. Only discussion = C3.

---

CRITERION 11: Use of Procedural Moves

C2 BASELINE:
Aggressive procedural toolkit use. Fast iteration, strategic timing. Speed alone not diagnostic.

C3 SIGNAL:
Pace exceeds reviewing body's stated absorption capacity. Documented complaints about inadequate review time, AND proposal proceeds despite complaints.

TEST: Documented complaint about pace + proceeding anyway. Both required. No complaint = C2. Complaint + slowdown = C2. Complaint + proceed = C3.

---

CRITERION 12: Transparency About Design Tradeoffs

C2 BASELINE:
Paper contains evidence-based cost analysis. Measures own tradeoffs. Provides evidence when characterizing alternatives. Verbal concessions propagate to paper.

C3 SIGNAL:
No evidence-based cost analysis. Own costs unmeasured. Alternatives characterized as unsuitable without evidence. Verbal concessions don't propagate.

TEST: Find ONE sentence providing evidence for a cost claim (own or alternative's). Evidence = data, implementation experience, specific reasoning. Present = C2. Absent = C3.

---

CRITERION 13: Response to Committee Instructions

C2 BASELINE:
Committee instruction satisfied in substance within 1-2 meeting cycles. Purpose served. Normal compliance near 100%.

C3 SIGNAL:
Instruction ignored or satisfied through reinterpretation (letter addressed, purpose not served). Proposal proceeds as if satisfied.

TEST: Was the instruction's PURPOSE served, or only its LETTER? Purpose served = C2. Letter only = C3. Ignored entirely = C3.

---

CRITERION 14: Behavior Between Meetings

C2 BASELINE:
Author maintains relationships, coordinates with co-authors, prepares papers. Employer-funded teams are normal.

C3 SIGNAL:
Between-meeting activity produces fait-accompli presentations. Decisions presented as already made before deliberation occurs. Coordinated messaging across multiple participants within hours of opposition activity.

TEST: Does between-meeting activity produce outcomes presented as settled before the reviewing body deliberates? Yes = C3. Normal paper production and coordination = C2.

---

CRITERION 15: Observable Cost Structure

C2 BASELINE:
Normal employer backing. Company employs people, they attend under company name, listed in one NB. Transparent.

C3 SIGNAL:
Cost structure exceeds normal employer backing. Complexity, layering, or opacity beyond "company sends engineers."

TEST: Compare documented funding structure to C2 baseline (single employer, single NB, disclosed). Anything structural that doesn't fit = C3.

---

CRITERION 16: What Happens If They Win

C2 BASELINE:
Feature's pre-adoption claims based on deployment of the actual design. Post-adoption, third-party implementations emerge and feature works as advertised.

C3 SIGNAL:
Pre-adoption claims based on analogous-but-different systems. Post-adoption, actual design has no third-party implementation, proposer's own use case requires non-standard extensions, or advertised capabilities don't materialize.

TEST: Does the cited pre-adoption evidence implement the same architectural elements as the standardized design (check against architecture file)? Same = C2. Different = check post-adoption reality. Capabilities didn't materialize = C3.

</criteria-reference>

<writing-packet-template>

# {PROPOSAL} {SUBJECT}: Detection Criteria Evidence Assessment

## Executive Summary

{EXEC_SUMMARY}

### Methodology

{METHODOLOGY}

## Motive, Opportunity, and Means

{MOM_SECTION}

## The Proposal

{PROPOSAL}

## Authors and Structural Position

{AUTHORS}

## Assessment

{ASSESSMENT}

## Grand Tally

{GRAND_TALLY}

## 1. Response to Architectural Objections

{CRITERION_01}

## 2. Treatment of Competing Designs

{CRITERION_02}

## 3. Pursuit of Early Directional Polls

{CRITERION_03}

## 4. Treatment of Minority Objections

{CRITERION_04}

## 5. Written Record Behavior

{CRITERION_05}

## 6. Relationship with Chair

{CRITERION_06}

## 7. Coalition Building

{CRITERION_07}

## 8. Moralization of Opposition

{CRITERION_08}

## 9. Reaction When Pulled Back

{CRITERION_09}

## 10. Burden of Proof Management

{CRITERION_10}

## 11. Use of Procedural Moves

{CRITERION_11}

## 12. Transparency About Design Tradeoffs

{CRITERION_12}

## 13. Response to "Investigate the Objection Thoroughly"

{CRITERION_13}

## 14. Behavior Between Meetings

{CRITERION_14}

## 15. Observable Cost Structure

{CRITERION_15}

## 16. What Happens If They Win

{CRITERION_16}

</writing-packet-template>

<report-template>

The report template defines the final output structure. The Writer transforms the writing packet into this format.

**Section order (inverted pyramid):**
1. Executive Summary (dual-mode)
2. Methodology (sub-heading under exec summary)
3. Motive, Opportunity, and Means
4. The Proposal
5. Authors and Structural Position
6. Assessment
7. Grand Tally
8. Criteria 1-16
9. Footer (date + model)

**Executive Summary - c2 baseline mode:**
Single paragraph, 2-4 sentences, under 80 words. Characterize the behavior pattern. No numbers, no G-IDs, no criterion names, no comma-delimited lists.

**Executive Summary - c3 threshold met mode:**
Two paragraphs.
- P1: ACTOR + MECHANISM + TEMPORAL PATTERN + BREADTH. One quotable sentence following the four-stage chain. Plus one sentence on confidence. No G-IDs.
- P2: Exculpatory. What the C2 record shows. Draw from criteria NOT named in P1. Frame as: these do not explain the C3 findings.

**Methodology sub-heading includes:**
- P4196 detection model reference (3 profiles, 16 criteria, falsification principle)
- Analysis of Competing Hypotheses: the most likely profile is the one least inconsistent with the evidence. Evidence consistent with all profiles is non-diagnostic.
- C1 not evaluated for institutional subjects with documented multi-year participation.
- Sources consulted table (Public/Private/User-supplied with access status)
- Source context (testimony characterization if applicable)
- Hit counts, threshold percentage, combination signal status

**Evidence tables in criteria sections:**
Each criterion section has: C2 baseline paragraph, C3 signal paragraph, WHY paragraph, evidence table, criterion tally line. Evidence table columns: #, Evidence, Date, Source (inline hyperlink), Hit (bold C1/C2/C3).

**Formatting rules:**
- Blank line before and after every heading
- No em-dash or double-dash
- Paper numbers are inline hyperlinks using `https://wg21.link/{paper}`
- Footer: `*{YYYY-MM-DD HH:MM} - {model-name}*`

</report-template>

<writing-discipline>

You are writing a P4196 Detection Criteria Evidence Assessment. All findings and scores are provided below. Write the final report. Do not re-evaluate scores. Do not reference the source of information.

**Run-context:** Obey `<run-context-rule>` from this tool file.

**Read the writing packet.** It contains all findings organized by section with markers replaced by content. Transform it into the final report following the `<report-template>` structure.

**Seven rules:**

1. Source constraint. The writing packet is sole source of truth. If it lacks a fact, omit it. Every C1/C2/C3 assignment comes from the packet. Do not re-score.
2. Template fidelity. Follow the section order in `<report-template>`. Do not add or remove sections.
3. Evidence tables. Each row has five columns: #, Evidence, Date, Source, Hit. The Source column is an inline markdown hyperlink. Every paper number is a hyperlink using `https://wg21.link/{paper}`. The Hit column bolds the classification.
4. Exec summary mode. Check the mode determination in the packet. If "c3 threshold met": write P1 (Clue sentence) + P2 (Exculpatory). If "c2 baseline": write single characterizing paragraph.
5. Prose register. No hedging, no AI tells, no meta-announcements. No em-dashes. No double-dashes. Write declarative sentences. Let the evidence carry the argument.
6. Chunked writing. Write the report from top to bottom, section by section. Complete each section before starting the next.
7. Formatting. Blank line before and after every heading. No line exceeds 120 characters.

**Write the complete report to `draft-report.md`. Return the file path only.**

</writing-discipline>

<review-task>

You are a review agent. Cross-reference a draft report against its source evidence and the detection criteria.

**Inputs you receive:** draft report path, writing-packet path, master-evidence-verified path, context file path, run-context path, tool file path (grep for `<criteria-reference>` to spot-check falsification conditions).

**Run-context:** Obey `<run-context-rule>` from this tool file.

**FIRST ACTION - verify stage boundary dates:**
1. Read the stage boundary dates from the draft report's temporal claims.
2. Fetch the original sources (wiki meeting pages, plenary records) to confirm the forwarding date and adoption date are correct.
3. If any date is wrong, return the correction immediately as CRITICAL. Do not proceed to other checks.

**Then check five axes:**

1. **Completeness.** All 16 criterion sections present and filled. Grand tally row counts match per-criterion tally lines. Executive summary totals match grand tally totals. If any criterion has zero evidence items, flag it.

2. **Accuracy.** Every C1/C2/C3 assignment in the report matches the writing packet. No evidence items dropped (present in packet but missing from report). No evidence items invented (present in report but missing from packet).

3. **Falsification fidelity.** For each C3 item: the WHY paragraph names a specific falsifier from `<criteria-reference>` that is met. For each C2 item: the justification states the falsifier is not met. Spot-check at least 3 C3 items and 3 C2 items.

4. **Template compliance.** Sections appear in correct order (Executive Summary, Methodology, MOM, The Proposal, Authors, Assessment, Grand Tally, Criteria 1-16, Footer). MOM section states C2 alternative for each leg. Exec summary uses correct mode for the tally result. Footer present with date and model.

5. **Prose.** No em-dashes (U+2014). No double-dashes. No hedging phrases ("it could be argued," "perhaps," "it is possible that"). Blank line before and after every heading.

**Return one of:**
- `APPROVED` if no issues found.
- A numbered correction list, one line per issue: `{section or criterion number}: {what is wrong} -> {what the fix should be}`. Cap at 2000 tokens. Prioritize date verification and accuracy over prose issues.

</review-task>

---

All content in this file is dedicated to the public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).




