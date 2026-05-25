# Agent Project Seed

A copy-and-use multi-agent collaboration scaffold. Clone it, initialize once, and give Codex, Claude Code, and Gemini CLI the same project rules, state, and record trail.

- Python >= 3.9, zero runtime dependencies
- Supports Codex / Claude Code / Gemini CLI
- Plain-text governance: no database, no hosted service, no agent framework

## Why Use It

AI agents work better when they share the same operating context. This scaffold gives a repository:

- A shared contract for project rules, goals, and acceptance criteria
- A current-state snapshot for handoff between sessions and agents
- A structured ledger for requirements, decisions, risks, issues, and artifacts
- Safe commit tooling that rejects secrets, temp files, generated outputs, and unexpected paths
- Synced `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` entry points
- A lightweight status panel for Claude Code hooks and Codex-friendly helper commands

## What's Included

| Feature | Description |
| --- | --- |
| Status Panel | Shows project status, git status, ledger count, goal, and next action |
| Safe Commit | Whitelist-based commit command for agent-made changes |
| Unified Ledger | One structured record format for requests, decisions, sessions, risks, issues, and artifacts |
| Health Check | Validates required files, entry-file sync, Claude/Codex hook helpers, gitkeep files, imports, and platform junk |
| Agent Sync | Regenerates `CLAUDE.md` and `GEMINI.md` from `AGENTS.md` |
| Utility Package | Small Python helpers for paths, atomic writes, env loading, API gating, records, manifests, QC, and review pages |
| Multi-Agent Entry Points | Tool-specific files all point back to the same shared contract |

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
│   └── panel.py            # Status panel generator
├── src/
│   └── base_scaffold/      # Small reusable Python utilities
├── tests/
├── .codex/
│   └── config.example.toml
├── .claude/
│   ├── hooks/panel_hook.py
│   └── settings.example.json
├── AGENTS.md
├── CLAUDE.md
└── GEMINI.md
```

## Codex Hooks

Codex reads the shared entry point from `AGENTS.md`. For end-of-turn guarded commits, copy the `notify` example from `.codex/config.example.toml` into your user-level `~/.codex/config.toml` and replace the placeholder path with this repository's absolute path.

The notify script calls `python3 tools/project.py commit`, so it keeps the same allowlist and secret/temp/output protections as the Claude Code Stop hook. Codex does not currently use the Claude-style prompt-injection hook in this scaffold; run `python3 tools/hooks/panel_print.py` whenever you want the same status panel printed in a terminal.
