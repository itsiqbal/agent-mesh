#!/usr/bin/env bash
# ai-agent-kit installer
# One canonical source (agents/, skills/, workflows/, AGENTS.md) -> installed for
# Claude Code, Google Antigravity, and opencode. Global (all-projects) install, idempotent.
#
# Usage:
#   ./install.sh                         # install for all three tools found (or all three regardless)
#   ./install.sh --only claude,opencode   # install for a subset
#   ./install.sh --dry-run                # print what would happen, change nothing
set -euo pipefail

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS="claude,antigravity,opencode"
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --only) TOOLS="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

want() { [[ ",$TOOLS," == *",$1,"* ]]; }

run() {
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "  [dry-run] $*"
  else
    "$@"
  fi
}

copy_dir() {
  # copy_dir <src> <dst>  -- mkdir -p dst, then copy contents of src into it
  local src="$1" dst="$2"
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "  [dry-run] install -> $dst"
  else
    mkdir -p "$dst"
    cp -R "$src"/. "$dst"/
    find "$dst" -name ".DS_Store" -type f -delete 2>/dev/null || true
  fi
}

MARKER_BEGIN="<!-- BEGIN ai-agent-kit -->"
MARKER_END="<!-- END ai-agent-kit -->"

install_rules_block() {
  # install_rules_block <target-file> <content-file>
  # Idempotently inject/update a marked block inside target-file, backing up any
  # pre-existing unmanaged content the first time the file is touched.
  local target="$1" content="$2"
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "  [dry-run] update rules block -> $target"
    return
  fi
  mkdir -p "$(dirname "$target")"
  if [[ ! -f "$target" ]]; then
    : > "$target"
  fi
  if [[ -f "$target" ]] && ! grep -qF "$MARKER_BEGIN" "$target" 2>/dev/null; then
    if [[ -s "$target" ]]; then
      cp "$target" "${target}.pre-ai-agent-kit.bak"
      echo "  (backed up existing $(basename "$target") -> $(basename "$target").pre-ai-agent-kit.bak)"
    fi
  fi
  local tmp
  tmp="$(mktemp)"
  if grep -qF "$MARKER_BEGIN" "$target" 2>/dev/null; then
    awk -v b="$MARKER_BEGIN" -v e="$MARKER_END" '
      $0==b {skip=1}
      !skip {print}
      $0==e {skip=0}
    ' "$target" > "$tmp"
  else
    cat "$target" > "$tmp"
  fi
  {
    cat "$tmp"
    echo "$MARKER_BEGIN"
    cat "$content"
    echo "$MARKER_END"
  } > "$target.new"
  mv "$target.new" "$target"
  rm -f "$tmp"
}

echo "Installing ai-agent-kit from $KIT_DIR"
echo "Targets: $TOOLS"
echo

# ---------------- Claude Code ----------------
if want claude; then
  echo "== Claude Code =="
  run mkdir -p "$HOME/.claude/agents" "$HOME/.claude/skills" "$HOME/.claude/commands"

  for role_dir in "$KIT_DIR"/agents/*/; do
    role="$(basename "$role_dir")"
    [[ -f "$role_dir/claude-code.md" ]] && run cp "$role_dir/claude-code.md" "$HOME/.claude/agents/$role.md"
  done
  echo "  agents -> ~/.claude/agents/ ($(ls "$KIT_DIR"/agents | wc -l | tr -d ' ') roles)"

  for skill_dir in "$KIT_DIR"/skills/*/; do
    name="$(basename "$skill_dir")"
    copy_dir "$skill_dir" "$HOME/.claude/skills/$name"
  done
  echo "  skills -> ~/.claude/skills/"

  for wf_dir in "$KIT_DIR"/workflows/*/; do
    name="$(basename "$wf_dir")"
    [[ -f "$wf_dir/claude-code.md" ]] && run cp "$wf_dir/claude-code.md" "$HOME/.claude/commands/$name.md"
  done
  echo "  workflows -> ~/.claude/commands/ (as /slash commands)"

  install_rules_block "$HOME/.claude/CLAUDE.md" "$KIT_DIR/AGENTS.md"
  echo "  rules -> ~/.claude/CLAUDE.md (marked block, safe to re-run)"
  echo
fi

# ---------------- Antigravity ----------------
if want antigravity; then
  echo "== Antigravity =="
  run mkdir -p "$HOME/.gemini/config/agents" "$HOME/.gemini/antigravity/skills" \
              "$HOME/.gemini/config/skills" "$HOME/.gemini/antigravity/global_workflows"

  for role_dir in "$KIT_DIR"/agents/*/; do
    role="$(basename "$role_dir")"
    [[ -f "$role_dir/antigravity.md" ]] && run cp "$role_dir/antigravity.md" "$HOME/.gemini/config/agents/$role.md"
  done
  echo "  agents -> ~/.gemini/config/agents/"

  for skill_dir in "$KIT_DIR"/skills/*/; do
    name="$(basename "$skill_dir")"
    copy_dir "$skill_dir" "$HOME/.gemini/antigravity/skills/$name"
    copy_dir "$skill_dir" "$HOME/.gemini/config/skills/$name"
  done
  echo "  skills -> ~/.gemini/antigravity/skills/ (+ compat copy in ~/.gemini/config/skills/)"

  for wf_dir in "$KIT_DIR"/workflows/*/; do
    name="$(basename "$wf_dir")"
    [[ -f "$wf_dir/antigravity.md" ]] && run cp "$wf_dir/antigravity.md" "$HOME/.gemini/antigravity/global_workflows/$name.md"
  done
  echo "  workflows -> ~/.gemini/antigravity/global_workflows/"

  install_rules_block "$HOME/.gemini/GEMINI.md" "$KIT_DIR/AGENTS.md"
  echo "  rules -> ~/.gemini/GEMINI.md (marked block, safe to re-run)"
  echo
fi

# ---------------- opencode ----------------
if want opencode; then
  echo "== opencode =="
  run mkdir -p "$HOME/.config/opencode/agents" "$HOME/.config/opencode/skills" "$HOME/.config/opencode/command"

  for role_dir in "$KIT_DIR"/agents/*/; do
    role="$(basename "$role_dir")"
    [[ -f "$role_dir/opencode.md" ]] && run cp "$role_dir/opencode.md" "$HOME/.config/opencode/agents/$role.md"
  done
  echo "  agents -> ~/.config/opencode/agents/"

  # opencode natively falls back to ~/.claude/skills/, but we copy explicitly here too so
  # this install is self-contained even if the Claude Code target above is skipped.
  for skill_dir in "$KIT_DIR"/skills/*/; do
    name="$(basename "$skill_dir")"
    copy_dir "$skill_dir" "$HOME/.config/opencode/skills/$name"
  done
  echo "  skills -> ~/.config/opencode/skills/ (opencode also auto-reads ~/.claude/skills/ if present)"

  for wf_dir in "$KIT_DIR"/workflows/*/; do
    name="$(basename "$wf_dir")"
    [[ -f "$wf_dir/opencode.md" ]] && run cp "$wf_dir/opencode.md" "$HOME/.config/opencode/command/$name.md"
  done
  echo "  workflows -> ~/.config/opencode/command/ (as /slash commands)"

  install_rules_block "$HOME/.config/opencode/AGENTS.md" "$KIT_DIR/AGENTS.md"
  echo "  rules -> ~/.config/opencode/AGENTS.md (marked block, safe to re-run)"
  echo
fi

echo "Done. Re-run this script any time after editing the kit to pick up changes; it's idempotent."
