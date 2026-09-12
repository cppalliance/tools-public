#!/usr/bin/env python3
"""writer.py — Standalone novelist chapter writer.

Reads a story bible, extracts exactly what each chapter needs,
calls the Anthropic API, writes chapters, assembles the manuscript.
"""

import argparse
import json
import logging
import os
import re
import shutil
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from lib.bible import (
    Bible, Chapter,
    BibleParseError, parse_bible, to_dict,
)

# ---------------------------------------------------------------------------
# Model Configuration
# ---------------------------------------------------------------------------

@dataclass
class AttemptConfig:
    thinking: dict
    extra_kwargs: dict = field(default_factory=dict)
    label: str = ""


@dataclass
class ModelConfig:
    model: str
    max_tokens: int
    attempts: list[AttemptConfig]
    verify_kwargs: dict = field(default_factory=dict)


def _configure_opus_46(model: str, chapter: "Chapter") -> ModelConfig:
    multipliers = [6.0, 4.5, 3.0]
    attempts = []
    for mult in multipliers:
        budget = max(1_024, int(chapter.target * mult))
        attempts.append(AttemptConfig(
            thinking={"type": "enabled", "budget_tokens": budget},
            label=f"thinking_budget={budget:,}",
        ))
    return ModelConfig(
        model=model,
        max_tokens=128_000,
        attempts=attempts,
        verify_kwargs={
            "max_tokens": 2_048,
            "thinking": {"type": "enabled", "budget_tokens": 1_024},
        },
    )


def _configure_opus_47(model: str, chapter: "Chapter") -> ModelConfig:
    efforts = ["xhigh", "high", "medium"]
    attempts = []
    for effort in efforts:
        attempts.append(AttemptConfig(
            thinking={"type": "adaptive", "display": "summarized"},
            extra_kwargs={"output_config": {"effort": effort}},
            label=f"effort={effort}",
        ))
    return ModelConfig(
        model=model,
        max_tokens=128_000,
        attempts=attempts,
        verify_kwargs={
            "max_tokens": 1_024,
            "thinking": {"type": "adaptive"},
            "output_config": {"effort": "low"},
        },
    )


def configure_model(model: str, chapter: "Chapter") -> ModelConfig:
    if model.startswith("claude-opus-4-7") or model.startswith("claude-4.7"):
        return _configure_opus_47(model, chapter)
    return _configure_opus_46(model, chapter)


# ---------------------------------------------------------------------------
# Prompt Files
# ---------------------------------------------------------------------------

PROMPT_DIR = Path(__file__).parent / "prompt"
SYSTEM_FILE = PROMPT_DIR / "system.md"
ANTI_TIC_FILE = PROMPT_DIR / "anti-tic.md"
REVISE_FILE = PROMPT_DIR / "remove-tic.md"


def load_prompt(path: Path) -> str:
    if not path.exists():
        print(f"Prompt file missing: {path}", file=sys.stderr)
        sys.exit(1)
    return path.read_text(encoding="utf-8").strip()


QUOTED_RE = re.compile(r'"([^"]+)"')


def _extract_mandatory_lines(chapter: "Chapter") -> list[str]:
    lines = []
    for entry in chapter.log_entries:
        if entry.entry_type == "echo":
            m = QUOTED_RE.search(entry.raw)
            if m:
                lines.append(f'"{m.group(1)}"')
    return lines


# ---------------------------------------------------------------------------
# 2. Name Matcher
# ---------------------------------------------------------------------------

def find_prior_entries(bible: Bible, chapter_num: int) -> list[tuple[int, str, str]]:
    chapter = bible.chapters[chapter_num]
    target_names = {e.name for e in chapter.log_entries}

    prior = []
    for n in sorted(bible.chapters):
        if n >= chapter_num:
            break
        for entry in bible.chapters[n].log_entries:
            if entry.name in target_names:
                prior.append((n, bible.chapters[n].title, entry.raw))
    return prior


# ---------------------------------------------------------------------------
# 3. Character Extractor
# ---------------------------------------------------------------------------

