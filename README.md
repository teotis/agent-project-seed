# Agent Project Seed

A copy-and-use multi-agent collaboration scaffold. Clone it, initialize once, and give Codex and Claude Code the same project rules, state, and record trail.

- Python >= 3.9, zero runtime dependencies
- Supports Codex / Claude Code
- Plain-text governance: no database, no hosted service, no agent framework

## Why Use It

AI agents work better when they share the same operating context. This scaffold gives a repository:

- A shared contract for project rules, goals, and acceptance criteria
- A current-state snapshot for handoff between sessions and agents
- A structured ledger for requirements, decisions, risks, issues, and artifacts
- Safe commit tooling that rejects secrets, temp files, generated outputs, and unexpected paths
- Synced `AGENTS.md` and `CLAUDE.md` entry points
- A lightweight status panel for Claude Code hooks and Codex-friendly helper commands

## What's Included

| Feature | Description |
| --- | --- |
| Status Panel | Shows a compact Chinese entry/handoff snapshot, leading with the user goal, acceptance progress, evidence, gaps, and next decision when a delivery receipt exists |
| Safe Commit | Path-allowlisted commit command that blocks disallowed artifacts and high-confidence secret patterns before staging |
| Claude Code Project Hooks | Project-level `.claude/settings.json` enables the status panel and the same baseline-aware clean-checkpoint Stop gate as Codex |
| Clean Checkpoint Gate | Project-level Codex hook blocks session stop when new tracked dirty changes are left uncheckpointed |
| Unified Ledger | One structured record format for requests, decisions, sessions, risks, issues, and artifacts |
| Health Check | Validates required files, entry-file sync, hook helpers, gitkeep files, imports, safety, and platform junk |
| Agent Sync | Regenerates `CLAUDE.md` from `AGENTS.md` |
| Portable User Skills | Bundles selected user-installed skills for fast Codex/Claude setup |
| Claude Code Defaults | Configures user-level new sessions to `auto` permission review after requiring Claude Code v2.1.140 or newer |
| Complex Task Work Packet | Optional `tools/project.py task init` command for cross-session or multi-package work, with intent, curated context, live state, evidence, and a knowledge-promotion review |
| Governance Lifecycle | Optional `tools/project.py governance init` command for long-lived projects that need rule/script/report lifecycle tracking |
| Utility Package | Small Python helpers for paths, atomic writes, env loading, API gating, records, manifests, QC, and review pages |
| Multi-Agent Entry Points | Tool-specific files all point back to the same shared contract |

## Clean Checkpoint Design

This seed treats agent work as a sequence of auditable checkpoints, not as an
open-ended dirty working tree. A local checkpoint commit, even if it later needs
amend/squash cleanup, is preferred to leaving mixed tracked changes behind.

Recommended Codex App shape for copied projects:

- Use a reusable skill for the repair/closeout workflow: inspect, implement,
  verify, stage relevant files only, commit locally, and report branch status.
- Use hooks for mechanical end-of-turn gates, especially detecting new tracked
  dirty changes that were produced by the current session but not checkpointed.
- Use rules or permissions for dangerous command boundaries such as push,
  destructive reset, broad remove, or coarse staging.
- Use Codex App worktrees for independent issue branches, then use one
  integration/finalizer session to merge, verify, and explain the final state.
- Keep `AGENTS.md` small. It should point to the workflow and invariants; bulky
  procedure belongs in skills, scripts, and hook checks.

The default policy is local-only: do not push unless the user explicitly asks
for remote sync.

In plain terms, the project-level `clean-checkpoint-first` gate protects the user
from a common agent failure mode: an agent edits tracked files, does not commit
or clearly hand off the changes, then ends the session. The hook records the
starting tracked dirty state at session start. At stop time, it compares the
current tracked dirty state against that baseline. If the session created new
tracked dirt and no checkpoint commit removed it, Stop is blocked until the
agent either creates a local checkpoint or explicitly reports why closeout is
blocked. It does not auto-commit, push, delete, or rewrite files.

## Claude Code New-Session Defaults

On new machines, use Claude Code v2.1.140 or newer, then run the project helper
to make new sessions default to `auto` permission review:

macOS/Linux:

```bash
python3 tools/project.py configure-claude
```

