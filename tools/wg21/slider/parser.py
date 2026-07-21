"""Markdown -> slide data model.

Parses a Slider markdown document into a list of `TitleSlide` / `ContentSlide`
objects using mistune v3's AST. The renderer consumes these objects; it never
sees raw markdown.

Authoring model:
  #  heading             -> title/interstitial slide (body paragraph = subtitle)
  ## heading             -> content slide; heading text = section label
  first paragraph        -> slide title (left panel)
  ---                     -> separator between left panel and right panel
  right-panel body        -> paragraphs, lists, quotes, code
  ---                     -> a SECOND separator begins speaker notes
  everything after it     -> speaker notes (PowerPoint notes pane; not on slide)

A title/interstitial slide has no right panel, so a single --- on it begins
speaker notes directly. Notes run until the next # or ## heading.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

import mistune

# --- Rich text ----------------------------------------------------------------


@dataclass
class TextRun:
    text: str
    bold: bool = False
    italic: bool = False
    code: bool = False
    url: str | None = None


# --- Right-panel body elements ------------------------------------------------


@dataclass
class Paragraph:
    runs: list[TextRun]


@dataclass
class Subheading:
    runs: list[TextRun]


@dataclass
class Bullet:
    runs: list[TextRun]
    level: int = 0
    highlight: bool = False
    ordered: bool = False
    number: int | None = None


@dataclass
class Callout:
    runs: list[TextRun]


@dataclass
class CodeBlock:
    text: str
    language: str | None = None


# --- Slides -------------------------------------------------------------------


@dataclass
class TitleSlide:
    title: list[TextRun]
    subtitle: str | None = None
    image_path: str | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class ContentSlide:
    section_label: str
    title: list[TextRun] = field(default_factory=list)
    image_path: str | None = None
    body: list[object] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


# --- Helpers ------------------------------------------------------------------

_IMG_SRC_RE = re.compile(r"""<img[^>]*\bsrc\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
_FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)


def strip_frontmatter(text: str) -> str:
    """Remove a leading YAML frontmatter block (delimited by --- lines)."""
    if text.startswith("---"):
        return _FRONTMATTER_RE.sub("", text, count=1)
    return text


def runs_to_plain(runs: list[TextRun]) -> str:
    return "".join(r.text for r in runs)


def _img_from_html(raw: str) -> str | None:
    m = _IMG_SRC_RE.search(raw or "")
    return m.group(1) if m else None


def inline_to_runs(children, bold=False, italic=False, url=None) -> list[TextRun]:
    runs: list[TextRun] = []
    for tok in children or []:
        ttype = tok.get("type")
        if ttype == "text":
            runs.append(TextRun(tok.get("raw", ""), bold, italic, False, url))
        elif ttype == "strong":
            runs.extend(inline_to_runs(tok.get("children"), True, italic, url))
        elif ttype == "emphasis":
            runs.extend(inline_to_runs(tok.get("children"), bold, True, url))
        elif ttype == "codespan":
            runs.append(TextRun(tok.get("raw", ""), bold, italic, True, url))
        elif ttype == "link":
            link_url = tok.get("attrs", {}).get("url", url)
            runs.extend(inline_to_runs(tok.get("children"), bold, italic, link_url))
        elif ttype == "softbreak":
            runs.append(TextRun(" ", bold, italic))
        elif ttype == "linebreak":
            runs.append(TextRun("\n", bold, italic))
        elif ttype in ("image", "inline_html", "block_html"):
            continue  # images/comments handled at the block level
        else:
            if tok.get("children"):
                runs.extend(inline_to_runs(tok.get("children"), bold, italic, url))
            elif "raw" in tok:
                runs.append(TextRun(tok.get("raw", ""), bold, italic))
    return runs


def _find_image_in_children(children) -> str | None:
    for tok in children or []:
        if tok.get("type") == "image":
            return tok.get("attrs", {}).get("url")
        if tok.get("type") == "inline_html":
            url = _img_from_html(tok.get("raw", ""))
            if url:
                return url
    return None


def _paragraph_is_only_image(children) -> bool:
    meaningful = [t for t in (children or []) if t.get("type") not in ("softbreak", "linebreak")]
    if not meaningful:
        return False
    for tok in meaningful:
        if tok.get("type") == "image":
            continue
        if tok.get("type") == "inline_html" and _img_from_html(tok.get("raw", "")):
            continue
        return False
    return True


def _blockquote_runs(tok) -> list[TextRun]:
    runs: list[TextRun] = []
    for i, child in enumerate(tok.get("children", [])):
        if child.get("type") == "paragraph":
            if i > 0 and runs:
                runs.append(TextRun("\n"))
            runs.extend(inline_to_runs(child.get("children")))
    return runs


def _walk_list_items(list_tok, level: int = 0):
    """Yield `(level, ordered, number, runs)` for each item, depth-first.

    The one traversal shared by the on-slide bullet builder and the speaker-note
    line builder; a parent is yielded before its nested children.
    """
    ordered = list_tok.get("attrs", {}).get("ordered", False)
    number = list_tok.get("attrs", {}).get("start", 1) if ordered else None
    for item in list_tok.get("children", []):
        if item.get("type") != "list_item":
            continue
        runs: list[TextRun] = []
        sublists = []
        for sub in item.get("children", []):
            stype = sub.get("type")
            if stype in ("block_text", "paragraph"):
                runs.extend(inline_to_runs(sub.get("children")))
            elif stype == "list":
                sublists.append(sub)
        yield level, ordered, number, runs
        if ordered and number is not None:
            number += 1
        for sublist in sublists:
            yield from _walk_list_items(sublist, level + 1)


