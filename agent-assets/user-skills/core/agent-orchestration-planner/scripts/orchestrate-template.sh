#!/usr/bin/env bash
# orchestrate-template v1.1.1 — see skills/agent-orchestration-planner/scripts/orchestrate-template.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLAN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
GRAPH="$PLAN_ROOT/launchers/package-graph.tsv"
STATE="$PLAN_ROOT/status/state.tsv"
EVENTS="$PLAN_ROOT/status/events.jsonl"
RUNNER_STATE="$PLAN_ROOT/status/runner"
LOGS_DIR="$PLAN_ROOT/status/logs"
SCRATCH="$PLAN_ROOT/scratch"
PROMPTS="$PLAN_ROOT/launchers/agent-prompts.md"
LOCK_DIR="$PLAN_ROOT/status/.orchestrate.lock"
MAX_PARALLEL="${ORCHESTRATION_MAX_PARALLEL:-10}"
if [ -n "${ORCHESTRATION_RUNNER+x}" ]; then
  ORCHESTRATION_RUNNER_SOURCE="environment"
elif [ -s "$RUNNER_STATE" ]; then
  ORCHESTRATION_RUNNER="$(head -n 1 "$RUNNER_STATE")"
  ORCHESTRATION_RUNNER_SOURCE="persisted"
else
  ORCHESTRATION_RUNNER="claude"
  ORCHESTRATION_RUNNER_SOURCE="default"
fi
CLAUDE_MODEL="${CLAUDE_MODEL:-sonnet}"
CLAUDE_EFFORT="${CLAUDE_EFFORT:-xhigh}"
CLAUDE_PERMISSION_MODE="${CLAUDE_PERMISSION_MODE:-}"
CLAUDE_SETTING_SOURCES="${CLAUDE_SETTING_SOURCES:-user,project,local}"
ORCHESTRATION_CODEX_MODEL="${ORCHESTRATION_CODEX_MODEL:-}"
ORCHESTRATION_CODEX_EFFORT="${ORCHESTRATION_CODEX_EFFORT:-}"
ORCHESTRATION_CODEX_SANDBOX="${ORCHESTRATION_CODEX_SANDBOX:-workspace-write}"
ORCHESTRATION_CODEX_APPROVAL_POLICY="${ORCHESTRATION_CODEX_APPROVAL_POLICY:-never}"
PLAN_NAME="$(basename "$PLAN_ROOT")"
ORCHESTRATION_INTEGRATION_BRANCH="${ORCHESTRATION_INTEGRATION_BRANCH:-agent/$PLAN_NAME/integration}"
ORCHESTRATION_INTEGRATION_WORKTREE="${ORCHESTRATION_INTEGRATION_WORKTREE:-$REPO_ROOT/.worktrees/$PLAN_NAME/00-integration}"
STATE_HEADER="package_id	state	launched_at	completed_at	agent	branch	worktree	base_commit	commit_hash	verification	integration	cleanup	last_error	failed_command	conflict_files	log_summary	recovery_hint"
GRAPH_HEADER="package_id	package_doc	status_file	dependencies	dependency_type	wave	branch	worktree	manual	finalize"
SIG_FILE="$PLAN_ROOT/status/.state.sig"
LOCK_ACQUIRED=0

log() {
  printf '[orchestrate] %s\n' "$*" >&2
}

die() {
  printf '[orchestrate] ERROR: %s\n' "$*" >&2
  exit 1
}

timestamp() {
  date -u "+%Y-%m-%dT%H:%M:%SZ"
}

json_escape() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  value="${value//$'\t'/\\t}"
  value="${value//$'\n'/\\n}"
  value="${value//$'\r'/\\r}"
  printf '%s' "$value"
}

json_pair() {
  local key="$1"
  local value="$2"
  printf ',"%s":"%s"' "$(json_escape "$key")" "$(json_escape "$value")"
}


state_signature_secret() {
  local secret
  secret="${ORCHESTRATION_SIGNING_SECRET:-}"
  if [ -n "$secret" ]; then
    printf '%s' "$secret"
    return 0
  fi
  secret="$(head -c 32 /dev/urandom | base64 | tr -d '
')"
  printf '%s' "$secret"
}

ensure_signing_secret() {
  if [ -f "$SIG_FILE" ]; then
    return 0
  fi
  local secret
  secret="$(state_signature_secret)"
  mkdir -p "$(dirname "$SIG_FILE")"
  printf '%s
' "$secret" > "$SIG_FILE"
  chmod 600 "$SIG_FILE"
}

compute_state_signature() {
  local secret sha
  if [ ! -f "$SIG_FILE" ]; then
    return 0
  fi
  secret="$(cat "$SIG_FILE")"
  if command -v openssl >/dev/null 2>&1; then
    sha="$(awk '!/^# signature:/' "$STATE" | openssl dgst -sha256 -hmac "$secret" 2>/dev/null | awk '{print $NF}')"
    printf '%s' "$sha"
    return 0
  fi
  if command -v sha256sum >/dev/null 2>&1; then
    printf '%s' "$( { printf '%s' "$secret"; awk '!/^# signature:/' "$STATE"; } | sha256sum | awk '{print $1}')"
    return 0
  fi
  if command -v shasum >/dev/null 2>&1; then
    printf '%s' "$( { printf '%s' "$secret"; awk '!/^# signature:/' "$STATE"; } | shasum -a 256 | awk '{print $1}')"
    return 0
  fi
  printf 'unsigned'
}

verify_state_signature() {
  if [ ! -f "$SIG_FILE" ]; then
    printf 'state.tsv has no signature guard; run repair-state to initialize
' >&2
    return 1
  fi
  local expected actual
  expected="$(compute_state_signature)"
  if [ "$expected" = "unsigned" ]; then
    printf 'state.tsv cannot be verified: no hashing tool available
' >&2
    return 2
  fi
  actual="$(tail -n 1 "$STATE" | sed -n 's/^# signature://p')"
  if [ -z "$actual" ]; then
    printf 'state.tsv is missing signature line; it may have been edited outside mark-state
' >&2
    return 1
  fi
  if [ "$expected" != "$actual" ]; then
    printf 'state.tsv signature mismatch; it was modified outside of mark-state
' >&2
    return 1
  fi
  return 0
}

tsv_safe() {
  local value="$1"
  value="${value//$'\t'/ }"
  value="${value//$'\n'/ }"
  value="${value//$'\r'/ }"
  printf '%s' "$value" | sed 's/[[:space:]][[:space:]]*/ /g; s/^[[:space:]]*//; s/[[:space:]]*$//'
}

emit_event() {
  local event="$1"
  local package_id="${2:-}"
  local extra="${3:-}"
  mkdir -p "$(dirname "$EVENTS")"
  printf '{"ts":"%s","event":"%s","package_id":"%s"%s}\n' \
    "$(timestamp)" "$(json_escape "$event")" "$(json_escape "$package_id")" "$extra" >> "$EVENTS"
}

ensure_scratch_root() {
  mkdir -p "$SCRATCH"
  if [ ! -f "$SCRATCH/.gitignore" ]; then
    {
      printf '*\n'
      printf '!.gitignore\n'
    } > "$SCRATCH/.gitignore"
  fi
}

scratch_path_for() {
  local package_id="$1"
  printf '%s/%s\n' "$SCRATCH" "$package_id"
}

failure_fingerprint() {
  local message="$1"
  message="${message%%; see *}"
  message="${message//$'\t'/ }"
  message="${message//$'\n'/ }"
  printf '%s' "$message" | sed 's/[[:space:]][[:space:]]*/ /g; s/^[[:space:]]*//; s/[[:space:]]*$//'
}

terminal_failure_count() {
  local package_id="$1"
  local fingerprint="$2"
  local package_json fingerprint_json line count=0
  [ -f "$EVENTS" ] || {
    printf '0\n'
    return
  }
  package_json="$(json_escape "$package_id")"
  fingerprint_json="$(json_escape "$fingerprint")"
  while IFS= read -r line; do
    if [[ "$line" == *'"event":"terminal_failure"'* ]] &&
      [[ "$line" == *"\"package_id\":\"$package_json\""* ]] &&
      [[ "$line" == *"\"fingerprint\":\"$fingerprint_json\""* ]]; then
      count=$((count + 1))
    fi
  done < "$EVENTS"
  printf '%s\n' "$count"
}

terminal_failure_recorded() {
  local package_id="$1"
  local state="$2"
  local fingerprint="$3"
  local package_json state_json fingerprint_json line
  [ -f "$EVENTS" ] || return 1
  package_json="$(json_escape "$package_id")"
  state_json="$(json_escape "$state")"
  fingerprint_json="$(json_escape "$fingerprint")"
  while IFS= read -r line; do
    if [[ "$line" == *'"event":"terminal_failure"'* ]] &&
      [[ "$line" == *"\"package_id\":\"$package_json\""* ]] &&
      [[ "$line" == *"\"state\":\"$state_json\""* ]] &&
      [[ "$line" == *"\"fingerprint\":\"$fingerprint_json\""* ]]; then
      return 0
    fi
  done < "$EVENTS"
  return 1
}

emit_terminal_failure_event() {
  local package_id="$1"
  local state="$2"
  local error="$3"
  local fingerprint="$4"
  local failed_command="$5"
  local conflict_files="$6"
  local log_summary="$7"
  local recovery_hint="$8"
  local old_state="${9:-}"
  local extra
  extra="$(json_pair "state" "$state")$(json_pair "error" "$error")$(json_pair "fingerprint" "$fingerprint")$(json_pair "failed_command" "$failed_command")$(json_pair "conflict_files" "$conflict_files")$(json_pair "log_summary" "$log_summary")$(json_pair "recovery_hint" "$recovery_hint")"
  if [ "$old_state" = "$state" ] && terminal_failure_recorded "$package_id" "$state" "$fingerprint"; then
    emit_event "terminal_failure_duplicate" "$package_id" "$extra"
    return 0
  fi
  emit_event "terminal_failure" "$package_id" "$extra"
}

enforce_retry_breaker() {
  local package_id="$1"
  local last_error fingerprint count
  last_error="$(state_field "$package_id" last_error || true)"
  [ -n "$last_error" ] && [ "$last_error" != "pending" ] || return 0
  fingerprint="$(failure_fingerprint "$last_error")"
  [ -n "$fingerprint" ] || return 0
  count="$(terminal_failure_count "$package_id" "$fingerprint")"
  if [ "$count" -ge 3 ]; then
    emit_event "retry_blocked" "$package_id" "$(json_pair "fingerprint" "$fingerprint")$(json_pair "failure_count" "$count")"
    die "retry breaker open for $package_id after $count repeated failures: $fingerprint"
  fi
}

