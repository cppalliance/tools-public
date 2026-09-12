# A Foundation Built on One Conference

**The Standard C++ Foundation operates as a $2 million conference-organizing entity governed by a five-person self-selecting board with no community accountability mechanisms, consuming founder reputational capital without building institutional capacity.**

April 2026, by Vinnie Falco

---

## 1. Executive Summary

The Standard C++ Foundation is structurally a conference company wearing a foundation's clothes. Revenue of $1.8-2.1 million flows overwhelmingly through CppCon, the single annual event that funds all other programs.<sup>1</sup><sup>2</sup> When CppCon was disrupted by the pandemic, WG21 financial assistance - the Foundation's most distinctive non-conference program - was suspended.<sup>7</sup> The revenue model is not diversified. It is a single point of failure.

The Foundation's governance has not matured beyond its founding structure in twelve years. A five-person self-selecting board publishes minutes and annual reports, but these are the only transparency mechanisms, and the board controls them.<sup>3</sup> No independent audit exists. No community election exists. No advisory body exists. No term limits are published. The C++ developer community - the Foundation's stated beneficiary - has no governance voice and no formal path to acquiring one. When external stakeholders requested governance reforms in 2022, some requested changes were not implemented.<sup>6</sup>

The dominant structural dynamic is what this analysis terms the Blind Keystone: concentrated power and information in a small board that prevents the community from observing the Foundation's structural risks - including an approaching demographic succession cliff, the consumption of founder reputational capital, and the performative nature of its governance ceremonies. The institutional prognosis is Cargo Cult: the Foundation performs the rituals of institutional governance (minutes, reports, policies) without the substance (independent oversight, community accountability, succession planning). The rituals are not understood as accountability instruments by the body that performs them, because the body performing them is the same body they are meant to hold accountable.

One improving signal: Herb Sutter is no longer the WG21 Convener.<sup>5</sup> Guy Davidson now holds that role, partially decoupling the Foundation's leadership from the standards committee it supports. This weakens the bidirectional reputational contagion and reduces the related-party dynamics in WG21 financial assistance. But the internal governance deficits remain unaddressed by the external transition.

---

## 2. The Subject

The Standard C++ Foundation is a Washington state nonprofit organized as a 501(c)(6) trade association, EIN 46-1356355, formed in 2012 with federal tax-exempt recognition since June 2014.<sup>1</sup><sup>3</sup> Its stated mission is to support the C++ developer community and promote the use of modern Standard C++. It states it will not make political statements.<sup>3</sup>

The Foundation operates four programs: isocpp.org (community website), GitHub organizations (isocpp and cplusplus), CppCon (annual conference including cppcon.org and YouTube channel), and WG21 financial assistance (hosting subsidies, travel grants, and proposal-development grants under a published policy).<sup>3</sup><sup>4</sup>

The board comprises five officers:

1. Herb Sutter - Chairman, President (compensated; $85,275 in FYE 2024, $40,650 in FYE 2025)
2. Bjarne Stroustrup - Treasurer (uncompensated)
3. Nina Ranns - Vice-President, Marketing and IP (uncompensated)
4. Inbal Levi - Secretary (uncompensated)
5. Michael Wong - Director (uncompensated)

The Foundation reports zero employees on IRS filings.<sup>1</sup><sup>2</sup> All operations are conducted by the board and volunteers. Contributions are not tax-deductible (501(c)(6) classification). Net assets grew from $404,663 to $936,950 between FYE 2024 and FYE 2025.<sup>1</sup><sup>2</sup>

---

## 3. The Landscape

Programming language foundations occupy a specific niche: they provide infrastructure, governance, and community coordination for a language ecosystem without owning the language itself. The Standard C++ Foundation is legally separate from ISO/IEC JTC1/SC22/WG21 - the committee that develops the C++ standard. The Foundation does not own, govern, or control C++ standardization. Its relationship to WG21 is voluntary financial assistance under a published policy that requires both Foundation board and WG21 officer approval for disbursements.<sup>4</sup>

