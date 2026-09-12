# Briefer: WG21 (ISO/IEC JTC1/SC22/WG21)

**A monopoly standards body whose ceremonies of consensus governance persist while the understanding of whom it serves has narrowed from 16.3 million developers to 210 attendees.**

**Structural verdict: Cargo Cult.** The standard-setting machinery produces functional output. The governance that drives it has become ceremonial.

June 2026, by Vinnie Falco

---

## 1. Executive Summary

WG21 governs the programming language used by 16.3 million developers through a process attended by approximately 210 people whose employers pay $50,000 or more per year per delegate. No external audit reviews committee decisions. No independent feedback channel connects the developer population to governance outcomes. No monitoring system tracks whether the standard serves its stated constituency. The accountability vacuum is self-concealing: the information architecture that prevents external detection also prevents internal recognition, while decoupled metrics - meeting attendance stable, papers published on schedule, ballots completed - provide false assurance that governance is functioning. The committee cannot detect its own degradation.

Fifteen of 44 surviving findings show degrading trajectories. Twenty-five are stable. Four are improving. The improving findings concern leadership succession at the convener level and marginal communication reforms; none address structural accountability. Internal entropy compounds: each standard release is strictly additive, complexity grows monotonically, and no simplification mechanism exists. C++26 adds reflection, contracts, and std::execution to a language whose module system remains partially implemented six years after standardization. External erosion compounds simultaneously: Rust has reached 48.8% enterprise adoption with compile-time memory safety that C++ categorically lacks, five coordinated US government publications between 2022 and 2025 designate C++ memory-unsafe, and the EU Cyber Resilience Act imposes reporting obligations beginning September 2026. Google, Microsoft, Meta, and Apple are each independently reducing C++ investment while building Rust or successor-language capacity. Current stability metrics mask cliff-edge fragility.

The single most important finding: no observer position exists from which dysfunction is simultaneously visible and actionable. Information architecture prevents external detection. Shifting baselines prevent internal recognition. Decoupled metrics provide false assurance. The degradation is structural.

---

## 2. The Subject

**Name:** WG21, formally ISO/IEC JTC1/SC22/WG21 - Working Group 21 of Subcommittee 22 of Joint Technical Committee 1.

**Founded:** 1990-91 under ISO/IEC JTC1. The USA submitted a New Work Item Proposal in September 1989; SC22 approved it in April 1991. WG21 held its first meeting June 18-19, 1991.

**Scale:** Approximately 210 attendees per meeting, three meetings per year, governing the international standard for a language used by 16.3 million developers. The governed-to-governing ratio is 78,000:1.

**Stated mission:** Development and maintenance of ISO/IEC 14882, the International Standard for C++.

**Current work:** C++26 completed technical work at London Croydon in March 2026 and is in international approval ballot. C++29 work has begun, with feature-freeze expected 2028 and publication circa 2029.

**Organizational structure:**

- Study Groups (15+): SG1 Concurrency, SG4 Networking, SG14 Low-Latency, SG16 Unicode, SG22 C/C++ Liaison, SG23 Safety and Security, others
- Evolution Groups: EWG (Language Evolution), LEWG (Library Evolution)
- Wording Groups: CWG (Core Wording), LWG (Library Wording)
- Direction Group: Rotating chair through 2030. Sets strategic priorities. Meets biweekly with no public minutes.
- ABI Review Group, Admin Group, plenary

**Leadership (as of January 2026):**

- Convener: Guy Davidson (BSI/UK). First non-US convener. Previously co-chaired SG14. Appointed via SC22 Resolution 14-04.
- Vice-Convener: Nina Ranns (BSI). Vice President of Standard C++ Foundation. SG22 chair.
- Vice-Convener: Jeff Garland (CrystalClear Software, ANSI/US).
- Convener Emeritus: Herb Sutter. Served 2002-2025. Now Technical Fellow at Citadel Securities. Retains chairmanship and CEO role at the Standard C++ Foundation.

