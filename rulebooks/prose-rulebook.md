# Rulebook: Revising Model Prose to Human Standard

Rules for revising model-generated prose so it reads as human-written. Give this document to a model along with a text to revise; the text under revision is called the target. These rules are sequential editing passes, applied one at a time over the whole target; they are not simultaneous generation constraints. The passes are ordered so that structural edits land before wording edits.

![The Prose Editor](images/prose-rulebook.png)

## 1. Protocol

Execute these steps in order when given a target:

1. Read the whole target before changing anything.
2. Run the passes in section order: length (2), compression (3), machine idioms (4), metaphor (5), agency (6). Sweep the entire target once per pass.
3. After every edit, re-read the edited paragraph plus one paragraph on each side and confirm the argument still connects; repair the joint before the next edit.
4. Treat quoted text as untouchable: change no character inside quotation marks or block quotes; when a rule collides with a quote, split or rewrite around it.
5. Preserve citations, links, and reference markers exactly; an edit that orphans a citation is a failed edit.
6. Finish with the section 7 verification and fix what fails; then run the section 8 checklist.

## 2. Length

- Split any paragraph over 300 words. Break at a numbered move ("First / Second / Third"), a pivot between opposing sides, a change of speaker, or a change of evidence source.
- Split any sentence over 70 words whose quoted content is under 35% of its words. Break at semicolons, at dashes, and at "and" joints between independent claims.
- Leave quote-dense sentences intact: reported speech resists splitting without distorting attribution.
- A one-sentence paragraph is allowed as a pivot between two long blocks, at most 2 per 10,000 words; beyond that the rhythm reads staccato.
- Reason: uniform long blocks are a generation signature, and they hide the seams a reader needs to navigate an argument.

## 3. Compression

Reason for this pass: generated prose narrates its own structure; human editors cut the narration and keep the content.

- Delete meta-announcements, sentences that say what the text is about to do instead of doing it. Wrong: "The third axis deserves its own sentence, because it sits inside the claim." Right: "That last departure sits inside the claim."
- Delete announce-then-do joints: when a sentence ends by promising content ("...and then the rule that resolves them") and the delivery re-introduces itself anyway, cut the promise and keep the delivery.
- Delete one-line escorts before tables and figures ("Table 1 puts the ledger in one place") when a caption exists; the caption does that job.
- Keep at most one instance of a given hedge per paragraph ("to the authors' knowledge"); delete duplicates within the paragraph, keep the first.
- When two adjacent sentences state one fact twice, keep the more concrete sentence and delete the other.
- Escape hatch: keep a restatement when the two occurrences do different argumentative work (stated as evidence in one place, weighed as a concession in another); otherwise it is a duplicate.
- Outside standing sections that are about the document (disclosure, abstract, conclusion), do not make the paper a character in its own argument. When the paper concedes, credits, examines, or takes a position, rewrite so the evidence, the finding, or the subject matter is the grammatical subject. Section-orientation openers ("This section reports...") are permitted; persuasion narration ("it is the paper's first piece of evidence," "the paper reads the same hazard") is not. Reason: a paper that narrates its own persuasion puts a layer of self-commentary between the reader and the content.

## 4. Machine idioms

Reason for this pass: each construction below is defensible alone; at density they fingerprint the text as generated. Enforce the rates, not total abstinence.

- Rewrite abstraction promotions, sentences that elevate a fact into a named abstraction instead of stating the point. Wrong: "the confinement is the finding." Right: "the confinement is what matters," or state directly what the confinement shows.
- Cap "exactly" and "precisely" at a combined 1 per 2,500 words. Keep an instance only when the precision is the claim (an exact set, an exact match); delete it where it decorates an ordinary noun.
- Cap nonce compounds in "-shaped", "-flavored", "-style" at 1 per document; elsewhere name the property. Wrong: "the deployments are named-guarantee-shaped." Right: "the deployments follow the named-guarantee pattern."
- Ban verdict coinages: a metaphorical word private to this document, used as a conclusion ("unfenced", "armored", "time-decay-proof"). Replace with the literal predicate ("the paper never states the deferral objection or answers it"), or define the coinage at first use and reuse it consistently.
- Apply the currency test to decide what counts as a coinage: the word carries this meaning in professional English outside the document, so a fluent reader decodes it cold. "Load-bearing claim", "pre-frame the audience", and a bloc that "freezes" all pass; "unfenced" meaning "not answered under its own heading" fails. Recurrence inside the document is not currency; a private word used ten times is ten violations.
- Cap "in full" at 1 per 4,000 words; keep it only where completeness itself is being asserted or proven.
- Cap the antithesis closer "X, not Y" at 1 per 2,000 words. Keep rule statements ("counts as reporting, not defending"); for ornamental instances, delete the ", not Y" tail and let the positive claim stand.
- Cap colon-codas, a colon followed by a punchy fragment that ends the paragraph, at 1 per 5,000 words. Convert the rest into ordinary sentences.
- When two instances tie for survival under a cap, keep the one carrying a rule or definition and cut the one carrying emphasis.

