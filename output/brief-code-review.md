# Code Review: The Briefer

- **Date:** 2026-04-13
- **Model:** Opus 4.6

A well-architected happy-path machine with a contract hole in its output schema and no error surface.

## Executive Summary

The Briefer is a ten-phase analytical compiler specified in ~800 lines of imperative prose. Its pipeline design is strong: research phases compress external reality through fast sub-agents with anti-hallucination guards, the main-context analytical kernel runs 45 diagnostic tests with dual adversarial challenge rounds, and a coupling analysis phase discovers compound dynamics that no individual test could find. The Briefer/Analyst separation is clean. The breadcrumb-to-coupling-map data path is elegant. The token economics are explicitly bounded.

The specification has one high-severity contract violation: Section 6 of the Brief template (Predictions) demands calibrated, time-horizoned, conditional predictions that no phase in the pipeline is instructed to produce. The entire error and recovery surface is unspecified - sub-agent failure, all-clean diagnostic results, cache corruption, and crash-during-write all produce undefined behavior. Structural rules are stated in multiple locations with slightly different wording, creating divergence risk on future edits.

## Synthesis

### The Missing Producer

Phase 9 (Synthesis) defines seven explicit steps: consume the coupling map, identify the dominant dynamic, select a historical parallel, generate Section 4 headers, determine the prognosis, evaluate GFT coherence, and write the internal thesis. None of these steps generate the time-horizoned conditional predictions that Section 6 of the Brief template requires. The prognosis (step 5) classifies the subject's state but does not project trajectories with confidence levels. Section 6 asks for "Short-term, medium-term, long-term" predictions with "If X, then Y. If not, then Z" structure. This content has no defined origin anywhere in the pipeline. An implementer must either invent the Predictions step or skip Section 6.

### The Undefined Error Surface

The spec covers its happy path to the level of individual field names in breadcrumb packets but provides zero specification for failure modes:

- If Reconnaissance returns empty (obscure subject, web search failure), the pipeline has no domain primer, no market structure classification, and no domain-specific rules. Phase 5 runs 45 tests without domain context. No fallback or abort condition exists.
- If all 45 tests come back clean, there are no findings, no breadcrumbs, no coupling map, and no compound dynamics. Synthesis step 2 ("Which compound dynamic would improve the most other findings?") presupposes at least one compound exists. The path through Synthesis for the empty case is undefined.
- If a Regenerate command overwrites the prior report and the pipeline then fails mid-execution, the prior report is lost with no replacement. No atomic-write or crash-recovery protocol exists.
- Cache corruption (partial writes, missing required fields, incompatible structure from spec evolution) produces undefined behavior. No validation, versioning, or recovery path exists.

### The Duplication Risk

Four structural rules are stated in multiple locations:

1. The main-context delegation rule appears in Phase 5 and in Token Economics, including the Phase 7 exception. Both must be updated together.
2. The zero-false-positive rule appears in Phase 2 and Phase 3 with slightly different wording.
3. Progress reporting is stated as a general rule and re-invoked per-phase three times.
4. Section 5 conditionality is described in Synthesis step 6 and in the Brief template.

Each duplication is a future-edit divergence risk. A single canonical statement with forward references would be more maintainable.

### Implicit Interfaces

The two-command interface (Evaluate, Regenerate) is clean but thin. Users also interact with the spec through an implicit filesystem interface: inspecting cache files to check freshness, deleting cache files to force re-collection, browsing `.reports/` for prior evaluations. The spec doesn't acknowledge cache deletion as a supported operation, offers no status or inspection command, and provides no manual cache invalidation path. A user who knows the cache is stale (major event just occurred) must wait 21 days or perform an undocumented filesystem operation.

### Concurrency Gaps

Phase 3 (Theoretical Foundation) is marked "Sequential with Reconnaissance - never parallel" but the rationale is implicit. The likely dependency is that Theoretical Foundation needs domain identification from Reconnaissance, but this is never stated. If an implementer discovers the Phase 3 prompt doesn't actually consume Phase 2 output, they might parallelize and lose nothing - or they might break an unstated contract.

Within Phase 5, the 45 tests are independent by design, but the spec neither permits nor forbids parallel execution. Since they run in main context, practical parallelism is unlikely, but the spec should state whether test ordering matters.

## Files With Findings

### brief.md

The Briefer - a natural-language tool specification (~800 lines) that drives an AI through a ten-phase institutional analysis pipeline using Great Founder Theory, IO economics, and political-risk framing. Key abstractions: phases with hard delegation rules, 45 numbered diagnostic tests with cluster tags, breadcrumbs for coupling analysis, dual adversarial challenge rounds, and a cache/report separation.

