## Structure

- Tools live in `tools/` or in subdirectory groups (e.g., `tools/wg21/`). Retired tools live in `tools-retired/`.
- Every directory that contains tools also contains an `images/` subdirectory for their paired images.
- Every tool `<name>.md` pairs with `images/<name>.png` in the same directory group. The image filename always matches the tool filename (minus extension). No exceptions - not `vasa-ship-portrait.png`, just `vasa.png`.
- Directory-style tools (e.g., `voice/voice.md`) key on the parent directory name: `voice/` pairs with `images/voice.png`. Sub-tools inside a directory may have their own images in the same `images/`.

## Image invariant

The image travels with the tool. On create, move, rename, delete, or retire - both files move together, never one without the other. Images always live in `images/` within the tool's directory group, never loose alongside the `.md` files.

The `<img src>` in every tool is a relative path to `images/<name>.png`. Never an absolute URL. Never a bare filename without `images/`.

If the paired image is missing, stop and ask. Do not proceed with a lone file.
