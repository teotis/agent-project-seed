# Artifact Templates

This reference owns long generated Markdown templates and final user output
shape. Read it when producing `INDEX.md`, `agent-prompts.md`, `99-finalize.md`,
or the final chat instructions after creating an orchestration kit.

### 3. INDEX.md Required Sections

`INDEX.md` is the static execution contract. Dynamic status belongs in `status/`.

```markdown
# <Plan Title> - Orchestration Index

## Goal
<combined outcome>

## Projection Ownership
- `INDEX.md` owns static human intent, policy, authorization, landing strategy, capability gates, and the intended dependency contract.
- `launchers/package-graph.tsv` owns machine-readable dispatch topology. It must match the dependency intent in this INDEX.
- `status/state.tsv` owns current scheduler state. It must not be edited manually.
- `status/events.jsonl` owns append-only event history, retry accounting, and failure fingerprints.
- `status/<package-id>.md` owns human-readable evidence, risks, verification details, and blocker diagnosis.
- `scratch/` is temporary and non-authoritative; it cannot unlock dependencies or satisfy acceptance criteria by itself.
- If these projections disagree, treat the orchestration as invalid or blocked until repaired; do not infer success from one artifact alone.

## Execution Contract Proof Route
- Need proof: <why native agents, direct execution, Task Package Contract, ledger-lite, or manual-pack are insufficient>
- Projection proof: <which artifact owns each information type and how drift is detected>
- Unlock proof: <why dependency unlock requires scheduler truth and only completed/finalized unlocks>
- Capability proof: <autonomous / substitute / external-assist classification summary>
- Landing proof: <how task-level outcomes and fallback paths are decided>
- Cleanup proof: <evidence required before cleanup and protected resources>
- Falsifier / downgrade trigger: <what would block or downgrade this kit>

## Orchestration Value Score
- Durable state need:
- Dependency unlock value:
- Recovery value:
- Integration value:
- Runner value:
- Operator burden:
- Decision: <full kit | ledger-lite/manual-pack | native agents | needs-user-decision>

## User Entry Points
- Manual: copy prompts from `launchers/agent-prompts.md` into any agent platform.
- Script: use the selected runner wrapper for this plan. Codex App / Codex runner plans use `bash launchers/start-codex-app.sh` and JSONL/thread-id inspection. Claude Code plans use `bash launchers/start-claude-code.sh` and `claude agents`.
- Status: run `bash launchers/orchestrate.sh status`.
- Retry: run `bash launchers/orchestrate.sh retry <package-id>`.
- Manual advancement fallback: run `bash launchers/orchestrate.sh advance`.
- App-native fallback: if the user wants to stay inside Codex App subagents instead of a script runner, copy ready package prompts into a Codex subagent workflow and manually run `advance` when a platform cannot run shell tail calls.
- Cross-runner launch: both `start-codex-app.sh` and `start-claude-code.sh` are generated. A kit planned in one app may be launched from the other by running the other wrapper.

## Repository And Branch Policy
- Main checkout: <absolute path>
- Coordinator plan root: <absolute path to docs/plans/<name>>
- Mainline branch: <branch>
- Integration branch: <branch created/updated by 99-finalize>
- Functional package branches: `agent/<plan>/<package-id>`
- Implementation isolation: one worktree per functional package unless explicitly excepted.
- Coordinator status/state files are not implementation artifacts and must not be committed on package branches unless explicitly requested.

## Authorization
Package agents are authorized to:
- Create or reuse only their assigned worktree and branch.
- Edit only allowed paths.
- Run listed verification commands.
- Commit local package changes.
- Write only their assigned coordinator status file.
- Update the state ledger only through `bash <plan-root>/launchers/orchestrate.sh mark-state ...`; do not edit `state.tsv` manually.
- Write temporary, non-sensitive shared working notes or intermediate artifacts only under their assigned scratch path from `bash <plan-root>/launchers/orchestrate.sh scratch-path <package-id>`.
- Call `bash <plan-root>/launchers/orchestrate.sh advance --from <package-id>` after recording final status.
- The launcher persists the selected runner in `status/runner`, so this plain tail call must continue with the runner chosen by `start-codex-app.sh`, `start-claude-code.sh`, or the initial `start`; do not rely on environment inheritance.

`99-finalize` is authorized by default to perform incremental orchestration operations for this plan:
- Inspect package docs, status files, state, branches, commits, and diffs.
- Create/update the integration branch.
- Merge package branches into the integration branch according to Merge Strategy.
- Run integration verification.
- Merge the verified integration branch back to mainline.
- Write `FINAL_REPORT.md` and `status/99-finalize.md`.
- Delete only local branches/worktrees created and recorded by this orchestration after every finalize step succeeds.

Forbidden without explicit user approval:
- force-push
- hard reset
- delete branches/worktrees not recorded as created by this orchestration
- delete remote branches
- add secrets or credentials
- edit outside allowed paths

## Dependency Graph
| Package | Depends On | Dependency Type | Unlock Condition | Wave |
|---|---|---|---|---|
| 01-xxx | none | status | completed | 1 |
| 02-xxx | none | status | completed | 1 |
| 03-xxx | 01-xxx, 02-xxx | code | upstream merged to integration branch or explicit branch base | 2 |
| 99-finalize | all functional packages | status+code | all functional packages completed | final |

## Merge Strategy
- Functional merge order: <ordered package IDs>
- Code dependency policy: <status dependency | merge-to-integration first | downstream bases on upstream branch>
- Conflict owner: `99-finalize`
- Mainline merge: local non-force merge after integration verification passes.
- Analysis/planning artifact landing: reports, plans, task packages, HTML review surfaces, and `FINAL_REPORT.md` are merge-eligible documentation assets by default when they only touch approved docs/reports paths and pass privacy/sensitive-content, format/link, and conflict checks. Do not leave them only on package branches, watches/sessions, temporary worktrees, or worker threads unless this INDEX records a specific isolation reason.
- Cleanup: delete only recorded local package worktrees/branches after all finalize steps succeed.

## Landing Strategy
- Primary landing path: <what must be true for the main plan to count as landed>
- Mainline documentation landing: <for analysis/planning packages, default to merge durable docs/reports artifacts to mainline after privacy/sensitivity, path, format/link, and conflict checks pass; write "n/a" only for code-only plans>
- Preapproved fallback paths, in order: <fallback id, trigger, acceptance criteria, verification, and whether it may merge to mainline>
- Unacceptable degradation: <shortcuts or partial states that must not be shipped>
- Abort conditions: <conditions that end this orchestration as failed instead of retrying>
- Independent merge candidates if main plan fails: <package ids or "none"; for each, explain independence, standalone acceptance, and standalone verification>

Allowed task-level outcomes:
- `landed`: primary path landed and verification passed.
- `landed-with-approved-fallback`: a preapproved fallback landed and verification passed.
- `ready-for-external-gate`: autonomous work is complete but a declared release-blocking external gate is still pending.
- `failed-no-merge`: the main plan failed, no fallback is approved, and nothing may be merged.
- `failed-with-candidate-independent-fixes`: the main plan failed, but predeclared independent fixes are available for separate review.

## UX Delta Policy
- Packages with user-visible behavior, layout, copy, workflow, visual output, or trust-boundary changes must include a User-Visible Delta Ledger in the package doc.
- Bounded discretion: package agents may make small adjacent changes when they are necessary to solve the assigned user problem and remain near the target surface.
- Required recording: any visible drift outside the target surface must be recorded as `expected`, `acceptable-adjacent`, or `decision-required`.
- `expected`: the visible change is the package goal.
- `acceptable-adjacent`: the visible change is near the package goal, has rationale, and includes preservation evidence.
- `decision-required`: the visible change affects protected primary workflows, first-screen composition, navigation model, release promise, or an explicit non-goal. It needs user/product decision, a split package, a downgrade, or an approved fallback before mainline merge.
- Protected surfaces for this plan: <project-specific surfaces or "none declared">.

## Stop Conditions
- Any functional package is `blocked`, `stale`, or `invalid`.
- Graph has duplicate package IDs, missing dependencies, or cycles.
- Package evidence is incomplete.
- Package changed forbidden paths.
- A package records a `decision-required` UX delta that has not been approved, split, downgraded, or mapped to a preapproved fallback.
- Merge conflict or verification failure occurs.
- Status/state mismatch cannot be reconciled.
- Abort condition in Landing Strategy is met.
- A package identifies the main plan as non-landable and no preapproved fallback applies.

## Capability Preflight
| Package Or Gate | Class | Owner | Why Not Fully Autonomous | Autonomous Substitute | External Evidence Required | Blocks |
|---|---|---|---|---|---|---|
| 01-implementation | autonomous | Claude Code | n/a | tests/build | none | normal graph |
| real-device-qa | external-assist | user/Codex/device owner | requires physical device or human visual judgment | APK path, install command, logs, focused tests | checklist result, screenshot/video/log if available | release only after explicit user approval; otherwise stop before generating this kit |
```

