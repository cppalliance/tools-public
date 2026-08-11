---
description: Apply the D4196 gaming detection model to any WG21 proposal's documented record
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
    S0["0 Receive (main)"] --> S1["1 Profile + Gather (parallel)"]
    S1 --> S2["2 Score (parallel x16)"]
    S2 --> S3["3 Tally (main)"]
    S3 --> S4["4 Prepare (main + shell)"]
    S4 --> S5["5 Write (isolated subagent)"]
    S5 --> S6["6 Review (fresh subagent)"]
    S6 --> S7["7 Deliver (main)"]
```

---

## Token Economy

**In main:** user inputs, file paths, step completion status, tally line reads (grep output), review corrections (cap 2000 tokens).

**Never in main:** raw source material, profile prose body, master evidence body, score scratch file bodies, evidence packet body, evidence details body, writer's draft body. All consumed by path from subagents or read from file by the review subagent only.

The only large read in main: Step 7 (Deliver) when corrections exist. Bounded by report size (~500 lines).

---

## Global Rules

- Every subagent launches fresh. Dispatch by tag reference: tool path + tag name + run variables.
- No data dependency between Score subagents. Run in parallel batches of 3-5.
- All intermediates are **scratch**. Final report is **output**.
- One proposal per run. Single writer. No em-dash or double-dash anywhere.
- The falsification principle binds every scoring decision: C3 only when the C2 baseline explanation fails. If no falsifier fires, the item scores C2.

---

## Commands

- `cheat-finder [proposal] [subject] [gathering-instructions]`

Run the full pipeline. Proposal: a paper number (P2900) or file path. Subject: the name or entity being evaluated. Gathering instructions: what evidence to collect and where to find it.

Example:

```
cheat-finder P2900 Bloomberg "Search Pinecone for SG21 poll history,
check wiki for Kona/Wroclaw/Tokyo/Hagenberg minutes,
read workspace files in profiles-coalition/"
```

---

## Pipeline

### Step 0: Receive (main)

Accept three inputs: target proposal (paper number or path), subject name, gathering instructions. If the proposal is a file path, verify the file exists; if a paper number, accept as-is. Set scratch directory: `cabinet/_scratch/cheat-finder-{proposal}-{subject}/`. Create it.

Extract from the gathering instructions any instruction that would change how a subagent behaves (source restrictions, quoting rules, presentation preferences, testimony, institutional context). Write these to `cabinet/_scratch/cheat-finder-{proposal}-{subject}/run-context.md`. If no such instructions exist, write an empty file.

### Step 1: Profile + Gather (parallel)

Profile and Gather launch in parallel. No data dependency between them.

**Profile (1 subagent).** Dispatch: read this tool file, grep for `<profile-task>`, execute. Pass the proposal identifier, subject name, run-context file path, and any user-supplied institutional context extracted from the gathering instructions. Subagent writes one scratch file establishing the subject's structural position. Returns path only.

**Gather (N subagents).** Dispatch: read this tool file, grep for `<gather-task>`, execute. Pass the run-context file path along with source-specific instructions. Main decomposes the user's gathering instructions into source-specific tasks:

- Explicit source mentions spawn one subagent each ("search Pinecone" = 1, "check wiki" = 1, "read workspace files in X/" = 1).
- If the user gives no source specifics, default: one Pinecone subagent, one wiki subagent, one workspace subagent (if evidence directories exist).
- Cap: 5 Gather subagents per run.

Each subagent writes a scratch file of evidence items. Format:

```
# {source_type}: {source_description}

1. {description (1-2 sentences)}
   date: {ISO or "Ongoing" or "Pattern"}
   source: {internet URL - public or authenticated}
   criteria: {comma-separated criterion numbers 1-16}
   quote: {verbatim if available, or "none"}
```

Each subagent makes at most 5 tool calls. Returns count + path only.

After all Gather subagents return, shell-concatenate their scratch files into one master evidence file. Assign global IDs by prepending `G{n}.` to each item, sequential across all sources. These IDs are the stable references for Score subagents and the writer.

### Step 2: Score (parallel-capable, 16 subagents)

Dispatch: read this tool file, grep for `<score-task>`, execute. The task directs the subagent to also grep for `<criteria-reference>` and read its own criterion's entry.

Each subagent receives (via dispatched prompt): tool path, tag names, criterion number, path to the master evidence file. The subagent filters to evidence items tagged to its criterion number.

Run in parallel batches of 3-5 at main's discretion.

Each subagent writes a scratch file:

```
CRITERION {N}: {name}

