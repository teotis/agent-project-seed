# Runtime Contract

This reference owns the machine-readable orchestration runtime: generated
directory shape, `package-graph.tsv`, `state.tsv`, `orchestrate.sh`, runner
variation, and dependency unlock semantics.

## Codex Status Semantic Mapping

Do not add a separate Codex-specific state column. Map Codex/runtime statuses
onto the existing package lifecycle:

| Runtime observation | Orchestration treatment |
|---|---|
| `pending_init` | Keep package `launched` until a real run starts or doctor marks it stale. |
| `running` | Keep package `launched` or `in_progress`; it cannot unlock dependencies. |
| `interrupted` | Treat as retryable `stale` unless package evidence proves a deliberate blocker. |
| `completed` | May become package `completed` only after the package writes evidence and calls `mark-state completed`. Completion is not merge/finalize success. |
| `errored` | Treat as `blocked` or `invalid` with failure context and retry fingerprint. |
| `not_found` | Treat as `invalid` for missing launch/session identity, or `stale` when a previously launched agent can no longer be inspected. |
| `shutdown` | Resource lifecycle only; it is not package success by itself. |

`launched`, `in_progress`, and `finalizing` are active states. They must never
unlock downstream packages, start `99-finalize`, or satisfy acceptance criteria.
Only `completed` and `finalized` can satisfy dependency checks.

### 2. Generate Orchestration Kit

Create this structure under the plan directory:

```text
docs/plans/<plan-name>/
├── INDEX.md
├── packages/
│   ├── 01-<name>.md
│   ├── 02-<name>.md
│   └── 99-finalize.md
├── launchers/
│   ├── agent-prompts.md
│   ├── package-graph.tsv
│   ├── orchestrate.sh
│   ├── start-codex-app.sh
│   └── start-claude-code.sh
├── status/
│   ├── README.md
│   ├── state.tsv
│   ├── events.jsonl
│   ├── package-status-template.md
│   ├── <package-id>.md
│   └── 99-finalize.md
├── scratch/
│   └── .gitignore
└── FINAL_REPORT.md (created by 99-finalize)
```

`status/package-status-template.md` must be generated as a concrete template file using the
format defined in `artifact_templates.md` section 5. The `## State` value must be
backtick-wrapped (e.g. `` `pending` ``); the coordinator script's `markdown_status()`
only parses backtick-wrapped state lines, and bare values resolve to `unknown`.

`dispatch-claude-agents.sh` is no longer a primary generated entrypoint. If backward compatibility is useful, generate it only as a thin wrapper that calls `orchestrate.sh start`. Any wrapper must compute `REPO_ROOT` with `git rev-parse --show-toplevel`, not hardcoded relative paths.

`launchers/orchestrate.sh` must be copied from `scripts/orchestrate-template.sh` (resolved relative to this SKILL.md file), then syntax-checked with `bash -n`. Do not recreate this script from memory or prose. The template is the tested runtime contract for launch handshakes, state mutation, repair, and retry behavior.

`launchers/start-codex-app.sh` must be copied from `scripts/start-codex-app-template.sh`; `launchers/start-claude-code.sh` must be copied from `scripts/start-claude-code-template.sh`. Both wrappers must be syntax-checked with `bash -n`. They are platform entrypoints, not independent schedulers.

### 5. launchers/package-graph.tsv

Generate a machine-readable graph with a header:

```tsv
package_id	package_doc	status_file	dependencies	dependency_type	wave	branch	worktree	manual	finalize
01-xxx	packages/01-xxx.md	status/01-xxx.md		status	1	agent/<plan>/01-xxx	<worktree-path>	0	0
02-xxx	packages/02-xxx.md	status/02-xxx.md		status	1	agent/<plan>/02-xxx	<worktree-path>	0	0
03-xxx	packages/03-xxx.md	status/03-xxx.md	01-xxx,02-xxx	code	2	agent/<plan>/03-xxx	<worktree-path>	0	0
99-finalize	packages/99-finalize.md	status/99-finalize.md	01-xxx,02-xxx,03-xxx	status+code	final	agent/<plan>/99-finalize	<worktree-path>	0	1
```

Rules:
- Package IDs must be unique.
- Dependencies must reference existing package IDs.
- The graph must be acyclic.
- Functional packages are all rows where `finalize != 1`.
- `99-finalize` must be present exactly once.
- `worktree` must be an absolute path under the repository root, such as `<repo-root>/.worktrees/<plan>/<package-id>`, so the launcher works from any current directory.

