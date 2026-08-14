Assay is a two-pass structural analysis pipeline for WG21 proposals. You point it at a paper already in paperstore and receive a procedure-based assessment: what the text claims, what evidence backs those claims, where the argument has gaps, and whether the thesis still stands after a second reading under six named lenses. The product is not a reviewer's opinion. It is a record that the same inspections ran, in the same order, and that the paper landed on Sound, Weakened, or Undermined. You gain a defensible structural file of the proposal, written as `{pid}.assay.md`, rather than a take.

## What Assay Is

Assay runs two-pass structural analysis on a WG21 proposal. Pass 1 extracts what the paper asserts and derives a thesis from those assertions. Pass 2 re-reads every section with that thesis in hand and files findings against it.

You receive a procedure-based assessment. Assay does not express opinions about the paper. It has procedures, and the procedures were followed.

The analysis inspects a proposal through six named lenses: Performance, Design, Specification, Usability, Ecosystem, and Rationale. A paper that passes every inspection is not necessarily good. A paper that fails several is not necessarily bad. Assay files what it finds. Interpretation is someone else's department.

## Two-Pass Analysis

Pass 1 runs from Receive through Derive (steps 0 through 8). It extracts claims, evidence, gaps, and asks per chunk, then derives a thesis. That pass is Intake: the paper is received, cataloged, and compressed into a thesis.

At Derive (step 8), pass-1 claims are compressed into a thesis and load-bearing claims are identified. Load-bearing means their retraction would collapse the thesis.

Pass 2 runs from Verify through Report (steps 9 through 17). It re-scans every chunk with the thesis, cross-chunk gaps, external research, and companion paper summaries injected. That second reading is Review.

Assay produces findings, challenges them against concessions, evidence, and scope, detects compound dynamics, and derives a verdict. It weighs structure rather than the count of findings. Three minor findings in the periphery do not weaken a paper whose thesis is sound. Zero findings do not strengthen a paper whose thesis is unsupported.

The synthesized verdict scale is Sound, Weakened, or Undermined. Insufficient is the default when synthesis has not placed a paper. Skipped is a Survey triage outcome, not a synthesized quality verdict. Sound means the thesis survives and findings, if any, do not undermine it. Weakened means the thesis survives but surviving findings weaken the structural support, so specific sections need reinforcement. Undermined means the thesis does not survive: the structural support is insufficient and the submission requires substantial revision.

## Citations and Delivery

Every citation is scanned, cross-referenced against the archive, and flagged when the edition is stale. A citation is stale when the cited id is recorded as the previous version of a later paper. A bare paper number (no R-suffix) resolves to the latest revision stored in paperstore.

Assay requires a C++ standard MCP server for normative lookups, mechanism verification, and specification analysis grounding. You point it at that server under `[mcp.cpp-standard]` in SERVICES.toml:

````toml
[mcp.cpp-standard]
base_url = "https://mcpserver1.cpp.al/mcp"
api_key = "$CPP_MCP_API_KEY"
````

The code default for an unset URL is the same Alliance endpoint, `https://mcpserver1.cpp.al/mcp`.

The finished analysis is `{pid}.assay.md` in paperstore. Intermediate artifacts (claims, evidence, gaps, thesis, findings) are stored in the database for downstream use.

## Running Assay

The user-facing entry point is the paperflow CLI verb `assay`, invoked with a document ID. The run is fully batch: no interactive steps and no user identity.

````bash
paperflow assay P4003R3
````

That is the whole invocation once the paper is in paperstore and the standard server is reachable. Routing, NLI, and sequence-classification data files ship inside the installed assay wheel. There is no separate data fetch.

Capture a full-fidelity debug transcript of every LLM call, and a compact per-step trace dump, in one run. Any prior debug file for that paper is wiped first.

````bash
paperflow assay P4003R3 --debug --trace
````

Stop after a chosen pipeline step when you want the trace instead of the finished report. Stopping after a step also turns on trace. Extract is step 4. Derive is step 8.

````bash
paperflow assay P4003R3 --step 4
paperflow assay P4003R3 --step 8
````

Re-run even when a prior complete result already exists:

