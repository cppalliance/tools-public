# Certifying the Unmeasurable

### An industry that sells safety assurance it cannot verify, sustained by mandates it cannot survive without

April 2026, by Vinnie Falco

---

## 1. Executive Summary

Software safety certification is a credence-goods market. The buyer cannot evaluate the quality of a safety assessment before, during, or after receiving it - and neither can the regulator who mandated it. This single structural property - unobservability of the connection between certification and safety outcomes - produces every major dysfunction in the ecosystem: ceremonial compliance, adverse selection among certification bodies, regulatory capture of standards committees, a three-link principal-agent chain where every link is misaligned, and self-correction mechanisms funded by the entities they oversee. The industry functions not because it demonstrably produces safety, but because regulatory mandates create captive demand that masks the epistemic gap.

The dominant compound dynamic is the Credence Good Trap: safety as a credence attribute prevents market-based quality correction, which drives competitive selection toward speed and cost rather than assessment rigor, which degrades the information architecture that could provide outcome feedback, which ensures the market never acquires the signal that would enable correction. The trap is self-reinforcing and structurally stable.

The trajectory is not collapse but calcification. Captive demand insulates the industry from market correction. An aging assessor cohort approaches a competence cliff that the industry cannot see because captive demand masks capital consumption. AI/ML systems are arriving into a framework designed for deterministic software, widening the gap between certification capability and technology reality on revision cycles measured in decades. The structural parallel is the financial auditing industry before Arthur Andersen - stable until a single catastrophic failure forces external restructuring.

Prognosis: Cargo Cult. The industry faithfully reproduces the forms of functional safety assurance - safety integrity levels, V-model lifecycles, safety cases - without the epistemic substance: a validated connection between certification and safety outcomes. The forms are inherited from industrial safety contexts where they were more functional, and each generation of imitation has widened the gap between ceremony and engineering judgment.

---

## 2. The Subject

The software safety certification industry is a private-sector ecosystem of three tiers:

1. **Standards bodies and consortia** that produce normative text: IEC (IEC 61508<sup>1</sup>), ISO (ISO 26262<sup>2</sup>), RTCA/EUROCAE (DO-178C<sup>3</sup>), and industry groups like MISRA<sup>7</sup>, a not-for-profit consortium that publishes C and C++ coding guidelines for safety-critical systems.

2. **Certification bodies (CBs)** that sell conformity assessments: TUV SUD, TUV Rheinland, TUV Nord, Bureau Veritas, SGS, UL, Intertek, DNV, and numerous smaller specialists. These organizations are accredited under ISO/IEC 17065<sup>5</sup> to certify products, processes, and services against the normative standards.

3. **Accreditation bodies** that oversee CBs: national bodies (ANAB, A2LA, DAkkS, UKAS) that assess CB competence against ISO/IEC 17065 and ISO/IEC 17025.

Regulators - FAA, EASA, NHTSA, EU type-approval authorities - are external forces that mandate participation in this ecosystem but do not produce the assessments or standards themselves. The FAA recognizes DO-178C as an acceptable means of compliance<sup>8</sup> but retains final approval authority. The EU Machinery Regulation and automotive type-approval frameworks delegate assessment to notified bodies operating under CB accreditation.

The ecosystem is approximately three decades old in its modern form. IEC 61508 Edition 1 published in 1998. MISRA C first published in 1998. ISO 26262 Edition 1 in 2011. The industry spans automotive, aerospace, medical devices, industrial automation, and rail - any domain where software controls systems whose failure could cause harm.

---

## 3. The Landscape

Five structural facts define this domain:

1. **Standards are upstream constraints; conformity is downstream commerce.** Regulators and OEMs demand evidence against published standards. That demand is satisfied by supplier documentation plus third-party audits, assessments, and certificates sold by CBs. The split between rule-making and rule-assessment is the industry's fundamental structure.