### 6. status/state.tsv

Generate a machine-readable state ledger with a header:

```tsv
package_id	state	launched_at	completed_at	agent	branch	worktree	base_commit	commit_hash	verification	integration	cleanup	last_error	failed_command	conflict_files	log_summary	recovery_hint
01-xxx	pending	pending	pending	pending	agent/<plan>/01-xxx	<worktree-path>	pending	pending	pending	pending	pending	pending	pending	pending	pending	pending
```

Allowed states:
- `pending`
- `ready`
- `manual_required`
- `launched`
- `in_progress`
- `completed`
- `blocked`
- `stale`
- `invalid`
- `finalizing`
- `finalized`

Markdown status is for humans. `state.tsv` is the scheduler source of truth. If Markdown status and `state.tsv` disagree, `orchestrate.sh status` reports `invalid` and does not unlock downstream packages.

The `worktree` column mirrors `package-graph.tsv` and should be recorded as an absolute repo-root path, so retry and finalize verification never depend on the shell's current directory.

Failure recovery context is part of the scheduler ledger, not an informal chat note. For merge conflicts, failed tests, launch failures, or verification failures, write:
- `last_error`: concise failure statement.
- `failed_command`: exact command or operation that failed, such as `git merge agent/...` or `./gradlew test`.
- `conflict_files`: comma-separated conflicted or suspect files, or empty when none.
- `log_summary`: short summary of the decisive log lines; keep raw logs in `status/` or scratch when needed.
- `recovery_hint`: the next action a downstream retry or repair agent should try first.

Do not blindly retry a blocked package. A retry must preserve the prior recovery context long enough for the relaunched package agent to inspect it, and repeated identical fingerprints must trip the retry breaker.

Projection rule for `state.tsv`: keep it a compact current scheduler snapshot. The five recovery context columns (`last_error`, `failed_command`, `conflict_files`, `log_summary`, `recovery_hint`) are short scheduler-facing summaries, not the full incident record. Put long retry history, repeated failure accounting, raw logs, QA screenshots, release tickets, manual review notes, and narrative risk analysis in `events.jsonl`, package status Markdown, `FINAL_REPORT.md`, or the external evidence channel named in INDEX. Do not add a new `state.tsv` column unless the scheduler needs it to compute readiness, blocking, verification, integration, or cleanup.

### 7. launchers/orchestrate.sh

Generate one script with these subcommands:

```bash
bash launchers/orchestrate.sh start
bash launchers/orchestrate.sh advance [--from <package-id>]
bash launchers/orchestrate.sh status
bash launchers/orchestrate.sh retry <package-id>
bash launchers/orchestrate.sh finalize
bash launchers/orchestrate.sh cleanup --mainline <branch>
bash launchers/orchestrate.sh mark-state <package-id> <state> [--base <sha>] [--commit <sha>] [--verification <text>] [--integration <text>] [--cleanup <text>] [--error <text>] [--failed-command <text>] [--conflict-files <text>] [--log-summary <text>] [--recovery-hint <text>]
bash launchers/orchestrate.sh repair-state
bash launchers/orchestrate.sh doctor [--environment]
bash launchers/orchestrate.sh collect-logs <package-id>
bash launchers/orchestrate.sh verify-package <package-id>
bash launchers/orchestrate.sh verify-finalize
bash launchers/orchestrate.sh scratch-path <package-id>
```

