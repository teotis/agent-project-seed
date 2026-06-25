#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
PLAN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
ORCHESTRATE="$SCRIPT_DIR/orchestrate.sh"
REPO_ROOT="$(git -C "$PLAN_ROOT" rev-parse --show-toplevel 2>/dev/null || pwd -P)"

run_orchestrate() {
  ORCHESTRATION_RUNNER=claude bash "$ORCHESTRATE" "$@"
}

usage() {
  cat <<EOF
Usage: $(basename "$0") [start|doctor|status|agents|advance|retry|finalize|cleanup|mark-state|repair-state|collect-logs|verify-package|verify-finalize|scratch-path] [args...]

Default:
  $(basename "$0") start

Claude helper:
  $(basename "$0") agents
EOF
}

cmd="${1:-start}"
[ "$#" -eq 0 ] || shift

case "$cmd" in
  start)
    run_orchestrate doctor --environment
    run_orchestrate start
    run_orchestrate status
    cat <<EOF

View Claude Code background sessions with:
  claude agents --cwd "$REPO_ROOT"

Or run:
  "$0" agents
EOF
    ;;
  doctor)
    if [ "$#" -eq 0 ]; then
      run_orchestrate doctor --environment
    else
      run_orchestrate doctor "$@"
    fi
    ;;
  status|advance|retry|finalize|cleanup|mark-state|repair-state|collect-logs|verify-package|verify-finalize|scratch-path)
    run_orchestrate "$cmd" "$@"
    ;;
  agents)
    claude agents --cwd "$REPO_ROOT"
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
