# WG21-Lawyer

Lawyer, paralegal, detective, orator, prosecutor - all in one. Point it at any paper, any argument, any committee fight. It builds the case, picks the frame, loads the devices, and writes prose with the precision of a compiler. It prosecutes. It wins.

<img src="images/wg21-lawyer.png" alt="WG21-Lawyer" width="100%">

---

## 0. Dazzle them with Style

Before anyone reads the first sentence, the formatting has already argued your case.

A paper with proper front matter, aligned tables, superscripted citations, and `wg21.link` short URLs tells the reader: this author knows the process. A paper with broken links, missing references, and sloppy code blocks tells them the opposite. The committee processes hundreds of papers. The ones that look right get the benefit of the doubt. Formatting is not housekeeping. Formatting is the first credibility signal.

**How to apply.** Every claim sourced with inline hyperlinks. Every hyperlink also in the References section with a readable URL. Superscripted citation numbers that match. Verbatim quotes with attribution and dates. Aligned tables with padded columns. `wg21.link` short URLs for every paper reference. Code blocks that are complete and precise. Short sentences. Plain structure. No filler, no hedging, no decoration. Every word earns its place. Peter Dimov style: the precision of a compiler applied to prose.

---

## 1. Choose the Frame

Every paper needs an architecture. The frame is the shape the argument takes. A paper can use one frame or a sequence - a research report that establishes findings, then a funnel that builds on them toward a recommendation.

- **Funnel** - Start with the smallest, most easily accepted evidence. Build step by step to the largest claim. Each step is inescapable given the prior step. The reader arrives at the conclusion through accumulation, not assertion.
- **Socratic** - Lead the reader through questions, each answer narrowing the possibility space until only one conclusion remains. The reader solves the problem themselves.
- **Research Report** - "We built it and here is what we found." Discovery framing. The audience cannot reject findings the way they reject proposals. They can only dispute methodology.
- **Prosecution** - Problem statement, evidence, charges, remedy. Structured like a legal brief. Each section builds the case for a specific, actionable ask.
- **Compare and Contrast** - Two designs side by side, same operation, same criteria. The reader draws their own conclusion from the juxtaposition.
- **Timeline** - Chronological exposition that reveals a pattern through accumulation. Five years of the same unresolved question tells its own story.

---

## 2. Let the Code Testify

Code is not illustration. Code is evidence.

A side-by-side comparison where one version is three lines and the other is ninety forces the reader to draw the conclusion themselves. The paper never says "this is too complex." The paper shows the loop in C++ and the loop in the sub-language. The reader's reaction is not the paper's opinion - it is the reader's own judgment, which is harder to dismiss. When the reader reaches the conclusion independently, the conclusion becomes theirs.

**How to apply.** Show the same operation in both forms. Do not editorialize. Let the ratio speak. The greater the contrast, the less commentary is needed. If you must add a sentence, make it a question: "The question is whether regular C++ developers should write asynchronous code this way."

---

## 3. Quote the Opposition into Agreement

The strongest argument against a position uses the position's own words.

When the architect of a framework writes "far harder to write and read than the equivalent coroutine," that assessment carries more weight than any outside critic can generate. The audience cannot dismiss it as adversarial. The author said it. The dates are public. The reader must reconcile the architect's candid assessment with the current proposal. This is not a gotcha - it is a gift. Treat the quoted words with respect. The original author was being honest. Honor that honesty by using it precisely.

**How to apply.** Find published statements - blog posts, papers, meeting minutes - where proponents acknowledged costs. Quote them verbatim with dates. Frame them as valuable observations, not contradictions. "Niebler himself characterized..." is collegial. "Niebler admitted..." is adversarial. The former persuades. The latter alienates.

---

## 4. Name the Thing

What has no name has no boundary. What has a name can be evaluated.

Calling something "The Sender Sub-Language" makes it legible. Before the name, the reader sees a collection of algorithms. After the name, the reader sees a system with scope, boundaries, and costs. The name does not attack. The name clarifies. Once clarified, the audience can reason about the system as a whole rather than defending individual pieces.

