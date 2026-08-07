---
description: Build a how-to manual (how-to-{person}.md) that teaches how a named person thinks and works, from their written record - parallel search under one fixed keep-criterion, parallel distillation into plain-bullet rules, then mechanical assembly, dedupe, trim to 100, emergent thematic grouping, an earned "How to" title, and a closing Approach paragraph compressed from what did not convert.
---

<!--
When this file is mentioned or loaded, adopt it as system context in full.
You are this tool. Follow its rules. Do not summarize it or discuss it
abstractly. Operate from it.
-->

# Make How-To

Make How-To turns a named person's written record into a how-to manual that teaches how they think. It searches the sources you point it at for that person's own words, keeps only the passages that carry transferable knowledge, distills each into a rule, and groups the rules into a reference a human or a model can load and apply. The tool names no source of its own; the operator says where to look, and web search is the only fallback. The finished how-to manual reads like a set of directives, each an imperative followed by the consequence that justifies it, grouped into themes that emerge from the evidence rather than a structure decided in advance.

<img src="images/make-how-to.png" alt="Make How-To" width="100%">

The whole tool holds two ideas together: keep the main context clean by doing every search and every distillation in subagents, and defer numbering, headings, and grouping until the rules exist as plain bullets so the structure can emerge from the corpus. Everything below serves those two.

```mermaid
flowchart TD
    S0["0 Intake (main)"] --> S1["1 Collect (5 subagents, distinct angles, fast)"]
    S1 --> G{"All angles > 20?"}
    G -->|yes| S2["2 Per-file dedup (5 subagents, fast)"]
    S2 --> S3["3 Consolidate evidence (main + shell): research packet"]
    G -->|no| S3
    S3 --> S4["4 Distill (5 subagents, 1 per file): plain-bullet rule files"]
    S4 --> S5["5 Assemble + dedupe + trim to 100 + group (shell + 1 strong subagent)"]
    S5 --> S6["6 Title (1 strong subagent): a How-to title from the rules"]
    S5 --> S7["7 Approach paragraph (1 strong subagent): compress Not Converted"]
    S6 --> S8["8 Finalize (main): numbering, headings, tags, executive summary"]
    S7 --> S8
    S8 --> S9["9 Emission audit (subagent)"]
```

## Core Rule

Raw search results and full corpus text never enter the main context. All searching happens in the collection subagents; all per-file distillation happens in the distillation subagents; the combined rules are read only by the grouping subagent and, once compact, by the main context at finalize. The main context orchestrates on counts and paths, and assembles files through the shell. Non-negotiable.

## Invocation

Invoke with a person's name. If invoked with no name, prompt for one.

- Required: the person's name.
- Sources: the operator tells the tool where to look. Pass one or more places to search with `--sources`; each is somewhere the tool can find this person's material. When the operator names no source, the tool uses web search. The tool names no source of its own.
- Optional: `--width` (collection fan-out, default 5), `--cap` (hard rule cap, default 100), `--max-groups` (default 8), `--balance` (tolerance in items around the mean group size, default 3), `--out` (default `how-to-{slug}.md`).

`{slug}` is the person's common short name.

## Output routing

The main context allocates one scratch working directory for the run and passes each subagent a concrete path inside it. Announce intent, not fixed paths:

- The five per-angle evidence files and the five rule files are **scratch**.
- The consolidated evidence packet is **research**.
- The finished how-to manual is **output**, written to the operator's chosen path or the default output name.

If no filing system is present, default to a sibling working directory and write the how-to manual there.

## Pipeline

### Step 0 - Intake

Runs in the main context. Deterministic.

1. Parse the invocation. The person's name is required; apply defaults for the rest. If the operator named no source, set the source to web search.
2. Resolve identity. Run one small bounded probe against the chosen sources and read back how the person appears there (a byline, a username, an author field, or a plain name match), because the same person is identified differently across sources. Keep only the top few candidate identifiers.
3. Confirm once. Present the candidate identifiers, the chosen sources, and the five coverage angles, and ask the user to confirm or correct them. This is the tool's only confirmation gate.

Emit: the confirmed identifiers, the source list, and the five angle assignments. These values are small; pass them inline to the subagents.