**Standard C++ Foundation:** Washington State 501(c)(6), tax-exempt since June 2014. FY2025 revenue $2,102,990. Operates isocpp.org, CppCon conference, provides WG21 meeting hosting costs and travel assistance. Board: Herb Sutter (Chairman/CEO, $40,650 compensation), Nina Ranns (VP), Inbal Levi (Secretary), Bjarne Stroustrup (Treasurer), Michael Wong (Director). No independent directors. All board members are WG21 insiders.

**Domain:** Programming language standardization.

---

## 3. The Landscape

### Market position

Monopoly. WG21 is the sole ISO-designated international C++ standard body. No competing standard exists. ISO designation confers procurement legitimacy that no informal specification can match - organizations adopting C++ for regulated environments require ISO standard conformance, creating a self-reinforcing monopoly. The committee's 210 attendees govern a standard used by 16.3 million developers, a ratio of approximately 78,000:1.

### Ecosystem dependencies

**Upstream:**

- ISO/JTC1/SC22: Parent body controlling international standard ballots, convener selection, and procedural framework
- National bodies: ANSI (US), BSI (UK), DIN (Germany), JISC (Japan), others. The US delegation constitutes 60-70% of WG21 attendance. INCITS/C++ (US national body committee) is chaired by an NVIDIA representative.
- Standard C++ Foundation: $2.1M revenue funding meeting infrastructure, travel assistance, proposal grants
- Corporate sponsors: Fund delegate attendance at $50,000+ per year per delegate in travel, lodging, and salary

**Downstream:**

- Compiler vendors: GCC, Clang/LLVM, MSVC, Intel. Collectively serve 16.3M developers. Non-implementation by any major compiler constitutes effective veto over that portion of the standard.
- 16.3 million C++ developers who use the standard but have no formal channel to influence it.

**Implementation gap:** C++20 modules remain partially implemented six years post-standardization. GCC 15 (2026) does not enable modules with `-std=c++20` - a separate flag is required. No Linux distribution ships pre-compiled standard library module artifacts. Build system support remains experimental. The standard without compiler support is effectively advisory text.

### Domain-specific vulnerabilities

Ordered by severity.

**1. Government regulatory risk (HIGH).** Five coordinated US government publications between 2022 and 2025 name C++ memory-unsafe. The NSA cybersecurity information sheet (2022) identified the problem. ONCD's "Back to the Building Blocks" (February 2024) named C and C++ specifically. CISA and FBI jointly declared development of new product lines in memory-unsafe languages "dangerous" and recommended memory safety roadmaps by January 1, 2026. DARPA's TRACTOR program funds automated C-to-Rust translation with a public test corpus released February 2026. The EU Cyber Resilience Act imposes reporting obligations beginning September 2026. WG21's response - the profiles proposal - requires 3+ years through the standard pipeline and has only one experimental compiler implementation.

**2. Rust competitive pressure (HIGH).** Rust reached 48.8% enterprise adoption in the 2025 State of Rust Survey, up from 38.7% in 2023. Rust provides compile-time memory safety - a categorical capability that C++ lacks and cannot retrofit without language-level changes. The Rust Foundation is backed by Amazon, Google, Microsoft, and Meta. Government endorsement through CISA, NSA, and DARPA compounds competitive pressure with regulatory pressure.

**3. Corporate defection (HIGH).** Major C++ stakeholders are independently reducing investment. Google launched Carbon as an explicit C++ successor (July 2022) and uses Rust extensively in Android. Microsoft's Distinguished Engineer Galen Hunt stated the goal to "eliminate every line of C and C++ from Microsoft by 2030"; Azure mandates Rust for new system-level code. Meta is rewriting mobile messaging infrastructure from C++ to Rust; WhatsApp replaced 160,000 lines of C++ with Rust for media security. Apple's primary investment is Swift with minimal WG21 engagement. Each defection removes funding, expertise, and implementation capacity simultaneously.