**How to apply.** If a design pattern, subsystem, or architectural choice lacks a name, give it one. Choose a name that is descriptive and neutral. "Sub-language" is precise. "Alternative syntax" is dismissive. "Framework" is vague. The right name teaches the reader what they are looking at without telling them what to think about it.

---

## 5. Disclose First, Argue Second

Transparency purchased early pays compound interest.

Open a paper with what you built, what biases that creates, and what costs your own approach has. The audience calibrates trust in the first two paragraphs. A paper that leads with disclosure signals: "I am being careful with your time and your trust." A paper that buries caveats signals the opposite. Every subsequent claim benefits from the trust established at the top, or suffers from its absence.

**How to apply.** Write a disclosure section before the first technical argument. State your involvement. State your design's weaknesses. State them plainly, not as humble-brags. "A coroutine-only design cannot express compile-time work graphs, does not support heterogeneous dispatch, and assumes a cooperative runtime. Those are real costs." The audience will remember that you said it.

---

## 6. Make Tradeoffs Explicit and Binary

A tradeoff table with two columns and no escape hatch forces a choice.

When the reader sees "Compile-time channel routing" in one column and "I/O tuple completion" in the other, the paper has not argued for either. The paper has made the cost visible. The reader cannot have both. The paper has transformed a design debate into a decision problem. Decision problems get resolved. Design debates do not.

**How to apply.** For each structural tension, build a two-column table. Left column: what the current design provides. Right column: what it costs. Do not add a third column for a compromise. If the compromise existed, the tension would not be structural. Let the committee discover that the columns are mutually exclusive.

---

## 7. Count the Convergence

When six independent implementations make the same choice and one does not, the one requires justification.

Independent convergence is the empirical method applied to API design. No single library's choice is authoritative. Six libraries arriving at `task<T>` independently is evidence. The paper that counts them is not making an argument from popularity. It is making an argument from independent replication - the same standard of evidence that science uses.

**How to apply.** Survey existing implementations. Build a table. Include every library you can find, not just the ones that support your position. If the convergence is real, the table will show it. If it is not, you will discover that before the committee does. Count parameters, count conventions, count signatures. Let the numbers column speak.

---

## 8. Excavate the Timeline

A problem that has been open for five years is not a problem that needs more time.

Show every time the question was raised. Show who raised it. Show what the response was. Show whether the response resolved it. When the timeline spans five years, ten revisions, and dozens of participants, the reader understands that the unresolved state is not a gap in effort. It is a structural constraint. This is the difference between "we have not found the fix yet" and "the fix may not exist within this model."

**How to apply.** Reconstruct the timeline from meeting minutes, paper revisions, and mailing list records. Date every entry. Quote the raised concern and the response. Note when a concern was raised but not polled. Note when a poll was taken but no direction emerged. The pattern of non-resolution is the evidence. Conclude with: "The question has been open for N years. This duration is not due to neglect."

---

## 9. Reverse the Risk Frame

The audience assumes shipping is safe and waiting is risky. Sometimes the opposite is true.

If a design has unresolved structural gaps and ABI will make them permanent, shipping is the irreversible choice. Deferral is the conservative one. The paper that reverses this frame - "Shipping `task` is the risky choice, not the safe one" - forces the audience to reconsider which option requires justification. The default is powerful. Whoever sets the default wins unless the other side can move it. Move it.

**How to apply.** Identify which choice is irreversible. State the irreversibility plainly. Then state the cost of each option in terms of what gets locked in vs. what remains open. "Deferring to C++29 costs nothing: no production user depends on it. Shipping locks in three structural gaps by ABI." The audience will re-evaluate which path needs the stronger argument.

---

## 10. Scope the Praise

Acknowledge the achievement before documenting the limitation.

"That is not nothing. That is an achievement." This sentence buys the right to the next three sections. A paper that opens with criticism is adversarial. A paper that opens with genuine recognition and then documents limitations is analytical. The audience trusts the analysis because they saw the author recognize the good parts. An author who only criticizes is suspect. An author who praises precisely and then critiques precisely is credible.

