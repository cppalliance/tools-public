# Slider

Convert a structured Markdown file into a themed PowerPoint (`.pptx`) deck.

Slider is the rendering engine. The conversational workflow (planning a deck,
choosing an art style, generating images) lives in the tool spec at
[`../slider.md`](../slider.md). This README covers the CLI and the markdown
format.

## Install / run

Requires [`uv`](https://docs.astral.sh/uv/). Dependencies (`python-pptx`,
`mistune`, `pyyaml`, `Pillow`) are declared in `pyproject.toml` and installed
automatically.

```bash
# from this directory
uv run slider slides.md -o slides.pptx

# or from anywhere
uv run --project tools-public/tools/wg21/slider slider slides.md -o slides.pptx
```

If `-o` is omitted, the output is written next to the input with a `.pptx`
extension. `--year` overrides the year stamp on title slides (defaults to the
current year). `--style` selects a layout style (see [Styling](#styling)).

## Slide types

- `#` heading -> **title / interstitial** slide: full-bleed background image (or
  a solid background fallback), large title, italic subtitle, year stamp.
- `##` heading -> **content** slide: image-dominant. A wide navy left panel
  (section label at the top + a large 4:3 image flush to the bottom) and a
  narrower right panel holding the centered title above the body.

The body of a content slide starts after a `---` separator. A further `---`
begins the slide's speaker notes (see [Speaker notes](#speaker-notes)).

## Markdown constructs

| Markdown | Renders as |
|---|---|
| `#` | Title / interstitial slide; following paragraph is the subtitle |
| `##` | Content slide; heading text is the section label (uppercased) |
| First paragraph after `##` | Slide title (right panel, large and centered) |
| `###` | Subheading in the right panel |
| `---` (first on a content slide) | Separator between the left panel and the right-panel body |
| `---` (after the body; or the only `---` on a title slide) | Begins the slide's speaker notes |
| paragraph | Body text |
| `*italic*` | Italic (italic font, dimmed in body; keeps its color in the subtitle and links) |
| `**bold**` | Bold |
| `***bold italic***` | Bold italic |
| `` `code` `` | Monospace with a lighter background |
| `[text](url)` | Underlined orange link |
| `- item` | Bullet (orange square marker, orange text) |
| `- **item**` | Highlight bullet (orange square marker, orange bold text) |
| nested `- item` | Indented sub-bullet (circle marker) |
| `1. item` | Numbered item (orange number, orange text) |
| `> quote` | Callout box with an orange left border |
| ```` ```code``` ```` | Code block on a lighter background |
| `<!-- ... -->` | Image-generation prompt for the LLM; ignored by Slider |
| `![alt](path)` / `<img src>` | Image (left panel on content slides, full-bleed on title slides) |
| `style:` frontmatter | Art-style hint for the LLM (image generation); ignored by Slider |
| `theme:` frontmatter | Layout style: inherit a built-in style and override values (see [Styling](#styling)) |

Image paths are resolved relative to the markdown file. A missing image simply
leaves the background showing, so a deck can be built before the art exists.

## Auto-fit

Every title is measured against its box and its font size is reduced (down to a
per-role floor) if it would overflow. The right-panel body is measured as a
whole and scaled down proportionally if it would not fit. The estimate is pure
arithmetic - no rendering engine required.

## Body spacing

Right-panel elements are stacked by a running vertical cursor. Between two
elements of the same family the cursor advances by the base inter-element gap
(`text.gap_ratio` of the following element's line height). When the element
family changes - paragraph to list, list to callout, anything to a subheading -
the boundary gets one extra full line height of the following element, so blocks
separate visibly instead of reading as one run of text. All list items (bullets,
sub-bullets, numbered items) are one family, so nested and mixed lists stay
tight. Every list item is orange; paragraphs are white. The extra gap is folded
into the same measurement the auto-fit scale uses, so a size change rescales it
automatically.

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

## Styling

Every appearance value - dimensions, colors, fonts, sizes, spacing - lives in a
YAML style file under `styles/`. `styles/default.yaml` holds every key; the
Python reads from it and contains no appearance numbers. Canvas and panel
geometry is in absolute inches; body micro-spacing (indents, box padding, the
inter-element gap) is an em ratio multiplied by the element's font size, so a
size change rescales spacing automatically.

A style can inherit another and override a subset:

```yaml
inherits: default
colors:
  orange: "D64500"
```

A deck selects and overrides a style from its own frontmatter, without a
separate file, via a `theme:` block (distinct from the art-style `style:` key,
which is an image-generation hint the renderer ignores):

```yaml
---
style: "1920s editorial cartoon, sepia, hand-lettered captions"   # art style (ignored here)
theme:
  inherits: default        # a built-in style in styles/ (default if omitted)
  colors:
    orange: "D64500"       # deep-merged onto the inherited style
  sizes:
    slide_title: 40
---
```

The cascade, low to high: `styles/default.yaml`, then the base named by
`--style` (else `theme.inherits`, else `default`), then the frontmatter `theme:`
overrides. An override key absent from the base is rejected, catching typos.

## Image compression

PNG images are re-encoded to JPEG in memory as they are embedded, so the
`.pptx` stays small without any change to the PNG files on disk. The behavior is
the style key `images.jpeg_quality`, on a 0-9 scale:

| Value | Effect |
|---|---|
| `0` | Off - PNGs are embedded unchanged |
| `1` | Maximum compression (smallest file, lowest quality) |
| `5` | Default - balanced size and quality |
| `9` | Minimal compression (largest file, highest quality) |

Only PNG sources are converted; images already in another format are embedded
as-is. Transparent regions are flattened onto the slide background color
(`colors.background`) during conversion, and a conversion failure falls back to
embedding the original PNG. Like any style value, it can be changed per deck in
a `theme:` block or in a custom style file:

```yaml
---
theme:
  images:
    jpeg_quality: 0    # keep PNGs uncompressed for this deck
---
```

## Testing

```bash
uv run --project tools-public/tools/wg21/slider pytest
```

Tests live in `tests/`. `tests/golden/notes.md` is the golden fixture that
exercises every speaker-notes case (title and content slides, with and without
notes, rich notes, notes to end-of-file); `tests/test_notes.py` asserts both the
parsed model and the notes written into a rebuilt `.pptx`, and guards that
existing single-`---` decks (`test.md`) are unaffected. `tests/test_spacing.py`
covers the inter-block spacing rule: same-family boundaries keep the base gap,
family transitions add one line height, and the auto-fit scale accounts for both.

## Files

- `slider.py` - CLI entry point
- `parser.py` - Markdown -> slide data model (mistune AST walk)
- `style.py` - style loading, the `inherits:` cascade, frontmatter resolution, `em()`
- `layout.py` - pure fit math and resolved slide geometry (no pptx)
- `draw.py` - pptx drawing primitives (rectangles, text boxes, run styling, boxes, images)
- `renderer.py` - slide composition -> `.pptx`, using `draw` and `layout`
- `styles/` - YAML style files (`default.yaml` is the complete base)
- `test.md` - exercises every supported construct
- `tests/` - pytest suite and golden fixtures