### 4. launchers/agent-prompts.md

Generate one compact bootstrap prompt per package. The package doc owns local
scope, acceptance, and verification detail; the prompt carries only the
execution invariants needed before those files are read. Each prompt must end
with the shared tail call.

The heading is a machine-readable runtime key, not presentation-only Markdown.
For every row in `package-graph.tsv`, generate exactly one heading in this exact
shape. Do not shorten it to `## <package-id>`, and do not duplicate package
headings:

### Compact Functional Package Prompt

Use this compact form for normal functional packages. Expand it only for a
package-specific manual gate, external-assist boundary, retry context, or other
declared exception. Do not paste the full INDEX authorization, Landing Strategy,
projection catalog, recovery taxonomy, or finalize workflow into every package.

````markdown
# Agent Prompts

## Package: <package-id> - <title>

**Mode**: functional package executor
**INDEX**: <absolute-plan-dir>/INDEX.md
**Package doc**: <absolute-plan-dir>/packages/<package-id>.md
**Coordinator status**: <absolute-plan-dir>/status/<package-id>.md
**Coordinator state**: <absolute-plan-dir>/status/state.tsv
**Package graph**: <absolute-plan-dir>/launchers/package-graph.tsv
**Orchestrator**: <absolute-plan-dir>/launchers/orchestrate.sh

