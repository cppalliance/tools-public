"""Pure layout arithmetic: text-fit estimation and resolved slide geometry.

No pptx, no appearance literals - every number comes from a style dict (`cfg`).
Kept free of side effects so it can be reasoned about and unit-tested alone.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass

from PIL import ImageFont

Box = tuple[float, float, float, float]  # x, y, w, h in inches


def _char_factor(cfg: dict, mono: bool) -> float:
    t = cfg["text"]
    return t["char_factor_mono"] if mono else t["char_factor"]


# --- Font measurement ---------------------------------------------------------
#
# The char_factor estimate below assumes one average glyph width for every
# character, which overcounts lines at wrap boundaries (proportional fonts pack
# tighter than the average). When the real font can be loaded we measure actual
# glyph advances instead; otherwise we fall back to char_factor so the tool
# still runs where the font is not installed.

_FONT_CACHE: dict[tuple[str, int], "ImageFont.FreeTypeFont | None"] = {}

_FONT_DIRS = [
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts"),
    "/usr/share/fonts",
    "/usr/local/share/fonts",
    os.path.expanduser("~/.fonts"),
    os.path.expanduser("~/.local/share/fonts"),
    "/Library/Fonts",
    "/System/Library/Fonts",
    os.path.expanduser("~/Library/Fonts"),
]


def _font_candidate_names(family: str) -> list[str]:
    compact = family.replace(" ", "")
    names = [
        family, f"{family}.ttf", f"{family}.ttc",
        f"{compact}.ttf", f"{compact}-Regular.ttf", f"{compact}.ttc",
        f"{compact.lower()}.ttf", f"{compact.lower()}.ttc",
    ]
    seen: set[str] = set()
    out: list[str] = []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def _resolve_font(family: str, size_pt: float):
    """A Pillow font for `family` at `size_pt`, or None if it cannot be found.

    Pillow does not search per-user Windows font directories by bare name, so we
    probe known font directories with common filename spellings and cache the
    result (misses included) per (family, rounded size).
    """
    size = max(1, int(round(size_pt)))
    key = (family, size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    names = _font_candidate_names(family)
    candidates = list(names)
    for d in _FONT_DIRS:
        if d and os.path.isdir(d):
            candidates += [os.path.join(d, n) for n in names]
    font = None
    for cand in candidates:
        try:
            font = ImageFont.truetype(cand, size)
            break
        except Exception:
            continue
    _FONT_CACHE[key] = font
    return font


def _measured_lines(text: str, box_w_in: float, font, wrap_safety: float = 1.0) -> int:
    """Wrapped line count for `text` in a `box_w_in`-inch box via real glyph
    metrics. Pillow sizes glyphs in pixels at 72 DPI, so a point size loads as
    that many pixels and getlength returns points; the box width in points is
    inches * 72. `wrap_safety` (<=1) trims that width to absorb the small amount
    PowerPoint/Google Slides lay text wider than Pillow measures, so borderline
    lines wrap here the same way they wrap when rendered. Wrapping is greedy
    word-by-word, matching how the box fills."""
    limit = box_w_in * 72.0 * wrap_safety
    if limit <= 0:
        return 1
    total = 0
    for line in text.split("\n"):
        cur = ""
        count = 1
        for word in line.split(" "):
            trial = word if not cur else cur + " " + word
            if not cur or font.getlength(trial) <= limit:
                cur = trial
            else:
                count += 1
                cur = word
        total += count
    return max(1, total)


def estimate_lines(text: str, box_w: float, size_pt: float, char_w: float,
                   font_family: str | None = None, wrap_safety: float = 1.0) -> int:
    """How many wrapped lines `text` occupies. Measures the real font when
    `font_family` resolves; otherwise falls back to the char_factor estimate."""
    if not text:
        return 1
    if font_family:
        font = _resolve_font(font_family, size_pt)
        if font is not None:
            return _measured_lines(text, box_w, font, wrap_safety)
    char_in = char_w * size_pt / 72.0
    if char_in <= 0:
        return 1
    per_line = max(1, int(box_w / char_in))
    return max(1, sum(max(1, math.ceil(len(line) / per_line)) for line in text.split("\n")))


def line_height_in(cfg: dict, size_pt: float) -> float:
    t = cfg["text"]
    return size_pt * t.get("single_line_height", 1.0) * t["line_spacing"] / 72.0


def text_height_in(cfg: dict, text: str, box_w: float, size_pt: float,
                   mono: bool = False, font_family: str | None = None) -> float:
    lines = estimate_lines(text, box_w, size_pt, _char_factor(cfg, mono), font_family,
                           cfg["text"].get("wrap_safety", 1.0))
    return lines * line_height_in(cfg, size_pt)


def fit_font_size(cfg: dict, text: str, box_w: float, box_h: float,
                  start_pt: int, min_pt: int, mono: bool = False,
                  font_family: str | None = None) -> int:
    """Largest size <= start_pt whose text fits `box_h`, never below `min_pt`.

    A pure estimate, not a render; a safety net against overflow.
    """
    pt = int(start_pt)
    while pt > min_pt and text_height_in(cfg, text, box_w, pt, mono, font_family) > box_h:
        pt -= 1
    return max(int(min_pt), pt)


@dataclass(frozen=True)
class Geom:
    slide: Box
    left_panel: Box
    image: Box
    label: Box
    title: Box
    content: Box
    ts_title: Box
    ts_subtitle: Box
    ts_year: Box
    page_number: Box


def geometry(cfg: dict) -> Geom:
    """Resolve every inch box the renderer needs from the style dict."""
    sw = cfg["slide"]["width"]
    sh = cfg["slide"]["height"]
    p = cfg["panels"]

    left_w = round(sw * p["left_fraction"], 3)
    right_w = round(sw - left_w, 3)

    # Image fills the width of the left (navy) panel at the panel ratio, flush
    # to the bottom; it is the dominant element of a content slide.
    img_h = round(left_w * p["image_ratio"], 3)
    img_y = round(sh - img_h, 3)
    image = (0.0, img_y, left_w, img_h)

    # Section label sits in the navy strip above the image, top-left.
    pad = p["left_pad"]
    text_w = left_w - 2 * pad
    lb = cfg["content"]["label"]
    label = (pad, lb["y"], text_w, lb["h"])

    # Right panel holds the title (top, centered) and the body beneath it.
    cx = round(left_w + p["right_pad"], 3)
    cw = round(right_w - 2 * p["right_pad"], 3)
    tr = cfg["content"]["title_right"]
    title = (cx, tr["y"], cw, tr["h"])
    cy = round(tr["y"] + tr["h"] + tr["body_gap"], 3)
    ch = round(sh - cy - p["content_bottom"], 3)
    content = (cx, cy, cw, ch)

    ts = cfg["title_slide"]
    tst = ts["title"]
    tss = ts["subtitle"]
    tsy = ts["year"]
    ts_title = (tst["x"], tst["y"], sw - tst["w_margin"], tst["h"])
    ts_subtitle = (tss["x"], tss["y"], sw - tss["w_margin"], tss["h"])
    ts_year = (tsy["x"], sh - tsy["bottom"], tsy["w"], tsy["h"])

    pn = cfg["page_number"]
    page_number = (sw - pn["right"] - pn["w"], sh - pn["bottom"], pn["w"], pn["h"])

    return Geom(
        slide=(0.0, 0.0, sw, sh),
        left_panel=(0.0, 0.0, left_w, sh),
        image=image,
        label=label,
        title=title,
        content=content,
        ts_title=ts_title,
        ts_subtitle=ts_subtitle,
        ts_year=ts_year,
        page_number=page_number,
    )