acquire_lock() {
  local tries=0
  until mkdir "$LOCK_DIR" 2>/dev/null; do
    tries=$((tries + 1))
    if [ "$tries" -gt 30 ]; then
      die "could not acquire lock: $LOCK_DIR"
    fi
    sleep 1
  done
  printf '%s\n' "$$" > "$LOCK_DIR/pid"
  LOCK_ACQUIRED=1
}

release_lock() {
  if [ "$LOCK_ACQUIRED" -eq 1 ] &&
    [ -f "$LOCK_DIR/pid" ] &&
    [ "$(cat "$LOCK_DIR/pid" 2>/dev/null || true)" = "$$" ]; then
    rm -rf "$LOCK_DIR"
  fi
}

trap 'release_lock' EXIT

valid_state() {
  case "$1" in
    pending|ready|manual_required|launched|in_progress|completed|blocked|stale|invalid|finalizing|finalized)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

graph_field() {
  local package_id="$1"
  local column="$2"
  awk -F '\t' -v id="$package_id" -v col="$column" '
    FNR == 1 {
      for (i = 1; i <= NF; i++) idx[$i] = i
      next
    }
    $1 == id {
      print $idx[col]
      found = 1
      exit
    }
    END { if (!found) exit 1 }
  ' "$GRAPH"
}

state_field() {
  local package_id="$1"
  local column="$2"
  awk -F '\t' -v id="$package_id" -v col="$column" '
    /^# signature:/ { next }
    FNR == 1 {
      for (i = 1; i <= NF; i++) idx[$i] = i
      next
    }
    $1 == id {
      print $idx[col]
      found = 1
      exit
    }
    END { if (!found) exit 1 }
  ' "$STATE"
}

resolve_worktree_path() {
  local path="$1"
  case "$path" in
    ""|pending)
      printf '%s\n' "$path"
      ;;
    /*)
      printf '%s\n' "$path"
      ;;
    *)
      printf '%s/%s\n' "$REPO_ROOT" "$path"
      ;;
  esac
}

physical_path() {
  local path="$1"
  local dir base
  if [ -d "$path" ]; then
    (cd "$path" && pwd -P)
    return 0
  fi
  dir="$(dirname "$path")"
  base="$(basename "$path")"
  if [ -d "$dir" ]; then
    printf '%s/%s\n' "$(cd "$dir" && pwd -P)" "$base"
    return 0
  fi
  printf '%s\n' "$path"
}

graph_worktree() {
  resolve_worktree_path "$(graph_field "$1" worktree)"
}

state_worktree() {
  resolve_worktree_path "$(state_field "$1" worktree)"
}

all_package_ids() {
  awk -F '\t' 'FNR > 1 && NF { print $1 }' "$GRAPH"
}

functional_package_ids() {
  awk -F '\t' 'FNR > 1 && NF && $10 != "1" { print $1 }' "$GRAPH"
}

finalize_package_id() {
  awk -F '\t' 'FNR > 1 && NF && $10 == "1" { print $1; exit }' "$GRAPH"
}

cleanup_complete() {
  awk -F '\t' '
    /^# signature:/ { next }
    FNR == 1 {
      for (i = 1; i <= NF; i++) idx[$i] = i
      next
    }
    NF && $idx["cleanup"] != "removed" { exit 1 }
  ' "$STATE"
}

status_file_for() {
  local package_id="$1"
  local rel
  rel="$(graph_field "$package_id" status_file)"
  printf '%s/%s\n' "$PLAN_ROOT" "$rel"
}

markdown_status() {
  local package_id="$1"
  local file line value
  file="$(status_file_for "$package_id")"
  if [ ! -f "$file" ]; then
    printf 'missing\n'
    return
  fi
  line="$(awk '
    /^## State/ { in_state = 1; next }
    in_state && /`/ {
      gsub(/`/, "", $0)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", $0)
      print tolower($0)
      exit
    }
    /\*\*Status\*\*:/ {
      sub(/^.*\*\*Status\*\*:[[:space:]]*/, "", $0)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", $0)
      print tolower($0)
      exit
    }
  ' "$file")"
  value="${line:-unknown}"
  case "$value" in
    done|complete) printf 'completed\n' ;;
    *) printf '%s\n' "$value" ;;
  esac
}

