# AGENTS.md

This file is the shared source of truth for AI coding agents working in this repository.

## Current Intent

**Project**: Agent Project Seed
**Status**: Seed Template — copy this scaffold to start a new project.

## Project overview

A copy-and-use lightweight project scaffold. Ships with minimal structure for multi-agent collaboration. Python 3.9+, toolchain via `tools/project.py`.

## How to work in this repository

- Read this file before making changes.
- Inspect nearby code before editing.
- Prefer small, focused changes.
- Do not invent commands, dependencies, or conventions.
- Preserve existing project style unless there is a clear reason to change it.

### Reading order

Before starting a task, read:

1. `AGENTS.md` (this file)
2. `control/state.md`
3. Recent records in `control/ledger.md` related to the task
4. Files directly involved in the current task

### Task completion

Every task completion must include:

- This round's results
- Modified/new files
- Risk points
- Suggested next steps

If there are no new risks, explicitly write "No new risks found." Next steps must be concrete, actionable items.

If the task produced a patch that was committed or otherwise merged into git, start the completion reply with the compact handoff status panel from `python3 tools/panel.py --mode handoff` on macOS/Linux or `py -3 tools/panel.py --mode handoff` on Windows, then summarize the change.

### Ledger rule

Requirements, decisions, risks, sessions, conflicts, and artifacts are appended to `control/ledger.md` as `Record` entries. Unified format:

```text
## YYYY-MM-DDTHH:MM:SS - short title

type: request | decision | session | risk | issue | artifact
status: open | closed  # optional; use for active requests, risks, and issues
tags: tag-a, tag-b

summary:
- ...

details:
- ...

links:
- path/or/url
```

Only record facts useful for the project's future. Do not save complete chat logs, keys, or raw private data. Use `status: open` for unfinished requests, risks, and issues that should appear in the status panel; switch to `status: closed` when they are done or no longer relevant.

### Conflict rule

When conflicts cannot be auto-resolved, append `type: issue` to `control/ledger.md`. After the user or an authoritative file resolves it, append `type: decision`. Do not create the illusion of resolution by silently rewriting.

## Validation

```bash
# Project preflight check
make preflight          # runs: python3 tools/project.py check

# Run tests
make test               # runs: python3 -m pytest
```

Windows PowerShell equivalents:

```powershell
py -3 tools/project.py check
py -3 -m pytest
```

## Coding conventions

- Git is used by default. Before each logical task ends:
  1. Run `python3 tools/project.py check` (`py -3 tools/project.py check` on Windows) or equivalent verification.
  2. Review changes, commit only files relevant to this round.
  3. Use `python3 tools/project.py commit --message "type: summary"` (`py -3 tools/project.py commit --message "type: summary"` on Windows) for assisted safe commits.
  4. Do not commit `.env`, `work/tmp/`, formal outputs in `work/out/`, large caches, or secrets.
  5. Do not push unless the user explicitly requests it.
- Initialized projects include a project-level Codex clean-checkpoint hook in
  `.codex/hooks.json`. It blocks Stop if the current session leaves new tracked
  dirty changes beyond the session-start baseline; close out with a local
  checkpoint commit or an explicit blocked handoff.

## Architecture notes

```
control/contract.md → deleted (content merged here)
control/ledger.md   — Unified record ledger
control/state.md    — Current state snapshot
reports/            — Durable analysis reports and review artifacts
work/in/            — Input materials
work/out/           — Final artifacts and manifest
work/tmp/           — Temporary files, not committed
tools/project.py    — Initialization, preflight checks, sync, safe commits
src/                — Minimal general-purpose utilities
```

### Optional capabilities

The following do not have pre-built directories; generate them when needed:

- data lifecycle: CSV/JSONL state tables, schema, sync scripts
- complex task live state: generate `control/tasks/<slug>/status.tsv` with `python3 tools/project.py task init` (`py -3 tools/project.py task init` on Windows) when work spans multiple packages, worktrees, agents, or handoff sessions
- content pipeline: draft/approved layering, publish gating, conflict resolution
- image generation: provider, queue, manifest, cost gating
- html delivery: Markdown + self-contained HTML dual delivery
- governance lifecycle: generate `control/governance.md` with `python3 tools/project.py governance init` (`py -3 tools/project.py governance init` on Windows) when rules, verification scripts, reports, or agent workflows need explicit keep/defer/retire decisions

## Generated files

No auto-generated files in this scaffold project.

## Security

- Any external API call, cost-incurring operation, material upload, or large-scale rewrite must satisfy both:
  - Environment variable explicitly enabled.
  - CLI argument or explicit user authorization in this session.
- API keys may only come from environment variables or `.env`.
- `.env` is git-ignored, never commit it.

## Agent-specific adapters

- Claude Code should read `CLAUDE.md`, which points back to this file.
- Codex app should use this `AGENTS.md` as the shared project instruction file.
- After modifying shared rules, run `python3 tools/project.py sync-agents` (`py -3 tools/project.py sync-agents` on Windows).
- Portable user skills live under `agent-assets/user-skills/` and are governed by `agent-assets/user-skills/manifest.json`; after changing that bundle, run `python3 tools/project.py check` (`py -3 tools/project.py check` on Windows).
- Context7 is the standard documentation MCP to verify for new environments with `codex mcp get context7` and `claude mcp get context7`.
- Project-level Codex hooks in `.codex/hooks.json` provide the status panel and clean-checkpoint Stop gate after initialization.
- For optional guarded end-of-turn commits in Codex, copy `.codex/config.example.toml` into `~/.codex/config.toml` on macOS/Linux, or `.codex/config.windows.example.toml` into `%USERPROFILE%\.codex\config.toml` on Windows, and update the absolute path.
