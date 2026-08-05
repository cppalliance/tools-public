#!/usr/bin/env python3
"""Generate .claude-plugin/plugin.json from the lists in install.sh.

The installer and the plugin manifest describe the same set of tools. Keeping
two hand-maintained lists is what let install.sh drift out of sync with the tree
for months, so install.sh stays the single source of truth and this regenerates
the manifest from it.

  ./scripts/sync_plugin_manifest.py            rewrite the manifest
  ./scripts/sync_plugin_manifest.py --check    exit 1 if it is stale (used in CI)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTALL_SH = ROOT / "install.sh"
MANIFEST = ROOT / ".claude-plugin" / "plugin.json"


def bash_array(source: str, name: str) -> list[str]:
    """Pull the entries out of a NAME=( ... ) block, ignoring comments."""
    match = re.search(rf"^{name}=\((.*?)^\)", source, re.S | re.M)
    if not match:
        raise SystemExit(f"{INSTALL_SH.name}: could not find the {name} array")
    return [
        line.strip()
        for line in match.group(1).splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def build_manifest() -> dict:
    source = INSTALL_SH.read_text()

    commands = [f"./{path}" for path in bash_array(source, "TOP_LEVEL")]
    for family in bash_array(source, "FAMILIES"):
        # The parent prompt sits next to the directory of its sub-prompts.
        commands.append(f"./{family}.md")
        commands.append(f"./{family}/")
    skills = [f"./{path}/" for path in bash_array(source, "SKILLS")]

    existing = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    # Preserve hand-edited metadata, replace only the generated lists.
    return {**existing, "commands": commands, "skills": skills}


def main(argv: list[str]) -> int:
    manifest = build_manifest()
    rendered = json.dumps(manifest, indent=2) + "\n"

    if "--check" in argv:
        current = MANIFEST.read_text() if MANIFEST.exists() else ""
        if current != rendered:
            print(
                f"{MANIFEST.relative_to(ROOT)} is out of sync with {INSTALL_SH.name}.\n"
                f"Run ./scripts/{Path(__file__).name} and commit the result.",
                file=sys.stderr,
            )
            return 1
        print(f"{MANIFEST.relative_to(ROOT)} is up to date.")
        return 0

    MANIFEST.parent.mkdir(exist_ok=True)
    MANIFEST.write_text(rendered)
    print(
        f"Wrote {MANIFEST.relative_to(ROOT)}: "
        f"{len(manifest['commands'])} command entries, {len(manifest['skills'])} skills."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