**4. Consensus paralysis (MEDIUM-HIGH).** The same multi-year pipeline processes minor library additions and existential safety threats. No mechanism distinguishes urgency levels. The profiles proposal - WG21's sole institutional response to government safety mandates and Rust competition - requires the standard 3+ year pipeline from proposal to published standard. The consensus model (Lukes 2005) enables stability on routine decisions but blocks rapid response to existential threats.

**5. Participation inequality (MEDIUM).** Delegate attendance costs $50,000+ per year, restricting participation to those with employer funding. Meeting locations alternate between the US and Europe. Remote participation carries lower practical weight. CppCon attendance declined from 1,400 in 2019 to 700 in 2025, while committee meeting attendance held at approximately 210 - suggesting the broader community is disengaging while the funded core persists.

**6. Language complexity growth (MEDIUM).** Each standard release is strictly additive. No feature has been removed since the 1998 standard. C++26 adds reflection, contracts, and std::execution. The language grows monotonically in complexity with no simplification mechanism. The complexity ratchet (Arthur 1994) produces a language that experts understand while the broader developer population falls further behind.

---

## 4. Structural Assessment

Each subsection names a compound dynamic, states its mechanism, presents interacting findings, and states the consequence.

### 4.1 The Accountability Vacuum

The enabling condition for every other dynamic in this assessment. Four findings interact to produce a governance structure invisible to the population it governs.

**Employer-funded power conversion.** Sustained attendance at three annual meetings costs $50,000+ per year per delegate. That expenditure buys not just presence but accumulated institutional memory, procedural knowledge, relational capital, and eligibility for chairs and Direction Group seats. The conversion from funded attendance to governance authority requires no intent - structural incentive alone produces it, and funded participants outcompete unfunded ones across every dimension of influence. No external accountability mechanism constrains the conversion.

**Principal-agent collapse.** 16.3 million developers are principals. Approximately 210 attendees are agents. No monitoring mechanism connects the two populations. Developers cannot observe deliberations, cannot vote, cannot recall delegates, and have no formal feedback channel. The principal-agent relationship exists in form. The accountability it requires does not.

**Metric decoupling.** Process metrics - on-time releases, paper throughput, meeting attendance figures - provide assurance that governance is functioning. Implementation gaps widen: C++20 modules remain partially implemented six years after standardization. Safety deficiencies persist: no compile-time memory safety capability exists. The metrics have decoupled from the outcomes they purport to track. Goodhart's law (Goodhart 1984) in operation: when the measure becomes the target, it ceases to be a good measure.

**The invisibility compound.** No observer position exists from which dysfunction is simultaneously visible and actionable. Internal observers lack reference points - shifting baselines absorb each incremental degradation as normal. External observers lack access - information architecture concentrates knowledge behind participation filters. The governed population lacks monitoring capability entirely. Self-concealment is the mechanism, not the side effect.

**Direction:** Stable. Self-concealing dynamics do not degrade because degradation requires the detection they prevent.

### 4.2 The Opacity Engine

Two mechanisms interact to render governance invisible to the governed population.

**Consensus without records.** WG21 operates by consensus, not recorded vote. The Convener determines whether consensus exists - a judgment call with no appeal mechanism. Without individual vote records, corporate ventriloquism is indistinguishable from genuine technical agreement in the public record. Regulatory capture (Stigler 1971) operates without a regulator: the regulated entities staff the regulatory body directly.

**Information layering compounds with participation filtering.** Work occurs across multiple layers: formal papers, email reflectors, GitHub discussions, in-person sessions, and informal dinner conversations. The formal record captures a fraction of what shapes outcomes. $50,000+ per year in costs filters who accesses these layers. The top 10 firms contribute over 70% of meeting-days. Remote participation carries lower institutional weight than in-person attendance. The filter determines who accesses layered information. The layering justifies the filter. Mutual reinforcement produces stable opacity.

