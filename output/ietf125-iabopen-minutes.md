# IAB Open - IETF 125 - 18 March 2026

**Session Date/Time:** 18 Mar 2026 03:30
**Format:** In-person with remote participation (Meetecho)
**Chairs:** Dhruv Dhody (incoming IAB Chair), Ying-Zhen Qu
**Outgoing Chair:** Tommy Pauly (remote)

## Attendees

- Dhruv Dhody - incoming IAB Chair
- Tommy Pauly - outgoing IAB Chair (remote)
- Ying-Zhen Qu - IAB member
- Bron Gondwana - M3AAWG liaison
- Jason Livingood - workshop presenter
- Eric Rescorla
- Mallory Knodel
- Xing Li - invited speaker, past IAB member
- Yaroslav - outreach coordinator (mentioned, did not speak)
- James
- [Speaker?] - ITU-T SG17 Chair [AMB-1]
- [Speaker?] [AMB-2]
- [Speaker?] [AMB-3]
- [Speaker?] [AMB-4]
- [Speaker?] [AMB-5]
- [Speaker?] [AMB-6]
- [Speaker?] [AMB-7]

## Summary

IAB Open at IETF 125 covered IAB leadership transition, a liaison update, an IP geolocation workshop report, and an invited talk on internet architecture challenges in the AI age. The IP geolocation discussion produced the sharpest disagreement, with strong pushback from the floor on whether the IAB should build consent-based geolocation replacements or instead work to degrade IP-based geolocation to force change.

### Welcome and IAB Updates
The incoming IAB chair presented updates on document status, WSIS+20 outcomes, and outreach activities.
- Permanent mandate for IGF secured at the UN General Assembly (adopted by consensus, December 2025); multi-stakeholder model and technical community role reaffirmed
- IAB protocol greasing document adopted from the EDM technical program; liaison documents 4052bis and 4053bis continue toward BCP publication
- New outreach coordinator appointed; outreach conducted at ICANN Mumbai (GAC, ALAC, newcomer sessions) and APRICOT/APNIC (operator engagement)

### M3AAWG Liaison Update
New liaison introduced; M3AAWG covers email, SMS, and RCS anti-abuse in a closed meeting environment, with published best practices available to all.
- M3AAWG's scope now includes SMS, RCS, and "shaken and stirred" in addition to email
- SMS Blaster attacks raised as an emerging threat - portable infrastructure in backpacks/vehicles conducting mobile SMS attacks, observed in Geneva and London
- AI is a major topic at M3AAWG; five or six regular M3AAWGers are attending IETF 125

### IP Geolocation Workshop Report
Workshop findings from December revealed that existing IP geolocation mechanisms (RFC 8005, RFC 9632) are under strain from CGNAT, proxies, and LEO networks, with fundamental disagreement on whether the path forward is building consent-based replacements or degrading IP geolocation to force adoption of privacy-respecting alternatives.
- Use cases span optimization (CDN, language settings, nearby content), enforcement (content licensing, legal compliance), and safety (emergency alerting, law enforcement)
- Existing mechanisms break down with shared IP addresses: CGNAT, Apple Private Relay, and Starlink/LEO networks where addresses span wide geographic areas
- "IP geolocation" is ambiguous - can mean physical user location, home location, network egress, infrastructure location, or regulatory jurisdiction
- GeoIP providers use degrees of trust/confidence rather than binary accuracy; deployment delays cause stale data (e.g., IETF attendees showing location from prior meetings)
- Privacy and consent emerged as the central tension: "break-before-make" (degrade IP geolocation first) versus "make-before-break" (build consent-based replacements first)
- Three to four new mechanisms proposed for conveying geographic data within packet exchanges or user sessions, potentially authenticated and consent-based
- RIR engagement urged - they are jurisdictionally positioned for regulatory use cases and have their own pain around regional IP allocation
- Architectural principle proposed: geolocation data and routing information should be completely distinct, with consent required for both revealing and querying location
- Community directed to read the report and provide feedback on architecture-discuss list

