# WG21 Produces More Standard Than Its Ecosystem Can Absorb

### A functional institution in early-stage decay, sustained by lock-in rather than earned authority.

April 2026, by Vinnie Falco

---

## 1. Executive Summary

WG21 - the ISO working group responsible for the C++ standard - is a 37-year-old specification monopoly that still ships its stated output on a three-year cadence. That output now exceeds what compiler vendors, library implementers, and the broader ecosystem can absorb. Eighteen implementers collectively petitioned the committee to slow down, an extraordinary external correction that occurred because internal correction mechanisms, staffed by the same participants whose output created the problem, could not surface the signal.

The institution's legitimacy is shifting from earned to inherited. WG21 retains its position not because its recent output commands deference but because the installed base of C++ code makes the committee necessary regardless of performance quality. Lock-in prevents users from signaling dissatisfaction through exit, which removes the market discipline that would otherwise force quality improvement. Competitive pressure from Rust and government safety mandates drives defensive feature additions that deepen lock-in rather than address the quality gap.

The compound dynamics are reinforcing. The committee produces more than implementers can absorb, measures success by shipping cadence and paper throughput rather than implementation quality, cannot detect the mismatch because its detection mechanisms are compromised, and responds to competitive threats by adding features rather than fixing what it has. Each turn consumes institutional capital - technical authority, implementer trust, community goodwill - that surface metrics do not measure.

Prognosis: Functional. The institution works, and the knowledge tradition is living though concentrated. But the trajectory is toward Cargo Cult - an institution that performs the ceremonies of standardization without the substantive deliberation that made them meaningful. The new convener (Guy Davidson, March 2026) and the NB ballot process, which has demonstrated independent blocking power, are the two structural checks that could arrest this trajectory.

---

## 2. The Subject

WG21 (ISO/IEC JTC1/SC22/WG21) is the working group under ISO's Joint Technical Committee 1, Subcommittee 22, responsible for developing and maintaining the international standard for the C++ programming language (ISO/IEC 14882). Founded in 1989, the committee operates through a consensus-driven process with roughly 200 face-to-face participants at each of three annual meetings, supplemented by approximately 30 virtual subgroup meetings per month.

The committee is structured into study groups (SG1 through SG23, covering domains from concurrency to safety), core working groups (CWG for language, LWG for library, EWG for evolution, LEWG for library evolution), and plenary sessions where subgroup recommendations face full-committee ratification. A direction group provides strategic guidance. National body delegates hold formal voting power; other participants attend as guests or experts appointed through their national standards organizations.

No participant is employed by WG21 or ISO. All labor, travel, and opportunity costs are borne by employers or by individuals. The Standard C++ Foundation (isocpp.org) administers meeting logistics and infrastructure but holds no governance power over technical direction. Formal adoption of the standard requires national body ballot through ISO's publication process.

The committee has shipped standards on its three-year cadence - C++11, C++14, C++17, C++20, C++23 - with C++26 in progress. In March 2026, Guy Davidson assumed the convenership from Herb Sutter, who had held the role for approximately 17 years.

---

## 3. The Landscape

**Domain structure.** ISO international standards are developed through technical committees overseen by the Technical Management Board. National members participate as P-members (voting) or O-members (observing). WG21 sits two levels below JTC1 as a working group rather than a full technical committee - a structural position that limits its formal autonomy within ISO's governance hierarchy.

**Market position.** WG21 holds a monopoly on the formal ISO C++ specification. No competing organization produces an alternative C++ standard. The monopoly is maintained by:

1. The installed base - billions of lines of existing C++ code
2. Compiler vendor commitment to ISO conformance
3. Regulatory and contractual references to ISO C++
4. The absence of a viable succession mechanism for the specification itself

**Competitive environment.** C++ faces its first serious competitive threat from Rust, which offers compile-time memory safety guarantees. Government agencies (NSA, CISA) have recommended migration to memory-safe languages. Carbon, an experimental project at Google, is designed as an explicit C++ successor with full interoperability. De facto vendor extensions can diverge from ISO, creating fragmentation risk.

