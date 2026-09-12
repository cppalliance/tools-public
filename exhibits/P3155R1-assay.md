# P3155R1 Assay

noexcept policy for SD-9 (The Lakos Rule)

The paper's quantitative centerpiece - an 82% Lakos Rule adherence survey - rests on undisclosed LLM-assisted methodology, and the strongest conclusion drawn from it ("the only choice consistent with the status quo") overreaches the data by ignoring alternatives that accommodate the 16% principled violations.

---

## Verdict

**Weakened** (High)

The paper argues that the Lakos Rule should be reconfirmed as official LEWG policy because 82% of narrow-contract functions in the C++ Standard Library already follow it, because the rule is foundational for C++26 contract assertions, and because abandoning it would irreversibly preclude programmatic recovery and negative testing. The thesis survives (High): no finding directly contradicts it, and the companion paper P2831R0 delivers the deferred technical rationale with field-experience evidence. However, 7 findings survived challenge (3 critical, 2 significant, 2 minor) and 1 was killed. The paper needs revision but the direction is viable.

---

## Asks

- **LEWG**: "We propose to retain the noexcept policy that we have already had for a long time and that the vast majority of the C++ Standard Library follows today" (adopt)
- **LEWG**: "Append to 'List of Standard Library Policies' section of SD-9 the items a)-f) enumerated in Section 4 above" (adopt)

---

## Structural Assessment

P3155R1 is an envelope paper: it wraps the detailed technical arguments of P2831R0, P2861R0, and P3005R0 in SD-9-compliant packaging, adds a new quantitative survey of Lakos Rule adherence, and asks LEWG to adopt the existing P0884R0 policy rules into SD-9. The structure is effective for its stated purpose. The rationale section provides seven clear arguments, the prior-art survey provides hard numbers, and the policy wording is concrete and actionable.

The structural weakness is that the paper's two original contributions - the survey and the "only choice consistent" conclusion - are both vulnerable. The survey's LLM methodology is undisclosed, and the conclusion drawn from it leaps past alternatives without examination. The contracts argument, the paper's strongest forward-looking pillar, rests on claims about EWG intent and design assumptions that are asserted without citation. When these findings compound, a pattern emerges: the paper relies on the reader already agreeing with the Lakos Rule rather than building a self-contained case. For a policy paper under the P2267R1 framework, where the goal is to establish consensus among committee members who may not already agree, this is a structural deficiency.

The companion deferral is sound. Probe confirms P2831R0 delivers all three deferred topics (rationale, case studies, technical arguments) with field-experience quality evidence. The envelope architecture works - but only if the reader follows the cross-references.

---

## Compound Dynamics

### Evidence Fragility

**Constituents:** Findings 1, 2, 6

**Mechanism:** The paper's empirical centerpiece (82% survey) has undisclosed LLM methodology (Finding 1). The conclusion drawn from that survey overreaches the data (Finding 2). The paper's alternative cost comparison ("orders of magnitude slower") is also unsubstantiated (Finding 6).

These three findings interact to create a pattern where the paper's internally-generated evidence is either under-validated or overstated. The survey could be challenged on reproducibility grounds; the conclusion could be challenged on logical grounds; the performance claim could be challenged on empirical grounds. A reviewer who questions any one of these will find the other two reinforce the doubt. The emergent risk is that a single methodological challenge to the survey could cascade to undermine the paper's strongest quantitative argument.

---

### Contracts Grounding Gap

**Constituents:** Findings 3, 4

**Mechanism:** The paper claims C++26 contracts were designed assuming the Lakos Rule (Finding 3) and that EWG has rejected removing throwing handlers "multiple times" (Finding 4). Neither claim is cited.

External research partially supports Finding 4: EWG did achieve consensus at St. Louis 2024 to keep throwing violation handlers. But the paper asserts a pattern of repeated rejection without any poll numbers or meeting references. Finding 3 is the more consequential gap: if the contracts community disputes that their design assumed the Lakos Rule, the mutual-exclusivity framing weakens. The emergent risk is that the contracts pillar, the paper's strongest forward-looking argument, could be challenged on historical accuracy rather than technical merit. Cross-lens: Design + Rationale.

---