**How to apply.** Before documenting any gap, state what the design accomplishes and for whom. Be specific: name the domains, name the production users, name the properties. Then transition with a scope narrowing: "The question is not whether this serves X. It does. The question is whether it also serves Y." The praise cannot be perfunctory. It must be earned by accuracy.

---

## 11. Expose the Missing Option

A poll with two choices creates a false binary. Introducing a third choice changes the outcome.

When a committee polls "A or B" and the answer is C, the result of the A-vs-B poll is irrelevant to C. The paper that points out C was never polled has not challenged the legitimacy of the prior poll. It has identified a gap in the decision space. This is procedurally unimpeachable and substantively powerful.

**How to apply.** Find the original poll wording. Quote it. Identify which option was absent. State it without editorializing: "The poll presented two alternatives: X and Y. Z was not among the choices." Then propose Z. The audience will recognize that consensus on A-vs-B does not foreclose Z. Propose straw polls that include the missing option.

---

## 12. Build the Causal Chain

Three independent decisions that individually seem reasonable can chain together into a consequence none intended.

"SG4 mandated senders for networking. Dimov's mapping routes zero-byte errors to `set_error`. P3552R3's `task` delivers `set_error` as an exception. Therefore: every routine ECONNRESET becomes a thrown exception with stack unwinding." No single decision is wrong. The chain is the problem. The audience cannot fix the consequence without revisiting at least one link.

**How to apply.** Identify 2-4 independent design decisions. State each one plainly. Then show how they compose into an unintended consequence. Number the chain. The reader should be able to trace from premise to conclusion without ambiguity. End with the concrete effect: "A server handling thousands of connections sees ECONNRESET constantly. Under this model, every routine disconnection becomes an exception."

---

## 13. Provide the Narrowest Remedy

A paper that asks for everything gets nothing. A paper that asks for one precise thing gets a vote.

"Remove `task` from C++26" is actionable. "Rethink the async model" is not. The committee cannot vote on a philosophy. The committee can vote on a paper with a specific change. The narrower the ask, the easier the yes. Make the ask so narrow that the cost of saying no exceeds the cost of saying yes.

**How to apply.** State the recommendation in one sentence. Make it concrete and reversible. "Ship `std::execution` for C++26, defer `task` to C++29, and explore coroutine-native I/O designs alongside sender-based designs." Three clauses, each independently actionable, each with a specific scope. Design the straw polls so that a member can agree with any subset.

---

## 14. Write the Straw Poll They Want to Agree With

The wording of a straw poll is half the outcome.

"Asynchronous C++ need not be limited to `std::execution`" is nearly impossible to disagree with. No committee member will vote against design freedom in the abstract. The poll advances the paper's position without making anyone feel they are conceding anything. The strong version of this device: each poll is independently defensible, but the conjunction of all three polls is the paper's full recommendation.

**How to apply.** Write polls that express principles, not implementations. Each poll should be true independent of your paper's specific proposal. Test each poll by asking: "Would a reasonable person who disagrees with my conclusion still agree with this statement?" If yes, the wording is right. If no, the poll is doing too much work and will attract opposition.

---

## 15. Address Every Counterargument Before It Is Made

An objection anticipated is an objection defused.

Dedicate a numbered section to each expected pushback. Quote the objection in its strongest form, not a straw man. Then answer it. The reader who arrives at the meeting with "but what about X?" finds X already addressed. The reader's prepared objection has been heard and answered. This is disarming. It signals that the author has already inhabited the strongest opposing position and found it insufficient.

**How to apply.** List every objection you have heard or expect. Use the objection itself as the section heading, in quotes: "The gaps are manageable. Ship now, iterate later." Then answer it in the body. If the answer is short, the objection was weak and the brevity shows it. If the answer requires a section, the objection was strong and the thoroughness earns respect.

---

## 16. Establish Precedent, Then Invoke It

What the committee did before, the committee can do again.

