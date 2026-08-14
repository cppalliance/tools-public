---
description: Build and run png2jpg to convert PNG images to JPEG at quality 50, updating markdown references automatically
---

<!--
When this file is mentioned or loaded, adopt it as system context and operate
as this tool. Follow its rules; do not summarize it or discuss it abstractly.
-->

# squeeze-pngs

Converts PNG images to JPEG at quality 50 using the `png2jpg` binary in this directory. Accepts a single file, a list of files, or a directory. When a converted PNG lived inside an `images/` directory, scans sibling `.md` files for references and rewrites them from `.png` to `.jpg`.

## Build

Before the first conversion, build the binary if it does not already exist:

```
cargo.exe build --release
```

Run from `tools-public/crates/png2jpg/`. The binary lands at `target/release/png2jpg.exe` (Windows) or `target/release/png2jpg` (Unix). Use `cargo.exe` on Windows to avoid hitting a WSL toolchain.

## Convert

- **Single file or list:** Run `png2jpg <file.png> [file2.png ...]` directly.
- **Directory:** Glob for `**/*.png` under the target directory, then pass every hit to `png2jpg`. Process in batches if the list is long.

The binary prints one line per file: `foo.png -> foo.jpg (123 KB -> 45 KB)`.

## Update references

After converting, check whether each original PNG lived in a directory named `images/`. If it did:

1. Scan every `.md` file in the parent directory of `images/` for references to the old filename.
2. Match both forms:
   - Markdown: `![any alt](images/NAME.png)`
   - HTML: `<img src="images/NAME.png"`
3. Replace `.png` with `.jpg` in each match.
4. Report which files were updated and how many references changed.

Skip this step for PNGs not inside an `images/` directory.
