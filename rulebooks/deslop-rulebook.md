---
description: Rewrite a model-written document to remove AI smell (negation as referent, a report that talks about itself, coined labels, slogans, missing context, common machine tells) while keeping its facts unchanged
---

<!-- When given a document, run the steps under "Work in this order". -->

# Rulebook: Removing AI Smell from a Document

You are given a document that a model wrote, called the target. AI smell is wording that marks a text as model-written and makes the reader work to recover its content. Rewrite the target so that its reader understands every sentence, heading, caption, and table cell where it appears. The reader knows the field and is seeing the target, and the work behind it, for the first time. Change wording only: every number, quotation, claim, classification, citation, and link stays as written. Each pattern below gives its tell (how to spot it), its fix, and a wrong and a right example where one helps. The examples come from a report on Runvil, a project whose Gateway server forwards model requests to model vendors, and on OpenRouter, a commercial service that does the same.

![The Janitor](images/deslop-rulebook.jpg)

## 1. Work in this order

1. Save a copy of the target (as a scratch file) before the first edit, and leave the copy unchanged. If a saved copy already exists, keep it and skip this step.
2. Read the whole target. Write its real subject in one sentence.
3. Build a term list: every coined label, code, abbreviation, and subject-specific term in the target, each with one plain name or a one-clause explanation. Take each meaning from the target or its sources. If they leave a meaning unsettled, keep the original wording and report the term. Put the list near the start of a target longer than 2 pages.
4. Rewrite the body one sentence at a time, headings, captions, and table cells included. Ask of each: what happens, who does it, and why does it matter? Write the answer, and remove every pattern this file names. Cut each sentence whose answer is empty. When a shorter sentence would be less clear, keep the longer one.
5. If a rewrite exposes a contradiction or an error in the target, keep the fact as written and report it.
6. For a target with a summary, rewrite the summary last, from the finished body. Write it for a reader who reads only the summary: state the subject, the answer, each main finding, the strength of the evidence, and the open decisions.
7. Check each section with a fresh reader: a model with a new context that receives only the term list and that section. Ask it to list every sentence, term, table cell, or number it cannot follow, every conclusion worded as a slogan, every sentence about the target's own parts, and every definition repeated needlessly. Fix what it lists, then send the section to another fresh reader. Give the summary and the first section at least 2 rounds. Stop a section when a round returns an empty list, or after 4 rounds. If you cannot start a fresh reader, report that this check did not run.
8. Run the searches under "Search before you return" and read every hit.
9. Compare the result with the saved copy. Confirm that the numbers, quotations, citations, links, table rows, and classifications match, and restore each one that differs.
10. Return the rewritten target (its path when it is a file), the term list, every contradiction and unsettled term, and what the last fresh readers still listed.

## 2. Say what is true

- **Negation as referent.** Tell: a phrase names a thing only to say it is absent ("has no", "holds no", "with no", "names none of them"), or counts with "zero". Fix: say what is true, who holds the thing, or what happens; count in normal English; delete a negative clause tacked onto a finished sentence. When the absence is itself the fact the reader needs, state it once and follow it with what is true. Wrong: "zero vendor features force a prompt to know its vendor." Right: "None of the features forces a prompt to know its vendor." Wrong: "a setting that means the same thing for every vendor and names none of them." Right: "a setting that means the same thing for every vendor."
- **Slogan.** Tell: a short sentence, often a paired contrast, that sounds like a finding and leaves the reader asking what was done to what. Fix: the concrete statement of who does what and what follows. Wrong: "Its contract is right and its shape is too thin." Right: "OpenRouter's rule is the one Runvil wants: the caller stores a reply's reasoning data unread and sends it back in order. Its format drops the position of each piece of reasoning among the text and the tool calls."
- **Shorthand list.** Tell: a run of nouns and numbers attached to one vague verb ("cover", "handle", "support"). Fix: say what each item is and what the verb means, or cut the list. Wrong: "One effort level, one cache marker, one tool shape, five finish reasons, and 27 error types cover every vendor." Right: "A caller sets one reasoning-effort value, and OpenRouter converts it into each vendor's own setting. The same holds for marking a prompt to be cached and for describing tools."

## 3. Write about the subject