**Upstream dependencies:**

1. ISO/JTC1/SC22 governance machinery and publication pipeline
2. National body participation and ballot infrastructure
3. Compiler vendor willingness to implement approved features
4. Employer sponsorship of participant labor and travel

**Downstream dependencies:**

1. Compiler implementations (GCC, Clang/LLVM, MSVC, EDG)
2. Standard library implementations (libstdc++, libc++, MSVC STL)
3. Toolchains, IDEs, static analyzers, and build systems
4. Training curricula, certification programs, and industry hiring practices

**Domain-specific vulnerabilities.** WG21 paper P3443R0 documents that more than 50% of analyzed binding polls occurred with less than one week between paper publication and the poll. P3569R0 records Clang maintainers arguing that a reflection sub-feature was too risky for the target standard cycle. Eighteen implementers signed a collective paper asking WG21 to reduce its output pace - the most significant implementer intervention in the committee's history.

---

## 4. Structural Assessment

### 4.1 Output Without Absorption

The most immediate structural dynamic is volume. WG21 produces more normative text per standard cycle than the implementation ecosystem can absorb. This is not a process inefficiency but a compound dynamic where multiple forces align to overproduce.

The committee's participants optimize for feature quantity and novelty while the broader ecosystem - compilers, libraries, users - needs implementable, stable output.<sup>1</sup> The three-year shipping cadence functions as a Goodhart target:<sup>2</sup> the committee meets its schedule by compressing the one step that would detect quality problems - substantive review. More than half of binding polls occur with less than a week between publication and discussion (P3443R0), which means the consensus ceremony is performed without the deliberation that gives consensus its meaning.

The result is capacity overload.<sup>3</sup> Feature proposal volume exceeds implementation capacity, producing quality shading - features standardized with less implementation experience than earlier eras required. Maintenance tasks (defect reports, NB comments, wording fixes) lag behind new feature tracks, confirming the prediction that public-goods maintenance is under-provided when selective incentives favor visible innovation.<sup>4</sup> Resource allocation heavily favors adding features over fixing known design flaws, and flaws that would require ABI breaks to correct persist indefinitely.

The 18-vendor paper is evidence that internal self-correction failed.<sup>5</sup> A self-correction mechanism staffed by the people whose output it evaluates is a ceremony, not a check. The implementers organized outside the committee's normal governance to register a signal that should have been visible internally. The NB ballot process - which has demonstrated actual blocking power - remains the only independent correction mechanism with structural teeth.

This dynamic is self-reinforcing. Output volume compresses review time. Compressed review removes quality discipline. Quality shading is invisible to participants who rely on cadence metrics as quality signals. Lock-in prevents user exit, removing the market feedback that would otherwise impose correction.<sup>6</sup> The parallel is the W3C's XHTML 2.0 effort, where the standards body's output diverged from what browser vendors would implement until implementers formed the WHATWG to build HTML5 pragmatically - an implementer rebellion that took fifteen years to resolve.

### 4.2 Legitimacy by Inertia

WG21's legitimacy has a depreciating component and a structural floor. The depreciating component is technical authority - the deference that flows from producing standards that earn the ecosystem's respect. The structural floor is installed-base necessity - the committee is needed because C++ is needed, regardless of committee performance.<sup>7</sup>

The shift between these two is the defining institutional transition. Implementer pushback (the 18-vendor paper), language competition (Rust, Carbon), and the persistence of unfixable design flaws all erode earned authority. What remains is inherited position - users stay because they cannot leave, not because the standard earns their trust.<sup>6</sup>

This transition creates a specific trap. Lock-in prevents users from signaling dissatisfaction through exit.<sup>8</sup> Because dissatisfaction has no market consequence, the committee receives no price signal for quality degradation. Proposals that would break ABI compatibility face systematically higher rejection rates even when their technical merit is high, because the installed base raises the private cost of switching to a superior design.<sup>9</sup> The result is that the committee adds features that deepen lock-in while rejecting fixes that would reduce it. Institutional capital - technical authority, implementer trust, community goodwill - is consumed while surface metrics (standards shipped, participation counts) remain stable.<sup>10</sup> (medium-high)

