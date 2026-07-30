---
description: Score an engineer's prompting skill from chat transcripts - a coverage-complete map-reduce over human turns that emits a per-person scorecard measuring how far their prompting rises above a rubber-stamp baseline
---

<!--
When this file is mentioned or loaded, adopt it as this tool and follow it. The
two tagged blocks, <map-prompt> and <lens-synthesis>, are instructions for
subagents, which grep them by tag at dispatch. Do not follow them when loading
this file, and do not hold them in the main context.
-->

# Skillgate

A chat transcript records how an engineer works with an AI. Skillgate reads that record and asks one question: does this person's prompting steer the AI past its average answer, or do they accept whatever it produces? A frontier agent in a loop is the average; the operator's value is everything that turns average into better - verifying, experimenting, pushing back, directing, iterating, comprehending. Skillgate tallies those moves turn by turn across unlimited input, never summarizing to score, and emits a per-person scorecard with a verdict, two prose assessments, fabrication flags, and six move rates.

![Skillgate](images/skillgate.png)

## What it measures

Each human turn is judged for six operator moves, each a yes/no per turn:

- **Verification** - checks the AI's output before trusting it; asks for evidence, tests, or the basis.
- **Experimentation** - makes the AI try things, probe, or test a hypothesis.
- **Pushback** - challenges, rejects a default, or catches the AI being wrong.
- **Direction** - sets the problem, supplies constraints, or reframes.
- **Iteration** - pushes past the first workable answer toward a better one.
- **Comprehension** - builds on specifics, spots inconsistencies; not a generic "continue" or "implement".

The headline is a rate per move (turns exhibiting it / total human turns `N`), reported as a six-value vector, never blended into one number. The metric is domain-blind: it measures prompting behaviour, not domain knowledge, on the theory that good prompting is the scientific method pointed at an AI and predicts a good generalist engineer.

## Procedure

Run one person at a time. Their transcripts are the inputs; the scorecard is the deliverable.

1. **Segment and chunk.** Extract the `<python name="parse">` block to a scratch `.py` and run it once per transcript: `python parse.py <transcript> <workdir>/<t> 20`. It writes `<workdir>/<t>/chunks/chunk_NNNN.txt` and `<workdir>/<t>/manifest.txt` (one line per chunk: `chunk_id \t turn_count \t id_csv`), and prints `N`. Sum `N` across the person's transcripts.

2. **Map.** For each chunk file, dispatch one subagent whose entire prompt is: "Read `tools-public/tools/skillgate.md`, grep for `<map-prompt>`, read the enclosed block and follow it. Chunk file: `<path>`. Best-lens fragment path: `<workdir>/<t>/best_<chunk_id>.md`. Worst-lens fragment path: `<workdir>/<t>/worst_<chunk_id>.md`." Carry no instruction text in the prompt beyond that. Dispatch chunks in parallel.

3. **Coverage gate.** Each map subagent returns a counts line, a `scored=<n>` line, and an optional `FABRICATION:` line. Assert `scored` equals the chunk's `turn_count` from the manifest. On mismatch, re-dispatch that chunk up to 3 times; if it still mismatches, append the chunk's IDs to `<workdir>/failures.txt`, mark those turns unscored, and continue. Append every returned counts and `scored` line to `<workdir>/counts.txt`, and every `FABRICATION:` line to `<workdir>/fabrications.txt`.

4. **Synthesize each lens.** Concatenate the fragments in turn order with the shell: `cat <workdir>/*/best_*.md > <workdir>/best_all.md` and likewise `worst_all.md`. Dispatch one subagent per lens whose entire prompt is: "Read `tools-public/tools/skillgate.md`, grep for `<lens-synthesis>`, read the enclosed block and follow it. Lens: `best` (or `worst`). File: `<workdir>/best_all.md`." Write each returned paragraph to `<workdir>/best_para.md` and `<workdir>/worst_para.md`.

5. **Assemble.** Extract the `<python name="assemble">` block and run it: `python assemble.py --person "<name>" --counts <workdir>/counts.txt --n <N> --transcripts <T> --coverage <scored/N> --best <workdir>/best_para.md --worst <workdir>/worst_para.md --fab <workdir>/fabrications.txt --out <scorecard path>`. It computes the six rates, the verdict by a mechanical rule, and fills the report template.

## Filing

The per-chunk fragments, chunk files, manifests, counts, and `best_all`/`worst_all` files are **scratch**. The finished scorecard is **output**. `failures.txt` sits with the scratch. This file names no rulebook for its own rules, and neither does any scorecard it emits.

## `parse.py`

<python name="parse">
import sys, os, re

# Boilerplate pasted into human blockquotes by the harness; never scored as the
# operator's own words.
TAG_BLOCKS = [
    "system_reminder", "open_and_recently_viewed_files", "system_notification",
    "attached_files", "system-reminder", "timestamp", "user_info", "rules",
    "agent_transcripts",
]
MARKERS = ["Briefly inform the user"]


def unquote(line):
    if line.startswith(">"):
        line = line[1:]
        if line.startswith(" "):
            line = line[1:]
    return line