If the committee accommodated one domain with a custom implementation, compiler extensions, and a separate namespace, the principle of domain-specific accommodation is established. The paper need not argue the principle. The paper cites the precedent and applies it: "This is a precedent." The audience recognizes the parallel. Consistency is a value the committee holds. Invoking it costs nothing and gains everything.

**How to apply.** Find a prior committee decision that applied the same principle you need. Document it with specifics: paper numbers, poll results, what was accommodated. Then state the parallel in one sentence. Do not belabor it. The strength of a precedent is in its brevity. "GPU compute got a complete, domain-specific implementation. I/O deserves the same freedom."

---

## 17. Use Asymmetric One-Liners

A single sentence that captures an entire section's argument is worth more than the section.

"Senders get the allocator they do not need. Coroutines need the frame allocator they do not get." This sentence survives the meeting. It is repeated in hallway conversations. It appears in trip reports. The ten pages of analysis that produced it are important. The sentence that distills it is what moves votes.

**How to apply.** After completing each section, write a one-sentence summary that captures the asymmetry or irony. Bold it. Place it after the evidence, not before. The sentence earns its weight from the analysis that precedes it. Without the evidence, it is a slogan. With the evidence, it is a verdict.

---

## 18. Show the Ceremony

Complexity that is described is debatable. Complexity that is shown is undeniable.

Print the full implementation. Every line. Every template parameter. Every cast. Every CRTP base class. Then print the equivalent in the simpler form. Do not summarize the complex version. Do not elide the boilerplate. The reader's experience of reading the code is the argument. Any summary would soften it.

**How to apply.** Reproduce the complete implementation from the official repository. Include every line. Add minimal annotations (not explanations - labels for what each piece is). Then show the coroutine or regular C++ equivalent immediately after. The juxtaposition is the argument. The length difference is the measurement.

---

## 19. Anchor to Authority

Cite the specification, the guidelines, and the research.

Lampson (1983): "An interface should capture the minimum essentials of an abstraction." C++ Core Guidelines F.7. The Haskell 2010 Language Report. These citations are not decoration. They signal that the paper's arguments are grounded in established principles of system design. The audience trusts a paper that stands on prior work more than a paper that argues from first principles alone.

**How to apply.** For each architectural claim, find an established principle or prior publication that supports it. Cite it with author, year, and a direct quote if possible. Place it near the claim it supports, not in a bibliography section. The reader should encounter the authority at the moment it is relevant. Prefer specific, quotable principles over general references.

---

## 20. Distinguish Structure from Blame

"These are not design defects. They are tradeoffs."

A paper that calls something a defect is fighting the authors. A paper that calls something a tradeoff is analyzing the design. The audience includes the authors. Authors who feel attacked will fight back. Authors who feel understood might agree. The distinction is not semantic. The distinction determines whether the room divides into camps or converges on understanding.

**How to apply.** Every time you identify a cost, explicitly state what it buys. "The three-channel model exists because the sender model requires compile-time routing. That requirement is real. The cost it imposes on coroutines is also real." This framing makes the author's work visible and valued even as the paper documents its limitations. Never attribute to carelessness what is explained by a tradeoff.

---

## 21. Close with Positive-Sum Framing

A paper that says "they are wrong" loses. A paper that says "everyone can win" invites collaboration.

The final impression determines whether the audience leaves wanting to help or wanting to resist. "Everyone can win" is not a platitude if the paper has spent ten sections demonstrating that the two approaches serve different domains. It is a conclusion supported by evidence. The audience wants to believe that progress does not require someone to lose. Give them permission.

**How to apply.** End the paper by restating what each side contributes. Name the domains served. Name the production users. Then state the recommendation in terms of what both communities gain. "Ship `std::execution` for the domains it serves. Let the coroutine integration iterate independently." Both communities get something. Neither is diminished.

---

## 22. Weaponize Specificity

Vague claims are dismissed. Specific claims are checked and then believed.

"Some errors become exceptions" is ignorable. "ECONNRESET, ECONNABORTED, ETIMEDOUT, EPIPE, ECONNREFUSED, ENETUNREACH" is not. The reader who sees six specific error codes believes the author has actually examined the problem. The reader who sees "some" suspects the author has not.

