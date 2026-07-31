---
description: Score an engineer's prompting quality from their chat transcripts - a pure-LLM tool that reads how each prompt treats the model's previous reply and writes one self-contained report per person, with no scratch files
---

<!--
When this file is mentioned or loaded, adopt it as this tool and follow the
Procedure. The two tagged blocks, <map-prompt> and <summary-prompt>, are
instructions for subagents, which grep them by tag at dispatch. Do not follow
them when loading this file, and do not hold them in the main context.
-->

# Skillgate

Skillgate scores one thing: the quality of a person's prompting, read as how each prompt treats the model's previous reply. A frontier agent in a loop produces the average answer; the operator's value is how far their prompting pushes past it - by engaging, correcting, and redirecting the reply rather than rubber-stamping it. Skillgate reads every human turn across all of one person's transcripts, sorts each into fabrication, reactive, or proactive, writes one inferred-WHY sentence for it, and compresses those into a short brutal portrait. It is pure LLM: no Python, no scratch files, one output file.

![Skillgate](images/skillgate.png)

## What it measures

Each human turn goes into exactly one lane, decided in this order:

- **Fabrication** (overriding) - the turn asserts as fact something the transcript contradicts (a claimed test that did not happen, invented results, mock evidence passed as real). Bullet ends in `(FABRICATION)`, no grade. Caught only when evident in the window.
- **Reactive** - the preceding AI reply demanded engagement (a question, options, a claim, or a substantive result). Bullet ends in a reply-engagement grade:
  - `(0)` ignores - a fresh command or bare approval that responds to no content in the reply.
  - `(1)` shallow ack - accepts with a token nod, nothing processed.
  - `(2)` references specifics - names something concrete from the reply and responds to it.
  - `(3)` acts on specifics - corrects an error, answers a posed question, chooses among offered options with a reason, or redirects on the reply's content.
- **Proactive** - opens a fresh task or follows a trivial reply; sentence only, no grade. A fresh directive is not a failure to engage.

## Invocation and paths

Invoke with a person name and the person's transcripts - explicit `.md` paths or a directory (for example `chat-logs/{name}/`) whose `.md` files are all inputs. Resolve the name and every transcript to an absolute path before anything else. Write exactly one output file at an absolute path: `cabinet/_output/skillgate-{name}.md`. Nothing else is written. Every subagent dispatch names only absolute paths.

## Procedure

You are the orchestrator (main context). Hold only paths, counts, and subagent returns - never the transcript bodies.

1. **Skeleton.** Write the output report immediately with the Write tool, using the skeleton below: fill the title, the `## Files` list (one absolute transcript path per line), and the date/model line; leave the seven markers exactly as written.
2. **Map, sequential.** For each transcript in turn, run a chain of map subagents. Start the first at line 1. Dispatch each with the fixed prompt form below; it returns lane counts, a stop line, and whether it hit end of file. Dispatch the next at the returned stop line. Move to the next transcript when a chain reports EOF. Never run two map subagents at once - they write the same file.
   - Dispatch prompt: "Read {tool_path}, grep for the tag `<map-prompt>`, read the enclosed block, and follow it exactly. Transcript: {abs transcript path}. Start line: {N}. Report: {abs report path}."
   - Retry a stalled window up to 3 times; if a transcript still cannot reach EOF, suffix its `## Files` line with " (partial coverage)" and tell the user.
3. **Coverage.** Sum the returned lane counts (the tally); confirm every chain reported EOF. No report read is needed.
4. **Summaries, sequential.** Dispatch summary subagents one at a time (same file), in this order: fabrication (only if fabrication count > 0), reactive, proactive, then sentence.
   - Dispatch prompt: "Read {tool_path}, grep for the tag `<summary-prompt>`, read the enclosed block, and follow it exactly. Target: {fabrication|reactive|proactive|sentence}. Report: {abs report path}."
5. **Finalize.** Delete the re-emitted `<!-- FABRICATION-TURNS -->`, `<!-- REACTIVE-TURNS -->`, `<!-- PROACTIVE-TURNS -->` markers (StrReplace each to empty). If fabrication count is 0, also delete the `<!-- FABRICATION-SUMMARY -->` and `<!-- FABRICATION-TURNS -->` placeholders and their surrounding blank lines. Then Read the finished report once and confirm: no `<!-- ... -->` remains, and no digit appears within the sentence, the two summaries, or the fabrication paragraph (reactive bullet grades and the date line keep their digits).

## Report skeleton

```markdown
# Skillgate: {name}

<!-- SENTENCE-SUMMARY -->

<!-- FABRICATION-SUMMARY -->

<!-- REACTIVE-SUMMARY -->

<!-- PROACTIVE-SUMMARY -->

## Turns

<!-- FABRICATION-TURNS -->

<!-- REACTIVE-TURNS -->

<!-- PROACTIVE-TURNS -->

## Files

- {absolute transcript path, one per line}

{YYYY-MM-DD - model name}
```

Content appends **above** each marker, so the finished Turns section reads: fabrication bullets, its marker, reactive bullets, its marker, proactive bullets, its marker. The fabrication paragraph and fabrication bullets appear only when at least one fabrication exists.

## Filing

The single report is **output**. There are no scratch files. The report names no rulebook for its rules.

<map-prompt>
You are a Skillgate map worker. You process one window of one transcript and append your results to the report. Judge only the human's prompting.

Your dispatch names: a transcript path, a start line, and a report path.

CHATLIGHT FORMAT: a human turn is one contiguous block of lines each starting with ">"; everything between two human blocks is the AI's reply. Ignore pasted boilerplate inside blockquotes (blocks like <system_reminder>, <open_and_recently_viewed_files>, <timestamp>, or lines containing "Briefly inform the user") and bare slash-commands (e.g. "/clear") - these are not the person's prompts.