## Package Execution Authorization

The INDEX authorizes routine in-scope work without another confirmation: use only
this package's branch/worktree, edit only package-doc allowed paths, run focused
verification, commit local changes, and write only this package's coordinator
status. Never edit `state.tsv` manually; scheduler state changes only through
`mark-state`.

Normal-path context:
1. Read the package doc, assigned coordinator status, this package's graph/state
   rows, and relevant repository files.
2. Read `INDEX.md` only when authorization, capability boundaries, dependency
   policy, or an approved fallback cannot be resolved from the package doc.
3. Read `status/events.jsonl` only when this package is retried, was previously
   blocked, or needs prior failure context.
4. Request `scratch-path <package-id>` only when the package declares a real
   temporary exchange need. Scratch is non-authoritative and must not contain
   secrets or completion evidence.

Do not emit progress narration, restate the task, or produce intermediate chat
summaries. Use tools, then write durable evidence once to the assigned status
file. Global merge, fallback selection, cleanup, and task-level outcome decisions belong to `99-finalize`.

Forbidden without explicit approval: destructive git operations, unassigned
branch/worktree deletion, edits outside allowed paths, secrets or credentials,
undeclared external accounts/devices/human gates, graph/policy changes, or edits
to another package's status.

For user-visible packages, use bounded UX discretion. You may make small
adjacent visible changes when they are necessary to solve the assigned user
problem and remain near the package's target surface. Record any visible drift
outside the target surface in the coordinator status as `expected`,
`acceptable-adjacent`, or `decision-required`. Do not hide a change to protected
primary workflows, first-screen composition, navigation model, release promise,
or an explicit non-goal inside a bugfix; mark it `decision-required` with a
concrete recovery hint.