Windows PowerShell:

```powershell
py -3 tools/project.py configure-claude
```

This edits only the user-level Claude settings file and preserves existing
`allow`/`deny` rules. The helper writes `permissions.defaultMode = "auto"` and
refuses to write when it cannot verify that Claude Code is v2.1.140 or newer.

## Complex Task Work Packets

Most projects should start with the lightweight default: `control/state.md` for
current state, `control/ledger.md` for durable records, and local checkpoint
commits for auditability. Do not create a full task control surface for routine
single-session work.

When work becomes complex enough to span multiple packages, branches, worktrees,
agents, or handoff sessions, create an explicit Work Packet:

macOS/Linux:

```bash
python3 tools/project.py task init --name "Complex Refactor" \
  --package 01-contract-characterization \
  --package 02-implementation
```

Windows PowerShell:

```powershell
py -3 tools/project.py task init --name "Complex Refactor" `
  --package 01-contract-characterization `
  --package 02-implementation
```

This creates `control/tasks/<slug>/` with:

- `brief.md` for the user goal, acceptance criteria, and non-goals;
- `context.jsonl` for the smallest stage-scoped set of project files an agent
  must read, with a reason for every entry;
- `status.tsv`, `events.jsonl`, and per-package evidence notes for live state;
- `promotion.md` for the final decision about which learnings belong in a test,
  hook, module document, ledger record, the task itself, or nowhere permanent.

Add and inspect curated context without introducing another runtime dependency:

```bash
python3 tools/project.py task context add complex-refactor \
  --file control/state.md \
  --reason "Current project state and next action" \
  --stage implement
python3 tools/project.py task context list complex-refactor --stage implement
```

The `handoff` phase reuses `check` context because handoff should verify and
explain the finished work rather than introduce a fourth manifest stage.

The project health check validates every context entry: paths must stay inside
the repository, point to an existing supported text file, include a reason, use
`plan`, `implement`, or `check`, and avoid duplicate file/stage pairs.
The shared agent reading order requires an active Work Packet's `brief.md` and
stage-relevant context to be read before work begins, so the manifest is an
operational input rather than passive documentation.

Activate a Work Packet for the current git worktree when its phase and next
required action should appear in the status panel:

```bash
python3 tools/project.py task activate complex-refactor \
  --phase implement \
  --next "Implement the first verified slice"
python3 tools/project.py task current
python3 tools/project.py task deactivate
```

Active-task state is git-private and worktree-scoped, so it is not committed or
shared accidentally. In the task folder, `status.tsv` remains the live source
of truth for package execution state; chat transcripts, status panels, and final
reports are secondary projections. If `99-finalize` is marked `finalized`, the
project health check requires at least one classification in `promotion.md`, so
the finish review cannot remain an untouched template.

Task directories created by older seed versions remain valid live-state
surfaces. They become Work Packets only when one of the new packet files
(`brief.md`, `context.jsonl`, or `promotion.md`) is present, which keeps upgrades
from breaking existing task records.

## Governance Lifecycle

Most copied projects should not start with a governance control surface. The
default rule is lighter: when a durable project rule, verification script,
report flow, or agent workflow is added, record why it exists and what would let
the project downgrade or remove it later.

Use the optional lifecycle file only when project assets are likely to outlive a
single task:

- `one-off`: skip `control/governance.md`; clean temporary rules and reports at
  handoff.
- `lightweight`: use `control/ledger.md` for the few rules or scripts that need
  future recall.
- `sustained`: generate `control/governance.md` and classify important
  governance items as `Protect`, `Pilot`, `Defer`, or `Retire`.

macOS/Linux:

```bash
python3 tools/project.py governance init --profile sustained
```

Windows PowerShell:

```powershell
py -3 tools/project.py governance init --profile sustained
```

The generated file is deliberately small. It is a review surface for the rules,
scripts, reports, and workflows around a project; it does not enable a hook,
delete files, create recurring process, or make preflight stricter.

## Portable User Skills

This seed carries a portable skill bundle under `agent-assets/user-skills/`.
The bundle keeps skill packages in one flat directory:

- `skills/<skill-name>/`: the portable skill package copied into a user skill root.
- `manifest.json`: profile and source metadata for installation decisions.

