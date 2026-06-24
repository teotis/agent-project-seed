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
| Status Panel | Shows a compact Chinese entry/handoff snapshot: git state, recent worktrees/branches, open ledger items, risks, and next action |
| Safe Commit | Whitelist-based commit command for agent-made changes |
| Clean Checkpoint Gate | Project-level Codex hook blocks session stop when new tracked dirty changes are left uncheckpointed |
| Unified Ledger | One structured record format for requests, decisions, sessions, risks, issues, and artifacts |
| Health Check | Validates required files, entry-file sync, hook helpers, gitkeep files, imports, safety, and platform junk |
| Agent Sync | Regenerates `CLAUDE.md` from `AGENTS.md` |
| Portable User Skills | Bundles selected user-installed skills and superpowers skills for fast Codex/Claude setup |
| Standard MCP Checks | Records Context7 as the default documentation MCP to verify on new machines |
| Complex Task Live State | Optional `tools/project.py task init` command for multi-package work that needs a stronger source of truth than chat or reports |
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

## Standard MCP Checks

Context7 is the standard documentation MCP to verify when setting up a new
machine or copied project environment. It gives agents current library and
framework documentation without putting project-specific secrets in this repo.

```bash
codex mcp get context7
claude mcp get context7
```

If either command fails, fix the user-level MCP configuration outside this
repository. Do not copy API keys, MCP tokens, or provider credentials into the
project.

## Complex Task Live State

Most projects should start with the lightweight default: `control/state.md` for
current state, `control/ledger.md` for durable records, and local checkpoint
commits for auditability. Do not create a full task control surface for routine
single-session work.

When work becomes complex enough to span multiple packages, branches, worktrees,
agents, or handoff sessions, create an explicit live-state surface:

```bash
python3 tools/project.py task init --name "Complex Refactor" \
  --package 01-contract-characterization \
  --package 02-implementation
```

This creates `control/tasks/<slug>/` with an `INDEX.md`, `status.tsv`,
`events.jsonl`, and per-package evidence notes. In that folder, `status.tsv` is
the live source of truth for package execution state; chat transcripts, status
panels, and final reports are secondary and should be refreshed from the live
state before deciding whether a complex task is complete.

## Portable User Skills

This seed carries a portable skill bundle under `agent-assets/user-skills/`.
The bundle is organized by migration intent, not by agent vendor:

- `core`: default workflow and engineering skills for a fresh environment.
- `optional`: generally useful analysis and interview/refinement skills selected
  for this workspace family.
- `superpowers`: the complete local superpowers skill set, copied as ordinary
  portable skills.

The manifest at `agent-assets/user-skills/manifest.json` is the source of truth.
Use the project tool to inspect or install the bundle:

```bash
python3 tools/project.py list-user-skills
python3 tools/project.py install-user-skills --target codex --group core
python3 tools/project.py install-user-skills --target all --group all --force
```

The installer copies skills into the chosen user skill root. It does not copy
tokens, MCP secrets, model provider settings, conversation logs, hook state, or
other machine-local private configuration.

## Quick Start

```bash
# 1. Copy the scaffold
cp -r project_seed my-new-project
cd my-new-project

# 2. Initialize
python3 tools/project.py init --name "My Project"

# 3. Verify
make preflight
make test
```

See [SETUP_NEW_MACHINE.md](SETUP_NEW_MACHINE.md) for detailed first-time setup.

Initialization is a one-way transition from template workspace to project
workspace. It rewrites the project-facing README, updates `AGENTS.md` and
`control/state.md`, resets `control/ledger.md` to a project-local first record,
renames the Python package, activates local Claude settings, and writes
`control/init_manifest.md` so the user can see what changed and what still needs
manual project-specific editing. The health check rejects obvious template
residue in project-facing files after initialization.

## Directory Layout

```text
├── control/
│   ├── ledger.md           # Structured long-term records
│   └── state.md            # Current state snapshot
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
│   ├── hooks.json
│   └── hooks/
│       ├── clean_checkpoint_first.py
│       └── panel_hook.py
├── .claude/
│   ├── hooks/panel_hook.py
│   └── settings.example.json
├── AGENTS.md               # Shared source of truth
├── CLAUDE.md               # Claude Code entry point
└── SETUP_NEW_MACHINE.md    # First-time setup guide
```

## Codex Hooks

Codex reads the shared entry point from `AGENTS.md`. Initialized projects carry
`.codex/hooks.json` by default with:

- `SessionStart`: record the starting tracked dirty baseline.
- `PostToolUse`: keep the latest tracked dirty snapshot available for debugging.
- `Stop`: block session stop if this session leaves new tracked dirty changes.
- `UserPromptSubmit`: inject the lightweight Chinese status panel.

The clean-checkpoint hook stores its state in Git-private storage when
available, or `.tmp/` as a fallback. It never auto-commits, pushes, deletes, or
rewrites files. A local checkpoint commit is still the expected closeout when a
task produces tracked changes.

For optional end-of-turn guarded commits, copy the `notify` example from
`.codex/config.example.toml` into your user-level `~/.codex/config.toml` and
replace the placeholder path with this repository's absolute path.

The notify script calls `python3 tools/project.py commit`, so it keeps the same allowlist and secret/temp/output protections as the Claude Code Stop hook. Run `python3 tools/hooks/panel_print.py` whenever you want the same status panel printed in a terminal.

The status panel can also be rendered manually with:

```bash
python3 tools/panel.py --mode entry
python3 tools/panel.py --mode handoff
```

The panel stays lightweight by reading only `AGENTS.md`, `control/state.md`,
`control/ledger.md`, `src/`, and bounded git metadata commands. It does not scan
the full source tree, inspect large diffs, call networks, or invoke an LLM.

For broader Codex App use across unrelated projects, a user-level
`clean-checkpoint-first` skill and Stop hook can provide the same default outside
repositories created from this seed.
