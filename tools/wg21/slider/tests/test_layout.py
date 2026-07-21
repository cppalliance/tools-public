"""Pure layout math and geometry resolution."""

import pytest

import layout
import style


def _cfg():
    return style.load_default()


def test_text_height_grows_with_length():
    cfg = _cfg()
    short = layout.text_height_in(cfg, "one line", 8.0, 20)
    long = layout.text_height_in(cfg, "word " * 200, 8.0, 20)
    assert long > short


def test_text_height_grows_with_font_size():
    cfg = _cfg()
    small = layout.text_height_in(cfg, "word " * 40, 8.0, 12)
    big = layout.text_height_in(cfg, "word " * 40, 8.0, 28)
    assert big > small


def test_fit_font_size_never_below_floor():
    cfg = _cfg()
    size = layout.fit_font_size(cfg, "word " * 500, 2.0, 0.5, start_pt=36, min_pt=18)
    assert size == 18


def test_fit_font_size_keeps_start_when_it_fits():
    cfg = _cfg()
    size = layout.fit_font_size(cfg, "short", 8.0, 5.0, start_pt=36, min_pt=18)
    assert size == 36


def test_geometry_boxes_are_sane():
    cfg = _cfg()
    g = layout.geometry(cfg)
    sw = cfg["slide"]["width"]
    left_w = g.left_panel[2]
    assert 0 < left_w < sw
    assert g.content[2] > 0 and g.content[3] > 0
    # Image sits flush to the bottom of the slide.
    assert round(g.image[1] + g.image[3], 3) == cfg["slide"]["height"]


def test_geometry_is_image_dominant_with_title_on_the_right():
    cfg = _cfg()
    g = layout.geometry(cfg)
    sw = cfg["slide"]["width"]
    left_w = g.left_panel[2]
    # Left (navy + image) panel is now the majority of the slide.
    assert left_w > sw / 2
    # Title and body both live on the right panel, past the left edge.
    assert g.title[0] >= left_w
    assert g.content[0] >= left_w
    # Body starts below the title box.
    assert g.content[1] >= g.title[1] + g.title[3]


def test_estimate_lines_falls_back_to_char_factor_without_font():
    cfg = _cfg()
    text = "word " * 30
    cw = cfg["text"]["char_factor"]
    expected = layout.estimate_lines(text, 4.0, 20, cw, font_family=None)
    # A family that cannot resolve must fall back to the identical estimate.
    got = layout.estimate_lines(text, 4.0, 20, cw, font_family="No Such Font 12345")
    assert got == expected


def test_measured_font_is_tighter_than_char_factor_at_boundary():
    cfg = _cfg()
    # The exact string that overcounted by a line under char_factor at the
    # old right-panel width (~7.27in): char_factor said 3, the font fits 2.
    text = ("The Iron Law of Bureaucracy: control flows to those who "
            "prioritize the organization over the mission.")
    box_w = 7.266
    cw = cfg["text"]["char_factor"]
    estimated = layout.estimate_lines(text, box_w, 20, cw, font_family=None)
    if layout._resolve_font(cfg["fonts"]["body"], 20) is None:
        pytest.skip("body font not installed; measurement path unavailable")
    measured = layout.estimate_lines(text, box_w, 20, cw, font_family=cfg["fonts"]["body"])
    assert measured <= estimated
    assert measured == 2
