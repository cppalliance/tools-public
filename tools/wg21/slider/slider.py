"""Slider CLI: Markdown -> themed PowerPoint (.pptx).

Usage:
    uv run slider input.md -o output.pptx
    uv run slider input.md            # writes input.pptx next to the source
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys

from parser import parse_markdown
from renderer import build_presentation, save_presentation


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="slider",
        description="Convert a structured Markdown file into a themed PowerPoint deck.",
    )
    ap.add_argument("input", help="Path to the Markdown source file.")
    ap.add_argument("-o", "--output", help="Path to the output .pptx (default: alongside input).")
    ap.add_argument("--year", help="Year stamp for title slides (default: current year).")
    args = ap.parse_args(argv)

    in_path = args.input
    if not os.path.isfile(in_path):
        print(f"slider: input not found: {in_path}", file=sys.stderr)
        return 1

    out_path = args.output or os.path.splitext(in_path)[0] + ".pptx"
    year = args.year or str(_dt.date.today().year)
    base_dir = os.path.dirname(os.path.abspath(in_path))

    with open(in_path, encoding="utf-8") as fh:
        text = fh.read()

    slides = parse_markdown(text, base_dir=base_dir)
    if not slides:
        print("slider: no slides found (need at least one # or ## heading).", file=sys.stderr)
        return 1

    prs = build_presentation(slides, year=year)
    save_presentation(prs, out_path)

    n_title = sum(1 for s in slides if type(s).__name__ == "TitleSlide")
    n_content = len(slides) - n_title
    print(f"slider: wrote {out_path} ({len(slides)} slides: {n_title} title, {n_content} content)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
