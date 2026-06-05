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
- Synced `AGENTS.md` and `CLAUDE.md` entry points (optional `GEMINI.md`)
- A lightweight status panel for Claude Code hooks and Codex-friendly helper commands

## What's Included

| Feature | Description |
| --- | --- |
| Status Panel | Shows project status, git status, ledger count, goal, and next action |
| Safe Commit | Whitelist-based commit command for agent-made changes |
| Unified Ledger | One structured record format for requests, decisions, sessions, risks, issues, and artifacts |
| Health Check | Validates required files, entry-file sync, hook helpers, gitkeep files, imports, safety, and platform junk |
| Agent Sync | Regenerates `CLAUDE.md` (required) and `GEMINI.md` (optional) from `AGENTS.md` |
| Utility Package | Small Python helpers for paths, atomic writes, env loading, API gating, records, manifests, QC, and review pages |
| Multi-Agent Entry Points | Tool-specific files all point back to the same shared contract |

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
├── GEMINI.md               # Optional Gemini CLI entry point
└── SETUP_NEW_MACHINE.md    # First-time setup guide
```

## Codex Hooks

Codex reads the shared entry point from `AGENTS.md`. For end-of-turn guarded commits, copy the `notify` example from `.codex/config.example.toml` into your user-level `~/.codex/config.toml` and replace the placeholder path with this repository's absolute path.

The notify script calls `python3 tools/project.py commit`, so it keeps the same allowlist and secret/temp/output protections as the Claude Code Stop hook. Codex does not currently use the Claude-style prompt-injection hook in this scaffold; run `python3 tools/hooks/panel_print.py` whenever you want the same status panel printed in a terminal.
