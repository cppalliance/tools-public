#!/usr/bin/env python3
"""Rank open PRs across the wg21 repos and pick the one worth reviewing next.

Read-only. Shells out to `gh` (one GraphQL call per repo, plus one merged-PR
listing per repo for the area tie-break).

Tiers, highest priority first:
  1 responded   I reviewed it, the author has since replied or pushed
  2 requested   review is explicitly requested from me
  3 unreviewed  nobody has reviewed it
  4 other       reviewed by others, or I reviewed and the author is silent
Tier 4 never wins the top slot, it only fills the alternatives list.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_REPOS = ["cppalliance/wg21-website", "cppalliance/wg21-paperflow"]

# How far back to look for "areas I've worked in recently", and the weight a
# merged PR (or local commit) contributes at each age.
AFFINITY_WINDOW_DAYS = 90
AFFINITY_WEIGHTS = ((30, 1.0), (60, 0.6), (90, 0.3))

TIER_NAMES = {1: "responded", 2: "requested", 3: "unreviewed", 4: "other"}

PR_QUERY = """
query($owner:String!,$name:String!){
 repository(owner:$owner,name:$name){ pullRequests(states:OPEN,first:50,orderBy:{field:UPDATED_AT,direction:DESC}){ nodes{
   number title isDraft url createdAt updatedAt additions deletions changedFiles
   author{login}
   reviewRequests(first:20){nodes{requestedReviewer{__typename ... on User{login} ... on Team{slug}}}}
   reviews(last:30){nodes{author{login} state submittedAt}}
   commits(last:1){nodes{commit{committedDate}}}
   comments(last:20){nodes{author{login} createdAt}}
   reviewThreads(first:60){nodes{isResolved comments(last:5){nodes{author{login} createdAt}}}}
   timelineItems(last:20, itemTypes:[REVIEW_REQUESTED_EVENT]){nodes{... on ReviewRequestedEvent{createdAt requestedReviewer{... on User{login}}}}}
   files(first:100){nodes{path}} } } } }