The market for C++ community infrastructure is competitive. Multiple conferences serve the C++ community (Meeting C++, C++ Now, CppNorth, ACCU, and others). No entity has exclusive control over C++ education, tooling, or community gathering. The Foundation's distinctive assets are the CppCon brand, isocpp.org, and the WG21 financial assistance relationship - none of which constitute a monopoly.

Comparable foundations in adjacent language ecosystems operate at different scales and governance models. The Python Software Foundation (501(c)(3), elected board, staff, direct governance of CPython) and the Apache Software Foundation (501(c)(3), merit-based membership, elected board, project-centric governance) both feature community accountability mechanisms the Standard C++ Foundation lacks. The Linux Foundation (501(c)(6), like the Standard C++ Foundation) operates with hundreds of staff and thousands of members. The comparison is structurally relevant because the Standard C++ Foundation presents itself as the same category of institution while lacking the governance infrastructure that defines the category.

---

## 4. Structural Assessment

### 4.1. The Personal Empire

The Foundation's power structure is a personal empire in the structural sense (Burja 2020): operational capacity, institutional legitimacy, external relationships, and information all concentrate in a small group dominated by its chairman. With zero employees, the board does not govern an organization - it IS the organization. There is no staff to implement board decisions independently. There is no executive director to provide operational continuity across board transitions. The chairman's personal capacity is the Foundation's institutional capacity.

Herb Sutter's influence derived from holding simultaneous positions as Foundation Chairman/President and WG21 Convener - the person who steers both the supporting organization and the committee it supports. This dual position made the Foundation's most distinctive power borrowed: the WG21 convener role is an ISO appointment the Foundation does not control (Grossman and Hart 1986). The convener transition to Guy Davidson partially resolves this.<sup>5</sup> The Foundation's WG21 link now runs through its published financial assistance policy rather than through a single person sitting on both sides of disbursement decisions.<sup>4</sup> This is an improving signal. But the transition was not initiated by Foundation governance reform - it resulted from a change in an ISO appointment. The Foundation did not build structural separation; structural separation happened to it.

The legitimacy underpinning the Foundation is primarily founder-derived (Suchman 1995). Sutter and Stroustrup are among the most recognized names in C++. The Foundation has not built governance mechanisms that generate legitimacy independent of its founders - no elected board, no community governance structure, no institutional identity separate from its officers' personal brands. If both founders departed, the remaining institutional assets would be CppCon's brand and isocpp.org's content - operational assets, not institutional authority. (medium-high)

### 4.2. CppCon as Institution

The Foundation's annual report states that the majority of funds received and spent came from running CppCon.<sup>7</sup> Form 990 filings show total revenue of $1,823,333 (FYE 2024) and $2,102,990 (FYE 2025), with expenses of $1,748,100 and $1,570,703 respectively.<sup>1</sup><sup>2</sup> The Foundation's stated mission encompasses "the C++ developer community" globally, but its resource allocation concentrates on a single annual conference held in the United States with ancillary programs consuming a fraction of the budget. The alignment gap between stated mission scope and actual resource allocation is structural (Jensen and Meckling 1976).

This concentration creates a portfolio risk that is not theoretical. When the pandemic disrupted CppCon, WG21 hosting support was suspended and only resumed post-pandemic (Kingma 1993).<sup>7</sup> The revenue shock propagated directly to the Foundation's non-conference programs, confirming that CppCon is not merely the primary revenue source but the sole revenue source on which all other programs depend. CppCon in-person attendance declined from approximately 750 in 2024 to 700 in 2025.<sup>8</sup> No new revenue streams have been announced.

The Foundation is accumulating financial capital - net assets nearly doubled between FYE 2024 and FYE 2025.<sup>1</sup><sup>2</sup> But financial accumulation masks reputational capital consumption (Mises 1949). The Foundation's institutional reputation depends on its founders' personal brands, and no investment is visible in building institutional legitimacy independent of those brands - no hired executive director, no expanded programs, no community governance structure that would generate its own authority. Financial reserves grow while institutional capacity remains static. (medium)

