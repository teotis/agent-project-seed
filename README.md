# Base Project

This directory is a copy-ready starter project for Codex, Claude Code, Gemini CLI, and other agent-assisted workflows.

## Quick Start

```bash
cp -R base_project my_new_project
cd my_new_project
python3 tools/project.py init --name "My New Project"
python3 tools/project.py check
```

By default `tools/project.py init` initializes a Git repository and creates an initial commit. Use `--no-git` only when the project will be embedded into an existing repository.

## Core Habits

- Shared agent rules live in `control/contract.md`.
- `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` are thin entry files generated from the shared contract.
- User requirements, decisions, risks, sessions, issues, and artifacts go to `control/ledger.md`.
- Each logical task should end with a precise Git commit, a risk note, and a concrete next action.