````bash
paperflow assay P4003R3 --force
````

Supply the cpp-mcp API key in the environment before running. When SERVICES.toml writes the key as `$CPP_MCP_API_KEY`, the value is resolved from that environment variable.

````bash
export CPP_MCP_API_KEY="<your-api-key>"
````

Assay hard-errors rather than proceeds when the MCP server is unreachable or the API key is missing. Running without standard access degrades finding quality in ways that cannot be detected downstream. A missing key raises that `$CPP_MCP_API_KEY` is not set, or that the cpp-mcp API key is empty and must be set in the environment (referenced by SERVICES.toml). A handshake failure names the URL and tells you to check `CPP_MCP_API_KEY`. The MCP client is closed even when the pipeline errors.

The Python public API of the assay package is four names: `Section`, `assay_paper`, `chunk_paper`, and `format_numbered_lines`. No other pipeline helpers are public. `assay_paper` is the async single-paper pipeline. `chunk_paper` splits markdown into heading-based leaf sections. Each `Section` exposes heading, markdown level, 1-based start and end line, and character count. `format_numbered_lines` formats a line range with numbered prefixes.

````python
from assay import assay_paper

report = await assay_paper("P4003R3", backend)
````

`assay_paper` accepts `debug`, `trace`, and `stop_after` with the same meaning as the CLI, plus an optional `provider` override for which classifier provider backs paper routing, and an optional `on_progress` callback that reports step progress.

The default embedder from SERVICES.toml is used for RAG, gap upgrades, and companion search. Companion-paper Verify is skipped entirely when no embedder is configured.

## Pipeline Authority and Steps

All LLM-facing text comes from the assay markdown document at runtime. That document is the pipeline authority: step sequence, per-step model slots, output budgets, thinking budgets, tools, LLM service slots, and local classifier slots. The step body above the divider is the prompt. The text below is documentation. There are no prompt strings in Python. You change prompts, step metadata, service slots, and classifier slots by editing that document, not by patching Python.

LLM service slots are `gemma`, `deepseek`, and `default`. In the current binding, `gemma` maps to `b200x2-gemma4`; `deepseek` and `default` map to `h200x8-deepseek-v4-pro`. The selector classifier slot is pinned to `nli-small`. Missing or empty Classifiers fails fast. Routing cannot silently fall back to classifier defaults.

````markdown
## Classifiers

- **selector:** nli-small

## Config

- **concurrency:** 2
````

You set **concurrency**, **model**, **max-output**, **thinking-budget**, **chunk-tokens**, and **tools** in that document. Pure-Python steps declare **model:** none. Every assay agent is capped at 16384 max output tokens. Production targets open-weight thinking backends. Schema misses are solved with retries and prompt engineering, not by retreating to a cloud API.

Pipeline-wide concurrency is set from the Config block (documented as 2). Per-step LLM concurrency defaults to serial (1) when Config is absent. Extract, Decide, Classify, and Analyze declare **concurrency:** 8 in step metadata. Analyze is documented as running serially despite that metadata.

The 18 steps, in order, are: Receive, References, Index, Survey, Extract, Decide, Classify, Collect, Derive, Verify, Research, Probe, Analyze, Rationale, Challenge, Couple, Synthesize, Report.

Receive (step 0) validates that the paper exists in paperstore, then loads metadata and converted markdown. Title, date, audience, authors, and intent come from paperstore metadata. References (step 1) extracts citations mechanically and cross-checks them. Index (step 2) builds a RAG index over cited papers that exist in paperstore. Survey (step 3) chunks the paper, scores wording signals, triages, and routes.

Extract (step 4) extracts per-chunk items with an LLM, one call per chunk. Decide (step 5) judges per-chunk claim support with an LLM. Classify (step 6) turns unsupported claims into gaps with an LLM. Collect (step 7) deduplicates items, groups gaps, and aggregates asks. This step is pure Python. Derive (step 8) compresses claims into a thesis and identifies load-bearing claims in one LLM call.

