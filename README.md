# Agent Project Seed

A copy-and-use multi-agent collaboration project scaffold. One command to initialize, and you get a named, checkable, paneled, rule-governed project with safe commits.

- Python >= 3.9, zero external dependencies
- Supports Codex / Claude Code / Gemini CLI

## Who Is This For

- Teams using AI agents for development who need unified engineering discipline
- Multi-agent codebases
- Lightweight projects that need structured tracking of requirements, decisions, and risks

## 5-Minute Quick Start

**Option 1: GitHub Template (Recommended)**

1. Click "Use this template" on the repository page to create a new repo
2. Clone the new repo locally
3. Run initialization:

```bash
python3 tools/project.py init --name "your-project-name"
python3 tools/project.py check
```

**Option 2: Local Copy**

```bash
cp -R agent_project_seed my_new_project
cd my_new_project
python3 tools/project.py init --name "your-project-name"
```

**Option 3: Direct Clone (Not Recommended)**

```bash
git clone <repo> my_new_project
cd my_new_project
rm -rf .git
python3 tools/project.py init --name "your-project-name"
```

> Cloning without deleting `.git` means the remote still points to the seed repo.

## What You Get After Initialization

`init` automatically completes:

| Step | Description |
|------|-------------|
| Text replacement | Project name, package name, slug replaced across all files |
| Package rename | `src/base_scaffold/` → `src/your_package_name/` |
| Update contract.md | Current Intent populated with project name and pending status |
| Update state.md | Records project name, package name, initialization time |
| Append ledger.md | Adds a `type: decision` initialization record |
| Activate settings | Copies `.claude/settings.example.json` → `settings.json` |
| Git init | Creates repo and initial commit (`--no-git` to skip) |

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

## Required Steps After Initialization

After running `init`, edit the `Current Intent` section in `control/contract.md` to specify:

1. Project goals
2. Non-goals
3. Acceptance criteria

Once complete, the panel status will change from "goals pending" to "ready".

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