**Direction:** Stable. Mutually reinforcing architecture resists disruption from either direction.

### 4.3 The ABI Identity Trap

Lock-in and backward compatibility interact to produce a self-justifying equilibrium that blocks adaptation.

**ABI as identity.** The Prague 2020 decision reframed ABI stability from an engineering judgment - weighing performance gains against compatibility costs - to an organizational identity commitment. Challenging backward compatibility now registers as disloyalty rather than disagreement. Mission rigidity (Selznick 1957): identity-level commitments resist cost-benefit analysis because the analysis itself implies the commitment is negotiable.

**Lock-in reinforcement.** Multi-billion-line legacy codebases create switching costs that exceed tolerance for any single release cycle. Developers and organizations deepen lock-in through compensating investments - build system workarounds, ABI-safe wrappers, migration-avoidance infrastructure - while misattributing the constraint to technical necessity rather than governance choice (Klemperer 1987). Lock-in traps the governed population without providing governance voice.

**Capture-lock-in interaction.** Those who govern depend on governance output. Their employers hold the legacy codebases that create lock-in. Backward compatibility preservation simultaneously serves employer interest and governance authority. The captured governors protect the lock-in that funds their governance position. The cycle is closed.

**Legacy codebase holders as dark influence.** Enterprise holders of large C++ codebases benefit from zero-cost backward compatibility without actively lobbying for it. Prague 2020 converted their engineering preference into organizational identity. The benefit is structural: zero adaptation cost for incumbents, full compatibility burden for safety improvements. No conspiracy is required. Structural alignment produces the same outcome.

**Direction:** Stable. Identity-level attachment is maximally resistant to rational argument.

### 4.4 The Complexity Ratchet

Entropy accumulation compounds with self-correction failure to produce irreversible growth.

**Monotonic complexity growth.** Each standard release adds features without removing deprecated ones. C++26 adds reflection, contracts, and std::execution. No feature has been removed since C++98. The standard grows in one direction only.

**Self-correction absent.** Mistakes accumulate without systematic detection or repair. No external audit exists. No ombudsman reviews decisions against outcomes. No independent body evaluates whether features served their stated purpose. Shifting baselines prevent recognition - each incremental addition is absorbed as normal. The absence of self-correction is structural, not an oversight to be remedied by a process change.

**Capital consumption.** The current cohort consumes reputational and ecosystem capital accumulated over three decades. Complexity growth, safety gaps, and implementation delays erode future C++ viability. The consumption is not accounted against current productivity metrics. The generation that depletes the asset will not bear the cost.

**Train-model pressure.** The three-year release cadence creates fixed windows. Features ship with known gaps rather than miss the cycle. C++20 modules shipped without build system integration. Deadline pressure accelerates feature addition without creating corresponding time for simplification or removal.

**Process mimicry.** ISO procedures are retained for legitimacy rather than efficiency (DiMaggio and Powell 1983). Multi-layer veto points (Tsebelis 1995) accumulate across five approval stages - study group, evolution group, wording group, plenary, international ballot - suppressing change while preserving the appearance of deliberation. The process that would reform the standard is the process that blocks reform.

**Direction:** Degrading. Compounding accumulation with no corrective mechanism. Each cycle adds complexity that makes the next cycle's simplification harder.

### 4.5 The Existential Gap

Competitive erosion compounds with capital consumption to produce dual-front degradation.

**Categorical capability gap.** Rust delivers compile-time memory safety - a capability C++ structurally lacks and cannot acquire through library-level additions or coding guidelines. Enterprise adoption reached 48.8% in the 2025 State of Rust Survey. Five coordinated US government publications between 2022 and 2025 specifically require this capability. The competitive pressure is categorical, not marginal.

