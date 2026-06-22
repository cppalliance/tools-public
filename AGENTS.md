## Structure

- Tools live in `tools/` or in subdirectory groups (e.g., `tools/wg21/`). Retired tools live in `tools-retired/`.
- Dossiers live in `dossiers/`. These are composite behavioral models - aggregate profiles of populations, not individuals.
- Every directory that contains tools or dossiers also contains an `images/` subdirectory for their paired images.
- Every `.md` file pairs with `images/<name>.png` in the same directory group. The image filename always matches the `.md` filename (minus extension).
- Directory-style tools (e.g., `voice/voice.md`) key on the parent directory name: `voice/` pairs with `images/voice.png`. Sub-tools inside a directory may have their own images in the same `images/`.

## Image invariant

The image travels with its file. On create, move, rename, delete, or retire - both files move together, never one without the other. Images always live in `images/` within the file's directory group, never loose alongside the `.md` files.

The `<img src>` in every tool or dossier is a relative path to `images/<name>.png`. Never an absolute URL. Never a bare filename without `images/`.

If the paired image is missing, stop and ask. Do not proceed with a lone file.