## Major Findings

6 findings promoted to Major (touch thesis or compound constituent). 7 total survived challenge, 1 killed.

### 1. Undisclosed Survey Methodology

**Severity:** critical
**Lens:** Rationale
**Test:** novel

> "The quantitative survey of Lakos Rule adherence across the entire C++ working draft has been performed with the help of an LLM."

(line 151)

The 82% adherence figure (1053 of 1284 narrow-contract functions follow the Lakos Rule) is the paper's strongest internally-generated evidence. The disclaimer acknowledges LLM assistance but discloses no methodology: which model, what prompts, how functions were classified, what validation was performed, what the error rate is. The prompts are "available from the authors upon request" - but a policy paper under the P2267R1 framework should be self-contained and reproducible. For ask type "adopt," every load-bearing claim requires evidence at prototype tier or above; an unvalidated LLM survey does not meet this bar without disclosed methodology.

**Examiner:** specification reviewer

**Damage:** The 82% figure anchors claims C25 ("largely following"), C26 ("not random, but principled"), and C27 ("the only choice consistent"). If the survey methodology is challenged, all three claims lose their empirical foundation.

---

### 2. "Only Choice" Logical Leap

**Severity:** critical
**Lens:** Rationale
**Test:** novel

> "Our analysis demonstrates that the Lakos Rule is the norm in the C++ Standard Library today. Therefore, reinstating the Lakos Rule as official LEWG policy is the only choice consistent with the status quo in the C++ Standard Library specification."

(line 107)

The paper's own data shows 15.9% of narrow-contract functions (204 functions) violate the Lakos Rule, and that these violations are "principled" and "clearly localised." The leap from "82% adherence with principled exceptions" to "the only choice consistent with the status quo" ignores alternatives that could codify both the rule and its principled exceptions (e.g., Policy D from P3005R0 with carve-outs, or the existing clusters as named exemptions). The paper does not explain why a policy that accommodates the 16% would be "inconsistent" with the status quo.

**Examiner:** specification reviewer

**Damage:** The claim that no alternative is consistent with existing practice is the bridge between the survey evidence and the policy ask. If the bridge does not hold, the survey supports a weaker conclusion: "the Lakos Rule is the dominant pattern" rather than "the only consistent choice."

---

### 3. Unsubstantiated Contracts Design Assumption

**Severity:** critical
**Lens:** Design
**Test:** 7 (Unstated Assumption)

> "The Lakos Rule is foundational for C++26 contract assertions, which were designed with the assumption that the Lakos Rule is an established design principle."

(line 70)

No citation to EWG minutes, SG21 design papers, P2900 revision history, or any statement from the contracts authors supports the claim that C++26 contracts were "designed with the assumption" that the Lakos Rule holds. The contracts feature permits throwing violation handlers, which is consistent with the Lakos Rule - but "consistent with" is not "designed assuming." External research confirms EWG consensus at St. Louis 2024 to keep throwing handlers, but this reflects a design choice about handler semantics, not an assumption about library noexcept policy.

**Examiner:** specification reviewer

**Damage:** The mutual-exclusivity argument (contracts + noexcept = broken) is the paper's strongest forward-looking argument. If the contracts design did not in fact assume the Lakos Rule, the framing shifts from "we must reinstate the rule to honor the contracts design" to "we should consider the rule because it happens to be compatible with contracts."

---

### 4. Uncited EWG Rejection History

**Severity:** significant
**Lens:** Rationale
**Test:** novel

> "doing the latter has been rejected multiple times in EWG, whose position is clearly that throwing contract-violation handlers belong in the language."

(line 70)

No poll numbers, paper references, or meeting identifiers are cited for the claim that removing throwing handlers was "rejected multiple times." External research confirms one clear data point: EWG achieved consensus at St. Louis 2024 to keep throwing handlers, and the Tokyo 2024 poll was evenly split before that. But "multiple times" implies a longer history of rejections that the paper does not substantiate.

**Examiner:** specification reviewer

**Damage:** The argument that "EWG has clearly decided" constrains the design space. Without verifiable precedent, this reads as the authors' interpretation of committee sentiment rather than documented committee position.

---

### 5. Zero-Cost Framing Without Counterargument

