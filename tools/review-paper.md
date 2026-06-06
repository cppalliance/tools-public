# Review Paper

Point this tool at any WG21 paper. It reads the paper, researches the context, questions the author, tests every claim, and delivers findings. The findings may be objections. The findings may be nothing - a clean result means the paper held up under every test. A review that always produces objections is performing opposition, not analysis.

Every candidate finding is challenged internally before it reaches the output. A second perspective tests whether the finding is real and worth raising. When the challenge holds, the section is certified strong. When the finding holds, it stands. When neither is clear, the matter is referred to the author for input.

<img src="https://raw.githubusercontent.com/cppalliance/tools-public/master/tools/images/review-paper.png" alt="Review Paper" width="100%">

---

## Operational Directive: File Output

Findings are always written to a file unless the user explicitly requests inline output.

**Default filename:** `{paper}-feedback.md`, where `{paper}` is the document number in lowercase with the revision suffix, derived from the paper's front matter (e.g., `d4003r1-feedback.md` for document D4003R1). If the document number is unavailable or ambiguous, ask before proceeding.

**Output location** is determined by the workspace's ambient filing rules.

**Execution protocol:** Save output after each complete semantic unit (never mid-paragraph). Always save output BEFORE marking plan items done - never the reverse. On resumption: read the plan and last ~30 lines of the output file. Repair any truncated tail. Continue from where output ends, matching existing style. Never rewrite prior content.

---

## 0. Orientation

Do not approach the review expecting to find problems.

A clean result is not a failure. It is the best possible outcome - it means the paper withstood every test. The burden is on each objection to justify its existence, not on the paper to justify its innocence. Before filing any finding, ask: would I prefer this finding not to exist? If yes - if finding this weakness genuinely serves the paper - the finding may proceed. If no - if the finding exists because the reviewer needed something to report - discard it.

---

## Phase I. Setup

### 1. Identify the Paper

Receive the paper. Extract: title, document number, author, target audience. Determine whether it is an ask-paper (proposes a poll, requests adoption, seeks a direction) or an inform-paper (documents, analyzes, places evidence in the record). The distinction governs the entire review. An ask-paper needs consensus among colleagues with different priorities. An inform-paper needs to persuade careful readers that the evidence supports the framing.

If the classification is clear from the text, proceed without asking. State the classification and continue.

If genuinely ambiguous, present the determination and ask the user to confirm using AskQuestion:
- State the determination and reasoning as the prompt
- Offer three options: "Yes, this is an ask-paper", "Yes, this is an inform-paper", "It is both / neither - let me explain"

If the user selects the third option, hear their explanation and proceed with the corrected classification.

---

### 2. Determine the Posture

Check whether the user is the paper's author. Compare the paper's reply-to field against the user's identity.

- **Author's own paper (improvement posture):** Findings are areas to strengthen before presenting. Suggestions say "consider strengthening this." Strong sections say "this holds."
- **Someone else's paper (preparation posture):** Findings are points to understand before discussion. Suggestions say "this is worth discussing." Strong sections say "this is well-supported."

Same process. Same rigor. Different framing.

**How:** Check the reply-to field. If ambiguous - multiple authors, unclear attribution - ask: "Is this your paper?"

---

### 3. Read the Paper

Read the paper end to end. Extract every claim it actually makes - factual and normative, stated and conceded. Quote each with its section reference. These are the claims under review. Nothing outside these claims may be examined. Nothing the paper did not claim may be questioned.

**How:** Three readings.

**First reading (comprehension and claims).** Read end to end. Identify the central thesis in one sentence. Mark every claim the paper makes, tagging each as factual or normative. Factual: dates, numbers, quotes, technical properties, historical assertions. Normative: arguments that X should be Y, proposed rules, design recommendations, process changes, value judgments. Quote the exact text. Note the section. The distinction matters for testing - factual claims are tested against evidence; normative claims are tested against logic and political reality. When a claim rests on an empirical premise offered as evidence ("in our experience," "more often than not," "we have found that"), that premise is itself a factual claim - extract it, tag it, and test it in Rule 6 on its own merits.

**Second reading (boundaries and premises).** Identify what the paper does NOT claim - disclaimers, concessions, what it leaves to the reader. These boundaries constrain the review: do not question what the paper did not claim. Then identify the one or two premises the reader must accept before the paper's central thesis follows. For ask-papers, these are the premises before the recommendation works. For inform-papers, these are the premises before the analysis is meaningful - the assumptions about what belongs in the problem space, which events are significant, or how the boundaries are drawn. These premises are mandatory claims for testing in Rule 6, regardless of how well-supported they appear in the paper's own text. They are tested not as "what the paper got wrong" but as "what you have to accept before the argument works."

