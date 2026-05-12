"""Story bible parser and structured representation.

Pure function ``parse_bible(path)`` reads a story bible from disk and returns a
fully-populated :class:`Bible` dataclass. On malformed content it raises
:class:`BibleParseError` with ``line_num``, ``line_text``, and ``message``
suitable for neat display to the user.

Round-trip fidelity contract
----------------------------
Every authored piece of content in the bible is preserved verbatim in the
returned data:

- Log entry lines in ``LogEntry.raw``
- Character entries in ``Character.raw`` (full markdown block) plus a
  structured ``Character.fields`` dict
- Chapter summaries as stored multi-line strings
- Metadata and theme values as strings

Cosmetic whitespace (extra blank lines, trailing whitespace) may be lost.

The :func:`to_dict` serializer walks the dataclasses and produces a
``json.dumps``-ready tree; it inherits the parser's fidelity. It exists for
debugging (``writer.py --dump-json``) and is not on the pipeline's hot path.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Grammar regexes
# ---------------------------------------------------------------------------

LOG_ENTRY_RE = re.compile(
    r"^\s*-\s*\[([\w-]+)(?:\s+(\w+(?:/\w+)?))?]\s+(.+?)(?:\s+--\s+(.*))?$"
)
CHAPTER_HEADER_RE = re.compile(r"^###\s+Ch\s+(\d+):\s+(.+)$")
POV_LINE_RE = re.compile(
    r"^POV:\s+(.+?)\s*\|\s*Register:\s+(.+?)\s*\|\s*Target:\s+~?([\d,]+)"
)
CHARACTER_RE = re.compile(r"^-\s+\*\*(.+?)\*\*")
METADATA_RE = re.compile(r"^-\s+(.+?):\s+(.+)$")
CHAR_FIELD_RE = re.compile(r"^  -\s+([^:]+):\s*(.*)$")


# ---------------------------------------------------------------------------
# Error class
# ---------------------------------------------------------------------------

class BibleParseError(Exception):
    """Raised when :func:`parse_bible` encounters malformed content.

    Attributes:
        line_num: 1-indexed line number where the error was detected.
        line_text: the offending line's text.
        message: a human-readable problem description.
    """

    def __init__(self, line_num: int, line_text: str, message: str):
        self.line_num = line_num
        self.line_text = line_text
        self.message = message
        super().__init__(
            f"Bible parse error at line {line_num}: {message}\n"
            f"  > {line_text}"
        )


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class LogEntry:
    entry_type: str
    sequence: str | None
    name: str
    description: str | None
    raw: str


@dataclass
class Chapter:
    num: int
    title: str
    pov: str
    register: str
    target: int
    summary: str
    log_entries: list[LogEntry] = field(default_factory=list)
    log_raw: str = ""


@dataclass
class Character:
    name: str                       # original casing, e.g. "Mick"
    raw: str                        # full multi-line markdown block
    fields: dict[str, str] = field(default_factory=dict)


@dataclass
class Bible:
    metadata: dict[str, str] = field(default_factory=dict)
    characters: dict[str, Character] = field(default_factory=dict)
    chapters: dict[int, Chapter] = field(default_factory=dict)
    themes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Character field parsing
# ---------------------------------------------------------------------------

def _normalize_field_key(raw: str) -> str:
    return re.sub(r"\s+", "_", raw.strip().lower()).replace("-", "_")


def parse_character_fields(
    lines: list[str], first_line_num: int
) -> dict[str, str]:
    """Parse the indented ``- Field: value`` sub-bullets under a character header.

    ``lines[0]`` is the character heading (``- **Name**``); ``lines[1:]`` are
    the sub-bullets. ``first_line_num`` is the 1-indexed line number of
    ``lines[0]``.

    Raises :class:`BibleParseError` on any non-blank, non-comment line that is
    not a parseable ``  - Field: value`` sub-bullet.
    """
    fields: dict[str, str] = {}
    for offset, line in enumerate(lines[1:], start=1):
        line_num = first_line_num + offset
        stripped = line.strip()
        if not stripped or stripped.startswith("<!--"):
            continue
        m = CHAR_FIELD_RE.match(line)
        if not m:
            raise BibleParseError(
                line_num, line,
                "Character sub-bullet must have form '  - Field: value'.",
            )
        key = _normalize_field_key(m.group(1))
        value = m.group(2).rstrip()
        fields[key] = value
    return fields


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_bible(bible_path: Path) -> Bible:
    """Parse a story bible into a :class:`Bible` dataclass.

    Raises :class:`BibleParseError` with ``line_num``, ``line_text``, and
    ``message`` on malformed content. File IO is the only side effect.
    """
    text = Path(bible_path).read_text(encoding="utf-8")
    lines = text.splitlines()

    bible = Bible()
    state = "PREAMBLE"
    cur_char_name: str | None = None
    cur_char_lines: list[str] = []
    cur_char_line_num = 0
    cur_chapter: Chapter | None = None
    cur_chapter_line_num = 0
    summary_lines: list[str] = []
    log_lines: list[str] = []
    awaiting_pov = False
    seen_log_keyword = False

    def _flush_character():
        nonlocal cur_char_name, cur_char_lines, cur_char_line_num
        if cur_char_name:
            has_sub_bullets = any(
                l.strip() and not l.strip().startswith("<!--")
                for l in cur_char_lines[1:]
            )
            if not has_sub_bullets:
                raise BibleParseError(
                    cur_char_line_num, cur_char_lines[0],
                    f"Character '{cur_char_name}' has no sub-bullets.",
                )
            fields = parse_character_fields(cur_char_lines, cur_char_line_num)
            raw_md = "\n".join(cur_char_lines)
            key = cur_char_name.lower()
            bible.characters[key] = Character(
                name=cur_char_name, raw=raw_md, fields=fields
            )
        cur_char_name = None
        cur_char_lines = []
        cur_char_line_num = 0

    def _flush_chapter():
        nonlocal cur_chapter, summary_lines, log_lines, seen_log_keyword
        if cur_chapter:
            header_text = f"### Ch {cur_chapter.num}: {cur_chapter.title}"
            if cur_chapter.pov == "" or cur_chapter.target == 0:
                raise BibleParseError(
                    cur_chapter_line_num, header_text,
                    f"Chapter {cur_chapter.num} is missing its POV line "
                    "(expected 'POV: ... | Register: ... | Target: N').",
                )
            if not seen_log_keyword:
                raise BibleParseError(
                    cur_chapter_line_num, header_text,
                    f"Chapter {cur_chapter.num} is missing its 'Log:' section.",
                )
            cur_chapter.summary = "\n".join(summary_lines).strip()
            cur_chapter.log_raw = "\n".join(log_lines).strip()
            cur_chapter.log_entries = _parse_log_entries(log_lines)
            bible.chapters[cur_chapter.num] = cur_chapter
        cur_chapter = None
        summary_lines = []
        log_lines = []
        seen_log_keyword = False

    for i, raw_line in enumerate(lines):
        line_num = i + 1
        line = raw_line.rstrip()

        # --- Section headers ---------------------------------------------
        if line.startswith("## Book Metadata"):
            _flush_character()
            _flush_chapter()
            state = "METADATA"
            continue
        if line.startswith("## Character Registry"):
            _flush_character()
            _flush_chapter()
            state = "CHARACTERS"
            continue
        if line.startswith("## Thematic Threads"):
            _flush_character()
            _flush_chapter()
            state = "THEMES"
            continue
        if line.startswith("## ") and state not in ("PREAMBLE",):
            _flush_character()
            _flush_chapter()
            state = "PREAMBLE"
            continue

        # --- Chapter header (any state; '### Ch' prefix must match) ------
        if line.startswith("### Ch"):
            ch_m = CHAPTER_HEADER_RE.match(line)
            if not ch_m:
                raise BibleParseError(
                    line_num, raw_line,
                    "Chapter header must match '### Ch N: Title'.",
                )
            _flush_character()
            _flush_chapter()
            cur_chapter = Chapter(
                num=int(ch_m.group(1)),
                title=ch_m.group(2).strip(),
                pov="", register="", target=0, summary="",
            )
            cur_chapter_line_num = line_num
            state = "CHAPTER_HEADER"
            awaiting_pov = True
            summary_lines = []
            log_lines = []
            seen_log_keyword = False
            continue

        # --- State: METADATA ---------------------------------------------
        if state == "METADATA":
            stripped = line.strip()
            if not stripped or stripped.startswith("<!--") or stripped == "---":
                continue
            if stripped.startswith("- "):
                m = METADATA_RE.match(line)
                if not m:
                    raise BibleParseError(
                        line_num, raw_line,
                        "Metadata line must have form '- Key: value'.",
                    )
                bible.metadata[m.group(1).strip()] = m.group(2).strip()
            continue

        # --- State: CHARACTERS -------------------------------------------
        if state == "CHARACTERS":
            if line == "---":
                _flush_character()
                continue
            stripped = line.strip()
            if not stripped or stripped.startswith("<!--"):
                if cur_char_name is not None:
                    cur_char_lines.append(line)
                continue
            cm = CHARACTER_RE.match(line)
            if cm:
                _flush_character()
                cur_char_name = cm.group(1).strip()
                cur_char_lines = [line]
                cur_char_line_num = line_num
            elif cur_char_name is not None:
                cur_char_lines.append(line)
            continue

        # --- State: THEMES -----------------------------------------------
        if state == "THEMES":
            stripped = line.strip()
            if not stripped or stripped.startswith("<!--") or line == "---":
                continue
            if stripped.startswith("-"):
                theme = stripped.lstrip("-").strip()
                if theme:
                    bible.themes.append(theme)
            continue

        # --- State: CHAPTER_HEADER ---------------------------------------
        if state == "CHAPTER_HEADER":
            if awaiting_pov and line.strip():
                stripped = line.strip()
                if stripped.startswith("<!--"):
                    # Structural notes and HTML comments are allowed between
                    # the chapter header and the POV line; capture them in
                    # the summary so log_raw/summary preserve the author's text.
                    summary_lines.append(line)
                    continue
                pm = POV_LINE_RE.match(stripped)
                if not pm:
                    raise BibleParseError(
                        line_num, raw_line,
                        f"Chapter {cur_chapter.num}: expected POV line "
                        "'POV: ... | Register: ... | Target: N' but got "
                        "something else.",
                    )
                cur_chapter.pov = pm.group(1).strip()
                cur_chapter.register = pm.group(2).strip()
                cur_chapter.target = int(pm.group(3).replace(",", ""))
                awaiting_pov = False
                continue
            if line.strip().lower() == "log:":
                state = "CHAPTER_LOG"
                seen_log_keyword = True
                continue
            if line == "---":
                _flush_chapter()
                state = "PREAMBLE"
                continue
            summary_lines.append(line)
            continue

        # --- State: CHAPTER_LOG ------------------------------------------
        if state == "CHAPTER_LOG":
            if line == "---":
                _flush_chapter()
                state = "PREAMBLE"
                continue
            log_lines.append(line)
            continue

    _flush_character()
    _flush_chapter()
    return bible


def _parse_log_entries(lines: list[str]) -> list[LogEntry]:
    entries: list[LogEntry] = []
    for raw in lines:
        normalized = raw.replace("\u2014", "--")
        m = LOG_ENTRY_RE.match(normalized)
        if m:
            entries.append(LogEntry(
                entry_type=m.group(1),
                sequence=m.group(2),
                name=m.group(3).strip(),
                description=m.group(4).strip() if m.group(4) else None,
                raw=raw,
            ))
    return entries


# ---------------------------------------------------------------------------
# Serializer: Bible -> plain dict/list tree (JSON-ready)
# ---------------------------------------------------------------------------

def to_dict(bible: Bible) -> dict:
    """Walk the :class:`Bible` and return a JSON-serializable dict.

    Structure:
        {
          "metadata": {...},
          "characters": {"Name": {"role": "...", ...}, ...},
          "chapters": [{"num": 1, ..., "log": [{...}, ...]}, ...],
          "themes": ["...", ...]
        }

    Chapters are ordered by ``num``. Log entries within each chapter preserve
    their original parsed order.
    """
    return {
        "metadata": dict(bible.metadata),
        "characters": {
            ch.name: dict(ch.fields)
            for ch in bible.characters.values()
        },
        "chapters": [
            {
                "num": ch.num,
                "title": ch.title,
                "pov": ch.pov,
                "register": ch.register,
                "target": ch.target,
                "summary": ch.summary,
                "log": [
                    {
                        "entry_type": e.entry_type,
                        "sequence": e.sequence,
                        "name": e.name,
                        "description": e.description,
                        "raw": e.raw,
                    }
                    for e in ch.log_entries
                ],
            }
            for ch in sorted(bible.chapters.values(), key=lambda c: c.num)
        ],
        "themes": list(bible.themes),
    }
