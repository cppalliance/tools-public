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

This step launches one subagent per numbered template section to collect evidence, then assembles the sections into a single Evidence File. The merged Evidence File is `{date}-staker-{slug}/{date}-staker-{slug}-evidence.md` (**scratch**). Each subagent writes to the file evidence-N.md where N is its assigned section number (1-11).

Launch eleven subagents (model tier: **parent**), one per numbered section of the template. Each subagent receives these instructions verbatim, with the template reduced to the frontmatter block, the `# {organization}` heading, and only its assigned section. Do NOT paraphrase. Do NOT add anything. Do NOT augment from your training data. USE ONLY THIS:

Use WebSearch to fill in this exact template in the file. Follow source chains: when a result names a document, paper, filing, or primary record not yet in your notes, search for it directly.

Search your assigned section independently and exhaustively: at least 2-3 different query angles. After each search pass, note what's still missing and search again for gaps. Do not conclude the section until claims have primary sources or you've exhausted available search strategies.

```
---
date:
model:
domain:
---

# {organization}

## 1. Organization Profile

founding, stated mission, structure, governance, funding model, and Blau-Scott classification (mutual-benefit, business, service, or commonweal). Identify any adjacent support entities (foundations, fiscal sponsors, allied nonprofits) with their legal form, founding date, leadership overlap with the organization, and funding sources. Quote specific financial metrics where publicly documented: revenue, expenses, compensation, membership fees, sponsor tiers, event costs, and per-unit pricing of the organization's output.

## 2. Actual Purpose

what the organization observably does and what drives its resource acquisition. If stated and actual purpose align, note it. If they diverge, note the divergence as governance context, not as the dominant pathology.

## 3. Domain Primer

three to five structural facts a reader needs to understand the sector

## 4. Domain Landscape

search broadly: position, competitors, dependencies, peer bodies for benchmarking, trend, and anything structurally significant the searches reveal beyond these. Where available, report cohort metrics: population, growth rate, and survey penetration for any measurable group - the organization's constituency, its output's user base, its competitors, and its workforce.

## 5. Public Record

press, filings, controversy, reputation. Search for named departures, public resignations, or burnout testimony by former participants; individuals removed, expelled, or banned from participation and the circumstances; governance reform campaigns and their outcomes; code-of-conduct or safety incidents at meetings or affiliated conferences; and fiscal or governance disputes among the organization's adjacent entities. Search for any external regulatory or government pressure campaigns directed at the organization or its domain. If `{prompt}` names a specific concern, also search whether the organization has an existing mechanism for that class of concern (ombudsman, grievance process, code of conduct enforcement, appeals process) and whether it has been invoked. No concern named is valid - skip it.

## 6. Outlier Signals

identify the organization's peer class yourself (peer bodies serving a comparable function in the sector), then benchmark against it

## 7. Base-peer

establish the peer baseline independently, then treat the organization as normal absent evidence; finding nothing is valid and leaves the default standing.

## 8. Concrete

leadership tenure and transitions; governing-body selection method; largest funder, customer, or sponsor share; share of effort sustaining itself versus producing stated output; membership trend; leadership careers overlapping funders, regulators, customers, or suppliers; role concentration - whether any individual holds concurrent leadership positions across the organization and its adjacent entities. Specific facts only, benchmarked where a standard peer benchmark already exists - never synthesize one.

## 9. Qualitative

documented descriptions of the organization as unusual or non-standard - by press, researchers, members, or competitors - on dimensions the concrete facts don't reach. Search for academic or organizational-behavior analyses of the organization as a case study.

## 10. Domain-Specific Vulnerabilities

sector-specific risks with sources. Include: parent-body or supply-chain dependencies that create friction the organization cannot control; binding constraints from implementers, adopters, or certifiers whose capacity gates the organization's output; sustainability risks from volunteer or single-maintainer concentration; and single-points-of-failure in infrastructure maintained by or for the organization (wikis, document repositories, mailing list archives, build systems).

## 11. Initial Stakeholder Enumeration

a wide-net list built by snowball logic (who funds, governs, uses, competes with, or depends on the organization), with a one-line rationale for each inclusion. Cast the net beyond direct participants: include tool and compliance vendors whose products depend on the organization's output, academic and research contributors, regulatory or government bodies exerting external pressure, and the end-user community that consumes the output but does not participate in governance.
```

Return one status line containing the output filename and number of lines when complete.

When all subagents have finished, assemble the Evidence File by concatenating sections 1 through 11 from evidence-1.md through evidence-11.md in order, deduplicating any claims that repeat across sections.

---

All content in this file is dedicated to the public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