"""


# --- shelling out ------------------------------------------------------------


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd[:3])}... failed: {proc.stderr.strip()}")
    return proc.stdout


def check_auth() -> None:
    proc = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit("gh is not authenticated. Run `gh auth login` and retry.")


def whoami() -> str:
    return run(["gh", "api", "user", "--jq", ".login"]).strip()


def fetch_open_prs(repo: str) -> list[dict]:
    owner, name = repo.split("/", 1)
    out = run(
        ["gh", "api", "graphql", "-f", f"query={PR_QUERY}", "-f", f"owner={owner}", "-f", f"name={name}"]
    )
    payload = json.loads(out)
    if payload.get("errors"):
        raise RuntimeError(f"{repo}: {payload['errors']}")
    return payload["data"]["repository"]["pullRequests"]["nodes"]


# --- time helpers ------------------------------------------------------------


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def age_days(ts: datetime | None, now: datetime) -> float | None:
    return None if ts is None else (now - ts).total_seconds() / 86400


def humanize_age(days: float | None) -> str:
    if days is None:
        return "unknown"
    if days < 1:
        return "today"
    if days < 2:
        return "1 day"
    if days < 14:
        return f"{int(days)} days"
    return f"{int(days / 7)} weeks"


# --- area affinity -----------------------------------------------------------


def path_area(path: str) -> str | None:
    """Bucket a file path into a coarse area label, or None if it carries no signal.

    Root-level files (CLAUDE.md, .gitignore, pyproject.toml, lockfiles) churn in
    almost every PR, so counting them as an area makes everything look related to
    everything. Test dirs fold into the area they test.
    """
    parts = Path(path).parts
    if not parts or len(parts) == 1:
        return None  # a file at the repo root
    if parts[0] == "packages" and len(parts) > 1:
        return parts[1]  # paperflow: assay, agora, tomd, mailing, pipeline, ...
    if parts[0] == "wg21_site":
        # wg21_site/mailing/... -> wg21_site/mailing; wg21_site/views.py -> wg21_site
        sub = parts[1] if len(parts) > 2 else None
        return f"wg21_site/{sub}" if sub and sub not in ("tests", "migrations") else "wg21_site"
    if parts[0] == "templates" and len(parts) > 2:
        return f"templates/{parts[1]}"
    return parts[0]


def areas_of(paths) -> set[str]:
    return {area for area in (path_area(p) for p in paths) if area}


def recency_weight(days: float) -> float:
    for cutoff, weight in AFFINITY_WEIGHTS:
        if days <= cutoff:
            return weight
    return 0.0


def my_areas(repos: list[str], now: datetime, quiet: bool) -> dict[str, dict[str, float]]:
    """Areas I've touched recently per repo, recency-weighted, each repo normalized to 1.0.

    Normalization is deliberately per repo, not global. Affinity breaks ties
    *within* a tier, and that tier mixes PRs from every repo. A global scale
    would just mean "whichever repo I committed to most this month wins", which
    is not the question being asked.
    """
    since = (now - timedelta(days=AFFINITY_WINDOW_DAYS)).date().isoformat()
    weights: dict[str, dict[str, float]] = {repo: {} for repo in repos}
    local_repo = detect_local_repo(repos)

    def add(repo: str, paths, days: float) -> None:
        weight = recency_weight(days)
        if weight <= 0:
            return
        for area in areas_of(paths):
            weights[repo][area] = weights[repo].get(area, 0.0) + weight

    for repo in repos:
        try:
            out = run(
                # fmt: off
                ["gh", "pr", "list", "--repo", repo, "--author", "@me", "--state", "merged",
                 "--search", f"merged:>={since}", "--limit", "50", "--json", "number,mergedAt,files"],
                # fmt: on
            )
        except RuntimeError as exc:
            if not quiet:
                print(f"note: no merge history for {repo} ({exc})", file=sys.stderr)
            out = "[]"
        for pr in json.loads(out):
            merged = parse_ts(pr.get("mergedAt"))
            if merged is None:
                continue
            add(repo, [f["path"] for f in pr.get("files") or []], age_days(merged, now))
        if repo == local_repo:
            add_local_commits(repo, since, now, add)

    return {
        repo: {area: round(w / max(areas.values()), 4) for area, w in areas.items()}
        for repo, areas in weights.items()
        if areas
    }


def detect_local_repo(repos: list[str]) -> str | None:
    """Which target repo, if any, the current directory is a checkout of.

    Matched on the repo name rather than owner/name, since this checkout's
    `origin` is usually a personal fork.
    """
    try:
        remotes = run(["git", "remote", "-v"])
    except RuntimeError:
        return None
    for repo in repos:
        name = repo.split("/", 1)[1]
        if f"/{name}.git" in remotes or f"/{name} " in remotes:
            return repo
    return None


def add_local_commits(repo: str, since: str, now: datetime, add) -> None:
    """Fold in unmerged local work from the current checkout.

    Merged PRs miss whatever is still sitting on a feature branch, which is
    usually the most recent signal there is.
    """
    try:
        log = run(["git", "log", f"--since={since}", "--name-only", "--pretty=format:@@%aI"])
    except RuntimeError:
        return
    stamp: datetime | None = None
    paths: list[str] = []
    for line in log.splitlines():
        if line.startswith("@@"):
            if stamp is not None and paths:
                add(repo, paths, age_days(stamp, now))
            stamp, paths = parse_ts(line[2:].strip()), []
        elif line.strip():
            paths.append(line.strip())
    if stamp is not None and paths:
        add(repo, paths, age_days(stamp, now))


def affinity(pr_paths: list[str], areas: dict[str, float]) -> tuple[float, list[str]]:
    """Weighted overlap between a PR's areas and mine, in 0..1."""
    pr_areas = [area for area in (path_area(p) for p in pr_paths) if area]
    if not pr_areas or not areas:
        return 0.0, []
    counts: dict[str, int] = {}
    for area in pr_areas:
        counts[area] = counts.get(area, 0) + 1
    total = len(pr_areas)
    score = sum(areas.get(area, 0.0) * (n / total) for area, n in counts.items())
    matched = sorted((a for a in counts if a in areas), key=lambda a: -areas[a])
    return round(score, 4), matched


# --- classification ----------------------------------------------------------