def extract_characters(bible: Bible, chapter_num: int) -> list[str]:
    chapter = bible.chapters[chapter_num]
    names = {chapter.pov.lower()}
    for entry in chapter.log_entries:
        if entry.entry_type == "char":
            names.add(entry.name.lower())

    for key, char in bible.characters.items():
        if re.search(r"\b" + re.escape(char.name) + r"\b", chapter.summary):
            names.add(key)

    results = []
    for name in sorted(names):
        if name in bible.characters:
            results.append(bible.characters[name].raw)
    return results


# ---------------------------------------------------------------------------
# 4. Prompt Assembler
# ---------------------------------------------------------------------------

def assemble_prompt(
    bible: Bible,
    chapter_num: int,
    pen_contents: list[str],
) -> tuple[str, str]:
    chapter = bible.chapters[chapter_num]

    anti_tic = load_prompt(ANTI_TIC_FILE)
    system_base = load_prompt(SYSTEM_FILE).format(
        num=chapter.num,
        title=chapter.title,
    )
    system = f"{anti_tic}\n\n{system_base}"

    parts = []

    OPERATIONAL_KEYS = {"Output", "Model", "Pen files"}
    parts.append("## BOOK METADATA\n")
    for key, value in bible.metadata.items():
        if key not in OPERATIONAL_KEYS:
            parts.append(f"- {key}: {value}")
    parts.append("")

    chars = extract_characters(bible, chapter_num)
    if chars:
        parts.append("## CHARACTER REGISTRY\n")
        for c in chars:
            parts.append(c)
            parts.append("\n---\n")
        parts.append("")

    if bible.themes:
        parts.append("## THEMATIC THREADS\n")
        for theme in bible.themes:
            parts.append(f"- {theme}")
        parts.append("")

    prior = find_prior_entries(bible, chapter_num)
    if prior:
        parts.append("## PRIOR ELEMENTS\n")
        current_ch = None
        for ch_num, ch_title, raw_line in prior:
            if ch_num != current_ch:
                if current_ch is not None:
                    parts.append("")
                parts.append(f"From Ch {ch_num}: {ch_title}")
                current_ch = ch_num
            parts.append(raw_line)
        parts.append("")

    parts.append(f"## EMIT AT LEAST {chapter.target:,} POLISHED WORDS\n")

    parts.append(f"## CHAPTER SPEC — Ch {chapter.num}: {chapter.title}")
    parts.append(f"POV: {chapter.pov} | Register: {chapter.register}")
    parts.append("")
    if chapter.summary:
        parts.append(chapter.summary)
        parts.append("")
    parts.append("Log:")
    if chapter.log_raw:
        parts.append(chapter.log_raw)
    parts.append("")

    mandatory = _extract_mandatory_lines(chapter)
    if mandatory:
        parts.append("## MANDATORY LINES — deploy verbatim\n")
        parts.append("These exact lines MUST appear in the chapter prose, word for word:\n")
        for line in mandatory:
            parts.append(f"- {line}")
        parts.append("")

    for i, pen in enumerate(pen_contents):
        if i == 0:
            parts.append("## PEN FILE\n")
        else:
            parts.append(f"\n## PEN FILE (continued)\n")
        parts.append(pen)
    parts.append("")

    user = "\n".join(parts)
    return system, user


# ---------------------------------------------------------------------------
# 5. Streaming Helper
# ---------------------------------------------------------------------------

def _get_client(logger: logging.Logger):
    """Return an Anthropic client, or None on failure."""
    try:
        import anthropic
    except ImportError:
        logger.error("anthropic package not installed. Run: pip install anthropic")
        return None
    if not os.environ.get("ANTHROPIC_API_KEY"):
        logger.error("ANTHROPIC_API_KEY not set in environment")
        return None
    return anthropic.Anthropic()


