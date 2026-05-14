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
- A lightweight status panel for Claude Code hooks

## Quick Start

```bash
python3 tools/project.py init --name "Your Project Name"
python3 tools/project.py check
```

Then edit:

```text
control/contract.md
```

When shared rules change:

```bash
python3 tools/project.py sync-agents
```

## What's Included

| Feature | Description |
| --- | --- |
| Status Panel | Shows project status, git status, ledger count, goal, and next action |
| Safe Commit | Whitelist-based commit command for agent-made changes |
| Unified Ledger | One structured record format for requests, decisions, sessions, risks, issues, and artifacts |
| Health Check | Validates required files, entry-file sync, hooks, gitkeep files, imports, and platform junk |
| Agent Sync | Regenerates `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` from `control/contract.md` |
| Utility Package | Small Python helpers for paths, atomic writes, env loading, API gating, records, manifests, QC, and review pages |
| Multi-Agent Entry Points | Tool-specific files all point back to the same shared contract |

## Positioning

Use `AGENTS.md` if you only need one instruction file. Look at agentkit-style tools if you want instruction generation or linting. Look at agentseed-style tools if you want automatic context generation. Use Agent Project Seed when you want a small repo-level governance layer that keeps multiple AI coding tools aligned.

## Directory Layout

```text
├── control/
│   ├── contract.md         # Shared rules and project intent
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
├── .claude/
│   ├── hooks/panel_hook.py
│   └── settings.example.json
├── AGENTS.md
├── CLAUDE.md
└── GEMINI.md
```