If an in-scope operation is prevented by runner, sandbox, permission,
subscription, credential, network, or external capability limits, do not wait
interactively or retry blindly. Record a precise blocker.

Before the tail call:
- Write worktree, branch, base/commit SHA, changed files, verification results,
  risks, and blocker diagnosis when applicable to the coordinator status file.
- For user-visible packages, write UX delta class, changed surfaces,
  preservation evidence, and any decision-required drift.
- Mark machine state through one of these commands:

```bash
bash <absolute-plan-dir>/launchers/orchestrate.sh mark-state <package-id> completed --commit <commit-sha> --verification "<command: result>"
```

```bash
bash <absolute-plan-dir>/launchers/orchestrate.sh mark-state <package-id> blocked \
  --error "<specific blocker>" \
  --failed-command "<failed command, if any>" \
  --conflict-files "<comma-separated files, if any>" \
  --log-summary "<short log summary>" \
  --recovery-hint "<specific next action>"
```

Tail call:
```bash
bash <absolute-plan-dir>/launchers/orchestrate.sh advance --from <package-id>
```

After the tail call returns, terminate the package session immediately. Do not ask for input, emit another summary, suggest a reply, or wait at an interactive prompt. Completion, blocker, and recovery details already belong in the coordinator artifacts.

If the platform cannot run shell commands, record `completed but advance not
run`; the coordinator may then expose the manual `advance` command to the user.
````

After generating all artifacts, run:

```bash
bash -n <absolute-plan-dir>/launchers/orchestrate.sh
bash -n <absolute-plan-dir>/launchers/start-codex-app.sh
bash -n <absolute-plan-dir>/launchers/start-claude-code.sh
bash <absolute-plan-dir>/launchers/orchestrate.sh status
```

Do not present start commands to the user until these commands pass. The `status`
preflight must reject missing, duplicate, unknown, or malformed package prompt
headings before any worktree or state mutation.

### 5. status/package-status-template.md

`status/<package-id>.md` is the human-readable package evidence file. The coordinator
script reads and writes `## State` via `markdown_status()` and `sync_markdown_state()`;
both functions require the state value to be wrapped in backticks on its own line
immediately after `## State`.

**CRITICAL**: The state value after `## State` MUST be wrapped in backticks. A bare
`pending` or `completed` line without backticks will be parsed as `unknown`, causing
`status_consistency_ok()` to fail and `repair-state` to reset the package to `pending`.

Valid states (from `valid_state()` in `orchestrate-template.sh`):

| State | Meaning |
|---|---|
| `pending` | Not yet dispatched |
| `ready` | Dependencies satisfied, eligible for launch |
| `manual_required` | Needs human intervention before dispatch |
| `launched` | Agent session started |
| `in_progress` | Agent is executing |
| `completed` | Finished successfully (aliases: `done`, `complete` recognized by `markdown_status()`) |
| `blocked` | Cannot proceed; needs investigation or recovery |
| `stale` | Agent session unreadable or lost |
| `invalid` | Precondition violated (missing commit, broken dependency) |
| `finalizing` | `99-finalize` is in progress |
| `finalized` | `99-finalize` has finished |

Template:

