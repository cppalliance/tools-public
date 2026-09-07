"""Acceptance checks for the Debt Collector prompt protocol."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "coding" / "debt-collector.md"


def _git(repository: Path, *arguments: str) -> str:
    environment = os.environ.copy()
    environment.update(
        {
            "GIT_AUTHOR_NAME": "Debt Collector Tests",
            "GIT_AUTHOR_EMAIL": "debt-collector@example.invalid",
            "GIT_COMMITTER_NAME": "Debt Collector Tests",
            "GIT_COMMITTER_EMAIL": "debt-collector@example.invalid",
        }
    )
    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        encoding="utf-8",
        env=environment,
    )
    return completed.stdout


def _init_repository(path: Path) -> Path:
    path.mkdir()
    subprocess.run(
        ["git", "init", "-b", "main", str(path)],
        check=True,
        capture_output=True,
    )
    (path / "tracked.txt").write_text("baseline\n", encoding="utf-8")
    _git(path, "add", "tracked.txt")
    _git(path, "commit", "-m", "Establish baseline")
    return path


def _commit(repository: Path, subject: str, body: str, content: str) -> str:
    tracked = repository / "tracked.txt"
    tracked.write_text(tracked.read_text(encoding="utf-8") + content, encoding="utf-8")
    _git(repository, "add", "tracked.txt")
    _git(repository, "commit", "-m", subject, "-m", body)
    return _git(repository, "rev-parse", "HEAD").strip()


@dataclass(frozen=True)
class ResolvedScope:
    baseline: str
    endpoint: str
    target_commits: tuple[str, ...]
    worktree_included: bool
    complete_messages: tuple[tuple[str, str], ...]
    design_records: tuple[str, ...]
    plan_paths: tuple[str, ...]
    missing_plan_references: tuple[str, ...]


def _revisions(repository: Path, expression: str) -> tuple[str, ...]:
    output = _git(repository, "rev-list", "--reverse", expression)
    return tuple(line for line in output.splitlines() if line)


def _resolve_scope(
    repository: Path,
    revision: str | None = None,
    active_plan: str | None = None,
) -> ResolvedScope:
    if revision is None:
        baseline = _git(repository, "rev-parse", "@{upstream}").strip()
        endpoint = _git(repository, "rev-parse", "HEAD").strip()
        targets = _revisions(repository, f"{baseline}..{endpoint}")
        worktree_included = bool(_git(repository, "status", "--porcelain"))
    elif ".." in revision:
        baseline_name, endpoint_name = revision.split("..", 1)
        baseline = _git(repository, "rev-parse", baseline_name).strip()
        endpoint = _git(repository, "rev-parse", endpoint_name).strip()
        targets = _revisions(repository, f"{baseline}..{endpoint}")
        worktree_included = False
    else:
        endpoint = _git(repository, "rev-parse", revision).strip()
        baseline = _git(repository, "rev-parse", f"{endpoint}^").strip()
        targets = (endpoint,)
        worktree_included = False

    history = _revisions(repository, endpoint)
    complete_messages = tuple(
        (commit, _git(repository, "show", "-s", "--format=%B", commit))
        for commit in history
    )

    design_records = tuple(
        candidate.as_posix()
        for candidate in (Path("vibe/archdoc.md"), Path("vibe/archdoc-next.md"))
        if (repository / candidate).is_file()
    )
    referenced_plans: list[str] = []
    missing_plans: list[str] = []
    for commit in targets:
        for line in _git(repository, "show", "-s", "--format=%B", commit).splitlines():
            if not line.startswith("Plan:"):
                continue
            reference = line.removeprefix("Plan:").strip()
            if (repository / reference).is_file():
                referenced_plans.append(reference)
            else:
                missing_plans.append(reference)
    if active_plan is not None and worktree_included:
        referenced_plans.append(active_plan)

    return ResolvedScope(
        baseline=baseline,
        endpoint=endpoint,
        target_commits=targets,
        worktree_included=worktree_included,
        complete_messages=complete_messages,
        design_records=design_records,
        plan_paths=tuple(referenced_plans),
        missing_plan_references=tuple(missing_plans),
    )


def _write(repository: Path, relative_path: str, content: str) -> None:
    path = repository / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_repository_only_scope_includes_branch_worktree_and_design_records(
    tmp_path: Path,
) -> None:
    repository = _init_repository(tmp_path / "repository")
    remote = tmp_path / "origin.git"
    subprocess.run(
        ["git", "init", "--bare", str(remote)],
        check=True,
        capture_output=True,
    )
    _git(repository, "remote", "add", "origin", str(remote))
    _git(repository, "push", "-u", "origin", "main")
    upstream = _git(repository, "rev-parse", "@{upstream}").strip()

    _write(repository, "vibe/archdoc.md", "# Current architecture\n")
    _write(repository, "vibe/archdoc-next.md", "# Next architecture\n")
    _write(repository, "vibe/target.plan.md", "# Target plan\n")
    _git(repository, "add", "vibe")
    target = _commit(
        repository,
        "Add target behavior",
        "Keep this multiline rationale intact.\n\nPlan: vibe/target.plan.md",
        "target\n",
    )
    _write(repository, ".cursor/plans/active.plan.md", "# Active plan\n")
    _write(repository, "working.txt", "uncommitted target work\n")

    scope = _resolve_scope(
        repository,
        active_plan=".cursor/plans/active.plan.md",
    )

    assert scope.baseline == upstream
    assert scope.endpoint == target
    assert scope.target_commits == (target,)
    assert scope.worktree_included
    assert scope.design_records == ("vibe/archdoc.md", "vibe/archdoc-next.md")
    assert scope.plan_paths == (
        "vibe/target.plan.md",
        ".cursor/plans/active.plan.md",
    )
    assert scope.complete_messages[-1][1] == _git(
        repository, "show", "-s", "--format=%B", target
    )


def test_single_commit_scope_stops_history_at_requested_endpoint(tmp_path: Path) -> None:
    repository = _init_repository(tmp_path / "repository")
    baseline = _git(repository, "rev-parse", "HEAD").strip()
    target = _commit(
        repository,
        "Implement one change",
        "First body line.\nSecond body line.\n\nReviewed-by: Example",
        "target\n",
    )
    later = _commit(repository, "Later unrelated work", "Not in scope.", "later\n")

    scope = _resolve_scope(repository, target)

    assert scope.baseline == baseline
    assert scope.endpoint == target
    assert scope.target_commits == (target,)
    assert tuple(commit for commit, _ in scope.complete_messages) == (baseline, target)
    assert later not in tuple(commit for commit, _ in scope.complete_messages)
    assert "First body line.\nSecond body line." in scope.complete_messages[-1][1]
    assert "Reviewed-by: Example" in scope.complete_messages[-1][1]
    assert scope.design_records == ()


def test_explicit_range_marks_only_range_and_records_missing_plan(
    tmp_path: Path,
) -> None:
    repository = _init_repository(tmp_path / "repository")
    baseline = _git(repository, "rev-parse", "HEAD").strip()
    first = _commit(
        repository,
        "First range commit",
        "Range body one.\n\nPlan: vibe/missing.plan.md",
        "first\n",
    )
    _write(repository, "vibe/archdoc-next.md", "# Proposed architecture\n")
    second = _commit(
        repository,
        "Second range commit",
        "Range body two.\n\nQueue: cleanup",
        "second\n",
    )

    scope = _resolve_scope(repository, f"{baseline}..{second}")

    assert scope.baseline == baseline
    assert scope.endpoint == second
    assert scope.target_commits == (first, second)
    assert tuple(commit for commit, _ in scope.complete_messages) == (
        baseline,
        first,
        second,
    )
    assert scope.design_records == ("vibe/archdoc-next.md",)
    assert scope.plan_paths == ()
    assert scope.missing_plan_references == ("vibe/missing.plan.md",)


def test_prompt_has_structural_and_bounded_dispatch_guards() -> None:
    text = TOOL.read_text(encoding="utf-8")
    lines = text.splitlines()

    assert lines.count("<debt-analysis-instructions>") == 1
    assert lines.count("</debt-analysis-instructions>") == 1
    assert lines.index("<debt-analysis-instructions>") < lines.index(
        "</debt-analysis-instructions>"
    )
    assert "Resolve an explicit commit or range exactly." in text
    assert "compare the tracked upstream with the current branch and worktree" in text
    assert "Preserve multiline bodies and trailers exactly." in text
    assert "treat them as read-only evidence" in text
    assert "Record missing or malformed references without inventing their contents." in text
    assert "the bare tag name `debt-analysis-instructions`" in text
    assert "read only that inclusive block" in text
    assert "Do not paste the block or repository payloads into its dispatch." in text
    assert "never through a question tool" in text

    template = text.split("```markdown", 1)[1].split("```", 1)[0]
    required_sections = (
        "## Product Requirements",
        "## Debt Inventory",
        "## Technical Design",
        "## Testing Plan",
        "## Decision Record",
        "## Execution Instructions",
    )
    assert tuple(
        line for line in template.splitlines() if line.startswith("## ")
    ) == required_sections