- **Bugs, flag:** Section 6 (Predictions) has no upstream pipeline producer. The Brief template demands calibrated, time-horizoned, conditional predictions that no phase generates. Severity: high.
- **Bugs, flag:** Coupling map entry path is described contradictorily. Phase 7 says the map "enters the main context as compressed input to Synthesis." Phase 8's closing says "Compounds that survive enter the main context as the coupling map." Phase 8 already operates on the map in main context. Severity: medium.
- **Bugs, advisory:** Section numbering gap when Section 5 is omitted - output jumps from 4 to 6. No rule says whether to renumber or preserve the gap.
- **Bugs, advisory:** Evaluate command skips Reconnaissance on cache hit but not Theoretical Foundation, despite the cache storing both. Wastes a sub-agent call on every cached evaluation.
- **Bugs, advisory:** Regenerate overwrites prior report before pipeline completes. Pipeline failure after overwrite loses the prior report with no replacement.
- **Documentation, flag:** `AskQuestion` (Phase 4) is referenced but never defined. An implementer cannot distinguish between a platform API call, a message format, or a conceptual instruction. Severity: medium.
- **Documentation, advisory:** "Fast model" and "parent model" are used throughout as delegation targets but never defined.
- **Documentation, advisory:** "GFT findings (tests 1-17)" conflates section grouping with theoretical origin. Many tests in that range cite non-GFT sources.
- **Documentation, advisory:** Phase 7 sub-agent prompt is underspecified compared to Phases 2-3, which give explicit bullet-list request formats.
- **Documentation, advisory:** "Light refresh" for stale cache is underspecified - no definition of "recent activity," baseline communication, or merge-on-contradiction rules.
- **Contract fidelity, flag:** Section 6 (Predictions) contract violation - the output schema demands content no phase produces. Severity: high.
- **Contract fidelity, advisory:** Opening paragraph omits Phase 4 (User Questions) and Phase 8 (Coupling Challenge) from the pipeline overview.
- **Contract fidelity, advisory:** Phase 8 (Coupling Challenge) outcomes are not explicitly included in the cache's Diagnostic Detail section.
- **Error handling, flag:** Sub-agent failure is unaddressed. Empty Reconnaissance leaves Phase 5 without domain context. No fallback or abort. Severity: medium.
- **Error handling, flag:** All-45-tests-clean path is undefined. Synthesis presupposes at least one compound dynamic exists. Severity: medium.
- **Error handling, advisory:** Phase 4 no-answer path uses "enough ground truth" without defining the threshold.
- **Error handling, advisory:** Model ID fallback is missing - the Brief footer requires it but no rule handles absence from system prompt.
- **Duplication, advisory:** Main-context delegation rule stated in Phase 5 and Token Economics (divergence risk).
- **Duplication, advisory:** Zero-false-positive rule stated with different wording in Phase 2 and Phase 3.
- **Duplication, advisory:** Progress reporting general rule echoed per-phase three times.
- **Duplication, advisory:** Section 5 conditionality described in both Synthesis step 6 and Brief template.
- **Single responsibility, advisory:** Phase 9 (Synthesis) performs seven distinct sub-steps - highest internal complexity of any phase.
- **Resource management, advisory:** Main context token budget is implicit. A subject with 30+ surviving findings could overflow.
- **Resource management, advisory:** Cache corruption unhandled - no validation, no recovery path.
- **Resource management, advisory:** No cache size bound. Diagnostic Detail for complex subjects could grow unbounded.
- **Formatting, advisory:** Missing blank lines before horizontal rules at test-subsection boundaries (between Institutional Health/Economic and Economic/Labor). Some parsers will not render these correctly.
- **Formatting, advisory:** Brief template heading hierarchy skip - title uses `#`, characterization uses `###`, sections use `##`. The subtitle sits below section level.
- **Security, advisory:** No prompt-injection defense on subject description. Adversarial input flows directly into sub-agent prompts.
- **Security, advisory:** Web-sourced content enters sub-agents without sanitization. Zero-false-positive guards hallucination but not adversarial web content.
- **Security, advisory:** Cache files have no integrity check. Filesystem access allows undetected modification of cached findings between runs.
- **Concurrency, advisory:** Phase 3 sequential constraint lacks stated rationale for the dependency on Phase 2.
- **Concurrency, advisory:** Within-Phase-5 test parallelism neither permitted nor forbidden.
- **API design, advisory:** No status or inspection command for cache state.
- **API design, advisory:** No manual cache invalidation command.
- **API design, advisory:** Cluster definitions are closed - no mechanism for domain-specific clusters from Reconnaissance.
- **API design, advisory:** Cache contract lacks corruption recovery, versioning scheme, and concurrent-access rules.

## Clean Files

| File |
|------|
| (none - single file under review) |