The manifest at `agent-assets/user-skills/manifest.json` is the source of truth.
Use the project tool to inspect or install the bundle. The default `recommended`
profile is intentionally small (implementation, diagnosis, tests, review, research,
handoff, and clean closeout); `all` is the opt-in specialist snapshot. Audit an
existing installation before replacing it with `--force`.

macOS/Linux:

```bash
python3 tools/project.py list-user-skills
python3 tools/project.py install-user-skills --target codex
python3 tools/project.py audit-user-skills --target codex --strict
python3 tools/project.py configure-claude
python3 tools/project.py install-user-skills --target all --profile all --force
```

Windows PowerShell:

```powershell
py -3 tools/project.py list-user-skills
py -3 tools/project.py install-user-skills --target codex
py -3 tools/project.py audit-user-skills --target codex --strict
py -3 tools/project.py configure-claude
py -3 tools/project.py install-user-skills --target all --profile all --force
```

The installer copies skills into the chosen user skill root. It does not copy
tokens, MCP secrets, model provider settings, conversation logs, hook state, or
other machine-local private configuration.

## Quick Start

macOS/Linux:

```bash
# 1. Copy the scaffold
cp -r project_seed my-new-project
cd my-new-project

# 2. Initialize from a goal brief (recommended)
python3 tools/project.py init --name "My Project" --brief product-brief.md

# 3. Verify
make preflight
make test
```

Windows PowerShell:

```powershell
# 1. Copy the scaffold
Copy-Item -Recurse project_seed my-new-project
Set-Location my-new-project

# 2. Initialize from a goal brief (recommended)
py -3 tools/project.py init --name "My Project" --brief product-brief.md

# 3. Verify
py -3 tools/project.py check
py -3 -m pytest
```

See [SETUP_NEW_MACHINE.md](SETUP_NEW_MACHINE.md) for detailed first-time setup.

Initialization is a one-way transition from template workspace to project
workspace. It rewrites the project-facing README, updates `AGENTS.md` and
`control/state.md`, resets `control/ledger.md` to a project-local first record,
renames the Python package, activates local Claude settings, and writes
`control/init_manifest.md` so the user can see what changed and what still needs
manual project-specific editing. The health check rejects obvious template
residue in project-facing files after initialization.

Use a small Markdown brief to make the initialized project immediately usable:

```markdown
## Target User
Independent researchers

## Core Problem
They lose decision context between research sessions.

## Project Goals
- Preserve decision context with each research artifact.

## Acceptance Criteria
- A researcher can recover a decision and its evidence in one view.
```

`init --brief product-brief.md` writes this intent into `AGENTS.md`,
`control/state.md`, the initial ledger record, and `control/delivery_receipt.md`.
The receipt is the default user-facing handoff surface; update its checkbox
criteria, evidence, gaps, and next decision as work progresses. For a terminal
prompt instead of a file, use `init --interactive`.

## Run a Problem-Solving Round

`AGENTS.md` contains the authoritative adaptive contract. The minimum path is
to read it plus the files directly involved. Read `control/state.md` or relevant
ledger records only when current state or prior decisions constrain the task.

Use `reports/<topic>/` for conclusions that will be reused or reviewed. When a
task changes tracked files, run the project check and proportional tests, then
close with a guarded local checkpoint or an explicit blocked handoff. Create a
Work Packet only for work that actually crosses dependent packages, worktrees,
agents, or handoff sessions, and enter one only when the current user request
explicitly continues, resumes, or names it. A stale active marker is background
handoff context, not an instruction to take over another task.

## Keep Verification Separate from Delivery

Verification may create disposable local output, but it does not allocate a
version, create a handoff artifact, or make a result active outside the
project. Generate a handoff artifact only when the current request asks for a
user-reviewable or transferable result. Publishing, installation, upload, and
other deployments remain separate external effects that require explicit
authorization. Add a project-specific manifest or review surface only when a
repeated project need justifies it.

## Directory Layout

