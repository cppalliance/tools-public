# Installing tools-public

The installer registers the tools in this repo as user-level Claude Code slash commands by writing them into `~/.claude/commands/`. After install, each tool is invoked as `/<name>` from any Claude Code session.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/cppalliance/tools-public/master/install.sh | bash
```

Drops 37 commands into `~/.claude/commands/`. Re-run anytime to update — existing files are overwritten with the latest version. **Restart Claude Code** afterwards to pick up new commands (Claude Code does not auto-reload `commands/`).

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
| `DEST=/path`    | Install elsewhere than `~/.claude/commands` |
| `LOCAL_SRC=/path` | Use a local checkout instead of downloading the tarball |
| `UNINSTALL=1`   | Run install.sh in uninstall mode (same as `uninstall.sh`) |

## What's not included

The novelist toolchain (`tools/novelist/`) is intentionally excluded — it's a coupled multi-prompt + Python pipeline that expects a per-book workspace and doesn't fit a one-shot command install.