Verify (step 9) cross-checks claims against companion papers in one LLM call per companion. Research (step 10) looks up external evidence once per lens (six LLM calls). Probe (step 11) inventories stale references and author overlap. This step is pure Python. Analyze (step 12) re-analyzes each chunk with the thesis injected. Rationale (step 13) runs an SD-4 checklist and emits quality findings in one LLM call. Challenge (step 14) cross-examines findings with an LLM. Couple (step 15) detects compound dynamics in one LLM call. Synthesize (step 16) promotes Major findings and derives a verdict. This step is pure Python. Report (step 17) renders the assay markdown report. This step is pure Python.

When Survey triages a paper out, Extract through Couple are skipped. Synthesize and Report still run. Synthesize keeps the Survey skip verdict instead of writing a new synthesis.

Survey chunking uses a 1000-token budget (**chunk-tokens:** 1000). Direct chunking defaults to 6500 characters. The pipeline falls back to 2000 chunk-tokens if the step omits the field. Extract currently uses **max-output:** 8192 and **thinking-budget:** 2048. Research binds **tools:** `web_search`, `web_fetch`.

## Intake: Blanking, Chunking, and Triage

At Receive the paper is verified against the archive and assigned a case number. Referenced papers that are on file are retrieved, sectioned, indexed, and placed in the case folder. YAML front matter is always blanked so analysis sees proposal prose, not title, date, or audience metadata. Revision-history sections, references and bibliography sections, and acknowledgments sections are dropped so changelogs, citation lists, and thank-you notes do not enter analytical prompts. Dropped lines are replaced with empty newlines rather than deleted, so original line numbers stay valid for later citations.

You see the paper as numbered lines. Non-blank lines keep the original text after a pipe and a space. A run of blank lines collapses to one numbered sentinel.

````text
    12| We propose to add std::widget.
    13|
    14| This design is ABI-stable.
````

The paper is split into heading-based leaf sections. Oversized sections flatten into children. Small adjacent leaves coalesce when they still fit the budget. Numbered bold subsections such as **3.5.1** can split a section that has no heading children. Skip-level issue lists (H4 under an H2) split rather than remaining one monolithic chunk.

Survey triage decides whether a paper is worth full structural analysis. The decision is deterministic from front matter, heading structure, and size. There is no LLM call. Each paper is classified as a proposal to analyze, a wording-dominant skip, or a reference-document skip.

Wording-dominant papers are detected from headings named Wording or Proposed Changes (and Proposed resolution at Survey) and from CWG or LWG audience. Wording-dominant skip is checked before treating the same large paper as a generic reference document. Intent values ask, adopt, direction, or review force analysis even if the paper is huge. A heading containing abstract, motivation, design, poll, or straw poll treats the paper as a proposal. A title containing rationale, proposal, towards, or a plan for does the same. A proposal heading or ask-style intent overrides size and wording ratio, so a large wording paper with an Abstract still analyzes.

Papers larger than 300,000 characters whose majority of headings are Standard clause tags such as `[exec.syn]` are skipped as wording-dominant (wording ratio above 0.5). Large papers with no proposal signal and no wording dominance are skipped as reference documents. Papers at or under 300,000 characters are analyzed even without proposal headings or intent.

Processing ends at Survey when the paper is primarily specification wording or a reference document with no structural claims. Most papers continue. A skip reason quotes clause-heading counts or missing proposal sections and the character size:

````text
Wording-dominant: 40/48 clause headings (83%), 350000 characters.
Reference document: no abstract, motivation, or design sections. 400000 characters.
````

Skipped-paper statistics include character count, section count, largest section, wording ratio, and audience. When Survey triaged the paper as Skipped, you receive a short classification-and-stats summary instead of the full assay. Methodology states triage skipped at Step 3 (Survey). Placeholder Model or Service lines are omitted.

## Paper Routing

At Survey, papers are routed to WG21 review groups through a six-stage classifier. Routing labels are advisory. An administrative (no-group) result is recorded for trace and eval. It does not skip remaining steps. Survey triage, not routing, is what can stop the full analysis.

Review-group labels are LEWG, LWG, EWG, and CWG. Each sits at the intersection of domain (library versus language) and mode (design versus wording). LEWG and LWG are library. EWG and CWG are language. LEWG and EWG are design. LWG and CWG are wording.

