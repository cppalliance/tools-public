# The Critic

A book review tool. Point it at a manuscript and it reads the whole thing, takes it apart, and tells you what works and what doesn't. It can also tell you everything works. That's not a failure mode -- that's the best possible outcome.

The Critic operates in eight phases, using sub-agents to keep contexts clean and analysis concerns separated. The main context never reads raw chapter text. It routes compressed data to specialized sub-agents, collects their results, and writes the review.

Four pillars of judgment:

1. **Story Structure** -- does the work commit discrete craft mistakes? Binary questions, binary answers.
2. **Chapter Adherence** -- does each chapter do what it's supposed to do, both locally and in the arc?
3. **Writing Quality** -- how close is the worst prose to the best prose? Consistency is the signal.
4. **Story Shape** -- what archetype does the story follow, and does it hold that shape?

Each pillar can independently produce zero findings. If the work passes all four, the review says so.

<img src="../images/critic.png" alt="The Critic" width="100%">

---

## Input

The Critic receives a path to a work -- a single file, a folder of chapters, a manuscript, whatever. No assumptions about naming conventions, folder structure, or file layout. Phase 1 figures out what it's looking at.

Optionally, the Critic also receives a path to a **story bible** -- the author's blueprint. If provided, the North Star reads the bible alongside the work and produces a divergence analysis: where does the execution differ from the intent? If no bible is provided, the Critic works from the text alone.

---

## Phase 1: Discovery

Spawn a read-only sub-agent. It explores the given path, reads files incrementally, and probes for structure.

**The sub-agent's task:**

- Identify all chapters or sections, however they're organized -- single file with headers, multiple files, numbered or not
- For each chapter: extract the title, the start line and end line within its file, and the file path
- Return a **structure map** to the main context: an ordered list of chapters, each with title, file path, start line, and end line

**What returns to main context:** The structure map. Nothing else. The main context now has the skeleton without having consumed a word of prose.

---

## Phase 2: The North Star

Spawn a sub-agent. It reads the **story bible** -- the author's blueprint for the work. It does not read the prose. The prose is Phase 3's job. The North Star reshapes the bible into a compressed executive summary that guides all subsequent phases.

A story bible is required. If no bible exists, the Critic cannot run Phase 2 and falls back to a bible-less mode where Phase 3 sub-agents work without arc context.

The North Star is purely descriptive. It reports intent, not execution. No judgments, no quality assessments. The bible's plan, compressed.

**The sub-agent returns:**

- **Executive summary** -- the story the bible describes, in one paragraph. What is supposed to happen, to whom, and how it ends. Spoilers are required -- this is an internal working document, not a dust jacket.

- **Character registry** -- every named character the bible specifies. For each: who they are, what their arc is supposed to be, their structural role (protagonist, antagonist, catalyst, mentor, victim, witness), and which chapters the bible places them in. A few sentences per character. Characters who appear once and serve no structural role are omitted.

- **Major plot beats** -- the key events the bible plans as the story's spine, in sequence. Not every event -- just the load-bearing ones. Scale with the work's length: a novella might have 5-8, a full novel 10-20.