C2 BASELINE:
{one paragraph, copied from <criteria-reference>}

C3 SIGNAL:
{one paragraph, copied from <criteria-reference>}

WHY C2 DOES/DOES NOT EXPLAIN:
{one paragraph, written by the subagent}

SCORED ITEMS:
{global_id} | {C1/C2/C3} | {one-sentence justification}
...

TALLY: C1={n} C2={n} C3={n}
```

Returns path only.

### Step 3: Tally (main)

Shell-grep the `TALLY:` line from each of the 16 score scratch files. Mechanical aggregation:

- Build the grand tally table (16 rows + totals).
- Check the combination signal: do criteria 1, 2, and 8 all have C3 hits? If yes, all three distinguishing markers are present simultaneously.
- Write one-sentence verdict for the Executive Summary.
- Write to a tally scratch file.

### Step 4: Prepare (main + shell)

The analytical firewall. All analysis is complete. This step assembles what the writer needs.

Write THREE scratch files:

**File 1: Evidence packet.** Shell-concatenate the profile scratch file, all 16 score scratch files, and the tally scratch file. Preserve heading lines for section boundaries. This file is the writer's sole source of truth.

**File 2: Evidence details.** Copy the master evidence file from Gather. Raw quotes, source citations, dates. The writer consults this when constructing evidence tables.

**File 3: Report template.** Read `<report-template>` from this tool file and write it to a scratch file, filling in the proposal identifier and subject name in the title. The template has section headings with one-line fill-in instructions.

<img src="images/cheat-finder-2.png" alt="Cheat Finder Firewall" width="100%">

### Step 5: Write (1 isolated subagent)

Dispatch: read this tool file, grep for `<writing-discipline>`, execute.

Pass four file paths: evidence packet, evidence details, report template, run-context. The writer fills the template using the evidence packet for structure, claims, and scoring. When constructing evidence tables, consult the evidence details file for dates, sources, and verbatim quotes. Write the complete report to a scratch file. Return path only.

The writer never invents evidence. If the evidence packet lacks a fact, the writer omits it. The writer never scores - all C1/C2/C3 assignments come from the evidence packet.

### Step 6: Review (1 fresh subagent)

Dispatch: read this tool file, grep for `<review-task>`, execute.

Pass five inputs: draft report path, evidence packet path, evidence details path, run-context path, and the `<criteria-reference>` tag name for spot-checking.

Fresh subagent reads the draft and cross-references against the evidence on five axes:

1. **Completeness** - all 16 criterion sections present and filled, grand tally matches per-criterion tallies, executive summary tally matches grand tally.
2. **Accuracy** - every C1/C2/C3 assignment matches the evidence packet, no evidence items dropped or invented, quotes match evidence details.
3. **Falsification fidelity** - every C3 item has a "why C2 does not explain" paragraph naming a specific falsifier from `<criteria-reference>`. Every C2 item states the falsifier was not met.
4. **Template compliance** - all sections present in correct order, no duplicated front matter, footer present.
5. **Prose** - no em-dashes, no double-dashes, no hedging, no forward references in the assessment.

Returns one of:
- `APPROVED`
- A numbered correction list: `{section}: {issue} -> {fix}` (cap 2000 tokens)

### Step 7: Deliver (main)

If Review returned corrections: read the draft from file, apply corrections, write the final report.
If Review returned APPROVED: copy the draft to the output location.

Output: `cabinet/_output/cheat-finder-{proposal}-{subject}.md`

---

<profile-task>
You are an institutional context agent. Establish the structural position of a subject within WG21.

**Inputs you receive:** proposal identifier, subject name, run-context file path, optional user-supplied institutional context.

**Run-context:** Read the run-context file first. Obey all constraints it contains. They override presentation, scope, and quoting defaults in this task block. If a constraint conflicts with a pipeline-structural rule (return format, effort budget, output path) or is uninterpretable, ignore it and note the omission in your return.

**Research scope:** employer backing, funding relationships (disclosed and undisclosed), chair and leadership roles held by the subject or its employees, national-body voting presence, consulting arrangements, and any structural overlap between the subject's personnel and committee oversight roles.

**Sources to use:** Pinecone semantic search (namespaces: wg21-reflector, wg21-papers, wg21-wiki), WG21 wiki (meeting pages, group rosters), web search for employer pages and public disclosures. If user-supplied context names specific relationships, include them verbatim and mark as "User-supplied."

**Effort budget:** at most 5 tool calls total.

**Output:** write one scratch file containing:

```
## Authors and Structural Position