def requested_reviewers(pr: dict) -> list[str]:
    out = []
    for node in pr["reviewRequests"]["nodes"]:
        reviewer = node.get("requestedReviewer") or {}
        if reviewer.get("__typename") == "User" and reviewer.get("login"):
            out.append(reviewer["login"])
    return out


def author_activity_at(pr: dict, author: str) -> datetime | None:
    """Latest sign of life from the PR author, across all four event streams.

    Authors reply in different places: a push, an issue comment, a review-thread
    reply, or a PR-level review with state COMMENTED. All four count.
    """
    stamps: list[datetime] = []
    for node in pr["commits"]["nodes"]:
        stamps.append(parse_ts(node["commit"]["committedDate"]))
    for node in pr["comments"]["nodes"]:
        if (node.get("author") or {}).get("login") == author:
            stamps.append(parse_ts(node["createdAt"]))
    for node in pr["reviews"]["nodes"]:
        if (node.get("author") or {}).get("login") == author:
            stamps.append(parse_ts(node["submittedAt"]))
    for thread in pr["reviewThreads"]["nodes"]:
        for node in thread["comments"]["nodes"]:
            if (node.get("author") or {}).get("login") == author:
                stamps.append(parse_ts(node["createdAt"]))
    stamps = [s for s in stamps if s is not None]
    return max(stamps) if stamps else None


def my_last_review(pr: dict, me: str) -> dict | None:
    mine = [r for r in pr["reviews"]["nodes"] if (r.get("author") or {}).get("login") == me]
    return mine[-1] if mine else None


def requested_from_me_at(pr: dict, me: str) -> datetime | None:
    stamps = [
        parse_ts(node["createdAt"])
        for node in pr["timelineItems"]["nodes"]
        if (node.get("requestedReviewer") or {}).get("login") == me
    ]
    return max(stamps) if stamps else None


def classify(pr: dict, me: str, include_drafts: bool) -> dict | None:
    """Return a candidate dict, or None if the PR should be dropped."""
    author = (pr.get("author") or {}).get("login")
    if author == me:
        return None  # you cannot review your own PR

    reviewers = requested_reviewers(pr)
    requested = me in reviewers
    last_review = my_last_review(pr, me)

    if pr["isDraft"] and not include_drafts and not (requested or last_review):
        return None

    responded_at = author_activity_at(pr, author)
    my_review_at = parse_ts(last_review["submittedAt"]) if last_review else None
    author_moved = bool(my_review_at and responded_at and responded_at > my_review_at)

    if last_review and last_review["state"] == "APPROVED" and not author_moved:
        return None  # already approved and nothing has changed since

    if author_moved:
        tier, waiting_since = 1, responded_at
    elif requested:
        tier = 2
        waiting_since = requested_from_me_at(pr, me) or parse_ts(pr["createdAt"])
    elif not pr["reviews"]["nodes"]:
        tier, waiting_since = 3, parse_ts(pr["createdAt"])
    else:
        tier, waiting_since = 4, parse_ts(pr["updatedAt"])

    return {
        "number": pr["number"],
        "title": pr["title"],
        "url": pr["url"],
        "author": author,
        "is_draft": pr["isDraft"],
        "tier": tier,
        "tier_name": TIER_NAMES[tier],
        "waiting_since": waiting_since.isoformat() if waiting_since else None,
        "changed_files": pr["changedFiles"],
        "additions": pr["additions"],
        "deletions": pr["deletions"],
        "unresolved_threads": sum(1 for t in pr["reviewThreads"]["nodes"] if not t["isResolved"]),
        "requested_from_me": requested,
        "my_last_review": (
            {"state": last_review["state"], "at": last_review["submittedAt"]} if last_review else None
        ),
        "author_activity_at": responded_at.isoformat() if responded_at else None,
        "other_reviewers": sorted(
            {
                (r.get("author") or {}).get("login")
                for r in pr["reviews"]["nodes"]
                if (r.get("author") or {}).get("login") not in (me, author, None)
            }
        ),
        "paths": [f["path"] for f in pr["files"]["nodes"]],  # capped at 100 by the query
    }


