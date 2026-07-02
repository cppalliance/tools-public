# The Staker

## Pipeline

### Step 0. Global Rules

* `{date}` is YYYY-MM-DD when the run started.

* `{prompt}` is the user's verbatim query, carried unchanged from the run's start.

* `{slug}` is the kebab-case organization name, known preferred form, or up to four best words:
  - `wg21` for "Working Group 21"
  - `bitcoin-core-developers` for "Bitcoin Core Developers"
  - `standard-cpp-foundation` for "Standard C++ Foundation"
  - `society-promotion-japanese-animation` for "Society for the Promotion of Japanese Animation"

* Write scratch files into `{date}-staker-{slug}/`
  - Overwrite existing contents
  - Never import a prior run's files.

---

### Step 1. Survey

This step launches multiple subagents to collect corroborated evidence, then merges and deduplicates the evidence. The merged Evidence File is `{date}-staker-{slug}/{date}-staker-{slug}-evidence.md` (**scratch**). Subagents write to the file evidence-N.md with different N starting at 1.

Launch five subagents (model tier: **parent**) and run these instructions verbatim. Do NOT paraphrase. Do NOT add anything. Do NOT augment from your training data. USE ONLY THIS:

Use WebSearch to fill in this exact template in the file. Follow source chains: when a result names a document, paper, filing, or primary record not yet in your notes, search for it directly.

For each section, search independently and exhaustively: at least 2-3 different query angles per section. After each search pass, note what's still missing and search again for gaps. Do not conclude a section until claims have primary sources or you've exhausted available search strategies.

```
---
date:
model:
domain:
---

# {organization}

## Organization Profile

founding, stated mission, structure, governance, funding model, and Blau-Scott classification (mutual-benefit, business, service, or commonweal). Identify any adjacent support entities (foundations, fiscal sponsors, allied nonprofits) with their legal form, founding date, leadership overlap with the organization, and funding sources. Quote specific financial metrics where publicly documented: revenue, expenses, compensation, membership fees, sponsor tiers, event costs, and per-unit pricing of the organization's output.

## Actual Purpose

what the organization observably does and what drives its resource acquisition. If stated and actual purpose align, note it. If they diverge, note the divergence as governance context, not as the dominant pathology.

## Domain Primer

three to five structural facts a reader needs to understand the sector

## Domain Landscape

search broadly: position, competitors, dependencies, peer bodies for benchmarking, trend, and anything structurally significant the searches reveal beyond these. Where available, report cohort metrics: population, growth rate, and survey penetration for any measurable group - the organization's constituency, its output's user base, its competitors, and its workforce.

## Public Record

press, filings, controversy, reputation. Search for named departures, public resignations, or burnout testimony by former participants; governance reform campaigns and their outcomes; and any external regulatory or government pressure campaigns directed at the organization or its domain. If `{prompt}` names a specific concern, also search whether the organization has an existing mechanism for that class of concern (ombudsman, grievance process, code of conduct enforcement, appeals process) and whether it has been invoked. No concern named is valid - skip it.

## Outlier Signals

benchmark against the peer class from Domain Landscape

### Base-peer

normal absent evidence; finding nothing is valid and leaves the default standing.

### Concrete

leadership tenure and transitions; governing-body selection method; largest funder, customer, or sponsor share; share of effort sustaining itself versus producing stated output; membership trend; leadership careers overlapping funders, regulators, customers, or suppliers; role concentration - whether any individual holds concurrent leadership positions across the organization and its adjacent entities. Specific facts only, benchmarked where a standard peer benchmark already exists - never synthesize one.

### Qualitative

documented descriptions of the organization as unusual or non-standard - by press, researchers, members, or competitors - on dimensions the concrete facts don't reach.

## Domain-Specific Vulnerabilities

sector-specific risks with sources. Include: parent-body or supply-chain dependencies that create friction the organization cannot control; binding constraints from implementers, adopters, or certifiers whose capacity gates the organization's output; and sustainability risks from volunteer or single-maintainer concentration.

## Initial Stakeholder Enumeration

a wide-net list built by snowball logic (who funds, governs, uses, competes with, or depends on the organization), with a one-line rationale for each inclusion. Cast the net beyond direct participants: include tool and compliance vendors whose products depend on the organization's output, academic and research contributors, regulatory or government bodies exerting external pressure, and the end-user community that consumes the output but does not participate in governance.
```