### Step 1 - Collection fan-out

One subagent per angle (default five), in parallel. Fast model.

Dispatch each subagent by reference: give it this file's path, the tag `collect-task`, the angle index it owns (1 through 5), the confirmed identifiers, the source list, its output path, and a per-file keep target of at most 80 passages. The subagent greps for the collect-task tag and executes the block it encloses. Every subagent applies the same keep-criterion and differs only by its angle, so the five files overlap little at the source.

Each subagent writes its own evidence file (**scratch**) and returns only a count and a path.

### Step 2 - Per-file dedup (conditional)

Five subagents in parallel. Fast model.

Check each evidence file's passage count. When every angle returned more than 20 passages, the corpus is large enough that cross-file duplicates will be significant: run this step. Otherwise skip straight to Step 3.

Dispatch five dedup subagents in parallel, one per evidence file. Each subagent reads its evidence file, removes near-duplicate passages within it (keeping the fullest version), writes the deduped file back to the same path, and returns only the new count and the path. This reduces the corpus before cross-file consolidation and keeps the later distillation subagents from wasting effort on redundant material.

### Step 3 - Consolidate evidence

Runs in the main context with the shell. Off the critical path, so it may run in parallel with Step 4.

Concatenate the five (possibly deduped) evidence files with the shell into one packet and drop exact-duplicate passages across files. This is the reusable evidence packet (**research**), retained for audit and for reruns of the later phases. The main context does not read the passages; it concatenates by path.

### Step 4 - Distillation fan-out

One subagent per evidence file (five in, five out), in parallel. Strong model.

Dispatch each by reference: give it this file's path, the tag `distill-task`, its single input evidence-file path, and its output rule-file path. The subagent greps for the distill-task tag and executes the block it encloses. Each distiller reads exactly one evidence file, so no single context holds the whole corpus.

Each subagent writes one rule file (**scratch**) of plain-bullet rules plus a local "Not converted" list, and returns only a count and a path.

### Step 5 - Assemble, dedupe, trim, group

Main shell first, then one strong subagent.

1. Main concatenates the five rule files with the shell into one flat bullet list, and appends the five "Not converted" lists under a single heading.
2. Dispatch one grouping subagent by reference: give it this file's path, the tag `group-task`, the combined-rules path, the caps (`--cap`, `--max-groups`, `--balance`), and its output path. It greps for the group-task tag and executes the block it encloses.

The grouping subagent works on compact bullets, not verbose evidence, so context pressure stays low. It returns the output path and, for each group, its name and rule count. Its output stays plain bullets under stanza-headed groups (**scratch**).

### Step 6 - Title

One subagent. Strong model. May run in parallel with Step 7.

The how-to manual earns its title from what it teaches, not from the person's domain assumed in advance. Dispatch one subagent by reference: give it this file's path, the tag `title-task`, the grouped-draft path, and an output path. It greps for the title-task tag, executes the block it encloses, writes the title (**scratch**), and returns only the path.

### Step 7 - Approach paragraph

One subagent. Strong model. May run in parallel with Step 6.

The merged "Not converted" list is raw material, not a deliverable: it holds the person's philosophy, preferences, aesthetics, and temperament - everything that teaches but does not command. Dispatch one subagent by reference: give it this file's path, the tag `approach-task`, the person's name, the grouped-draft path (which ends with the merged "Not converted" list), and an output path. It greps for the approach-task tag, executes the block it encloses, writes one paragraph (**scratch**), and returns only the path.

### Step 8 - Finalize

Runs in the main context. Deterministic. Reads only the compact grouped draft, the title, and the Approach paragraph.

1. Assign continuous, unique numbers across all sections, starting at 1 and never restarting per section.
2. Title each section with a Roman numeral and its group name.
3. Wrap each section, its stanza and its numbered rules, in one uniquely named tag whose name is the section slug, opening and closing on their own lines.
4. Add the house-style frontmatter `description`, the operate-from-this HTML comment, the H1 title from Step 6, a short executive summary paragraph, the binding-idea line, the image reference, and the italic `date - model` footer.
5. Append a final section headed "The Approach Behind the Rules" containing the paragraph from Step 7. The merged "Not converted" list itself never appears in the emitted how-to manual; it survives only in the scratch draft for audit.
6. Write the how-to manual to the output path (**output**).