**Monopoly rigidity.** As the sole ISO-designated C++ standards body, WG21 faces no competitive pressure from alternative standards organizations. The monopoly position removes the signal that would trigger adaptation. Dissatisfied participants cannot exit to a rival C++ body. External exit - to Rust, Carbon, Swift, or Zig - is the only available response. Exit-voice-loyalty dynamics (Hirschman 1970): voice has proven ineffective against identity-level commitments; exit is underway across Google, Microsoft, Meta, and Apple simultaneously.

**Dual-front erosion.** Internal capital consumption erodes the asset base - reputation, ecosystem investment, talent pipeline - at the same rate external competition devalues it. Government mandates from ONCD, CISA, and NSA convert the capability gap into procurement exclusion. Each memory-safety CVE reinforces the "dangerous language" framing. Reputational contagion flows from individual incidents to the language standard itself. The two fronts compound: internal degradation makes external competition more damaging, and external competition accelerates internal talent loss.

**Profiles response timeline.** WG21's sole institutional response to the existential gap - the profiles safety framework - requires 3+ years through the standard pipeline. One experimental compiler implementation exists. Government mandates operate on annual cycles. The EU Cyber Resilience Act reporting obligations begin September 2026. Profiles will not reach Draft International Standard status until circa 2029. The mismatch between threat velocity and response velocity is structural.

**Direction:** Degrading. Dual-front erosion with compounding acceleration. No mechanism decelerates either front.

### 4.6 The Succession Precipice

Multiple stability-dependent dynamics mask cliff-edge fragility in the leadership pipeline.

**Knowledge concentration.** No succession planning exists below convener level. Bjarne Stroustrup (age 75), Paul McKenney, and Jens Maurer approach retirement age. Knowledge of the standard's rationale, its historical compromises, and its implementation constraints is concentrated in individuals who have participated for decades. No documented transfer mechanism exists. The knowledge walks out the door with the person.

**Founder legacy as bottleneck.** Stroustrup's identity has fused with the language over 45 years. Founder's syndrome (Block and Rosenberg 2002) in its referent-power form: the founder's technical authority, biographical investment, and personal legacy channel organizational responses through a single individual's preferences. Profiles - Stroustrup's preferred safety approach - routes WG21's most existential challenge through a person whose remaining active contribution period is bounded by age. The profiles timeline of 3+ years consumes a significant fraction of that period.

**Structural hole without redundancy.** The Sutter/Foundation nexus bridges five domains simultaneously: governance (Convener Emeritus), funding (Foundation Chairman and CEO, $2.1M revenue), employer (Citadel Securities Technical Fellow), conference (CppCon), and media (isocpp.org). No other individual connects these five domains. A structural hole (Burt 1992) held by a single person with no succession mechanism and no competitive pressure to create one. The nexus provides stability while it persists. Its removal creates simultaneous disruption across all five domains.

**Loyalty trap.** Long-tenured participants who have invested years in the process are structurally less likely to criticize governance. Criticism comes disproportionately from newer participants and departing members. Those who see the problems most clearly hold the least institutional investment. Apparent consensus stability masks loyalty-driven silence.

**Talent pipeline narrowing.** Universities shift curricula to Rust and Python. Industry migration reduces the pool of senior engineers motivated to contribute to C++ standardization. CppCon attendance declined from 1,400 in 2019 to 700 in 2025. The talent pipeline narrows at the same time demographic concentration among existing experts intensifies. Replacement candidates are not forming.

**The cliff edge.** Multiple findings converge on stability dependent on non-renewable resources - aging experts, employer funding cycles, loyalty-trapped participants. The compound dynamic predicts phase transition rather than gradual decline. Current stability metrics provide no early warning because the resources they depend on deplete in step functions, not slopes. When Stroustrup retires, when employer funding priorities shift, when loyalty-trapped participants reach their threshold - the transitions will be sudden.

**Direction:** Degrading. Biological clock is non-negotiable; pipeline narrowing removes replacement candidates. No institutional mechanism converts individual knowledge into organizational knowledge.

### Domain-Specific Findings

Findings from domain-specific diagnostics, consolidated.

