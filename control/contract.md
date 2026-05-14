# Project Contract

This file is the single source of shared rules for multi-agent collaboration in this repository. `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` are platform entry points that only point to this file.

## Project Shape

This is a copy-and-use lightweight project scaffold. It ships with only the minimum structure:

- `control/contract.md`: Rules, goals, working methods, optional capability checklist.
- `control/ledger.md`: Unified record ledger for requirements, decisions, sessions, risks, issues, artifacts.
- `control/state.md`: Current state snapshot for easy handoff.
- `work/in/`: Input materials.
- `work/out/`: Final artifacts and manifest.
- `work/tmp/`: Temporary files, not committed.
- `tools/project.py`: Initialization, preflight checks, sync entry points, safe commits.
- `src/`: Minimal general-purpose utilities.

## Current Intent

After copying this scaffold, update this section and `control/state.md` first. Specify project goals, non-goals, and acceptance criteria. Do not create domain directories prematurely; let them split out naturally when a category of materials grows.

## Reading Order

Before starting a task, read:

1. `control/contract.md`
2. `control/state.md`
3. Recent records in `control/ledger.md` related to the task
4. Files directly involved in the current task

## Ledger Rule

Requirements, decisions, risks, sessions, conflicts, and artifacts are all written as `Record` entries and appended to `control/ledger.md`. Unified format:

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

## Git Rule

Git is used by default. Before each logical task ends:

1. Run `python3 tools/project.py check` or equivalent verification.
2. Review changes, commit only files relevant to this round.
3. Use `python3 tools/project.py commit --message "type: summary"` for assisted safe commits.
4. Do not commit `.env`, `work/tmp/`, formal outputs in `work/out/`, large caches, or secrets.
5. Do not push unless the user explicitly requests it.

## External Capability Gate

Any external API call, cost-incurring operation, material upload, or large-scale rewrite must satisfy both:

- Environment variable explicitly enabled.
- CLI argument or explicit user authorization in this session.

API keys may only come from environment variables or `.env`.

## Optional Capabilities

The following capabilities do not have pre-built directories; generate them when needed:

- data lifecycle: CSV/JSONL state tables, schema, sync scripts.
- content pipeline: draft/approved layering, publish gating, conflict resolution.
- image generation: provider, queue, manifest, cost gating.
- html delivery: Markdown + self-contained HTML dual delivery.

## Conflict Rule

When conflicts cannot be auto-resolved, append `type: issue` to `control/ledger.md`. After the user or an authoritative file resolves it, append `type: decision`. Do not create the illusion of resolution by silently rewriting.

## Final Response Rule

Every task completion must include:

- This round's results
- Modified/new files
- Risk points
- Suggested next steps

If there are no new risks, explicitly write "No new risks found." Next steps must be concrete, actionable items.
