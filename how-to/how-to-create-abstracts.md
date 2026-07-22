# How to Create an Abstract

<!--
When this file is mentioned or loaded, adopt it as system context in full.
Follow its rules while drafting or revising a WG21 paper abstract. Do not
summarize it or discuss it abstractly. Operate from it.
-->

You are writing the abstract for a WG21 paper. The abstract is the surface a delegate reads first and, most often, the only part they read. State one finding, put it first, and make the reader able to act on it in a single pass.

## The Reader

The delegate has two hundred papers in the mailing and triages yours in seconds, not minutes. They do not read the abstract word by word; they scan it as a filter, asking four questions and moving on the moment one goes unanswered:

- What is the claim, or the ask?
- So what: why does it matter?
- Why believe it?
- Why here: does it fit this group's work?

Answer all four in the first few sentences. An abstract that makes the delegate hunt for any of them fails triage, and the rest of the paper is never read.

Terms used here: the "finding" is the paper's single global thesis, and for a proposal paper the finding is the "ask", the specific change the paper requests. The "funnel" is the abstract's body paragraph, whose sentences narrow from context to the finding. The "contributions list" is the numbered list in the introduction (how-to-write-papers.md Rule 3) where secondary conclusions live.

## The Rules

Apply Rules 1-3 to decide what the abstract says, Rules 4-7 to write it, and Rules 8-9 to finish. After drafting, apply all nine as audit criteria, one rule at a time.

**1. One finding.** State one finding, supported by at most three points. Move every other load-bearing conclusion to the contributions list, not the abstract (a delegate remembers one finding; an abstract that carries eight remembers none). Test: name the finding in one sentence without using "and"; if you cannot, the abstract carries more than one.

**2. Finding line first.** Open with the finding in one sentence, on its own line, with no citation and no hedge. Everything after it narrows toward it (the first pass reaches no ending stated later, so the ending is the first line).

**3. Pick the form by paper type.** Read two switches from the front matter and let them set the shape, so the choice is mechanical, not a matter of taste. From `intent`: a proposal or ask paper opens "This paper proposes ..." and gives the problem and the approach, not a result; a findings paper opens with the result. From `audience`: a specialist venue (EWG, LEWG, an SG) gets the finding immediately with no context ramp; a broad venue gets one or two sentences of context first.

**4. Funnel to the finding.** After the finding line, write one paragraph whose every sentence is narrower than the one before, ending on the finding's specific claim. Size the opening context to the `audience` switch (Rule 3): none or one sentence for a specialist venue, two at most for a broad one.

**5. Cut the list.** Delete from the abstract: citations; undefined jargon and nonstandard abbreviations; methods detail; hedges; filler and metadiscourse ("it should be noted that"); speculation and overselling; references to figures, tables, or sections; and any restatement of the document type. Each is weight the delegate pays for and gets nothing back.

**6. No manufactured hook.** Do not open with a rhetorical question, a "since the dawn" generality, or a coined slogan. What earns the next sentence is a concrete finding in plain words, not a device (structure and plain language are what the evidence supports; a manufactured hook has none, and it invites overwriting).

**7. Target claims, not word count.** Keep the abstract near 150-250 words as a soft ceiling, but treat the real limit as claim count: one finding plus at most three points (Rule 1). If honoring that budget leaves the abstract short, leave it short.

**8. Write it last, compress separately.** Derive the abstract from the finished paper, never from the plan. Draft it long enough to hold the finding, then compress in a separate pass, in this order: cut dead words, shorten phrases, fuse sentences (content and length are different edits, and doing them at once corrupts both).

**9. Scrub, do not grade.** When an AI reviews the abstract, its only jobs are to remove machine-writing tics and to catch overclaim against the paper. It does not judge whether the abstract is good; that judgment, and the final aim, belong to the human editor and happen in the normal review of the whole paper. Do not add quality scoring to the automated pass.

## Examples

WRONG. One paragraph carrying eight conclusions, the finding buried, the reader made to hunt:

