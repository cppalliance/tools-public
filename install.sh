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
#   LOCAL_SRC=/path use a local checkout instead of downloading the tarball

set -euo pipefail

REPO="cppalliance/tools-public"
BRANCH="master"
TARBALL_URL="https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz"
DEST="${DEST:-${HOME}/.claude/commands}"
LOCAL_SRC="${LOCAL_SRC:-}"

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

TOP_LEVEL=(
  advocatus.md
  auditor.md
  boost-review.md
  btc-talk.md
  code-cleanup.md
  code-review.md
  herald.md
  is-this-cpp.md
  lib-review.md
  normalize.md
  refine-plan.md
  research.md
  review-paper.md
  tighten.md
)

FAMILIES=(voice interview tutor)

die() { echo "error: $*" >&2; exit 1; }

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
plan() {
  local src="$1"
  NAMES=()
  SOURCES=()
  TARGETS=()

  for f in "${TOP_LEVEL[@]}"; do
    [[ -f "$src/$f" ]] || continue
    NAMES+=("/${f%.md}")
    SOURCES+=("$src/$f")
    TARGETS+=("$DEST/$f")
  done

  for family in "${FAMILIES[@]}"; do
    if [[ -f "$src/$family/$family.md" ]]; then
      NAMES+=("/$family")
      SOURCES+=("$src/$family/$family.md")
      TARGETS+=("$DEST/$family.md")
    fi
    if [[ -d "$src/$family" ]]; then
      for f in "$src/$family"/*.md; do
        [[ -e "$f" ]] || continue
        local base
        base="$(basename "$f" .md)"
        [[ "$base" == "$family" ]] && continue
        NAMES+=("/$family:$base")
        SOURCES+=("$f")
        TARGETS+=("$DEST/$family/$base.md")
      done
    fi
  done
}

print_banner() {
  cat <<EOF

tools-public — Claude Code slash commands
==========================================

A curated set of prompt-based "tools" from github.com/cppalliance/tools-public.
Each command is a markdown prompt invoked via /<name> inside Claude Code,
covering code review, document tightening, plan refinement, persona voices,
adaptive interviews, tutorials, and more.

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
  for family in "${FAMILIES[@]}"; do
    if [[ -d "$DEST/$family" ]]; then
      rmdir "$DEST/$family" 2>/dev/null || true
    fi
  done

  echo "Removed $removed commands from $DEST."
  (( skipped > 0 )) && echo "Skipped $skipped (not currently installed)."
}

acquire_source() {
  if [[ -n "$LOCAL_SRC" ]]; then
    SRC="$LOCAL_SRC/tools"
    [[ -d "$SRC" ]] || die "LOCAL_SRC=$LOCAL_SRC has no tools/ subdirectory"
    echo "Source: local checkout at $LOCAL_SRC"
    return
  fi

  command -v curl >/dev/null || die "curl is required"
  command -v tar  >/dev/null || die "tar is required"

  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT

  echo "Source: downloading ${REPO}@${BRANCH}..."
  curl -fsSL "$TARBALL_URL" | tar -xz -C "$TMP"

  SRC="$(find "$TMP" -maxdepth 2 -type d -name tools | head -n 1)"
  [[ -n "$SRC" && -d "$SRC" ]] || die "could not locate tools/ in extracted tarball"
}

main() {
  print_banner
  echo "Mode:   $MODE"
  echo "Target: $DEST"

  acquire_source

  plan "$SRC"
  [[ ${#NAMES[@]} -gt 0 ]] || die "nothing to process"

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
