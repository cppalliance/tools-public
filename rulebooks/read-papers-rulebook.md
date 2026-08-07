# Rulebook: Reading Technical Papers

Rules for reading a paper to evaluate its quality. Give this document to a model along with a paper; the paper under evaluation is called the target. The method is three passes, each building on the last: the first pass yields the general idea, the second the content, the third the depth a verdict needs. Passes are sequential stages with exit criteria, not simultaneous demands; run each to its exit before starting the next, and stop at the depth the task requires.

![The Scholar](images/read-papers-rulebook.png)

## 1. Protocol

Execute these steps in order when given a target:

1. Set the depth from the ask before reading: triage needs the first pass, a content summary needs the first two, a quality verdict needs all three. When no depth is named, run all three.
2. Run the passes in section order: scan (2), grasp (3), re-implement (4). Complete a pass and record its findings before starting the next.
3. Claim no more depth than the passes run: a verdict from one pass is a triage note, not a review.
4. Apply section 5 when the task is a literature survey of a field; it schedules the passes across many papers. Skip it for a single target.
5. Report in the section 6 format, findings before verdict.
6. Before returning, run the section 7 checklist on your own report and fix what fails.

## 2. First pass: scan

- Read the title, the abstract, and the introduction in full.
- Read every section and sub-section heading; skip the body text under them.
- Read the conclusion in full.
- Scan the reference list: note its size, its recency, and whether the foundational work you would expect for this topic appears.
- Answer the five Cs, 1-3 sentences each:
  - Category: what type of paper is this - a measurement paper, an analysis of an existing system, a description of a research prototype, a proposal?
  - Context: which other papers is it related to, and which theoretical bases does it build on?
  - Correctness: do the assumptions appear valid?
  - Contributions: what are the paper's main contributions?
  - Clarity: is the paper well written?
- Apply the one-pass test to clarity: most reviewers and readers make only one pass, so a paper whose gist cannot be recovered from title, abstract, headings, and conclusion has failed its audience. Record that as a clarity defect regardless of what later passes reveal.
- If you lack the background to parse even the abstract and headings, say so now and cap verdict confidence at low; do not guess onward silently.
- Exit: the five Cs are answered. When the ask is triage, stop here and report them.

## 3. Second pass: grasp

- Read the whole paper; skip proofs and detailed derivations.
- Record each section's key claim paired with the evidence the section offers for it.
- Scrutinize every figure, graph, and table: axes labeled, units given, error bars or significance shown, and conclusions actually supported by the plotted data. Sloppy figures separate rushed work from excellent work, so weigh them in the verdict.
- Mark relevant references you have not read; they map the paper's background and feed section 5 when a survey follows.
- Exit: you can summarize the main thrust in under 250 words with the 3-5 strongest pieces of supporting evidence, at a level you could defend to a domain expert.
- If you cannot reach the exit, diagnose why and attribute honestly. Unfamiliar terminology or an unknown technique is a reader gap: name what is missing and lower verdict confidence. Unsubstantiated assertions, undefined terms, and numerous forward references are paper defects: record them as findings. Never blend the two; a disguised reader gap becomes a false defect, and a disguised defect becomes false praise.

## 4. Third pass: re-implement

- Virtually re-implement the target: adopt the authors' assumptions, then re-derive the design, proof, or experiment yourself before re-reading how the authors did it.
- Compare your reconstruction with the actual paper; classify every difference as either the paper's innovation or its hidden failing.
- Identify and challenge every assumption in every statement, stated or implicit.
- Ask how you would present each idea; where the paper's presentation loses to a clearly better one, record a presentation finding.
- Note the future work the paper should have named but did not; these seed the weaknesses list.
- Exit: you can reconstruct the paper's structure from memory and name its strong and weak points - specifically implicit assumptions, missing citations to relevant work, and issues with its experimental or analytical techniques.

## 5. Literature surveys

Apply this section when the task is a survey of a field, not a single paper; skip it otherwise.

1. Find 3-5 recent papers in the area with an academic search engine and well-chosen keywords. Run a first pass on each, then read their related-work sections. If they point to a recent survey paper, read that survey; the search is done.
2. Otherwise, collect shared citations and repeated author names across the bibliographies; these are the field's key papers and key researchers. Set the key papers aside. Check where the key researchers have published recently; that identifies the field's top venues.
3. Scan those venues' recent proceedings for high-quality related work. That set plus the key papers is the survey's first version; run two passes on each member. If they share a citation you missed, fetch it and repeat, at most two iterations.

## 6. Verdict

Report in this order, reasoning before judgment:

1. The five Cs, answered.
2. Per-pass findings: clarity defects from the scan, claim-evidence gaps and figure defects from the grasp, assumption failures, missing citations, and technique issues from the re-implementation.
3. Strengths and weaknesses, each tied to a specific location in the target (section, figure, or page); a finding that names no location cannot be checked and does not count.
4. The verdict, with confidence (high, medium, low) and the cause of any confidence loss: reader gap or paper defect, named.

## 7. Checklist

Run these checks on the finished report. Each answers yes or no; each no returns to its section.

- The depth came from the ask, and the verdict claims no more depth than the passes run. (1)
- Each of the five Cs has a 1-3 sentence answer. (2)
- The clarity judgment includes the one-pass test. (2)
- Every figure, graph, and table was checked for labeled axes and supported conclusions. (3)
- Every comprehension failure is attributed to reader gap or paper defect, with the gap named. (3)
- A reconstruction was attempted, and every difference from the paper is classified innovation or failing. (4)
- Every finding names its location in the target. (6)
- Findings precede the verdict, and confidence carries its cause. (6)

*2026-07-12 - Claude Fable 5 (Cursor agent). Distilled from S. Keshav, "How to Read a Paper," ACM SIGCOMM Computer Communication Review, 2007.*