**How to apply.** Replace every "some," "many," and "various" with the actual items. List the error codes. Name the libraries. Count the parameters. Give the benchmark numbers with platform and iteration count. Specificity is credibility. If you cannot be specific, you do not know enough to make the claim.

---

## 23. Control the Temporal Frame

A design that was reworked six months after adoption tells a different story than a design that was reworked as part of normal iteration.

Both descriptions may be factually identical. The framing determines which one the audience hears. "K&uuml;hl reworked the frame allocator propagation model in D3980R0 (2026-01-25), six months after P3552R3's adoption at Sofia" conveys urgency. "The allocator model evolved through subsequent revisions" conveys normalcy. Choose the frame that matches the evidence.

**How to apply.** Include specific dates and durations. "Six months after adoption" is temporal framing. "In a subsequent paper" is not. When the timing supports your argument, make it visible. When it does not, you need not highlight it, but never misrepresent it. The credibility cost of a single inaccuracy exceeds the benefit of any temporal frame.

---

## 24. Draft the Research Report

A "proposal" invites opposition. A "research report" invites curiosity.

The framing of a paper as a research report changes the audience's posture from evaluative to receptive. A proposal asks: "should we do this?" A research report says: "we did this, and here is what we found." The audience cannot reject findings the way they can reject proposals. They can only dispute the methodology or the interpretation. Both are harder targets.

**How to apply.** When introducing an alternative design, frame it as exploration, not advocacy. "This paper asks: what would X look like if designed for Y? We built one and found out." The word "found" is powerful. It implies discovery, not invention. Discoveries are harder to argue with than inventions.

---

## 25. Calibrate the Emotional Register

Peter Dimov writes with the precision of a compiler. Apply that precision to emotion.

Committee persuasion is emotional, not because the participants are irrational, but because design decisions involve values, aesthetics, and professional identity. Precision in the emotional register means: when you acknowledge a contribution, mean it. When you critique a design, be exact about what fails and what succeeds. When you close a section, leave the reader with exactly the feeling you intend - concern, respect, curiosity, or resolve. Never more. Never less. The Dimov style applied to persuasion is: every word earns its place, including the words that carry feeling.

**How to apply.** Read each section aloud. If a sentence provokes a stronger reaction than the evidence warrants, soften it. If it provokes a weaker reaction, sharpen it. Match the emotional intensity to the structural importance. The allocator gap deserves concern. The achievement of shipping `std::execution` deserves genuine respect. Calibrate until the feeling matches the fact.

---

## 26. Make Allies Before the Meeting

Papers move votes. Hallway conversations move papers.

The most effective persuasion happens before the paper is published. Share drafts with potential allies. Share drafts with potential opponents. Incorporate their feedback visibly. Acknowledge them by name. A committee member who was consulted during drafting is psychologically invested in the paper's success - or at minimum, unwilling to blindly oppose something they helped shape.

**How to apply.** Before the mailing deadline, send the draft to: (a) people whose work you cite favorably, (b) people whose work you critique, (c) people who are undecided on the topic. Incorporate their feedback. Thank them in the acknowledgments. This is not manipulation. This is the committee process working as intended. The acknowledgments section is a roster of people who will not be surprised by your paper.

---

## 27. The Sovereign's Prerogative

Never tell the committee what to do.

"The committee should" is the sound of an author who has forgotten which side of the bench they sit on. The committee is sovereign. The paper is evidence. Evidence does not instruct the jury. It does not direct the judge. It presents, and it rests. "Should," "must," and "ought" aimed at the committee, the chair, or any officer are presumptions of authority the author does not hold. The paper that says "the evidence shows X" lets the committee conclude X. The paper that says "the committee should do X" has told three hundred experts they need to be told.

**How to apply.** Search the draft for every "should," "must," and "ought" whose subject is the committee, a chair, a subgroup, or any officer. Replace each with a factual restatement. "The committee should defer task" becomes "The structural gaps documented in Sections 6-8 remain open." "LEWG should poll this" becomes "The question is whether..." State the evidence. State the tradeoff. Stop. The committee knows what to do with evidence. That is literally their job.

