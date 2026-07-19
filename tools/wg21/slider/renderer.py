"""Slide data model -> .pptx via python-pptx.

Renders the objects produced by parser.py into a themed PowerPoint file.

Layout strategy for the right panel: instead of one text frame, each body
element (paragraph, subheading, bullet, callout, code block) is placed as its
own shape with a running vertical cursor. This gives per-element control -
real background rectangles behind code blocks and callouts, exact bullet
markers, and independent styling - and lets us estimate height per element for
auto-fit.
"""

from __future__ import annotations

import os
import re
import zipfile

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

import theme as T
from parser import (
    Bullet,
    Callout,
    CodeBlock,
    ContentSlide,
    Paragraph,
    Subheading,
    TextRun,
    TitleSlide,
    runs_to_plain,
)

_LATIN_ORDER = ("a:latin", "a:ea", "a:cs", "a:sym", "a:hlinkClick", "a:hlinkMouseOver", "a:rtl", "a:extLst")


def _rgb(hex_str: str) -> RGBColor:
    return RGBColor.from_string(hex_str)


def _no_line(shape) -> None:
    shape.line.fill.background()


def _kill_shadow(shape) -> None:
    try:
        shape.shadow.inherit = False
    except Exception:
        pass


def add_rect(slide, x, y, w, h, fill_hex):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = _rgb(fill_hex)
    _no_line(shape)
    _kill_shadow(shape)
    return shape


def _zero_margins(tf) -> None:
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0


def _set_highlight(run, hex_color: str) -> None:
    """Give a run a background highlight (used for inline code).

    python-pptx has no API for this, so we inject <a:highlight> into the run
    properties at the schema-correct position. Any failure degrades silently to
    plain colored text.
    """
    try:
        rpr = run._r.get_or_add_rPr()
        for existing in rpr.findall(qn("a:highlight")):
            rpr.remove(existing)
        hl = rpr.makeelement(qn("a:highlight"), {})
        srgb = rpr.makeelement(qn("a:srgbClr"), {"val": hex_color})
        hl.append(srgb)
        insert_before = None
        for child in rpr:
            if child.tag in (qn(t) for t in _LATIN_ORDER):
                insert_before = child
                break
        if insert_before is not None:
            insert_before.addprevious(hl)
        else:
            rpr.append(hl)
    except Exception:
        pass


def _apply_run(run, tr: TextRun, default_color: str, mono_bg: str | None, code_color: str) -> None:
    font = run.font
    is_code = tr.code
    font.name = T.FONT_MONO if is_code else T.FONT_BODY
    font.bold = tr.bold
    font.italic = tr.italic
    if tr.url:
        font.color.rgb = _rgb(T.ORANGE)
        font.underline = True
        try:
            run.hyperlink.address = tr.url
        except Exception:
            pass
    elif is_code:
        font.color.rgb = _rgb(code_color)
    else:
        font.color.rgb = _rgb(default_color)
    if is_code and mono_bg:
        _set_highlight(run, mono_bg)


def _fill_paragraph(p, runs, size_pt, default_color, mono_bg, align=PP_ALIGN.LEFT, code_color=T.ORANGE):
    p.alignment = align
    p.line_spacing = T.LINE_SPACING
    if not runs:
        runs = [TextRun("")]
    for tr in runs:
        # A run carrying a hard line break splits into separate runs; pptx runs
        # cannot contain newlines cleanly, so we split on them.
        parts = tr.text.split("\n")
        for i, part in enumerate(parts):
            if i > 0:
                p.add_line_break()
            r = p.add_run()
            r.text = part
            r.font.size = Pt(size_pt)
            _apply_run(r, TextRun(part, tr.bold, tr.italic, tr.code, tr.url), default_color, mono_bg, code_color)


def add_textbox(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP, wrap=True):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    _zero_margins(tf)
    return tb, tf


def _place_image_or_placeholder(slide, path, x, y, w, h):
    if path and os.path.isfile(path):
        try:
            slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
            return
        except Exception:
            pass
    add_rect(slide, x, y, w, h, T.PLACEHOLDER)


# --- Title / interstitial slide ----------------------------------------------


def render_title_slide(slide, s: TitleSlide, year: str):
    if s.image_path and os.path.isfile(s.image_path):
        _place_image_or_placeholder(slide, s.image_path, 0, 0, T.SLIDE_W, T.SLIDE_H)
    else:
        add_rect(slide, 0, 0, T.SLIDE_W, T.SLIDE_H, T.NAVY)

    x, y, w, h = T.TS_TITLE_BOX
    title_text = runs_to_plain(s.title)
    size = T.fit_font_size(title_text, w, h, T.SIZE["ts_title"], T.MIN_SIZE["ts_title"])
    tb, tf = add_textbox(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP)
    _fill_paragraph(tf.paragraphs[0], _forced_bold(s.title), size, T.WHITE, None)

    if s.subtitle:
        sx, sy, sw, sh = T.TS_SUBTITLE_BOX
        ssize = T.fit_font_size(s.subtitle, sw, sh, T.SIZE["ts_subtitle"], T.MIN_SIZE["ts_subtitle"])
        _, stf = add_textbox(slide, sx, sy, sw, sh)
        _fill_paragraph(stf.paragraphs[0], [TextRun(s.subtitle, italic=True)], ssize, T.ORANGE, None)

    yx, yy, yw, yh = T.TS_YEAR_BOX
    _, ytf = add_textbox(slide, yx, yy, yw, yh, anchor=MSO_ANCHOR.BOTTOM)
    _fill_paragraph(ytf.paragraphs[0], [TextRun(year)], T.SIZE["year"], T.MUTED, None)