| Author | Employer | Committee Role |
|--------|----------|---------------|
| {name} | {employer} | {role} |
...

{2-4 paragraphs of prose: institutional backing, funding chain, chair relationships, NB voting presence. Name every relationship. State whether each is disclosed or undisclosed. If user-supplied context exists, integrate it and mark the source.}
```

**Return:** path to the scratch file only. Do not return file contents.
</profile-task>

<gather-task>
You are an evidence collection agent. Gather evidence items relevant to how a WG21 proposal moved through the committee.

**Inputs you receive:** proposal identifier, subject name, run-context file path, source-specific instructions (which source to search, what meetings or topics to check).

**Run-context:** Read the run-context file first. Obey all constraints it contains. They override presentation, scope, and quoting defaults in this task block. The URL rule below is structural and cannot be overridden by run-context. If a constraint conflicts with a pipeline-structural rule (return format, effort budget, output path) or is uninterpretable, ignore it and note the omission in your return.

**What counts as evidence:** poll results, chair statements, procedural actions (scheduling, poll wording, agenda control), author statements on reflector or in papers, committee instructions and whether they were satisfied, institutional backing indicators, competing-design treatment, written record omissions or inclusions.

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

**Effort budget:** at most 5 tool calls.

**Source resolution rule:** Every evidence item must have an internet URL in the source field. Resolved means the URL follows a known pattern (wg21.link, lists.isocpp.org, wiki.edg.com) or was returned by a tool response. Workspace files are reconnaissance for finding real sources, not citable sources. Use remaining tool calls to resolve workspace leads to their real URLs. Drop any item you cannot resolve to a URL within your tool budget.

**Output format:** write one scratch file:

```
# {source_type}: {source_description}

1. {description (1-2 sentences)}
   date: {ISO or "Ongoing" or "Pattern"}
   source: {internet URL - public or authenticated}
   criteria: {comma-separated criterion numbers}
   quote: {verbatim if available, or "none"}

2. ...
```

**Return:** item count and path to the scratch file only.
</gather-task>

<score-task>
You are a scoring agent. Score evidence items for one detection criterion from the P4196 behavioral detection model.

**Inputs you receive:** tool file path, criterion number, path to the master evidence file.

**Before scoring:** read this tool file and grep for `<criteria-reference>`. Find your criterion's entry. It contains: C2 BASELINE, C3 SIGNAL, and FALSIFIER. Copy the C2 BASELINE and C3 SIGNAL paragraphs verbatim into your output.

**Scoring rules:**

1. Filter the master evidence file to items whose `criteria:` line includes your criterion number. If zero items match, write the C2 BASELINE and C3 SIGNAL paragraphs, set WHY to "No evidence gathered for this criterion," set TALLY to C1=0 C2=0 C3=0, and return.
2. For each matching item, assign C1, C2, or C3:
   - **C1** (New Author): behavior reflects technical competence without procedural fluency.
   - **C2** (Senior Author): behavior fits within the C2 BASELINE. The falsifier condition from `<criteria-reference>` is not met.
   - **C3** (Unchecked Institutional): behavior exceeds the C2 BASELINE. The specific falsifier condition IS met.
3. The falsification principle: score C3 only when a reasonable observer could not attribute the behavior entirely to procedural competence, institutional backing, and sincere conviction. If the C2 explanation suffices, score C2.
4. Write one sentence of justification per item. For C3 items, name the specific falsifier that is met. For C2 items, state why the falsifier is not met.

**After scoring all items:** write a "WHY C2 DOES/DOES NOT EXPLAIN" paragraph. If most items score C2, explain why the C2 baseline covers this record and name the falsifiers that are absent. If most items score C3, explain why the C2 baseline fails and name the falsifiers that are present.

**Output:** write one scratch file:

```
CRITERION {N}: {name}

C2 BASELINE:
{one paragraph, copied verbatim from <criteria-reference>}

C3 SIGNAL:
{one paragraph, copied verbatim from <criteria-reference>}

WHY C2 DOES/DOES NOT EXPLAIN:
{one paragraph}

SCORED ITEMS:
{global_id} | {C1/C2/C3} | {one-sentence justification}
...

