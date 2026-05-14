# Agent Project Seed

Turn any repository into a disciplined workspace for AI coding agents.

Agent Project Seed is a copy-ready, zero-dependency scaffold for teams and solo builders who use Codex, Claude Code, Gemini CLI, or multiple AI agents in the same project. It does not try to be an agent framework. It gives your repository the boring but essential coordination layer: shared rules, current state, a structured ledger, health checks, safe commits, and synced entry files for different agent tools.

Most AI-agent setups stop at an instruction file. This project goes one layer deeper.

- One shared contract for all agents
- One current-state snapshot for handoff
- One structured ledger for decisions, risks, issues, sessions, and artifacts
- Safe commit tooling that refuses secrets, temp output, and unexpected paths
- Synced `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` entry points
- Python >= 3.9, no runtime dependencies

## Why This Exists

AI coding tools are getting good at isolated tasks, but projects still drift when every session starts from a different memory, prompt, or tool-specific convention.

Agent Project Seed is for the moment when you think:

- "I keep re-explaining the same project rules to every agent."
- "Claude, Codex, and Gemini should read the same source of truth."
- "I want lightweight project memory without adopting a heavy workflow system."
- "I need agents to leave useful records, not chat transcripts."
- "I want automatic guardrails before agent-made changes get committed."

## Quick Start

Clone or copy this repository, then initialize it for your project:

```bash
python3 tools/project.py init --name "Your Project Name"
```

Then fill in the project intent:

```bash
$EDITOR control/contract.md
```

Run the project check:

```bash
python3 tools/project.py check
```

If you change the shared rules, regenerate the agent entry files:

```bash
python3 tools/project.py sync-agents
```

## How It Works

The scaffold separates coordination from project work.

| Layer | Files | Purpose |
| --- | --- | --- |
| Governance | `control/contract.md` | Shared rules, project goals, non-goals, acceptance criteria |
| Handoff | `control/state.md` | Short current-state snapshot for the next agent or session |
| Memory | `control/ledger.md` | Structured records for requests, decisions, sessions, risks, issues, and artifacts |
| Work Area | `work/in`, `work/out`, `work/tmp` | Inputs, final artifacts, and disposable temporary files |
| Tooling | `tools/project.py`, `tools/panel.py` | Init, checks, sync, safe commits, and status panel generation |
| Agent Entrypoints | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` | Tool-specific files that point back to the shared contract |

## What You Get

| Feature | Description |
| --- | --- |
| Shared Contract | `control/contract.md` is the single source of truth for collaboration rules. |
| Unified Ledger | Requirements, decisions, risks, issues, sessions, and artifacts use the same readable record format. |
| Current State | `control/state.md` keeps handoffs short, concrete, and easy to update. |
| Safe Commit | `project.py commit` stages only allowlisted paths and rejects `.env`, temp files, generated outputs, conflicts, and surprise paths. |
| Health Check | `project.py check` validates required files, agent sync, package imports, Claude hook files, gitkeep files, and tracked platform junk. |
| Agent Sync | `project.py sync-agents` regenerates `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` from the shared contract. |
| Status Panel | `tools/panel.py` reports project status, ledger count, git status, package name, goal, and next action. |
| Claude Hooks | Example Claude Code hooks can inject the status panel and run safe checkpoints. |
| Utility Package | `src/base_scaffold/` includes path helpers, atomic writes, env loading, API gating, records, manifests, QC helpers, and review-page utilities. |

## Example Ledger Record

```text
## 2026-05-14T14:00:39 - Competitive positioning research

type: session
tags: positioning, github, promotion

summary:
- Found adjacent projects, but no exact match for this lightweight governance scaffold.

details:
- Position as a copy-ready project coordination layer, not an agent framework.

links:
- README.md
- control/contract.md
```

## What Makes It Different

Agent Project Seed is intentionally small. It is not trying to orchestrate agents, replace your issue tracker, run a background swarm, or invent a new project-management religion.

| If you need... | Use... |
| --- | --- |
| A standard instruction file for coding agents | `AGENTS.md` |
| Generated or linted agent instruction files | `agentkit-cli` or similar tooling |
| Automatic repo context generation | `agentseed` or similar context generators |
| Heavy multi-agent project management | A full agentic project-management framework |
| A copy-ready repo governance layer for AI-assisted work | Agent Project Seed |

The wedge is simple:

> One repo, many agents, one shared operating record.

## Directory Layout

```text
.
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

## Commands

```bash
# Validate the scaffold
python3 tools/project.py check

# Initialize after copying
python3 tools/project.py init --name "Your Project Name"

# Regenerate AGENTS.md, CLAUDE.md, and GEMINI.md
python3 tools/project.py sync-agents

# Commit only safe, allowlisted changes
python3 tools/project.py commit --message "chore: checkpoint agent work"

# Run tests
python3 -m pytest
```

The same commands are available through `make`:

```bash
make preflight
make test
make sync-agents
```

## Good Fit

- Repositories worked on by more than one AI coding tool
- Long-running solo projects where agent memory matters
- Teams that want lightweight rules before adopting heavier process
- Content, data, research, automation, and software projects with repeatable handoffs
- Projects where generated artifacts, temp files, and secrets must stay out of commits

## Not A Good Fit

- You only need a single static prompt file
- You want a hosted dashboard or SaaS workflow
- You need autonomous agent scheduling or task execution
- You want a full replacement for GitHub Issues, Linear, Jira, or your existing PM stack

## Design Principles

- Keep the source of truth in plain text.
- Make records useful for future agents, not verbose for their own sake.
- Prefer small, inspectable scripts over framework lock-in.
- Guard commits by default.
- Let project structure grow only when the work actually needs it.

## Requirements

- Python >= 3.9
- Git recommended
- No runtime dependencies

Tests use `pytest`:

```bash
python3 -m pip install -e ".[test]"
python3 -m pytest
```

## Suggested GitHub Topics

`ai-agents`, `codex`, `claude-code`, `gemini-cli`, `agents-md`, `agentic-coding`, `project-template`, `developer-tools`, `multi-agent`, `python`

## License

Add your preferred license before publishing broadly.