Return one status line containing the output filename and number of lines when complete.

When all subagents have finished, merge and deduplicate all the subagent output into a single Evidence File. Claims are strongest when they appear multiples times, and weakest when they appear once. Note this.

---

### Step 2. Stakeholder Identification

After Step 1 finishes.

Launch a subagent (model tier: **parent**) and run these instructions verbatim. Do NOT paraphrase. Do NOT add anything. Do NOT augment from your training data. USE ONLY THIS:

**Create** the Evidence File `{date}-staker-{slug}/{date}-staker-{slug}-evidence.md` (**scratch**). Use WebSearch to fill in this exact template in the file. Follow source chains: when a result names a document, paper, filing, or primary record not yet in your notes, search for it directly.

For each section, search independently and exhaustively: at least 2-3 different query angles per section. After each search pass, note what's still missing and search again for gaps. Do not conclude a section until claims have primary sources or you've exhausted available search strategies.





Spawn one subagent (parent tier). Its prompt is these lines, paths resolved:

1. From the Evidence File read the Organization Profile, Public Record, Outlier Signals, and Initial Stakeholder Enumeration.
2. Grep `stakeholder-identification` in {tool-path} and follow the instructions between the opening and closing tags.

<stakeholder-identification>

Screen every candidate in the Initial Stakeholder Enumeration for salience, flag actor types, and write the results. This is triage, not final classification - Step 6 rescores with full evidence.

Set the unit of analysis first. Group actors that share the same structural role and the same type of stake. Separate an individual from its institution only when at least two of three tests say separate:

| Test | Separate when | Aggregate when |
|---|---|---|
| Divergent response | The actor would plausibly act against the position of every institution it belongs to | The actor acts as an institution's instrument |
| Non-transferable power | Influence rests on personal expertise or reputation a successor would not inherit | Influence rests on the office and transfers with it |
| Independent stake | Exposure or incentives extend beyond every institution the actor belongs to | The stake is a subset of an institution's stake |

A unique office - a chair, an editorship - is not by itself grounds for separation. Ask whether replacing the holder would change the dynamics; if not, the office belongs to the institution's entry.

**Three salience attributes (Mitchell, Agle and Wood 1997):**

- **Power** - the actor can impose its will on the organization through force or threat, control of material resources, or social influence and prestige. Test: if this actor withdrew cooperation or applied pressure, would the organization be compelled to respond?
- **Legitimacy** - the actor's relationship with the organization is recognized as appropriate within the norms of the domain. Test: would a reasonable observer of this domain expect this actor to have a stake in the organization's decisions?
- **Urgency** - the actor's own claim on the organization is both time-sensitive and critical. Both components required. Domain pressure is not actor urgency; it counts only where it lands on this actor's own claim.

| Urgency component | Question | Present when |
|---|---|---|
| Time sensitivity | Is delay unacceptable to this actor? | A deadline, closing window, or worsening trajectory attaches to this actor's own exposure |
| Criticality | Does the claim matter deeply to this actor? | The claim touches the actor's core function, survival, or primary value proposition |

For each candidate, mark each attribute present or absent with a one-sentence structural justification naming the structural fact. Power-base typing belongs to later steps.

The attributes place each candidate in one of seven classes; the tier is the attribute count:

| Tier | Class | Attributes |
|---|---|---|
| 3 | Definitive | P+L+U |
| 2 | Dominant | P+L |
| 2 | Dangerous | P+U |
| 2 | Dependent | L+U |
| 1 | Dormant | P |
| 1 | Discretionary | L |
| 1 | Demanding | U |