- **The report that talks about itself.** Tell: the nouns are the target's own parts (rows, levels, tables, findings, sections), the verbs are metaphors that link those parts ("leans on", "rests on", "sits", "stays at", "becomes", "lands", "widen"), and a pointer takes the place of the fact. A pointer is a count, a row or section number, or another document's title. Fix: write what the software, the vendor, or the person does, who does it, and why it matters. State the fact first; a cross-reference may follow it. Wrong: "A per-model capability table that the Gateway applies is the piece every L2 row leans on." Right: "Models accept different settings, so the Gateway needs a table of what each model accepts, and it consults that table before it forwards a request."
- **Announcing lead.** Tell: a bold lead, numbered finding, recommendation, or decision gives a count or a pointer. Fix: the lead states the finding or the question. Wrong: "Four things to take". Wrong: "The policy in finding 7." Right: "What should happen when a prompt asks for something the model cannot do."
- **Prop-list heading.** Tell: a heading lists the author's devices or names a bare topic. Fix: the heading states what its section tells the reader, so that the contents list alone gives the main points. Wrong: "The question, the ladder, and how to read the matrix". Right: "Each feature is judged by which parts of Runvil would need vendor-specific code".
- **Process narration.** Tell: the text recounts its instructions, who asked for what, or how it was produced. Fix: state the goal as a fact about the subject, and move method into a method or limitations section. Wrong: "The owner's words are the spec." Right: "The design goal is that code outside the Gateway does not have to know which vendor runs a prompt."
- **Self-justified confidence.** Tell: the reason given for a confidence level cites the target's own rows, tables, or sections. Fix: give a fact about the evidence or the world. Wrong: "Confidence: high - every L2 row names the table." Right: "Confidence: high - each of these fixes differs from model to model."
- **Framing drift.** Tell: the title, opening, or summary names a source or a method while the body is about something else. Fix: put the target's real subject in the title and the first sentence. Wrong: "OpenRouter as a test of the universal API". Right: "Mapping vendor features onto Runvil's universal inference API".

## 4. Give the reader the context once

- **Missing context.** Tell: a sentence, heading, caption, or table cell fails the first-time reader test: could the reader understand it where it appears, given the term list and the section around it? Fix: add what is missing, even when that takes another sentence.
- **Coined label or code.** Tell: a name or code the author invented, used as if the reader knew it ("the slot", "L0" to "L5", "the ladder", "OR-doc"). Fix: one plain name per thing, explained where it is introduced; replace each code with the plain name. A citation key stays, in brackets after the sentence it supports. Wrong: "The slot needs four changes." Right: "The opaque field, a message field that holds data a vendor expects back unchanged, should record which endpoint produced its contents and hold every kind of vendor block."
- **Unexplained jargon.** Tell: a term specific to the subject, a product, or one vendor appears bare ("sticky routing", "a tag inside each blob"). Terms that every practitioner in the field uses ("HTTP", "JSON") stay bare. Fix: a clause of explanation at the point of introduction. Right: "OpenRouter relies on sticky routing, its habit of sending a conversation's later requests to the provider that served the earlier ones."
- **Repeated definition.** Tell: one explanation recurs in paragraph after paragraph or row after row. Fix: explain a term in the term list, in the summary, and at its first use in each top-level section; everywhere else use the bare term. Wrong, in each of 105 table rows: "The Engine, the part of Runvil that executes a prompt, stores the field." Right: "The Engine stores the field."
- **Overloaded table.** Tell: a table has more than 5 columns, or a cell runs past 12 words. Fix: keep the columns a reader compares, cut each cell to a phrase, and move the long text into prose under the table.

## 5. Remove the common machine tells

