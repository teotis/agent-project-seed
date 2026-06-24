#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
PLAN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"
ORCHESTRATE="$SCRIPT_DIR/orchestrate.sh"

run_orchestrate() {
  ORCHESTRATION_RUNNER=codex bash "$ORCHESTRATE" "$@"
}

usage() {
  cat <<EOF
Usage: $(basename "$0") [start|doctor|status|tail|resume|advance|retry|finalize|cleanup|mark-state|repair-state|collect-logs|verify-package|verify-finalize|scratch-path] [args...]

Default:
  $(basename "$0") start

Codex helpers:
  $(basename "$0") tail <package-id>
  $(basename "$0") resume <thread-id-or-codex-thread:id>
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

Codex runner evidence:
  tail -f "$PLAN_ROOT/status/launch-<package-id>.log"
  $(basename "$0") resume <thread-id>

Use concrete package ids from the status table. If a recorded agent id is
codex-thread:<id>, pass only <id> or pass the full value to this wrapper.
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
  tail)
    package_id="${1:-}"
    [ -n "$package_id" ] || {
      usage >&2
      exit 2
    }
    tail -f "$PLAN_ROOT/status/launch-$package_id.log"
    ;;
  resume)
    thread_id="${1:-}"
    [ -n "$thread_id" ] || {
      usage >&2
      exit 2
    }
    thread_id="${thread_id#codex-thread:}"
    codex exec resume "$thread_id"
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