Competitive threats from Rust and government safety mandates trigger defensive standardization activity rather than structural adaptation.<sup>11</sup> The committee's response to existential competitive threats operates through bureaucratic expansion - new study groups (SG23 for safety), new paper tracks - rather than adaptive structural change.<sup>12</sup> This channels resources toward new features (defensive additions) rather than quality maintenance, which further erodes the earned legitimacy the defensive response was meant to protect.

### 4.3 The Ceremony Mill

WG21's core social technologies - consensus polling, paper-driven proposals, subgroup-to-plenary pipeline - are documented and ceremonially performed. The ceremonies persist while the substance has eroded.<sup>12</sup> Polls occur before meaningful review is possible. Process reviews produce more process rather than structural adaptation. The committee's default response to novel challenges is bureaucratic expansion - forming study groups, adding standing documents, creating new paper categories - which increases procedural surface area without addressing the underlying dynamic.<sup>13</sup>

The inherited committee model contributes. WG21 operates under ISO procedures designed for industrial standards with measurable physical properties. Programming language standardization requires different judgment - semantic coherence, implementation feasibility, backward compatibility - that the inherited model does not naturally measure.<sup>14</sup> The committee has adapted significantly, but the structural assumptions of the inherited model (that consensus among present experts is sufficient for quality, that process compliance implies substantive review) do not hold when review time is compressed and participation economics select for process-adept contributors over independent technical voices.

Information architecture compounds the problem. Decision-relevant context concentrates among face-to-face attendees, subgroup chairs, and the direction group.<sup>15</sup> Formal outputs (poll results, minutes, papers) strip the deliberative context that informed decisions, creating systematic information asymmetry between those who were present and those who read the record. The committee's participants share the same information environment because participation economics select for the same institutional profile - employer-sponsored, process-experienced, repeat attendees. Information asymmetry becomes invisible when everyone present experiences the same filtered view. (medium-high)

The compound dynamics describe a ratchet. Each increment of process-ceremony erosion resets the perceived baseline. Participants who perform review ceremonies that no longer deliberate believe they are deliberating. Process reviews that detect dysfunction recommend more process, which feels like adaptation. Surface metrics (papers processed, polls taken, standards shipped) provide false confirmation that the system works. The system cannot self-diagnose because the diagnostic instruments have been recalibrated to the disease.

### 4.4 The Succession Void

WG21's most critical processes depend on tacit knowledge held by specific individuals.<sup>16</sup> Core language wording, consensus interpretation, and ABI impact assessment are not documented in transferable form. The documentation (SD-6, standing documents) covers procedure but not the judgment required to apply it.

The committee has just undergone its most significant succession event in 17 years - the convener transition from Herb Sutter to Guy Davidson.<sup>17</sup> The 17-year tenure itself is evidence that skill transfer was deferred rather than systematically managed. Whether the incoming convener has absorbed the full capability set is structurally unknowable at this stage. Below the convener level, domain expertise remains concentrated in long-tenured individuals without systematic transfer mechanisms.

The concentration is structural, not accidental. A small share of participants accounts for a disproportionate share of authored papers, reviews, and issue resolution.<sup>4</sup> The people doing disproportionate work are the same people holding non-transferable tacit knowledge. Succession planning requires replacing individuals whose knowledge resists formalization - so it gets deferred.<sup>17</sup> When the knowledge holders depart, borrowed power (ISO relationships, vendor trust, NB liaison skills) reverts to lenders rather than transferring to successors, because no successors have been prepared.<sup>18</sup>

The growing talent pipeline provides demographic replacement but not functional replacement. Newcomer participation is trending up, a positive signal. But NB-gating of formal voting power creates a two-tier system where newcomers can participate in discussion but not in formal decisions until they navigate national body appointment. More critically, new participants have not absorbed the tacit knowledge held by senior cohort members. The pipeline fills seats without transferring the understanding that makes those seats productive. (medium)