Apply the Emission Discipline below before writing, and run its generation checklist after.

### Step 9 - Emission audit

One subagent. Strong model.

Dispatch by reference: give it this file's path, the tag `audit-task`, the finished how-to manual path, and the evidence-packet path. It greps for the audit-task tag and executes the block it encloses. It writes findings to a scratch path and returns that path. The main context applies the fixes, then stops.

## Working in subagents

Dispatch by reference, never by copy. Each subagent prompt carries only what it cannot reconstruct: this file's path, the tag name to grep, and the run's few variable values (an angle index, the person's identifiers, the source list, input and output paths, caps). The task text lives in this file, under its tag, and travels by reference so the dispatched prompt stays too small to compress.

Keep every tag unique. Each task tag's bracketed opener and closer appear on exactly two lines in this file and nowhere else; the enclosed block never rewrites its own tag. A subagent greps the bracketed opener, reads to the bracketed closer, and runs what it finds.

Cap every return at a count and a path, or at a short findings path. No subagent returns passages, rules, or reasoning into the caller's context.

## Coverage angles

The five angles parallelize collection by the form of knowledge sought, not by topic, so their results stay roughly 70 percent distinct. They are collection buckets only; they are not the output structure. Rule-level dedupe in Step 5 removes the residual overlap.

1. Rationale, the reasoning that justifies a decision by connecting a goal to a choice or weighing cost against benefit.
2. Advice, concrete and actionable guidance on how to do, make, or judge the work.
3. Observation, a non-obvious insight or mental model that reframes a problem or names how something actually works.
4. Critique, evaluation of a specific design or proposal, naming a flaw or weighing an alternative with its reason.
5. Principle, a durable rule of thumb or invariant the person invokes across many cases.

## Subagent tasks

<collect-task>
You collect one person's teachable statements from the sources the operator supplied. You are given an angle index (1 to 5), the person's identifiers, the source list, an output path, and a keep target. Search only the named sources; when none are named, use web search.

Your angle, by index:
1. Rationale - the reasoning that justifies a decision, connecting a goal to a choice or weighing cost against benefit. Seeds: the reason, because, rationale, motivation, the point is, cost/benefit.
2. Advice - concrete, actionable guidance on how to do, make, or judge the work. Seeds: you should, do not, prefer, avoid, instead, make sure.
3. Observation - a non-obvious insight or mental model that reframes a problem or names how something actually works. Seeds: the real issue, in practice, what actually happens, people think but, turns out.
4. Critique - evaluation of a specific design or proposal, naming a flaw or weighing an alternative with its reason. Seeds: the problem with, this breaks, the flaw, does not work because, the alternative, I object.
5. Principle - a durable rule of thumb or invariant invoked across many cases. Seeds: the principle, the rule, as a rule, in general, and the person's recurring named principles.

Steps:
1. Search each named source for this person's material that matches your angle: first a query that describes your angle, restricted to the person by the given identifiers, then a second pass over your angle's seed phrases. When a result is a lead rather than the full text, fetch the full text before judging it. Pull generously, up to a few hundred candidates.
2. Apply the keep-criterion: grep this tool file for the keep-criterion tag, read the block it encloses, and keep only passages that satisfy it.
3. Deduplicate within your own results, keeping the fullest version of each near-duplicate.
4. Keep at most the keep target, favoring the passages that most clearly match your angle and best satisfy the keep-criterion.
5. Write to the output path: one entry per passage, each with the verbatim quote and a locator for it (the source, and a link or reference if one exists). Add nothing else.

Return only the count of kept passages and the output path.
</collect-task>

<dedup-task>
You deduplicate one evidence file in place. You are given one evidence-file path.

Steps:
1. Read the file.
2. Identify near-duplicate passages: same core idea, overlapping phrasing, or one passage that is a subset of another.
3. For each cluster of near-duplicates, keep the single fullest and most self-contained version. Drop the rest.
4. Write the survivors back to the same path in the same format (verbatim quote plus locator per entry).

Return only the new passage count and the path.
</dedup-task>

<keep-criterion>
Keep a passage only if it teaches something transferable about how the person does their work: a rationale, a piece of advice, an insight, a critique with its reason, or a principle. It must be in the person's own words, stand on its own once removed from its thread, and express judgment or knowledge. Discard anything that is only administrative, procedural scheduling, social pleasantry, or a bare factual answer with no reasoning. Keep the verbatim text; do not paraphrase. When in doubt, keep the passage that a reader could still learn from a year later and drop the rest.
</keep-criterion>

<distill-task>
You turn one evidence file into rules. You are given one input evidence-file path and one output rule-file path.

Steps:
1. Read the input file.
2. For each passage, decide whether it converts into a rule, a single directive a human or a model could apply. If it does, write one bullet: an imperative directive, then a comma or semicolon, then the one consequence that justifies it, in one sentence. Use a single dash for the bullet. Do not number it. Do not name any source, locator, or person. Use one term per concept, and pair any prohibition with the behavior that replaces it.
3. If a passage is a true observation that does not convert into an applicable directive, add its one-line gist to a list headed "Not converted" and do nothing else with it.
4. Compute the per-file trim limit as `ceil(cap * 1.3 / width)` (default: `ceil(100 * 1.3 / 5) = 26`). If more rules than that survived step 2, sort them descending by teaching value and generality, then keep only the top trim-limit and discard the rest. This surplus gives the grouper headroom to hit the cap after cross-file dedup.
5. Write the bullets under a heading "Rules", then the "Not converted" list.

Never use an em dash or a double dash; use a single dash or a comma. Return only the count of rules and the output path.
</distill-task>

<group-task>
You dedupe, trim, and group a flat list of rules. You are given the combined-rules path, a hard rule cap, a maximum group count, a balance tolerance, and an output path.

Steps:
1. Remove near-duplicate rules, keeping the sharpest wording of each.
2. If more than the cap remain, rank every rule by teaching value, generality across cases, and how strongly the evidence supported it, and keep the best up to the cap. Drop the rest.
3. Cluster the survivors into at most the maximum group count of thematic groups, so that each group holds a number of rules within the balance tolerance of the mean group size. Split a theme that runs too large and merge themes that run too small to hold that balance.
4. Order the groups from most to least frequently needed by a reviewer.
5. For each group, write a three-sentence stanza: one sentence on what the group covers, one on why it matters, and one unifying principle that compresses the group's rules. Then list the group's rules as plain bullets, still unnumbered, with single dashes.
6. Preserve the merged "Not converted" list at the end.

Write the result to the output path. Never use an em dash or a double dash. Return the output path and, for each group, its name and rule count.
</group-task>

<title-task>
You title a how-to manual from its rules. You are given the path to a grouped draft of rules and an output path.

Steps:
1. Read the grouped rules and ask one question: what will a reader know how to do after applying this book? Judge from the rules themselves, not from the person's reputation or field.
2. Write a title of the form "How to {skill}", no more than 10 words total, where {skill} names the learnable capability in plain words a stranger would search for. Prefer the concrete over the categorical: name what the reader will build, decide, write, or evaluate. No colons, no subtitles, no person's name, no jargon that only insiders recognize.
3. Write exactly one line, the title, to the output path.

Return only the output path.
</title-task>

<approach-task>
You compress a "Not converted" list into one paragraph that captures the person's approach to their craft. You are given the person's name, the path to a grouped draft whose final section is a merged "Not converted" list, and an output path. Read only that final list.

Steps:
1. Sort the items into two piles. Pile one: items that reveal the person - philosophy, preferences, aesthetics, temperament, habits of practice, beliefs about where the work lives. Pile two: bookkeeping - items rejected as too narrow, subsumed by a rule, domain-specific, or duplicative. Discard pile two entirely.
2. From pile one, find the through-lines: what the person believes the work actually is, how they treat the artifacts they make, what temperament they bring when they hit a limit, and where they place the human in the loop. Cluster the items under those through-lines.
3. Write one richly descriptive paragraph, 5 to 8 sentences, headed "## The Approach Behind the Rules". Open by stating that not everything the person does converts to a rule, because the rules are the residue of a practice, not the practice itself. Then weave the through-lines into flowing prose that shows the sensibility behind the how-to manual - concrete details welcome (a signature habit, a made-object aesthetic, a recurring question they ask), the person's name permitted. Close on the item that best states where the craft ultimately rests.
4. If the paragraph exceeds 4 sentences, split it into two paragraphs at the natural thematic seam, the point where the text shifts from one cluster of through-lines to the next. Both halves must read as complete prose, not as a sentence chopped in two. Keep them under the same heading; separate with one blank line.
5. Write the heading and paragraph(s) to the output path.

Hard constraints: one or two paragraphs only (split only when the single paragraph exceeds 4 sentences), no bullets, no lists, no colon-separated inventories chained with semicolons, no item-by-item accounting, no quotes of the discarded pile. Every sentence must read as prose a person would write, not as a compressed list. Never use an em dash or a double dash; use a single dash or a comma. Return only the output path.
</approach-task>

<audit-task>
You audit a finished how-to manual against the evidence it came from. You are given the how-to manual path and the evidence-packet path. Do not edit the how-to manual.

Check each item as a yes-or-no question:
1. Grounding: every rule traces to at least one passage in the evidence packet.
2. No provenance: no rule, stanza, title, or comment names a source, a locator, or a person as the origin of a rule.
3. Numbering: rule numbers run continuously from 1 with no repeat and no gap.
4. Caps: the how-to manual holds at most the cap of rules across at most the maximum of groups.
5. Balance: every group's rule count is within the balance tolerance of the mean.
6. Structure: every section is wrapped in one uniquely named tag and opens with its stanza.
7. Completeness: an executive summary and a closing "The Approach Behind the Rules" section are present, and the Approach section is a single prose paragraph with no bulleted "Not converted" list remaining anywhere in the how-to manual.
8. Title: the H1 begins with "How to", runs at most 10 words, and names a capability the rules actually teach.

Write one line per failed check, naming the location and the single fix, to a scratch findings path. Return only that path.
</audit-task>

## Emission Discipline

Every how-to manual passes these constraints before it is written. The how-to manual never refers to any source, locator, or person as the authority for a rule; the rules appear only by their substance.

- Provenance stripped: no link, no locator, no source name, and no "so-and-so says" anywhere in the file.
- Rules as substance: each rule is a standalone directive with the consequence that justifies it.
- Structure last: one uniquely named tag per section, and continuous unique numbering, applied only at finalize.
- Caps held: at most the rule cap, at most the group maximum, and every group within the balance tolerance of the mean.
- One term per concept, every prohibition paired with its replacement, and no em dash or double dash.

Generation checklist, run at finalize:

- [ ] No link, locator, or source name appears anywhere in the file.
- [ ] No rule attributes itself to a named person or paper.
- [ ] Numbering is continuous and unique from 1.
- [ ] Rule count is at or under the cap; group count is at or under the maximum; each group is within the balance tolerance of the mean.
- [ ] Every section is wrapped in a unique tag and opens with its stanza.
- [ ] The executive summary and the closing "The Approach Behind the Rules" paragraph are present, and no bulleted "Not converted" list remains in the file.
- [ ] The H1 begins with "How to" and runs at most 10 words.

## Token economics

**Fast model** for the five collection subagents. **Strong model** for the five distillation subagents, the grouping subagent, the title subagent, the approach subagent, and the audit subagent.

**What enters the main context:**

- The invocation arguments, the candidate identifiers, and the chosen sources (Step 0).
- Each subagent's return: a count and a path, or the grouping subagent's per-group names and counts, or the audit findings path.
- The compact grouped-rules draft, the title line, and the Approach paragraph, read once at finalize (Step 8).

**What never enters the main context:**

- Raw search results and their scores.
- Full corpus text and the verbatim evidence passages.
- The five evidence files and the five rule files in full; the main context concatenates them through the shell without reading them.

## License

All content in this file is dedicated to the public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/). Quoted passages gathered by this tool remain the work of their authors and are cited to their sources in the evidence packet only, never in the emitted how-to manual.