def _forced_bold(runs: list[TextRun]) -> list[TextRun]:
    """Titles render bold by default; keep italics/code but force bold on."""
    return [TextRun(r.text, True, r.italic, r.code, r.url) for r in runs]


# --- Content slide ------------------------------------------------------------


def render_content_slide(slide, s: ContentSlide, page_no: int, total: int):
    add_rect(slide, 0, 0, T.LEFT_W, T.SLIDE_H, T.NAVY)
    add_rect(slide, T.RIGHT_X, 0, T.RIGHT_W, T.SLIDE_H, T.BLACK)

    _place_image_or_placeholder(slide, s.image_path, T.IMG_X, T.IMG_Y, T.IMG_W, T.IMG_H)

    # Section label.
    lx, ly, lw, lh = T.SECTION_LABEL_BOX
    _, ltf = add_textbox(slide, lx, ly, lw, lh)
    _fill_paragraph(ltf.paragraphs[0], [TextRun(s.section_label, bold=True)], T.SIZE["section_label"], T.ORANGE, None)

    # Slide title (auto-fit to the box above the image).
    tx, ty, tw, th = T.TITLE_BOX
    title_text = runs_to_plain(s.title)
    tsize = T.fit_font_size(title_text, tw, th, T.SIZE["slide_title"], T.MIN_SIZE["slide_title"])
    _, ttf = add_textbox(slide, tx, ty, tw, th)
    _fill_paragraph(ttf.paragraphs[0], _forced_bold(s.title), tsize, T.WHITE, None)

    _render_body(slide, s.body)

    # Page number.
    px, py, pw, ph = T.PAGENO_BOX
    _, ptf = add_textbox(slide, px, py, pw, ph, anchor=MSO_ANCHOR.BOTTOM)
    _fill_paragraph(ptf.paragraphs[0], [TextRun(f"{page_no} / {total}")], T.SIZE["page_number"], T.MUTED, PP_ALIGN.RIGHT)


# --- Right-panel body flow ----------------------------------------------------

_MARKER_SQUARE = "\u25AA"  # black small square
_MARKER_CIRCLE = "\u2022"  # bullet


def _body_scale(body) -> float:
    """Global shrink factor so the whole body fits the content height."""
    total = _estimate_body_height(body, 1.0)
    if total <= T.CONTENT_H or total <= 0:
        return 1.0
    return max(0.5, T.CONTENT_H / total)


def _role_size(role: str, scale: float) -> int:
    base = T.SIZE[role]
    floor = T.MIN_SIZE.get(role, 8)
    return max(floor, int(round(base * scale)))


def _elem_text(el) -> tuple[str, str]:
    if isinstance(el, CodeBlock):
        return el.text, "code"
    if isinstance(el, Subheading):
        return runs_to_plain(el.runs), "subheading"
    if isinstance(el, Callout):
        return runs_to_plain(el.runs), "callout"
    if isinstance(el, Bullet):
        role = "subbullet" if el.level > 0 else ("numbered" if el.ordered else "bullet")
        return runs_to_plain(el.runs), role
    if isinstance(el, Paragraph):
        return runs_to_plain(el.runs), "body"
    return "", "body"


def _elem_width(el) -> float:
    indent = 0.0
    if isinstance(el, Bullet):
        indent = 0.35 + el.level * 0.3
    elif isinstance(el, (Callout, CodeBlock)):
        indent = 0.0
    return max(1.0, T.CONTENT_W - indent)


def _elem_height(el, size_pt: int, width: float) -> float:
    text, role = _elem_text(el)
    mono = role == "code"
    h = T.text_height_in(text, width, size_pt, mono=mono)
    if isinstance(el, (Callout, CodeBlock)):
        h += 0.28  # internal padding of the box
    return h


def _gap_before(el) -> float:
    if isinstance(el, Subheading):
        return 0.20
    if isinstance(el, (Callout, CodeBlock)):
        return 0.14
    return 0.08


def _estimate_body_height(body, scale: float) -> float:
    y = 0.0
    for el in body:
        _, role = _elem_text(el)
        size = _role_size(role, scale)
        y += _gap_before(el) + _elem_height(el, size, _elem_width(el))
    return y