Required behavior:
- `start`: preflight the graph, acquire lock, launch all currently ready functional packages up to `ORCHESTRATION_MAX_PARALLEL`, then exit.
- `advance`: acquire lock, re-read graph/status/state, validate dependencies, stop on blocked/stale/invalid, launch newly ready functional packages, or launch `99-finalize` when all functional packages are completed.
- `status`: print a concise table of package state, branch, worktree, verification, integration, last error, failed command, and recovery hint.
- `retry <package-id>`: only reset `blocked`, `stale`, or `invalid` packages after reporting prior recovery context. It must not retry already launched or completed packages unless the user explicitly changes state. If the same package hits the same terminal failure fingerprint three times, block further retry and require human diagnosis.
- `finalize`: run or re-run the `99-finalize` package idempotently.
- `cleanup --mainline <branch>`: after successful finalize verification, remove only graph/state-recorded local worktrees and branches whose recorded commits and branch tips are merged into the named mainline. It must validate all resources before deleting any resource, block dirty worktrees or unmerged commits, delete worktrees before branches, use non-force `git branch -d`, record cleanup events/results, and be idempotent.
- `mark-state`: the only supported way for package agents to mutate `state.tsv`; it also keeps Markdown status in sync.
- `repair-state`: rebuild `state.tsv` from graph and Markdown status when a ledger is empty or malformed.
- `doctor`: run preflight and consistency checks without launching work, then reconcile active runner sessions/processes. For Claude, check recorded session ids and collect logs. For Codex, check recorded `codex exec` process ids and JSONL launch logs. If an active session/process is unreadable, missing, or exited without package evidence, mark the package `stale` or `invalid`, write recovery context, and record `agent_lost`.
- `doctor --environment`: report repo root, plan root, selected runner, runner-specific CLI path/version/capabilities, permission mode, setting sources, and generated template version vs current template version. Warn if the generated script is older than the current template.
- `collect-logs <package-id>`: persist a `claude logs <session-id>` snapshot to `status/logs/<package-id>.log` and record `agent_logs_collected` or `agent_logs_unreadable` in `events.jsonl`. If an active package's logs are unreadable, mark it `stale`.
- `verify-package` / `verify-finalize`: verify package evidence before integration, including completed state, branch, commit hash, commit existence, clean package worktree when present, and `dependency_type=code/status+code` ancestry. For every code dependency, `git merge-base --is-ancestor <dependency_commit> <package_commit>` must pass.
- `scratch-path <package-id>`: create `scratch/.gitignore`, create the package-local scratch directory, print its absolute path, and record the request in `events.jsonl`.

Projection consistency behavior:
- If `INDEX.md` and `package-graph.tsv` disagree about dependency intent, report the mismatch for human review. Do not silently choose the more permissive graph.
- If Markdown package status and `state.tsv` disagree, block downstream dispatch until `mark-state`, `repair-state`, or an explicit package-status correction restores consistency.
- If `events.jsonl` shows terminal failures or retry blocks that conflict with a package's optimistic status, require 99-finalize or a human repair step to reconcile the evidence before merge.
- If scratch contains useful evidence, summarize it into the package status file and appropriate state/event fields; scratch itself remains non-authoritative.