```text
├── control/
│   ├── ledger.md           # Structured long-term records
│   └── state.md            # Current state snapshot
├── reports/                # Durable analysis reports and review artifacts
├── work/
│   ├── in/                 # Input materials
│   ├── out/                # Final artifacts, not committed
│   └── tmp/                # Temporary files, not committed
├── tools/
│   ├── project.py          # Init, check, sync, safe commit
│   ├── panel.py            # Status panel generator
│   └── hooks/              # Codex hook helpers
├── src/
│   └── base_scaffold/      # Small reusable Python utilities
├── tests/
├── agent-assets/
│   └── user-skills/        # Portable user-installed skill bundle
├── docs/                   # Project documentation
├── .tmp/                   # Local scratch space, not committed
├── .codex/
│   ├── config.example.toml
│   ├── config.windows.example.toml
│   ├── hooks.json
│   ├── hooks.windows.json
│   └── hooks/
│       ├── clean_checkpoint_first.py
│       └── panel_hook.py
├── .claude/
│   ├── hooks/panel_hook.py
│   ├── settings.json
│   ├── settings.example.json
│   └── settings.windows.example.json
├── AGENTS.md               # Shared source of truth
├── CLAUDE.md               # Claude Code entry point
└── SETUP_NEW_MACHINE.md    # First-time setup guide
```

## Claude Code Project Hooks

Initialized projects include `.claude/settings.json` as the active project-level
configuration. During `init`, the active file is rewritten from the
platform-specific example: Windows uses `py -3`, while macOS/Linux uses
`python3`. This project-level configuration is the default path for Claude Code:

- `UserPromptSubmit`: inject the lightweight Chinese status panel.
- `Stop`: block session exit when the current session leaves new tracked dirty
  changes without a deliberate local checkpoint or a documented blocker.

The Stop hook does not auto-commit. It records the session baseline on the first
prompt, then refuses to exit only when new tracked dirt remains. Agents review,
stage, and run `python3 tools/project.py commit` deliberately, so pre-existing
user changes are not silently committed.

User-level Claude/Codex hook setup is optional. Use it only when you want similar
behavior outside repositories that carry this project-level configuration.

## Codex Hooks

Codex reads the shared entry point from `AGENTS.md`. Initialized projects carry
`.codex/hooks.json` by default; during `init`, it is activated for the current
platform so Windows uses `py -3` and macOS/Linux uses `python3`. It includes:

- `SessionStart`: record the starting tracked dirty baseline.
- `PostToolUse`: keep the latest tracked dirty snapshot available for debugging.
- `Stop`: block session stop if this session leaves new tracked dirty changes.
- `UserPromptSubmit`: inject the lightweight Chinese status panel.

The clean-checkpoint hook stores its state in Git-private storage when
available, or `.tmp/` as a fallback. It never auto-commits, pushes, deletes, or
rewrites files. A local checkpoint commit is still the expected closeout when a
task produces tracked changes.

For optional end-of-turn guarded commits, copy the `notify` example for your
platform into the user-level Codex config and replace the placeholder with this
repository's absolute path:

- macOS/Linux: copy from `.codex/config.example.toml` into `~/.codex/config.toml`.
- Windows: copy from `.codex/config.windows.example.toml` into `%USERPROFILE%\.codex\config.toml`.

The notify script calls `tools/project.py commit` through the configured Python
launcher, so it keeps the same allowlist and secret/temp/output protections as
the manual safe-commit command. Run `python3 tools/hooks/panel_print.py` on
macOS/Linux or `py -3 tools/hooks/panel_print.py` on Windows whenever you want
the same status panel printed in a terminal.

The status panel can also be rendered manually with:

macOS/Linux:

```bash
python3 tools/panel.py --mode entry
python3 tools/panel.py --mode handoff
```

Windows PowerShell:

```powershell
py -3 tools/panel.py --mode entry
py -3 tools/panel.py --mode handoff
```

When `control/delivery_receipt.md` exists, the panel puts the user goal,
acceptance progress, evidence, remaining gaps, and user decision ahead of Git
metadata. The panel stays lightweight by reading only `AGENTS.md`,
`control/state.md`, `control/ledger.md`, `control/delivery_receipt.md`, `src/`,
and bounded git metadata commands. It does not scan
the full source tree, inspect large diffs, call networks, or invoke an LLM.

For broader Codex App use across unrelated projects, a user-level
`clean-checkpoint-first` skill and Stop hook can provide the same default outside
repositories created from this seed.
