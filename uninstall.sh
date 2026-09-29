#!/usr/bin/env bash
# ai-agent-kit uninstaller. Mirrors install.sh: removes exactly the kit-installed
# files from all three tool locations, and strips the marked rules block back out
# of CLAUDE.md / GEMINI.md / AGENTS.md (restoring nothing else in those files).
#
# Usage:
#   ./uninstall.sh
#   ./uninstall.sh --only claude,opencode
set -euo pipefail

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS="claude,antigravity,opencode"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --only) TOOLS="$2"; shift 2 ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

want() { [[ ",$TOOLS," == *",$1,"* ]]; }

MARKER_BEGIN="<!-- BEGIN ai-agent-kit -->"
MARKER_END="<!-- END ai-agent-kit -->"

strip_rules_block() {
  local target="$1"
  [[ -f "$target" ]] || return 0
  grep -qF "$MARKER_BEGIN" "$target" 2>/dev/null || return 0
  local tmp; tmp="$(mktemp)"
  awk -v b="$MARKER_BEGIN" -v e="$MARKER_END" '
    $0==b {skip=1; next}
    $0==e {skip=0; next}
    !skip {print}
  ' "$target" > "$tmp"
  mv "$tmp" "$target"
  echo "  removed rules block from $target"
}

echo "Uninstalling ai-agent-kit"
echo "Targets: $TOOLS"
echo

if want claude; then
  echo "== Claude Code =="
  for role_dir in "$KIT_DIR"/agents/*/; do
    role="$(basename "$role_dir")"
    rm -f "$HOME/.claude/agents/$role.md"
  done
  for skill_dir in "$KIT_DIR"/skills/*/; do
    rm -rf "$HOME/.claude/skills/$(basename "$skill_dir")"
  done
  for wf_dir in "$KIT_DIR"/workflows/*/; do
    rm -f "$HOME/.claude/commands/$(basename "$wf_dir").md"
  done
  strip_rules_block "$HOME/.claude/CLAUDE.md"
  echo
fi

if want antigravity; then
  echo "== Antigravity =="
  for role_dir in "$KIT_DIR"/agents/*/; do
    role="$(basename "$role_dir")"
    rm -f "$HOME/.gemini/config/agents/$role.md"
  done
  for skill_dir in "$KIT_DIR"/skills/*/; do
    name="$(basename "$skill_dir")"
    rm -rf "$HOME/.gemini/antigravity/skills/$name"
    rm -rf "$HOME/.gemini/config/skills/$name"
  done
  for wf_dir in "$KIT_DIR"/workflows/*/; do
    rm -f "$HOME/.gemini/antigravity/global_workflows/$(basename "$wf_dir").md"
  done
  strip_rules_block "$HOME/.gemini/GEMINI.md"
  echo
fi

if want opencode; then
  echo "== opencode =="
  for role_dir in "$KIT_DIR"/agents/*/; do
    role="$(basename "$role_dir")"
    rm -f "$HOME/.config/opencode/agents/$role.md"
  done
  for skill_dir in "$KIT_DIR"/skills/*/; do
    rm -rf "$HOME/.config/opencode/skills/$(basename "$skill_dir")"
  done
  for wf_dir in "$KIT_DIR"/workflows/*/; do
    rm -f "$HOME/.config/opencode/command/$(basename "$wf_dir").md"
  done
  strip_rules_block "$HOME/.config/opencode/AGENTS.md"
  echo
fi

echo "Done. Any .pre-ai-agent-kit.bak backup files created at install time were left in place."
