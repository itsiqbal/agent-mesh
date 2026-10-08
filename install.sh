#!/usr/bin/env bash
# Defaults: claude,antigravity,opencode; use --only codex or --dry-run.
set -euo pipefail
KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$KIT_DIR/scripts/codex_install.py" install "$@"