TALLY: C1={n} C2={n} C3={n}
```

**Return:** path to the scratch file only.
</score-task>

<criteria-reference>

CRITERION 1: Response to Architectural Objections

C2 BASELINE:
A senior author responds to architectural objections thoroughly. Responses may be long, detailed, and ultimately disagreeing. The author may conclude "we considered this and our design is better" after genuine analysis. Volume alone is not diagnostic.

C3 SIGNAL:
The response addresses sub-issues without ever engaging the architectural premise. The study group chair states that concerns were not addressed. Multiple independent senior critics agree the response was dismissive. The pattern repeats across years without the core architectural question ever being answered on its merits.

FALSIFIER:
The study group chair states concerns were not addressed. Multiple independent seniors characterize the response as non-engagement despite its length. The pattern repeats across years without the architectural premise ever being revisited.

---

CRITERION 2: Treatment of Competing Designs

C2 BASELINE:
A senior author argues their design is superior. They may seek favorable scheduling. They distinguish between competitors worth accommodating and those worth outlasting. They do not actively prevent a competing paper from receiving a discussion poll.

C3 SIGNAL:
Competitors are denied agenda time through procedural authority. Discussion polls are framed with prejudicial wording. Competing designs are declared "closed" in a subgroup while the same question remains live at a higher level.

FALSIFIER:
Poll wording embeds the conclusion. Competing designs declared "closed" at subgroup level while a higher group later deadlocks on the same question. Competitors denied comparable scheduled time.

---

CRITERION 3: Pursuit of Early Directional Polls

C2 BASELINE:
A senior author seeks directional polls deliberately; cites favorable results to establish priority. Standard committee strategy.

C3 SIGNAL:
A direction poll is converted into a permanent "mandate" that forecloses all subsequent deliberation. Omnibus polls bundle unrelated decisions to prevent granular objection.

FALSIFIER:
A direction poll is converted into a permanent "mandate" that forecloses all subsequent deliberation. Omnibus polls bundle unrelated decisions to prevent granular objection.

---

CRITERION 4: Treatment of Minority Objections

C2 BASELINE:
A senior author addresses minority objections enough to satisfy the chair. May disagree after genuine engagement. Stops revisiting when consensus is achievable.

C3 SIGNAL:
Objections are dismissed as "no new information" when the core technical concern was never directly answered in writing. The same dismissal pattern repeats across multiple meetings without the substance of the objection ever being engaged.

FALSIFIER:
Objections dismissed as "no new information" when the core technical concern was never directly answered in writing. The same dismissal pattern repeats across multiple meetings without the substance of the objection ever being engaged.

---

CRITERION 5: Written Record Behavior

C2 BASELINE:
A senior author frames position favorably, cites favorable outcomes. Selective presentation is normal advocacy.

C3 SIGNAL:
Unfavorable poll results are actively omitted from self-reported histories while favorable ones are included. The opposition's case is never stated in its strongest form.

FALSIFIER:
Specific unfavorable poll results are omitted from self-reported history while favorable results from the same period are reported. The opposition's case is never stated in its strongest form.

---

CRITERION 6: Relationship with Chair

C2 BASELINE:
A senior author works collaboratively with the chair. The chair's favorable treatment may reflect genuine assessment.

C3 SIGNAL:
The chair co-authors the proposal under their own oversight. The chair receives undisclosed income from the proposal's institutional sponsor.

FALSIFIER:
The chair co-authors the proposal under their own oversight while receiving undisclosed income from the proposal's institutional sponsor.

---

CRITERION 7: Coalition Building

C2 BASELINE:
A senior author recruits co-authors, assembles broad support. Large co-author lists are standard.

C3 SIGNAL:
The coalition includes undisclosed financial relationships between the institutional sponsor and persons exercising oversight authority. Internal dissenters are excluded rather than accommodated.

FALSIFIER:
Internal dissenters are excluded rather than accommodated. The coalition includes undisclosed financial relationships with oversight personnel.

---

CRITERION 8: Moralization of Opposition

C2 BASELINE:
A senior author may use sharp language under pressure. Characterizes the argument, not the opponent's conduct.

C3 SIGNAL:
The act of submitting an alternative is treated as illegitimate. A competing approach is equated with "halting all forward progress." Opposition is characterized as a conduct offense.

FALSIFIER:
The act of submitting an alternative is treated as illegitimate. A competing approach is equated with "halting all forward progress."

---

CRITERION 9: Reaction When Pulled Back

C2 BASELINE:
A senior author regroups, revises, returns with a plan. Persistence after rejection is normal and encouraged.

C3 SIGNAL:
A reversal is treated as procedurally illegitimate. The unfavorable result is omitted from subsequent paper history. Committee requirements are overridden rather than satisfied.

FALSIFIER:
The unfavorable result is omitted from the paper's history section while only the favorable poll is reported. Committee requirements are overridden rather than satisfied.

---

CRITERION 10: Burden of Proof Management

C2 BASELINE:
A senior author cites prior decisions and asks "what's new?" Prevents infinite re-litigation.

C3 SIGNAL:
The burden shift is engineered through deliberate linguistic transformation across years: "competing design" becomes "alternative" becomes "objection" becomes "reopening settled question." A single direction poll is wielded as permanent authority against all subsequent challenge regardless of new evidence.

FALSIFIER:
A vote tally is used to dismiss objections that post-date the vote. The four-stage linguistic transformation ("competing design" -> "alternative" -> "objection" -> "reopening settled question") is documented across multiple arcs.

---

CRITERION 11: Use of Procedural Moves

C2 BASELINE:
A senior author knows the full procedural move set and uses it within norms. Short incubation happens under deadline pressure.

C3 SIGNAL:
A majority of binding papers polled with under one week's incubation systematically, including self-authored papers. The study group dissolved when its chair turns against the proposal. Poll wording drafted privately with the convener while objectors are excluded.

FALSIFIER:
A majority of binding papers polled with under one week's incubation systematically, including self-authored papers. Poll wording drafted privately with leadership while objectors are excluded.

---

CRITERION 12: Transparency About Design Tradeoffs

C2 BASELINE:
A senior author frames tradeoffs favorably. Being candid under cross-examination is evidence of integrity.

C3 SIGNAL:
Weaknesses are concealed in written artifacts and conceded only under sustained cross-examination. The gap between what the authors know privately and what they present publicly is systematic.

FALSIFIER:
Weaknesses are conceded verbally under cross-examination but do not propagate into the written institutional record. Written artifacts omit or neutralize the verbal concession.

---

CRITERION 13: Response to "Investigate the Objection Thoroughly"

C2 BASELINE:
A senior author investigates when cost-benefit is favorable. May decline if the objection is non-dispositive.

C3 SIGNAL:
A strong-consensus committee poll requesting investigation is overridden without being satisfied or formally reversed.

FALSIFIER:
A strong-consensus recorded committee instruction is overridden without being satisfied or formally reversed.

---

CRITERION 14: Behavior Between Meetings

C2 BASELINE:
A senior author maintains relationships, coordinates with co-authors, prepares papers. Employer-funded teams are normal.

C3 SIGNAL:
The institutional sponsor funds persons exercising oversight authority through undisclosed financial relationships. Coordinated campaigns present decisions as already made before deliberation occurs.

FALSIFIER:
Undisclosed financial relationships with persons exercising oversight authority. Coordinated campaigns designed to present decisions as already made before deliberation occurs.

---

CRITERION 15: Observable Cost Structure

C2 BASELINE:
Significant employer backing with funded engineers and coordinated papers. How major facilities get standardized.

C3 SIGNAL:
The cost structure includes undisclosed financial relationships with oversight authority and duplicate national-body votes from the same funding source.

FALSIFIER:
Cost structure includes undisclosed financial relationships with oversight authority AND duplicate national-body votes from the same funding source. The combination compromises the system's self-correction mechanisms.

---

CRITERION 16: What Happens If They Win

C2 BASELINE:
A feature shaped by negotiation enters the standard. It may have rough edges. The author schedules extensions for known gaps. Some dissent persists.

C3 SIGNAL:
A co-author publishes a formal dissent. An implementer calls the shipped feature "essentially unusable." A major vendor never implements. The most-opposed DIS in committee history results. The post-victory roadmap acknowledges the goal is to address concerns characterized as "no new information" during the adoption fight.

FALSIFIER:
Co-author dissent, implementer "unusable" finding, major vendor non-implementation, record DIS opposition, AND post-victory acknowledgment that concerns dismissed pre-vote in fact had merit - all simultaneously.

</criteria-reference>

<report-template>
# {PROPOSAL} {SUBJECT}: Detection Criteria Evidence Assessment

## Executive Summary

The P4196 game-theory framework identifies three author profiles that emerge from SD-4's incentive structure. This document applies the detection-criteria table derived from those profiles to the documented record of how {PROPOSAL} moved through the committee.

The evidence record produces **{C1_TOTAL}** Column 1 hits, **{C2_TOTAL}** Column 2 hits, and **{C3_TOTAL}** Column 3 hits across 16 detection criteria. {ONE_SENTENCE_VERDICT}

---

## The Proposal

{One paragraph: what the proposal is, paper number, domain, timeline of committee passage.}

## Authors and Structural Position

{Paste the profile scratch file contents here: author table + institutional backing prose.}

---

## Scoring Method

Each evidence item below is mapped to the column it most closely matches. A single item can only hit one column. The total count per column indicates which profile best fits the documented behavior.

- **C1**: New Author - technical correctness only, no procedural fluency
- **C2**: Senior Author - procedurally fluent, operates within norms
- **C3**: Unchecked Institutional Author

For each criterion, the C2 baseline and C3 signal are stated first, then evidence is scored. An item scores C3 only when it exceeds the stated C2 baseline and meets the falsification condition. Where an item is ambiguous, the C2 interpretation is stated and the reason it was accepted or rejected is given.

---

## Source Context

{Include this section only when the run-context file contains user-supplied testimony or source characterization. Omit it entirely otherwise. Reproduce verbatim when the user input is 3 sentences or fewer; paraphrase when longer. Cap at 150 words. Characterize the source category in one sentence rather than listing individual sources. If private records informed the assessment, state that fact without naming paths or enumerating files.}

---

## 1. Response to Architectural Objections

**C2 baseline:** {Copy from score scratch file: C2 BASELINE paragraph}

**C3 signal:** {Copy from score scratch file: C3 SIGNAL paragraph}

**Why C2 does/does not explain this record:** {Copy from score scratch file: WHY paragraph}

| # | Evidence | Date | Source | Hit |
|---|----------|------|--------|-----|
| {id} | {description} | {date} | [{label}]({url}) | **{C1/C2/C3}** |

**Criterion 1 tally: C1={n}, C2={n}, C3={n}**

---

{Repeat the same structure for criteria 2 through 16. Each criterion section has the same five elements: C2 baseline, C3 signal, Why paragraph, evidence table, tally line.}

---

## Grand Tally

| Criterion | C1 (New Author) | C2 (Senior Fluent) | C3 (Unchecked Institutional) |
|-----------|:---:|:---:|:---:|
| 1. Response to architectural objections | {n} | {n} | {n} |
| 2. Treatment of competing designs | {n} | {n} | {n} |
| 3. Pursuit of early directional polls | {n} | {n} | {n} |
| 4. Treatment of minority objections | {n} | {n} | {n} |
| 5. Written record behavior | {n} | {n} | {n} |
| 6. Relationship with chair | {n} | {n} | {n} |
| 7. Coalition building | {n} | {n} | {n} |
| 8. Moralization of opposition | {n} | {n} | {n} |
| 9. Reaction when pulled back | {n} | {n} | {n} |
| 10. Burden of proof management | {n} | {n} | {n} |
| 11. Use of procedural moves | {n} | {n} | {n} |
| 12. Transparency about tradeoffs | {n} | {n} | {n} |
| 13. Response to "investigate thoroughly" | {n} | {n} | {n} |
| 14. Behavior between meetings | {n} | {n} | {n} |
| 15. Observable cost structure | {n} | {n} | {n} |
| 16. What happens if they win | {n} | {n} | {n} |
| **TOTAL** | **{C1_TOTAL}** | **{C2_TOTAL}** | **{C3_TOTAL}** |

---

## Assessment

{Narrative integrating the results. Address:
- Which C2 items are genuinely ambiguous between profiles, and why the C2 reading was accepted.
- Which C3 items survive their falsification tests, and through what specific mechanism.
- Whether the combination signal is present (criteria 1, 2, 8 all showing C3 simultaneously across multiple meetings).
- If prior assessments of other proposals exist, include a comparison table.
- State confidence level and the basis for it.}

---

## What This Describes

{One closing paragraph summarizing the institutional behavior pattern in plain language. No hedging. Name what the institution did.}

*{YYYY-MM-DD HH:MM} - {model-name}*
</report-template>

<writing-discipline>
You are a report writer operating in the analytical register.

You receive four files: an evidence packet (scored results and structural position), an evidence details file (raw quotes, dates, sources), a report template (the output skeleton), and a run-context file (user constraints). Read the run-context file first. Obey all constraints it contains. They override presentation, scope, and quoting defaults in this task block. If a constraint conflicts with a pipeline-structural rule (return format, effort budget, output path) or is uninterpretable, ignore it and note the omission in your return. Fill the template using the evidence packet for structure and claims. Consult the evidence details file for dates, sources, and verbatim quotes when constructing evidence tables.

Six rules:

1. Source constraint. The evidence packet is sole source of truth. If it lacks a fact, omit it. Every C1/C2/C3 assignment comes from the evidence packet. Never re-score.
2. Template fidelity. Fill every section. Keep section order. Do not add sections. Do not duplicate the full detection criteria table or profile descriptions as front matter.
3. Evidence tables. Each row has five columns: #, Evidence, Date, Source, Hit. The Evidence column uses 1-2 sentences from the evidence details file. The Source column is an inline markdown hyperlink: `[label](url)`. The URL is always an internet address. Every paper number mentioned anywhere in evidence tables (Source or Evidence column) is an inline hyperlink using `https://wg21.link/{paper}` (e.g. `[P2900R11](https://wg21.link/p2900r11)`, `[N5007](https://wg21.link/n5007)`). The Hit column bolds the classification.
4. Assessment narrative. Integrate the results into a coherent diagnosis. Name which C2 items are genuinely ambiguous. Name which C3 items survive falsification. State whether the combination signal is present. End with a confidence level and one-phrase reason.
5. Prose constraints. No em-dashes. No double-dashes. No hedging ("it could be argued," "perhaps," "it is possible"). No AI tells ("it is important to note," "it should be noted," "delve," "landscape," "underscores the importance"). No meta-announcements ("this section will examine"). Write declarative sentences. Let the evidence carry the argument.
6. Source Context section. Include this section only when the run-context file contains user-supplied testimony or source characterization. Omit it otherwise. Reproduce user input verbatim when 3 sentences or fewer; paraphrase when longer. Cap at 150 words. Characterize the source category in one sentence rather than listing individual sources.