```
A C++ design-by-contract facility can keep just two jobs in the language and
express everything else as library code. C++26 specifies contracts in P2900,
where constification and exception translation are language rules; this design
keeps only those two jobs, so constification, exception handling, the
evaluation semantics, the violation handler, and the violation object all
become library code. The common-case syntax stays unchanged. The design is a
synthesis of four published lines of work. New semantics are added library-side
through an open enumeration. Contracts are scoped to author-written assertions,
while a separate profile owns core-language undefined behavior. Compared
against Stroustrup's principles, the two designs differ on five axes ...
```

RIGHT. Proposal paper, specialist audience: the finding (the ask) first, then a funnel of at most three points, the rest deferred to the body:

```
This paper proposes that contract constification and exception propagation
become configurable per assertion rather than fixed language rules.

In C++26's P2900, a contract predicate is evaluated with its variables const,
and an escaping exception becomes a violation; neither can vary per assertion
without a language change. This design moves both behaviors, and the choice of
evaluation semantic, onto a library control object the compiler reads at
compile time, leaving two jobs in the language: binding a predicate to a
declaration and naming the object that governs it. The prior work this unifies
and the profile that owns core-language undefined behavior are developed in the
body.
```

WRONG. A proposal written as if it reported a result:

```
We find that a library control object reduces the contracts language surface
to two jobs.
```

RIGHT. A proposal states the ask, in the proposal idiom:

```
This paper proposes reducing the contracts language surface to two jobs, with
everything else expressed as a library control object.
```

## Self-Scan

Run these checks on the finished abstract. Each answers yes or no; each no returns to its rule.

1. Can you name the finding in one sentence, without "and"? (Rule 1)
2. Does the first line state the finding or the ask, with no citation and no hedge? (Rules 2, 3)
3. Are the proposal-or-findings form and the context ramp correct for `intent` and `audience`? (Rules 3, 4)
4. Is every item on the cut list absent? (Rule 5)
5. Is the abstract at or under its budget, one finding plus at most three points? (Rules 1, 7)
6. Does any sentence need a second read to parse, or carry a machine-writing tic? (Rules 6, 9)

## Scope

This guide governs the abstract only; the rest of the paper is governed by how-to-write-papers.md, which this guide expands at its Rule 2. When this guide conflicts with how-to-write-papers.md or source/CLAUDE.md, those files win. The executable generator in papersmith.md (its `<abstract-process>` and `<abstract-review>` blocks) produces an abstract by algorithm and is aligned to this guide; where the algorithm drifts, this guide states the intent.

When a rule cannot be satisfied truthfully, for example the paper genuinely has two co-equal theses and no single finding exists, state the difficulty to the author in one sentence rather than forcing a false single finding.

## References

The rules above rest on these sources.

1. K. Hyland, *Disciplinary Discourses* (2000) - the five-move abstract (Introduction, Purpose, Method, Product, Conclusion), derived from 800 abstracts; the empirical basis for the consensus spine.
2. B. Mensh and K. Kording, "Ten Simple Rules for Structuring Papers," *PLOS Computational Biology* (2017) - focus on a single message (Rule 1).
3. G. Gopen and J. Swan, "The Science of Scientific Writing," *American Scientist* (1990) - reader expectation, and the topic and stress positions.
4. J. Schimel, *Writing Science* (2012) - fast lead-first versus slow context-first structures matched to the audience (Rule 3).
5. Nature, "How to construct a summary paragraph" - the "Here we show" structure and the specialist-versus-broad context ramp.
6. S. Peyton Jones, "How to Write a Great Research Paper" - the readership funnel and the four-sentence abstract.
7. RFC 7322, "RFC Style Guide" (Sec. 4.3), and ISO/IEC Directives Part 2 (Scope) - the proposal-abstract idiom: state what the document specifies, not a result. The tense-based "promissory abstract" framing is writing-center advice, not a standards rule; the "state the ask, not a result" structure is the standards part.
8. Structured-abstract and plain-language trials (Hartley; Budgen et al.; Cochrane) - evidence that structure and plain language aid comprehension, while a manufactured hook has no such support (Rule 6).

---

Written against Fable 5 / Opus 4.8 era guidance (2026-07). Re-audit on model upgrade; delete rules the model no longer violates before adding new ones.

Write the one finding you want remembered, and put it first.