### 4.3. Governance Without Constituents

The Foundation's information architecture concentrates all operational visibility in five board members while the community relies on voluntarily disclosed summaries (Akerlof 1970).<sup>3</sup> No independent audit exists. No external oversight committee exists. No mandatory disclosure mechanism exists beyond IRS Form 990 filings. The board publishes its own minutes - a self-correction mechanism run by the people whose work it evaluates. Such mechanisms are ceremonies, not feedback instruments (Ashby 1956).

This information closure sustains a principal-agent misalignment (Jensen and Meckling 1976). The C++ developer community is the Foundation's stated beneficiary - the principal. But the community has no governance voice: no elections, no advisory board, no formal feedback mechanism, no path to board membership. The board controls all information disclosure and all resource allocation decisions. The community's only recourse for dissatisfaction is public criticism or disengagement. When #include &lt;C++&gt; publicly assessed the Foundation's governance transparency in June 2022, requesting reforms including board composition changes and CppCon governance improvements, some requested changes were not implemented.<sup>6</sup> The criticism was voluntarily received and voluntarily addressed - the Foundation was not structurally obligated to respond.

The Olson trap explains the equilibrium (Olson 1965). Active participation concentrates among board members and CppCon sponsors who receive selective benefits - conference access, networking, visibility. The broader C++ community benefits from public goods (free CppCon YouTube recordings, isocpp.org content) without contributing to governance. This is rational: governance voice has no entry point, and the selective benefits of engagement accrue only to insiders. The community's rational disengagement eliminates pipeline pressure for governance reform. The board faces no competitive pressure from outside candidates because no candidate mechanism exists (Lave and Wenger 1991). The result is a self-reinforcing equilibrium: no one demands governance entry points because no one expects governance voice, and the board does not create entry points because no one demands them.

### 4.4. The Succession Problem No One Discusses

The Foundation faces a demographic cliff it has no mechanism to address. Bjarne Stroustrup is approximately 76 years old. Herb Sutter is approximately 59. Michael Wong's career timeline suggests he is in his 50s or 60s. The board's most prominent members - the people who carry institutional knowledge, sponsor relationships, and community legitimacy - are concentrated in an older cohort (Rao and Argote 2006). With zero employees and no documented knowledge transfer, departure would be a cliff, not a slope. (medium)

The succession problem is compounded by the extreme skill intersection required for Foundation governance (Becker 1964). A successor would need C++ technical expertise, nonprofit governance experience, conference management capability, and WG21 process knowledge. This intersection is not supplied by any training pipeline. The current board was assembled from personal networks, not developed through institutional mechanisms. Even if a governance pipeline were established, the external supply of qualified candidates is nearly zero.

CppCon organizational knowledge - venue relationships, sponsor relationships, volunteer networks, speaker pipelines - appears to reside as tacit knowledge in a small number of people (Polanyi 1966). With zero employees, formal process documentation is unlikely to be comprehensive. The knowledge and its carriers face the same demographic clock. When holders depart, the question of whether their knowledge is transferable will be answered for the first time - and by then it will be too late to transfer it. (medium)

The coupling between succession risk and information closure makes the problem structurally invisible. The community cannot assess whether succession planning exists because the board controls all disclosure. The board may not recognize the urgency because no independent feedback mechanism forces self-assessment (Katz and Kahn 1966). The gap-derived dynamic across these findings describes an organization that lacks the structural capacity for self-recognition: knowledge holders assume documentation is adequate, governance does not track its own demographic concentration, and the community cannot investigate either assumption.

---

## 5. Institutional Durability

**Cargo Cult.** The Standard C++ Foundation performs the rituals of institutional governance without the substance. Board minutes are published - but the board writes its own report card. Annual reports are filed - but the board controls the narrative. A financial assistance policy exists - but the arm's-length relationship was personnel-dependent rather than structurally guaranteed. The Foundation adopted the form of a programming language foundation (Burja 2020) but not the generating principles of its models: no elected board, no community governance, no staff, no multiple programs, no institutional identity independent of its founders. After twelve years and documented external criticism, no adaptation in governance structure is visible (North 1990). The ceremonies persist. The understanding is absent.