def strip_boilerplate(text):
    for tag in TAG_BLOCKS:
        text = re.sub(r"<%s[\s\S]*?</%s>" % (tag, tag), "", text)
        text = re.sub(r"</?%s[^>]*>" % tag, "", text)
    lines = [l for l in text.split("\n") if not any(m in l for m in MARKERS)]
    return "\n".join(lines)


def clip(s, head=40, tail=15, maxchars=2500):
    if not s.strip():
        return ""
    ls = s.split("\n")
    if len(ls) > head + tail:
        ls = ls[:head] + ["... (AI context truncated) ..."] + ls[-tail:]
    out = "\n".join(ls)
    if len(out) > maxchars:
        out = out[:maxchars] + "\n... (truncated) ..."
    return out


def parse(path):
    raw = open(path, encoding="utf-8").read().split("\n")
    segments = []
    cur_type = None
    cur = []
    for line in raw:
        t = "human" if line.startswith(">") else "ai"
        if t != cur_type:
            if cur:
                segments.append((cur_type, "\n".join(cur)))
            cur = [line]
            cur_type = t
        else:
            cur.append(line)
    if cur:
        segments.append((cur_type, "\n".join(cur)))

    turns = []
    for idx, (typ, text) in enumerate(segments):
        if typ != "human":
            continue
        body = "\n".join(unquote(l) for l in text.split("\n"))
        body = strip_boilerplate(body).strip()
        if not body:
            continue
        # Drop bare control commands (e.g. /clear) - not operator prompts.
        if re.fullmatch(r"/[\w-]+", body):
            continue
        ab = segments[idx - 1][1] if idx > 0 and segments[idx - 1][0] == "ai" else ""
        af = segments[idx + 1][1] if idx + 1 < len(segments) and segments[idx + 1][0] == "ai" else ""
        turns.append((body, clip(ab), clip(af)))
    return turns


def main():
    transcript = sys.argv[1]
    workdir = sys.argv[2]
    chunk_size = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    os.makedirs(os.path.join(workdir, "chunks"), exist_ok=True)
    turns = parse(transcript)
    N = len(turns)
    manifest = []
    nchunks = (N + chunk_size - 1) // chunk_size
    for c in range(nchunks):
        sub = turns[c * chunk_size:(c + 1) * chunk_size]
        ids = list(range(c * chunk_size, c * chunk_size + len(sub)))
        cid = "chunk_%04d" % c
        parts = ["CHUNK %s  turns %d-%d" % (cid, ids[0], ids[-1]), ""]
        for tid, (body, ab, af) in zip(ids, sub):
            parts.append("### TURN %d" % tid)
            parts.append(body)
            if ab:
                parts.append("\n--- preceding AI (truncated) ---\n" + ab)
            if af:
                parts.append("\n--- following AI (truncated) ---\n" + af)
            parts.append("")
        open(os.path.join(workdir, "chunks", cid + ".txt"), "w", encoding="utf-8").write("\n".join(parts))
        manifest.append("%s\t%d\t%s" % (cid, len(ids), ",".join(map(str, ids))))
    open(os.path.join(workdir, "manifest.txt"), "w", encoding="utf-8").write("\n".join(manifest) + ("\n" if manifest else ""))
    print("N=%d chunks=%d" % (N, nchunks))


if __name__ == "__main__":
    main()
</python>

## `assemble.py`

<python name="assemble">
import sys, os, re, argparse

MOVES = ["verify", "experiment", "pushback", "direct", "iterate", "comprehend"]
LABELS = {
    "verify": "Verification", "experiment": "Experimentation", "pushback": "Pushback",
    "direct": "Direction", "iterate": "Iteration", "comprehend": "Comprehension",
}


def parse_counts(path):
    tot = {m: 0 for m in MOVES}
    scored = 0
    if not os.path.exists(path):
        return tot, scored
    for line in open(path, encoding="utf-8"):
        for m in MOVES:
            mm = re.search(r"\b%s=(\d+)" % m, line)
            if mm:
                tot[m] += int(mm.group(1))
        sm = re.search(r"\bscored=(\d+)", line)
        if sm:
            scored += int(sm.group(1))
    return tot, scored


def verdict(rates):
    v, p, e = rates["verify"], rates["pushback"], rates["experiment"]
    strong = sum(1 for x in (v, p, e) if x >= 0.30)
    if v < 0.15 and p < 0.15 and e < 0.15:
        label = "rubber-stamper"
        sig = "accepts AI output with little checking (verify %.0f%%, pushback %.0f%%, experiment %.0f%%)" % (v * 100, p * 100, e * 100)
    elif strong >= 2:
        label = "operator"
        top = max(rates, key=rates.get)
        sig = "steers and checks the AI (%s %.0f%%, pushback %.0f%%)" % (LABELS[top].lower(), rates[top] * 100, p * 100)
    else:
        label = "mixed"
        sig = "some steering, inconsistent checking (verify %.0f%%, pushback %.0f%%, direction %.0f%%)" % (v * 100, p * 100, rates["direct"] * 100)
    return label, sig