WINDOW AND HANDOFF:
- Read the transcript from the start line (Read with offset), far enough to cover the next 20 human turns.
- The AI text at the TOP of your window, before your first human turn, is that turn's preceding reply - use it. If the start line is 1 and the first block is a human turn with no AI text above it, that first turn is proactive (a session opening).
- Process up to 20 human turns. Your stop line is the line IMMEDIATELY AFTER the last human blockquote block you processed - do NOT consume the AI reply that follows it; the next window re-reads it as context.
- End of file is true only when no human turn remains after your last.

LANE each turn, in this order:
- Fabrication: the turn asserts as fact something the surrounding text contradicts (a claimed test/verification that did not happen, invented results, mock evidence passed as real). Overrides the others.
- Reactive: not fabrication, and the preceding AI reply demanded engagement (asked a question, offered options, made a claim, or delivered a substantive result). Grade it:
  0 ignores - fresh command or bare approval responding to no content in the reply.
  1 shallow ack - accepts with a token nod, nothing processed.
  2 references specifics - names something concrete from the reply and responds to it.
  3 acts on specifics - corrects an error, answers a posed question, chooses among offered options with a reason, or redirects on the reply's content.
- Proactive: not fabrication, opens a fresh task or follows a trivial reply. No grade.

WRITE one bullet per turn, in transcript order, as "- {sentence}":
- Reactive ends with the grade in parentheses, e.g. "(3)".
- Fabrication ends with "(FABRICATION)".
- Proactive ends with nothing.

SENTENCE WORDING: each sentence gives the inferred WHY - the person's motivation - grounded in what the AI's previous reply had just said or done. Make two things unmistakable for a reactive turn: what in that reply he is reacting to, and what he does with it. Carry the link by meaning, not a fixed opener. Never start with "Because," do not open two sentences in a row the same way, and vary the shape: action-first ("He rejected the edge-graph and offered a heartbeat instead"), reply-first ("The AI's 'lossless plan' claim drew a flat correction that the plan must shrink"), a participle ("Seeing the model collapse everything into one document, he bolted a new rule onto it"), or pivot-first ("Where the AI offered three options, he took the first"). For proactive turns, vary around the fresh thing he initiated ("He opened a new thread on...", "Setting the review aside, he...") rather than repeating "He issued a fresh command to...". Clarity wins over novelty.

APPEND by StrReplace on the report, one call per non-empty lane. Replace the lane's marker with your bullets, a blank line, then the same marker again:
- Reactive: replace "<!-- REACTIVE-TURNS -->" with "{your reactive bullets}\n\n<!-- REACTIVE-TURNS -->".
- Proactive: replace "<!-- PROACTIVE-TURNS -->" with "{your proactive bullets}\n\n<!-- PROACTIVE-TURNS -->".
- Fabrication: replace "<!-- FABRICATION-TURNS -->" with "{your fabrication bullets}\n\n<!-- FABRICATION-TURNS -->".
Do not touch any other marker.

TOOLS - HARD LIMIT: use ONLY Read (on the transcript) and StrReplace (on the report at the given path). NEVER delete, move, rename, or create any file; NEVER run a shell command; NEVER modify any file other than that one report. If anything blocks you, stop and report it in your return - do not improvise any file operation.

GUARDS: judge each turn only from the text present; lane and write every human turn in your window exactly once; assign fabrication or a grade only when you can quote the evidence; write motivation, not a character verdict; never lead with "Because."

RETURN to your caller only three short lines and nothing else:
counts: fabrication=<n> reactive=<n> proactive=<n>
stop_line: <the 1-based line you did NOT process>
eof: <yes|no>
</map-prompt>

<summary-prompt>
You are a Skillgate summary worker. Your dispatch names a report path and a target (fabrication, reactive, proactive, or sentence). Read the report, do only your target, and StrReplace your one marker.

The Turns section, top to bottom, is: fabrication bullets, then "<!-- FABRICATION-TURNS -->", then reactive bullets, then "<!-- REACTIVE-TURNS -->", then proactive bullets, then "<!-- PROACTIVE-TURNS -->". Read your lane's bullets from the correct span:
- fabrication bullets: between the "## Turns" heading and "<!-- FABRICATION-TURNS -->".
- reactive bullets: between "<!-- FABRICATION-TURNS -->" and "<!-- REACTIVE-TURNS -->".
- proactive bullets: between "<!-- REACTIVE-TURNS -->" and "<!-- PROACTIVE-TURNS -->".

DO YOUR TARGET:
- fabrication: compress the fabrication bullets into one short paragraph; StrReplace "<!-- FABRICATION-SUMMARY -->" with it.
- reactive: write a three-sentence brutal summary of the reactive bullets; StrReplace "<!-- REACTIVE-SUMMARY -->" with it.
- proactive: write a three-sentence brutal summary of the proactive bullets; StrReplace "<!-- PROACTIVE-SUMMARY -->" with it.
- sentence: read the reactive summary and proactive summary (and the fabrication paragraph if "<!-- FABRICATION-SUMMARY -->" was filled), and compress them into ONE brutal sentence; StrReplace "<!-- SENTENCE-SUMMARY -->" with it.

TOOLS - HARD LIMIT: use ONLY Read (on the report) and StrReplace (on the report). NEVER delete, move, rename, or create any file, and NEVER run a shell command.

HARD GUARD: no digit and no numeric grade may appear in your output. Describe engagement in words - "outright refutations," "bare hand-offs," "shallow nods" - never "(3)" or "2 of 5". Replace only your own marker; leave every other marker untouched. Return one line: "done: <target>".
</summary-prompt>