2. **IEC 61508 is the generic functional safety baseline** from which sector standards derive<sup>1</sup>. It defines safety lifecycle concepts and safety integrity levels (SILs) for programmable electronic safety-related systems. ISO 26262<sup>2</sup> adapts this for automotive. IEC 62304<sup>4</sup> adapts it for medical device software. DO-178C<sup>3</sup> follows a parallel lineage in aerospace.

3. **The trust chain has four links:** regulators define what counts as evidence; CBs supply attestations; accreditation bodies assess CB competence; manufacturers pay for everything. Each link is a delegation with its own incentive structure.

4. **The market is an oligopoly with regulatory gatekeeping.** Several multinational CBs (TUV SUD, Bureau Veritas, SGS, UL, Intertek) recur across functional safety sectors. Below them, many smaller specialists and consultancies compete for sub-tier work. Entry requires accreditation - a barrier maintained by ISO/IEC 17065<sup>5</sup> requirements.

5. **MISRA occupies a distinctive position.** As a not-for-profit consortium<sup>7</sup>, MISRA publishes coding guidelines widely adopted as procurement criteria and hiring filters. MISRA is not a certification body and does not issue compliance certificates. Its guidelines function as de facto procurement standards, often specified contractually without formal certification against them.

**Upstream dependencies:** international standards organizations, national regulators, accreditation bodies, OEM procurement rules, liability law, qualified assessor pipelines, qualified tool chains.

**Downstream dependents:** automotive programs (ISO 26262 evidence), medical device manufacturers (IEC 62304 within QMS), avionics suppliers (DO-178C objectives), industrial safety programs, training and consulting firms, static analysis and lifecycle tool vendors.

**Domain-specific vulnerability:** The industry's public record includes one catastrophic attestation failure in an adjacent domain. In 2019, Brazilian federal police accused Vale SA and TUV SUD employees of fraud-related allegations tied to the Brumadinho tailings dam collapse, including allegedly falsified stability attestations<sup>6</sup>. This was geotechnical infrastructure attestation, not software - but it is on the public record regarding commercial third-party inspection behavior under fee-paying client relationships.

---

## 4. Structural Assessment

### 4.1 The Credence Architecture

Safety assessment is a credence good (Darby and Karni 1973). The buyer cannot evaluate its quality before purchase, at the time of purchase, or after purchase. A manufacturer who receives an ISO 26262 certificate cannot determine whether the assessment that produced it was rigorous or perfunctory - the certificate looks the same either way. The end user who relies on a certified product cannot evaluate the certification's depth. The regulator who mandated certification cannot observe assessment quality at scale.

This unobservability is the root structural condition. In search goods, buyers verify before purchase. In experience goods, buyers verify after use. In credence goods, buyers never verify. The result is that competitive dynamics operate on observable dimensions - price, speed, relationship quality, brand prestige - rather than on the unobservable dimension that the industry exists to provide: connection between certification and safety outcomes.

The information architecture compounds this. Decision-relevant information concentrates at the supplier level, degrades at each delegation link, and reaches the risk-bearer (the public) as a binary signal: certified or not certified. Safety integrity levels, which were designed to indicate reliability targets, have become optimization targets in their own right (Goodhart 1984). Achieving SIL 2 certification is the goal; whether the certified system achieves SIL 2 reliability is a question the industry does not structurally answer.

No entity in the ecosystem independently measures whether certification correlates with safety outcomes. The self-correction mechanisms that exist - accreditation audits, peer assessments - are financially dependent on the entities they oversee. Accreditation bodies are paid by CBs. This is not a corruption allegation; it is the standard governance model of conformity assessment under ISO/IEC 17065<sup>5</sup>. The three-link principal-agent chain running from regulator through accreditation body to CB to assessor is misaligned at every link (Jensen and Meckling 1976), and the party that bears the safety risk - the public - is the most distant from the assessment decision.

### 4.2 Borrowed Power, Borrowed Legitimacy

