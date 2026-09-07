---
description: Planning tool that traces technical debt to new work through repository history, diffs, code, and design records, then leaves a self-contained removal plan.
---

# The Debt Collector

A clean diff can shake your hand while hiding a knife behind its back, *capisce*. One new function looks innocent. Four commits later, its parameter tuple has cousins in three modules. Shared state says it is only visiting, then becomes a *made man* with dependents throughout the family. A compatibility shim invokes *omerta* and refuses to name the day it will retire. Meanwhile, every plan swears the arrangement is temporary, and *cosa nostro* quietly becomes the permanent shape of the system. Nothing fails today, which is how the debt survives. Tomorrow, every caller votes, every persisted byte has seniority, and every wire contract tells refactoring to *va fa Napoli*. The Debt Collector reads beyond the friendly subject lines. It follows the pattern across the whole ledger until coincidence confesses.

The tool accepts a repository, single commit, or commit range and identifies the new crew on the street. It binds every full commit message into one scratch dossier and gives it to a subagent that knows how to follow aliases, plans, deferrals, and architectural obligations. The corresponding design records provide testimony, while the actual diffs and source establish the facts. Reversible debts are paid immediately and entered in the ledger with their consequences. Expensive architecture choices go upstairs to the user in chat. Then the Collector slides one final document across the table: an offer the model cannot refuse, containing the complete plan for removing the debt.

![The Debt Collector](images/debt-collector-1.jpg)

## Plan Mode

Enter Plan mode through the host mechanism before analysis. If Plan mode is unavailable or the switch fails, state the cost in one sentence and stop.

## Scope and Evidence

Accept a repository path and, optionally, one commit or revision range. Read the repository without modifying it.

Resolve an explicit commit or range exactly. For a repository-only request, compare the tracked upstream with the current branch and worktree. If no upstream exists, choose the most defensible baseline and record why. Before drafting findings, state the baseline, endpoint, target commits, worktree inclusion, available design records, and analysis limits. Stop concisely if the repository or requested revision cannot be read. If the target contains no new work, still produce the required plan and state that no removal work is proposed.

Create one local scratch file containing every complete commit message in reachable history through the endpoint, in chronological order. Preserve multiline bodies and trailers exactly. Add enough separate metadata to identify each commit and clearly mark commits in the target set. Keep history, diffs, source, and detailed findings file-backed rather than returning their payloads to the main context.

Use commit messages as evidence of intent and as a navigation index, never as prose to rewrite or grade. Follow references to affected code, design plans, queues, aliases, architectural obligations, and explicit deferrals.

When `vibe/` exists, discover `archdoc.md` and `archdoc-next.md` and treat them as read-only evidence. Resolve `Plan:` trailers in target commits to their plan files. Include the active plan when uncommitted target work belongs to it. Record missing or malformed references without inventing their contents.

![The Collection](images/debt-collector-2.jpg)

## Analysis and Judgment

Dispatch an isolated analysis subagent with this tool's path, the bare tag name `debt-analysis-instructions`, the repository path, resolved scope, commit-log scratch path, and discovered design-record paths. The subagent must locate exactly two lines matching the anchored pattern `^</?debt-analysis-instructions>$`, in opening-then-closing order, and read only that inclusive block. Do not paste the block or repository payloads into its dispatch. If evidence volume requires partitioning, make additional isolated calls with the same instruction reference and non-overlapping scopes, then merge their findings.

<debt-analysis-instructions>

Analyze technical debt attributable to the resolved target work. Choose how to examine the complete commit-log scratch file according to its size and contents. Use message content to reconstruct intent and direct inspection, but do not rewrite or grade commit messages.

Inspect the actual target diffs and current code before accepting historical claims. Read the supplied design records as evidence only. Classify each candidate as introduced, worsened, exposed, or unrelated pre-existing debt. Exclude unrelated debt from remediation.

For every retained finding, record a stable debt ID, classification, supporting commits and paths, message or design evidence, observed code facts, consequence, reversal cost, dependencies, plausible remediations, verification, and uncertainty. Distinguish facts from inference. Findings must be detailed enough for a fresh context to synthesize a removal plan.

Write detailed findings to a local scratch file. Return no raw repository content and no finding prose. Return only `done` or `blocked`, finding counts by classification, the findings path, and any analysis limit, within 150 words.

</debt-analysis-instructions>

Read the detailed findings from their paths and reconcile overlaps. Actual diffs and current code outrank commit-message claims. Retain only debt introduced, worsened, or exposed by the target work.

Choose reversible remediations autonomously. For each choice, record the selected remedy, rejected alternatives, resulting tradeoff, and verification. Do not choose a hard-to-reverse change affecting a public interface, persisted or wire format, component ownership, dependency direction, or trust boundary. Raise that choice in ordinary chat with its evidence, options, and consequences, never through a question tool, and wait for the user.

![The Settlement](images/debt-collector-3.jpg)

## Removal Plan

Write one self-contained plan that a fresh implementation context can execute without this conversation or the scratch files. Tie every proposed change and check to a retained debt ID. Cite repository paths and revisions as evidence. Do not modify source code, execute the plan, catalog unrelated legacy defects, or update architecture records.

Use exactly these six H2 sections:

```markdown
## Product Requirements

- Scope and target work
- Cleanup goals and non-goals
- Success criteria

## Debt Inventory

- Stable debt IDs with evidence, relationship to target work, impact, reversal cost, and target state

## Technical Design

- Consequential module, interface, data, protocol, security, failure, and lifecycle changes required by the retained debt

## Testing Plan

- Focused, integration, regression, architecture, and exit checks tied to debt IDs

## Decision Record

- Reversible decisions and consequences
- User-resolved architecture choices
- Rejected alternatives, assumptions, and risks

## Execution Instructions

- Unordered work items tied to debt IDs, with dependencies, verification expectations, and explicit exclusions
```

## Restated

Resolve the target, preserve the full ledger, corroborate intent against code, collect only attributable debt, settle reversible choices, escalate consequential architecture in chat, and leave the complete removal plan.

![The Final Account](images/debt-collector-4.jpg)

All content in this file is dedicated to the public domain under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).

*2026-09-07 - GPT-5.6 Sol (Cursor agent)*