The operational layer is functional. CppCon runs. Revenue grows. WG21 receives assistance. isocpp.org serves the community. The Foundation fills a real socioeconomic niche - if it vanished, CppCon would stop, and that would be noticed within six months. The institution is not Terminal. But operational functionality masking governance dysfunction is the defining characteristic of a cargo cult institution: the cargo arrives despite the ceremonies, not because of them. CppCon succeeds because conferences with strong brands, good content, and network effects succeed - not because the Foundation's governance drives quality. The governance layer could be removed entirely and CppCon would function identically, which means the governance layer is not functional governance.

---

## 6. Predictions

**Short-term (1-3 years):**

- If CppCon attendance continues declining below 700, Foundation revenue will contract and WG21 financial assistance will be the first program cut - consistent with the pandemic precedent when CppCon disruption immediately suspended WG21 support.<sup>7</sup> If attendance stabilizes above 700, the revenue model holds for the near term. Confidence: medium-high (documented precedent and declining trend).

- If the convener transition to Guy Davidson is accompanied by no changes to the Foundation's financial assistance approval process, the related-party dynamics will diminish structurally but the governance opacity will remain. If the Foundation updates its policy to reflect the new convener relationship, this would indicate governance adaptation capacity. Confidence: medium (structurally inferred).

**Medium-term (3-7 years):**

- If board composition remains unchanged, Bjarne Stroustrup's eventual departure from the Treasurer role will remove a founding name from governance and test whether the Foundation has institutional legitimacy independent of its founders. If the board proactively recruits younger members with transparent selection criteria, the demographic cliff becomes manageable. Confidence: medium-high (verifiable demographic trajectory).

- If no independent governance mechanisms are established (elected positions, advisory committee, community representation), the Foundation will continue to function as a conference-operating entity but will face increasing governance legitimacy pressure as community expectations rise and comparable foundations (PSF, ASF) set higher transparency baselines. If governance reforms are implemented, legitimacy becomes self-renewing. Confidence: medium (structural inference and documented criticism trajectory).

**Long-term (7-15 years):**

- If C++ language market share erodes significantly to memory-safe alternatives, conference demand declines, governance remains unreformed, and succession is unplanned, the Foundation faces existential risk from compounding structural deficits - none individually fatal, all mutually reinforcing. If any one condition is addressed (C++ remains dominant, governance reforms, succession planned), the compound risk is mitigated. Confidence: low-medium (compound conditional with long time horizon).

---

## 7. Audit Trail

**Cache:** `.cache/_standard-cpp-foundation.md` - fresh, collected 2026-04-13 UTC

**Sources consulted:**

- IRS Form 990 filings via ProPublica Nonprofit Explorer (FYE 2024, FYE 2025)
- isocpp.org/about (governance, mission, officers, programs)
- isocpp.org/about/financial-assistance-policy (WG21 assistance policy)
- isocpp.org/std/the-committee/ (WG21 Convener listing)
- #include &lt;C++&gt; assessment, June 2022 (governance criticism)
- Standard C++ Foundation FY2024 Annual Report, isocpp.org blog
- CppCon Sponsorship Prospectus, 2024-2025
- Cause IQ and ProPublica Nonprofit Explorer (entity data, financial extracts)
- WG21 cache (cross-referenced for ecosystem context)

**Domain-specific rules generated:** 7 (revenue mix, WG21 funding flows, governance independence, executive compensation, conference safety, trademark/IP, operational footprint)

**Diagnostic tests run:** 45 baked-in + 7 domain-specific + 7 theory-derived predictions = 59 total

**Findings produced:** 25 candidate findings from 18 tests, 4 domain rules, 3 theory predictions