```markdown
# <Package Title> - Status

## State

`pending`

## Evidence

- **Worktree**: <absolute path or "not yet created">
- **Branch**: <branch name or "not yet created">
- **Base commit**: <sha or "pending">
- **Commit hash**: <sha or "pending">
- **Changed files**:
  - <path> — <summary of change>

## Verification

- `<command>`: `<result or "not yet run">`

## User-Visible Delta

Fill for user-visible packages; otherwise write `n/a`.

- **UX delta class**: n/a | expected | acceptable-adjacent | decision-required
- **Target surface**: <surface or "n/a">
- **Changed surfaces**: <surfaces changed beyond code internals>
- **Preserved surfaces evidence**: <tests, screenshots, metrics, manual notes, or "n/a">
- **Decision required**: <decision needed, or "none">

## Risks

- <known risk or "none identified">

## Blocker Diagnosis

Fill only when state is `blocked`, `stale`, or `invalid`.

- **Failure category**: capability-gap | invalid-requirement | external-dependency | verification-failure | merge-conflict | design-invalid | cost-out-of-scope | unknown-needs-investigation
- **Last error**: <concrete error message>
- **Failed command**: <command that failed, or "n/a">
- **Conflict files**: <comma-separated paths, or "none">
- **Log summary**: <decisive log excerpt>
- **Recovery hint**: <specific next action for user or coordinator>
```

`sync_markdown_state()` keeps the `## State` value in sync with `state.tsv` on every
`mark-state` write. If an existing status file uses the legacy `**Status**:` format, it is
updated in place; if neither backtick nor `**Status**:` is found, a new `## State` section
is appended at the end of the file.

### 8. packages/99-finalize.md

Generate a finalize package, not a passive audit-only prompt.

`99-finalize` must:
1. Read INDEX, graph, all package docs, all status files, and `state.tsv`.
2. Run `bash launchers/orchestrate.sh verify-finalize` before merging.
3. Verify every functional package:
   - acceptance criteria addressed
   - changed files are within allowed paths
   - evidence pack complete
   - branch, worktree, base commit, commit hash recorded
   - verification commands passed or failure is explicitly justified
   - package branch exists
   - package commit hash exists
   - package changed files are within allowed paths
   - package worktree is clean, or dirty state is recorded as a blocker
4. Check projection consistency across INDEX, graph, state, package status, and events before treating any package as globally complete.
5. Check the Capability Preflight section. If an external-assist gate is release-blocking and evidence is absent, stop with "ready for external QA" or "waiting for external gate"; do not claim overall PASS.
6. Run UX Delta Review for user-visible packages: classify actual visible changes as `expected`, `acceptable-adjacent`, or `decision-required`. Accept `expected` and justified `acceptable-adjacent` deltas with evidence; block, split, downgrade, or request user decision for unresolved `decision-required` deltas.
7. Check Landing Strategy. Decide task-level outcome before any mainline merge: `landed`, `landed-with-approved-fallback`, `ready-for-external-gate`, `failed-no-merge`, or `failed-with-candidate-independent-fixes`.
8. Decide whether merging is allowed. For analysis-only or planning-only artifacts, the default is to merge durable docs/reports outputs to mainline after privacy/sensitive-content screening, path classification, format/link checks, and conflict checks pass; leaving them only on worker branches, watches/sessions, temporary worktrees, or worker threads requires a recorded isolation reason.
9. Create or update the integration branch.
10. Merge functional package branches in Merge Strategy order.
11. Stop and record conflicts without cleaning anything.
12. Run integration verification.
13. Merge integration branch back to mainline only after verification passes, release-blocking external gates are satisfied or explicitly deferred by the user, and no unresolved `decision-required` UX delta remains.
14. Write `FINAL_REPORT.md` and `status/99-finalize.md` for both success and failure.
15. Run `bash launchers/orchestrate.sh cleanup --mainline <mainline-branch>` after every prior step succeeds. Do not delete branches/worktrees manually.
16. Mark `99-finalize` as `finalized` only after cleanup reports success.

