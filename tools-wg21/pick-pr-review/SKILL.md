---
name: pick-pr-review
description: Pick the single highest-value open PR to review across the wg21 repos
disable-model-invocation: true
argument-hint: "[repo=owner/name] [--include-drafts] [--explain]"
---

# Pick a PR to Review

Scan the open PRs in `cppalliance/wg21-website` and `cppalliance/wg21-paperflow`
and recommend **exactly one** to review next. The point is to remove the choice,
not to hand back a queue.

Requires the `gh` CLI, authenticated as the reviewer (`gh auth login`). The
script resolves the current user itself, so it needs no per-person config.

## 1. Run the triage script

The script sits next to this SKILL.md. Claude Code exposes that directory as
`${CLAUDE_SKILL_DIR}`; in any other agent, use the directory this SKILL.md was
loaded from (for a user-level install, `~/.cursor/skills/pick-pr-review/`).

```bash
python3 "${CLAUDE_SKILL_DIR}/triage_prs.py" $ARGUMENTS --json
```

It is read-only: it makes one GraphQL call per repo plus one merged-PR listing,
and writes nothing. `$ARGUMENTS` may add `repo=owner/name` (scans that repo on
top of the two defaults), `--include-drafts`, or `--explain` (dumps the derived
area weights to stderr).

The script ranks by tier, then breaks ties on how close the PR sits to the areas
the user has worked in recently:

| Tier | Meaning |
|---|---|
| 1 `responded` | The user reviewed it and the author has since replied or pushed. The ball is back in their court. |
| 2 `requested` | Review explicitly requested from the user, no review from them yet. |
| 3 `unreviewed` | Nobody has reviewed it. |
| 4 `other` | Reviewed by someone else, or the user reviewed and the author has gone quiet. |

Already excluded: the user's own PRs, PRs they approved with no changes since,
and drafts they have no involvement with. Tier 4 never wins the top slot, so
`pick` is null when only tier 4 remains.

An unsubmitted draft review (the `PENDING` state step 5 leaves behind) is not a
review anyone else can see, so it does not set a tier. It surfaces instead as
`my_pending_review` on the candidate, and it means review work is sitting there
unsent.

## 2. Report

Keep it to a handful of lines. No preamble, no tables, no em dashes.

- **The pick**: `owner/repo#N`, the title, the direct URL on its own line, the
  one-line reason from `reason`, and the diff size. If it is a draft, say so.
- **1-2 alternatives**: one line each, with their tier reason, so skipping the
  top pick is cheap.
- If `pick` is null, say the queue is clear. Do not promote a tier-4 PR into the
  top slot to have something to recommend.
- **Unsubmitted drafts**: any candidate with `my_pending_review` gets its own
  line, wherever it ranks, naming the PR and the date the draft was started.
  Those comments are invisible until the user submits them, so an old one is
  review work already done and going to waste. Say that even when the top pick
  is something else.

## 3. Offer, do not start

End by offering to review the pick. **Wait for confirmation.** The user asked for
a recommendation, and pulling a large diff into context uninvited is not that.

## 4. On acceptance, review it

```bash
gh pr view <N> --repo <repo> --json title,body,files
gh pr diff <N> --repo <repo>
```

For a **tier 1** pick, read the prior exchange first, because the question is not
"is this code good" but "did the author's response actually address what was
raised":

```bash
gh api repos/<repo>/pulls/<N>/comments --jq '.[] | "\(.user.login) \(.path):\(.line)\n\(.body)\n"'
gh pr view <N> --repo <repo> --json reviews --jq '.reviews[] | "\(.author.login) \(.state)\n\(.body)\n"'
```

Present the findings in chat first and get agreement on them.

## 5. Post as a pending review, never a submitted one

The human submits the review, not the agent. Post the comments as a **pending
draft** so they can be edited and sent from the GitHub UI.

Write the comments to a JSON file:

```json
[
  { "path": "relative/path.py", "line": 42, "side": "RIGHT", "body": "Comment text." }
]
```

`side` is `RIGHT` for added or changed lines, `LEFT` for removed ones. Line
numbers must land on lines present in the diff, otherwise the API returns 422.

```bash
gh api repos/<repo>/pulls/<N>/reviews --method POST \
  -f commit_id="$(gh pr view <N> --repo <repo> --json headRefOid --jq .headRefOid)" \
  -f body="<summary or empty>" \
  -F comments=@comments.json \
  --jq '.state, .html_url'
```

**HARD RULE: no `event` field in that payload.** Any value (`COMMENT`,
`APPROVE`, `REQUEST_CHANGES`) submits the review immediately, the comments go
live, and a `COMMENTED` review cannot be dismissed. The call must return
`state: PENDING`. If it returns anything else, say so immediately: the comments
are now public and can only be deleted one at a time.

Report the returned `html_url` and note it is a draft awaiting their submission.
