# Installing tools-public

Two ways to install. **Claude Code users can use the plugin marketplace**, which handles updates and uninstall for you:

```
/plugin marketplace add cppalliance/tools-public
/plugin install tools-public@cppalliance
```

Refresh later with `/plugin marketplace update`. **Cursor users, and anyone who prefers a plain copy, use the installer below**, which is the only path that installs into `~/.cursor/skills/`.


The installer registers the tools in this repo as user-level Claude Code slash commands by writing them into `~/.claude/commands/`. After install, each tool is invoked as `/<name>` from any Claude Code session.

It also installs **skills**, the directory-based tools that ship a script alongside the prompt. Those go to `~/.claude/skills/` and `~/.cursor/skills/`, since Claude Code and Cursor both read the `SKILL.md` format. They are invoked as `/<name>` in either agent.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/cppalliance/tools-public/master/install.sh | bash
```

Drops the commands into `~/.claude/commands/` and the skills into `~/.claude/skills/` and `~/.cursor/skills/`. The run prints the exact list and asks before writing anything. Re-run anytime to update — existing files are overwritten with the latest version. **Restart Claude Code** afterwards to pick up new commands (Claude Code does not auto-reload `commands/`).

## Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/cppalliance/tools-public/master/uninstall.sh | bash
```

Removes only the files this installer placed. Anything else under `~/.claude/commands/` is left alone, and the directory itself is preserved.

## Sample output

```text
tools-public — Claude Code slash commands
==========================================

A curated set of prompt-based "tools" from github.com/cppalliance/tools-public.
Each command is a markdown prompt invoked via /<name> inside Claude Code,
covering code review, document tightening, plan refinement, persona voices,
adaptive interviews, tutorials, and more.

Mode:   install
Target: /Users/martin/.claude/commands
Source: downloading cppalliance/tools-public@master...

Will install 37 commands to /Users/martin/.claude/commands

  + /advocatus                        Advocatus Diaboli, examiner, appointed adversary of the cause
  + /auditor                          Mechanical compliance checker for WG21 papers
  + /code-review                      Language-agnostic code review with adversarial challenge
  + /lib-review                       Design analysis of open source projects using 38 diagnostic tests
  + /refine-plan                      Refine any plan through numbering, audit, and compression
  + /tighten                          Compress a document to half its length while preserving voice
  + /voice                            A tool that builds tools.
  + /voice:voice-of-william-gibson    On load: you are William Gibson.
  + /voice:voice-of-franz-kafka       On load: you are Franz Kafka.
  + /interview                        Generate role-specific adaptive interview protocols.
  + /tutor                            Curriculum architect, scout of the world's best teaching
  ... (26 more)

Legend:  + new   ↻ overwrite (update)

Proceed with install? [y/N] y
Installed 37 commands to /Users/martin/.claude/commands.
Restart Claude Code to pick them up.
```

On re-run, the `+` markers become `↻` for files already present.

## Options

Pass these as env vars before the curl pipe (or as flags to a local `bash install.sh`):

| Env var | Effect |
| --- | --- |
| `INSTALL_YES=1` | Skip the `[y/N]` confirmation |
| `DEST=/path`    | Install commands elsewhere than `~/.claude/commands` |
| `SKILL_DEST=a:b` | Colon-separated skill install roots. Default `~/.claude/skills:~/.cursor/skills`. Set to a single path to install for one agent only |
| `LOCAL_SRC=/path` | Use a local checkout instead of downloading the tarball |
| `UNINSTALL=1`   | Run install.sh in uninstall mode (same as `uninstall.sh`) |

## Skills

A command is one markdown prompt. A skill is a directory: `SKILL.md` plus whatever scripts it calls. That is the difference that gives skills their own list and their own install path.

To add one, drop the directory in the repo and list it in the `SKILLS` array in `install.sh`, by directory rather than filename:

```bash
SKILLS=(
  tools-wg21/my-skill
)
```

The installer skips any entry without a `SKILL.md`, copies the whole directory to each root in `SKILL_DEST`, and clears the previous copy first so a file dropped upstream does not linger. Uninstall removes a directory only if it exists and still contains a `SKILL.md`.

After editing `TOP_LEVEL`, `FAMILIES`, or `SKILLS`, regenerate the plugin manifest from them and check both agree with the tree:

```bash
./scripts/sync_plugin_manifest.py          # rewrite .claude-plugin/plugin.json
./scripts/sync_plugin_manifest.py --check  # exit 1 if it is stale
claude plugin validate . --strict          # exit 1 if any listed path is missing
```

Skills that shell out to a tool the user may not have (`gh`, `python3`) should say so in the `SKILL.md` and fail with a clear message rather than a stack trace.

## What's not included

The novelist toolchain (`tools/novelist/`) is intentionally excluded — it's a coupled multi-prompt + Python pipeline that expects a per-book workspace and doesn't fit a one-shot command install.