def _stream_call(
    client,
    model: str,
    max_tokens: int,
    system: str,
    user: str,
    thinking: dict,
    extra_kwargs: dict,
    tag: str,
    logger: logging.Logger,
) -> tuple[str, str | None]:
    """Stream an API call and return (response_text, stop_reason).

    Returns ("", None) on error.
    """
    import anthropic

    full_text: list[str] = []
    word_count = 0
    thinking_chars = 0
    last_report = time.time()

    stop_reason = None
    block_types: list[str | None] = []
    input_tokens = 0
    output_tokens = 0

    try:
        with client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            thinking=thinking,
            system=system,
            messages=[{"role": "user", "content": user}],
            **extra_kwargs,
        ) as stream:
            for event in stream:
                if event.type == "content_block_start":
                    block_type = getattr(event.content_block, "type", None)
                    block_types.append(block_type)
                    if block_type == "thinking":
                        status(tag, "Thinking...")
                        last_report = time.time()
                    elif block_type == "text":
                        if thinking_chars:
                            status(tag, f"Thinking done ({thinking_chars:,} chars). Writing...")
                        else:
                            status(tag, "Writing...")
                        last_report = time.time()
                elif event.type == "content_block_delta":
                    delta = event.delta
                    dtype = getattr(delta, "type", None)
                    if dtype == "text_delta":
                        full_text.append(delta.text)
                        word_count += len(delta.text.split())
                        now = time.time()
                        if now - last_report > 3:
                            status(tag, f"Writing... {word_count:,} words")
                            last_report = now
                    elif dtype == "thinking_delta":
                        thinking_chars += len(getattr(delta, "thinking", ""))
                        now = time.time()
                        if now - last_report > 3:
                            status(tag, f"Thinking... {thinking_chars:,} chars")
                            last_report = now
                elif event.type == "message_delta":
                    stop_reason = getattr(event.delta, "stop_reason", None)
                elif event.type == "message_start":
                    usage = getattr(event.message, "usage", None)
                    if usage:
                        input_tokens = getattr(usage, "input_tokens", 0)

            final_msg = stream.get_final_message()
            if final_msg:
                stop_reason = stop_reason or final_msg.stop_reason
                usage = getattr(final_msg, "usage", None)
                if usage:
                    output_tokens = getattr(usage, "output_tokens", 0)

        status(
            tag,
            f"Response: stop={stop_reason}, blocks={block_types}, "
            f"in={input_tokens:,}, out={output_tokens:,}",
        )

    except anthropic.APIError as e:
        logger.error(
            "API error [%s]: status=%s type=%s message=%s",
            tag, getattr(e, "status_code", "?"), type(e).__name__, str(e),
        )
        return "", None
    except Exception as e:
        logger.error(
            "Network error [%s] after %d words: %s: %s",
            tag, word_count, type(e).__name__, str(e),
        )
        return "", None

    return "".join(full_text), stop_reason