**Third reading (coverage).** Flag any section where the paper states a scope but provides treatment of one sentence or a placeholder. For papers targeting multiple audiences, identify which target audience is most likely to object to the thin treatment and why that section matters to them specifically. Underspecified sections become mandatory claims for testing.

**Fourth reading (argument architecture).** Identify the argument structures the paper deploys - elimination arguments, arguments by analogy, and inductive generalizations. For elimination arguments: list every option eliminated and the evidence cited for each elimination. Test whether the conclusion survives if any single elimination is weakened or rehabilitated. For arguments by analogy: identify the structural mapping and test whether the compared structures are genuinely isomorphic. These structures become mandatory items for testing in Rule 6 alongside the premises from the second reading.

---

## Phase II. Research

### 4. Gather Evidence

Assemble the evidence before any examination begins. No examination proceeds without it.

#### 4.1 Check cache

Check for `cache/_{paper}.md` relative to the repository root.

- **Cache miss.** Run full collection (4.2). Write cache file.
- **Cache hit, fresh (< 21 days).** Read cached content. Skip collection.
- **Cache hit, stale (> 21 days).** Load cached content as baseline. Run light refresh: one web search for the paper number + topic scoped to recent activity, one MCP query for recent indexed records. Merge new findings - append, do not rewrite unless directly contradicted. Update timestamp.

**Cache file format:**

```
collected: YYYY-MM-DD HH:MM UTC
model: [full model ID]

# Evidence: [paper number] - [title]

## Paper Reception
[findings]

## Committee History
[findings]

## Referenced Papers
[findings]

## Domain Landscape
[findings]
```

#### 4.2 Collect evidence

Delegate to a single sub-agent using the fast model. The sub-agent searches everything available - web, MCP, workspace - and returns compressed structured findings across four categories. Returns a bullet list per category; each finding has source, date, and substance. Not raw search results. Not full page contents. Structured findings only.

**Paper reception.** Search for the paper number (P and D variants) across web and indexed archives. Find reflector threads, blog posts, social media commentary, trip reports that mention the paper. Record what was said, where, when.

**Committee history.** Search for prior papers on the same subject, prior polls and their results, prior committee decisions in this domain. Check for related papers in the current mailing.

**Referenced papers.** For each paper cited by number, retrieve enough of the cited source to verify the paper's characterization of it.

**Domain landscape.** Search for competing proposals, related active papers, recent developments in the paper's domain. Check for papers targeting the same audience that might be scheduled in the same session.

**Rehabilitated alternatives.** When the fourth reading identified an elimination argument, search for whether any eliminated option has been revived - implementations, papers, or protocols that resolve the costs cited as grounds for elimination. Candidate counterexamples from this search do not enter analysis directly; they are held for user confirmation in Rule 5.

Write the results to the cache file.

#### 4.3 Check prior reviews

Search `reports/` for prior feedback outputs on the same paper. Import prior answers still in force, prior findings still relevant, questions already answered. Discard what has been superseded by revision. Combine evidence and prior review context into the working evidence.

---

## Phase III. Questions

### 5. Question the User

Before analysis, audit every assumption the reviewer is making. Unverified assumptions collapse under scrutiny.

**How:** Three steps.

**Audit.** List every assumption about the paper, its author, and the committee context. For each, attempt to verify from the evidence. Verified assumptions need no question. Unverified assumptions that are plausible but unconfirmed need confirmation. Assumptions that are purely speculative - about intent, private conversations, or committee dynamics - must be asked.

**Ask.** Build a question list from the unverified assumptions, ordered so earlier answers inform later questions. Ask the user one or two at a time using AskQuestion - never batched - because each answer may change the next question. If all assumptions are verified, skip.

**Process.** Update each assumption's status after each answer. If an answer reveals new uncertainty - a committee dynamic not in the evidence, a prior decision not in the record - add a new question. The user may also volunteer context unprompted; this is admitted with the same standing as solicited answers. Continue until all assumptions are resolved or enough ground truth exists to proceed.

**Confirm counterexamples.** If the rehabilitated-alternatives search (Rule 4.2) returned candidate counterexamples to any elimination argument, present them to the user via AskQuestion before they enter analysis: "The evidence search found [N] candidate counterexamples to the paper's elimination of [X]. Before any enter the record, review them. Which, if any, are real?" Nothing from this search enters analysis without user confirmation. Searches directionally aligned with an expected outcome are the most hallucination-prone searches the tool performs.

---

## Phase IV. Analysis

**Burden of proof.** During research, the burden was on the reviewer - evidence must be found before findings can be contemplated. During analysis, the burden shifts to the paper - each claim must withstand scrutiny. During the challenge step, the burden shifts back to the reviewer - every finding must be affirmatively established, not merely undisproved.

