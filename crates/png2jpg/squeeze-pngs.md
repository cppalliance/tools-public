---
description: Convert PNG to JPEG at quality 50, resize to 1024 width, rewrite markdown references
---

# squeeze-pngs

Convert PNG files to JPEG at quality 50, keeping the originals. Images wider than 1024 pixels are resized proportionally to 1024 wide; alpha channels are flattened onto white. When the PNG sits under an `images/` directory, `images/<name>.png` is rewritten to `images/<name>.jpg` in every `.md` file in the parent directory.

Build if missing: `cargo.exe build --release` from `tools-public/crates/png2jpg/`. Binary: `target/release/png2jpg.exe`. Usage: `png2jpg <file.png> [file2.png ...]`.