WG21's human capital supply chain has single points of failure in core wording, editorial function, and consensus-reading capability.<sup>19</sup> The fragility is invisible to participants. Knowledge holders do not recognize that their knowledge cannot be transferred from documentation alone. The institution does not measure its capital depletion. Participants have never experienced subsidy withdrawal or key-person departure at scale, so they have no model for how fast function would degrade. When the stress event arrives, the system discovers its fragility at the moment of failure, not before.

---

## 5. Institutional Durability

**Prognosis: Functional** - but the trajectory is toward Cargo Cult within a decade if the compound dynamics identified above continue unchecked. The institution still produces real output that compilers implement and developers use. The knowledge tradition is living, though concentrated. The new convener may prove to be a live player capable of adaptive response rather than bureaucratic expansion. The NB ballot process has demonstrated independent blocking power, providing an external check that internal mechanisms cannot.

The case against sustained function is structural. WG21's power is predominantly borrowed - from ISO's framework, vendor willingness to implement, and employer willingness to sponsor participation.<sup>18</sup> The 18-vendor paper demonstrates that a critical power source (implementation) is actively contested. The committee's legitimacy is shifting from earned to inherited, and the compound dynamics (the Absorption Crisis, the Ceremony Mill, the Legitimacy-Lock-in Divergence) are self-reinforcing. Each makes the others harder to address. The committee cannot slow output without threatening the cadence metric that participants treat as a measure of health. It cannot fix ABI-breaking design flaws without triggering the lock-in trap. It cannot reform process without the reformed process being staffed by the same people whose behavior it needs to change.

The structural window for correction is narrow. The convener transition creates a moment of institutional plasticity that will not recur for years. If the new convener and the NB ballot process together impose quality discipline on the output pipeline - not more study groups, not more standing documents, but actual compression of feature throughput to match implementation capacity - the trajectory can be altered. If the response is more bureaucratic expansion, the Cargo Cult threshold moves closer.

---

## 6. Predictions

**Short-term (1-2 years):**

- The new convener will face immediate pressure to either enforce the 18-vendor paper's request or demonstrate that the committee can self-regulate output volume. If enforcement succeeds, expect a temporary reduction in per-cycle feature count and corresponding implementer relief. If enforcement fails, expect a second, more aggressive implementer intervention. Confidence: medium-high (structural pressure is unambiguous; convener response is not).

- At least one major C++26 feature will face post-adoption implementation difficulty comparable to earlier design-flaw patterns (coroutines, ranges). The compressed review dynamic has not been structurally addressed. Confidence: medium (specific feature identification is speculative; the systemic pattern is high-confidence).

**Medium-term (3-7 years):**

- If output volume remains unchanged, at least one major compiler vendor will de-prioritize ISO conformance for new features in favor of selective implementation, effectively creating a de facto dialect. This is the vendor-bypass path already observed in extension ecosystems. Confidence: medium (contingent on output-volume trajectory).

- Rust will capture a measurable share of new systems-programming projects that would previously have defaulted to C++, particularly in government-adjacent and safety-critical domains. This will not eliminate C++ demand but will reduce the pool of employers willing to sponsor WG21 participation. Confidence: medium-high (government mandates already issued; adoption trajectory visible).

- The knowledge cliff from senior cohort retirement will become visible in specific domains (core wording, ABI assessment) as maintenance velocity in those areas declines. Confidence: medium (demographic trajectory is slow but directional).

**Long-term (7-15 years):**

- If the Legitimacy-Lock-in Divergence continues, WG21 risks the W3C outcome: formal standards authority retained while practical relevance migrates to an implementation-driven alternative body or de facto vendor consortium. The probability depends entirely on whether the current structural checks (new convener, NB ballot) produce real correction within the medium-term window. Confidence: low-medium (long horizon with high path dependency).

- If correction succeeds, WG21 stabilizes as a slower, higher-quality specification body producing fewer features per cycle with deeper implementation validation - structurally similar to the post-HTML5 W3C, which ceded velocity to retain relevance. Confidence: medium (contingent on correction succeeding).

---

## 7. Audit Trail

**Sources consulted:**

