# Slider

Convert a structured Markdown file into a themed PowerPoint (`.pptx`) deck.

Slider is the rendering engine. The conversational workflow (planning a deck,
choosing an art style, generating images) lives in the tool spec at
[`../slider.md`](../slider.md). This README covers the CLI and the markdown
format.

## Install / run

Requires [`uv`](https://docs.astral.sh/uv/). Dependencies (`python-pptx`,
`mistune`) are declared in `pyproject.toml` and installed automatically.

```bash
# from this directory
uv run slider slides.md -o slides.pptx

# or from anywhere
uv run --project tools-public/tools/wg21/slider slider slides.md -o slides.pptx
```

If `-o` is omitted, the output is written next to the input with a `.pptx`
extension. `--year` overrides the year stamp on title slides (defaults to the
current year).

## Slide types

- `#` heading -> **title / interstitial** slide: full-bleed background image (or
  navy fallback), large white title, orange italic subtitle, year stamp.
- `##` heading -> **content** slide: navy left panel (section label + title +
  4:3 image flush to the bottom) and a black right panel holding the body.

The body of a content slide starts after a `---` separator. A further `---`
begins the slide's speaker notes (see [Speaker notes](#speaker-notes)).

## Markdown constructs

| Markdown | Renders as |
|---|---|
| `#` | Title / interstitial slide; following paragraph is the subtitle |
| `##` | Content slide; heading text is the section label (uppercased) |
| First paragraph after `##` | Slide title (left panel) |
| `###` | Subheading in the right panel |
| `---` (first on a content slide) | Separator between the left panel and the right-panel body |
| `---` (after the body; or the only `---` on a title slide) | Begins the slide's speaker notes |
| paragraph | Body text |
| `*italic*` | Italic |
| `**bold**` | Bold |
| `***bold italic***` | Bold italic |
| `` `code` `` | Monospace with a lighter background |
| `[text](url)` | Underlined orange link |
| `- item` | Bullet (orange square marker, white text) |
| `- **item**` | Highlight bullet (orange square marker, orange bold text) |
| nested `- item` | Indented sub-bullet (circle marker) |
| `1. item` | Numbered item (orange number) |
| `> quote` | Callout box with an orange left border |
| ```` ```code``` ```` | Code block on a lighter background |
| `<!-- ... -->` | Image-generation prompt for the LLM; ignored by Slider |
| `![alt](path)` / `<img src>` | Image (left panel on content slides, full-bleed on title slides) |
| `style:` frontmatter | Art-style hint for the LLM; ignored by Slider |

Image paths are resolved relative to the markdown file. Missing images render as
a subtle placeholder rectangle so a deck can be built before art exists.

## Auto-fit

Every title is measured against its box and its font size is reduced (down to a
per-role floor) if it would overflow. The right-panel body is measured as a
whole and scaled down proportionally if it would not fit. The estimate is pure
arithmetic - no rendering engine required.

## Speaker notes

A slide's final `---` section is its speaker notes. On a **content** slide the
first `---` splits the left panel from the body, and a second `---` starts the
notes; on a **title / interstitial** slide (which has no body) a single `---`
starts the notes. Notes are ordinary visible Markdown - not an HTML comment - so
they show in any Markdown viewer, while the renderer writes them to the
PowerPoint notes pane instead of onto the slide.

Notes run until the next `#` or `##`. Each paragraph becomes its own note
paragraph; lists flatten to `- item` / `N. item` lines; inline emphasis is
dropped to plain text. A slide with no notes section gets no notes page at all.

```markdown
## THE RATCHET

First movers get a one-way valve

![ratchet](images/ratchet.png)

---

Once a chair declares consensus, reversal is near-impossible.

---

Pause here. Name the stakes before advancing - this is the slide that has to land.
```

## Testing

```bash
uv run --project tools-public/tools/wg21/slider pytest
```

Tests live in `tests/`. `tests/golden/notes.md` is the golden fixture that
exercises every speaker-notes case (title and content slides, with and without
notes, rich notes, notes to end-of-file); `tests/test_notes.py` asserts both the
parsed model and the notes written into a rebuilt `.pptx`, and guards that
existing single-`---` decks (`test.md`) are unaffected.

## Files

- `slider.py` - CLI entry point
- `parser.py` - Markdown -> slide data model (mistune AST walk)
- `renderer.py` - slide data model -> `.pptx` (python-pptx)
- `theme.py` - dimensions, colors, fonts, sizes, and the fit math
- `test.md` - exercises every supported construct
- `tests/` - pytest suite and golden fixtures