def _write_file(path: Path, content: str, logger: logging.Logger) -> bool:
    """Atomic write via tmp + rename."""
    tmp = path.with_suffix(".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        return True
    except OSError as e:
        logger.error("Failed to write %s: %s", path, e)
        return False


# ---------------------------------------------------------------------------
# 5. Chapter Writer
# ---------------------------------------------------------------------------

def write_chapter(
    system: str,
    user: str,
    chapter: Chapter,
    output_dir: Path,
    cfg: ModelConfig,
    logger: logging.Logger,
) -> bool:
    client = _get_client(logger)
    if not client:
        return False

    draft_dir = output_dir / "draft"
    draft_dir.mkdir(parents=True, exist_ok=True)
    draft_path = draft_dir / f"ch-{chapter.num:02d}.md"
    tag = f"ch {chapter.num}"

    response = ""
    num_attempts = len(cfg.attempts)

    for attempt_idx, acfg in enumerate(cfg.attempts):
        attempt = attempt_idx + 1
        if attempt > 1:
            status(tag, f"Retry {attempt}/{num_attempts} with {acfg.label} (downgraded)")

        status(
            tag,
            f"Calling {cfg.model} (target: {chapter.target:,} words, "
            f"max_tokens: {cfg.max_tokens:,}, {acfg.label})...",
        )

        response, _stop = _stream_call(
            client, cfg.model, cfg.max_tokens,
            system, user, acfg.thinking, acfg.extra_kwargs,
            tag, logger,
        )

        if response.strip():
            break

        logger.warning(
            "Empty response on attempt %d/%d for ch %d",
            attempt, num_attempts, chapter.num,
        )

    if not response.strip():
        logger.error("Empty response after %d attempts for ch %d", num_attempts, chapter.num)
        return False

    prose_words = len(response.split())
    if prose_words < chapter.target * 0.3:
        logger.warning(
            "Ch %d prose very short: %d words (target %d)",
            chapter.num, prose_words, chapter.target,
        )

    if not _write_file(draft_path, response, logger):
        return False

    status(tag, f"Done: {prose_words:,} words -> {draft_path.name}")
    return True


# ---------------------------------------------------------------------------
# 6. Chapter Reviser
# ---------------------------------------------------------------------------

def revise_chapter(
    chapter: Chapter,
    output_dir: Path,
    model: str,
    logger: logging.Logger,
) -> bool:
    draft_dir = output_dir / "draft"
    chapters_dir = output_dir / "chapters"
    draft_path = draft_dir / f"ch-{chapter.num:02d}.md"
    final_path = chapters_dir / f"ch-{chapter.num:02d}.md"
    tag = f"revise {chapter.num}"

    if not draft_path.exists():
        logger.error("No draft to revise: %s", draft_path)
        return False

    draft = draft_path.read_text(encoding="utf-8")
    draft_words = len(draft.split())

    client = _get_client(logger)
    if not client:
        return False

    anti_tic = load_prompt(ANTI_TIC_FILE)
    revise_base = load_prompt(REVISE_FILE)
    system = f"{anti_tic}\n\n{revise_base}"

    cfg = configure_model(model, chapter)
    acfg = cfg.attempts[min(1, len(cfg.attempts) - 1)]

    status(tag, f"Calling {model} ({acfg.label}, draft: {draft_words:,} words)...")

    response, stop = _stream_call(
        client, cfg.model, cfg.max_tokens,
        system, draft, acfg.thinking, acfg.extra_kwargs,
        tag, logger,
    )

    if not response.strip():
        logger.warning("Revision returned empty for ch %d, keeping draft", chapter.num)
        return False

    revised_words = len(response.split())
    ratio = revised_words / max(draft_words, 1)
    if ratio < 0.5 or ratio > 1.5:
        logger.warning(
            "Revision word count suspicious for ch %d: %d -> %d (%.1fx), keeping draft",
            chapter.num, draft_words, revised_words, ratio,
        )
        return False

    chapters_dir.mkdir(parents=True, exist_ok=True)
    if not _write_file(final_path, response, logger):
        return False

    status(tag, f"Revised: {draft_words:,} -> {revised_words:,} words -> {final_path.name}")
    return True


def assemble_revise_prompt(chapter_num: int, output_dir: Path) -> tuple[str, str] | None:
    """Build the revision prompt for --show-revise. Returns (system, user) or None."""
    draft_dir = output_dir / "draft"
    draft_path = draft_dir / f"ch-{chapter_num:02d}.md"
    if not draft_path.exists():
        return None
    anti_tic = load_prompt(ANTI_TIC_FILE)
    revise_base = load_prompt(REVISE_FILE)
    system = f"{anti_tic}\n\n{revise_base}"
    user = draft_path.read_text(encoding="utf-8")
    return system, user


# ---------------------------------------------------------------------------
# 7. Assembler
# ---------------------------------------------------------------------------

def assemble_manuscript(bible: Bible, output_dir: Path, logger: logging.Logger) -> bool:
    chapters_dir = output_dir / "chapters"
    if not chapters_dir.exists():
        logger.error("Chapters directory not found: %s", chapters_dir)
        return False

    # Only pick up exact ch-##.md files (not drafts, backups, or alternates)
    chapter_pattern = re.compile(r"^ch-\d{2}\.md$")
    chapter_files = sorted(
        f for f in chapters_dir.glob("ch-*.md") if chapter_pattern.match(f.name)
    )
    if not chapter_files:
        logger.warning("No chapter files found in %s", chapters_dir)
        return False

    parts = []

    # Add title and metadata from bible
    title = bible.metadata.get("Title", "Untitled")
    author = bible.metadata.get("Author", "")
    dedication = bible.metadata.get("Dedication", "")

    parts.append(f"# {title}")
    parts.append("")
    if author:
        parts.append(f"<!-- author: {author} -->")
    if dedication:
        parts.append(f"<!-- dedication: {dedication} -->")
    if author or dedication:
        parts.append("")
    parts.append("---")
    parts.append("")

    for cf in chapter_files:
        content = cf.read_text(encoding="utf-8").strip()
        parts.append("")
        parts.append(content)

    # Add back matter from bible if present
    back_cover = bible.metadata.get("Back cover", "")
    back_author = bible.metadata.get("Back author", "")

    if back_cover or back_author:
        parts.append("")
        parts.append("---")
        parts.append("")
        parts.append("<!-- back-cover -->")
        parts.append("")
        if back_cover:
            parts.append("## Back Cover")
            parts.append("")
            parts.append(back_cover)
            parts.append("")
        if back_author:
            parts.append("<!-- back-author -->")
            parts.append("")
            parts.append(back_author)

    manuscript = "\n".join(parts) + "\n"

    final_path = output_dir / "manuscript.md"
    if not _write_file(final_path, manuscript, logger):
        return False

    word_count = len(manuscript.split())
    status("assemble", f"Wrote {final_path.name}: {word_count:,} words from {len(chapter_files)} chapters")
    return True


# ---------------------------------------------------------------------------
# Progress + Logging
# ---------------------------------------------------------------------------

def status(tag: str, msg: str):
    print(f"[{tag:<10s}] {msg}", file=sys.stderr)
    logging.getLogger("writer").info(f"[{tag}] {msg}")


def setup_logging(log_path: Path) -> logging.Logger:
    logger = logging.getLogger("writer")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stderr)
    sh.setLevel(logging.WARNING)
    sh.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(sh)

    return logger


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Write chapters from a story bible using the Anthropic API."
    )
    parser.add_argument("bible", type=Path, help="Path to the story bible markdown file")
    parser.add_argument("--chapter", type=int, help="Write a specific chapter (even if it exists)")
    parser.add_argument("--show", type=int, metavar="N", help="Show the full prompt for chapter N and exit")
    parser.add_argument("--show-revise", type=int, metavar="N", help="Show the revision prompt for chapter N and exit")
    parser.add_argument("--revise", action="store_true", help="Run revision pass on drafts")
    parser.add_argument("--assemble", action="store_true", help="Assemble manuscript only")
    parser.add_argument("--dry-run", action="store_true", help="Print prompt to stdout, don't call API")
    parser.add_argument("--model", default=None, help="Anthropic model (overrides bible)")
    parser.add_argument(
        "--dump-json", nargs="?", const="", default=None, metavar="PATH",
        help="Debug: dump parsed bible to JSON at PATH (default: <bible_dir>/bible.json), then exit.",
    )
    args = parser.parse_args()

    bible_path = args.bible.resolve()
    if not bible_path.exists():
        print(f"Bible not found: {bible_path}", file=sys.stderr)
        sys.exit(1)

    bible_dir = bible_path.parent
    logger = setup_logging(bible_dir / "writer.log")

    status("bible", f"Parsing {bible_path.name}...")
    try:
        bible = parse_bible(bible_path)
    except BibleParseError as e:
        print(f"Bible parse error at line {e.line_num}:", file=sys.stderr)
        print(f"  > {e.line_text}", file=sys.stderr)
        print("", file=sys.stderr)
        print(f"  {e.message}", file=sys.stderr)
        logger.error(
            "BibleParseError at line %d: %s | line text: %s",
            e.line_num, e.message, e.line_text,
        )
        sys.exit(1)
    except Exception as e:
        logger.error("Failed to parse bible: %s", e)
        sys.exit(1)

    output_str = bible.metadata.get("Output", ".").strip()
    output_dir = (bible_dir / output_str).resolve()
    status("bible", f"Parsed {len(bible.chapters)} chapters, {len(bible.characters)} characters")

    if args.dump_json is not None:
        dump_path = Path(args.dump_json).resolve() if args.dump_json else bible_dir / "bible.json"
        dump_path.write_text(
            json.dumps(to_dict(bible), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        status("dump", f"Wrote bible JSON -> {dump_path}")
        sys.exit(0)

    DEFAULT_MODEL = "claude-opus-4-6"
    if args.model:
        model = args.model
        model_source = "CLI"
    elif "Model" in bible.metadata:
        model = bible.metadata["Model"].strip()
        model_source = "bible"
    else:
        model = DEFAULT_MODEL
        model_source = "default"
    status("model", f"Resolved: {model} (from {model_source})")

    sys_chars = len(SYSTEM_FILE.read_text(encoding="utf-8")) if SYSTEM_FILE.exists() else 0
    tic_chars = len(ANTI_TIC_FILE.read_text(encoding="utf-8")) if ANTI_TIC_FILE.exists() else 0
    status("prompt", f"Loaded system.md ({sys_chars} chars)")
    status("prompt", f"Loaded anti-tic.md ({tic_chars} chars)")

    pen_dir = Path(__file__).parent / "pen"
    pen_paths_raw = bible.metadata.get("Pen files", "none")
    pen_contents = []
    if pen_paths_raw.lower() != "none":
        for raw in pen_paths_raw.split(","):
            p = raw.strip()
            # Bare filename -> look in tools/novelist/pen/ first, fall back to bible_dir.
            # Path with separator or leading '.' -> resolve relative to bible_dir.
            if "/" in p or "\\" in p or p.startswith("."):
                pen_path = (bible_dir / p).resolve()
            else:
                candidate = (pen_dir / p).resolve()
                pen_path = candidate if candidate.exists() else (bible_dir / p).resolve()
            if not pen_path.exists():
                logger.error("Pen file not found: %s (resolved from '%s')", pen_path, p)
                sys.exit(1)
            pen_contents.append(pen_path.read_text(encoding="utf-8"))
        status("pen", f"Loaded {len(pen_contents)} pen files")

    if args.show is not None:
        if args.show not in bible.chapters:
            print(f"Chapter {args.show} not found in bible", file=sys.stderr)
            sys.exit(1)
        system, user = assemble_prompt(bible, args.show, pen_contents)
        print("=" * 60)
        print("SYSTEM PROMPT")
        print("=" * 60)
        print(system)
        print()
        print("=" * 60)
        print(f"USER PROMPT — Ch {args.show}")
        print("=" * 60)
        print(user)
        prompt_words = len(system.split()) + len(user.split())
        print()
        print(f"[{prompt_words:,} words total]")
        sys.exit(0)

    if args.show_revise is not None:
        result = assemble_revise_prompt(args.show_revise, output_dir)
        if result is None:
            print(
                f"No draft for ch {args.show_revise} — write it first",
                file=sys.stderr,
            )
            sys.exit(1)
        system, user = result
        print("=" * 60)
        print("REVISION SYSTEM PROMPT")
        print("=" * 60)
        print(system)
        print()
        print("=" * 60)
        print(f"DRAFT INPUT — Ch {args.show_revise}")
        print("=" * 60)
        print(user)
        prompt_words = len(system.split()) + len(user.split())
        print()
        print(f"[{prompt_words:,} words total]")
        sys.exit(0)

    if args.assemble:
        ok = assemble_manuscript(bible, output_dir, logger)
        sys.exit(0 if ok else 1)

    if args.dry_run and args.chapter:
        if args.chapter not in bible.chapters:
            logger.error("Chapter %d not found in bible", args.chapter)
            sys.exit(1)
        system, user = assemble_prompt(bible, args.chapter, pen_contents)
        print("=" * 60)
        print("SYSTEM PROMPT")
        print("=" * 60)
        print(system)
        print()
        print("=" * 60)
        print("USER PROMPT")
        print("=" * 60)
        print(user)
        sys.exit(0)

    if not args.dry_run and not os.environ.get("ANTHROPIC_API_KEY"):
        logger.error("ANTHROPIC_API_KEY not set in environment")
        sys.exit(1)

    chapters_to_write = []
    chapters_to_revise = []
    chapters_dir = output_dir / "chapters"
    draft_dir = output_dir / "draft"
    if args.chapter:
        if args.chapter not in bible.chapters:
            logger.error("Chapter %d not found in bible", args.chapter)
            sys.exit(1)
        stale_final = chapters_dir / f"ch-{args.chapter:02d}.md"
        if stale_final.exists():
            stale_final.unlink()
            status(f"ch {args.chapter}", f"removed stale chapters/{stale_final.name}")
        chapters_to_write = [args.chapter]
    else:
        for n in sorted(bible.chapters):
            final = chapters_dir / f"ch-{n:02d}.md"
            draft = draft_dir / f"ch-{n:02d}.md"
            if final.exists():
                status(f"ch {n}", "exists, skipping")
            elif draft.exists() and args.revise:
                chapters_to_revise.append(n)
                status(f"ch {n}", "draft exists, will revise")
            elif draft.exists():
                chapters_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(draft, final)
                status(f"ch {n}", f"draft exists, promoting to chapters/{final.name}")
            else:
                chapters_to_write.append(n)

    if args.dry_run and chapters_to_write:
        ch_num = chapters_to_write[0]
        status("dry-run", f"Showing prompt for ch {ch_num} (first unwritten)")
        system, user = assemble_prompt(bible, ch_num, pen_contents)
        print("=" * 60)
        print("SYSTEM PROMPT")
        print("=" * 60)
        print(system)
        print()
        print("=" * 60)
        print("USER PROMPT")
        print("=" * 60)
        print(user)
        sys.exit(0)

    if not args.dry_run:
        probe_ch = bible.chapters[chapters_to_write[0]] if chapters_to_write else next(iter(bible.chapters.values()))
        probe_cfg = configure_model(model, probe_ch)
        try:
            import anthropic
            client = anthropic.Anthropic()
            verify = client.messages.create(
                model=model,
                messages=[{"role": "user", "content": "hi"}],
                **probe_cfg.verify_kwargs,
            )
            status("model", f"Verified: {verify.model} via API")
        except ImportError:
            logger.error("anthropic package not installed. Run: pip install anthropic")
            sys.exit(1)
        except anthropic.APIError as e:
            logger.error("Model verification failed: %s", e)
            sys.exit(1)

    wrote = []
    failed = []
    start_time = time.time()

    for n in chapters_to_write:
        system, user = assemble_prompt(bible, n, pen_contents)
        ch = bible.chapters[n]
        cfg = configure_model(model, ch)

        prompt_words = len(system.split()) + len(user.split())
        status(f"ch {n}", f"Prompt: ~{prompt_words:,} words")

        ok = write_chapter(system, user, ch, output_dir, cfg, logger)
        if ok:
            wrote.append(n)
            if args.revise:
                revise_chapter(ch, output_dir, model, logger)
            else:
                draft = draft_dir / f"ch-{n:02d}.md"
                final = chapters_dir / f"ch-{n:02d}.md"
                chapters_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(draft, final)
                status(f"ch {n}", f"Promoted draft/{draft.name} -> chapters/{final.name}")
        else:
            failed.append(n)

    revised = []
    for n in chapters_to_revise:
        ch = bible.chapters[n]
        if revise_chapter(ch, output_dir, model, logger):
            revised.append(n)

    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    chapters_changed = len(wrote) > 0 or len(revised) > 0
    manuscript_path = output_dir / "manuscript.md"
    should_assemble = (
        chapters_changed
        or not manuscript_path.exists()
    )

    if should_assemble:
        assemble_manuscript(bible, output_dir, logger)

    if wrote or revised or failed:
        parts = []
        if wrote:
            parts.append(f"wrote {len(wrote)}")
        if revised:
            parts.append(f"revised {len(revised)}")
        status("done", f"{', '.join(parts)} chapters in {minutes}m {seconds}s")
        if failed:
            status("done", f"Failed: ch {', '.join(str(n) for n in failed)}")
    elif not chapters_to_write and not chapters_to_revise:
        status("done", "All chapters already exist")


if __name__ == "__main__":
    main()
