"""Visual constants and text-fitting math for Slider.

Everything that controls how a deck looks lives here: slide dimensions, panel
geometry, colors, fonts, per-role font sizes, and the pure-python text height
estimator that drives auto-fit. No pptx imports - this module is just data and
arithmetic so it can be reasoned about and tested in isolation.
"""

from __future__ import annotations

import math

# --- Slide dimensions (inches) ------------------------------------------------

SLIDE_W = 13.333
SLIDE_H = 7.5

# --- Panel geometry (inches) --------------------------------------------------

# Left panel is ~38% of the slide width; the right panel takes the remainder.
LEFT_W = round(SLIDE_W * 0.38, 3)          # ~5.067"
RIGHT_X = LEFT_W
RIGHT_W = round(SLIDE_W - LEFT_W, 3)       # ~8.266"

# Left-panel image: 4:3, flush to the left/right/bottom edges of the panel.
IMG_W = LEFT_W
IMG_H = round(IMG_W * 3.0 / 4.0, 3)        # ~3.800"
IMG_X = 0.0
IMG_Y = round(SLIDE_H - IMG_H, 3)          # ~3.700"

# Left-panel text boxes (above the image).
LEFT_PAD = 0.4
SECTION_LABEL_BOX = (LEFT_PAD, 0.55, LEFT_W - 2 * LEFT_PAD, 0.4)
TITLE_BOX = (LEFT_PAD, 1.05, LEFT_W - 2 * LEFT_PAD, IMG_Y - 1.05 - 0.15)

# Right-panel content area.
RIGHT_PAD = 0.5
CONTENT_X = round(RIGHT_X + RIGHT_PAD, 3)
CONTENT_Y = 0.6
CONTENT_W = round(RIGHT_W - 2 * RIGHT_PAD, 3)
CONTENT_H = round(SLIDE_H - CONTENT_Y - 0.55, 3)

# Title / interstitial slide boxes.
TS_TITLE_BOX = (0.7, 0.7, SLIDE_W - 1.4, 1.7)
TS_SUBTITLE_BOX = (0.72, 2.35, SLIDE_W - 1.5, 1.0)
TS_YEAR_BOX = (0.72, SLIDE_H - 0.75, 3.0, 0.4)

# Page number, bottom-right.
PAGENO_BOX = (SLIDE_W - 1.7, SLIDE_H - 0.5, 1.4, 0.35)

# --- Colors (hex, no leading '#') ---------------------------------------------

NAVY = "1A1A2E"          # left panel / interstitial background
BLACK = "111111"         # right panel background
ORANGE = "E8A838"        # accent: labels, markers, highlights
WHITE = "FFFFFF"         # primary text
MUTED = "9AA0A6"         # secondary / year stamp
CODE_BG_RIGHT = "222222"  # inline code + code block on the black panel
CODE_BG_LEFT = "2A2A45"   # inline code on the navy panel
CODE_TEXT = "D6D9DF"      # code-block text (soft light; inline code uses ORANGE)
CALLOUT_BG = "1E1E1E"     # blockquote strip on the black panel
PLACEHOLDER = "232338"    # empty image placeholder on the navy panel

# --- Fonts --------------------------------------------------------------------

FONT_TITLE = "Calibri"        # rendered bold for titles
FONT_BODY = "Calibri"
FONT_LABEL = "Calibri"
FONT_MONO = "Consolas"

LINE_SPACING = 1.15

# --- Per-role font sizes (points) ---------------------------------------------

SIZE = {
    "section_label": 14,
    "slide_title": 36,
    "body": 20,
    "bullet": 18,
    "subbullet": 16,
    "numbered": 18,
    "subheading": 22,
    "callout": 18,
    "code": 14,
    "page_number": 11,
    "ts_title": 44,
    "ts_subtitle": 24,
    "year": 12,
}

# Floors for auto-fit: never shrink a role below this.
MIN_SIZE = {
    "slide_title": 18,
    "body": 12,
    "bullet": 11,
    "subbullet": 10,
    "numbered": 11,
    "subheading": 14,
    "callout": 11,
    "code": 9,
    "ts_title": 24,
    "ts_subtitle": 14,
}

# Approximate average glyph width as a fraction of the point size.
CHAR_FACTOR_PROPORTIONAL = 0.50
CHAR_FACTOR_MONO = 0.60


def char_factor(mono: bool = False) -> float:
    return CHAR_FACTOR_MONO if mono else CHAR_FACTOR_PROPORTIONAL


def estimate_lines(text: str, box_width_in: float, font_pt: float, mono: bool = False) -> int:
    """Estimate how many wrapped lines `text` occupies in a box of the given width."""
    if not text:
        return 1
    char_w_in = char_factor(mono) * font_pt / 72.0
    if char_w_in <= 0:
        return 1
    chars_per_line = max(1, int(box_width_in / char_w_in))
    total = 0
    for hard_line in text.split("\n"):
        total += max(1, math.ceil(len(hard_line) / chars_per_line))
    return max(1, total)


def line_height_in(font_pt: float, spacing: float = LINE_SPACING) -> float:
    return font_pt * spacing / 72.0


def text_height_in(
    text: str,
    box_width_in: float,
    font_pt: float,
    spacing: float = LINE_SPACING,
    mono: bool = False,
) -> float:
    """Estimated rendered height (inches) of `text` wrapped in a box."""
    return estimate_lines(text, box_width_in, font_pt, mono) * line_height_in(font_pt, spacing)


def fit_font_size(
    text: str,
    box_width_in: float,
    box_height_in: float,
    start_pt: int,
    min_pt: int,
    spacing: float = LINE_SPACING,
    mono: bool = False,
) -> int:
    """Return the largest font size <= start_pt that fits `text` in the box.

    Never returns below `min_pt`. This is a pure estimate (no rendering engine),
    intended as a safety net so long text does not overflow its bounds.
    """
    pt = int(start_pt)
    while pt > min_pt:
        if text_height_in(text, box_width_in, pt, spacing, mono) <= box_height_in:
            return pt
        pt -= 1
    return max(int(min_pt), pt)