sync_markdown_state() {
  local package_id="$1"
  local new_state="$2"
  local file tmp
  file="$(status_file_for "$package_id")"
  [ -f "$file" ] || return 0
  tmp="$(mktemp)"
  awk -v new_state="$new_state" '
    /^## State/ {
      print
      in_state = 1
      changed = 0
      next
    }
    in_state && !changed && /`/ {
      print "`" new_state "`"
      changed = 1
      in_state = 0
      next
    }
    /\*\*Status\*\*:/ {
      print "**Status**: " new_state
      changed = 1
      next
    }
    { print }
    END {
      if (!changed) {
        print ""
        print "## State"
        print ""
        print "`" new_state "`"
      }
    }
  ' "$file" > "$tmp"
  mv "$tmp" "$file"
}

preflight_files() {
  [ -f "$PLAN_ROOT/INDEX.md" ] || die "missing INDEX.md"
  [ -f "$GRAPH" ] || die "missing package graph: $GRAPH"
  [ -f "$STATE" ] || die "missing state ledger: $STATE"
  [ -f "$PROMPTS" ] || die "missing agent prompts: $PROMPTS"
}

preflight_graph() {
  preflight_files
  [ "$(head -n 1 "$GRAPH")" = "$GRAPH_HEADER" ] || die "invalid graph header"
  awk -F '\t' '
    FNR == 1 { next }
    NF == 0 { next }
    NF != 10 {
      printf("graph row has %d fields, expected 10: %s\n", NF, $0) > "/dev/stderr"
      bad = 1
    }
    seen[$1]++ {
      printf("duplicate package id: %s\n", $1) > "/dev/stderr"
      bad = 1
    }
    $10 == "1" { finalize++ }
    END {
      if (finalize != 1) {
        printf("expected exactly one finalize row, got %d\n", finalize + 0) > "/dev/stderr"
        bad = 1
      }
      exit bad ? 1 : 0
    }
  ' "$GRAPH" || die "graph validation failed"

  awk -F '\t' '
    FNR == 1 { next }
    NF == 0 { next }
    { ids[$1] = 1; deps[$1] = $4 }
    END {
      for (id in ids) {
        split(deps[id], arr, ",")
        for (i in arr) {
          dep = arr[i]
          gsub(/^[[:space:]]+|[[:space:]]+$/, "", dep)
          if (dep == "") continue
          if (!(dep in ids)) {
            printf("missing dependency: %s -> %s\n", id, dep) > "/dev/stderr"
            bad = 1
          }
          if (dep == id) {
            printf("self dependency: %s\n", id) > "/dev/stderr"
            bad = 1
          }
        }
      }
      exit bad ? 1 : 0
    }
  ' "$GRAPH" || die "graph dependency validation failed"
}

preflight_state() {
  [ -s "$STATE" ] || die "state ledger is empty; run repair-state"
  [ "$(head -n 1 "$STATE")" = "$STATE_HEADER" ] || die "invalid state header"
  awk -F '\t' '
    FNR == NR {
      if (FNR > 1 && NF) ids[$1] = 1
      next
    }
    /^# signature:/ { next }
    FNR == 1 { next }
    NF == 0 { next }
    {
      if (NF != 17) {
        printf("state row has %d fields, expected 17: %s\n", NF, $0) > "/dev/stderr"
        bad = 1
      }
      if (!($1 in ids)) {
        printf("state has unknown package: %s\n", $1) > "/dev/stderr"
        bad = 1
      }
      seen[$1] = 1
      if ($2 !~ /^(pending|ready|manual_required|launched|in_progress|completed|blocked|stale|invalid|finalizing|finalized)$/) {
        printf("invalid state for %s: %s\n", $1, $2) > "/dev/stderr"
        bad = 1
      }
    }
    END {
      for (id in ids) {
        if (!(id in seen)) {
          printf("state missing package: %s\n", id) > "/dev/stderr"
          bad = 1
        }
      }
      exit bad ? 1 : 0
    }
  ' "$GRAPH" "$STATE" || die "state validation failed"
}

preflight_state_signature() {
  if verify_state_signature; then
    return 0
  fi
  # Auto-initialize signature if state.tsv has no signature file yet
  if [ ! -f "$SIG_FILE" ]; then
    ensure_signing_secret
    local sig
    sig="$(compute_state_signature)"
    if [ "$sig" != "unsigned" ] && [ -n "$sig" ]; then
      printf '# signature:%s\n' "$sig" >> "$STATE"
      return 0
    fi
  fi
  die "state.tsv integrity check failed; use repair-state to reinitialize"
}

validate_events_cleanup() {
  local finalize_id bad=0
  finalize_id="$(finalize_package_id)"
  state="$(state_field "$finalize_id" state || true)"
  [ "$state" = "finalized" ] || return 0
  if [ -f "$EVENTS" ] && ! grep -q '"event":"cleanup_succeeded"' "$EVENTS" 2>/dev/null; then
    printf 'events.jsonl: 99-finalize is finalized but no cleanup_succeeded event found\n' >&2
    bad=1
  fi
  local id line_state line_cleanup
  while IFS= read -r id; do
    line_state="$(state_field "$id" state || true)"
    line_cleanup="$(state_field "$id" cleanup || true)"
    if [ "$line_state" = "finalized" ] && [ "$line_cleanup" != "removed" ] && [ -n "$line_cleanup" ]; then
      printf 'state.tsv: %s is finalized but cleanup is "%s" (expected "removed")\n' "$id" "$line_cleanup" >&2
      bad=1
    fi
  done < <(all_package_ids)
  return "$bad"
}

preflight_prompts() {
  awk -F '\t' '
    FNR == NR {
      if (FNR > 1 && NF) ids[$1] = 1
      next
    }
    /^## Package:/ {
      heading = $0
      if (heading !~ /^## Package: [^[:space:]]+ - .+$/) {
        printf("malformed prompt heading: %s\n", heading) > "/dev/stderr"
        bad = 1
        next
      }
      sub(/^## Package: /, "", heading)
      package_id = heading
      sub(/ - .+$/, "", package_id)
      if (!(package_id in ids)) {
        printf("prompt heading has unknown package: %s\n", package_id) > "/dev/stderr"
        bad = 1
        next
      }
      count[package_id]++
      if (count[package_id] > 1) {
        printf("duplicate prompt heading for package: %s\n", package_id) > "/dev/stderr"
        bad = 1
      }
    }
    END {
      for (package_id in ids) {
        if (count[package_id] == 0) {
          printf("prompt missing canonical heading: ## Package: %s - <title>\n", package_id) > "/dev/stderr"
          bad = 1
        }
      }
      exit bad ? 1 : 0
    }
  ' "$GRAPH" "$PROMPTS" || die "prompt validation failed"
}

preflight_all() {
  preflight_graph
  preflight_prompts
  preflight_state
  preflight_state_signature
  validate_events_cleanup || die "events.jsonl and state.tsv mismatch: cleanup not recorded"
}

status_consistency_ok() {
  local id state md
  while IFS= read -r id; do
    [ -n "$id" ] || continue
    state="$(state_field "$id" state)"
    md="$(markdown_status "$id")"
    case "$md" in
      missing|unknown)
        printf 'INVALID: %s markdown status is %s\n' "$id" "$md" >&2
        return 1
        ;;
    esac
    if [ "$state" = "completed" ] && [ "$md" != "completed" ]; then
      printf 'INVALID: %s state completed but markdown is %s\n' "$id" "$md" >&2
      return 1
    fi
    if [ "$md" = "completed" ] && [ "$state" != "completed" ] && [ "$state" != "finalized" ]; then
      printf 'INVALID: %s markdown completed but state is %s\n' "$id" "$state" >&2
      return 1
    fi
  done < <(all_package_ids)
  return 0
}

set_state_fields() {
  local package_id="$1"
  local new_state="$2"
  local launched_at="${3:-__KEEP__}"
  local completed_at="${4:-__KEEP__}"
  local agent="${5:-__KEEP__}"
  local branch="${6:-__KEEP__}"
  local worktree="${7:-__KEEP__}"
  local base_commit="${8:-__KEEP__}"
  local commit_hash="${9:-__KEEP__}"
  local verification="${10:-__KEEP__}"
  local integration="${11:-__KEEP__}"
  local cleanup="${12:-__KEEP__}"
  local last_error="${13:-__KEEP__}"
  local failed_command="${14:-__KEEP__}"
  local conflict_files="${15:-__KEEP__}"
  local log_summary="${16:-__KEEP__}"
  local recovery_hint="${17:-__KEEP__}"
  local now tmp old_state event_extra

  valid_state "$new_state" || die "invalid state: $new_state"
  old_state="$(state_field "$package_id" state || true)"
  now="$(timestamp)"
  tmp="$(mktemp)"
  awk -F '\t' -v OFS='\t' \
    -v id="$package_id" \
    -v new_state="$new_state" \
    -v now="$now" \
    -v launched="$launched_at" \
    -v completed="$completed_at" \
    -v agent="$agent" \
    -v branch="$branch" \
    -v worktree="$worktree" \
    -v base="$base_commit" \
    -v commit="$commit_hash" \
    -v verification="$verification" \
    -v integration="$integration" \
    -v cleanup="$cleanup" \
    -v last_error="$last_error" \
    -v failed_command="$failed_command" \
    -v conflict_files="$conflict_files" \
    -v log_summary="$log_summary" \
    -v recovery_hint="$recovery_hint" '
      FNR == 1 {
        for (i = 1; i <= NF; i++) idx[$i] = i
        seen_sig = 0
        print
        next
      }
      /^# signature:/ { seen_sig = 1; next }
      $1 == id {
        $idx["state"] = new_state
        if (launched == "__NOW__" || ((new_state == "launched" || new_state == "in_progress" || new_state == "finalizing") && launched == "__KEEP__")) $idx["launched_at"] = now
        else if (launched != "__KEEP__") $idx["launched_at"] = launched
        if (completed == "__NOW__" || ((new_state == "completed" || new_state == "blocked" || new_state == "stale" || new_state == "invalid" || new_state == "finalized") && completed == "__KEEP__")) $idx["completed_at"] = now
        else if (completed != "__KEEP__") $idx["completed_at"] = completed
        if (agent != "__KEEP__") $idx["agent"] = agent
        if (branch != "__KEEP__") $idx["branch"] = branch
        if (worktree != "__KEEP__") $idx["worktree"] = worktree
        if (base != "__KEEP__") $idx["base_commit"] = base
        if (commit != "__KEEP__") $idx["commit_hash"] = commit
        if (verification != "__KEEP__") $idx["verification"] = verification
        if (integration != "__KEEP__") $idx["integration"] = integration
        if (cleanup != "__KEEP__") $idx["cleanup"] = cleanup
        if (last_error != "__KEEP__") $idx["last_error"] = last_error
        else if (new_state == "completed" || new_state == "finalized") $idx["last_error"] = ""
        if (failed_command != "__KEEP__") $idx["failed_command"] = failed_command
        else if (new_state == "completed" || new_state == "finalized") $idx["failed_command"] = ""
        if (conflict_files != "__KEEP__") $idx["conflict_files"] = conflict_files
        else if (new_state == "completed" || new_state == "finalized") $idx["conflict_files"] = ""
        if (log_summary != "__KEEP__") $idx["log_summary"] = log_summary
        else if (new_state == "completed" || new_state == "finalized") $idx["log_summary"] = ""
        if (recovery_hint != "__KEEP__") $idx["recovery_hint"] = recovery_hint
        else if (new_state == "completed" || new_state == "finalized") $idx["recovery_hint"] = ""
        touched = 1
      }
      /^# signature:/ { next }
      { print }
      END { if (!touched) exit 1 }
    ' "$STATE" > "$tmp" || {
      rm -f "$tmp"
      if ! verify_state_signature; then
        die "state.tsv integrity check failed during write; aborting"
      fi
      die "unknown package in state ledger: $package_id"
    }
  mv "$tmp" "$STATE"
  sync_markdown_state "$package_id" "$new_state"
  event_extra="$(json_pair "old_state" "$old_state")$(json_pair "new_state" "$new_state")"
  if [ "$last_error" != "__KEEP__" ]; then
    event_extra="$event_extra$(json_pair "last_error" "$last_error")"
  fi
  if [ "$failed_command" != "__KEEP__" ]; then
    event_extra="$event_extra$(json_pair "failed_command" "$failed_command")"
  fi
  if [ "$conflict_files" != "__KEEP__" ]; then
    event_extra="$event_extra$(json_pair "conflict_files" "$conflict_files")"
  fi
  if [ "$log_summary" != "__KEEP__" ]; then
    event_extra="$event_extra$(json_pair "log_summary" "$log_summary")"
  fi
  if [ "$recovery_hint" != "__KEEP__" ]; then
    event_extra="$event_extra$(json_pair "recovery_hint" "$recovery_hint")"
  fi
  emit_event "state_changed" "$package_id" "$event_extra"
  # Append signature after every state.tsv mutation
  local sig
  sig="$(compute_state_signature)"
  if [ "$sig" != "unsigned" ] && [ -n "$sig" ]; then
    printf '# signature:%s\n' "$sig" >> "$STATE"
  fi
}

set_error_state() {
  local package_id="$1"
  local new_state="$2"
  local message="$3"
  local failed_command="${4:-}"
  local conflict_files="${5:-}"
  local log_summary="${6:-}"
  local recovery_hint="${7:-}"
  local fingerprint old_state
  old_state="$(state_field "$package_id" state || true)"
  message="$(tsv_safe "$message")"
  failed_command="$(tsv_safe "$failed_command")"
  conflict_files="$(tsv_safe "$conflict_files")"
  log_summary="$(tsv_safe "$log_summary")"
  recovery_hint="$(tsv_safe "$recovery_hint")"
  set_state_fields "$package_id" "$new_state" "__KEEP__" "__NOW__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "$message" "$failed_command" "$conflict_files" "$log_summary" "$recovery_hint"
  fingerprint="$(failure_fingerprint "$message")"
  emit_terminal_failure_event "$package_id" "$new_state" "$message" "$fingerprint" "$failed_command" "$conflict_files" "$log_summary" "$recovery_hint" "$old_state"
}

deps_completed() {
  local package_id="$1"
  local deps dep state
  deps="$(graph_field "$package_id" dependencies || true)"
  [ -z "$deps" ] && return 0
  IFS=',' read -r -a dep_array <<< "$deps"
  for dep in "${dep_array[@]}"; do
    dep="${dep#"${dep%%[![:space:]]*}"}"
    dep="${dep%"${dep##*[![:space:]]}"}"
    [ -z "$dep" ] && continue
    state="$(state_field "$dep" state)"
    [ "$state" = "completed" ] || [ "$state" = "finalized" ] || return 1
  done
  return 0
}

dependency_type_has_code() {
  case "$1" in
    code|status+code)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

package_has_code_dependencies() {
  local package_id="$1"
  local dep_type deps
  dep_type="$(graph_field "$package_id" dependency_type || true)"
  deps="$(graph_field "$package_id" dependencies || true)"
  [ -n "$deps" ] && dependency_type_has_code "$dep_type"
}

trim_dep() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf '%s' "$value"
}

ensure_integration_worktree() {
  local parent
  parent="$(dirname "$ORCHESTRATION_INTEGRATION_WORKTREE")"
  mkdir -p "$parent"
  if git -C "$ORCHESTRATION_INTEGRATION_WORKTREE" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    return 0
  fi
  if git -C "$REPO_ROOT" rev-parse --verify "$ORCHESTRATION_INTEGRATION_BRANCH" >/dev/null 2>&1; then
    git -C "$REPO_ROOT" worktree add "$ORCHESTRATION_INTEGRATION_WORKTREE" "$ORCHESTRATION_INTEGRATION_BRANCH" >/dev/null
  else
    git -C "$REPO_ROOT" worktree add -B "$ORCHESTRATION_INTEGRATION_BRANCH" "$ORCHESTRATION_INTEGRATION_WORKTREE" HEAD >/dev/null
  fi
}

merge_code_dependency_into_integration() {
  local package_id="$1"
  local dep="$2"
  local dep_commit="$3"
  local output status conflict_files

  ensure_integration_worktree
  if [ -n "$(git -C "$ORCHESTRATION_INTEGRATION_WORKTREE" status --porcelain)" ]; then
    set_error_state "$package_id" "blocked" "integration worktree is dirty before merging code dependency $dep" "git -C $ORCHESTRATION_INTEGRATION_WORKTREE status --porcelain" "" "Integration worktree has uncommitted or conflicted files." "Resolve or clean $ORCHESTRATION_INTEGRATION_WORKTREE, then retry $package_id."
    return 1
  fi
  if git -C "$ORCHESTRATION_INTEGRATION_WORKTREE" merge-base --is-ancestor "$dep_commit" HEAD >/dev/null 2>&1; then
    return 0
  fi

  set +e
  output="$(git -C "$ORCHESTRATION_INTEGRATION_WORKTREE" merge --no-edit "$dep_commit" 2>&1)"
  status=$?
  set -e
  if [ "$status" -ne 0 ]; then
    conflict_files="$(git -C "$ORCHESTRATION_INTEGRATION_WORKTREE" diff --name-only --diff-filter=U 2>/dev/null | paste -sd, -)"
    set_error_state "$package_id" "blocked" "failed to merge code dependency $dep into $ORCHESTRATION_INTEGRATION_BRANCH" "git merge $dep_commit" "$conflict_files" "$(tsv_safe "$output")" "Resolve conflicts in $ORCHESTRATION_INTEGRATION_WORKTREE, commit the integration branch, then retry $package_id."
    return 1
  fi
  emit_event "code_dependency_merged" "$package_id" "$(json_pair "dependency" "$dep")$(json_pair "dependency_commit" "$dep_commit")$(json_pair "integration_branch" "$ORCHESTRATION_INTEGRATION_BRANCH")$(json_pair "integration_worktree" "$ORCHESTRATION_INTEGRATION_WORKTREE")"
  return 0
}

prepare_code_dependency_base() {
  local package_id="$1"
  local deps dep dep_commit
  package_has_code_dependencies "$package_id" || return 0
  deps="$(graph_field "$package_id" dependencies || true)"
  IFS=',' read -r -a dep_array <<< "$deps"
  for dep in "${dep_array[@]}"; do
    dep="$(trim_dep "$dep")"
    [ -z "$dep" ] && continue
    dep_commit="$(state_field "$dep" commit_hash || true)"
    if [ -z "$dep_commit" ] || [ "$dep_commit" = "pending" ]; then
      set_error_state "$package_id" "invalid" "code dependency $dep is completed without commit_hash" "state_field $dep commit_hash" "" "Dependency type requires a concrete upstream commit before downstream launch." "Mark $dep completed with --commit <sha>, then retry $package_id."
      return 1
    fi
    if ! git -C "$REPO_ROOT" cat-file -e "$dep_commit^{commit}" >/dev/null 2>&1; then
      set_error_state "$package_id" "invalid" "code dependency $dep commit_hash does not exist: $dep_commit" "git cat-file -e $dep_commit^{commit}" "" "Dependency type requires an existing upstream commit before downstream launch." "Repair $dep commit_hash or rerun the upstream package."
      return 1
    fi
    if ! merge_code_dependency_into_integration "$package_id" "$dep" "$dep_commit"; then
      return 1
    fi
  done
  return 0
}

worktree_base_ref() {
  local package_id="$1"
  if package_has_code_dependencies "$package_id"; then
    printf '%s\n' "$ORCHESTRATION_INTEGRATION_BRANCH"
  else
    printf 'HEAD\n'
  fi
}

any_bad_terminal_state() {
  awk -F '\t' 'FNR > 1 && ($2 == "blocked" || $2 == "stale" || $2 == "invalid") { print $1 ":" $2 }' "$STATE"
}

all_functional_completed() {
  local id
  while IFS= read -r id; do
    [ -n "$id" ] || continue
    [ "$(state_field "$id" state)" = "completed" ] || return 1
  done < <(functional_package_ids)
  return 0
}

running_count() {
  awk -F '\t' 'FNR > 1 && ($2 == "launched" || $2 == "in_progress" || $2 == "finalizing") { count++ } END { print count + 0 }' "$STATE"
}

ready_packages() {
  local id state manual
  while IFS= read -r id; do
    [ -n "$id" ] || continue
    state="$(state_field "$id" state)"
    manual="$(graph_field "$id" manual)"
    if { [ "$state" = "pending" ] || [ "$state" = "ready" ]; } && [ "$manual" != "1" ] && deps_completed "$id"; then
      printf '%s\n' "$id"
    fi
  done < <(functional_package_ids)
}

mark_ready_manual_packages() {
  local id state manual
  while IFS= read -r id; do
    [ -n "$id" ] || continue
    state="$(state_field "$id" state)"
    manual="$(graph_field "$id" manual)"
    if { [ "$state" = "pending" ] || [ "$state" = "ready" ] || [ "$state" = "manual_required" ]; } &&
      [ "$manual" = "1" ] && deps_completed "$id"; then
      prepare_code_dependency_base "$id" || continue
      if [ "$state" != "manual_required" ]; then
        set_state_fields "$id" "manual_required" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" ""
      fi
      log "manual package ready: $id"
    fi
  done < <(functional_package_ids)
}

prompt_for_package() {
  local package_id="$1"
  awk -v id="$package_id" '
    $0 ~ "^## Package: " id "([[:space:]-]|$)" { found = 1; print; next }
    found && /^## Package: / { exit }
    found { print }
  ' "$PROMPTS"
}

ensure_worktree() {
  local package_id="$1"
  local branch worktree parent base_ref base_commit deps dep dep_commit
  branch="$(graph_field "$package_id" branch)"
  worktree="$(graph_worktree "$package_id")"
  parent="$(dirname "$worktree")"
  mkdir -p "$parent"
  if git -C "$worktree" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if package_has_code_dependencies "$package_id"; then
      deps="$(graph_field "$package_id" dependencies || true)"
      IFS=',' read -r -a dep_array <<< "$deps"
      for dep in "${dep_array[@]}"; do
        dep="$(trim_dep "$dep")"
        [ -z "$dep" ] && continue
        dep_commit="$(state_field "$dep" commit_hash || true)"
        if [ -n "$dep_commit" ] && [ "$dep_commit" != "pending" ] &&
          ! git -C "$worktree" merge-base --is-ancestor "$dep_commit" HEAD >/dev/null 2>&1; then
          set_error_state "$package_id" "invalid" "existing worktree baseline does not contain code dependency $dep" "git merge-base --is-ancestor $dep_commit HEAD" "" "Worktree $worktree is not based on the required integration baseline." "Remove/recreate the package worktree from $ORCHESTRATION_INTEGRATION_BRANCH, then retry $package_id."
          return 1
        fi
      done
    fi
    base_commit="$(git -C "$worktree" rev-parse HEAD)"
    set_state_fields "$package_id" "$(state_field "$package_id" state)" "__KEEP__" "__KEEP__" "__KEEP__" "$branch" "$worktree" "$base_commit" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__"
    return 0
  fi
  base_ref="$(worktree_base_ref "$package_id")"
  git -C "$REPO_ROOT" worktree add -B "$branch" "$worktree" "$base_ref" >/dev/null
  base_commit="$(git -C "$worktree" rev-parse HEAD)"
  set_state_fields "$package_id" "$(state_field "$package_id" state)" "__KEEP__" "__KEEP__" "__KEEP__" "$branch" "$worktree" "$base_commit" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__"
}

validate_runner() {
  case "$ORCHESTRATION_RUNNER" in
    claude|codex)
      return 0
      ;;
    *)
      die "unsupported ORCHESTRATION_RUNNER: $ORCHESTRATION_RUNNER"
      ;;
  esac
}

persist_runner() {
  local current=""
  validate_runner
  mkdir -p "$(dirname "$RUNNER_STATE")"
  if [ -f "$RUNNER_STATE" ]; then
    current="$(head -n 1 "$RUNNER_STATE")"
  fi
  if [ "$current" != "$ORCHESTRATION_RUNNER" ]; then
    printf '%s\n' "$ORCHESTRATION_RUNNER" > "$RUNNER_STATE"
    emit_event "runner_selected" "" "$(json_pair "runner" "$ORCHESTRATION_RUNNER")$(json_pair "source" "$ORCHESTRATION_RUNNER_SOURCE")$(json_pair "previous_runner" "$current")"
  fi
}

validate_permission_mode() {
  case "$CLAUDE_PERMISSION_MODE" in
    ""|default|acceptEdits|plan)
      return 0
      ;;
    auto)
      [ "${CLAUDE_AUTO_MODE_OPTED_IN:-}" = "1" ] ||
        die "CLAUDE_PERMISSION_MODE=auto requires CLAUDE_AUTO_MODE_OPTED_IN=1 after running claude --permission-mode auto interactively"
      ;;
    bypassPermissions)
      [ "${CLAUDE_BYPASS_PERMISSIONS_APPROVED:-}" = "1" ] ||
        die "CLAUDE_PERMISSION_MODE=bypassPermissions requires CLAUDE_BYPASS_PERMISSIONS_APPROVED=1; this repo must not silently grant bypass permissions"
      ;;
    *)
      die "unsupported CLAUDE_PERMISSION_MODE: $CLAUDE_PERMISSION_MODE"
      ;;
  esac
}

validate_codex_runner() {
  case "$ORCHESTRATION_CODEX_SANDBOX" in
    read-only|workspace-write|danger-full-access)
      ;;
    *)
      die "unsupported ORCHESTRATION_CODEX_SANDBOX: $ORCHESTRATION_CODEX_SANDBOX"
      ;;
  esac
  case "$ORCHESTRATION_CODEX_APPROVAL_POLICY" in
    untrusted|on-request|never)
      ;;
    *)
      die "unsupported ORCHESTRATION_CODEX_APPROVAL_POLICY: $ORCHESTRATION_CODEX_APPROVAL_POLICY"
      ;;
  esac
}

codex_exec_supports_approval_policy() {
  codex exec --help 2>&1 | grep -q -- "--ask-for-approval"
}

codex_home_path() {
  printf '%s\n' "${CODEX_HOME:-${HOME:-}/.codex}"
}

codex_home_is_writable() {
  local codex_home probe
  codex_home="$(codex_home_path)"
  [ -n "$codex_home" ] && [ -d "$codex_home" ] || return 1
  probe="$codex_home/.orchestrate-write-probe.$$"
  if ! : > "$probe" 2>/dev/null; then
    return 1
  fi
  rm -f "$probe"
}

codex_pid_file() {
  printf '%s/status/codex-%s.pid\n' "$PLAN_ROOT" "$1"
}

parse_session_id() {
  sed -E $'s/\x1B\\[[0-9;]*[[:alpha:]]//g' | awk '
    /backgrounded/ {
      for (i = 1; i <= NF; i++) {
        if ($i == "backgrounded" || $i == "·" || $i == "-" || $i == "•") continue
        if ($i ~ /^[[:alnum:]_-]{6,}$/) {
          print $i
          exit
        }
      }
    }
  '
}

parse_codex_thread_id() {
  sed -n 's/.*"thread_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1
}

collect_agent_logs() {
  local package_id="$1"
  local session_id="${2:-}"
  local reason="${3:-manual}"
  local log_file output status size
  if [ -z "$session_id" ] || [ "$session_id" = "pending" ]; then
    session_id="$(state_field "$package_id" agent || true)"
  fi
  if [ -z "$session_id" ] || [ "$session_id" = "pending" ]; then
    return 2
  fi
  mkdir -p "$LOGS_DIR"
  log_file="$LOGS_DIR/$package_id.log"
  if ! command -v claude >/dev/null 2>&1; then
    printf 'claude command not found\n' > "$log_file"
    emit_event "agent_logs_unreadable" "$package_id" "$(json_pair "session_id" "$session_id")$(json_pair "reason" "$reason")$(json_pair "logs_path" "$log_file")$(json_pair "error" "claude command not found")"
    printf '%s\n' "$log_file"
    return 3
  fi

  set +e
  output="$(claude logs "$session_id" 2>&1)"
  status=$?
  set -e
  printf '%s\n' "$output" > "$log_file"
  size="$(wc -c < "$log_file" | tr -d ' ')"
  if [ "$status" -eq 0 ]; then
    emit_event "agent_logs_collected" "$package_id" "$(json_pair "session_id" "$session_id")$(json_pair "reason" "$reason")$(json_pair "logs_path" "$log_file")$(json_pair "bytes" "$size")"
    printf '%s\n' "$log_file"
    return 0
  fi
  emit_event "agent_logs_unreadable" "$package_id" "$(json_pair "session_id" "$session_id")$(json_pair "reason" "$reason")$(json_pair "logs_path" "$log_file")$(json_pair "error" "$output")"
  printf '%s\n' "$log_file"
  return 1
}

reconcile_active_agents() {
  local id state session_id logs_path count=0
  while IFS= read -r id; do
    [ -n "$id" ] || continue
    state="$(state_field "$id" state)"
    case "$state" in
      launched|in_progress|finalizing)
        ;;
      *)
        continue
        ;;
    esac
    session_id="$(state_field "$id" agent || true)"
    if [ -z "$session_id" ] || [ "$session_id" = "pending" ]; then
      set_error_state "$id" "stale" "active package has no recorded background session id" "state_field $id agent" "" "No session id recorded for active package" "Inspect state.tsv and relaunch or mark the package manually."
      emit_event "agent_lost" "$id" "$(json_pair "session_id" "$session_id")$(json_pair "reason" "missing_session_id")"
      count=$((count + 1))
      continue
    fi
    if logs_path="$(collect_agent_logs "$id" "$session_id" "reconcile")"; then
      emit_event "agent_health_checked" "$id" "$(json_pair "session_id" "$session_id")$(json_pair "session_status" "logs_readable")$(json_pair "logs_path" "$logs_path")"
    else
      set_error_state "$id" "stale" "claude session $session_id logs are not readable during doctor reconcile; see ${logs_path:-$PLAN_ROOT/status/logs/$id.log}" "claude logs $session_id" "" "Claude logs snapshot saved to ${logs_path:-status/logs/$id.log}" "Open claude agents/logs manually, then mark completed or retry."
      emit_event "agent_lost" "$id" "$(json_pair "session_id" "$session_id")$(json_pair "reason" "logs_unreadable")$(json_pair "logs_path" "${logs_path:-}")"
      count=$((count + 1))
    fi
  done < <(all_package_ids)
  printf '%s\n' "$count"
}

reconcile_active_codex() {
  local id state pid_file pid launch_log count=0
  while IFS= read -r id; do
    [ -n "$id" ] || continue
    state="$(state_field "$id" state)"
    case "$state" in
      launched|in_progress|finalizing)
        ;;
      *)
        continue
        ;;
    esac
    pid_file="$(codex_pid_file "$id")"
    pid="$(cat "$pid_file" 2>/dev/null || true)"
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      emit_event "agent_health_checked" "$id" "$(json_pair "runner" "codex")$(json_pair "process_id" "$pid")$(json_pair "session_status" "process_alive")"
      continue
    fi
    launch_log="$PLAN_ROOT/status/launch-$id.log"
    if [ -f "$launch_log" ] && grep -q '"type":"turn.completed"' "$launch_log"; then
      set_error_state "$id" "stale" "codex process completed without recording final package state" "codex exec --json" "" "Launch log reached turn.completed but coordinator state remained $state." "Inspect $launch_log and the package worktree, then mark completed with evidence or retry."
    else
      set_error_state "$id" "stale" "codex thread stalled after turn.started with no active codex exec process" "codex exec --json" "" "Launch log has no terminal event and recorded process is not active." "Inspect $launch_log and the package worktree, then retry or mark the package manually."
    fi
    emit_event "agent_lost" "$id" "$(json_pair "runner" "codex")$(json_pair "process_id" "$pid")$(json_pair "reason" "process_not_active")$(json_pair "logs_path" "$launch_log")"
    count=$((count + 1))
  done < <(all_package_ids)
  printf '%s\n' "$count"
}

launch_with_claude() {
  local package_id="$1"
  local finalize name worktree branch prompt_file launch_log launch_output status session_id new_state version_output logs_path
  finalize="$(graph_field "$package_id" finalize)"
  name="$(basename "$PLAN_ROOT")-$package_id"
  worktree="$(graph_worktree "$package_id")"
  branch="$(graph_field "$package_id" branch)"
  prompt_file="$(mktemp)"
  launch_log="$PLAN_ROOT/status/launch-$package_id.log"

  prompt_for_package "$package_id" > "$prompt_file"
  if [ ! -s "$prompt_file" ]; then
    rm -f "$prompt_file"
    set_error_state "$package_id" "invalid" "prompt section missing" "prompt_for_package $package_id" "" "agent-prompts.md has no matching package section" "Regenerate launchers/agent-prompts.md for this package."
    die "prompt section missing for $package_id"
  fi

  if ! command -v claude >/dev/null 2>&1; then
    rm -f "$prompt_file"
    set_error_state "$package_id" "invalid" "claude command not found" "command -v claude" "" "Claude CLI is unavailable in PATH" "Run doctor --environment in the same shell and fix PATH before retry."
    die "claude command not found"
  fi

  validate_permission_mode
  version_output="$(claude --version 2>&1 || true)"
  log "claude: $version_output"
  ensure_worktree "$package_id"
  log "launching $package_id"
  log "  branch: $branch"
  log "  worktree: $worktree"
  emit_event "launch_requested" "$package_id" "$(json_pair "branch" "$branch")$(json_pair "worktree" "$worktree")$(json_pair "finalize" "$finalize")"

  set +e
  if [ -n "$CLAUDE_PERMISSION_MODE" ]; then
    launch_output="$(
      cd "$worktree" &&
        claude --bg --name "$name" --model "$CLAUDE_MODEL" --effort "$CLAUDE_EFFORT" \
          --permission-mode "$CLAUDE_PERMISSION_MODE" --setting-sources "$CLAUDE_SETTING_SOURCES" \
          < "$prompt_file" 2>&1
    )"
  else
    launch_output="$(
      cd "$worktree" &&
        claude --bg --name "$name" --model "$CLAUDE_MODEL" --effort "$CLAUDE_EFFORT" \
          --setting-sources "$CLAUDE_SETTING_SOURCES" < "$prompt_file" 2>&1
    )"
  fi
  status=$?
  set -e
  printf '%s\n' "$launch_output" > "$launch_log"
  rm -f "$prompt_file"

  if [ "$status" -ne 0 ]; then
    set_error_state "$package_id" "invalid" "claude launch failed; see $launch_log" "claude --bg --name $name" "" "Launch output saved to $launch_log" "Inspect the launch log and Claude environment, then retry."
    printf '%s\n' "$launch_output" >&2
    die "claude launch failed for $package_id"
  fi

  printf '%s\n' "$launch_output"
  session_id="$(printf '%s\n' "$launch_output" | parse_session_id)"
  if [ -z "$session_id" ]; then
    set_error_state "$package_id" "invalid" "missing background session id; see $launch_log" "parse_session_id" "" "Launch output did not contain a parseable background session id; see $launch_log" "Check the Claude CLI output format before retry."
    die "missing background session id for $package_id"
  fi

  if ! logs_path="$(collect_agent_logs "$package_id" "$session_id" "postflight")"; then
    set_error_state "$package_id" "stale" "claude session $session_id logs are not readable; see ${logs_path:-$launch_log}" "claude logs $session_id" "" "Session was launched but logs could not be read; snapshot saved to ${logs_path:-$launch_log}" "Open claude agents/logs manually, then mark completed or retry."
    die "claude session $session_id logs are not readable"
  fi

  if [ "$finalize" = "1" ]; then
    new_state="finalizing"
  else
    new_state="launched"
  fi
  set_state_fields "$package_id" "$new_state" "__NOW__" "__KEEP__" "$session_id" "$branch" "$worktree" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__"
  emit_event "launch_succeeded" "$package_id" "$(json_pair "session_id" "$session_id")$(json_pair "new_state" "$new_state")$(json_pair "branch" "$branch")$(json_pair "worktree" "$worktree")"
}

launch_with_codex() {
  local package_id="$1"
  local finalize worktree branch prompt_file launch_log stderr_log pid session_id new_state version_output poll
  finalize="$(graph_field "$package_id" finalize)"
  worktree="$(graph_worktree "$package_id")"
  branch="$(graph_field "$package_id" branch)"
  prompt_file="$(mktemp)"
  launch_log="$PLAN_ROOT/status/launch-$package_id.log"
  stderr_log="$PLAN_ROOT/status/launch-$package_id.stderr.log"

  prompt_for_package "$package_id" > "$prompt_file"
  if [ ! -s "$prompt_file" ]; then
    rm -f "$prompt_file"
    set_error_state "$package_id" "invalid" "prompt section missing" "prompt_for_package $package_id" "" "agent-prompts.md has no matching package section" "Regenerate launchers/agent-prompts.md for this package."
    die "prompt section missing for $package_id"
  fi

  if ! command -v codex >/dev/null 2>&1; then
    rm -f "$prompt_file"
    set_error_state "$package_id" "invalid" "codex command not found" "command -v codex" "" "Codex CLI is unavailable in PATH" "Run doctor --environment in the same shell and fix PATH before retry."
    die "codex command not found"
  fi

  validate_codex_runner
  version_output="$(codex --version 2>&1 || true)"
  log "codex: $version_output"
  if ! codex_home_is_writable; then
    rm -f "$prompt_file"
    set_error_state "$package_id" "invalid" "Codex home is not writable: $(codex_home_path)" "codex home write probe" "" "Codex requires writable local state before codex exec can initialize." "Run doctor --environment from the launch shell, then use a writable CODEX_HOME or an approved runner environment."
    die "Codex home is not writable: $(codex_home_path)"
  fi
  ensure_worktree "$package_id"
  log "launching $package_id with codex"
  log "  branch: $branch"
  log "  worktree: $worktree"
  emit_event "launch_requested" "$package_id" "$(json_pair "branch" "$branch")$(json_pair "worktree" "$worktree")$(json_pair "finalize" "$finalize")$(json_pair "runner" "codex")"

  local -a codex_args
  codex_args=(exec --json --sandbox "$ORCHESTRATION_CODEX_SANDBOX")
  if codex_exec_supports_approval_policy; then
    codex_args+=(--ask-for-approval "$ORCHESTRATION_CODEX_APPROVAL_POLICY")
  elif [ "$ORCHESTRATION_CODEX_APPROVAL_POLICY" != "never" ]; then
    rm -f "$prompt_file"
    set_error_state "$package_id" "invalid" "codex approval policy unsupported by installed CLI" "codex exec --help" "" "Installed Codex CLI does not support --ask-for-approval" "Use ORCHESTRATION_CODEX_APPROVAL_POLICY=never or install a Codex CLI version that supports approval policy flags."
    die "codex approval policy unsupported by installed CLI"
  fi
  if [ -n "$ORCHESTRATION_CODEX_MODEL" ]; then
    codex_args+=(--model "$ORCHESTRATION_CODEX_MODEL")
  fi
  if [ -n "$ORCHESTRATION_CODEX_EFFORT" ]; then
    codex_args+=(--config "model_reasoning_effort=\"$ORCHESTRATION_CODEX_EFFORT\"")
  fi
  codex_args+=("-")
  (
    cd "$worktree" &&
      codex "${codex_args[@]}" < "$prompt_file" > "$launch_log" 2> "$stderr_log"
  ) &
  pid=$!
  printf '%s\n' "$pid" > "$(codex_pid_file "$package_id")"
  rm -f "$prompt_file"

  session_id=""
  for poll in 1 2 3 4 5 6 7 8 9 10; do
    if [ -s "$launch_log" ]; then
      session_id="$(parse_codex_thread_id < "$launch_log" || true)"
      [ -n "$session_id" ] && break
    fi
    if ! kill -0 "$pid" 2>/dev/null; then
      wait "$pid" || true
      break
    fi
    sleep 0.25
  done

  if [ -z "$session_id" ]; then
    if ! kill -0 "$pid" 2>/dev/null; then
      local err
      err="$(tsv_safe "$(cat "$stderr_log" "$launch_log" 2>/dev/null || true)")"
      [ -n "$err" ] || err="codex process exited before emitting thread.started"
      set_error_state "$package_id" "invalid" "codex launch failed; see $launch_log" "codex exec --json" "" "$err" "Inspect $stderr_log and retry after fixing the Codex environment."
      die "codex launch failed for $package_id"
    fi
    session_id="codex-pid:$pid"
  else
    session_id="codex-thread:$session_id"
  fi

  if [ "$finalize" = "1" ]; then
    new_state="finalizing"
  else
    new_state="launched"
  fi
  set_state_fields "$package_id" "$new_state" "__NOW__" "__KEEP__" "$session_id" "$branch" "$worktree" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__"
  emit_event "launch_succeeded" "$package_id" "$(json_pair "session_id" "$session_id")$(json_pair "new_state" "$new_state")$(json_pair "branch" "$branch")$(json_pair "worktree" "$worktree")$(json_pair "runner" "codex")"
}

launch_package() {
  validate_runner
  prepare_code_dependency_base "$1" || die "code dependency baseline unavailable for $1"
  case "$ORCHESTRATION_RUNNER" in
    claude)
      launch_with_claude "$1"
      ;;
    codex)
      launch_with_codex "$1"
      ;;
  esac
}

launch_ready_or_finalize() {
  local bad id launched active finalize_id finalize_state
  preflight_all
  bad="$(any_bad_terminal_state)"
  if [ -n "$bad" ]; then
    printf 'STOP: blocked/stale/invalid package present:\n%s\n' "$bad" >&2
    exit 1
  fi
  status_consistency_ok || exit 1
  mark_ready_manual_packages

  if all_functional_completed; then
    finalize_id="$(finalize_package_id)"
    finalize_state="$(state_field "$finalize_id" state)"
    case "$finalize_state" in
      pending|ready)
        prepare_code_dependency_base "$finalize_id" || die "code dependency baseline unavailable for $finalize_id"
        launch_package "$finalize_id"
        ;;
      finalizing|launched|in_progress)
        log "$finalize_id is already running: $finalize_state"
        ;;
      finalized)
        log "$finalize_id is already finalized"
        ;;
      *)
        die "$finalize_id state is $finalize_state"
        ;;
    esac
    print_agents_command
    return
  fi

  launched=0
  while IFS= read -r id <&3; do
    [ -n "$id" ] || continue
    if [ "$(running_count)" -ge "$MAX_PARALLEL" ]; then
      break
    fi
    launch_package "$id"
    launched=$((launched + 1))
  done 3< <(ready_packages)

  if [ "$launched" -eq 0 ]; then
    active="$(awk -F '\t' 'FNR > 1 && ($2 == "launched" || $2 == "in_progress" || $2 == "finalizing") { print $1 ":" $2 }' "$STATE")"
    if [ -n "$active" ]; then
      printf 'No ready packages to launch. Active packages:\n%s\n' "$active"
    else
      printf 'No ready packages to launch.\n'
    fi
  fi
  print_agents_command
}

print_agents_command() {
  case "$ORCHESTRATION_RUNNER" in
    claude)
      printf '\nView background sessions with:\n'
      printf '  claude agents --cwd "%s"\n' "$REPO_ROOT"
      ;;
    codex)
      printf '\nView Codex runner output with:\n'
      printf '  tail -f "%s/status/launch-<package-id>.log"\n' "$PLAN_ROOT"
      printf 'Recorded codex-thread ids can be resumed with:\n'
      printf '  codex exec resume <thread-id>\n'
      ;;
  esac
}

cmd_status() {
  preflight_all
  printf 'Runner: %s (%s)\n\n' "$ORCHESTRATION_RUNNER" "$ORCHESTRATION_RUNNER_SOURCE"
  printf '%-36s %-12s %-54s %-22s %-14s %-30s %-30s %s\n' "PACKAGE" "STATE" "BRANCH" "VERIFICATION" "INTEGRATION" "LAST_ERROR" "FAILED_COMMAND" "RECOVERY_HINT"
  awk -F '\t' 'FNR > 1 {
    printf "%-36s %-12s %-54s %-22s %-14s %-30s %-30s %s\n", $1, $2, $6, $10, $11, $13, $14, $17
  }' "$STATE"
  if status_consistency_ok; then
    printf '\nCoordinator consistency: ok\n'
  else
    printf '\nCoordinator consistency: invalid\n'
    exit 1
  fi
}

cmd_mark_state() {
  local package_id="${1:-}"
  local new_state="${2:-}"
  local base="__KEEP__" commit="__KEEP__" verification="__KEEP__" integration="__KEEP__" cleanup="__KEEP__" error="__KEEP__"
  local failed_command="__KEEP__" conflict_files="__KEEP__" log_summary="__KEEP__" recovery_hint="__KEEP__"
  local fingerprint event_failed_command event_conflict_files event_log_summary event_recovery_hint old_state
  [ -n "$package_id" ] || die "usage: mark-state <package-id> <state>"
  [ -n "$new_state" ] || die "usage: mark-state <package-id> <state>"
  shift 2 || true
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --base) shift; base="${1:-}" ;;
      --commit) shift; commit="${1:-}" ;;
      --verification) shift; verification="${1:-}" ;;
      --integration) shift; integration="${1:-}" ;;
      --cleanup) shift; cleanup="${1:-}" ;;
      --error) shift; error="${1:-}" ;;
      --failed-command) shift; failed_command="${1:-}" ;;
      --conflict-files) shift; conflict_files="${1:-}" ;;
      --log-summary) shift; log_summary="${1:-}" ;;
      --recovery-hint) shift; recovery_hint="${1:-}" ;;
      *) die "unknown mark-state option: $1" ;;
    esac
    shift || true
  done
  preflight_all
  acquire_lock
  old_state="$(state_field "$package_id" state || true)"
  if [ "$new_state" = "finalized" ] && ! cleanup_complete; then
    die "cannot mark $package_id finalized before cleanup completes"
  fi
  [ "$verification" = "__KEEP__" ] || verification="$(tsv_safe "$verification")"
  [ "$integration" = "__KEEP__" ] || integration="$(tsv_safe "$integration")"
  [ "$cleanup" = "__KEEP__" ] || cleanup="$(tsv_safe "$cleanup")"
  [ "$error" = "__KEEP__" ] || error="$(tsv_safe "$error")"
  [ "$failed_command" = "__KEEP__" ] || failed_command="$(tsv_safe "$failed_command")"
  [ "$conflict_files" = "__KEEP__" ] || conflict_files="$(tsv_safe "$conflict_files")"
  [ "$log_summary" = "__KEEP__" ] || log_summary="$(tsv_safe "$log_summary")"
  [ "$recovery_hint" = "__KEEP__" ] || recovery_hint="$(tsv_safe "$recovery_hint")"
  set_state_fields "$package_id" "$new_state" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "$base" "$commit" "$verification" "$integration" "$cleanup" "$error" "$failed_command" "$conflict_files" "$log_summary" "$recovery_hint"
  if { [ "$new_state" = "blocked" ] || [ "$new_state" = "stale" ] || [ "$new_state" = "invalid" ]; } &&
    [ "$error" != "__KEEP__" ] && [ -n "$error" ]; then
    fingerprint="$(failure_fingerprint "$error")"
    [ "$failed_command" = "__KEEP__" ] && event_failed_command="" || event_failed_command="$failed_command"
    [ "$conflict_files" = "__KEEP__" ] && event_conflict_files="" || event_conflict_files="$conflict_files"
    [ "$log_summary" = "__KEEP__" ] && event_log_summary="" || event_log_summary="$log_summary"
    [ "$recovery_hint" = "__KEEP__" ] && event_recovery_hint="" || event_recovery_hint="$recovery_hint"
    emit_terminal_failure_event "$package_id" "$new_state" "$error" "$fingerprint" "$event_failed_command" "$event_conflict_files" "$event_log_summary" "$event_recovery_hint" "$old_state"
  fi
  log "marked $package_id as $new_state"
}

cmd_repair_state() {
  local tmp id branch worktree md_state
  preflight_graph
  acquire_lock
  tmp="$(mktemp)"
  printf '%s\n' "$STATE_HEADER" > "$tmp"
  while IFS= read -r id; do
    [ -n "$id" ] || continue
    branch="$(graph_field "$id" branch)"
    worktree="$(graph_worktree "$id")"
    md_state="$(markdown_status "$id")"
    valid_state "$md_state" || md_state="pending"
    printf '%s\t%s\t\t\t\t%s\t%s\t\t\tpending\tpending\tpending\t\t\t\t\t\n' "$id" "$md_state" "$branch" "$worktree" >> "$tmp"
  done < <(all_package_ids)
  mv "$tmp" "$STATE"
  # Re-sign after repair
  ensure_signing_secret
  local sig
  sig="$(compute_state_signature)"
  if [ "$sig" != "unsigned" ] && [ -n "$sig" ]; then
    printf '# signature:%s\n' "$sig" >> "$STATE"
  fi
  log "repaired state ledger from graph and markdown status files"
}

cmd_retry() {
  local package_id="$1"
  local state last_error failed_command conflict_files log_summary recovery_hint
  [ -n "$package_id" ] || die "usage: retry <package-id>"
  preflight_all
  graph_field "$package_id" package_doc >/dev/null || die "unknown package: $package_id"
  state="$(state_field "$package_id" state)"
  case "$state" in
    blocked|stale|invalid)
      acquire_lock
      enforce_retry_breaker "$package_id"
      last_error="$(state_field "$package_id" last_error || true)"
      failed_command="$(state_field "$package_id" failed_command || true)"
      conflict_files="$(state_field "$package_id" conflict_files || true)"
      log_summary="$(state_field "$package_id" log_summary || true)"
      recovery_hint="$(state_field "$package_id" recovery_hint || true)"
      log "retrying $package_id from state $state"
      if [ -n "$last_error$failed_command$conflict_files$log_summary$recovery_hint" ]; then
        log "prior failure context:"
        log "  last_error: ${last_error:-none}"
        log "  failed_command: ${failed_command:-none}"
        log "  conflict_files: ${conflict_files:-none}"
        log "  log_summary: ${log_summary:-none}"
        log "  recovery_hint: ${recovery_hint:-none}"
      fi
      emit_event "retry_requested" "$package_id" "$(json_pair "from_state" "$state")$(json_pair "last_error" "$last_error")$(json_pair "failed_command" "$failed_command")$(json_pair "conflict_files" "$conflict_files")$(json_pair "log_summary" "$log_summary")$(json_pair "recovery_hint" "$recovery_hint")"
      set_state_fields "$package_id" "pending" "" "" "" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "pending" "pending" "pending"
      persist_runner
      launch_package "$package_id"
      ;;
    *)
      die "retry only supports blocked, stale, or invalid packages; $package_id is $state"
      ;;
  esac
}

cmd_finalize() {
  preflight_all
  acquire_lock
  persist_runner
  status_consistency_ok || exit 1
  if ! all_functional_completed; then
    die "cannot finalize until all functional packages are completed"
  fi
  prepare_code_dependency_base "$(finalize_package_id)" || die "code dependency baseline unavailable for $(finalize_package_id)"
  launch_package "$(finalize_package_id)"
  print_agents_command
}

cleanup_failure() {
  local message="$1"
  local failed_command="$2"
  local finalize_id
  finalize_id="$(finalize_package_id)"
  set_error_state "$finalize_id" "blocked" "$message" "$failed_command" "" "$message" "Resolve the cleanup blocker, then rerun cleanup --mainline <branch>."
  die "$message"
}

cmd_cleanup() {
  local mainline="" id state branch worktree graph_path physical_worktree physical_repo commit branch_tip finalize_id
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --mainline)
        shift
        mainline="${1:-}"
        ;;
      *)
        die "unknown cleanup option: $1"
        ;;
    esac
    shift || true
  done
  [ -n "$mainline" ] || die "usage: cleanup --mainline <branch>"
  preflight_all
  acquire_lock
  if cleanup_complete; then
    printf 'cleanup: already complete\n'
    return 0
  fi
  git -C "$REPO_ROOT" rev-parse --verify "$mainline^{commit}" >/dev/null 2>&1 ||
    cleanup_failure "mainline branch does not exist: $mainline" "git rev-parse --verify $mainline^{commit}"
  finalize_id="$(finalize_package_id)"
  physical_repo="$(physical_path "$REPO_ROOT")"

  # Validate every recorded resource before removing any of them.
  while IFS= read -r id; do
    [ -n "$id" ] || continue
    state="$(state_field "$id" state)"
    branch="$(state_field "$id" branch)"
    worktree="$(state_worktree "$id")"
    graph_path="$(graph_worktree "$id")"
    commit="$(state_field "$id" commit_hash)"

    if [ "$worktree" != "$graph_path" ]; then
      cleanup_failure "$id worktree differs between graph and state" "compare package-graph.tsv with state.tsv"
    fi
    physical_worktree="$(physical_path "$worktree")"
    case "$physical_worktree" in
      "$physical_repo"/.worktrees/*) ;;
      *)
        cleanup_failure "$id worktree is outside the managed .worktrees directory: $worktree" "validate recorded worktree path"
        ;;
    esac
    if [ -z "$branch" ] || [ "$branch" = "pending" ] || [ "$branch" = "$mainline" ]; then
      cleanup_failure "$id has unsafe recorded branch: $branch" "validate recorded branch"
    fi
    case "$state" in
      completed|finalizing|finalized|blocked) ;;
      *)
        cleanup_failure "$id is not ready for cleanup: $state" "inspect coordinator state"
        ;;
    esac
    if [ -z "$commit" ] || [ "$commit" = "pending" ] ||
      ! git -C "$REPO_ROOT" cat-file -e "$commit^{commit}" >/dev/null 2>&1; then
      cleanup_failure "$id has no valid recorded commit for cleanup" "git cat-file -e $commit^{commit}"
    fi
    if ! git -C "$REPO_ROOT" merge-base --is-ancestor "$commit" "$mainline" >/dev/null 2>&1; then
      cleanup_failure "$id commit is not merged into mainline $mainline" "git merge-base --is-ancestor $commit $mainline"
    fi
    if git -C "$REPO_ROOT" rev-parse --verify "$branch^{commit}" >/dev/null 2>&1; then
      branch_tip="$(git -C "$REPO_ROOT" rev-parse "$branch^{commit}")"
      if ! git -C "$REPO_ROOT" merge-base --is-ancestor "$branch_tip" "$mainline" >/dev/null 2>&1; then
        cleanup_failure "$id branch tip is not merged into mainline $mainline" "git merge-base --is-ancestor $branch_tip $mainline"
      fi
    fi
    if [ -e "$worktree" ]; then
      if ! git -C "$worktree" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        cleanup_failure "$id recorded worktree is not a Git worktree: $worktree" "git -C $worktree rev-parse --is-inside-work-tree"
      fi
      if [ -n "$(git -C "$worktree" status --porcelain)" ]; then
        cleanup_failure "$id worktree is dirty: $worktree" "git -C $worktree status --porcelain"
      fi
    fi
  done < <(all_package_ids)

  while IFS= read -r id; do
    [ -n "$id" ] || continue
    state="$(state_field "$id" state)"
    branch="$(state_field "$id" branch)"
    worktree="$(state_worktree "$id")"
    commit="$(state_field "$id" commit_hash)"
    if [ -e "$worktree" ]; then
      git -C "$REPO_ROOT" worktree remove "$worktree"
      emit_event "cleanup_worktree_removed" "$id" "$(json_pair "worktree" "$worktree")"
    fi
    if git -C "$REPO_ROOT" rev-parse --verify "$branch^{commit}" >/dev/null 2>&1; then
      git -C "$REPO_ROOT" branch -d "$branch"
      emit_event "cleanup_branch_removed" "$id" "$(json_pair "branch" "$branch")"
    fi
    set_state_fields "$id" "$state" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "__KEEP__" "removed"
    emit_event "cleanup_succeeded" "$id" "$(json_pair "branch" "$branch")$(json_pair "worktree" "$worktree")$(json_pair "commit" "$commit")$(json_pair "mainline" "$mainline")"
  done < <(all_package_ids)
  printf 'cleanup: complete\n'
}

template_version_for() {
  local file="$1"
  sed -n 's/^# orchestrate-template v\([^[:space:]]*\).*/\1/p' "$file" 2>/dev/null | head -n 1
}

current_template_path() {
  if [ -n "${ORCHESTRATION_TEMPLATE_PATH:-}" ]; then
    printf '%s\n' "$ORCHESTRATION_TEMPLATE_PATH"
    return 0
  fi
  if [ -f "$REPO_ROOT/skills/agent-orchestration-planner/scripts/orchestrate-template.sh" ]; then
    printf '%s\n' "$REPO_ROOT/skills/agent-orchestration-planner/scripts/orchestrate-template.sh"
    return 0
  fi
  if [ -n "${HOME:-}" ] && [ -f "$HOME/.codex/skills/agent-orchestration-planner/scripts/orchestrate-template.sh" ]; then
    printf '%s\n' "$HOME/.codex/skills/agent-orchestration-planner/scripts/orchestrate-template.sh"
    return 0
  fi
  return 1
}

version_lt() {
  local left="$1"
  local right="$2"
  awk -v left="$left" -v right="$right" '
    BEGIN {
      n = split(left, l, /[.-]/)
      m = split(right, r, /[.-]/)
      max = n > m ? n : m
      for (i = 1; i <= max; i++) {
        a = (i in l && l[i] ~ /^[0-9]+$/) ? l[i] + 0 : 0
        b = (i in r && r[i] ~ /^[0-9]+$/) ? r[i] + 0 : 0
        if (a < b) exit 0
        if (a > b) exit 1
      }
      exit 1
    }
  '
}

cmd_doctor() {
  if [ "${1:-}" = "--environment" ]; then
    local generated_template_version current_template_path current_template_version template_status
    generated_template_version="$(template_version_for "$0")"
    current_template_path="$(current_template_path || true)"
    current_template_version="unknown"
    template_status="unknown"
    if [ -n "$current_template_path" ] && [ -f "$current_template_path" ]; then
      current_template_version="$(template_version_for "$current_template_path")"
      if [ -n "$generated_template_version" ] && [ -n "$current_template_version" ]; then
        if [ "$generated_template_version" = "$current_template_version" ]; then
          template_status="ok"
        elif version_lt "$generated_template_version" "$current_template_version"; then
          template_status="generated-older"
        elif version_lt "$current_template_version" "$generated_template_version"; then
          template_status="generated-newer"
        else
          template_status="mismatch"
        fi
      fi
    fi
    printf 'repo_root=%s\n' "$REPO_ROOT"
    printf 'plan_root=%s\n' "$PLAN_ROOT"
    printf 'runner=%s\n' "$ORCHESTRATION_RUNNER"
    printf 'runner_source=%s\n' "$ORCHESTRATION_RUNNER_SOURCE"
    printf 'runner_state=%s\n' "$RUNNER_STATE"
    case "$ORCHESTRATION_RUNNER" in
      claude)
        if command -v claude >/dev/null 2>&1; then
          printf 'claude_path=%s\n' "$(command -v claude)"
          printf 'claude_version=%s\n' "$(claude --version 2>&1 || true)"
          if claude agents --help >/dev/null 2>&1; then
            printf 'claude_agents_help=available\n'
          else
            printf 'claude_agents_help=unavailable\n'
          fi
        else
          printf 'claude_path=missing\n'
          printf 'claude_version=missing\n'
          printf 'claude_agents_help=unavailable\n'
        fi
        ;;
      codex)
        if command -v codex >/dev/null 2>&1; then
          printf 'codex_path=%s\n' "$(command -v codex)"
          printf 'codex_version=%s\n' "$(codex --version 2>&1 || true)"
          if codex_exec_supports_approval_policy; then
            printf 'codex_exec_approval_policy_flag=available\n'
          else
            printf 'codex_exec_approval_policy_flag=unavailable\n'
          fi
        else
          printf 'codex_path=missing\n'
          printf 'codex_version=missing\n'
          printf 'codex_exec_approval_policy_flag=unavailable\n'
        fi
        printf 'codex_sandbox=%s\n' "$ORCHESTRATION_CODEX_SANDBOX"
        printf 'codex_approval_policy=%s\n' "$ORCHESTRATION_CODEX_APPROVAL_POLICY"
        printf 'codex_home=%s\n' "$(codex_home_path)"
        if codex_home_is_writable; then
          printf 'codex_home_writable=yes\n'
        else
          printf 'codex_home_writable=no\n'
        fi
        ;;
      *)
        printf 'runner_error=unsupported:%s\n' "$ORCHESTRATION_RUNNER"
        ;;
    esac
    printf 'permission_mode=%s\n' "${CLAUDE_PERMISSION_MODE:-default}"
    printf 'setting_sources=%s\n' "$CLAUDE_SETTING_SOURCES"
    printf 'template_generated_version=%s\n' "${generated_template_version:-unknown}"
    printf 'template_current_path=%s\n' "${current_template_path:-missing}"
    printf 'template_current_version=%s\n' "${current_template_version:-unknown}"
    printf 'template_version_status=%s\n' "$template_status"
    if [ "$template_status" = "generated-older" ]; then
      printf 'template_version_warning=generated script is older than current template\n'
    fi
    return 0
  fi
  local reconciled
  preflight_all
  status_consistency_ok
  if [ "$ORCHESTRATION_RUNNER" = "codex" ]; then
    reconciled="$(reconcile_active_codex)"
    if [ "$reconciled" -gt 0 ]; then
      printf 'doctor: reconciled %s stale Codex process(es)\n' "$reconciled"
      return 1
    fi
    printf 'doctor: ok\n'
    return 0
  fi
  acquire_lock
  reconciled="$(reconcile_active_agents)"
  status_consistency_ok
  if [ "$reconciled" -gt 0 ]; then
    printf 'doctor: reconciled %s stale agent session(s)\n' "$reconciled"
    return 1
  fi
  printf 'doctor: ok\n'
}

cmd_collect_logs() {
  local package_id="${1:-}"
  local state session_id logs_path
  [ -n "$package_id" ] || die "usage: collect-logs <package-id>"
  preflight_all
  graph_field "$package_id" package_doc >/dev/null || die "unknown package: $package_id"
  state="$(state_field "$package_id" state)"
  session_id="$(state_field "$package_id" agent || true)"
  if logs_path="$(collect_agent_logs "$package_id" "$session_id" "manual")"; then
    printf 'logs: %s\n' "$logs_path"
    return 0
  fi
  case "$state" in
    launched|in_progress|finalizing)
      set_error_state "$package_id" "stale" "claude session ${session_id:-pending} logs are not readable; see ${logs_path:-$LOGS_DIR/$package_id.log}" "claude logs ${session_id:-pending}" "" "Claude logs snapshot saved to ${logs_path:-$LOGS_DIR/$package_id.log}" "Open claude agents/logs manually, then mark completed or retry."
      ;;
  esac
  die "logs unavailable for $package_id"
}

cmd_scratch_path() {
  local package_id="${1:-}"
  local path
  [ -n "$package_id" ] || die "usage: scratch-path <package-id>"
  preflight_graph
  graph_field "$package_id" package_doc >/dev/null || die "unknown package: $package_id"
  ensure_scratch_root
  path="$(scratch_path_for "$package_id")"
  mkdir -p "$path"
  emit_event "scratch_path_requested" "$package_id" "$(json_pair "path" "$path")"
  printf '%s\n' "$path"
}

verify_package_evidence() {
  local package_id="$1"
  local state branch worktree commit deps dep dep_commit bad=0
  state="$(state_field "$package_id" state)"
  branch="$(state_field "$package_id" branch)"
  worktree="$(state_worktree "$package_id")"
  commit="$(state_field "$package_id" commit_hash)"

  if [ "$state" != "completed" ] && [ "$state" != "finalized" ]; then
    printf '%s not completed: %s\n' "$package_id" "$state" >&2
    bad=1
  fi
  if [ -z "$commit" ] || [ "$commit" = "pending" ]; then
    printf '%s missing commit_hash\n' "$package_id" >&2
    bad=1
  elif ! git -C "$REPO_ROOT" cat-file -e "$commit^{commit}" >/dev/null 2>&1; then
    printf '%s commit_hash does not exist: %s\n' "$package_id" "$commit" >&2
    bad=1
  fi
  if [ -z "$branch" ] || [ "$branch" = "pending" ]; then
    printf '%s missing branch\n' "$package_id" >&2
    bad=1
  elif ! git -C "$REPO_ROOT" rev-parse --verify "$branch" >/dev/null 2>&1; then
    printf '%s branch does not exist: %s\n' "$package_id" "$branch" >&2
    bad=1
  fi
  if [ -n "$worktree" ] && [ "$worktree" != "pending" ] &&
    git -C "$worktree" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if [ -n "$(git -C "$worktree" status --porcelain)" ]; then
      printf '%s worktree is dirty: %s\n' "$package_id" "$worktree" >&2
      bad=1
    fi
  fi
  if package_has_code_dependencies "$package_id"; then
    deps="$(graph_field "$package_id" dependencies || true)"
    IFS=',' read -r -a dep_array <<< "$deps"
    for dep in "${dep_array[@]}"; do
      dep="$(trim_dep "$dep")"
      [ -z "$dep" ] && continue
      dep_commit="$(state_field "$dep" commit_hash || true)"
      if [ -z "$dep_commit" ] || [ "$dep_commit" = "pending" ]; then
        printf '%s code dependency %s missing commit_hash\n' "$package_id" "$dep" >&2
        bad=1
        continue
      fi
      if ! git -C "$REPO_ROOT" cat-file -e "$dep_commit^{commit}" >/dev/null 2>&1; then
        printf '%s code dependency %s commit_hash does not exist: %s\n' "$package_id" "$dep" "$dep_commit" >&2
        bad=1
        continue
      fi
      if [ -n "$commit" ] && [ "$commit" != "pending" ] &&
        git -C "$REPO_ROOT" cat-file -e "$commit^{commit}" >/dev/null 2>&1 &&
        ! git -C "$REPO_ROOT" merge-base --is-ancestor "$dep_commit" "$commit" >/dev/null 2>&1; then
        printf '%s does not contain code dependency %s (%s is not an ancestor of %s)\n' "$package_id" "$dep" "$dep_commit" "$commit" >&2
        bad=1
      fi
    done
  fi
  return "$bad"
}

cmd_verify_package() {
  local package_id="${1:-}"
  [ -n "$package_id" ] || die "usage: verify-package <package-id>"
  preflight_all
  status_consistency_ok
  verify_package_evidence "$package_id"
}

cmd_verify_finalize() {
  local id bad=0
  preflight_all
  status_consistency_ok
  while IFS= read -r id; do
    [ -n "$id" ] || continue
    if ! verify_package_evidence "$id"; then
      bad=1
    fi
  done < <(functional_package_ids)
  [ "$bad" -eq 0 ] || exit 1
  printf 'verify-finalize: ok\n'
}

usage() {
  cat <<USAGE
Usage: bash launchers/orchestrate.sh <command>

Commands:
  start
  advance [--from <package-id>]
  status
  retry <package-id>
  finalize
  cleanup --mainline <branch>
  mark-state <package-id> <state> [--base <sha>] [--commit <sha>] [--verification <text>] [--integration <text>] [--cleanup <text>] [--error <text>] [--failed-command <text>] [--conflict-files <text>] [--log-summary <text>] [--recovery-hint <text>]
  repair-state
  doctor [--environment]
  collect-logs <package-id>
  verify-package <package-id>
  verify-finalize
  scratch-path <package-id>
USAGE
}

case "${1:-}" in
  start)
    acquire_lock
    persist_runner
    launch_ready_or_finalize
    ;;
  advance)
    shift || true
    if [ "${1:-}" = "--from" ]; then
      log "advance requested from ${2:-unknown}"
    fi
    acquire_lock
    persist_runner
    launch_ready_or_finalize
    ;;
  status)
    cmd_status
    ;;
  retry)
    shift || true
    cmd_retry "${1:-}"
    ;;
  finalize)
    cmd_finalize
    ;;
  cleanup)
    shift || true
    cmd_cleanup "$@"
    ;;
  mark-state)
    shift || true
    cmd_mark_state "$@"
    ;;
  repair-state)
    cmd_repair_state
    ;;
  doctor)
    shift || true
    cmd_doctor "$@"
    ;;
  collect-logs)
    shift || true
    cmd_collect_logs "${1:-}"
    ;;
  verify-package)
    shift || true
    cmd_verify_package "${1:-}"
    ;;
  verify-finalize)
    cmd_verify_finalize
    ;;
  scratch-path)
    shift || true
    cmd_scratch_path "${1:-}"
    ;;
  *)
    usage
    exit 1
    ;;
esac