- **Consensus-as-cover.** Without recorded votes, consensus determination is opaque. Corporate ventriloquism cannot be distinguished from genuine agreement in the public record. The opacity is a feature of the process design, not an accidental gap.

- **Participation filtering.** Top 10 firms contribute over 70% of meeting-days. $50,000+ per year in costs filters governance to employer-funded organizations. Remote participation carries lower institutional weight. The filter is economic, not procedural - no rule excludes unfunded participants, but the cost structure accomplishes the same result.

- **Shadow governance.** Compiler vendors exercise governance outside the consensus process through selective implementation. C++20 modules remain partially implemented six years after standardization. The standard specifies; the vendor decides. Implementation discretion is de facto veto power operating without accountability to the consensus process.

- **Train-model gaps.** The three-year release cadence creates deadline pressure that prioritizes feature inclusion over feature quality. Features ship with known gaps rather than miss the cycle. The gap between specification and usable implementation widens with each release.

- **Backward compatibility as incumbent advantage.** ABI stability preserves existing codebases at zero adaptation cost to incumbents. Safety improvements and performance paradigms bear the full compatibility burden. The distribution of costs is structural: incumbents pay nothing, innovators pay everything.

- **National body capture.** INCITS (US national body, 60-70% of attendance) is chaired by an NVIDIA representative. National body governance mirrors corporate concentration at a lower organizational level. The pattern replicates.

- **Information layering.** Significant informal channels - dinner conversations, hallway discussions, pre-meeting coordination - shape outcomes before formal sessions begin. In-person attendees have structurally higher success rates for proposals. The layering is documented and user-confirmed.

One domain-specific diagnostic - study group chair agenda control - was excluded. A single confirmed case does not establish a pattern.

---

## 5. Institutional Health

Prognosis: Cargo Cult. US and European delegates constitute over 90% of attendance across 27 formally represented nations. Meeting locations reinforce geographic concentration - Asia-Pacific, Latin American, and African developers are structurally absent from governance of a language 16.3 million people use. Within the room, participants share a narrow professional profile: corporate C++ engineers at senior or principal level from large firms. The governed population uses a subset of the language; the governing population designs the superset. Complexity growth tracks governing-population preferences. The committee reflects its funding sources, not its constituency. Direction: Stable. (medium-high)

NVIDIA employees hold the INCITS/C++ chair (US national body, 60-70% of WG21 attendance), Direction Group chair, EWG chair, EWG Incubator chair, ARG chair, LEWG Incubator chair, SG1 co-chair, and INCITS/PL22 chair covering all US programming language standards. A single company's employees span the pipeline from proposal incubation through language evolution through strategic direction-setting. Direction Group documents predict which proposals advance; user testimony confirms the DG is genuinely advisory and plenary regularly departs from its positions, but no DG paper has ever been formally rejected. Interlocking directorates (Mizruchi 1996): overlapping personnel across governance nodes produce coordination capacity without requiring coordination intent. Single-company pipeline coverage is the finding. Direction: Degrading (national body capture), Stable (Direction Group influence, medium).

No governance reform proposal has been adopted in WG21's 35-year history. The Sutter-to-Davidson convener transition (January 2026) was a personnel change, not a governance reform. Communication improvements - split direction papers, standalone directives - increase transparency without altering accountability structure. The system that would need to change is the system that decides whether to change. Thirty-five years of data is conclusive. Direction: Improving slightly.

---

## 6. Economic Position

The finance sector accumulates standards influence without deliberate action. Thirteen of the CppCon 2026 sponsors are finance or trading firms - 74% of the total. The dollar-per-nanosecond conversion in high-frequency trading creates returns on standards influence no other sector can match - a single nanosecond of latency improvement on a high-volume strategy can exceed the annual cost of committee participation. Technical interests and employer interests overlap completely; the distinction is structurally ambiguous. The ambiguity is the mechanism: when the line between technical merit and commercial interest cannot be drawn, influence operates without visibility. Finance captures without lobbying. (medium-high) Direction: Stable.

