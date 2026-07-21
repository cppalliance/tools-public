"""Style loading, the inherits cascade, and frontmatter resolution."""

import os

import pytest

import style

_HERE = os.path.dirname(os.path.abspath(__file__))


def test_default_loads_with_all_top_level_keys():
    cfg = style.load_default()
    required = {
        "slide", "panels", "title_slide", "content", "page_number",
        "colors", "fonts", "sizes", "min_sizes", "text", "body", "markers",
    }
    assert required <= set(cfg)


def test_inherits_overrides_one_value_and_keeps_the_rest(tmp_path):
    derived = tmp_path / "derived.yaml"
    derived.write_text('inherits: default\ncolors:\n  orange: "D64500"\n', encoding="utf-8")
    cfg = style.load_style(str(derived))
    assert cfg["colors"]["orange"] == "D64500"
    assert cfg["colors"]["navy"] == style.load_default()["colors"]["navy"]


def test_resolve_applies_frontmatter_override():
    cfg = style.resolve(None, {"inherits": "default", "colors": {"orange": "D64500"}})
    assert cfg["colors"]["orange"] == "D64500"
    assert cfg["colors"]["navy"] == style.load_default()["colors"]["navy"]


def test_resolve_without_theme_is_plain_default():
    assert style.resolve(None, None) == style.load_default()


def test_resolve_rejects_unknown_override_key():
    with pytest.raises(KeyError):
        style.resolve(None, {"colors": {"oragne": "x"}})


def test_extract_frontmatter_splits_theme_block():
    text = '---\nstyle: "art"\ntheme:\n  inherits: default\n---\n# Title\nbody\n'
    fm, body = style.extract_frontmatter(text)
    assert fm["style"] == "art"
    assert fm["theme"]["inherits"] == "default"
    assert body.startswith("# Title")


def test_extract_frontmatter_absent_returns_whole_text():
    fm, body = style.extract_frontmatter("# No frontmatter\n")
    assert fm == {}
    assert body == "# No frontmatter\n"
