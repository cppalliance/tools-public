"""Style loading, the inherits cascade, frontmatter resolution, and spacing.

A style is a plain dict loaded from a YAML file in `styles/`. `default.yaml`
holds every key; other styles set `inherits:` and override a subset. A deck's
own frontmatter `theme:` block sits at the top of the cascade: it names a base
to inherit and deep-merges its own overrides on top.
"""

from __future__ import annotations

import os
import re

import yaml

STYLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles")

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def em(size_pt: float, r: float) -> float:
    """Inches for a spacing ratio expressed in ems of a font size."""
    return size_pt * r / 72.0


def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base. Dicts merge; scalars and lists replace."""
    out = dict(base)
    for k, v in override.items():
        if isinstance(out.get(k), dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _style_path(name_or_path: str) -> str:
    if os.path.isfile(name_or_path):
        return name_or_path
    candidate = os.path.join(STYLES_DIR, f"{name_or_path}.yaml")
    if os.path.isfile(candidate):
        return candidate
    raise FileNotFoundError(f"style not found: {name_or_path}")


def load_style(name_or_path: str, _loading: set | None = None) -> dict:
    """Load a style dict, resolving its `inherits:` chain."""
    path = _style_path(name_or_path)
    _loading = _loading or set()
    key = os.path.abspath(path)
    if key in _loading:
        raise ValueError(f"circular style inheritance at {name_or_path}")
    _loading.add(key)

    with open(path, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    base_name = raw.pop("inherits", None)
    if base_name is None:
        return raw
    return deep_merge(load_style(base_name, _loading), raw)


def load_default() -> dict:
    return load_style("default")


def extract_frontmatter(text: str) -> tuple[dict, str]:
    """Split a leading `--- ... ---` YAML block from the markdown body."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, text[m.end():]


def _check_override_keys(base: dict, override: dict, trail: str = "") -> None:
    # A key absent from the base is a typo (e.g. colors.oragne); fail loudly
    # rather than silently deep-merging a dead value the renderer never reads.
    for k, v in override.items():
        where = f"{trail}.{k}" if trail else k
        if k not in base:
            raise KeyError(f"unknown style override: {where}")
        if isinstance(v, dict) and isinstance(base[k], dict):
            _check_override_keys(base[k], v, where)


def resolve(cli_style: str | None, fm_theme: dict | None) -> dict:
    """Build the effective style from the CLI flag and a deck's `theme:` block.

    Base selection, highest priority first: CLI --style, then theme.inherits,
    then default. Frontmatter overrides (theme minus `inherits`) merge on top.
    """
    fm_theme = fm_theme or {}
    base_name = cli_style or fm_theme.get("inherits") or "default"
    cfg = load_style(base_name)
    overrides = {k: v for k, v in fm_theme.items() if k != "inherits"}
    if overrides:
        _check_override_keys(cfg, overrides)
        cfg = deep_merge(cfg, overrides)
    return cfg
