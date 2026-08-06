#!/usr/bin/env bash
# tools-public installer — Claude Code slash commands from
# github.com/cppalliance/tools-public.
#
# Install:
#   curl -fsSL https://raw.githubusercontent.com/cppalliance/tools-public/master/install.sh | bash
#
# Uninstall (removes the same set, leaves your own commands alone):
#   curl -fsSL https://raw.githubusercontent.com/cppalliance/tools-public/master/uninstall.sh | bash
#   # or:
#   UNINSTALL=1 curl -fsSL https://raw.githubusercontent.com/cppalliance/tools-public/master/install.sh | bash
#
# Re-run install to update to the latest versions; existing files are overwritten.
# Env knobs:
#   INSTALL_YES=1   skip the [y/N] confirmation
#   UNINSTALL=1     remove instead of install
#   DEST=/path      override ~/.claude/commands
#   SKILL_DEST=a:b  override the skill install roots (colon-separated)
#   LOCAL_SRC=/path use a local checkout instead of downloading the tarball

set -euo pipefail

REPO="cppalliance/tools-public"
BRANCH="master"
TARBALL_URL="https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz"
DEST="${DEST:-${HOME}/.claude/commands}"
LOCAL_SRC="${LOCAL_SRC:-}"

# Skills install to every agent that reads the SKILL.md format, since the same
# directory works unmodified in each. Claude Code and Cursor both also read the
# other's path as a compat fallback, but writing both explicitly avoids relying
# on that.
SKILL_DEST="${SKILL_DEST:-${HOME}/.claude/skills:${HOME}/.cursor/skills}"

# Mode: parse --uninstall flag or UNINSTALL env var.
MODE="install"
for arg in "$@"; do
  case "$arg" in
    --uninstall) MODE="uninstall" ;;
    --help|-h)
      sed -n '2,20p' "$0"
      exit 0
      ;;
  esac
done
[[ "${UNINSTALL:-}" == "1" ]] && MODE="uninstall"

# Commands, as paths relative to the repo root. The slash command is named after
# the file, so tools-wg21/tighten.md installs as /tighten regardless of where it
# sits in the tree.
TOP_LEVEL=(
  tools/btc-talk.md
  tools/normalize-prompt.md
  tools/refine-plan.md
  tools/research.md
  tools/code/boost-review.md
  tools/code/code-cleanup.md
  tools/code/code-review.md
  tools/code/lib-review.md
  tools-wg21/advocatus.md
  tools-wg21/auditor.md
  tools-wg21/herald.md
  tools-wg21/is-this-cpp.md
  tools-wg21/review-paper.md
  tools-wg21/tighten.md
)

# Families are a parent prompt plus a directory of sub-prompts: tools/voice.md
# installs as /voice, and tools/voice/*.md as /voice:<name>.
FAMILIES=(
  tools/voice
  tools/interview
  tools/tutor
)

# Skills, as paths relative to the repo root.
#
# A command above is a single prompt file copied into ~/.claude/commands. A skill
# is a whole directory: SKILL.md plus whatever scripts it calls. That distinction
# is why they need their own list and their own install path. Add a skill here by
# its directory, not by a filename.
SKILLS=(
  tools-wg21/pick-pr-review
)

# Split the colon-separated SKILL_DEST into an array.
SKILL_DESTS=()
while IFS= read -r _dest; do
  [[ -n "$_dest" ]] && SKILL_DESTS+=("$_dest")
done <<< "${SKILL_DEST//:/$'\n'}"

die() { echo "error: $*" >&2; exit 1; }

# "1 skill" / "2 skills"
plural() { (( $1 == 1 )) && echo "$1 $2" || echo "$1 ${2}s"; }