def _parse_list(list_tok) -> list[Bullet]:
    out: list[Bullet] = []
    for level, ordered, number, runs in _walk_list_items(list_tok):
        visible = [r for r in runs if r.text.strip()]
        highlight = bool(visible) and all(r.bold for r in visible)
        out.append(Bullet(runs=runs, level=level, highlight=highlight, ordered=ordered, number=number))
    return out


def _resolve_image(url: str | None, base_dir: str | None) -> str | None:
    if not url:
        return None
    if base_dir and not os.path.isabs(url):
        return os.path.normpath(os.path.join(base_dir, url))
    return url


# --- Section state ------------------------------------------------------------
#
# `section` counts the --- separators seen so far on the current slide:
#   content: 0 = left panel (title), 1 = right panel (body), >= 2 = speaker notes
#   title:   0 = subtitle,                                    >= 1 = speaker notes


def _is_notes(cur: dict | None) -> bool:
    if cur is None:
        return False
    threshold = 1 if cur["kind"] == "title" else 2
    return cur.get("section", 0) >= threshold


def _is_body(cur: dict | None) -> bool:
    return cur is not None and cur["kind"] == "content" and cur.get("section", 0) == 1


def _list_to_note_lines(list_tok) -> list[str]:
    """Flatten a markdown list into plain-text note lines (`- item` / `N. item`)."""
    out: list[str] = []
    for level, ordered, number, runs in _walk_list_items(list_tok):
        indent = "  " * level
        text = runs_to_plain(runs).strip()
        if ordered and number is not None:
            out.append(f"{indent}{number}. {text}")
        else:
            out.append(f"{indent}- {text}")
    return out


# --- Main parse ---------------------------------------------------------------


def parse_markdown(text: str, base_dir: str | None = None) -> list[object]:
    """Parse Slider markdown into a list of slide objects."""
    text = strip_frontmatter(text)
    md = mistune.create_markdown(renderer=None)
    tokens = md(text)

    slides: list[object] = []
    cur: dict | None = None

    def finalize():
        nonlocal cur
        if cur is None:
            return
        if cur["kind"] == "title":
            slides.append(
                TitleSlide(
                    title=cur["title"] or [],
                    subtitle=cur["subtitle"],
                    image_path=_resolve_image(cur["image"], base_dir),
                    notes=cur["notes"],
                )
            )
        else:
            slides.append(
                ContentSlide(
                    section_label=cur["label"],
                    title=cur["title"] or [],
                    image_path=_resolve_image(cur["image"], base_dir),
                    body=cur["body"],
                    notes=cur["notes"],
                )
            )
        cur = None

    for tok in tokens:
        ttype = tok.get("type")

        if ttype == "blank_line":
            continue

        if ttype == "heading":
            level = tok.get("attrs", {}).get("level", 1)
            if level == 1:
                finalize()
                cur = {
                    "kind": "title",
                    "title": inline_to_runs(tok.get("children")),
                    "subtitle": None,
                    "image": None,
                    "section": 0,
                    "notes": [],
                }
            elif level == 2:
                finalize()
                label = runs_to_plain(inline_to_runs(tok.get("children"))).upper()
                cur = {
                    "kind": "content",
                    "label": label,
                    "title": None,
                    "image": None,
                    "section": 0,
                    "body": [],
                    "notes": [],
                }
            else:  # h3+ -> subheading in the right panel, or a line of notes
                if _is_notes(cur):
                    txt = runs_to_plain(inline_to_runs(tok.get("children"))).strip()
                    if txt:
                        cur["notes"].append(txt)
                elif cur and cur["kind"] == "content":
                    cur["body"].append(Subheading(inline_to_runs(tok.get("children"))))
            continue

        if ttype == "thematic_break":
            if cur is not None:
                cur["section"] = cur.get("section", 0) + 1
            continue

        if ttype in ("block_html", "inline_html"):
            url = _img_from_html(tok.get("raw", ""))
            if url and cur is not None and cur.get("image") is None and not _is_notes(cur):
                cur["image"] = url
            continue

        if ttype == "paragraph":
            children = tok.get("children")
            img = _find_image_in_children(children)
            if img and cur is not None and cur.get("image") is None and not _is_notes(cur):
                cur["image"] = img
                if _paragraph_is_only_image(children):
                    continue
            runs = inline_to_runs(children)
            if cur is None:
                continue
            if _is_notes(cur):
                txt = runs_to_plain(runs).strip()
                if txt:
                    cur["notes"].append(txt)
            elif cur["kind"] == "title":
                if cur["subtitle"] is None:
                    cur["subtitle"] = runs_to_plain(runs).strip() or None
            elif cur.get("section", 0) == 0:  # content, left panel
                if cur["title"] is None:
                    cur["title"] = runs
            else:  # content, right panel body
                cur["body"].append(Paragraph(runs))
            continue

        if ttype == "list":
            if _is_notes(cur):
                cur["notes"].extend(_list_to_note_lines(tok))
            elif _is_body(cur):
                cur["body"].extend(_parse_list(tok))
            continue

        if ttype == "block_quote":
            if _is_notes(cur):
                txt = runs_to_plain(_blockquote_runs(tok)).strip()
                if txt:
                    cur["notes"].append(txt)
            elif _is_body(cur):
                cur["body"].append(Callout(_blockquote_runs(tok)))
            continue

        if ttype == "block_code":
            if _is_notes(cur):
                code = tok.get("raw", "").rstrip("\n")
                if code:
                    cur["notes"].append(code)
            elif _is_body(cur):
                info = tok.get("attrs", {}).get("info")
                cur["body"].append(CodeBlock(tok.get("raw", "").rstrip("\n"), info))
            continue

    finalize()
    return slides
