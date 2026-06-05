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

### Ledger rule

Requirements, decisions, risks, sessions, conflicts, and artifacts are appended to `control/ledger.md` as `Record` entries. Unified format:

```text
## YYYY-MM-DDTHH:MM:SS - short title

type: request | decision | session | risk | issue | artifact
tags: tag-a, tag-b

summary:
- ...

details:
- ...

links:
- path/or/url
```

Only record facts useful for the project's future. Do not save complete chat logs, keys, or raw private data.

### Conflict rule

When conflicts cannot be auto-resolved, append `type: issue` to `control/ledger.md`. After the user or an authoritative file resolves it, append `type: decision`. Do not create the illusion of resolution by silently rewriting.

## Validation

```bash
# Project preflight check
make preflight          # runs: python3 tools/project.py check

# Run tests
make test               # runs: python3 -m pytest
```

## Coding conventions

- Git is used by default. Before each logical task ends:
  1. Run `python3 tools/project.py check` or equivalent verification.
  2. Review changes, commit only files relevant to this round.
  3. Use `python3 tools/project.py commit --message "type: summary"` for assisted safe commits.
  4. Do not commit `.env`, `work/tmp/`, formal outputs in `work/out/`, large caches, or secrets.
  5. Do not push unless the user explicitly requests it.

## Architecture notes

```
control/contract.md → deleted (content merged here)
control/ledger.md   — Unified record ledger
control/state.md    — Current state snapshot
work/in/            — Input materials
work/out/           — Final artifacts and manifest
work/tmp/           — Temporary files, not committed
tools/project.py    — Initialization, preflight checks, sync, safe commits
src/                — Minimal general-purpose utilities
```

### Optional capabilities

The following do not have pre-built directories; generate them when needed:

- data lifecycle: CSV/JSONL state tables, schema, sync scripts
- content pipeline: draft/approved layering, publish gating, conflict resolution
- image generation: provider, queue, manifest, cost gating
- html delivery: Markdown + self-contained HTML dual delivery

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
- After modifying shared rules, run `python3 tools/project.py sync-agents`.
- For guarded end-of-turn commits in Codex, copy `.codex/config.example.toml` into your user `~/.codex/config.toml` and update the absolute path.