The industry's power is overwhelmingly borrowed from regulatory mandates (Grossman and Hart 1986). If regulators ceased requiring third-party certification, voluntary demand for CB services would contract substantially. The industry's owned power - technical expertise, proprietary assessment methods, institutional knowledge - is real but secondary to the compulsory market that regulatory mandates create.

Borrowed power produces borrowed legitimacy (Suchman 1995). The industry's claim to authority rests not on demonstrated efficacy but on regulatory endorsement and historical brand. TUV's legitimacy derives from over a century of German inspection tradition, not from a published study demonstrating that TUV-certified software fails less often than uncertified software. No such study exists.

This power structure prevents the accumulation of earned legitimacy. Resources flow toward process compliance assessment - the activity mandated by regulation - rather than toward safety outcome measurement, which no mandate requires and no revenue stream rewards. Prestige within the industry flows to standards committee participation (Bourdieu 1984), the venue where borrowed power is maintained, rather than to assessment quality, the activity that would build owned power.

The regulatory capture pattern is classical (Stigler 1971). Standards committees - the bodies that write the rules defining what must be certified and how - are populated by CB employees, tool vendor representatives, and OEM compliance officers. These are the regulated parties writing their own rules. The captured rulemaking produces standards that reward process compliance (which CBs can assess) rather than outcome measurement (which would expose the credence-good gap). Changes in harmonized standards track organized industry participation more reliably than they track safety incident data.

### 4.3 The Ceremony Engine

The software safety standards descend from industrial safety contexts where their generating principles were more functional (Burja 2020). IEC 61508<sup>1</sup> drew on nuclear and chemical process safety experience. Safety integrity levels were designed for hardware-dominated systems where failure modes are physically characterizable and reliability is statistically demonstrable. ISO 26262<sup>2</sup> adapted IEC 61508 for automotive. Each generation of adaptation copied the forms - SILs became ASILs, V-models were preserved, safety cases were templated - without re-deriving their engineering rationale for the new context.

The current framework is at least two imitation generations from its industrial safety origins (Burja 2020). The result is that practitioners perform safety lifecycle activities from templates: safety cases follow boilerplate structures, hazard analyses use standardized categories, tool qualification follows checklist procedures. Consultants and CBs circulate these templates. Hiring flows spread the normative scripts. Safety-case documents converge across firms faster than underlying architecture diversity shrinks (DiMaggio and Powell 1983) - homogeneous paperwork wrapped around heterogeneous implementations.

The ceremonies are not empty - they contain real technical content. But the connection between the ceremony and the safety outcome it was originally designed to ensure has attenuated with each generation of imitation. Practitioners who have only known the templated version believe the templates ARE the work. The institution reproduces its ceremonies at growing imitation distance from the engineering judgment that generated them, on revision cycles - IEC 61508 Edition 2 was 2010, DO-178C was 2012 - that cannot close the gap with technology advancing on yearly cycles. (medium-high)

### 4.4 The Invisible Competence Cliff

The industry faces a sustainability crisis it cannot see. Functional safety assessment depends on tacit judgment - scoping decisions, evidence evaluation, challenge of supplier claims - that does not transfer through documentation (Polanyi 1966). The industry's qualified assessor pipeline is broken: assessment careers compete poorly with engineering roles at OEMs and Tier 1 suppliers on compensation, working conditions, and career trajectory (Becker 1964). The consequence is a broken talent pipeline (Lave and Wenger 1991) that produces no new cohort to replace the aging senior assessors who carry the industry's tacit knowledge.

The senior assessor cohort entered the field in the 1990s and 2000s with IEC 61508 Edition 1. They are aging out. The tacit knowledge they carry - how to challenge a supplier's safety case, when evidence is "sufficient," how to scope an assessment that catches real problems - requires apprenticeship-style transfer, which requires a functioning pipeline. The pipeline is broken. The knowledge transfer mechanism depends on the very thing that has failed. The vicious cycle closes: tacit knowledge cannot transfer without apprentices; the pipeline produces no apprentices; the knowledge exits with the cohort. (medium-high)