Failure rules:
- Any failure sets `99-finalize` to `blocked`.
- Record failure stage, command, branch, conflict files if any, log summary, and recovery suggestion in `status/99-finalize.md`.
- Also update the coordinator ledger with `mark-state 99-finalize blocked --error ... --failed-command ... --conflict-files ... --log-summary ... --recovery-hint ...`; do not leave merge/test failures only in prose.
- Check `status/events.jsonl` when explaining repeated failures; do not keep retrying the same fingerprint after the retry breaker opens.
- If the primary plan is non-landable, write a failure analysis that separates: observed facts, failed assumptions, failure category, attempted or rejected fallback paths, whether the user must decide, and the recommended next orchestration or abort action.
- If UX Delta Review finds an unresolved `decision-required` change, describe the changed surface, why it exceeds package discretion, the user value at stake, and whether to split, downgrade, accept explicitly, or use a preapproved fallback.
- Default to no merge when the task outcome is `failed-no-merge`.
- For `failed-with-candidate-independent-fixes`, list candidate package ids, recorded commits, allowed paths, standalone verification, and why each candidate is independent from the failed main plan. Do not merge a candidate unless it was predeclared in Landing Strategy and passes standalone verification.
- Preserve branches/worktrees on failure.
- If package status and current workspace disagree, verify the recorded package commit in a clean detached worktree before changing state.
- Never force-push, hard reset, delete remote branches, or delete unrecorded local resources.
- Never mark `99-finalize` as `finalized` while cleanup is deferred, blocked, or incomplete.
- Never mix coordinator ledger/final-report commits with unrelated orchestration documents or concurrent mainline edits.

Success rules:
- Run `cleanup --mainline <mainline-branch>`; it verifies recorded commits entered mainline, blocks dirty or unmerged resources, deletes recorded worktrees before local branches, and writes cleanup results into `state.tsv` and `events.jsonl`.
- Mark `99-finalize` as `finalized` only after cleanup succeeds.
- Record integration branch, mainline merge commit, verification summary, and cleanup results.
- Re-running finalize after success must be idempotent and report `already finalized`.

Terminal session rule:
- After recording either `blocked` or `finalized`, run `bash launchers/orchestrate.sh advance --from 99-finalize` as the tail call.
- After the `99-finalize` tail call returns, terminate the finalize session immediately. Do not ask for input, restate the final report in chat, suggest a reply, or wait at an interactive prompt. Keep blocker, recovery, and outcome details in `status/99-finalize.md`, `state.tsv`, `events.jsonl`, and `FINAL_REPORT.md`.

### 9. Output Style

After generating the kit, chat output must be immediately actionable and must
show the manual path, both platform script launch commands, and a small command
surface. Mark the selected runner's wrapper as the primary script path and the
other wrapper as the alternative runner.
The runtime still exposes the full recovery command set through
`orchestrate.sh`; do not turn every recovery ability into default chat output.

Always include this information:
- Plan directory path.
- Mainline branch.
- Integration branch.
- Max parallel agents.
- Selected runner and why it was selected: `codex`, `claude`, or `manual`.
- First wave packages.
- Final package: `99-finalize`.
- A statement that downstream dispatch is triggered by package tail calls to `advance`.
- Any external-assist gates, their owners, whether they block release or only final confidence, and the exact evidence expected.
- Any unresolved `decision-required` UX delta, the affected package, and the concrete user/product decision needed.
- Landing strategy summary: primary landing path, preapproved fallbacks, abort conditions, and independent merge candidates if the main plan fails.

For the **Manual** path, include a package table so the user can decide which prompts to copy first:

| Package | Prompt Location | Can Start Now | Must Wait For | Dependency Type | Notes |
|---|---|---|---|---|---|
| 01-xxx | `<plan>/launchers/agent-prompts.md#01-xxx` | yes | none | status | first wave |
| 02-xxx | `<plan>/launchers/agent-prompts.md#02-xxx` | yes | none | status | first wave |
| 03-xxx | `<plan>/launchers/agent-prompts.md#03-xxx` | no | 01-xxx, 02-xxx | code | started by `advance` |
| 99-finalize | `<plan>/launchers/agent-prompts.md#99-finalize` | no | all functional packages | status+code | auto final package |

The Manual section must say:
- Copy prompts from `<plan>/launchers/agent-prompts.md`.
- Start every row where `Can Start Now = yes` in any agent platform.
- Later packages should not be manually started unless their dependencies are satisfied or the user intentionally overrides automation.
- If an agent platform cannot run local shell commands, the user may manually run `advance`.

