# Agent Project Seed

A copy-and-use multi-agent collaboration project scaffold. One command to initialize, and you get a named, checkable, paneled, rule-governed project with safe commits.

- Python >= 3.9, zero external dependencies
- Supports Codex / Claude Code / Gemini CLI

## Who Is This For

- Teams using AI agents for development who need unified engineering discipline
- Multi-agent codebases
- Lightweight projects that need structured tracking of requirements, decisions, and risks

> Clone the repo, open Claude Code / Codex / Gemini CLI — the panel will automatically prompt you to initialize. No extra steps needed.

## Panel

A project status panel is automatically injected at the start of every Claude Code conversation.

```
[Your Project] 2026-05-14 (Wed)
Status: Initialized, goals pending
Git: clean | Ledger: 2 records | Package: your_pkg
Goal: Project goal
Next: Edit Current Intent in control/contract.md
```

Three status levels:
- **Seed Template** — `init` has not been run yet
- **Initialized, goals pending** — `init` has been run, but goals in `contract.md` have not been edited
- **Ready** — Goals have been customized

Verify the panel manually:

```bash
python3 tools/panel.py
```

## Commands

| Command | Description |
|---------|-------------|
| `python3 tools/project.py init --name "name"` | Initialize project |
| `python3 tools/project.py check` | Health check (files, sync, panel, consistency) |
| `python3 tools/project.py sync-agents` | Regenerate entry files from contract.md |
| `python3 tools/project.py commit --message "type: msg"` | Safe commit |
| `python3 tools/project.py commit --dry-run` | Preview which files would be committed |
| `python3 tools/panel.py` | View panel output manually |

## Safe Commit Mechanism

The `commit` command only allows committing whitelisted files (`control/`, `tools/`, `src/`, `tests/`, etc.). It automatically rejects:

- Files in `.env`, `work/tmp/`, `work/out/`
- Files not in the allowlist

Claude Code's Stop hook automatically attempts a safe commit at the end of each conversation. See `.claude/settings.example.json` for configuration.

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

## Python Utility Package

`src/base_scaffold/` provides reusable foundational capabilities:

- **core** — Path management, atomic file writes, environment variable loading, API gating
- **records** — `Record` / `Ledger` unified records, `Manifest` artifact manifest, `QCResult` quality checks
- **review** — Generate HTML review pages (image/link review)

Test dependencies: `python3 -m pip install -e ".[test]"`

## Troubleshooting

**Panel shows "Seed Template"**
→ Run `python3 tools/project.py init --name "your-project-name"`

**Panel shows "goals pending"**
→ Edit Current Intent in `control/contract.md` and remove the "initialized, goals pending" marker

**check reports "agent entry files not synced"**
→ Run `python3 tools/project.py sync-agents`

**check reports "platform junk files tracked"**
→ Run `git rm --cached ._filename` and confirm `.gitignore` contains `._*`

**check reports "missing .gitkeep"**
→ Run `touch work/in/.gitkeep work/out/.gitkeep work/tmp/.gitkeep`

## Agent Usage Rules

- Before starting a task, read in order: `contract.md` → `state.md` → `ledger.md` → task-related files
- Requirements, decisions, risks, etc. are recorded as `Record` entries appended to `ledger.md`
- At the end of each logical task: run `check` → commit → record risks → provide next steps
- External API calls require both environment variable enablement and explicit user authorization
- When conflicts cannot be auto-resolved, write to `ledger.md` and wait for user decision