**Severity:** significant
**Lens:** Design
**Test:** 23 (Alternative Deficit)

> "retaining the Lakos Rule costs nothing - on the other hand, abandoning it removes options irreversibly."

(line 64)

The claim that retaining the Lakos Rule "costs nothing" does not address known counterarguments. External research shows all three major Standard Library implementations (libstdc++, libc++, MSVC STL) already strengthen Throws: nothing to noexcept on narrow-contract functions. This means the Lakos Rule describes the specification, not the deployed reality. Retaining the rule preserves a specification-implementation gap that P3085R3 argues is itself a cost: implementations that mark vector::operator[] as noexcept cannot easily un-mark it. The paper does not address this tension.

**Examiner:** library author

**Damage:** The asymmetry argument (retaining preserves options, abandoning removes them) is logically sound in principle but ignores the practical asymmetry already created by implementations. A reviewer familiar with P3085's counterarguments will find this one-sided. (medium confidence)

---

### 6. Unexamined Alternatives

**Severity:** significant
**Lens:** Rationale
**Test:** 23 (Alternative Deficit)

> "Note that this set of rules corresponds to Policy C in [P3005R0], which considers seven possible noexcept policies B-H in addition to the null policy A ('no policy')."

(line 135)

The paper references P3005R0's seven candidate policies but does not evaluate any alternative. It does not engage with P3085R3's counterarguments despite being the direct competitor for the same SD-9 policy slot. It does not discuss P2946R0's [[throws_nothing]] proposal, which could dissolve the tension between the Lakos Rule and noexcept by separating optimization hints from contract semantics. For a policy paper asking LEWG to adopt a specific policy, the absence of systematic comparison is a structural gap. P2267R1's requirements for policy papers include demonstrating why the proposed policy is preferable.

**Examiner:** specification reviewer

**Damage:** LEWG members familiar with P3085 or P2946 will find no acknowledgment of the arguments against the Lakos Rule in this paper. The paper argues for its position but does not argue against alternatives.

---

## Findings

### 7. Unsupported Performance Quantification

**Severity:** minor
**Lens:** Performance
**Test:** 1 (Unsupported Performance Claim)

> "All known alternatives (death tests via fork, clone, or spawn, setjmp/longjmp, child threads, signals, conditional-noexcept macros) are variously platform-specific and non-portable, orders of magnitude slower, UB-prone, or change the code under test"

(line 68)

"Orders of magnitude slower" is a quantitative claim about relative performance of testing approaches. No benchmark data, timing measurements, or citations support it. The qualitative assessment (non-portable, UB-prone, change code under test) may be accurate, but the quantitative claim is unsubstantiated.

---

### 8. Missing Migration Path for Existing Violations

**Severity:** minor
**Lens:** Specification
**Test:** 16 (Missing Migration Path)

> "204 functions (15.9%) are noexcept, i.e. they violate the Lakos Rule."

(line 81)

The paper documents 204 functions that currently violate the Lakos Rule but proposes no migration path. Should these be retroactively corrected via DRs? Grandfathered? Treated as named exceptions to the policy? The paper characterizes the violations as "principled" but the proposed policy wording (rules a-f) does not include a mechanism for principled exceptions beyond the enumerated carve-outs (destructors, swap/move, C-compatible functions, wrapping types). The gap between the policy as written and the existing practice it claims to codify is not addressed.

---

## Strengths

### Quantitative Survey Coverage

> "we counted 1284 narrow-contract functions in the C++ Standard library (out of 7165 total, i.e. 17.9%)"

(line 78)

Despite methodology concerns (Finding 1), the survey's scope is a genuine contribution. No prior paper has attempted a complete census of narrow-contract functions across the entire working draft. The categorical breakdown of violations into principled clusters (smart pointer accessors, atomics, deallocation, intrinsically-nothrow operations, C++26 additions) demonstrates analytical depth. Load-bearing for claim C25.

---

### Contract Widening Irreversibility

> "Once a function with a narrow contract is specified as noexcept, its contract can never be widened to throw on what was previously a contract violation."

(line 60)