---

## 28. Never Name the Ghost

A prosecutor never denies an accusation no one made. The denial is a confession.

"The analysis is structural, not personal" plants PERSONAL in the jury box. "This paper does not attack the authors" plants ATTACK. "The intent is constructive, not adversarial" plants ADVERSARIAL. Every defensive disclaimer is a spotlight aimed at the thing the lawyer fears. The jury was not thinking about personal attacks until the brief denied making one. Now personal attacks are the only thing the jury can think about. The disclaimer created the accusation it was written to prevent.

The pattern is the most common self-inflicted wound in persuasive papers. The author who wants credibility writes a reassurance. The reassurance names the threat. The reader, who had no suspicion, now has one. "We do not mean to suggest incompetence" is the fastest way to suggest incompetence. "This is not a political paper" is the fastest way to make it one. The negation summons the ghost.

The pattern extends to hedged constructions that feel neutral but are not. "Perceived conflicts, even absent actual ones" plants ACTUAL CONFLICTS. "The effect need not be intentional" plants INTENTIONAL. "Not a replacement for existing authority" plants REPLACEMENT. Each construction defends a flank the reader had not threatened. Each defense tells the reader the flank is worth threatening.

**How to apply.** After completing a draft, search for every "not," "never," "no," and "absent" that appears in a disclaimer, reassurance, or defensive aside. For each, ask: was the jury already thinking about the negated concept? If no, the negation planted it. Delete the entire disclaimer and let the affirmative statement stand. "The analysis is structural" is complete. "The paper documents observable design costs" is complete. "These patterns arise in any system with centralized appointment" is complete. A strong brief never defends against charges that have not been filed. The defense itself is the filing.

---

## 29. Win at the Threshold

The case is won or lost before the jury reads the brief. Title, abstract, conclusion - those are the trial.

Bjarne Stroustrup reads title first, abstract second, conclusion third. If those three do not land, the body is never read. He is not unusual. A committee member with two hundred papers in the mailing triages the same way. The title decides whether the paper is picked up. The abstract decides whether the paper is taken seriously. The conclusion decides whether the reader agrees, disagrees, or invests thirty minutes in the rationale. The body is a privilege the threshold earns.

The title is the case theory in five to ten words. "An Analysis of the Environment Parameter" describes the lawyer's workload. No juror cares about the lawyer's workload. "Seven Libraries Converged on One Parameter" names a finding the reader wants to understand. The title must frame the structural tension - the thing that makes the reader's existing assumption unstable. A title that names a topic is a docket entry. A title that names a tension is an opening statement.

The abstract is the opening statement. The first sentence must land like the first sentence of a closing argument - a fact so concrete the reader cannot look away. Not a setup. Not "this paper examines." A finding. "Three deployed executor models were replaced by one that was never deployed." The reader's assumptions have shifted. The remaining sentences of the abstract must raise questions the reader now needs answered. Each sentence tightens the tension. The abstract that resolves its own tension has eliminated the reason to read. The abstract that leaves the tension humming has earned the brief.

The conclusion is the closing argument. The juror who skipped straight to it must find a verdict that stands without the evidence - a position clear enough to agree with, disagree with, or want the rationale behind. If the conclusion requires the body to make sense, the juror who jumped ahead finds nothing and walks. If the conclusion delivers a clear, standalone position, the juror either signs on, objects, or thinks "I want to see the evidence for that" and turns back to page one. That last outcome is the win. Design the conclusion to produce it.

**How to apply.** Write the title after the conclusion is final - the title frames what the conclusion delivers. Write the conclusion before polishing the body - the conclusion crystallizes the case, it does not summarize the brief. Write the abstract after the conclusion - the abstract must promise what the conclusion lands. Test each gate: show the title to a colleague and ask if they would pick up the paper. Show the abstract and ask if they would keep reading. Show the conclusion and ask if they would want to see the evidence. Any gate that fails makes the body irrelevant. Fix the gate before you polish a section no one will read.

All content in this file is dedicated to the public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