def _render_body(slide, body):
    scale = _body_scale(body)
    y = T.CONTENT_Y
    for el in body:
        y += _gap_before(el)
        _, role = _elem_text(el)
        size = _role_size(role, scale)
        width = _elem_width(el)

        if isinstance(el, CodeBlock):
            h = _elem_height(el, size, width)
            add_rect(slide, T.CONTENT_X, y, T.CONTENT_W, h, T.CODE_BG_RIGHT)
            _, tf = add_textbox(slide, T.CONTENT_X + 0.15, y + 0.12, T.CONTENT_W - 0.3, h - 0.24)
            first = True
            for line in el.text.split("\n"):
                p = tf.paragraphs[0] if first else tf.add_paragraph()
                first = False
                _fill_paragraph(p, [TextRun(line, code=True)], size, T.WHITE, None, code_color=T.CODE_TEXT)
            y += h
            continue

        if isinstance(el, Callout):
            h = _elem_height(el, size, width)
            add_rect(slide, T.CONTENT_X, y, T.CONTENT_W, h, T.CALLOUT_BG)
            add_rect(slide, T.CONTENT_X, y, 0.06, h, T.ORANGE)
            _, tf = add_textbox(slide, T.CONTENT_X + 0.25, y + 0.12, T.CONTENT_W - 0.4, h - 0.24)
            italic_runs = [TextRun(r.text, r.bold, True, r.code, r.url) for r in el.runs]
            _fill_paragraph(tf.paragraphs[0], italic_runs, size, T.WHITE, T.CODE_BG_RIGHT)
            y += h
            continue

        if isinstance(el, Subheading):
            h = _elem_height(el, size, width)
            _, tf = add_textbox(slide, T.CONTENT_X, y, T.CONTENT_W, h)
            _fill_paragraph(tf.paragraphs[0], _forced_bold(el.runs), size, T.WHITE, None)
            y += h
            continue

        if isinstance(el, Bullet):
            indent = 0.35 + el.level * 0.3
            h = _elem_height(el, size, width)
            # Marker.
            if el.ordered and el.number is not None:
                marker = f"{el.number}."
            elif el.level > 0:
                marker = _MARKER_CIRCLE
            else:
                marker = _MARKER_SQUARE
            _, mtf = add_textbox(slide, T.CONTENT_X + (indent - 0.32), y, 0.32, h)
            _fill_paragraph(mtf.paragraphs[0], [TextRun(marker, bold=True)], size, T.ORANGE, None)
            # Text.
            _, ttf = add_textbox(slide, T.CONTENT_X + indent, y, T.CONTENT_W - indent, h)
            color = T.ORANGE if el.highlight else T.WHITE
            runs = el.runs
            if el.highlight:
                runs = [TextRun(r.text, True, r.italic, r.code, r.url) for r in el.runs]
            _fill_paragraph(ttf.paragraphs[0], runs, size, color, T.CODE_BG_RIGHT)
            y += h
            continue

        if isinstance(el, Paragraph):
            h = _elem_height(el, size, width)
            _, tf = add_textbox(slide, T.CONTENT_X, y, T.CONTENT_W, h)
            _fill_paragraph(tf.paragraphs[0], el.runs, size, T.WHITE, T.CODE_BG_RIGHT)
            y += h
            continue


# --- Speaker notes ------------------------------------------------------------


def _apply_notes(slide, notes: list[str]) -> None:
    """Write speaker notes into the slide's notes pane, one paragraph per entry.

    Accessing `slide.notes_slide` lazily creates the notes slide, so slides with
    no notes never get a notes page at all.
    """
    if not notes:
        return
    tf = slide.notes_slide.notes_text_frame
    for i, para in enumerate(notes):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = para


# --- Deck ---------------------------------------------------------------------


def build_presentation(slides, year: str) -> Presentation:
    prs = Presentation()
    prs.slide_width = Inches(T.SLIDE_W)
    prs.slide_height = Inches(T.SLIDE_H)
    blank = prs.slide_layouts[6]

    total = len(slides)
    for i, s in enumerate(slides):
        slide = prs.slides.add_slide(blank)
        if isinstance(s, TitleSlide):
            render_title_slide(slide, s, year)
        else:
            render_content_slide(slide, s, i + 1, total)
        _apply_notes(slide, getattr(s, "notes", []))
    return prs


def _patch_theme_hyperlinks(path: str, hex_color: str) -> None:
    """Rewrite the theme's hyperlink colors so links render in the accent color.

    PowerPoint and LibreOffice color hyperlinked runs from the theme's hlink /
    folHlink slots rather than the run's own fill, which would otherwise show
    links in the default theme blue. We patch the theme parts in the saved file.
    """
    try:
        tmp = path + ".tmp"
        pat = re.compile(r"<a:(hlink|folHlink)>.*?</a:\1>", re.DOTALL)

        def repl(m):
            tag = m.group(1)
            return f'<a:{tag}><a:srgbClr val="{hex_color}"/></a:{tag}>'

        with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.startswith("ppt/theme/") and item.filename.endswith(".xml"):
                    data = pat.sub(repl, data.decode("utf-8")).encode("utf-8")
                zout.writestr(item, data)
        os.replace(tmp, path)
    except Exception:
        # Cosmetic only; never fail a build over link color.
        if os.path.exists(path + ".tmp"):
            os.remove(path + ".tmp")


def save_presentation(prs: Presentation, path: str) -> None:
    prs.save(path)
    _patch_theme_hyperlinks(path, T.ORANGE)