For the **Script** path, include complete copy-paste commands for a new macOS Terminal. Commands must use absolute paths and avoid assuming the user's current directory.
Always include both platform launch commands: one selected-runner primary block
and one alternative-runner block. The alternative block must include the
copy-paste launch command for the other platform, not merely mention that the
wrapper exists, so one app can plan and the other can launch the same kit.
When Codex is primary, include a separate Claude Code alternative block. When Claude Code is primary, include a separate Codex App / Codex runner alternative block.
Do not collapse the alternative into prose, omit `cd "<repo-root>"`, or replace
the other platform command with bare `orchestrate.sh`.

Required block labels:
- **Primary script path (Codex App / Codex runner)**
- **Alternative runner (Claude Code)**
- **Primary script path (Claude Code)**
- **Alternative runner (Codex App / Codex runner)**

Codex primary command surface, used when the selected runner is Codex. The same
commands are also the **Alternative runner (Codex App / Codex runner)** block
when Claude Code is primary:

```bash
cd "<repo-root>"
bash "<absolute-plan-dir>/launchers/start-codex-app.sh"
bash "<absolute-plan-dir>/launchers/start-codex-app.sh" status
```

Codex inspection surface:

```bash
bash "<absolute-plan-dir>/launchers/start-codex-app.sh" tail <package-id>
bash "<absolute-plan-dir>/launchers/start-codex-app.sh" resume <thread-id>
```

Use concrete package ids in place of `<package-id>`, and strip the
`codex-thread:` prefix before passing a thread id to
`codex exec resume <thread-id>`.

Claude primary command surface, used when the selected runner is Claude Code.
The same commands are also the **Alternative runner (Claude Code)** block when
Codex is primary:

```bash
cd "<repo-root>"
bash "<absolute-plan-dir>/launchers/start-claude-code.sh"
bash "<absolute-plan-dir>/launchers/start-claude-code.sh" status
bash "<absolute-plan-dir>/launchers/start-claude-code.sh" agents
```

If Codex is selected because the user is working in Codex App, add this note:
"This script lane uses local `codex exec --json` processes and coordinator
logs; Codex App native subagents remain available through the Manual path, but
the generated script does not create App UI subagent threads directly."

Recovery commands are contextual. Show only the one or two commands that match
the current state, and name the concrete package ids that may use them:

- If a package is `blocked`, `stale`, or `invalid`: show `retry <package-id>`
  after explaining why retry is permitted.
- If runner/environment setup is suspect: show `doctor --environment`.
- If logs are required for diagnosis: show `collect-logs <package-id>`.
- If a shell-less/manual agent completed work but could not tail-call: show
  `advance`.
- If finalize is blocked after all functional packages completed: show
  `verify-finalize` or `finalize`, whichever is the next concrete action.
- If a package explicitly needs temporary exchange space: show `scratch-path
  <package-id>`.

Example contextual recovery block:

```bash
bash "<absolute-plan-dir>/launchers/orchestrate.sh" retry <package-id>
```

For Codex runner status inspection, include:

```bash
bash "<absolute-plan-dir>/launchers/start-codex-app.sh" doctor
bash "<absolute-plan-dir>/launchers/start-codex-app.sh" tail <package-id>
bash "<absolute-plan-dir>/launchers/start-codex-app.sh" resume <thread-id>
```

If `doctor --environment` reports `codex_exec_approval_policy_flag=unavailable`, the default `ORCHESTRATION_CODEX_APPROVAL_POLICY=never` is still valid because the launcher omits the unsupported flag. If launch stderr reports a readonly Codex state DB or app-server initialization failure, fix the launch shell or runner permissions before retrying; do not classify that as package work failure.

If a command contains placeholders such as `<package-id>`, explicitly say which concrete package IDs are valid recovery targets. Do not leave the user to infer them from the docs.

Do not present `/batch`, `dispatch-claude-agents.sh`, or a separate audit prompt as peer user entrypoints.
