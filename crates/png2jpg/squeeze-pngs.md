---
description: Convert PNG to JPEG at quality 50, rewrite markdown references
---

# squeeze-pngs

Convert PNG files to JPEG at quality 50, delete originals, rewrite `.png` to `.jpg` in sibling `.md` files when the PNG is under an `images/` directory.

Build if missing: `cargo.exe build --release` from `tools-public/crates/png2jpg/`. Binary: `target/release/png2jpg.exe`. Usage: `png2jpg <file.png> [file2.png ...]`.