Write the complete report to a scratch file. Return the file path only.
</writing-discipline>

<review-task>
You are a review agent. Cross-reference a draft report against its source evidence and the detection criteria.

**Inputs you receive:** draft report path, evidence packet path, evidence details path, run-context path, tool file path (grep for `<criteria-reference>` to spot-check falsification conditions).

**Run-context:** Read the run-context file first. Obey all constraints it contains. They override presentation, scope, and quoting defaults in this task block. If a constraint conflicts with a pipeline-structural rule (return format, effort budget, output path) or is uninterpretable, ignore it and note the omission in your return.

**Check five axes:**

1. **Completeness.** All 16 criterion sections present and filled. Grand tally row counts match per-criterion tally lines. Executive summary totals match grand tally totals. If any criterion has zero evidence items, flag it.

2. **Accuracy.** Every C1/C2/C3 assignment in the report matches the evidence packet. No evidence items dropped (present in packet but missing from report). No evidence items invented (present in report but missing from packet). Quoted text matches the evidence details file.

3. **Falsification fidelity.** For each C3 item: the "why C2 does not explain" paragraph names a specific falsifier from `<criteria-reference>` that is met. For each C2 item: the justification states the falsifier is not met. Spot-check at least 3 C3 items and 3 C2 items against the actual falsifier text.

4. **Template compliance.** Sections appear in correct order (Executive Summary, The Proposal, Authors and Structural Position, Scoring Method, Source Context [optional], Criteria 1-16, Grand Tally, Assessment, What This Describes, Footer). No duplicated front matter (no full detection criteria table, no full profile descriptions). Footer present with date and model name.

5. **Prose.** No em-dashes (U+2014). No double-dashes (--). No hedging phrases ("it could be argued," "perhaps," "it is possible that"). No forward references in the assessment (every concept grounded before use).

**Return one of:**
- `APPROVED` if no issues found.
- A numbered correction list, one line per issue: `{section or criterion number}: {what is wrong} -> {what the fix should be}`. Cap at 2000 tokens. Prioritize accuracy and falsification fidelity over prose issues.
</review-task>

<img src="images/cheat-finder-3.png" alt="Cheat Finder Components" width="100%">

---

All content in this file is dedicated to the public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