### Invited Talk: Internet Architecture in the AI Age
A past IAB member presented high-level architectural thinking on resilience, trust, fragmentation, and IPv6, arguing that AI agents are the internet's next major user class and need IPv6 addresses, DNSSEC, and address certificates.
- Resilience requires fully distributed architecture (per Paul Baran's framework); large centralized providers are "resilience killers"
- Trust models span one-time (SSH), hierarchical (DNS/DNSSEC, RPKI), web of trust (BGP), and forest of CAs (TLS); "names should be global but trust can be local" (forest of trust)
- Internet fragmentation is technical (IPv4/IPv6 incompatibility), governmental (geopolitics, firewalls), commercial (walled gardens), and AI-related (compute concentration, data bias, regulations)
- IPv4/IPv6 translation technologies (NAT64, 464XLAT, MAP-T per RFC 6052 and RFC 7915) are built into Android, iOS, and macOS; Windows support announced but not yet shipping
- AI agents need IPv6 addresses because they are servers, not clients; end-to-end connectivity preferred over cloud relay
- IPv6 address certificates (now supported by Let's Encrypt) are naturally coupled with routing and can provide agent identity
- Proposed "impossible triangle": resilience, trust, and controllability cannot all be achieved simultaneously
- Suggested adding AI considerations to every published RFC, alongside existing security and IANA considerations

### Open Mic
Brief exchange on whether AI agents can affect DNS operations; chair directed further discussion to architecture-discuss list and the Catalyst BoF recordings.

## Open Questions

- How should IETF approach the tension between IP geolocation use cases and privacy/consent?
- Should the IAB articulate architectural principles separating geolocation data from routing information?
- Should the approach be "break-before-make" or "make-before-break"?
- How should RIRs be engaged on IP geolocation from the numbering perspective?
- How should regulatory/law-enforcement geolocation requirements be handled where users may not have a legal right to refuse?
- Should every RFC include AI considerations?
- What are the architectural implications of AI agents as first-class internet participants needing IPv6 addresses?

---

## Discussion

### Welcome and IAB Updates

Dhruv Dhody (DD): Welcome to IAB Open. I'm your new incoming IAB Chair. Tommy is online as outgoing chair.

Tommy Pauly (TP): I've been very happy to be on the IAB for the past six years. Really looking forward to seeing where the incoming and continuing IAB takes it. These open meetings are a great way for the community and the IAB to have a dialogue.

DD: Note Well applies. Reach out via iab@iab.org (goes to all NomCom-elected members plus liaisons, IRTF chairs, some secretariat staff). Architecture-discuss list for bigger architectural discussions. liaison-coordination@iab.org for liaison queries.

DD: Workshop report from December is brand new. Adopted IAB protocol greasing document from the EDM technical program. Continuing work on liaison documents 4052bis and 4053bis - once IAB process complete, Roman will complete the IETF process as a BCP.

DD: WSIS+20 outcome at the UN General Assembly was adopted by consensus in December. Permanent mandate for IGF secured. Multi-stakeholder model reaffirmed, role of the technical community clearly established. Now the hard work continues.

DD: New outreach coordinator is Yaroslav. At the ICANN meeting in Mumbai, we did sessions with the GAC, ALAC, and a "how it works" session for fellows and newcomers. At APRICOT and APNIC, Warren presented on IETF topics, BoFs, and operator engagement.

Ying-Zhen Qu (YZQ): Agenda includes liaison update from M3AAWG, IP Geolocation Workshop report, and an invited talk from Xing Li. IAB has two Help Desk sessions - Monday already happened, another on Thursday. EDM technical program is not meeting this time but the draft is available.

### M3AAWG Liaison Update

Bron Gondwana (BG): I'm your liaison to M3AAWG. M3AAWG is an email and texting anti-abuse working group. Very different from IETF - M3AAWG is a closed environment. You don't want adversaries knowing the techniques used to block their behavior. Members may have product roadmaps they don't want publicized prematurely.

BG: M3AAWG publishes best practices about email. A lot of what IETF develops gets used by M3AAWG members in the real world. Some IETF work started in M3AAWG discussions. Five or six regular M3AAWGers are at IETF right now. AI is a big topic at M3AAWG as well. Published best practices are available to everybody even though the meetings are closed. Thanks to Barry for the slides and for having been the M3AAWG liaison for many years.

[Speaker?] [AMB-1]: I'm the ITU-T SG17 Chair, new Chair. SG17 Question 4 deals with spam. We recently discovered the SMS Blaster problem - people creating infrastructure they can put in a backpack, on a bike, on a car, moving around a city as an SMS Blaster. We've seen this in Geneva and London. We have a very bad feeling about the long-term intention. Is M3AAWG aware of this?

BG: I don't do much in the SMS space myself, but there are groups at M3AAWG working on SMS. M3AAWG covers mail, SMS, RCS, and all the "shaken and stirred" stuff. Scams, spams, and attacks on individuals are big topics.

### IP Geolocation Workshop Report

Jason Livingood (JL): The workshop was virtual across multiple days in December, focused on three topics: (1) use cases for publishing, discovery, and consuming IP geolocation data, (2) areas for incremental improvement within the existing system, (3) out-of-the-box thinking on better solutions.

JL: IP addresses were originally conceived to support routing, not carry geographic meaning. But extensive assumptions about geographic location are now widespread and deeply ingrained.

JL: Use cases include language and regional settings, finding nearby content ("pizza near me"), CDN optimization, content licensing enforcement (video streaming rights per country), legal compliance, emergency alerting, and law enforcement.

JL: Current mechanisms include RFC 8005 (CSV format), RFC 9632 (discovery and authentication), SVTA JSON format, and a large ecosystem of bespoke GeoIP providers. Providers use degrees of trust/confidence in location data - not binary true/false.

JL: Existing mechanisms struggle when IP addresses are widely shared: CGNAT on mobile networks, mask and proxies like Apple Private Relay, and LEO ISP services like Starlink where addresses are shared across wide areas.

JL: "IP geolocation" can mean many things: physical user location, physical home location, egress location, network infrastructure location, or regulatory jurisdiction. This causes confusion and misuse.

JL: Gaps include privacy/security issues around user consent, Geofeed format issues, deployment delays (updated CSV files not picked up promptly by list providers - IETF attendees sometimes show location from prior meetings), and location ambiguity between regions.

JL: Future directions: update Geofeed formats (CSV and JSON), plus three or four suggestions for entirely new mechanisms for conveying geographic data within a packet exchange or user session that could be authenticated, rely on user consent, or be more accurate.

JL: Bottom line: IP geolocation is not going away, no more than NAT is going away. How can we optimize the existing system while exploring entirely new mechanisms?

TP: Not everyone in the workshop, but many people raised privacy and consent as fundamental. Two things came out: even for those who just want geolocation for other reasons, more consent and intent would be good. The use cases aren't going away. To wean things off IP geolocation, we need consent-based mechanisms to satisfy use cases like enforcement validation. Then things like Mask can ramp up to obfuscate IP geolocation.

Eric Rescorla (ER): I'm frankly disappointed to hear the consent issue described as a gray area. The IETF has leaned in heavily on security and privacy. Being unconsensually located through a permanent address that reflects your location and identity is a serious bug in the internet architecture that has existed since the beginning. We are attempting to fix that with technology like Mask. Inventing new mechanisms to disclose information consensually - we've run this experiment before with Privacy Sandbox. People don't stop using the old mechanism; they use both and things get worse. What I want from the IAB is thinking about how to remove this privacy hole, not how to create new ones. Break-before-make, not make-before-break.

JL: The location discussed and used today is fairly coarse-grained - not a street address, more like a city.

ER: I agree use cases aren't going away, but what I hear is we're not going to work on the important part and instead work on making the problem worse. I want to hear what the IAB will do to actually resolve this problem. This is exactly the Privacy Sandbox story - we were going to get rid of third-party cookies, but in the meantime we created new tracking mechanisms. Break-before-make, not make-before-break.

Mallory Knodel (MK): I'm on Eric's side that this has to be solved. I want to address where this work should go. I looked for RIR participation in the workshop. I see RIPE, mainly because of RIPE Atlas, not because the ASO is taking action. Have you looked at this from the numbers side? RIRs are jurisdictionally placed to deal with thornier use cases like law enforcement. I'm surprised not to see anyone from AFRINIC or APNIC presenting.

DD: I'll disagree on the APNIC part. We had more people participate than were presenting. A number of RIRs attended the discussion; they just weren't presenters, which may indicate they don't have ready solutions.

MK: RIRs don't necessarily have solutions. They also have a lot of pain. AFRINIC has pain around regional allocation of IP space, and RIPE as well with Ukraine-Russia. Engaging them on the problem space from the numbering side could help find middle-ground solutions.

DD: Point taken. We continue to engage with all of them and will continue.

[Speaker?] [AMB-2]: If you want to build something new, you have to get the requirements right. I see this space very hard to define, especially around consent. There are cases where users want to be located for better service. Cases where the service provider wants to locate users and the user doesn't consent. And cases where the service provider must locate the user to apply policy rules and regulation, and the user has no legal right to object. You may not be able to keep all three use cases together. Make sure you talk to the policy community and regulators as stakeholders.

[Speaker?] [AMB-3]: Reinforcing what Eric said - we are not going to get a good system by building a good system. If we build a good system, people will keep using the bad system because it's easier. The only way to make this system evolve is to burn it to the ground. Study how to make IP geolocation impossible to make work right so that people are forced to do the right thing. That should be the work for the IAB.

[Speaker?] [AMB-4]: From an architectural principle, geolocation data and routing information should be completely distinct. Mechanisms to reveal your location should require consent. Mechanisms to query that location should require consent. These are architectural principles the IAB could articulate and are already the basis of work like Mask. GeoPriv was an effort I was involved with for many years, and it was frustrated by requirements from e-911 and others that location be attested by trusted entities rather than asserted by individuals. There is very little chance of making this architectural principle plain without facing friction, but it's worth facing that friction.

[Speaker?] [AMB-5]: The problem should be split between IPv6 and IPv4. Due to IPv4 scarcity, majority cases involve NATting, so geolocation can only arrive at the legislation level. For IPv6, theoretically more precise positioning is possible, but then there is the privacy issue. This has to be linked to user consent.

DD: We are still discussing this on architecture-discuss list. Please give feedback, read the report.

### Invited Talk: Internet Architecture in the AI Age

Xing Li (XL): I've been working on internet for more than 30 years. We built three networks. First was CERNET, the first internet national backbone in China - from IP over X.25 to 100G WDM. Second, because there are about 320 million students in China and we didn't think we'd have enough IPv4 addresses, we started IPv6 in 1997. We chose single-stack IPv6 rather than dual stack. CERNET2 is still IPv6-only. Now building CERNET3/FITI (Future Internet Testing Bed [?]), also IPv6-only, addressing the walled garden problem.

XL: On resilience, referring to Paul Baran's report - centralized, decentralized, and distributed. Only fully distributed can support resilience. I enjoy the IRTF Decentralization working group.

XL: On the internet hourglass architecture - connectionless, best effort, end-to-end. Should we keep this or improve? SRv6, if every hop has a segment, may be back to connection-oriented. AI requires high quality. CDN - I tell my students it's still end-to-end, just two segments: user to cloud and server to cloud.

XL: In the AI age, each layer can use LLM to improve performance and functionality. More importantly, above the application layer and below humans, there's an AI layer - an eighth layer. Current public internet has some big players that are resilience killers. IAB should identify those bottlenecks.

XL: On trust - SSH is one-time trust. DNS/DNSSEC are hierarchical. BGP is a form of web of trust, distributed. But RPKI requires trust anchors (five, one per RIR) - still hierarchical. Web relies on a forest of CAs and TLS. I believe names should be global but trust can be local - a forest of trust.

XL: On internet fragmentation, drawing from Vint Cerf's IGF report: technical (IPv4/IPv6 incompatibility, DNS hijacking, new gTLDs creating semantic non-uniqueness), governmental (geopolitics, firewalls), commercial (walled gardens), and AI-related (compute concentration, data biases, regulations). My belief is a single internet connecting everywhere, but we have to fight these forces as engineers.

XL: On the Snowden event in 2013 when I was on the IAB - IETF really pushed HTTPS. But with HTTPS, gateways can no longer selectively reset TCP sessions on non-sensitive content. HTTPS is a good solution but it does introduce a form of fragmentation.

XL: On IPv4/IPv6 translation - v4 and v6 are not compatible, but through translation (NAT64, 464XLAT, MAP-T based on RFC 6052 and RFC 7915), real IPv6 can talk to real IPv4. Modern operating systems (Android, iOS, macOS) have these built in. Microsoft announced Windows support last March but it's still not reality.

XL: We've done linear translation (RFC 6052), nonlinear/one-directional mapping, non-stateful remapping for privacy, and crypto-based mapping. Recently did AI-based mapping using language models for addresses - published as "IPv6 Transformers" before ChatGPT was introduced.

XL: AI challenges for the network: performance and reliability requirements. Fragmentation means double firewalls for accessing services like OpenAI from China. Centralization - AI controlled by big players. Agents - we have IDs and faces for people, but for agents we don't know. On the internet, nobody knows you're a dog; currently nobody knows you're a robot.

XL: AI agents need IPv6 addresses because they're servers, not clients. For internet, we don't want everything relayed through the cloud - we want end-to-end. I'm surprised there isn't more talk about IPv6 for AI agents. Trust should use DNSSEC and IPv6 address certificates. Let's Encrypt announced automatic signing for IPv6 addresses.

XL: On fragmentation and geopolitics - engineers cannot convince politicians. My idea is back to the beginning: network of networks. Whatever the geopolitics or natural disasters, if servers and clients are inside networks, internet should work. DNS resolving chain breakage and isolated RPKI need to be solved.

XL: I see an impossible triangle: resilience, trust, and controllable. Distributed approaches can achieve resilience and trust but not controllability. Hierarchical can achieve controllability and trust but not distributed resilience. This may be a fundamental problem for IETF and researchers.

XL: IPv6 - originally internet for connecting machines, then mobile internet for connecting people, IPv6 for IoT. But after ChatGPT, the majority of internet users will be robots, not humans. We must keep the distributed nature and maintain uniqueness of addresses, names, and protocol parameters.

XL: In RFC considerations, we have security considerations and IANA considerations. IETF is working on human rights considerations. My suggestion: starting now, we should put AI considerations in every published RFC.

#### Q&A

[Speaker?] [AMB-6]: You mentioned IPv6 will be important for agent networks. Beyond address space, can you give more benefits?

XL: Agents are basically HTTP/HTTPS servers. You can use HTTPS with address certificates - that's your agent, not a hijacked agent. IPv6 address certificates are naturally coupled with routing. Inside your network, if the certificate is trustable, even if outside connections break, you still have connectivity. Maybe we need double certificates - DNS certificates for names and IP address certificates for routing.

[Speaker?] [AMB-7]: Regarding AI and centralization - when we make technological choices, it's very difficult to map requirements to design. We have never formalized a theory of design that could create such a mapping. We should work on methodology to materialize requirements into concrete standardization requirements.

XL: I believe this is important.

### Open Mic

James: Can AI agents affect the operation of DNS systems, positively or negatively?

XL: DNS is the easiest thing to keep unique, so DNS is very important even for robots. IPv6 address certificates can work together with DNS. DNS or DNS extensions for robots are very important, in conjunction with address certificates.

James: Can AI agents impact the DNS system positively or negatively?

DD: Let's take this discussion to architecture-discuss list. Watch the recordings of the Catalyst BoF and continue the discussion.

DD: Thanks everyone for participating. IAB is always available for feedback.

YZQ: Thank everybody. It's my first time chairing the IAB Open. Hope to see you next time.

---

## Unknowns [?]

- "FITI" - Future Internet Testing Bed, mentioned by Xing Li as CERNET3
- "Catalyst BoF" - referenced as a BoF session held earlier at IETF 125

## Ambiguities

- [AMB-1] "Speaker 1" identifies as the ITU-T SG17 Chair, new Chair. Name not stated in the transcript. Resolution needed: confirm speaker identity.
- [AMB-2] "Speaker 2" is unidentified. Made comments about requirements around consent and the need to engage the policy community. Resolution needed: confirm speaker identity.
- [AMB-3] "Speaker 3" is unidentified. Argued that IP geolocation should be made unreliable to force adoption of better mechanisms. Referenced "what Ecker said" (likely referring to Eric Rescorla). Resolution needed: confirm speaker identity.
- [AMB-4] "Speaker 4" is unidentified. Referenced personal involvement in GeoPriv and discussed architectural principles around consent. Resolution needed: confirm speaker identity.
- [AMB-5] "Speaker 5" is unidentified. Discussed splitting the problem between IPv6 and IPv4, and source privacy. Resolution needed: confirm speaker identity.
- [AMB-6] "Speaker 6" is unidentified. Asked Xing Li about IPv6 benefits for agent internet beyond address space. Resolution needed: confirm speaker identity.
- [AMB-7] "Speaker 7" is unidentified. Referenced the Catalyst BoF and discussed formalization of design theory. Resolution needed: confirm speaker identity.

## Corrections Welcome

Please correct anything that was misunderstood or missed.