The vector::operator[] example is concrete and widely understood. The argument is logically sound: noexcept is part of the type and ABI, observable via the noexcept operator, and breaks Liskov substitutability. Throws: Nothing preserves evolutionary freedom. This is the paper's strongest design argument. Load-bearing for claim C4.

---

### Compositional Asymmetry

> "implementations remain free to strengthen Throws: nothing to noexcept unilaterally"

(line 64)

The one-way nature of the restriction is a genuine structural advantage. A specification that uses Throws: Nothing permits implementations to be noexcept (and all three major ones are). A specification that uses noexcept forces all implementations and all downstream code to honor it. This asymmetry means the Lakos Rule is the strictly more permissive specification choice. Load-bearing for claim C13.

---

### Companion Evidence Delivery

The envelope architecture works. Probe confirms P2831R0 delivers all three deferred topics:

- **Rationale for the Lakos Rule:** Delivered (true). Systematic treatment of seven arguments with case studies.
- **Case studies of companies:** Delivered (true). Cradle (gaming) and Maven Securities (finance) provide first-person field-experience reports of exception-based negative testing and programmatic recovery.
- **Technical arguments against noexcept on narrow-contract functions:** Delivered (true). libc++'s abandoned _NOEXCEPT_DEBUG experiment provides concrete implementation-failure evidence.

---

## Rationale Checklist

| # | Item | Pass | Location | Note |
|---|------|------|----------|------|
| SD4-1 | Motivating Examples | fail | "1 Rationale" (partial) | One inline example (vector::operator[]) but no before/after code. Detailed examples deferred to P2831R0. |
| SD4-2 | Design Principles | pass | "1 Rationale" | Articulates contract widening, Liskov substitutability, compositional asymmetry, and implementation freedom as design principles. |
| SD4-3 | Alternatives Considered | fail | absent | References P3005R0's seven policies but does not compare them. Does not engage with P3085 or P2946. |
| SD4-4 | Cost Acknowledgment | fail | absent | Does not address implementation burden, documentation cost, teaching cost, or backward compatibility impact. |
| SD4-5 | Beneficiary Identification | pass | "1 Rationale" | Names gaming, desktop publishing, host-plugin systems, and negative-testing practitioners as beneficiaries. |

**Score:** 2/5

The two failures (Alternatives, Cost) are the same gaps identified by Findings 5 and 6. The Motivating Examples failure reflects the envelope structure: the detailed examples live in P2831R0, not in this paper. For a standalone policy paper, this is a structural weakness; as an envelope paper, it is by design.

---

## Reference Table