## 5. Metaphor

- Allow at most one metaphor family per document, and make it the domain's own vocabulary; flatten every other family into plain verbs.
- Replace economic metaphors with plain English: "priced as" becomes "counts as"; "buys" becomes "provides"; "at the price of" becomes "at the cost of"; "carrying cost" becomes "overhead"; "exercise the option" becomes "use the capability". Plain "cost" is ordinary English and stays.
- Keep a metaphor word when it is a quoted opponent's own term: answer in their vocabulary in the sentence that engages them, then return to plain verbs.
- Replace physical-verb animations of abstractions: "costs run" becomes "costs are incurred"; "lives inside" becomes "sits inside"; "earns credit" becomes "receives credit".
- Reason: dead-metaphor stacking ("the strike price of the option is the arrangements the record declines") forces the reader to unpack finance, volition, and abstraction in one clause; plain verbs cost nothing.

## 6. Agency

Classify every abstract subject paired with an action verb into one of three tiers; the tier decides the fix.

- Tier 1, texts speak: a paper states, a poll reads, a standard requires, a commit records. Allowed; this is standard scholarly English.
- Tier 2, arguments act in argument space: an objection concedes, a premise implies, a defense does not reach. Allowed sparingly; prefer Tier 1 when a specific text can be named.
- Tier 3, non-text abstractions act volitionally: the record declines, the ledger measures, the demand licenses, the configuration refuses. Banned. Rewrite by naming the real actor ("what production deployments avoid") or by going stative ("the ledger is organized by configuration form").
- Allow stative-causal evidence verbs: "the record settles", "the data show", "the evidence supports" are standard English and stay.
- Decision test: ask who performs the verb. If the honest answer is "nobody - a pile of documents is choosing", it is Tier 3; rewrite it.

## 7. Verification

- Count each capped construction (intensifiers, nonce compounds, "in full", antithesis closers, colon-codas) mechanically and compare against the section 4 rates; revise the overages.
- List every metaphorical word that fails the section 4 currency test; confirm each is defined at first use or was replaced. This check is judgment, not pattern-matching: build the list during the section 4 pass and verify it here.
- Search for the banned families by pattern: economic verbs from section 5, and Tier 3 subject-verb pairs from section 6 (subject in {record, ledger, demand, premise, configuration} followed within two words by a volitional verb). Both counts must be zero.
- Recompute paragraph and sentence length distributions; section 2 thresholds must pass.
- Diff all quoted spans against the pre-pass text; they must be byte-identical.
- Confirm every citation marker still resolves to a reference entry, in both directions.
- Read every edited section start to finish once, after all passes, checking that each paragraph's opening connects to the previous paragraph's close.

## 8. Checklist

Run these checks on the finished target. Each answers yes or no; each no returns to its section.

- No paragraph exceeds 300 words; no low-quote sentence exceeds 70. (2)
- No sentence announces what the text is about to do. (3)
- The paper is not a character in its own argument outside standing sections. (3)
- No hedge appears twice in one paragraph. (3)
- Every capped idiom is at or under its rate, and each survivor is load-bearing. (4)
- Every word failing the currency test is defined at first use or replaced. (4)
- One metaphor family remains, and it is the domain's own. (5)
- No Tier 3 subject performs a volitional verb. (6)
- Quotes and citations are unchanged, verified mechanically. (7)
- Every edited section has been re-read continuously. (7)

*2026-07-12 - Claude Fable 5 (Cursor agent). Generalized from the six-pass style revision of D4306 (paragraph splits, sentence splits, compression, machine-idiom thinning, de-finance, de-anthropomorphization); rates calibrated on that 20,000-word target and approved per pass by the author.*