A candidate with no attribute present is a non-stakeholder: keep its block, Class: None, ranked last.

**Three actor-type flags:**

Apply these flags to any candidate that matches. A candidate may carry zero or more flags.

- **Hidden** - an actor whose influence on the organization is real but not visible in the org chart, membership list, or public record. Identification: the survey's Organization Profile, Public Record, or Outlier Signals sections name an influence source that does not appear in the Initial Stakeholder Enumeration as a named actor. Example: a funder who operates through intermediaries, or an informal advisor whose recommendations consistently appear in decisions without attribution.
- **Proxy** - an actor who exercises another actor's stake on their behalf, whether by delegation, mandate, or structural position. Identification: the survey names an actor whose stated position or voting pattern consistently aligns with a specific external interest, and whose independent stake is insufficient to explain the alignment. Example: a national body representative whose positions track a single corporate member's agenda.
- **Intermediary** - an actor who sits between two or more stakeholders and controls the flow of information, access, or resources between them. Identification: removing this actor would sever a connection that currently exists between other stakeholders. Example: a committee chair who controls which proposals reach the full body, or a mailing list moderator who filters what the membership sees.

Every flag names the specific actor it applies to and its basis in the survey. Do not flag on inference alone.

Scan the Organization Profile, Public Record, and Outlier Signals for structural influence sources not named in the enumeration. Add each to the candidate set and screen it like the rest, applying the matching flag.

Honor any stakeholder inclusions or exclusions `{prompt}` names.

Rank all candidates by tier (3, 2, 1), within each tier by class in table order, and within each class by strength of justification.

Write to `{date}-staker-{slug}/{date}-staker-{slug}-stakeholders.md` (**scratch**). Open with a `## Unit of Analysis Decisions` section: one line per aggregation (individual folded into an institution) and per separation (individual split out), each naming the actor, its home stakeholder, and the basis. Downstream research reads this section to attribute individuals to the right stakeholder.

Then write the full screened list. Per candidate, one block:

```
#### [N]. [Actor Name]
- **Class:** [Definitive / Dominant / Dangerous / Dependent / Dormant / Discretionary / Demanding / None]
- **Power:** [present/absent] - [one-sentence justification]
- **Legitimacy:** [present/absent] - [one-sentence justification]
- **Urgency:** [present/absent] - [time sensitivity and criticality evidence, or which component fails]
- **Flags:** [hidden/proxy/intermediary - name the actor and basis; or none]
- **Rationale:** [one-line from enumeration]
```

Number blocks sequentially in ranked order. Before returning, confirm the block count matches the count you report. Return one status line naming the candidate count and file written.

</stakeholder-identification>

After the subagent completes, read the stakeholders file. Present the screened list to the user through AskQuestion for validation, additions, and removals. Screen any user addition through the same attribute tests and insert it in ranked order.

Finalize the register at 20 stakeholders. Go below 20 only when enumeration and user input yield fewer than 20 structurally distinct actors; never group distinct actors to compress. If fewer than 8 exist, proceed with what exists and flag the thin coverage in the Audit Trail. If more than 20 exist, cut to 20 in ranked order. Class None never enters the register.

**Append** the finalized register to the evidence file under the Stakeholder Register section: tier headers, one numbered line per stakeholder, numbering continuous across tiers, empty tiers omitted. After each name, one parenthetical holds the class and the flags, semicolon-separated when both appear. Omit the class on Tier 3 - the header already says Definitive. Omit the parenthetical when it would be empty:

```
### Tier 3 (Definitive)
1. [Actor Name]
2. [Actor Name] (intermediary)

### Tier 2 (Expectant)
3. [Actor Name] (Dominant)
4. [Actor Name] (Dependent; proxy)

### Tier 1 (Latent)
5. [Actor Name] (Discretionary)
```

---

All content in this file is dedicated to the public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