### 6. Test Each Claim

For each claim extracted in Rule 3, test it against the evidence and testimony. Four tests per claim. No test is skipped.

**Accuracy.** Does the evidence confirm or contradict the claim? Dates, numbers, quotes, technical properties, historical assertions - each is checked against sources.

**Logic.** Does the argument follow? Trace the logical chain step by step. Identify any gap where the conclusion does not follow from the premises.

**Citation support.** Does the cited evidence actually support the claim being made? A paper may cite a source accurately but draw a conclusion the source does not support.

**Internal consistency.** For any claim supported by quantitative data - cycle counts, throughput numbers, overhead percentages, benchmark results - verify that the numbers are internally consistent. Do the percentage claims match the ratio of the raw numbers? Do multiple benchmarks imply consistent conclusions? Is single-vendor data used to support a platform-general claim without qualification? Inconsistencies become candidate findings.

---

### 7. Draft Candidate Findings

For each claim that fails a test, draft a candidate finding. Every candidate finding must include four elements. A finding missing any element is not filed.

**How:** For each failed test, draft:

- **Quoted text** - the exact words from the paper being challenged, with section reference
- **Failed test** - which test (accuracy, logic, citation support, internal consistency) the claim failed, and how
- **Contradicting evidence** - the specific source, testimony, or logical gap that contradicts the claim
- **Core complaint** - the essential objection in one sentence. A finding whose core complaint cannot be stated in one sentence has no core complaint. It is an observation, not a finding.

Each candidate finding is also classified as one of two types:

- **Miss** - the paper does not address X, but X is relevant and a careful reader would notice the absence.
- **Inconsistency** - the paper addresses X but its treatment is internally contradictory, or its stated scope conflicts with what the proposed changes actually do.

Inconsistency findings are higher severity by default. When both types are present, inconsistency findings are ordered first in the output (Rule 11).

---

### 8. Challenge Each Finding

Before any candidate finding reaches the output, challenge it from a second perspective. Six tests, in order. The order is a funnel: each test is cheaper than the next. A finding eliminated at any stage does not face subsequent stages.

**How:**

**1. Paper already handles it.** Does the paper already address this point - either by explicitly conceding it or by containing material that constitutes a complete defense? Check for explicit concessions first. If none, attempt to defend the claim using only material already in the paper. If the paper's own text provides a complete response to the finding, whether framed as a concession or not, the finding is withdrawn.

**2. Not actually claimed.** Does the paper actually claim what this finding addresses? If the finding addresses an inference the reviewer drew rather than a claim the paper stated, it is withdrawn. The boundaries from Rule 3's second reading apply.

**3. Should have been a question.** Could this finding be dissolved by one question to the user? If a ten-second answer would collapse it, the finding should have been a question during Phase III, not a finding in Phase IV. Referred back for questioning.

**4. Not credible.** Would a reasonable committee member notice this from reading the paper? If the finding exists only because exhaustive machine analysis found it - if no colleague reading the paper would spot it - the finding is suppressed.

**5. Self-defeating.** Does pressing this objection require the objector to also condemn established practice they almost certainly depend on? If the principle behind the finding, applied consistently, would undermine types, patterns, or conventions already in the standard or in wide use, the finding is suppressed - not because it is wrong, but because no coherent reader would make the argument without undermining their own position.

**6. Too trivial.** Typos, formatting, word-choice quibbles, citation formatting, section numbering errors. These are not findings. They are housekeeping. Relegated to minor notes.

---

### 9. Interpret Results

After the challenge step, interpret the results for the whole paper.

**For each surviving finding:** state three things. A finding missing any of the three is not filed.

- **Who.** Name the person, faction, national body, or constituency that would raise this concern. Not "a careful reader" - a named actor from the evidence or testimony. If the reviewer cannot name the actor, the finding exists only in the reviewer's imagination.
- **Where.** Name the forum where the concern would surface: LEWG presentation, reflector thread, national body comment, informal hallway conversation. Different forums carry different weight.
- **What damage.** Name the specific consequence if the concern lands and is not addressed: blocks progress, forces a revision, weakens a specific section, costs political capital, creates noise that distracts from the thesis. The damage determines severity ordering in the output.

**For each section where a finding was killed:** certify it as strong. Note which challenge killed the finding and why the section holds up. This tells the user which parts of the paper are solid - not just "here is what needs work," but "here is what holds up, and why."

**For the paper as a whole:** step back from individual findings. Is the central thesis sound? Does the paper achieve what it sets out to do? The whole-paper assessment may diverge from the sum of individual findings. Three minor findings in the periphery do not undermine a paper whose central thesis is airtight. Zero findings on individual claims do not save a paper whose central thesis is flawed. State the central thesis, state whether it survives, state how individual findings relate to it - do they touch the core, or only the periphery? Then trace the central thesis back to the argument architecture identified in the fourth reading. If the thesis depends on an elimination argument, state whether the elimination survives - whether all eliminated options remain eliminated given the evidence and testimony. The whole-paper assessment must test argument structures, not just individual claims. This assessment directly informs the verdict.

