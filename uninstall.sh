#!/usr/bin/env bash
# Thin wrapper: download install.sh and run it in uninstall mode.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/cppalliance/tools-public/master/uninstall.sh | bash

set -euo pipefail

REPO="cppalliance/tools-public"
BRANCH="master"
INSTALL_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}/install.sh"

command -v curl >/dev/null || { echo "error: curl is required" >&2; exit 1; }

curl -fsSL "$INSTALL_URL" | UNINSTALL=1 bash