The cliff is invisible because captive demand masks it. Certification counts remain stable. Revenue remains stable. Assessment timelines lengthen but are attributed to market conditions. Assessor quality shades downward but is attributed to normal variation. Demand exceeds supply - every assessment gets less time, every assessor carries more cases - and quality degrades in a dimension the market cannot measure because safety is a credence good. The industry will appear stable until the senior cohort retires, at which point the decline is a cliff, not a slope (Rao and Argote 2006). (medium-high)

### 4.5 The Race to Adequacy

The competitive dynamics of the certification market select against assessment rigor. CBs compete on speed, cost, and client relationship - not on stringency. No CB advertises being the hardest to pass (Schumpeter 1942). The two-sided market structure is asymmetrically weighted toward the fee-paying supplier (Rochet and Tirole 2003): the supplier pays for the assessment, the regulator mandates it, and the end user trusts the badge. The paying customer's demand is for a certificate, not for a thorough assessment.

This market dynamic creates adverse selection (Akerlof 1970). The most commercially flexible CBs gain market share. The most rigorous CBs lose clients. Long-tenure CB-client relationships produce fewer major nonconformities not because clients improve but because the CB's economic incentive shifts from detection to retention (DeAngelo 1981). The industry's quality floor descends toward the minimum threshold that maintains regulatory acceptability. (medium-high)

Into this capacity-constrained market, AI and machine learning systems are arriving. The existing certification framework was designed for deterministic software following V-model development. Neural networks, reinforcement learning, and continuous learning systems do not fit: they lack the requirement traceability, code-level analysis, and deterministic verification that the framework requires. The industry has no mature epistemic model for assessing non-deterministic software. SOTIF (ISO 21448) addresses some scenarios but does not resolve the fundamental framework mismatch. The technology gap widens from the outside while market dynamics compress rigor from the inside. (medium-high)

### 4.6 The Moat as Fragility

The regulatory mandate is simultaneously the industry's protective moat, its revenue source, its legitimacy basis, and its single point of failure. Mandatory certification creates captive demand that sustains the industry regardless of whether its output produces safety. The mandate prevents market exit by dissatisfied buyers - they must be certified regardless. It funds the captured self-correction mechanisms. It creates the prestige that flows to standards committee participation rather than assessment quality.

The mandate also prevents the adaptation that would make the industry survivable without it. Because demand is compulsory, the industry faces no market pressure to demonstrate efficacy. Because efficacy is undemonstrated, the industry accumulates no owned power. Because power is entirely borrowed, the industry cannot survive mandate withdrawal.

The fragility surfaces through reputational contagion (Jonsson, Greve, and Fujiwara-Greve 2009). A single catastrophic failure attributable to certification failure - a certified automotive system causing deaths in a pattern that investigation traces to assessment inadequacy - would trigger regulatory response in the European jurisdiction where both normative authority and assessor talent concentrate. That response could restructure the mandatory certification framework. The industry's protective moat is the mechanism of its potential destruction: the mandate that prevents adaptation also concentrates the dependency that a contagion event could shatter. (medium)

The structural parallel is Arthur Andersen. The financial auditing industry operated in an identical credence-goods environment with identical structural dynamics - fee-paying clients, borrowed regulatory power, captured standard-setting, competition on relationship rather than stringency - until the Enron collapse destroyed one of the Big Five in months and forced Sarbanes-Oxley restructuring on the rest. The software safety certification industry awaits its Enron.

---

## 5. Institutional Durability

**Prognosis: Cargo Cult.** The software safety certification industry imitates the forms of functional safety assurance - safety integrity levels, V-model lifecycles, safety cases, tool qualification procedures - without the epistemic substance: a validated connection between the certification it produces and the safety outcomes it claims to ensure. The forms descend from industrial safety contexts (nuclear, chemical process) where the engineering basis was stronger. Each generation of adaptation has copied external structures while the generating principles - characterizable failure modes, demonstrable reliability, physical correspondence between models and systems - have become less applicable to software-dominated systems.

