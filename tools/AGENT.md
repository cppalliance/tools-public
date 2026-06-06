# tools

Public tool prompts. Each tool is either a `<name>.md` file or a `<name>/` directory containing `<name>.md` plus supporting data. Both forms have a corresponding `images/<name>.png`.

## Image pairing rule

Every tool must have a matching `images/<name>.png`. When moving a tool in or out of this directory, move its image with it. Never move one without the other.

- **Removing a tool:** move or delete both the tool (`.md` or directory) and `images/<name>.png`.
- **Adding a tool:** place both the tool and `images/<name>.png` here.
- **Directory-style tools:** the image key is the directory name. `voice/` pairs with `images/voice.png`. Sub-tools inside a directory (e.g. `voice/voice-of-*.md`) may have their own images in the same `images/` directory.

If an image is missing, stop and ask rather than proceeding with a lone file.