The default Survey path is regex catalog hits, every bound classifier slot (union of hypothesis hits), then a frozen histogram-gradient aggregator when the bound set is homogeneous NLI-only or seqcls-only. Regex stays on because the aggregator was trained on regex plus classifier features. Assay currently binds a single selector slot named `nli-small`. Routing runs on blanked paper so references, acknowledgments, and revision-history headings do not contribute hypothesis hits.

````python
from assay.paper_routing import route_paper

result = route_paper(
    paper_md,
    audience=audience,
    use_regex=True,
    use_learned_aggregator=True,
)
````

Regex catalog scoring is on by default (`use_regex=True`) and can be turned off so only classifier backends add hits. Classifier backends layer on top of regex (union, not replace). The learned aggregator is on by default (`use_learned_aggregator=True`) and can be disabled. Binding both NLI and a fine-tuned tagger in the same ensemble disables the learned aggregator and keeps the hand aggregate.

A stray mention is not enough to route. A label emits only when domain and mode co-fire across enough sentences (sustained co-firing). Zero labels above threshold means a non-proposal (administrative) document. A paper's declared audience list can influence group scores. Audience flags are independent: a LEWG label does not set LIBRARY, and a Library Evolution label does not set LEWG.

Headings are classified into seven section types so later routing can treat sentences by where they appear: preamble, motivation, design, wording, impact, implementation, or appendix. Hypotheses sit on two independent axes (Domain and Mode) plus structural or meta signals. The frozen catalog has 38 hypotheses. You do not configure hypothesis catalog IDs, feature-name JSON, or per-label thresholds in normal operation. Those ship frozen with the wheel. Routing scores at most 3000 sentences per paper and skips sentences shorter than 20 characters.

## References, RAG, and Standard Lookups

The paper is scanned line by line for WG21 D, P, and N paper numbers and URLs, without an LLM or HTTP fetch. Cited papers are cross-checked in paperstore: existence, stale revisions, and self-citations.

An ephemeral in-memory vector index is built over cited papers that already have markdown in paperstore. The paper under analysis is excluded (case-insensitive). Other papers by the same author remain in the index as companion papers. Network I/O is limited to embedding-model loading. Cited-paper markdown is split on H2 and H3 headings into RAG chunks of about 400 tokens. Oversized sections split on blank-line paragraph boundaries with no overlapping windows. The parent heading is prepended onto each sub-chunk.

Retrieved hits are formatted as markdown under a heading "Evidence from cited papers." Hits below cosine 0.3 are dropped. Ranking is capped per paper so one cited paper cannot dominate (query defaults: top 5 hits, at most 3 hits per paper). Evidence injection is capped at 3000 characters. Cited-paper RAG hits are injected into each Research lens prompt.

Only the Specification lens receives the C++ standard MCP tools. Web search remains available for non-normative context. The standard client talks to cpp-mcp through an authenticated Bearer session.

````text
Authorization: Bearer <CPP_MCP_API_KEY>
````

Lookups can be pinned to a named draft instead of the server default. Standard tools can list ingested drafts; check whether a C++ type, function, keyword, or concept exists; look up a section by stable label such as `basic.life`; look up several sections in one round trip; fetch a numbered paragraph including its normative force; fetch a normative definition; fetch library API specifications matching a declaration pattern; search the standard; search the index; look up a grammar production; walk cross-references; walk the parent chain to chapter root; and recommend a tool plus parameters from a natural-language question.

`[stable.label]` citations, `[label] paragraph N` citations, and backtick-quoted C++ names are pulled from paper text and can be prefetched into prompt-ready Standard context and verification blocks.

Probe inventories cited papers and lists which revisions are stale. Author overlap is Jaccard similarity between the analyzed paper's authors and each referenced paper's authors.

## Extraction through Thesis

Extract uses a seven-way funnel that stops at the first match: ask, question, dependency, scope, concession, evidence, claim. Each extracted item is the shortest exact verbatim substring plus its line number. Quotes are checked against the paper markdown after collapsing whitespace. Ungrounded quotes warn; they do not fail the run.

Decide judges whether each claim is supported by evidence that is separate from the claim itself. A claim restating itself is not support. Accepted support is benchmarks, code or worked examples, citations or formal definitions, comparative tables, or explanatory mechanisms with technical detail.