The prognosis is not Terminal because the institution produces real output (compliance artifacts that enable market access) and serves a real niche (regulatory compliance would otherwise be self-assessed). The prognosis is not Functional because the institution has never established the empirical basis for its core claim. It is Cargo Cult because the ceremonies are faithfully reproduced, the connection to outcomes is assumed rather than demonstrated, and the practitioners who perform the ceremonies believe - from inside the institutional epistemic environment - that the ceremonies are the substance.

---

## 6. Predictions

**Short-term (1-3 years):**

- Assessor capacity constraints will force quality shading that participants attribute to market growth rather than structural degradation. Confidence: high - demand trajectory is observable.
- AI/ML certification will be addressed through additive guidance documents (technical reports, supplements) rather than framework revision, because revision cycles are too slow and captured committees prefer additive rulemaking. Confidence: medium-high - tracks observed industry behavior with SOTIF and ISO/PAS 8800.
- If a major safety incident is traced to a certified system in European automotive, regulatory response will increase documentation requirements rather than restructure the certification model, because regulators are also inside the credence-good trap and have no independent outcome channel. Confidence: medium - depends on incident severity and political context.

**Medium-term (3-7 years):**

- The senior assessor cohort's retirement will produce visible competence gaps that the industry will attribute to talent market conditions rather than structural pipeline failure. Confidence: medium-high - demographic trajectory is observable; attribution pattern is predicted by Goodhart coupling.
- At least one major OEM will build sufficient internal V&V capability to argue for regulatory acceptance of self-assessment (with independent oversight), beginning the erosion of the third-party CB model. Confidence: medium - depends on OEM investment decisions and regulatory appetite.
- MISRA guidelines will face competition from language-integrated safety features (Rust's type system, formal verification tools) that provide safety properties the guidelines cannot, creating pressure to demonstrate the marginal safety contribution of guideline compliance. Confidence: medium - depends on adoption trajectory of alternative languages in safety-critical domains.

**Long-term (7-15 years):**

- The certification-safety gap will eventually surface through a catastrophic certified-system failure pattern that forces regulatory restructuring. The restructuring will impose outcome measurement requirements that the current industry structure cannot satisfy, forcing consolidation or transformation. Confidence: medium - direction is structurally predicted; timeline is speculative.
- If the gap surfaces gradually rather than catastrophically, the industry will calcify into pure ceremonial compliance - a regulatory tax on product development that neither produces safety nor pretends to, maintained by captured mandates and organizational inertia. Confidence: medium - alternative trajectory to catastrophic restructuring.

---

## 7. Audit Trail

**Sources consulted:** IEC 61508:2010, ISO 26262:2018, RTCA DO-178C:2012, IEC 62304:2006/AMD1:2015, ISO/IEC 17065:2012, MISRA public materials, FAA AC 20-115D, Reuters coverage of Brumadinho/TUV SUD (2019-2020). Academic literature: seven frameworks across quality economics, institutional theory, regulatory capture, agency theory, and audit independence.

**Cache status:** Fresh cache collected 2026-04-13. No prior report exists.

**Domain-specific rules generated:** Seven rules covering independence topology, accreditation scope match, artifact traceability, aerospace authority chain, sector standard fit, incident feedback, and tool qualification precision.

**Findings challenged and outcomes:**

- **Killed:** Test 19 (Network Effects) - domain mismatch; Test 24 (Commodity Trap) - domain mismatch; Test 37 (Sanctions Exposure) - insufficient evidence; R2 (Accreditation Scope) - subject already handles it; Test 30 (Vertical Integration Risk) - historical counter-example.
- **Reduced confidence:** Test 4 (Succession) reduced to medium-low.
- **Coupling Challenge:** Test 25 (Supply Chain Concentration) removed from Single-Point Regulatory Dependency compound (co-present, not amplifying). Gap Dynamic IV (Detection-Dismantlement) reframed from active dismantlement to underinvestment in monitoring.
- **Certified:** Twenty-nine findings survived Challenge. Five cross-cluster compounds, six within-cluster compounds, and four gap-derived dynamics survived Coupling Challenge.

---

## 8. References

**Primary Sources**

1. IEC 61508:2010, *Functional safety of electrical/electronic/programmable electronic safety-related systems*. International Electrotechnical Commission.
2. ISO 26262:2018, *Road vehicles - Functional safety*. International Organization for Standardization.
3. RTCA DO-178C / EUROCAE ED-12C, *Software Considerations in Airborne Systems and Equipment Certification*, 2012.
4. IEC 62304:2006/AMD1:2015, *Medical device software - Software life cycle processes*. International Electrotechnical Commission.
5. ISO/IEC 17065:2012, *Conformity assessment - Requirements for bodies certifying products, processes and services*. International Organization for Standardization.
6. Reuters, "Brazil police charge Vale, TUV SUD employees with homicide over dam collapse," 2020. Related coverage of German civil litigation against TUV SUD, 2019-2020.
7. MISRA Consortium Limited, public materials describing organizational structure and publications.
8. FAA Advisory Circular AC 20-115D, *Airborne Software Development Assurance Using EUROCAE ED-12() and RTCA DO-178()*.

---

Akerlof, George A. "The Market for 'Lemons': Quality Uncertainty and the Market Mechanism." *Quarterly Journal of Economics* 84(3):488-500, 1970.

Becker, Gary S. *Human Capital.* Columbia University Press, 1964.

Bourdieu, Pierre. *Distinction.* Harvard University Press, 1984.

Burja, Samo. "Great Founder Theory." Manuscript, 2020.

Darby, Michael R. and Karni, Edi. "Free Competition and the Optimal Amount of Fraud." *Journal of Law and Economics* 16(1):67-88, 1973.

DeAngelo, Linda E. "Auditor Independence, 'Low Balling', and Disclosure Regulation." *Journal of Accounting and Economics* 3(2):113-127, 1981.

DiMaggio, Paul J. and Powell, Walter W. "The Iron Cage Revisited: Institutional Isomorphism and Collective Rationality in Organizational Fields." *American Sociological Review* 48(2):147-160, 1983.

Goodhart, Charles A.E. *Monetary Theory and Practice.* Macmillan, 1984.

Grossman, Sanford J. and Hart, Oliver D. "The Costs and Benefits of Ownership." *Journal of Political Economy* 94(4):691-719, 1986.

Jensen, Michael C. and Meckling, William H. "Theory of the Firm: Managerial Behavior, Agency Costs, and Ownership Structure." *Journal of Financial Economics* 3(4):305-360, 1976.

Jonsson, Stefan, Greve, Henrich R. and Fujiwara-Greve, Takako. "Undeserved Loss: The Spread of Legitimacy Loss to Innocent Organizations in Response to Reported Corporate Deviance." *Administrative Science Quarterly* 54(2):195-228, 2009.

Lave, Jean and Wenger, Etienne. *Situated Learning.* Cambridge University Press, 1991.

Polanyi, Michael. *The Tacit Dimension.* University of Chicago Press, 1966.

Rao, Hayagreeva and Argote, Linda. "Organizational Learning and Forgetting." *European Management Review* 3(2):77-85, 2006.

Rochet, Jean-Charles and Tirole, Jean. "Platform Competition in Two-Sided Markets." *Journal of the European Economic Association* 1(4):990-1029, 2003.

Schumpeter, Joseph A. *Capitalism, Socialism and Democracy.* Harper & Brothers, 1942.

Stigler, George J. "The Theory of Economic Regulation." *Bell Journal of Economics* 2(1):3-21, 1971.

Suchman, Mark C. "Managing Legitimacy." *Academy of Management Review* 20(3):571-610, 1995.

---

*April 2026 - Opus 4.6*