def reason_for(cand: dict) -> str:
    if cand["tier"] == 1:
        state = cand["my_last_review"]["state"].replace("_", " ").lower()
        return (
            f"you left {state} on {cand['my_last_review']['at'][:10]}, "
            f"{cand['author']} has since responded ({cand['author_activity_at'][:10]})"
        )
    if cand["tier"] == 2:
        return f"{cand['author']} requested your review, no review from you yet"
    if cand["tier"] == 3:
        return "nobody has reviewed it yet"
    if cand["my_last_review"]:
        return f"you reviewed it on {cand['my_last_review']['at'][:10]}, no response from the author since"
    return f"reviewed by {', '.join(cand['other_reviewers']) or 'others'}, not by you"


# --- main --------------------------------------------------------------------


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    # Drafts are always sorted below review-ready PRs of the same tier, flag or not.
    parser.add_argument(
        "--include-drafts", action="store_true", help="also scan drafts you have no involvement with"
    )
    parser.add_argument("--json", dest="as_json", action="store_true", help="emit structured output")
    parser.add_argument("--explain", action="store_true", help="show the derived area weights")
    parser.add_argument("--limit", type=int, default=6, help="how many candidates to return")
    # Positional `repo=owner/name` args add repos on top of the defaults.
    parser.add_argument("extra", nargs="*", help="repo=owner/name to scan in addition to the defaults")
    args = parser.parse_args(argv)
    args.repos = list(DEFAULT_REPOS)
    for item in args.extra:
        if item.startswith("repo="):
            repo = item.split("=", 1)[1]
            if repo not in args.repos:
                args.repos.append(repo)
        else:
            parser.error(f"unrecognized argument: {item}")
    return args


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    check_auth()
    me = whoami()
    now = datetime.now(timezone.utc)

    areas = my_areas(args.repos, now, quiet=args.as_json)

    candidates = []
    for repo in args.repos:
        for pr in fetch_open_prs(repo):
            cand = classify(pr, me, args.include_drafts)
            if cand is None:
                continue
            cand["repo"] = repo
            cand["ref"] = f"{repo}#{cand['number']}"
            cand["affinity"], cand["matched_areas"] = affinity(cand.pop("paths"), areas.get(repo, {}))
            cand["waiting"] = humanize_age(age_days(parse_ts(cand["waiting_since"]), now))
            cand["reason"] = reason_for(cand)
            candidates.append(cand)

    candidates.sort(
        key=lambda c: (
            c["tier"],
            c["is_draft"],  # a draft never outranks a review-ready PR in the same tier
            -c["affinity"],
            c["waiting_since"] or "",  # oldest wait first, so nothing rots
            c["changed_files"],  # a quick win breaks a true tie
        )
    )
    top = candidates[: args.limit]

    if args.explain:
        # stderr, so this survives --json without corrupting the payload on stdout
        for repo in args.repos:
            print(f"Recent areas in {repo} (weight):", file=sys.stderr)
            ranked = sorted(areas.get(repo, {}).items(), key=lambda kv: -kv[1])[:8]
            for area, weight in ranked:
                print(f"  {weight:>5.2f}  {area}", file=sys.stderr)
            if not ranked:
                print("  (no recent work)", file=sys.stderr)
            print(file=sys.stderr)

    if args.as_json:
        print(
            json.dumps(
                {
                    "me": me,
                    "repos": args.repos,
                    "generated_at": now.isoformat(),
                    "area_weights": areas,
                    "pick": next((c for c in top if c["tier"] < 4), None),
                    "candidates": top,
                },
                indent=2,
            )
        )
        return 0

    if not top:
        print("No open PRs are waiting on you. The queue is clear.")
        return 0

    for i, c in enumerate(top):
        marker = "->" if i == 0 and c["tier"] < 4 else "  "
        draft = " (draft)" if c["is_draft"] else ""
        print(f"{marker} [{c['tier']} {c['tier_name']}] {c['ref']}{draft}  {c['title']}")
        print(f"     {c['url']}")
        print(f"     {c['reason']}; waiting {c['waiting']}")
        print(
            f"     {c['changed_files']} files, +{c['additions']}/-{c['deletions']}, "
            f"affinity {c['affinity']:.2f} {c['matched_areas'][:3]}"
        )
        print()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except RuntimeError as exc:
        sys.exit(str(exc))
