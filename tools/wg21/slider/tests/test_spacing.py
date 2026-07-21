"""Inter-block vertical spacing.

A boundary between two elements of the same family keeps the tight base gap;
a boundary where the family changes gets one extra line height of the following
element, so blocks read as separate. Both `_render_body` and `_body_scale`
share `_lead_gap`, so on-slide placement and auto-fit stay consistent.
"""

import layout
import renderer
import style
from parser import Bullet, Callout, CodeBlock, Paragraph, Subheading, TextRun


def _cfg():
    return style.load_default()


def _p(text):
    return Paragraph([TextRun(text)])


def _b(text, level=0, ordered=False, number=None):
    return Bullet([TextRun(text)], level=level, ordered=ordered, number=number)


def _size(cfg, el):
    return renderer._role_size(cfg, renderer._role(el), 1.0)


def test_first_element_has_no_leading_gap():
    cfg = _cfg()
    el = _p("first")
    assert renderer._lead_gap(cfg, None, el, _size(cfg, el)) == 0.0


def test_same_family_keeps_base_gap():
    cfg = _cfg()
    el = _b("second bullet")
    size = _size(cfg, el)
    assert renderer._lead_gap(cfg, _b("first bullet"), el, size) == renderer._gap(cfg, size)


def test_family_transition_adds_one_line_height():
    cfg = _cfg()
    el = _b("bullet after paragraph")
    size = _size(cfg, el)
    base = renderer._gap(cfg, size)
    trans = renderer._lead_gap(cfg, _p("prev paragraph"), el, size)
    assert trans == base + layout.line_height_in(cfg, size)
    assert trans > base


def test_nested_bullet_stays_tight():
    cfg = _cfg()
    sub = _b("nested", level=1)
    size = _size(cfg, sub)
    # parent bullet -> nested sub-bullet is the same 'list' family
    assert renderer._lead_gap(cfg, _b("parent"), sub, size) == renderer._gap(cfg, size)


def test_bullet_to_numbered_stays_tight():
    cfg = _cfg()
    num = _b("step one", ordered=True, number=1)
    size = _size(cfg, num)
    assert renderer._lead_gap(cfg, _b("plain bullet"), num, size) == renderer._gap(cfg, size)


def test_distinct_block_families_each_transition():
    cfg = _cfg()
    para, sub, call, code = _p("p"), Subheading([TextRun("s")]), Callout([TextRun("c")]), CodeBlock("x = 1")
    assert renderer._family(para) != renderer._family(sub)
    assert renderer._family(sub) != renderer._family(call)
    assert renderer._family(call) != renderer._family(code)
    size = _size(cfg, sub)
    assert renderer._lead_gap(cfg, para, sub, size) > renderer._gap(cfg, size)


def test_body_scale_shrinks_overfull_body():
    cfg = _cfg()
    body = [_p("word " * 40) for _ in range(12)]
    scale = renderer._body_scale(cfg, body, content_w=6.0, content_h=3.0)
    assert cfg["text"]["min_body_scale"] <= scale < 1.0


def test_body_scale_transition_costs_height():
    cfg = _cfg()
    # Same elements, but alternating families forces a transition at every join,
    # so the mixed body is taller and scales at least as small as the uniform one.
    uniform = [_p("word " * 8) for _ in range(6)]
    mixed = []
    for i in range(6):
        mixed.append(_p("word " * 8) if i % 2 == 0 else _b("word " * 8))
    su = renderer._body_scale(cfg, uniform, content_w=4.0, content_h=1.5)
    sm = renderer._body_scale(cfg, mixed, content_w=4.0, content_h=1.5)
    assert sm <= su
