# Summarize Papers

Summarize all WG21 papers in a source folder into a campaign briefing and a public-facing companion, with individual per-paper summaries and aggregate executive summaries.

<img src="images/summarize-papers.png" alt="Summarize Papers" width="100%">

## Parameters

The user provides (or the agent infers from context):

- **source_folder** - path to a directory of `.md` paper files (e.g. `source/07-july`)
- **output_folder** - path to the directory where output files are written (e.g. `campaign`), relative to the repo root

Filenames are auto-derived from the source folder name:

- Parse folder name `07-july` to get month name and infer year (2026).
- Campaign file: `{output_folder}/papers-2026-july.md`
- Public file: `{output_folder}/d0000-summary-july-2026.md`

## Execution

**HARD RULE: No parallelism. Never launch more than one subagent at a time. Every subagent must complete and return its result to the main context before the next subagent launches. Never write temporary files; all data flows through the main context as variables. After each subagent returns, extract and retain only the DOCUMENT, TITLE, and SUMMARY (or the labeled output for aggregate stages). Do not retain the full subagent prompt/response exchange in working memory. Accumulate results as a compact list.**

### Phase 1: Enumerate, Extract Metadata, and Discover History

1. Glob `source_folder/*.md` to get the list of papers. Exclude any file whose name contains `-summary-` (these are reader's-guide papers, not source papers to summarize).
2. Sort alphabetically by filename.
3. Infer the mailing name from the source folder name (e.g. `04-april` -> "April 2026", `05-may` -> "May 2026").
4. For each paper, read the YAML frontmatter and extract `document`, `title`, and `author` (if the `author` field is absent or the frontmatter uses `reply-to` instead, default to "Vinnie Falco"). Store these as the **ground-truth metadata** for the paper. Subagents will receive these values rather than extracting them independently.
5. Glob `{output_folder}/papers-*.md` (excluding files ending in `-public.md`). Sort chronologically by the year-month in the filename. Take up to 3 most recent files that precede the current month. Read just the executive summary section (everything above the first `---` separator) from each. These become the **prior sequence context**.

### Phase 2: Individual Summaries - Strictly Sequential

To achieve zero context contamination, public and campaign summaries are produced by **completely separate subagents** that never see each other's prompts.

**Phase 2A - Public per-paper summaries (one at a time)**

For each paper, **sequentially** launch a `generalPurpose` subagent. Pass it:

- The full path to the paper file
- Instruction to read the entire paper
- The ground-truth document number and title from Phase 1: "The document number is {document} and the title is {title}. Use these exactly as given."
- The **Per-Paper Public Prompt** below
- The **mandatory return format** (include verbatim in the subagent prompt):

```
Return your answer in exactly this format, with no other text before or after:

DOCUMENT: {the document number}
TITLE: {the title}
SUMMARY: {the summary paragraph}
```

Wait for the subagent to complete. Extract only the DOCUMENT, TITLE, and SUMMARY fields. If the subagent's return contains reasoning, commentary, or thinking beyond the three fields, discard everything except those fields. Store the clean triple in the main context before launching the next subagent.

**Phase 2B - Campaign per-paper summaries (one at a time)**

After **all** Phase 2A subagents have completed, process each paper **sequentially** with a `generalPurpose` subagent. Pass it:

- The full path to the paper file
- Instruction to read the entire paper
- The ground-truth document number and title from Phase 1: "The document number is {document} and the title is {title}. Use these exactly as given."
- The **Per-Paper Campaign Prompt** below
- The **mandatory return format** (include verbatim in the subagent prompt):

```
Return your answer in exactly this format, with no other text before or after:

DOCUMENT: {the document number}
TITLE: {the title}
SUMMARY: {the summary paragraph}
```

Wait for the subagent to complete. Extract only the DOCUMENT, TITLE, and SUMMARY fields. If the subagent's return contains reasoning, commentary, or thinking beyond the three fields, discard everything except those fields. Store the clean triple in the main context before launching the next subagent.

Phase 2A runs first, then Phase 2B. No overlap.

### Phase 3: Aggregate - Strictly Sequential

Stage A and Stage B are independent of each other - neither needs the other's output. They are serialized only because of the hard no-parallelism rule. Stage C depends on Stage B's output. The fixed ordering is A, then B, then C.

**Stage A - Public aggregate**

Launch a single `generalPurpose` subagent. Pass it:

- All individual **public** summaries (from Phase 2A, held in the main context)
- The **Public Aggregate Prompt** below
- No campaign context whatsoever

Wait for it to complete. Capture the returned **one-liner** and **public executive summary** into the main context.

**Stage B - Campaign aggregate**

After Stage A completes, launch a single `generalPurpose` subagent. Pass it:

- All individual **campaign** summaries (from Phase 2B, held in the main context)
- The **Campaign Aggregate Prompt** below

Wait for it to complete. Capture the returned **single-mailing campaign executive summary** into the main context.

**Stage C - Sequence analysis**

After Stage B completes, launch a single `generalPurpose` subagent. Pass it:

- The single-mailing campaign executive summary from Stage B (held in the main context)
- The prior sequence context (up to 3 prior executive summaries, oldest first)
- The **Sequence Prompt** below

Wait for it to complete. Capture the returned **sequence analysis** into the main context.

If there are no prior summaries (first mailing), skip Stage C entirely.

### Phase 4: Assemble Output Files

The main agent writes both files using the Write tool. After writing each file, verify that neither file contains Unicode dashes (U+2013 en-dash, U+2014 em-dash), mojibake sequences (such as the three-character sequence that results from double-encoding an em-dash), or double-spaced dashes (`  -  `). If any are found, replace them with ` - ` before finishing.

**Campaign file** (`papers-2026-july.md`):

```
# {mailing_name} Mailing: Paper Summaries

{single-mailing campaign executive summary from Stage B}

## Sequence Analysis

{sequence analysis from Stage C, or omit this section if Stage C was skipped}

---

**{document} - {title}** {campaign summary paragraph}

**{document} - {title}** {campaign summary paragraph}

...
```

**Public file** (`d0000-summary-july-2026.md`):

The public file is a proper WG21 paper. Assemble it from this template:

```
---
title: "A Reader's Guide to the {mailing_name} Mailing"
document: D0000R0
date: {YYYY-MM-DD, last day of the mailing month}
intent: info
audience: LEWG
reply-to:
  - "Vinnie Falco <vinnie.falco@gmail.com>"
---

## Abstract

{one-liner from Stage A}

This paper summarizes {N} papers published in the
{mailing_name} mailing. It is a reading guide: an executive summary
that identifies the logical series within the collection, describes
what each series delivers, and provides individual summaries of every
paper. It asks for nothing.

---

## 1. Disclosure

The author provides information and serves at the pleasure of the
committee.

This paper asks for nothing.

---

## 2. Executive Summary

{public executive summary from Stage A}

---

## 3. Individual Papers

### 3.1. {document} - {title}

{public summary paragraph}

### 3.2. {document} - {title}

{public summary paragraph}

...one subsection per paper, ordered by document number...

---

## 4. Conclusion

This reading guide covers {N} papers from the {mailing_name} mailing.
The author hopes it helps the reader find the papers most relevant to
their work and interests.

---

## References

[1] {document} - "{title}" ({author}, {year}).

[2] {document} - "{title}" ({author}, {year}).

...one entry per paper, ordered by document number. {author} comes from
the ground-truth metadata extracted in Phase 1...
```

Notes on assembly:
- The abstract paragraph and conclusion are mechanical templates filled from
  paper count and mailing name. They are not AI-generated.
- Section 3 subsections are numbered sequentially (3.1, 3.2, ...) and ordered
  by document number.
- References are ordered by document number. Each entry uses the paper's
  document number and title from the YAML frontmatter. If the paper has an
  `open-std.org` URL, link it: `[{document}]({url})`. Otherwise use the
  bare document number without a link.

---

## Per-Paper Public Prompt

Pass this prompt verbatim to each Phase 2A subagent:

```
You are writing a summary of a WG21 committee paper for a reading guide that
will itself be published as a WG21 paper. The audience is C++ developers,
committee participants, and technical bloggers. Your job is to make the reader
want to open this specific paper.

Write a single concise paragraph (3-5 sentences).

Structure:
- Sentence 1 is the hook. It is the single most compelling thing about this
  paper - the reason a developer would stop scrolling. If the paper is
  controversial, say so. If it surfaces a finding nobody expected, lead with
  that. If it ships working code that solves a real problem, lead with the
  code. The hook must land like a headline.
- Sentences 2-4 describe what the paper does. The register is one notch below
  sensational - make even a history lesson or a governance audit feel like
  something the reader cannot afford to miss. Name concrete artifacts: line
  counts, benchmark numbers, compiler support, production deployments, field
  interviews. If the paper contains working code, make the reader want to
  clone the repo.

Every summary must sound different from every other summary. If two summaries
could be swapped without anyone noticing, one of them is wrong.

Rules:
- WG21 register: no contractions, American English. But punchy and compelling.
  Think of the style "Three deployed executor models were replaced by one that
  was never deployed" - factual, hits hard, reads like a committee paper.
- Single dashes only. Use " - " for all dashes. Never use em-dashes, double
  dashes ("--"), or Unicode dashes.
- Write in third person throughout. Never use "you" or "your."
- Do not mention campaigns, targets, vulnerabilities, strategic effects, or
  manipulation.
- Do not mention specific individuals as opponents or targets.
- Do not describe papers as "weapons," "instruments," "ammunition," or
  "pressure."
- Match the register to the paper. A spec-level cost analysis reads differently
  from a twenty-one-year historical retrospective reads differently from a
  field report with production engineers.
- Do not include any reasoning, internal monologue, thinking steps, or
  commentary. Return only the requested output in the specified format.
```

---

## Per-Paper Campaign Prompt

Pass this prompt verbatim to each Phase 2B subagent:

```
You are summarizing a WG21 committee paper for a campaign briefing. The briefing's
introduction already establishes that every paper in this mailing asks for nothing,
is not scheduled, is not presented, and proposes no normative wording. Do not repeat
any of those facts in the summary.

Read the entire paper. Then write a single paragraph (3-8 sentences) that answers
these questions in order:

1. What is the paper's unique structural device? Every effective paper has one - a
   concession methodology, a scorecard, a reusable tool, a rhetorical ladder, a
   comparison table, a side-by-side code walkthrough, a historical parallel. Name it.
   This is the lead sentence.

2. What does the paper deposit into the permanent record that wasn't there before?
   Not "analysis" or "information" - the specific artifact. A dated scorecard with
   18/5 confirmed/unconfirmed. A CC0-licensed evaluation rubric. A normative-citation
   cost table showing 0 vs. 15 state<Rcvr> constructions. A cross-library interop
   table proving awaitables compose without coordination. Name the artifact and its
   key number or finding.

3. Who is the target reader, and what does that reader absorb? Not "the committee" --
   the specific segment. An implementer who now has spec-citation ammunition. An
   uncommitted delegate who now has a one-liner ("7/21 - not even close to C++"). A
   Direction Group member who now faces a documented gap between their stated priority
   and the revealed output. What does that reader carry away?

4. What is the paper's sharpest single line or finding? Quote it or state it. If the
   paper has a memorable conclusion, a devastating table entry, or a one-sentence
   finding that travels on its own - that goes here.

Rules:
- Lead with what the paper does, never with what it lacks.
- No paper sounds like any other paper. If two summaries could be swapped without
  anyone noticing, one of them is wrong.
- Do not use the words "noise," "shelf-stuffing," "rehash," "repackage," or "garnish."
- Do not say "it asks for nothing" or "it is not on any agenda." The introduction
  handles that.
- Match the paragraph's register to the paper's character. A spec-citation cost
  analysis reads differently from a civilizational-respect essay reads differently
  from a prediction scorecard.
- Single dashes only. Use " - " for all dashes. Never use em-dashes, double
  dashes ("--"), or Unicode dashes.
- If the paper is infrastructure (a building block for other papers rather than a
  standalone instrument), say so in two sentences and move on. Not every paper needs
  a full paragraph.
- Do not include any reasoning, internal monologue, thinking steps, or
  commentary. Return only the requested output in the specified format.
```

---

## Campaign Aggregate Prompt

Pass this prompt verbatim to the Stage B subagent:

```
You have a set of individual paper summaries from a single WG21 mailing, all by the
same author, all informational, all asking for nothing. Each summary was written to
surface the paper's unique structural device, its specific deposit into the permanent
record, its target reader, and its sharpest finding.

Read all the summaries together. Then write an aggregate assessment (roughly 10-20
paragraphs) that answers these questions:

1. What is the aggregate's unique structural device?

Individual papers have structural devices (a scorecard, a concession methodology, a
reusable rubric). What is the structural device of the *collection*? How does the
arrangement of papers create an effect that no individual paper creates? Name the
phenomenon - not with a generic label ("campaign") but by describing the specific
mechanism. How does paper A's deposit interact with paper B's deposit to produce
something neither achieves alone? Identify at least three specific paper-to-paper
interactions where the combination is more than the sum.

2. What does the aggregate deposit into the permanent record that the individual
   papers do not?

Each paper deposits an artifact. What artifact does the *collection* deposit? A
single paper deposits a scorecard or a cost table. A coordinated set of papers from
one author in one mailing deposits something else - a narrative arc, an interpretive
frame, a vocabulary set, a body of work that redefines a reader's baseline for
evaluating future proposals. Name it. What is the specific shift in the permanent
record's center of gravity?

3. Who is the aggregate's target reader, and what does that reader experience?

Individual papers target segments: implementers, uncommitted delegates, the Direction
Group, the C++ public. Who is the aggregate's target, and what happens to a reader
who encounters the *collection* rather than any single paper? Describe the experience
for at least three distinct reader profiles:
- A committee member who reads all or most of them
- A committee member who reads a handful
- A committee member who reads none but sits in a room where others have read them

What changes for each? What frame shift occurs, and how does it manifest in behavior
(voting, hallway conversation, evaluation of future proposals)?

4. What is the aggregate's sharpest single finding or effect?

Not the sharpest line from any individual paper - the sharpest finding about *the
collection itself*. What is the one-sentence observation about these papers together
that a reader carries away? If a trip report or blog post were to describe this
mailing, what would the headline be?

5. What is the aggregate's vulnerability?

Every instrument has a failure mode. What would neutralize this mailing? A single
devastating rebuttal paper? Ignoring it? A procedural response? A counter-campaign?
An ad hominem attack on the author? Identify the two or three most plausible
defensive responses from the institution and evaluate whether each one succeeds or
fails, and why. Be honest - if there is a response that works, name it.

6. What is the aggregate's implied next move?

Info papers ask for nothing. What do they set up? If these papers are shaping
operations, what is the decisive engagement they prepare? What would the author's
*next* mailing contain if the campaign is proceeding as designed? What ask papers,
proposals, or procedural motions become possible *because* these papers exist in the
permanent record? Name at least two concrete future moves that are unlocked by this
mailing and were not available before it.

Rules:
- The assessment is about the *collection*, not a recap of individual papers. Do not
  summarize each paper again. Reference individual papers only when describing
  specific interactions between them.
- Be specific. "The papers build a narrative" is not an assessment. Naming the exact
  paper-to-paper interaction and the compound effect it produces is an assessment.
- If the aggregate is less than the sum of its parts - if the papers actually
  interfere with each other, dilute each other's message, or create contradictions
  - say so.
- Match the register to the scale. This is a strategic assessment, not a book report.
- Single dashes only. Use " - " for all dashes. Never use em-dashes, double
  dashes ("--"), or Unicode dashes.
- Do not include any reasoning, internal monologue, thinking steps, or
  commentary. Return only the requested output.
```

---

## Sequence Prompt

Pass this prompt verbatim to the Stage C subagent:

```
You have two inputs:

1. The executive summary of the current mailing (just produced).
2. The executive summaries of up to three prior mailings, in chronological order.

Write a sequence analysis (5-10 paragraphs) that answers:

1. What is the arc across the full sequence? Not a recap of each mailing - the
   narrative trajectory. What did the first mailing establish, what did each
   subsequent mailing build on top of it, and what does the sequence deposit that
   no individual mailing deposits?

2. What ratchet effects operate across mailings? Where does mailing N's deposit
   make mailing N+1's deposit more powerful than it would be standalone? Name
   specific interactions.

3. What is the sequence's cumulative vulnerability? Not each mailing's individual
   vulnerability - the failure mode of the arc itself. What response neutralizes
   the sequence rather than any single mailing?

4. What does the sequence set up next? Given the full arc, what is the implied
   next mailing? What becomes possible that was not possible before the sequence?

Rules:
- Reference individual mailings by month name, not by recapping their contents.
- Be specific about cross-mailing interactions.
- If the sequence is losing momentum, fragmenting, or contradicting itself, say so.
- Single dashes only. Use " - " for all dashes. Never use em-dashes, double
  dashes ("--"), or Unicode dashes.
- Do not include any reasoning, internal monologue, thinking steps, or
  commentary. Return only the requested output.
```

---

## Public Aggregate Prompt

Pass this prompt verbatim to the Stage A subagent:

```
You have a set of public-facing individual paper summaries from a single WG21
mailing, all by the same author. Your job is to write an executive summary for
a reading-guide paper that will itself be published as a WG21 document.

You must return two clearly labeled items:

ONE-LINER: A single sentence that summarizes the entire collection. It will
appear alone as the first line of the paper's abstract. It must be true,
complete, and hit hard. No hedging. Examples of the register:
- "Twenty-three papers, two working libraries, and one production deployment
  trace the path from C++20 coroutines to standard networking."
- "One author audits a decade of committee decisions on async, builds the
  alternative, and ships the code."

EXECUTIVE SUMMARY: 5-10 paragraphs following the structure below.

Structure:

Step 1 - Identify clusters. Read all summaries and group the papers into
logical series by shared subject, sequential dependency, or explicit
cross-references. A cluster might be "a six-paper retrospective on executor
decisions," "a four-paper coroutine-native architecture," "a pair of interop
bridges," or "standalone papers." Name each cluster concisely.

Step 2 - Write one paragraph per cluster, ranked by reader interest. The
most compelling cluster comes first. Each paragraph opens with the strongest
sentence about what that cluster delivers as a unit - not a paper-by-paper
recap, but the compound payoff of reading the series. What will the reader
understand after reading this cluster that they did not understand before?

Step 3 - Build the value ladder. Across the paragraphs, make three levels
of value explicit and concrete:
- What a single paper gives the reader (a specific tool, finding, or code).
- What a cluster/series gives the reader (a compound understanding no single
  paper achieves).
- What the full collection gives the reader (a qualitatively different
  picture that emerges only from reading across clusters).

Step 4 - Close with a reading guide. Suggest 2-3 papers as entry points
for different reader profiles. Be specific about why each entry point suits
that reader.

Rules:
- WG21 register: no contractions, American English. Punchy and compelling -
  every paragraph opens with its strongest sentence.
- Single dashes only. Use " - " for all dashes. Never use em-dashes, double
  dashes ("--"), or Unicode dashes.
- Write in third person throughout. Never use "you" or "your."
- The goal is to make the reader want to read the papers. Every paragraph
  should increase curiosity, not satisfy it.
- Ground claims in concrete details: line counts, compiler support, benchmark
  numbers, production deployments, field interviews, paper counts.
- Do not mention campaigns, targets, vulnerabilities, strategic positioning,
  manipulation, pressure, or institutional weaknesses.
- Do not describe the author's intent in adversarial terms.
- Do not mention specific individuals as opponents or targets.
- Do not use the words "weapon," "instrument," "ammunition," "pressure," or
  "neutralize."
- Do not include any reasoning, internal monologue, thinking steps, or
  commentary. Return only the two labeled items: ONE-LINER and EXECUTIVE SUMMARY.
```

All content in this file is dedicated to the public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