---

### 10. Verify Citations

**Conditional.** This step runs only when no findings survived the challenge step. If the paper has substantive findings, the author will edit - verifying citations on text that will change is wasted work. Run citation verification once, on the final clean text.

**How:** Three passes, delegated to a sub-agent. Then tally.

**First pass (resolution).** Resolve every link:

- Try `wg21.link/pNNNNrN` first
- If 404, try `isocpp.org/files/papers/PNNNNrN.html` and `.pdf` variants
- If still not found, search the workspace - the author's own papers (D-prefixed drafts) are frequently pre-mailing and will not resolve publicly
- A P-number in the paper body that resolves to a D-number link (or vice versa) is not a mismatch - this is expected workflow

**Second pass (verification).** For every resolved link, check whether the cited source says what the paper claims. Compare quotes character by character. Note discrepancies.

**Third pass (classification).** For unresolved links: determine whether the cited paper is the author's own unpublished work or a third-party paper that should be publicly available. Self-citations to unpublished drafts are fine. Third-party papers that should exist but cannot be found are noted as informational.

**Tally.** Count: resolved, unresolved-self, unresolved-third-party. Record the complete citation table for the output. If citation verification produces findings, they are reported and the verdict changes from "no objections" to "with objections."

---

## Phase V. Output

### 11. Write the Output

The posture from Rule 2 governs the language. The content is identical. The framing differs.

- **Improvement posture (own paper):** Findings say "consider strengthening this," "this claim needs supporting evidence before [audience]," "address this before the meeting." Strong sections say "this section is well-supported." The tone is collaborative.
- **Preparation posture (other's paper):** Findings say "this is worth understanding," "this is where a colleague might ask questions." Strong sections say "this is well-supported - no concerns here." The tone is analytical.

**Header:**

```
date: YYYY-MM-DD HH:MM UTC
model: [full model ID]
```

> **Paper:** [title] ([number])
> **Author:** [author]. **Audience:** [audience]. **Type:** [ask/inform].
> **Posture:** [improvement/preparation].

**Body.** The verdict comes first. A reader who must wade through twenty findings to discover the verdict has been subjected to a process, not informed by one. The following sections, in this order. Absent sections are omitted.

**Summary.** One of three:

- **No objections** - The review found no basis to object. The paper is cleared for its audience.
- **With objections** - The review has findings that merit attention. Details follow.
- **Suspended** - The review cannot render judgment because critical information is missing. Pending user input.

**Strengths.** Every section or claim certified strong, with brief explanation of why it holds up. Listed before findings because strength is the higher signal.

**Findings.** Each surviving finding, in order of severity (highest first). Each includes: quoted text, core concern, consequence, and a recommendation (improvement posture) or context note (preparation posture).

**Notes.** Editorial observations too trivial for formal findings. Collapsed or clearly marked as optional.

**Audit trail.** Summary of sources consulted, what candidate findings were challenged, and the outcome of each.

**Citation table.** Included only when Rule 10 ran. A table listing every link in the paper, how it was resolved, and whether quotes matched their sources. D/P number mismatches are noted but not flagged. Unresolved links are marked informational.

**Close.** Summary restated and a one-sentence assessment. This sentence is what the user remembers. If no objections: "The paper is ready for [audience]." If with objections: "The review found [N] findings. The [most severe finding, one phrase] should be addressed before [audience]." If suspended: "The review is suspended pending input on [specific matters]."

---

### 12. Re-review

On subsequent rounds - when the user revises the paper and resubmits - the audit trail from the prior round carries forward. Findings already addressed are not re-filed. Answers already given are not re-solicited. Focus narrows to what changed: new text, revised claims, and whether prior objections were resolved.

Each successive round should be tighter than the last. The paper converges toward a clean result or toward a stable set of objections the user has chosen to accept. Either outcome is legitimate.

**When:** On every subsequent review of the same paper.

**How:** Import the prior audit trail. For each prior finding, check whether the revision addresses it. If addressed, note "resolved" and do not re-file. If partially addressed, note what remains. If not addressed, carry forward with a note that the user has seen the finding and chosen not to act. For new text, apply the full analysis (Rules 6-9). A re-review should produce fewer findings than the first. If it produces more, the revision introduced new problems - note this explicitly.

---

## License

All content in this file is dedicated to the public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/). Anyone may freely reuse, adapt, or republish this material - in whole or in part - with or without attribution.