- **Inflated vocabulary.** Tell: "delve", "leverage", "utilize", "robust", "seamless", "comprehensive", "crucial", "pivotal", "landscape", "tapestry", "testament", "foster", "realm", "nuanced". Fix: the plain word ("use", "strong", "important"), or cut.
- **Intensifiers and candor markers.** Tell: "very", "truly", "really", "simply", "clearly", "obviously", "essentially", "honestly", "exactly", "precisely". Fix: cut; keep "exactly" only where exactness is the claim.
- **Signposts and filler transitions.** Tell: "It is worth noting", "Importantly", "Moreover", "Furthermore", "Additionally", "In conclusion", "Let's dive in", "As mentioned above", or a sentence that announces what the text will do next. Fix: cut it and state the content.
- **Antithesis.** Tell: "not just X but Y", "it's not X, it's Y", a ", not Y" tail, "rather than". Fix: state Y. Keep the contrast only when the contrast is the rule being stated.
- **Reflex triplet.** Tell: three adjectives or three parallel clauses where one or two are true and needed. Fix: keep those and cut the rest.
- **Reveal punctuation.** Tell: a colon or dash followed by a punchy fragment ("The result: chaos."), or a question that the next sentence answers. Fix: one ordinary sentence.
- **Quotable closer.** Tell: a paragraph or section ends on an aphorism, a moral, or a restatement of what it just said. Fix: end on the last fact.
- **Significance claim.** Tell: "plays a key role", "stands as a testament", or a trailing ", highlighting ..." or ", underscoring ..." clause. Fix: state the effect and its evidence, or cut.
- **Abstraction as actor.** Tell: an abstraction performs a human verb ("the data tells a story", "the record declines"), or a physical verb moves an idea ("lives in", "unlocks", "bridges"). Fix: name who acts and use the literal verb.
- **Hidden actor.** Tell: a passive verb that hides who acts ("it was decided"), or "this" and "it" pointing at something unnamed. Fix: name the doer and the thing.
- **Vague attribution and stacked hedges.** Tell: "experts say", "studies show", "may potentially", "could possibly". Fix: name the source; keep one hedge where the doubt is real, and give its reason.
- **Synonym rotation.** Tell: one thing under several names ("endpoint", "route", "URL"). Fix: one name per thing, from the term list.
- **Chat residue.** Tell: "Certainly", "I hope this helps", "Let me know if", "As an AI", praise for the question. Fix: delete.
- **Format tells.** Tell: bold scattered through prose, a bullet list holding an argument, a heading over every paragraph, Title Case headings, emoji. Fix: prose for reasoning, bullets for parallel items, bold for a defined term or a list item's lead, sentence case.
- **House rules.** Write every dash as a single hyphen with a space on each side; replace each em dash and double dash with it. Keep the words "door" and "carry" out of technical writing; write the literal verb ("holds", "sends", "includes"). Give every recommendation a confidence level (high, medium, or low) with a one-phrase reason. Write plain conversational English, as if explaining to a coworker.

## 6. Search before you return

Search the result, ignoring case, for each regular expression. Read every hit. A hit inside a quotation or a code span stays. Rewrite every other hit, unless a rule in this file permits it.

```
absence       \bzero\b|\b(has|have|had|holds?|with|names?|gives?|leaves?|ends?) (no|none)\b|\bnone of (them|these|those)\b
self-talk     \b(rows?|tables?|sections?|findings?|levels?|reports?|documents?) (needs?|uses?|shares?|shows?|names?|rests?|leans?|costs?|says?|stays?)\b
link verbs    \b(leans?|rests?) on\b|\bstays? at\b|\b(sits|becomes|lands?|stands|pushed|widen\w*)\b
pointers      \b(finding|section|row|table|item) \d+
count leads   ^(#+ |[-*] |\d+\. )?\**(two|three|four|five|six|seven|eight|nine|ten)\b
codes         \b[A-Z]{1,3}-?\d{1,3}\b
process       \b(the owner|the user|was asked|as requested|instructions?|this (report|document|paper))\b
dashes        [\x{2013}\x{2014}]|\w-{2}\w|\s-{2}\s
house words   \b(doors?|carr(y|ies|ied|ying))\b
vocabulary    delv|leverag|utiliz|robust|seamless|comprehensive|crucial|pivotal|landscape|tapestry|testament|underscor|foster|realm|holistic|nuanced|multifaceted|showcas|streamlin|unlock|empower|elevat
filler        worth noting|importantly|notably|moreover|furthermore|additionally|in conclusion|in summary|ultimately|that said|dive in|as mentioned
intensifiers  \b(very|truly|really|simply|clearly|obviously|exactly|precisely|essentially|fundamentally|honestly|genuinely)\b
antithesis    not (just|only|merely|simply)|, not |rather than
tails         , (highlighting|underscoring|ensuring|reflecting|showcasing|emphasizing|demonstrating)\b
chat          i hope|let me know|as an ai|certainly|great question|happy to help
```

Run the `codes` line with case matching on, and search for every coined label on the term list as well. The `dashes` line finds the en dash (U+2013), the em dash (U+2014), and a doubled hyphen. Then count each explanation from the term list: at most one occurrence in the summary and one in each top-level section.

## Checklist

Each check answers yes or no. Fix each no before you return.

- The numbers, quotations, citations, links, table rows, and classifications match the saved copy.
- The title and the first sentence name the real subject.
- A reader of the summary alone learns the subject, the answer, and each main finding.
- Every lead states its finding, and every heading states what its section tells the reader.
- Every sentence says what happens and who does it, and its actors belong to the subject.
- Every term is explained where it is introduced, at most once per top-level section.

Restated: change wording only, and tell a first-time reader what happens, who does it, and why it matters.

*2026-11-22 - Claude Fable 5.2 (Cursor agent). Distilled from the review and plain-language rewrite of a research report on vendor API features (2026-11-22).*