extract_description() {
  local file="$1"
  local desc=""

  desc="$(awk '
    BEGIN { in_fm = 0; line = 0 }
    { line++ }
    line == 1 && /^---[[:space:]]*$/ { in_fm = 1; next }
    in_fm && /^---[[:space:]]*$/ { exit }
    in_fm && /^description:/ {
      sub(/^description:[[:space:]]*/, "")
      gsub(/^"|"$/, "")
      print
      exit
    }
  ' "$file")"

  if [[ -z "$desc" ]]; then
    desc="$(awk '
      BEGIN { seen = 0; in_comment = 0 }
      /^#[^!]/ { seen = 1; next }
      /<!--/ && !/-->/ { in_comment = 1; next }
      in_comment && /-->/ { in_comment = 0; next }
      in_comment { next }
      /^<!--.*-->[[:space:]]*$/ { next }
      seen && NF > 0 && !/^---/ && !/^```/ && !/^!\[/ && !/^\|/ { print; exit }
    ' "$file")"
  fi

  desc="${desc//\`/}"
  desc="${desc//\*\*/}"

  desc="$(printf '%s' "$desc" | awk '{
    n = index($0, ". ")
    if (n > 0 && n < 90) print substr($0, 1, n)
    else print substr($0, 1, 90)
  }')"

  printf '%s' "$desc"
}

# NAMES[i] = slash-command name (with leading /)
# SOURCES[i] = path to source .md inside the extracted tree
# TARGETS[i] = absolute path under $DEST
# SKILL_NAMES[i] / SKILL_SOURCES[i] = skill command name and its source directory
plan() {
  local root="$1"
  NAMES=()
  SOURCES=()
  TARGETS=()
  SKILL_NAMES=()
  SKILL_SOURCES=()
  MISSING=()

  local f base
  for f in "${TOP_LEVEL[@]}"; do
    # A listed command that does not resolve is a repo error, not a normal
    # condition. Silently skipping is how this list drifted out of sync with the
    # tree in the first place, so collect it and report at the end.
    if [[ ! -f "$root/$f" ]]; then
      MISSING+=("$f")
      continue
    fi
    base="$(basename "$f")"
    NAMES+=("/${base%.md}")
    SOURCES+=("$root/$f")
    TARGETS+=("$DEST/$base")
  done

  local family_path family
  for family_path in "${FAMILIES[@]}"; do
    family="$(basename "$family_path")"
    if [[ -f "$root/$family_path.md" ]]; then
      NAMES+=("/$family")
      SOURCES+=("$root/$family_path.md")
      TARGETS+=("$DEST/$family.md")
    else
      MISSING+=("$family_path.md")
    fi
    if [[ -d "$root/$family_path" ]]; then
      for f in "$root/$family_path"/*.md; do
        [[ -e "$f" ]] || continue
        base="$(basename "$f" .md)"
        [[ "$base" == "$family" ]] && continue
        NAMES+=("/$family:$base")
        SOURCES+=("$f")
        TARGETS+=("$DEST/$family/$base.md")
      done
    else
      MISSING+=("$family_path/")
    fi
  done

  # Guarded because bash 3.2, still the system bash on macOS, treats "${ARR[@]}"
  # on an empty array as an unbound variable under set -u.
  if (( ${#SKILLS[@]} > 0 )); then
    local skill
    for skill in "${SKILLS[@]}"; do
      # A directory without a SKILL.md is not a skill, skip it rather than
      # installing something no agent will load.
      [[ -f "$root/$skill/SKILL.md" ]] || continue
      SKILL_NAMES+=("/$(basename "$skill")")
      SKILL_SOURCES+=("$root/$skill")
    done
  fi
}

# Every install path for a skill, one per line.
skill_targets() {
  local name="$1" dest_root
  for dest_root in "${SKILL_DESTS[@]}"; do
    echo "$dest_root/$name"
  done
}

# A skill counts as present if it is installed in any of the destinations.
skill_present() {
  local name="$1" target
  while IFS= read -r target; do
    [[ -d "$target" ]] && return 0
  done < <(skill_targets "$name")
  return 1
}

print_banner() {
  cat <<EOF

tools-public — Claude Code slash commands and skills
====================================================

A curated set of prompt-based "tools" from github.com/cppalliance/tools-public.
Each command is a markdown prompt invoked via /<name> inside Claude Code,
covering code review, document tightening, plan refinement, persona voices,
adaptive interviews, tutorials, and more.

Skills are directory-based tools that ship scripts alongside the prompt. They
install to both Claude Code and Cursor, which share the SKILL.md format.

EOF
}

print_plan() {
  local action_word="$1"   # "install" or "remove"
  local present_count=0
  local i
  for i in "${!TARGETS[@]}"; do
    [[ -f "${TARGETS[$i]}" ]] && present_count=$((present_count + 1))
  done

  local max_width=0
  for name in "${NAMES[@]}"; do
    (( ${#name} > max_width )) && max_width=${#name}
  done
  if (( ${#SKILL_NAMES[@]} > 0 )); then
    for name in "${SKILL_NAMES[@]}"; do
      (( ${#name} > max_width )) && max_width=${#name}
    done
  fi

  if [[ "$action_word" == "install" ]]; then
    echo "Will install ${#NAMES[@]} commands to $DEST"
    if (( present_count > 0 )); then
      echo "($present_count already present — those will be overwritten with the latest version.)"
    fi
  else
    echo "Will remove ${present_count} commands from $DEST"
    if (( present_count < ${#NAMES[@]} )); then
      echo "($((${#NAMES[@]} - present_count)) listed below are not currently installed and will be skipped.)"
    fi
  fi
  echo

  for i in "${!NAMES[@]}"; do
    local desc marker=" "
    desc="$(extract_description "${SOURCES[$i]}")"
    if [[ "$action_word" == "install" ]]; then
      [[ -f "${TARGETS[$i]}" ]] && marker="↻" || marker="+"
    else
      [[ -f "${TARGETS[$i]}" ]] && marker="-" || marker=" "
    fi
    printf "  %s %-${max_width}s  %s\n" "$marker" "${NAMES[$i]}" "$desc"
  done
  echo

  if (( ${#SKILL_NAMES[@]} > 0 )); then
    local skill_present_count=0
    for i in "${!SKILL_NAMES[@]}"; do
      skill_present "${SKILL_NAMES[$i]#/}" && skill_present_count=$((skill_present_count + 1))
    done

    if [[ "$action_word" == "install" ]]; then
      echo "Will install $(plural ${#SKILL_NAMES[@]} skill) to:"
    else
      echo "Will remove $(plural ${skill_present_count} skill) from:"
    fi
    local dest_root
    for dest_root in "${SKILL_DESTS[@]}"; do
      echo "  $dest_root"
    done
    echo

    for i in "${!SKILL_NAMES[@]}"; do
      local desc marker=" "
      desc="$(extract_description "${SKILL_SOURCES[$i]}/SKILL.md")"
      if [[ "$action_word" == "install" ]]; then
        skill_present "${SKILL_NAMES[$i]#/}" && marker="↻" || marker="+"
      else
        skill_present "${SKILL_NAMES[$i]#/}" && marker="-" || marker=" "
      fi
      printf "  %s %-${max_width}s  %s\n" "$marker" "${SKILL_NAMES[$i]}" "$desc"
    done
    echo
  fi

  if [[ "$action_word" == "install" ]]; then
    echo "Legend:  + new   ↻ overwrite (update)"
  else
    echo "Legend:  - will be removed   (blank) not installed, skipped"
  fi
  echo
}

confirm() {
  local prompt="$1"
  if [[ "${INSTALL_YES:-}" == "1" ]]; then
    return 0
  fi
  if [[ ! -e /dev/tty ]]; then
    die "no tty for confirmation; re-run with INSTALL_YES=1 to skip the prompt"
  fi
  local answer
  read -r -p "$prompt [y/N] " answer </dev/tty
  [[ "$answer" =~ ^[Yy]$ ]]
}

do_install() {
  mkdir -p "$DEST"
  local i count=0
  for i in "${!TARGETS[@]}"; do
    local target="${TARGETS[$i]}"
    mkdir -p "$(dirname "$target")"
    cp "${SOURCES[$i]}" "$target"
    count=$((count + 1))
  done
  echo "Installed $count commands to $DEST."

  local skill_count=0
  if (( ${#SKILL_NAMES[@]} > 0 )); then
    for i in "${!SKILL_NAMES[@]}"; do
      local name="${SKILL_NAMES[$i]#/}" target
      while IFS= read -r target; do
        mkdir -p "$(dirname "$target")"
        # Clear the old copy first, so a file dropped from the skill upstream
        # does not linger in an install that is otherwise up to date.
        [[ -d "$target" ]] && rm -rf "$target"
        cp -R "${SKILL_SOURCES[$i]}" "$target"
        skill_count=$((skill_count + 1))
      done < <(skill_targets "$name")
    done
    echo "Installed $(plural ${#SKILL_NAMES[@]} skill) to $(plural ${#SKILL_DESTS[@]} location) ($(plural $skill_count copy | sed 's/copys/copies/'))."
  fi

  echo "Restart Claude Code to pick them up."
}

do_uninstall() {
  local i removed=0 skipped=0
  for i in "${!TARGETS[@]}"; do
    local target="${TARGETS[$i]}"
    if [[ -f "$target" ]]; then
      rm -f "$target"
      removed=$((removed + 1))
    else
      skipped=$((skipped + 1))
    fi
  done

  # Drop empty family subdirs we may have created.
  local family_path family
  for family_path in "${FAMILIES[@]}"; do
    family="$(basename "$family_path")"
    if [[ -d "$DEST/$family" ]]; then
      rmdir "$DEST/$family" 2>/dev/null || true
    fi
  done

  echo "Removed $removed commands from $DEST."
  (( skipped > 0 )) && echo "Skipped $skipped (not currently installed)."

  local skill_removed=0
  if (( ${#SKILL_NAMES[@]} > 0 )); then
    for i in "${!SKILL_NAMES[@]}"; do
      local name="${SKILL_NAMES[$i]#/}" target
      [[ -n "$name" ]] || continue
      while IFS= read -r target; do
        # Only ever remove a directory we would have written: it has to exist
        # and carry the SKILL.md that made it a skill in the first place.
        if [[ -d "$target" && -f "$target/SKILL.md" ]]; then
          rm -rf "$target"
          skill_removed=$((skill_removed + 1))
        fi
      done < <(skill_targets "$name")
    done
    echo "Removed $skill_removed skill $( (( skill_removed == 1 )) && echo copy || echo copies )."
  fi

  return 0
}

acquire_source() {
  if [[ -n "$LOCAL_SRC" ]]; then
    ROOT="$LOCAL_SRC"
    [[ -d "$ROOT/tools" ]] || die "LOCAL_SRC=$LOCAL_SRC has no tools/ subdirectory"
    echo "Source: local checkout at $LOCAL_SRC"
    return
  fi

  command -v curl >/dev/null || die "curl is required"
  command -v tar  >/dev/null || die "tar is required"

  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT

  echo "Source: downloading ${REPO}@${BRANCH}..."
  curl -fsSL "$TARBALL_URL" | tar -xz -C "$TMP"

  # Everything is listed relative to the repo root, which is tools/'s parent.
  local tools_dir
  tools_dir="$(find "$TMP" -maxdepth 2 -type d -name tools | head -n 1)"
  [[ -n "$tools_dir" && -d "$tools_dir" ]] || die "could not locate tools/ in extracted tarball"
  ROOT="$(dirname "$tools_dir")"
}

main() {
  print_banner
  echo "Mode:   $MODE"
  echo "Target: $DEST"

  acquire_source

  plan "$ROOT"
  [[ $(( ${#NAMES[@]} + ${#SKILL_NAMES[@]} )) -gt 0 ]] || die "nothing to process"

  # Loud, because a missing entry means the lists have drifted from the tree and
  # someone is quietly not getting a tool they should have.
  if (( ${#MISSING[@]} > 0 )); then
    echo >&2
    echo "warning: ${#MISSING[@]} listed entries were not found and will be skipped:" >&2
    for entry in "${MISSING[@]}"; do
      echo "  $entry" >&2
    done
    echo "Fix the TOP_LEVEL or FAMILIES list in install.sh." >&2
  fi

  echo
  if [[ "$MODE" == "install" ]]; then
    print_plan "install"
    if confirm "Proceed with install?"; then
      do_install
    else
      echo "Aborted. Nothing installed."
      exit 1
    fi
  else
    print_plan "remove"
    if confirm "Proceed with uninstall?"; then
      do_uninstall
    else
      echo "Aborted. Nothing removed."
      exit 1
    fi
  fi
}

main "$@"