Implementation rules:
- Use `scripts/orchestrate-template.sh` (resolved relative to this SKILL.md file) as the script body. Preserve the version comment (`# orchestrate-template vX.Y.Z`) in the generated script so `doctor --environment` can compare against the current template.
- Compute `REPO_ROOT` dynamically with `git rev-parse --show-toplevel` from the script's directory. Never use hardcoded relative path traversal like `../../..` — the plan directory depth from repo root varies per project.
- When awk processes the same TSV file twice (e.g. `awk '...' "$GRAPH" "$GRAPH"`), use `FNR == 1` to skip each file's header, not `NR == 1` which only skips the first file's header.
- Use a lock such as `status/.orchestrate.lock` so concurrent `advance` calls cannot double-launch packages.
- Never trust `--from`; it is only a hint for logging. Always compute readiness from coordinator status/state.
- Every package can be launched at most once unless `retry` explicitly resets it.
- Launch Claude Code background agents with `claude --bg --name` from the package's assigned worktree.
- Read the scheduler's ready-package stream through a dedicated file descriptor, never through the dispatch loop's stdin. Runner launch, log postflight, and health-check subprocesses may read stdin; they must not be able to consume remaining same-wave package IDs. Feed each Claude prompt from its own prompt file.
- Parse Claude Code session ids from observed output formats such as `backgrounded <id>` and `backgrounded · <id>`, including ANSI-colored CLI output. Never record punctuation such as `·` or color escape sequences as the session id.
- Do not silently grant elevated permission modes. Default to no explicit `--permission-mode`; `CLAUDE_PERMISSION_MODE=auto` requires `CLAUDE_AUTO_MODE_OPTED_IN=1` after an interactive opt-in, and `CLAUDE_PERMISSION_MODE=bypassPermissions` requires `CLAUDE_BYPASS_PERMISSIONS_APPROVED=1`.
- Before launch, create or verify the recorded package worktree and branch.
- Before launching a package with `dependency_type=code` or `status+code`, first require every upstream dependency to be `completed`/`finalized` with an existing `commit_hash`, merge those upstream commits into the orchestration integration branch, and create the downstream package worktree from that integration branch. The default integration branch is `agent/<plan-name>/integration`, overridable by `ORCHESTRATION_INTEGRATION_BRANCH`; the default integration worktree is `<repo-root>/.worktrees/<plan-name>/00-integration`, overridable by `ORCHESTRATION_INTEGRATION_WORKTREE`.
- If the integration merge for a code dependency conflicts, mark the downstream package `blocked` with recovery context and do not launch it. If the upstream commit is missing or invalid, mark the downstream package `invalid`.
- When a package worktree is created or reused, record the real `git rev-parse HEAD` in `state.tsv` `base_commit`. Do not leave generation-time placeholder bases in the ledger after launch.
- If an existing downstream worktree does not contain the required code dependency commits, mark the package `invalid`; do not launch on a stale baseline.
- If a graph row has `manual=1`, never auto-launch it. When its dependencies are satisfied, mark it `manual_required` and print the package id for manual execution.
- Capability preflight is mandatory before graph creation. Auto-launched packages may contain only `autonomous` or `agent-verifiable substitute` work. `external-assist` checks must be predeclared in the INDEX and kept out of autonomous package execution unless the active environment truly provides that capability. A blocking `external-assist` gate may be generated only after the user has approved that gate, owner, expected evidence, and blocking scope; otherwise planning must stop before artifact generation and ask for a decision.
- Treat runner differences as capability variation over the same lifecycle. Manual execution, Claude background sessions, CI runners, and other agent platforms may differ in launch mechanism, permission mode, evidence channel, and verification ability, but they must not introduce separate package states, duplicate finalize logic, or package-local scheduling.
- Runner selection policy for generated user guidance: follow explicit user/platform intent. If the user requests Codex App, Codex runner, or the active host is Codex App and Claude is not requested, show `launchers/start-codex-app.sh` as the primary script lane. If the user requests Claude Code, Agents View, or `claude --bg`, show `launchers/start-claude-code.sh` as the primary script lane. If the host/runner is unknown, keep Claude as the compatibility fallback and name Codex as an alternative only when relevant. Do not infer runner choice from whichever CLI happens to be installed.
- Persist the selected runner as coordinator runtime configuration in `status/runner`. Resolution order is explicit `ORCHESTRATION_RUNNER`, then persisted runner, then default `claude` for backward compatibility. `start`, `advance`, `retry`, and `finalize` must preserve/update this selection before launch. Package tail calls intentionally remain plain `bash ... advance --from ...`; they must not depend on tool subprocesses inheriting `ORCHESTRATION_RUNNER`.
- Runner wrappers: `start-codex-app.sh` and `start-claude-code.sh` must set `ORCHESTRATION_RUNNER=codex` or `ORCHESTRATION_RUNNER=claude` on every call into `orchestrate.sh`. Their default `start` command must run `doctor --environment`, `start`, and `status` in that order. Other supported orchestrator subcommands are pass-through helpers. Wrappers must not mutate `state.tsv` directly, compute readiness, launch packages themselves, or implement finalize/cleanup logic.
- Codex runner specifics: use `codex exec --json` with `ORCHESTRATION_CODEX_SANDBOX` (default `workspace-write`) and `ORCHESTRATION_CODEX_APPROVAL_POLICY` (default `never`). Pass `--ask-for-approval` only when `codex exec --help` advertises that flag; if the installed CLI lacks the flag, omit it for the default `never` policy and fail preflight for any non-default approval policy. Optional `ORCHESTRATION_CODEX_MODEL` maps to `--model`; optional `ORCHESTRATION_CODEX_EFFORT` maps to `model_reasoning_effort`. In non-interactive Codex flows, actions that require fresh approval can fail, so package prompts must keep the same explicit `mark-state` and `advance` tail call contract.
- Codex runner environment preflight is mandatory before `start`: `doctor --environment` must print the Codex CLI version, whether `codex exec` supports approval policy flags, the selected sandbox/approval policy, `CODEX_HOME` or `~/.codex`, and whether that home is writable from the launch shell. If launch stderr reports a readonly Codex state DB, PATH update permission failure, or app-server initialization failure, classify it as a runner environment failure (`invalid`/`stale`) with recovery guidance to rerun from a user shell with writable Codex state or an explicitly approved runner environment; do not treat it as package implementation failure.
- Codex launch postflight must distinguish "thread id emitted" from "agent alive enough to work." If a launch log contains only `thread.started`/`turn.started` and no active `codex exec` process remains, mark the package `stale` with the stalled-thread fingerprint and require retry or manual diagnosis instead of letting a hollow `launched` state unlock confidence.
- Maintain `status/events.jsonl` as an append-only audit log. Record at minimum: `launch_requested`, `launch_succeeded`, `state_changed`, `terminal_failure`, `retry_requested`, `retry_blocked`, `agent_logs_collected`, `agent_logs_unreadable`, `agent_health_checked`, `agent_lost`, `cleanup_worktree_removed`, `cleanup_branch_removed`, `cleanup_succeeded`, and `scratch_path_requested` with timestamp, package id, state transition or session id, path, and error fingerprint where relevant.
- On terminal package failures (`blocked`, `stale`, or `invalid` with `--error`), record recovery context in both `state.tsv` and `events.jsonl`: error, failed command, conflict files, log summary, and recovery hint. Sanitize tabs/newlines before writing TSV.
- Do not double-count repeated terminal failure writes for a package that is already in the same terminal state with the same normalized error fingerprint. Record a duplicate observation separately if useful, but retry breaker accounting must count distinct terminal failure transitions, not repeated ledger writes.
- Treat `events.jsonl` as the source for retry loop accounting. If `terminal_failure` records show the same package and normalized error fingerprint three times, `retry` must stop before relaunching and print the package id, failure count, and fingerprint.
- **Fingerprint normalization**: Before comparing retry fingerprints, strip variable noise from the error string: timestamps, ISO dates, hex session IDs (8+ hex chars), absolute paths to the repo root or worktree, line numbers (`:\d+`), and ephemeral port numbers. Normalize whitespace to single spaces and trim. Compare the normalized strings case-insensitively.
- Maintain `scratch/` as a plan-local, gitignored, non-authoritative exchange area. Runtime commands must create `scratch/.gitignore` with ignored contents, and package prompts must direct agents to request their package path through `scratch-path`. Scratch contents must never unlock dependencies, satisfy acceptance criteria by themselves, or replace status/evidence fields.
- Treat `## Package: <package-id> - <title>` headings in `agent-prompts.md` as machine-readable parser keys. Shared preflight must verify that every graph package has exactly one canonical heading and reject missing, duplicate, unknown, or malformed headings before creating worktrees, launching runners, or mutating package state.
- Write raw launch output to `status/launch-<package-id>.log`.
- Persist Claude session log snapshots under `status/logs/<package-id>.log`. Launch postflight, `doctor`, and `collect-logs` should use this path so finalize and retry agents can inspect real session output instead of relying only on package self-reports.
- Parse and record the background session id in the `agent` column.
- After launch, run a short `claude logs <session-id>` postflight and save the snapshot. If the session id is missing, mark the package `invalid`. If logs are not readable or the session exits immediately, mark it `stale`.
- Never unlock downstream packages from `launched`, `in_progress`, or `finalizing`; downstream unlock requires `completed` or `finalized`.
- `mark-state 99-finalize finalized` must be rejected until every graph/state row has `cleanup=removed`. A `--cleanup deferred` note is not a successful terminal state.
- `state.tsv` integrity is protected by HMAC-SHA-256 signing. Every `mark-state` invocation appends a `# signature:<hex>` line computed from `status/.state.sig` secret key + state.tsv content. Any direct edit to `state.tsv` outside of `mark-state` invalidates the signature.
- `preflight_state_signature` validates the signature on every `advance`, `retry`, `finalize`, `mark-state`, `doctor`, and `status` call; failed validation blocks all orchestrate commands with "state.tsv integrity check failed; use repair-state to reinitialize".
- `repair-state` strips the old signature, rewrites state.tsv from graph + markdown status, and re-signs with a fresh secret.
- `validate_events_cleanup` cross-checks: when `99-finalize` is `finalized`, `events.jsonl` must contain at least one `cleanup_succeeded` event and no row may have `cleanup` field set to a non-`removed` value (including empty string); violation blocks `preflight_all`.
- Default `ORCHESTRATION_MAX_PARALLEL=10`.
- Print runner-appropriate inspection instructions after launching agents: `claude agents` for Claude, package JSONL logs and recorded thread ids for Codex. Resume Codex sessions with `codex exec resume <thread-id>` after stripping any coordinator prefix such as `codex-thread:`.
- Do not run as a permanent watcher. Tail calls and manual `advance` drive progression.