Unsupported claims become gaps: a reviewer question, why it matters, primary and optional secondary lens, and severity. At Pass 1, severity is significant if retracting the claim breaks the paper's argument, otherwise minor. Critical is forbidden at Pass 1. Classify runs one LLM call per chunk that still has unsupported claims, so input and output cannot grow with paper size. If every claim is supported, the gap list is empty. Claims that fail their own chunk are re-judged against paper-wide evidence. A claim can flip to supported when another chunk supplies the evidence, with supporting line numbers recorded.

Collect is pure Python. Claims, evidence, concessions, and asks are deduplicated by exact quote, then a shorter quote is absorbed into a longer one that contains it. Questions, dependencies, and scope stay as raw per-chunk lists. Gaps are bucketed under the six lenses in fixed order. A gap may be indexed under both primary and a different secondary lens. Rationale is always in play even when that lens has no gaps. Empty other lenses are listed as inactive.

Derive compresses collected claims into a one-sentence thesis, derived bottom-up. A one-sentence case summary covers what the paper argues, what problem it addresses, what it covers and does not, and which claims are load-bearing. After Derive, a gap that touches the central thesis is upgraded from significant or minor to critical.

What the paper asks the committee to do is recorded as adopt, direction, review, poll, feedback, or inform. Ask calibration defaults to direction. Supporting evidence is ranked on a six-rung quality ladder: field experience, implementation, prototype, example, assertion, citation only. Bare citation markers such as "[10,11]" are evidence, not dependencies. One fenced code block may become multiple evidence items. For wording-heavy normative text, evidence is preferred over claim, and individual quotes stay under about 500 characters.

Paper text never enters the main context. Excerpts are injected as untrusted numbered lines.

## Review: Verify, Research, Challenge, and Verdict

Each section is read a second independent time for gaps: claims without evidence, design choices without rationale, performance assertions without benchmarks, and comparisons without data.

Verify searches companion papers by the same author or authors via semantic similarity. A gap closes only when the companion supplies direct evidence answering the gap question. Up to four companions with at least 50 percent author overlap are considered, in descending overlap. Closes apply before the next companion. Verify continues if one companion call fails. Verify is skipped entirely when no embedder is configured.

Research runs per lens with a budget of three web searches, stopping early if the first two return nothing relevant. Only findings that connect to the thesis are retained. If one lens fails, that lens records empty findings and the others continue.

Analyze examines each chunk against the thesis, load-bearing claims, cross-chunk gaps, six-lens research, and twenty-five standard test patterns. It produces findings (severity, explanation, test name, examiner role, damage statement, confidence) and strengths (well-supported load-bearing claims with no gaps). Analyze context is capped at 20 cross-chunk gaps, 10 companion evidence quotes, and 3 research findings per lens.

Rationale scores completeness against a five-item SD-4 mechanical checklist, each marked pass or fail with a location and a note. Quality findings emit when the checklist passes structurally but the content is shallow. The Rationale prompt shows at most 30 claims and 30 evidence quotes.

Challenge is an appeals desk. Findings are cross-examined through ordered kill grounds and stop at the first failure. The six grounds in the prompt are Concession, Phantom, Resolution, Technical accuracy, Plausibility, and Substance.

A finding is struck when the paper already concedes the point openly. A finding is struck when it attacks an inference rather than a statement the paper actually made. A finding is struck when the paper's own text, even in another section or implicitly, resolves the concern. A finding is struck when only exhaustive mechanical analysis would produce it, because it does not model a real committee-member concern. A finding is struck when it is editorial, formatting, or stylistic rather than structural.

A named standard C++ mechanism resolves a finding when the Standard verification block confirms the mechanism exists. The paper is not required to show the full implementation. A finding that asserts a language or ABI change is required is killed when the verification block shows a library-level solution already exists.

Challenge is fed the paper's concessions, scope statements, already-resolved Verify closes, and companion contradictions so it does not re-raise closed gaps. If Challenge output is truncated or incomplete, the run aborts rather than emit an unjudged finding. The error names each unjudged finding by id and title. After Challenge, ungrounded quotes in surviving findings and strengths warn without failing the run.