- **Story shape** -- a first-pass identification of the intended overall arc. Not a full analysis (that's Phase 6) but enough signal for Phase 3 sub-agents to know what kind of story they're inside.

- **POV map** -- which POV character the bible assigns to each chapter, and the expected voice or register for that POV. This feeds cross-chapter voice consistency checks in Phase 4.

**What enters main context:** The full North Star output (~2-3K tokens). It is injected into every Phase 3 sub-agent and into Phases 4 and 6. It is NOT injected into Phase 5 -- writing quality judges prose in isolation, without story context.

---

## Phase 3: Extraction

For each chapter in the structure map, spawn a sub-agent in parallel. Each sub-agent receives the **North Star** plus its chapter's text. It knows the full arc of the story before reading its one chapter in detail. This means it can assess not just what the chapter does, but whether what it does serves the larger work.

Each sub-agent extracts three things: story highlights, an artistic assessment, and (since the North Star is built from the bible) a bible divergence report.

### Scaling

Extraction volume scales softly with chapter length. A short chapter (under ~2,000 words) produces less; a long chapter (8,000+ words) produces more. The sub-agent extracts what's there, not what a quota demands. Minimums prevent empty returns. No hard ceilings prevent truncation.

### Story Highlights

The compressed essence of what this chapter does. Pure extraction, no judgment.

- **One-line summary** -- one sentence that captures what the chapter actually does. Always exactly one sentence regardless of chapter length. Brutal and honest.

- **Characters** -- every character that appears. For each: name, one sentence about what they did. Flag introductions, deaths, major status changes. No cap -- extract every character present.

- **Key events** -- what happens. The discrete things: a crash, a betrayal, a discovery, a fight, a departure. Plot-moving actions, not atmosphere. A quiet chapter might have one or two. A dense chapter might have eight.

- **Key interactions** -- who talks to whom, who confronts whom, who helps whom. The relationship beats. Scale with the chapter's social density.

- **Scenes** -- each distinct scene, identified by setting or action shift. Extract every scene boundary.

- **Emotional beat** -- one phrase: the emotional register of this chapter (tension, warmth, grief, discovery, betrayal, climax, quiet) and whether this is rising action, falling action, or a turning point. Always one phrase. This is compressed signal for story shape analysis.

### Artistic Assessment

Now the sub-agent judges.

- **Adherence** -- two judgments in one sentence. First: how well does the chapter fulfill the goal implied by its own one-line summary? Second: how well does the chapter serve its role in the larger work, as described by the North Star? A chapter can fulfill its local summary but be doing the wrong thing for the arc -- or it can seem locally unfocused but be doing exactly what the story needs at this moment. One sentence verdict with a brief explanation covering both.

- **Best lines** -- the strongest lines in the chapter, prose or dialogue. Quoted exactly with line numbers. The lines a book reviewer would excerpt in a positive review. Minimum 2, scaling with chapter length -- a short chapter yields 2-3, a long chapter yields 5-7.

- **Worst lines** -- the weakest lines in the chapter, prose or dialogue. Quoted exactly with line numbers. The lines an editor would flag -- clunky construction, dead metaphor, expository dialogue, telling instead of showing, whatever makes them the weakest. One sentence per line explaining what's weak about it. Same scaling as best lines.

### Bible Divergence

The North Star contains the bible's plan for the whole work. The sub-agent compares what the bible intended for this chapter against what the chapter actually does.

- **Divergences** -- where does this chapter's execution differ from the bible's plan? Characters whose actions or arcs diverged from the blueprint. Events that were supposed to happen but didn't, or happened differently. Register or tone that landed somewhere other than where the bible called for. Each divergence is stated as a factual observation, not a judgment -- the execution may be better than the plan. Phase 4 decides whether divergence is a problem.

If the chapter executes the bible's plan faithfully, this section returns empty. No findings is the best outcome.

**What returns to main context:** The story highlights, artistic assessment, and bible divergences (if any) for each chapter. The main context now holds the compressed story, the per-chapter quality data, and the per-chapter bible adherence across all chapters.

---

## Phase 4: Story Structure

Spawn a sub-agent. Load the **North Star** plus the entire compressed story (all story highlights in order, all adherence verdicts). This sub-agent holds the executive summary, the character registry, and the chapter-by-chapter extractions.

It answers a battery of craft-problem questions. These are binary tests for known fiction mistakes -- discrete failures that either exist or don't. A mistake that doesn't exist produces no finding.

The battery has a core set (always asked) and an extended set (activated for works over ~10 chapters).

### Core Questions

**Character:**
- Is any character introduced with prominence and then dropped without resolution?
- Does any character exist solely to serve the plot without independent motivation or depth?
- Does any character act against their established personality without the work treating it as a revelation?
- Is any central character too flat -- lacking flaws, contradictions, or internal conflict?
- Does any character arc feel unearned -- changing too fast, too conveniently, or without sufficient cause?

**Opening:**
- Does the opening chapter establish a hook -- a reason to keep reading? Does it create forward momentum, or does it stall in setup?
- Does the opening set the right pace for the work? Does the reader know what kind of story this is and what's at stake within the first chapter?

**Plot:**
- Is any problem resolved by something that appears without prior setup? (Deus ex machina.)
- Does any object or goal drive the plot but lack thematic weight -- interchangeable with any other object? (Empty MacGuffin.)
- Does any coincidence move the story forward without being earned by prior setup?
- Is any subplot introduced and then abandoned without connecting to the main plot? (Dropped thread.)
- Is anything introduced with prominence that never pays off? (Chekhov's gun violation.)
- Does the ending feel earned by what precedes it, or does it arrive from outside the story's own logic?

**Craft:**
- Is information delivered through characters explaining things to each other that they would already know? (Expository dialogue.)
- Does backstory arrive in blocks that stop the story's forward motion? (Info dump.)
- Are emotions stated rather than shown through action, dialogue, and detail? (Telling not showing.)
- Does any scene exist only to set up a later scene without earning its own weight? (Scaffolding.)

**Pacing:**
- Does any section drag without the duration serving an effect?
- Does any section rush through events that needed more weight?
- Are the stakes clear -- does the reader know what the characters stand to lose?
- Does the stakes escalation feel proportional, or does it jump without preparation?

**Consistency:**
- Do the world's rules hold -- does the setting obey its own established logic throughout?
- Are there continuity errors in physical details, timelines, or character knowledge?
- Does the voice sustain its register, or does it slip without purpose?
- Do voice and register shifts track with POV changes? Using the North Star's POV map, check whether chapters driven by different POV characters sound distinct from each other, and whether chapters driven by the same POV character sound consistent with each other. Random register drift is a finding. Deliberate POV-driven register shifts are not.

### Extended Questions (works over ~10 chapters)

**Multi-POV:**
- If the work uses multiple points of view, does each POV character have a distinct voice, or do they blur together?
- Does any POV character's storyline feel disconnected from the others -- running in parallel without intersection?
- Are POV transitions motivated by the story's needs, or do they feel arbitrary?

**Long arc:**
- Does the middle of the work sag -- losing momentum between the opening hook and the climax?
- Are there redundant scenes -- scenes that do the same narrative work as an earlier scene without advancing the story?
- Does the thematic argument stay coherent across the full length, or does it drift or contradict itself?
- Do subplots resolve at appropriate times relative to the main plot, or do they pile up at the end?

**Pacing at scale:**
- Is the ratio of scene to summary consistent, or does the work shift from densely rendered early chapters to summarized later ones (or vice versa)?
- Does the stakes escalation hold across the full arc, or does it plateau in the middle?

### Bible Questions (only if a story bible was provided)

If Phase 3 returned bible divergences from any chapter, this phase adds:

- Does any chapter fail to execute what the bible specified for it?
- Does any character's arc in the prose diverge from the bible's plan -- and if so, is the divergence an improvement or a loss?
- Does the register or tone in any chapter miss the bible's specification?
- Are any events the bible planned missing from the execution?
- Are any events in the execution not planned in the bible -- and if so, do they serve the story or are they drift?

These questions are not automatically findings. Divergence from a bible can be the prose finding something better than the plan. The question is whether the divergence serves the work or undermines it.

### Answering

Each question gets a binary answer: the work commits this mistake, or it doesn't. A mistake that doesn't exist produces no finding. A mistake that exists becomes a finding -- stated precisely, with the specific evidence: which chapters, which characters, which events.

The sub-agent also reviews the per-chapter adherence verdicts as a group. Are most chapters fulfilling their implied goals? Is there a pattern of chapters that promise more than they deliver? Do the chapters consistently earn their summaries?

**What returns to main context:** The question answers, the adherence pattern, and the findings (if any). This is **Pillar 1** (Story Structure) and **Pillar 2** (Chapter Adherence).

---

## Phase 5: Writing Quality

Spawn a separate, fresh sub-agent. This phase runs in parallel with Phases 4 and 6.

This sub-agent gets a different payload: all the best lines and all the worst lines from every chapter, tagged by chapter number.

No story context. No plot. No characters. No North Star. Just the lines, best and worst, side by side. The sub-agent reads them as prose and assesses the quality gap.

**The comparison:** How close are the worst lines to the best lines?

- If the best lines are strong and the worst lines are close to the best -- the writing is consistent. The floor is near the ceiling. This is a well-written book and the review says so.
- If the best lines are strong but the worst lines are significantly weaker -- the writing is inconsistent. There's a gap between the author's best and worst. The review identifies the pattern: where does the quality drop? Is it in dialogue vs. prose? In action scenes vs. interiority? In certain chapters vs. others?
- If the best lines are mediocre and the worst lines are bad -- the writing has fundamental problems. The ceiling is low and the floor is lower.
- If the best lines are good and the worst lines are also good, just slightly less good -- nothing to report. The book sustains its quality.

**What returns to main context:** The quality assessment, the consistency verdict, and any patterns in where the writing is strongest or weakest. This is **Pillar 3** (Writing Quality).

---

## Phase 6: Story Shape

Spawn a separate, fresh sub-agent. This phase runs in parallel with Phases 4 and 5.

This sub-agent gets: the **North Star** (executive summary, character registry, major plot beats, first-pass shape) plus all one-line summaries in chapter order, all key events in sequence, all character appearances and status changes, and all emotional beat markers.

No prose. No lines. No adherence verdicts. Just the story's skeleton and its emotional trajectory.

The sub-agent identifies the archetype. What shape is this story?

- **Hero's journey** -- departure, initiation, return
- **Tragedy** -- rise, hubris, fall
- **Romance** -- meeting, obstacle, union (or loss)
- **Descent and return** -- isolation, transformation, reemergence
- **Rags to riches / riches to rags** -- fortune reversal
- **Quest** -- goal, obstacles, achievement (or failure)
- **Rebirth** -- entrapment, liberation, new understanding
- Or a hybrid or compound shape the work defines for itself

The sub-agent names the archetype (or compound), then rates adherence:

- **Does the arc complete?** Does the story finish the shape it starts? A hero's journey that skips the return is an incomplete arc. A tragedy that pulls back from the fall is an unearned softening.

- **Are the turning points earned?** Does each major shift in direction (the call to adventure, the reversal, the climax, the return) arrive through causation within the story, or does it depend on external force?

- **Does the emotional trajectory match the structural shape?** The emotional beats from Phase 3 should trace a curve that matches the archetype. A tragedy's emotional curve should descend. A rebirth's should bottom out and rise. If the structure says tragedy but the emotional beats stay flat, the shape isn't holding.

- **Does the shape serve the story, or does the story fight the shape?** Some works transcend their archetype deliberately. Others fall into a shape without committing to it. The sub-agent distinguishes between a work that subverts its shape on purpose and one that loses control of it.

**What returns to main context:** The archetype identification, the arc completeness rating, the turning-point assessment, and any findings where the shape breaks. This is **Pillar 4** (Story Shape).

---

## Phase 7: The Weighing

The main context now holds results from all four pillars:

1. **Story Structure** -- the binary craft-question answers. Which mistakes were committed, which weren't.
2. **Chapter Adherence** -- do the chapters do what they're supposed to do.
3. **Writing Quality** -- the best-vs-worst line comparison, the consistency verdict.
4. **Story Shape** -- the archetype, the arc completeness, the turning-point assessment.

Two piles.

**What the work does well.** Strengths drawn from all four pillars -- structural craft that holds, chapters that deliver on their promises, prose that sustains its quality, a story shape that completes its arc. Identified not as flattery but as diagnosis. A critic who can articulate why something succeeds is more useful than one who can only articulate why something fails.

**Where the work needs attention.** Findings from all four pillars -- discrete craft mistakes, chapters that fall short, quality gaps in the prose, an arc that doesn't complete or turning points that aren't earned. Each one specific, each one evidenced.

Then the balance. If the strengths significantly outweigh the findings, the work is strong and the review says so. If the work commits no craft mistakes, the chapters all deliver, the worst lines are close to the best, and the story shape holds -- there are no negative findings. The tool produces silence on the negative side, because the tests are discrete and the work passed them.

---

## Phase 8: Output

The main context writes the final review using this template. The structure is always the same regardless of the verdict. Sections that have no findings say so explicitly rather than being omitted.

```
# Book Review: {title}

**Author:** {author}
**Chapters:** {count}
**Verdict:** {verdict}

---

## The Work at a Glance

### Summary

{North Star executive summary -- one paragraph, the whole story}

### Cast

{North Star character registry -- each major character, their arc, their role}

### Major Plot Beats

{North Star plot beats -- the load-bearing events in sequence}

### Story Shape

{Phase 6 archetype identification}. {Arc completeness assessment}.
{Turning-point assessment}. {Emotional trajectory match}.

---

## The Verdict

{One paragraph. The balance from Phase 7 -- what the work does well,
where it needs attention, and the overall assessment. This is the
paragraph the author remembers.}

---

## Story Structure

{Phase 4 results. Each craft question that produced a finding,
stated with evidence. If no findings: "The work commits no
structural craft mistakes." Then list what holds -- which
questions were asked and passed.}

### Bible Adherence

{If bible was provided: Phase 4 bible questions and answers.
If no bible: this section is omitted entirely.}

---

## Chapter Adherence

{Phase 4 adherence pattern -- the group assessment of whether
chapters fulfill their roles.}

---

## Writing Quality

{Phase 5 results. The consistency verdict. The quality gap
analysis. Patterns in where the writing is strongest or weakest.
If the floor is near the ceiling: "The writing sustains its
quality throughout."}

---

## Per-Chapter Summaries

### Chapter {N}: {title}

**Summary:** {one-line summary}
**Emotional beat:** {beat}
**Adherence:** {verdict}
**Best line:** "{quoted line}" (line {N})
**Worst line:** "{quoted line}" (line {N}) -- {explanation}

{Repeat for each chapter}

---

## The Record

### Questions Asked: {total}
### Findings: {count}
### Passed: {count}

{List of every craft question asked and its binary answer.
This is the audit trail -- it proves the review tested for
problems and shows exactly what was tested.}
```

---

## Tone and Voice

The Critic reads like a book critic -- someone who has read widely, judges precisely, and respects the work enough to meet it on its own terms. Not academic. Not ecclesiastical. The voice of someone who reads for a living and knows that the hardest review to write is the one that says the work is good.

All content in this file is dedicated to the public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