| Ref | Tier | Source | Link | Status | Notes |
|-----|------|--------|------|--------|-------|
| N2855 | background | Gregor, Abrahams (2009) | [open-std.org](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2009/n2855.html) | live | Rvalue references and exception safety |
| N3248 | predecessor | Meredith, Lakos (2011) | [open-std.org](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2011/n3248.pdf) | live | Original Lakos Rule proposal. Same-author. |
| N3279 | predecessor | Meredith, Lakos (2011) | [open-std.org](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2011/n3279.pdf) | live | Conservative use of noexcept. Same-author. |
| N5046 | dependency | Koppe (2026) | [wg21.link/n5048](https://wg21.link/n5048) | dead | URL typo: reference says N5046 but URL points to n5048. wg21.link/n5046 resolves correctly. |
| O'Dwyer2018 | background | O'Dwyer (2018) | [quuxplusone.github.io](https://quuxplusone.github.io/blog/2018/04/25/the-lakos-rule/) | live | Blog summary of the Lakos Rule |
| P0884R0 | predecessor | Josuttis (2018) | [open-std.org](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0884r0.pdf) | live | Extended noexcept policy. Rules a-f originate here. |
| P1656R2 | background | Berge (2020) | [open-std.org](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p1656r2.html) | live | Proposed overturning the Lakos Rule |
| P2148R0 | background | Johnson, Lelbach (2020) | [open-std.org](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2148r0.pdf) | live | Library Evolution Design Guidelines |
| P2267R1 | dependency | Levi, Craig, Fracassi (2023) | [wg21.link/p2267r1](https://wg21.link/p2267r1) | live | Policy paper framework this paper must satisfy |
| P2831R0 | companion | Doumler, Catmur (2023) | [wg21.link/p2831r0](https://wg21.link/p2831r0) | live | Primary companion. Delivers: rationale, case studies (Cradle, Maven Securities), technical arguments. Same-author. |
| P2861R0 | companion | Lakos (2023) | [wg21.link/p2861r0](https://wg21.link/p2861r0) | live | Companion treatise on inherent incompatibility. Same-author. |
| P2920R0 | background | Lelbach et al. (2023) | [wg21.link/p2920r0](https://wg21.link/p2920r0) | live | LEWG leadership's policy history understanding |
| P3004R0 | background | Lakos et al. (2024) | [wg21.link/p3004r0](https://wg21.link/p3004r0) | live | Principled Design methodology. Same-author. |
| P3005R0 | companion | Lakos et al. (2024) | [wg21.link/p3005r0](https://wg21.link/p3005r0) | live | Seven candidate policies framework. Same-author. |
| SD-9 | dependency | Levi (2024) | [wg21.link/sd9](https://wg21.link/sd9) | live | Standing document this policy targets |

**Reference tally:**
- Total: 15 references (14 with URLs, 0 non-electronic)
- Link status: 14 live, 1 dead (N5046 URL typo)
- Companions read: 1 of 3 companion-tier references (P2831R0)
- Deferred topics: 3 total, 3 delivered, 0 partial, 0 not delivered

**Tier distribution:**
- companion: 3
- predecessor: 3
- dependency: 3
- citation: 0
- background: 6
- tool: 0

---

## Inventory

**Items** (from `collect.items`):
- Claims: 31 (10 factual, 21 normative)
- Evidence: 21 (tiers: 2 field_experience, 10 implementation, 0 prototype, 2 example, 0 assertion, 7 citation_only)
- Concessions: 5
- Questions: 0
- Dependencies: 0
- Scope: 10 (8 covered, 2 gap)

**References** (from `collect.reference_registry`):
- Total: 15 unique references
- By tier: 3 companion, 3 predecessor, 3 dependency, 0 citation, 6 background, 0 tool
- Same-author: 6
- With URL: 15
- Non-electronic: 0

**Breadcrumbs** (from `collect.breadcrumbs_by_lens`, post-upgrade):
- Total: 19 (10 critical, 2 significant, 7 minor)
- By lens: Performance 2, Design 2, Usability 1, Ecosystem 4, Rationale 10

**Findings** (from `challenge`):
- Total generated: 8
- Survived: 7 (3 critical, 2 significant, 2 minor)
- Killed: 1 (1 conceded, 0 boundary, 0 falsified)
- Major: 6
- Regular: 2

**Compounds** (from `couple`):
- Total: 2
- Cross-lens: 2

**Strengths** (from `analyze`):
- Total: 4

---

## Methodology

- Paper: P3155R1, "noexcept policy for SD-9 (The Lakos Rule)"
- Model: claude-4.6-opus
- Date: 2026-06-05
- Chunks: 13 sections, ~612 tokens estimated

**Pass 1 (Steps 1-4):**
- Survey: 1 sub-agent
- Extract: 3 batch sub-agents (13 chunks), 67 items, 19 breadcrumbs, 4 asks, 30 references
- Collect: 31 unique claims, 21 unique evidence, 15 unique references
- Derive: thesis from 31 claims, 7 load-bearing, ask calibration: adopt

**Probe (Step 6):**
- Link verification: 15 URLs checked, 14 live, 1 dead
- Relevance ranking: 15 references ranked
- Companion ingestion: 1 companion read (of 3 companion-tier) - P2831R0
- Deferred topics: 3 identified, 3 delivered, 0 partial, 0 not delivered
- Claim verification: not performed (no citation-subtype evidence items requiring cross-check)

**Research (Step 5):**
- 5 lens sub-agents (Specification inactive), 15+ external sources found

**Pass 2 (Steps 7-10):**
- Analyze: 6 substantive chunk analyses + 1 Rationale, 8 findings, 4 strengths
- Challenge: 8 total, 7 survived, 1 killed (conceded)
- Compounds: 2 identified
- Rationale checklist: 2/5
- Verdict: Weakened (High)