**Challenge outcomes:** 0 killed. All 25 findings certified. 2 adjusted to medium confidence (Test 6 Intellectual Dark Matter, Test 33 Capital Consumption).

**Coupling analysis:** 11 compound dynamics identified. 1 constituent removed (Test 9 from Accountability Void compound - co-present but not genuinely amplifying). 4 gap-derived participant-level dynamics identified. All survived coupling challenge.

**Directional signals:** 7 findings with directional evidence. 3 improving (convener transition effects), 1 stable (revenue mix unchanged), 1 degrading (CppCon attendance), 2 partially improving (resumed WG21 spending, convener separation).

**Prior reports:** None. First evaluation of this subject.

**User questions:** 2 questions posed (dual role verification, Foundation authority scope). User declined to answer. Both assumptions proceeded as unresolved; findings that depend on them carry reduced confidence.

---

## 8. References

**Primary Sources**

1. IRS Form 990, Standard CPP Foundation, EIN 46-1356355, FYE 2024-06-30. ProPublica Nonprofit Explorer.
2. IRS Form 990, Standard CPP Foundation, EIN 46-1356355, FYE 2025-06-30. ProPublica Nonprofit Explorer.
3. "About the Standard C++ Foundation." isocpp.org/about.
4. "Financial Assistance Policy." isocpp.org/about/financial-assistance-policy.
5. "The Committee - WG21." isocpp.org/std/the-committee/ (listing Guy Davidson as Convener, January 2026).
6. #include &lt;C++&gt; governance assessment, June 23, 2022.
7. Standard C++ Foundation FY2024 Annual Report, isocpp.org blog.
8. CppCon Sponsorship Prospectus, attendance figures 2024-2025.

---

Akerlof, G.A. "The Market for 'Lemons': Quality Uncertainty and the Market Mechanism." *Quarterly Journal of Economics* 84(3):488-500, 1970.

Ashby, W.R. *An Introduction to Cybernetics.* Chapman & Hall, 1956.

Becker, G.S. *Human Capital.* Columbia University Press, 1964.

Bharath, D.M.N. and Carter Kahl, S. "Founder or flounder: When board and founder relationship impact nonprofit performance." *Journal of Public Affairs Education* 27(2):238-253, 2021.

Burja, S. "Great Founder Theory." Manuscript, 2020.

Grossman, S.J. and Hart, O.D. "The Costs and Benefits of Ownership: A Theory of Vertical and Lateral Integration." *Journal of Political Economy* 94(4):691-719, 1986.

Jensen, M.C. and Meckling, W.H. "Theory of the Firm: Managerial Behavior, Agency Costs and Ownership Structure." *Journal of Financial Economics* 3(4):305-360, 1976.

Katz, D. and Kahn, R.L. *The Social Psychology of Organizations.* John Wiley & Sons, 1966.

Kingma, B.R. "Portfolio Theory and Nonprofit Financial Stability." *Nonprofit and Voluntary Sector Quarterly* 22(2):105-119, 1993.

Lave, J. and Wenger, E. *Situated Learning: Legitimate Peripheral Participation.* Cambridge University Press, 1991.

Mises, L. *Human Action: A Treatise on Economics.* Yale University Press, 1949.

North, D.C. *Institutions, Institutional Change and Economic Performance.* Cambridge University Press, 1990.

Olson, M. *The Logic of Collective Action: Public Goods and the Theory of Groups.* Harvard University Press, 1965.

Pfeffer, J. and Salancik, G.R. *The External Control of Organizations: A Resource Dependence Perspective.* Harper & Row, 1978.

Polanyi, M. *The Tacit Dimension.* University of Chicago Press, 1966.

Rao, H. and Argote, L. "Organizational Learning and Forgetting: The Effects of Turnover and Structure." *European Management Review* 3(2):77-85, 2006.

Suchman, M.C. "Managing Legitimacy: Strategic and Institutional Approaches." *Academy of Management Review* 20(3):571-610, 1995.

---

*April 2026 - Opus 4.6*