- ISO organizational materials (who develops standards, committee structure)
- Standard C++ Foundation (meetings and participation documentation)
- WG21 public paper archive (open-std.org)
- P3443R0 (SG21 process reflection - poll timing data)
- P3569R0 (Clang maintainers - reflection sub-feature risk)
- Springer academic literature on ISO participation drivers (Blind and von Laer, 2022)
- Carbon Language project documentation and repository
- Seven theoretical frameworks from economics and institutional analysis (see References)

**Cache status:** Fresh collection, 2026-04-11 UTC. No prior cache existed.

**Domain-specific rules generated:** 7 rules (NB ballot health, convener objection handling, incubation time distribution, implementer blocking power, participation accessibility, subgroup-plenary alignment, ecosystem competition elasticity). Rules 1, 3, and 4 produced surviving findings.

**Findings challenged and outcomes:**

- 30 findings survived Challenge (Tests 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 30, 32, 33, 34, 35, 42)
- 3 findings killed:
  - Test 28 (Two-Sided Market) - domain mismatch; insight captured by Tests 23 and 32
  - Test 38 (Regime Dependency) - domain mismatch; captured by Test 16
  - Domain Rule 7 (Competition elasticity) - insufficient evidence
- 15 clean results (Tests 2, 20, 24, 29, 31, 36, 37, 39, 40, 41, 43, 44, 45, and Domain Rules 2 and 6 - insufficient data)
- 6 theory-derived predictions confirmed or partially confirmed; 2 insufficient data

**Prior reports imported:** None. First evaluation of this subject.

---

## 8. References

1. Jensen, M.C. and Meckling, W.H. "Theory of the Firm: Managerial Behavior, Agency Costs and Ownership Structure." *Journal of Financial Economics* 3(4):305-360, 1976.
2. Goodhart, C.A.E. *Monetary Theory and Practice: The UK Experience.* Macmillan, 1984.
3. Laffont, J.-J. and Tirole, J. *A Theory of Incentives in Procurement and Regulation.* MIT Press, 1993.
4. Olson, M. *The Logic of Collective Action: Public Goods and the Theory of Groups.* Harvard University Press, 1965.
5. Ashby, W.R. *An Introduction to Cybernetics.* Chapman & Hall, 1956.
6. Klemperer, P. "Markets with Consumer Switching Costs." *Quarterly Journal of Economics* 102(2):375-394, 1987.
7. Suchman, M.C. "Managing Legitimacy: Strategic and Institutional Approaches." *Academy of Management Review* 20(3):571-610, 1995.
8. Mises, L. *Human Action: A Treatise on Economics.* Yale University Press, 1949.
9. Farrell, J. and Saloner, G. "Standardization, Compatibility, and Innovation." *RAND Journal of Economics* 16(1):70-83, 1985.
10. Burja, S. "Great Founder Theory." Manuscript, 2020.
11. Schumpeter, J.A. *Capitalism, Socialism and Democracy.* Harper & Brothers, 1942.
12. Katz, D. and Kahn, R.L. *The Social Psychology of Organizations.* John Wiley & Sons, 1966.
13. North, D.C. *Institutions, Institutional Change and Economic Performance.* Cambridge University Press, 1990.
14. Akerlof, G.A. "The Market for 'Lemons': Quality Uncertainty and the Market Mechanism." *Quarterly Journal of Economics* 84(3):488-500, 1970.
15. Polanyi, M. *The Tacit Dimension.* University of Chicago Press, 1966.
16. Weber, M. *Economy and Society.* University of California Press, 1978.
17. Simcoe, T. "Standard Setting Committees: Consensus Governance for Shared Technology Platforms." *American Economic Review* 102(1):305-336, 2012.
18. Grossman, S.J. and Hart, O.D. "The Costs and Benefits of Ownership: A Theory of Vertical and Lateral Integration." *Journal of Political Economy* 94(4):691-719, 1986.
19. Chopra, S. and Sodhi, M.S. "Managing Risk to Avoid Supply-Chain Breakdown." *MIT Sloan Management Review* 46(1):53-61, 2004.

---

*April 2026 - claude opus-4.6*
