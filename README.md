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
| Unified Ledger | One structured record format for requests, decisions, sessions, risks, issues, and artifacts |
| Health Check | Validates required files, entry-file sync, hook helpers, gitkeep files, imports, safety, and platform junk |
| Agent Sync | Regenerates `CLAUDE.md` from `AGENTS.md` |
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
├── docs/                   # Project documentation
├── .tmp/                   # Local scratch space, not committed
├── .codex/
│   └── config.example.toml
├── .claude/
│   ├── hooks/panel_hook.py
│   └── settings.example.json
├── AGENTS.md               # Shared source of truth
├── CLAUDE.md               # Claude Code entry point
└── SETUP_NEW_MACHINE.md    # First-time setup guide
```

## Codex Hooks

Codex reads the shared entry point from `AGENTS.md`. For end-of-turn guarded commits, copy the `notify` example from `.codex/config.example.toml` into your user-level `~/.codex/config.toml` and replace the placeholder path with this repository's absolute path.

The notify script calls `python3 tools/project.py commit`, so it keeps the same allowlist and secret/temp/output protections as the Claude Code Stop hook. Run `python3 tools/hooks/panel_print.py` whenever you want the same status panel printed in a terminal.

For new-session context, `.codex/hooks.json` provides a `UserPromptSubmit`
example that injects the Chinese status panel on the first prompt in a session.
The panel can also be rendered manually with:

```bash
python3 tools/panel.py --mode entry
python3 tools/panel.py --mode handoff
```

The panel stays lightweight by reading only `AGENTS.md`, `control/state.md`,
`control/ledger.md`, `src/`, and bounded git metadata commands. It does not scan
the full source tree, inspect large diffs, call networks, or invoke an LLM.

For broader Codex App use across projects, prefer a user-level
`clean-checkpoint-first` skill plus a user-level Stop hook. The skill teaches the
workflow; the hook prevents silent dirty-workspace leakage. Repository-local
hooks remain useful when a copied project needs stricter project-specific gates.