Couple detects compound dynamics only when one finding's consequence is the input that triggers another, or fixing A alone fails because B blocks the same path. Thematic similarity is not a compound. When compounds exist, one is designated the dominant dynamic (the compound with the longest constituent chain). Each compound is named, lists constituent finding IDs, states the causal mechanism, marks whether it spans lenses, and records an emergent risk. Couple is skipped when nothing survived Challenge.

A surviving finding is promoted to Major when it is a compound constituent or shares at least three content words with the thesis (stop words excluded). Compound membership is preferred over thesis-overlap when both would promote the same finding.

Synthesize is pure Python. Sound with High confidence is the verdict when no findings survive, or when survivors exist but none are critical or significant. Weakened is the verdict when critical or significant findings survive without contradicting the thesis, with High confidence if any are critical and Medium if only significant. Undermined with High confidence is the verdict when a critical surviving finding overlaps the thesis. The thesis still stands on Sound and Weakened, and has fallen on Undermined. Insufficient remains the default until synthesis places the paper. Skipped remains the Survey triage outcome, not a synthesized quality label.

An empty findings section is the honest outcome when claims were supported, design choices justified, citations verified, and the rationale complete.

## Report and Trace

The finished analysis is `{pid}.assay.md` in paperstore. The report delivers the determination first, before findings.

The Verdict block shows label, confidence, whether the thesis survives, and critical, significant, and minor finding counts. After the determination you see: asks of the committee, the structural assessment, any compound dynamics, major findings in order of severity, regular findings, strengths, the rationale checklist, the reference table, and the complete inventory of what was extracted, filed, challenged, and survived.

Asks are listed with quotes and line numbers, or fall back to declared intent (ask or info) or inferred ask calibration including wording-line and CWG or LWG signals. Major Findings are separated from regular Findings. Each has severity, lens, test, quote, line, and explanation. Majors also have examiner and damage. A header notes how many survived challenge and how many were killed. Strengths are quoted, line-located claims the analysis judged well-supported.

Paper references are tabulated (link, resolved pid, count, status including in-paperstore, stale, and author-overlap). Standalone hyperlinks are listed with URL and line. C++ standard `[stable.label]` citations in the rendered report become eel.is hyperlinks (`https://eel.is/c++draft`).

The SD-4 rationale checklist shows pass or fail marks. A missing location is shown as absent, plus a numeric score. Compound dynamics show constituents, mechanism, and emergent risk. One compound is named as the dominant dynamic when a structural assessment is present. A structural summary states how many major findings participate in compound dynamics versus overlap the thesis.

The inventory counts claims, evidence, concessions, questions, dependencies, gaps by severity, findings generated, survived, and killed, majors, regulars, compounds, and strengths. Killed findings are grouped by challenge type in descending frequency. Unique gaps are counted once per gap id, keeping the more severe copy when the same gap appears under multiple lenses. Methodology names the paper and chunk count. The ratio of generated, survived, and struck findings is part of the record.

A stored assay can be re-rendered from database rows plus the current report template without re-running the LLM pipeline:

````bash
paperflow assay P4003R3 --rerender
```` A rerendered inventory omits questions, dependencies, and scope because those collections are not reloaded from the database. The report layout is changed by editing the Jinja in the assay markdown document. Python precomputes sorting, counting, and conditionals so the template only iterates and displays. The report step fails if that section has no fenced Jinja template.

A compact diagnostic trace covers every executed step up through a chosen step number, with named headings for all 18 steps:

````markdown
## Step 4 (Extract)
## Step 8 (Derive)
````

Per-step wall time appears on each trace heading. Trace quotes are truncated so the dump stays compact. Full I/O lives in debug. Step artifacts persist after the steps that produce them: references, collected items, thesis, gaps, strengths, checklist, findings, compounds, and synthesis.

Read `{pid}.assay.md` for the determination. Use debug when you need the exact LLM I/O. Use trace, or stop after a step, when you need to see whether a stage ran and what shape it produced. That is enough to run assay on a paper you already have in paperstore and to interpret the file it writes.
