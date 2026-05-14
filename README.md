# Agent Project Seed

A copy-and-use multi-agent collaboration project scaffold. Clone it, open your AI coding tool, and the panel guides you through initialization — no manual setup required.

- Python >= 3.9, zero external dependencies
- Supports Codex / Claude Code / Gemini CLI

## Who Is This For

- Teams using AI agents for development who need unified engineering discipline
- Multi-agent codebases that require structured coordination
- Lightweight projects that need structured tracking of requirements, decisions, and risks

## What's Included

| Feature | Description |
|---------|-------------|
| Status Panel | Auto-injected into every Claude Code conversation. Three levels: Seed Template → Initialized, goals pending → Ready |
| Safe Commit | Whitelist-based commit command. Rejects `.env`, `work/tmp/`, `work/out/`, and anything outside the allowlist |
| Unified Ledger | All requirements, decisions, risks, and artifacts recorded as structured `Record` entries in `control/ledger.md` |
| Health Check | `project.py check` validates files, sync, panel, hook, gitkeep, and platform junk |
| Agent Sync | `project.py sync-agents` regenerates `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` from the single source of truth in `control/contract.md` |
| Python Utility Package | `src/base_scaffold/` — path management, atomic writes, env loading, API gating, record/ledger/manifest/QC, HTML review pages |
| Multi-Agent Entry Points | Platform-specific entry files (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) all point to the shared contract |
| Auto Checkpoint | Stop hook runs safe commit at the end of each conversation |

## Directory Layout

```
├── control/                # Governance layer
│   ├── contract.md         # Single source of shared rules
│   ├── ledger.md           # Unified record ledger
│   └── state.md            # Current state snapshot
├── work/                   # Work layer
│   ├── in/                 # Input materials
│   ├── out/                # Final artifacts (not committed)
│   └── tmp/                # Temporary files (not committed)
├── tools/
│   ├── project.py          # Init, check, sync, safe commit
│   └── panel.py            # Panel generator
├── src/
│   └── base_scaffold/      # Python utility package
├── tests/                  # Tests
├── .claude/
│   ├── hooks/panel_hook.py # Panel injection hook
│   └── settings.example.json
├── AGENTS.md               # Codex entry point
├── CLAUDE.md               # Claude Code entry point
└── GEMINI.md               # Gemini CLI entry point
```