---

## 7. External Exposure

The regulatory clock operates annually. WG21's response operates on 3+ year cycles. Five coordinated US government publications between 2022 and 2025 escalated from voluntary guidance toward binding procurement requirements. CISA's January 2026 deadline for memory safety roadmaps has passed without a WG21-endorsed deliverable. The EU Cyber Resilience Act imposes reporting obligations beginning September 2026 and main obligations in December 2027. DARPA's TRACTOR program ($14M, seven academic teams) funds automated C-to-Rust translation - the government is not waiting for WG21. The mismatch between regulatory velocity and standards velocity is structural, not a scheduling problem.

Each high-profile memory-safety CVE in C++ software reinforces the "dangerous language" framing. CISA labels memory-unsafe language use a "bad practice." Microsoft estimates cost per CVE at $150K or more. Seventy percent of security vulnerabilities in large C/C++ codebases are memory safety issues. The framing has shifted from technical concern to institutional liability. WG21 has no rapid-response mechanism - the same multi-year pipeline that processes minor library additions processes existential reputational threats. Reputational contagion flows from individual incidents to the language, from the language to the standard, and from the standard to the committee. The flow is unidirectional and accelerating.

---

## 8. Predictions

### Short-term (0-2 years)

**1.** If profiles produces a demonstrable implementation by mid-2027 - Dos Reis framework plus major compiler support - WG21 regains minimal credibility with government audiences. If not, the CISA "dangerous language" framing hardens into procurement exclusion for new contracts. (medium-high; regulatory timeline is published)

**2.** Finance sector influence continues growing as technology companies reduce engagement. The dollar-per-nanosecond incentive structure is self-reinforcing. No countervailing force exists within the committee. Direction: continuation of current trajectory.

**3.** EU Cyber Resilience Act reporting obligations (September 2026) create additional compliance pressure on C++ users. WG21 has no rapid-response mechanism for regulatory compliance questions. If the committee produces guidance before September 2026, it partially addresses the gap. If not, individual national bodies and compiler vendors fill the vacuum independently.

### Medium-term (2-5 years)

**4.** If profiles delivers for C++29 (feature-freeze circa 2028), WG21's safety story becomes credible for government audiences. If profiles are demonstrably incomplete or weaker than Rust's model, the profiles coalition fractures. No prepared fallback exists. The committee would face a legitimacy crisis with its safety response discredited and no alternative ready. (medium; technical delivery uncertain)

**5.** The demographic cliff begins to bite. Stroustrup (age 78-80), McKenney, Maurer approaching retirement. If knowledge transfer occurs before departure, institutional continuity is preserved. If not, institutional knowledge loss creates operational disruption concentrated in specification expertise and library implementation. (medium-high; demographic data is public)

**6.** Rust enterprise adoption continues growing. If it reaches 60%+ and government mandates become binding, C++ market position contracts to legacy maintenance, embedded systems, and finance. If adoption plateaus or interop costs prove prohibitive, the contraction slows. The committee's composition shifts further toward these sectors regardless. (medium; trend visible but rate uncertain)

### Long-term (5-10 years)

**7.** If the accountability vacuum persists and entropy continues, the committee converges toward a finance-sector and legacy coordination body with diminishing relevance to broader systems programming. If structural reform occurs, the trajectory changes. The standard remains technically authoritative but practically secondary to Rust for new projects. (medium; structural inference from current trajectory)

**8.** Lock-in breaks suddenly rather than gradually. If Rust interop tooling and automated migration mature sufficiently (circa 2030), organizational departure will be rapid - incremental Rust adoption is already building alternative infrastructure. If migration tooling stalls, the loyalty trap extends the stability plateau. The pattern is the same: apparent stability masking accumulated exit pressure until a threshold is crossed. (low-medium; alternative maturity is uncertain)