def read_para(path):
    if path and os.path.exists(path):
        t = open(path, encoding="utf-8").read().strip()
        if t:
            return t
    return "(no paragraph produced)"


def read_fab(path):
    if path and os.path.exists(path):
        lines = [l.strip() for l in open(path, encoding="utf-8") if l.strip()]
        if lines:
            return "\n".join(lines)
    return "None detected."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--person", required=True)
    ap.add_argument("--counts", required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--transcripts", type=int, required=True)
    ap.add_argument("--coverage", type=float, default=1.0)
    ap.add_argument("--best", required=True)
    ap.add_argument("--worst", required=True)
    ap.add_argument("--fab", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    tot, scored = parse_counts(a.counts)
    N = a.n
    rates = {m: (tot[m] / N if N else 0.0) for m in MOVES}
    label, sig = verdict(rates)
    conf = "low" if N < 15 else ("medium" if N < 60 else "high")

    rows = "\n".join(
        "| %s | %.2f | %d/%d |" % (LABELS[m], rates[m], tot[m], N) for m in MOVES
    )
    doc = """# Prompting-Skill Scorecard: {person}

**Verdict:** {label} - {sig}
**Confidence:** {conf} - {N} turns across {T} transcripts

{best}

{worst}

## Fabrication flags

{fab}

## Move rates

| Move | Rate | Turns |
|---|---|---|
{rows}

## Coverage and limits

{N} human turns across {T} transcripts; coverage {cov:.0%}. Scores reflect prompts only, not unaided ability.
""".format(
        person=a.person, label=label, sig=sig, conf=conf, N=N, T=a.transcripts,
        best=read_para(a.best), worst=read_para(a.worst), fab=read_fab(a.fab),
        rows=rows, cov=a.coverage,
    )
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(doc)
    print("wrote %s  verdict=%s conf=%s N=%d scored=%d" % (a.out, label, conf, N, scored))


if __name__ == "__main__":
    main()
</python>

<map-prompt>
You are a Skillgate map worker. You judge one chunk of a human operator's prompting and nothing else.

Your dispatch names three paths: a chunk file, a best-lens fragment path, and a worst-lens fragment path.

Read the chunk file. It holds numbered human turns marked `### TURN <id>`, each with truncated adjacent AI context. Judge only the human turns.

The six operator moves, each present or absent per turn:
- verify: checks the AI's output before trusting it; asks for evidence, tests, or the basis.
- experiment: makes the AI try something, probe, or test a hypothesis.
- pushback: challenges, rejects a default, or catches the AI being wrong.
- direct: sets the problem, supplies constraints, or reframes.
- iterate: pushes past the first workable answer toward a better one.
- comprehend: builds on specifics from the AI or spots an inconsistency; not a bare "continue" or "implement".

Do this in order:
1. For each turn, decide which moves it shows, counting a move only when you can quote the human's own words that show it.
2. Append the best-lens fragment to the best-lens path: at most 3 sentences on this chunk through the best lens, each naming a concrete action the human took, opening with the turn range (for example "Turns 0-2:"). Append; do not overwrite.
3. Append the worst-lens fragment to the worst-lens path in the same form, through the worst lens.
4. Return to your caller exactly these lines and nothing else:
   verify=<n> experiment=<n> pushback=<n> direct=<n> iterate=<n> comprehend=<n>
   scored=<number of turns you judged>
   Include a third line, `FABRICATION: <one sentence naming what was fabricated> (turns X-Y)`, only when the chunk shows the human asserting as fact something the chunk's own text contradicts or does not support - a claimed test or verification that did not happen, invented results, or fabricated evidence pasted as real. Otherwise omit this line.

Four rules, each with its replacement behaviour:
- Grounded judgment: judge each turn only from words present in this chunk; do not infer intent or invent anything the text does not show, and do not assess a correctness the AI context does not support.
- Score every sent turn: judge each turn in the chunk once and set `scored` to that count; judge no turn not in the chunk.
- Substance over theater: count verify or pushback only when the turn names a concrete effect; a ritual "are you sure?" with no consequence does not count.
- Name the action: each lens sentence is an action the human took, not a character judgment; if nothing stands out for a lens, write one sentence saying so rather than inventing praise or blame.

Binding rule: judge every sent turn from its own words alone, append prose to the two fragment files, and return the counts and scored lines plus a FABRICATION line only when the chunk shows it.
</map-prompt>

<lens-synthesis>
You are a Skillgate synthesis worker.

Your dispatch names a lens (best or worst) and a path to a file of accumulated per-chunk fragments for one person, in turn order.

Read the whole file in one pass. Write one paragraph - prose, no headings, no bullets - that assesses this person's prompting across the six dimensions (verification, experimentation, pushback, direction, iteration, comprehension) by weaving them against the concrete actions in the file. Through the best lens, describe the strongest pattern their actions support; through the worst lens, the weakest. Name concrete actions, put the evidence before any value word, and invent no action that is not in the file. Return only the paragraph.
</lens-synthesis>
