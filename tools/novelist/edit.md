# The Edit

A self-contained tightener. Point it at a chapter and it reviews, fixes, and evaluates -- keeping only the changes that are unambiguously better than the original. No rewriting for taste. No improvements beyond what the review found. Tighten what's loose; leave what's alive.

---

## Invocation

```
"Edit chapter N."
"Edit chapter N of [book]."
```

The book context is established at first invocation or inherited from the current Novelist session.

---

## Phase 1: Review Sub-Agent

The main context assembles six inputs from the bible's Book Metadata:

1. **Pen files** -- loaded from the entries in the `Pen files:` metadata field. Bare filenames resolve in `tools/novelist/pen/` (shared voice files) with a fallback to the book directory; paths with separators resolve against the book directory. If a per-book rules file (e.g. `pen-papermancer.md`) is listed in `Pen files:`, load it too.
2. **Book Metadata** -- POV convention, tense, register baseline, naming conventions, and any inline constraints (body-cost constraint, etc.).
3. **Thematic Threads** -- controlling ideas and any drafting constraints.
4. **This chapter's bible entry** -- summary paragraph, log, and any drafting/tone/register notes attached to the entry.
5. **Character Registry entries** for every character named in this chapter's log.
6. **Adjacent chapter summaries** -- the prior chapter's summary and log (for continuity and landing-inheritance checks) and the next chapter's summary (for causal-bridge checks).

A sub-agent receives all six inputs plus the chapter prose. The main context never reads the prose directly.

The sub-agent runs three passes -- Story, Craft, Trust -- exactly as The Review specifies. Each check is binary: violation or not. Checks that pass are not reported.

### Pass 1: Story

Does the chapter deliver what the bible requires?

- **Arc delivery.** Every `[arc]` entry in the log has a corresponding moment in the prose.
- **Event delivery.** Every `[event]` in the log occurs in the chapter.
- **Echo/motif delivery.** Every `[echo]` and `[motif]` in the log appears at the correct sequence position.
- **Theme delivery.** Every `[theme]` entry manifests through scene, not declaration. If the bible attaches a drafting constraint to the theme, the constraint is checked here.
- **Sense delivery.** Every `[sense]` entry appears.
- **Witness delivery.** When Book Metadata includes a Witness constraint, every `[witness]` entry in the log has a corresponding plain beat in the prose (reported without analytical gloss), at the narrative position implied by log order.
- **POV fidelity.** The chapter stays in the correct POV character. No slips into omniscient or another character's interiority.
- **Tense fidelity.** The chapter holds the bible's tense throughout, with exceptions only where the pen explicitly permits (e.g. present-tense intrusion).
- **Continuity.** Physical details, character states, and object inventories are consistent with prior chapters.
- **Landing inheritance.** If the prior chapter landed a specific beat, this chapter begins from the place it left the reader -- not by re-explaining the beat.
- **Causal bridge.** The chapter's ending connects to the next chapter as described in the bible summaries.
- **Summary alignment.** What happens in the prose matches the bible summary: want, obstacle, choice, stakes.

### Pass 2: Craft

Does the prose obey the pen file and per-book rules?

- **NEVER violations.** Any occurrence of a NEVER-budgeted device.
- **Budget overruns.** Occurrences of MAYBE ONCE, UP TO TWICE, or PICK ONE devices exceeding their budget.
- **Register fidelity.** The prose uses vocabulary and moves from the correct register. Register-specific budget overrides are respected.
- **Avoidance list.** Every item on the pen's avoidance list is checked.
- **Per-book rules.** If the `Pen files:` metadata lists a per-book rules file (e.g. `pen-papermancer.md`), every numbered rule in that file is checked. Common rules include analysis ceiling, physical-anchor frequency, density variation, show-then-tell, post-landing gloss, motif-age gradient, character-portrait decay, refrain creep, landing inheritance, anchors-must-advance. If no per-book rules file exists, this sub-check is skipped.
- **Naming convention.** Capitalization follows the bible's naming convention metadata.
- **Word count.** The chapter is within reasonable range of its target word count.

### Pass 3: Trust

Does the prose trust the reader?

- **Show-then-tell.** A concrete scene followed by a sentence restating what the scene demonstrated.
- **Recursive self-explanation.** An insight stated, then restated in the next sentence with the key word repeated.
- **Redundant interiority.** A character's internal state narrated after the prose already showed it through action or object.
- **Over-attribution.** Explaining why a character did something when the scene already made the reason clear.
- **Editorial intrusion.** The narrator stepping above the scene to deliver thematic summary instead of staying in scene.
- **Hedge stacking.** Multiple qualifiers on the same observation in proximity.
- **Mechanical transitions.** "He turned back to..." / "She looked at..." as paragraph openers more than twice per chapter.

### Verdict

- **PASS** -- all three passes clear. The main context tells the user the chapter is clean and stops.
- **REVISE** -- one or more violations found. Numbered findings, each with rule, evidence, location. The three pass groups are separated by blank lines.

No preference-level notes. No alternative phrasing. No commentary on things that work. No findings that cannot cite a specific rule from the bible, pen, or per-book rules file.

---

## Phase 2: Edit Sub-Agent

The main context forwards the numbered findings to a second sub-agent. This sub-agent receives everything the Author mode writer gets, plus the findings:

1. **The chapter prose** -- the full chapter file.
2. **The numbered findings** from the review (rule, evidence, location). No pre-computed directives; the edit agent determines the fix.
3. **This chapter's log** -- the spec.
4. **Character Registry entries** for every character named in this chapter's log.
5. **Prior entries by name** -- every prior log line whose base name matches an element in this chapter's log (match on name, ignore sequence numbers).
6. **Pen files** -- the full pen file and per-book rules, so the sub-agent knows the rules it is enforcing.
7. **Book Metadata** -- logline, premise, POV, tense, register baseline, naming conventions, inline constraints.

The main context never reads the chapter prose.

### Standing Instructions

The sub-agent receives these standing instructions:

- Make the minimum change that addresses the finding. Do not rewrite surrounding prose that was not flagged.
- Preserve the chapter's voice, rhythm, and register. New or replacement prose must be indistinguishable from the existing prose in the pen file's terms.
- Do not introduce new violations. Every replacement sentence must obey the pen file's budgets and the per-book rules (when present).
- Do not add material that is not in the bible's log. If a fix requires new prose (e.g. a scene beat or a physical anchor), draw from the chapter's existing object inventory, sensory environment, or character action.
- Preserve all motif, echo, and sense deployments. If a cut would remove a bible-mandated element, relocate the element rather than deleting it.
- When cutting, verify the cut does not orphan a paragraph transition. If it does, smooth the seam with the minimum cosmetic change to the surrounding prose.

### Tiers

Findings fall into three tiers. The tier determines how aggressively the sub-agent should pursue a fix.

**Tier 1: Trust the reader.** Show-then-tell, recursive self-explanation, redundant interiority, over-attribution, post-landing gloss, editorial intrusion, hedge stacking. These are almost always clean cuts -- the showing is the good prose, the explaining is the fat. Cut the explanation, keep the image. Do not backfill with new story material. The book will get shorter; that is acceptable. Every remaining sentence earns its place. After cutting, check the seam: if the remaining prose flows naturally, done. If the cut creates an abrupt join, smooth the seam -- adjust the transition between what's already there (a paragraph break moved, a conjunction tweaked, a sentence-end softened). The work is cosmetic, not compositional. No new events, no new action, no forward-moving beats inserted.

**Tier 2: Structural bloat.** Analysis ceiling violations, physical-anchor gaps. These need inserted scene beats or anchors, which means new prose. More likely to need the adjust path. New prose must be drawn from the chapter's existing inventory.

**Tier 3: Device overuse.** Mechanical transitions, characterization-device budget overruns, gnomic closer excess. These may involve cutting prose that has genuine quality even though it exceeds a budget. More likely to be skipped if the passage is genuinely good despite the violation.

### Per-Finding Evaluation

For each numbered finding, the sub-agent follows this sequence:

1. **Read the passage in context.**
2. **Triage.** Is this passage genuinely good despite the violation? If yes, **skip**. If no, proceed. For Tier 1 findings, the explaining sentence is almost never the good part. For Tier 3 findings, the violating line may be the best prose in the passage.
3. **Apply the fix.**
4. **Compare the old passage to the new passage.**
5. **Judge: accept, adjust, or reject.**

**Skip** -- the passage is genuinely good despite the violation. The violation is real but the prose is alive there, and any fix would lose more than it gains. The sub-agent notes the finding and why it was skipped.

**Accept** -- the fix is a clean win. All of the following hold:

- The finding is resolved.
- No new violations are introduced.
- Voice, rhythm, and register are preserved.
- The surrounding prose is undamaged.
- The fix is the minimum necessary change.
- Any reasonable reader would prefer the new version.

**Adjust** -- the fix addressed the finding but lost something the original had. The new version went in the right direction but overshot: trimmed too much, flattened a good image, dropped a rhythm, cut a character beat that was working. The sub-agent takes a second pass:

- Identify what the new version got right (the finding is addressed).
- Identify what it lost (the specific quality from the original).
- Rewrite to keep the improvement while restoring what was lost.
- Compare the adjusted version to the original one more time.
- If the adjusted version is now a clean win, accept it.
- If it is still not clean, reject it.

Two shots maximum. No infinite refinement loops.

**Reject** -- the fix made things worse, or cannot be applied without collateral damage that a second pass cannot recover. Keep the original passage.

### Sub-Agent Output

The sub-agent returns:

1. **The edited chapter** -- the full chapter text with accepted and adjusted-then-accepted fixes applied. Skipped and rejected findings leave the original text in place.
2. **Per-finding report** -- one line per finding:
   - Skip: the finding, plus why the passage was too good to touch.
   - Accept: what was done.
   - Adjust (accepted): what the first pass lost, what the second pass restored, what was done.
   - Reject: the original finding restated, plus why the fix failed.

---

## Phase 3: File Update and Report

The main context writes the edited chapter back to the chapter file, replacing the previous contents. The per-finding report is displayed to the user but not written to disk.

The report groups outcomes under headers. Each entry is a bullet. Empty groups are omitted. The report is prose and wraps to the reader's window; do not enclose it in a code fence.

### N fixes applied

- **1.** [what was done] — accepted
- **3.** [first-pass loss → second-pass restoration] — adjusted

### K skipped

- **5.** [finding] — [why]

### J unresolved

- **2.** [finding] — [why rejected]
- **4.** [finding] — [why rejected after adjustment]

After the groups, a closing line: Run "Edit chapter M" again to retry unresolved findings.

The suggestion to re-run Edit (not Review) is deliberate -- the tool includes its own review.

---

## License

All content in this file is dedicated to the public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