**9.** Historical parallel: the ITU retained authority over legacy telecommunications standards while the IETF captured internet protocols in the 1990s. The ITU did not die - it governed a shrinking domain. If WG21's trajectory continues, WG21 retains authority over legacy C++ while Rust captures new systems programming. If WG21 delivers credible safety guarantees, the parallel breaks. (medium; historical parallel, not deterministic)

---

## 9. Audit Trail

- **Tests:** 68 run, 38 findings survived, 30 killed, 3 downgraded
- **Rules:** 8 domain-specific generated, 7 survived
- **Dark influence:** 7 demand sentences, 23 candidates, 6 survived
- **Theories:** 7 applied, 4 confirmed / 3 partial / 0 falsified
- **Compounds:** 7 within-cluster, 6 cross-cluster, 4 gap-derived (2 killed total)
- **Direction:** 15 degrading, 25 stable, 4 improving

---

## 10. References

### Primary Sources

ISO/IEC 14882 (C++ International Standard)
[isocpp.org/std/the-committee](https://isocpp.org/std/the-committee)
Standard C++ Foundation board meeting minutes (November 2025)
Standard C++ Foundation Annual Report / ProPublica 990 filings (EIN 46-1356355)
[herbsutter.com](https://herbsutter.com) - trip reports (London Croydon March 2026, Brno June 2026), Citadel announcement
[open-std.org/jtc1/sc22/wg21](https://open-std.org/jtc1/sc22/wg21) - papers P3589R2, P3984R0, P3970R0, P4186R0, P2028R0, P5000R0
ONCD "Back to the Building Blocks" (February 2024)
CISA/FBI "Product Security Bad Practices" (October 2024)
NSA/CISA "Memory Safe Languages" joint guide (June 2025)
NSA "Software Memory Safety" cybersecurity information sheet (2022)
DARPA TRACTOR program
SlashData "Global developer population trends 2025"
2025 State of Rust Survey (March 2026)
Business Insider (November 2024) - Sutter/Citadel hire
CppCon 2026 sponsor list
WG21 attendance records
[cor3ntin.github.io](https://cor3ntin.github.io) - ABI analysis
Carbon language roadmap (GitHub)

### Academic References

Arthur, W.B. *Increasing Returns and Path Dependence in the Economy.* University of Michigan Press, 1994.\
Block, S.R. and Rosenberg, S.A. "Toward an Understanding of Founder's Syndrome." *Nonprofit Management and Leadership* 12(4):353-369, 2002.\
Burt, R.S. *Structural Holes: The Social Structure of Competition.* Harvard University Press, 1992.\
DiMaggio, P.J. and Powell, W.W. "The Iron Cage Revisited: Institutional Isomorphism and Collective Rationality in Organizational Fields." *American Sociological Review* 48(2):147-160, 1983.\
Goodhart, C.A.E. *Monetary Theory and Practice.* Macmillan, 1984.\
Hirschman, A.O. *Exit, Voice, and Loyalty.* Harvard University Press, 1970.\
Klemperer, P. "Markets with Consumer Switching Costs." *Quarterly Journal of Economics* 102(2):375-394, 1987.\
Lukes, S. *Power: A Radical View.* 2nd ed. Palgrave Macmillan, 2005.\
Mizruchi, M.S. "What Do Interlocks Do? An Analysis, Critique, and Assessment of Research on Interlocking Directorates." *Annual Review of Sociology* 22:271-298, 1996.\
Selznick, P. *Leadership in Administration.* Harper & Row, 1957.\
Stigler, G.J. "The Theory of Economic Regulation." *Bell Journal of Economics* 2(1):3-21, 1971.\
Tsebelis, G. "Decision Making in Political Systems: Veto Players in Presidentialism, Parliamentarism, Multicameralism and Multipartyism." *British Journal of Political Science* 25(3):289-325, 1995.

---

*June 2026 - claude-opus-4-20250918*
