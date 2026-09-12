## Structure

- Directory entries with a leading slash in `.cursorindexingignore` are exactly the top-level directories not listed in README.md. Every other entry in that file (extension patterns such as `*.png`, and the unanchored `images/`) only excludes binary art from indexing; those entries do not affect the README.
- When a listed tool is added, moved, or removed, update README.md to reflect the change.
- `retired/` holds tools removed from the README. It may contain subgroups (for example `retired/wg21/`), each with its own `images/`. Retired tools are not listed in the README.

## Paired images

Some markdown files are paired with one or more images; the rest carry no image at all. A paired file's images live in an `images/` subdirectory of its own directory and are named from the markdown filename minus its extension:

- A single image is `images/<name>.png` or `images/<name>.jpg`.
- A numbered set is `images/<name>.1.jpg`, `images/<name>.2.jpg`, and so on (`.png` is also allowed). The number sits between the stem and the extension, separated by dots, so the stem is always the text before the first dot. Numbers start at 1 and are contiguous.

Tools listed in README.md are paired. Articles, READMEs, exhibits, chats, fixtures, and other supporting files are not. When in doubt, check whether `images/<name>.*` exists beside the file.

The rules below apply only to paired files.

- The markdown embeds each of its images with a markdown image reference: `![<alt>](images/<name>.png)`, `![<alt>](images/<name>.jpg)`, or `![<alt>](images/<name>.<n>.jpg)`. Never an HTML `<img>` tag, never an absolute URL, never a bare filename without `images/`, never a `../` prefix.
- The image travels with its file. On create, move, rename, or delete, the markdown and all of its images move together, never one without the other. Images always live in `images/`, never loose alongside the `.md` files.
- On retire, move the markdown and its images to `retired/` together and remove the file's README entry.
- If a paired file's image is missing, stop and ask. Do not proceed with a lone file.

## Hygiene

- Do not commit build or cache output. The root `.gitignore` excludes `__pycache__/`, `*.pyc`, `.pytest_cache/`, and Rust `target/` directories; subprojects may add their own `.gitignore` for their own artifacts.
- `artwork/` holds standalone images that pair with no markdown file. It is the only directory where images live outside an `images/` subdirectory.
