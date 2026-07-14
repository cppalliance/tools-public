# Papersmith: An Architectural Assessment

**Source reviewed:** [tools/wg21/papersmith.md](https://github.com/cppalliance/tools-public/blob/master/tools/wg21/papersmith.md)  
**Related design principle:** [The Fan-Out Problem: Why AI Is a Critic, Not an Author](https://github.com/cppalliance/tools-public/blob/master/lessons/ai-is-critic-not-author.md)

## Executive assessment

Papersmith is a production and review system for WG21 papers. It treats a committee paper not as prose to be generated but as a multi-resolution argument that must survive three different reading conditions: a brief surface pass, a substantive argument pass, and a hostile audit.

Its architecture follows a seven-stage pipeline:

1. Commission
2. Research
3. Skeleton
4. Body
5. Surface
6. Prose
7. Review

The crucial design move is that its many rules are **staged audit criteria rather than simultaneous generation constraints**. Only the small set of rules relevant to a drafting stage binds while that stage is being written. All other rules are applied afterward, one at a time, during review.

This solves two problems at once:

- it reduces instruction interference during generation;
- it turns writing quality into a sequence of critic tasks that frontier models perform well.

Papersmith's deepest contribution is therefore not its style guide. It is an architecture for converting institutional expertise into transformations, gates, and independent audits.

**Overall judgment: Papersmith is an exceptionally disciplined implementation of the principle that AI should be used as a critic-guided production system rather than a one-shot author.**

---

## 1. WG21 papers are not ordinary technical documents

A WG21 paper exists in an unusually constrained information environment.

The intended reader may have hundreds of papers in a mailing, limited time, substantial domain knowledge, pre-existing commitments, and an institutional role that requires not merely understanding but voting, objecting, scheduling, or carrying work forward.

A paper can fail before its argument is read.

It can fail because:

- the title does not reveal the contribution;
- the abstract withholds the conclusion;
- the headings name topics rather than findings;
- the ask cannot be stated as a vote;
- the evidence appears after the judgment;
- the assumptions are discoverable only by an opponent;
- citations are inaccessible;
- the paper sounds like a campaign;
- the surface promises a paper the body does not contain.

Papersmith starts with a realistic model of this reader. The delegate reads in passes and stops when a pass fails.

This model is not decorative. It determines the document's architecture:

- the surface must carry the entire paper for the five-minute reader;
- topic sentences and standalone figures must carry the argument for the one-hour reader;
- evidence, symmetry, limitations, and citations must survive the hostile reader.

The paper is therefore built to remain intelligible at several resolutions.

---

## 2. The central principle: staged refinement, not simultaneous perfection

A large writing specification can become self-defeating if every rule is imposed during every sentence. The model tries to satisfy evidence placement, paragraph structure, tone, loaded words, citation format, metaphor density, sentence length, audience level, objections, conclusions, and title searchability at once.

Papersmith avoids that failure explicitly.

The Commission stage settles decisions that should not be improvised during prose generation. The Research stage verifies evidence. The Skeleton fixes structure. The Body stage applies only six write-time rules. The Surface is written after the body. Prose is revised in sequential passes. Review audits every remaining rule one at a time.

This is a sophisticated response to model constraint capacity.

The system does not assume that the model can hold dozens of independent objectives in active balance while generating. It transforms the paper under a small local objective, then subjects the result to another transformation.

That is exactly the family resemblance to Booksmith: quality emerges from the process rather than from a heroic generation.

---

## 3. Commission is the requirements phase

Step 0 may be the most important stage in the entire system.

The Commission requires ten blocks:

- intent;
- thesis;
- audience;
- document number;
- structure pattern;
- sourcing constraints;
- conclusion targets;
- spine;
- sources to verify;
- override registry.

This stage removes the decisions that prose would otherwise silently make.

### Intent prevents rhetorical ambiguity

The `ask` versus `info` distinction forces the author to decide whether the paper requests action or places findings in the record.

That choice controls later rules. An ask paper must make a votable request. An information paper must not smuggle in urgency, scheduling requests, or pressure.

The binary is intentionally coercive. It prevents a common institutional ambiguity: a paper that claims merely to inform while being written to produce an unstated procedural outcome.

Frontier models may recognize a rare mixed case and use the override mechanism, but the default forces clarity.

### The thesis controls fan-out

The one-sentence thesis is a search-space constraint. A draft with several independent conclusions becomes several possible papers competing inside one file. The rule about splitting a thesis that needs "and" is best understood as a pressure test, not a grammatical theorem.

Its function is to identify whether the paper has one contribution.

### Conclusion targets reverse the usual workflow

Papersmith requires a conclusion paragraph and one conclusion sentence per planned section before research and drafting are complete.

This is not premature certainty. The targets are provisional destinations. They expose what the paper believes it will show and allow research to confirm, refine, or defeat that expectation.

Without such targets, the model can produce sections that are individually competent but do not converge.

### The override registry creates governance

The override registry is a particularly mature feature. It acknowledges that a frontier model or human author may know when a rule should be broken. But exceptions are explicit, reasoned, attributable, and treated as resolved during review.

This avoids both rigid formalism and invisible noncompliance.

---

## 4. Research changes the epistemology of drafting

Many AI-assisted writing workflows generate claims first and search for support afterward. That invites motivated sourcing. A fluent paragraph creates psychological pressure to preserve its thesis, so later retrieval becomes an exercise in finding something close enough to cite.

Papersmith reverses the order.

Research is organized by claim. Every source is verified for exact paper number, revision, title, authors, year, canonical URL, and public availability. Quotations include section and page locations. Deployment claims rely on primary documentation. Absence claims disclose a reproducible method.

A claim without a verified source does not enter the paper.

This is more than citation hygiene. It changes what generation is allowed to do.

The Body stage writes from persisted research files only. The model is not invited to draw on vague memory, generate plausible history, or fabricate evidence-shaped prose. Its task is to arrange verified material into an argument.

Papersmith also treats absence as a finding. A statement such as "the word X does not occur in Y" must include the indexes searched, search terms, fetch date, scope caveats, and recall gaps. This is unusually strong because negative claims are often rhetorically powerful and methodologically weak.

The invariant "never fabricate or embellish evidence" is therefore implemented as a pipeline gate, not merely stated as an ethical aspiration.

---

## 5. Skeleton and Body separate structure from surface persuasion

The Skeleton stage fixes the file and its section inventory before body prose exists. This prevents the model from discovering structure opportunistically through paragraphs.

The Body stage then applies a deliberately small rule set:

- open each section by stating what it covers and why;
- begin paragraphs with topic sentences;
- place evidence before value words;
- conclude each section immediately after its evidence;
- quote only verified research;
- make tables, figures, and code stand alone.

These rules create a strong argument spine.

### Evidence before value is a major rule

W9 requires evidence before the evaluative language it supports. This reverses a common advocacy pattern in which the writer announces that a design is harmful, incomplete, radical, or necessary and then recruits evidence.

For the delegate, order affects trust. A judgment that follows evidence reads as a conclusion. The same judgment before evidence reads as framing.

### Section conclusions make the argument locally complete

The requirement to state a conclusion at each section level can look repetitive if interpreted mechanically. Its purpose is stronger: the reader should never have to infer what the evidence was intended to establish.

Frontier models can vary the form when literal repetition would damage the prose. The rationale supplies the governing objective: no withheld conclusion.

### Topic sentences create an alternate representation

The sequence of paragraph openings is used later as a "thrust check." That means the paper contains an embedded compressed representation of its own argument.

The body can be audited by harvesting first sentences. This is a powerful design because it makes argumentative continuity mechanically inspectable without reducing the full paper to an outline.

---

## 6. Writing the surface last

Step 4 is one of Papersmith's most important decisions.

The conclusion, abstract, introduction, headings, and title are written after the body. This means the surface is derived from what the paper actually demonstrates rather than from the author's initial aspiration.

The order within the surface stage is also thoughtful:

1. conclusion;
2. abstract;
3. introduction;
4. headings;
5. title.

The conclusion first forces a full accounting of the contribution and evidence. The abstract compresses that result. The introduction exposes assumptions and contributions. The headings are rewritten to carry the argument. The title is chosen last from the finding-words.

This is a sequence of lossy compression with verification at each level.

A delegate who reads only the title should classify the paper. A delegate who reads title, abstract, headings, and conclusion should know the context, assumptions, contribution, ask, and verdict. A delegate who continues should find that the body supports exactly that surface.

Papersmith's statement that the surface "sells the paper that exists, not the paper that was planned" captures the principle.

---

## 7. Prose is treated as a late transformation

Papersmith does not confuse polished prose with a sound paper.

The Prose stage begins only after evidence, argument, and surface exist. It runs sequential passes for:

- length;
- structural compression;
- machine idioms;
- metaphor;
- agency.

This order matters. Structural edits occur before word-level edits. Quotations and citations are byte-protected. Edited paragraphs are reread with their neighbors so local improvements do not break transitions.

The prose rules are unusually specific because they target generated-text signatures:

- paragraphs with uniform long blocks;
- meta-announcements;
- repeated hedges;
- abstraction promotions;
- private verdict coinages;
- stacked metaphor families;
- non-text abstractions behaving as intentional agents.

The goal is not generic elegance. It is to remove patterns that make a committee paper feel generated, inflated, or theatrically argumentative.

The rate-based treatment of idioms is especially good. It does not ban every rhetorical construction. It recognizes that a colon coda, antithesis, or coined phrase can work once and become a machine signature at density.

---

## 8. Review is the heart of the system

Papersmith's strongest subsystem is the Review Process.

It separates six operations:

1. mechanical scans;
2. citation integrity;
3. fact check;
4. adversarial evaluation;
5. findings report;
6. resolution.

The fact check and adversarial evaluation use separate fresh-context subagents. The writer does not review its own draft because the writer shares the draft's blind spots.

This is a direct implementation of "AI is critic, not author."

The model is not asked a vague question such as "improve this paper." Each critic receives a bounded task:

- verify every quotation;
- verify every paper identifier and tally;
- rerun absence claims;
- reconstruct the surface;
- harvest topic sentences;
- state the strongest opponent case;
- test symmetry;
- test analogies;
- test quotation context.

These are local evaluation problems. Models are much more reliable when judging a concrete claim against a concrete source or rule than when asked to intuit global excellence.

---

## 9. Challenge filters discipline the critic

AI criticism has its own failure mode: it can generate endless plausible objections.

Papersmith addresses this with challenge filters.

A candidate finding is killed when:

- the paper already concedes or answers it;
- it assumes the wrong audience;
- the fix would not change the paper's effect.

This is a significant architectural feature.

The system does not treat the volume of criticism as a proxy for rigor. It asks whether a finding is new, relevant, and consequential. Low-value issues are relegated to notes rather than allowed to dominate the report.

The severity model then distinguishes:

- misleading or argument-breaking defects;
- credibility or argument weaknesses;
- polish costs.

This makes the review actionable.

---

## 10. Resolution prevents endless editing

Every finding receives exactly one disposition:

- structural fix;
- mechanical fix;
- recorded override.

This is the final governance layer.

A structural problem cannot be wordsmith-ed away. A mechanical problem does not trigger a wholesale rewrite. An intentional exception does not return as a fresh finding in every review.

After the final edit batch, only mechanical and citation checks are rerun once. Then the process stops.

The explicit stop condition is important. Iterative model review can otherwise continue indefinitely, trading one style preference for another and slowly destroying authorial intent.

---

## 11. Domain expertise is embedded in the rules

Papersmith is not a generic technical-writing tool with WG21 terminology pasted onto it. Its rules encode knowledge of committee work.

Examples include:

- ask papers require exact poll language;
- info papers ask for nothing;
- titles use established searchable terms;
- related work is summarized inline;
- public sources are preferred for future readers;
- technical costs attach to mechanisms, not people;
- favorable and unfavorable evidence receive symmetric standards;
- objections are stated in their strongest form;
- design properties are acknowledged before costs are analyzed;
- implementation claims require primary evidence;
- abbreviations and meeting names are expanded for the reader in 2032;
- loaded vocabulary is neutralized to avoid motive attribution and factional framing.

This is "expertise pre-baked in the rules" in a literal sense. The model is not expected to infer committee legitimacy norms, persuasion dynamics, archival needs, or rhetorical hazards during drafting.

The rules create a default path through those concerns.

---

## 12. Frontier judgment and rule breaking

A superficial reading might treat Papersmith as a rigid checklist. That would be mistaken.

The document supplies reasons for non-obvious rules, stages the criteria, and includes an override registry. Those features allow a strong model to reason about purpose rather than merely obey syntax.

For example, W8's topic-sentence rule exists so the argument remains navigable and reconstructible. A technical paragraph whose first sentence must establish a local object before advancing the argument may satisfy the objective without satisfying the most literal form.

The right interpretation is:

- the rule defines the normal implementation;
- the reason defines the objective;
- frontier judgment resolves edge cases;
- the override registry records deliberate deviations when needed.

This is closer to a constitution than a linter.

The specification is effective precisely because it does not rely on either pure discretion or pure formalism.

---

## 13. Risks and limitations

### 13.1 It can optimize for defensibility over discovery

Papersmith is exceptionally good at making a paper auditable, fair, sourced, and legible. A radically new framing may initially violate familiar structure or lack the kinds of evidence the tool prefers.

The override mechanism is essential. Without confident human use of it, the system could favor arguments that are easy to defend over arguments that are genuinely new.

### 13.2 The same model family can share blind spots

Fresh context is valuable, but two instances of the same model may still share training priors and systematic preferences. Independent roles do not guarantee independent judgment.

High-stakes papers may benefit from:

- model diversity;
- human domain review;
- explicit counter-model prompts;
- source-grounded tests rather than prose judgment alone.

### 13.3 Rules can create a recognizable house style

Declarative headings, explicit section conclusions, evidence-first paragraphs, neutral verbs, low metaphor density, and controlled rhetorical patterns may make Papersmith documents recognizably uniform.

For WG21, that may be a feature. The goal is institutional clarity, not literary individuality. Still, the system should distinguish committee readability from universal prose quality.

### 13.4 The ask/info split may need an explicit exceptional path

Some papers both establish a record and request a narrow procedural action. Frontier models can identify such cases, but the specification could state how to represent them without allowing vague mixed intent.

### 13.5 "Unverifiable" is not always publishable

The invariant says to state an unverifiable gap in one sentence and continue. In some papers, the correct action is to remove the claim entirely rather than publish a gap that distracts or implies unsupported suspicion.

The existing rule that unsupported claims do not enter the paper partly resolves this. The distinction between "the absence is itself material" and "the evidence is merely missing" should remain explicit.

### 13.6 Fact checking depends on source accessibility and interpretation

Character-for-character quote verification is objective. Whether a source actually supports an inference can be harder. The adversarial check addresses this, but legal, historical, or technical claims may still require expert human judgment.

---

## 14. What Papersmith contributes beyond WG21

Papersmith generalizes to other evidence-heavy institutional writing.

Its reusable ideas include:

### 14.1 Model the reader's stopping behavior

Design the artifact so that each reading depth yields a complete and accurate representation.

### 14.2 Settle intent before prose

A document that does not know whether it informs, persuades, requests, or records will improvise contradictory rhetoric.

### 14.3 Verify evidence before drafting

Do not let fluent prose create a sunk cost around unsupported claims.

### 14.4 Write the surface from the finished body

Compression should describe the demonstrated work, not the planned work.

### 14.5 Separate critics by failure class

Mechanical, factual, adversarial, and stylistic evaluation are different tasks and should not be blended.

### 14.6 Filter criticism

A critic needs standards for killing redundant, irrelevant, and trivial findings.

### 14.7 Record exceptions

Expert judgment is compatible with rules when deviations are explicit and reasoned.

---

## 15. Final evaluation

Papersmith is a highly mature AI-assisted writing architecture.

It recognizes that the central challenge of a committee paper is not sentence generation. It is the coordinated production of:

- a single contribution;
- verified evidence;
- an inspectable argument;
- a truthful surface;
- institutionally appropriate rhetoric;
- durable citations;
- a review record;
- a resolvable ask or finding.

The tool decomposes those requirements into transformations that models can execute and audits that models can perform reliably.

The strongest concise description is:

> Papersmith turns an open-ended writing task into an evidence-gated, multi-resolution argument pipeline whose outputs are independently criticized before acceptance.

That is a substantial contribution.

Its rules are strong not because they eliminate judgment, but because they encode expert defaults, explain their purposes, stage their application, and provide a governance mechanism for intentional exceptions.

Among the three tools assessed here, Papersmith is the most disciplined expression of process as intelligence. It demonstrates that a frontier model becomes more reliable not merely through a better prompt, but through a production architecture that decides what should be generated, what must be verified, who should criticize it, and when the work is allowed to stop.
