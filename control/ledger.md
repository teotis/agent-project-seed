# Ledger

Unified record ledger. Requirements, decisions, sessions, risks, issues, and artifacts are all appended here as Records.

## 2026-05-14T00:00:00 - Template initialized

type: decision
tags: scaffold, governance

summary:
- Use a unified ledger for long-term useful records.
- Do not create complex domain directories prematurely.

details:
- When a category of records naturally grows large, split into `control/ledger/YYYY-MM.md` or domain directories.

links:
- AGENTS.md

## 2026-06-23T12:47:23 - Record clean checkpoint design

type: decision
tags: codex, checkpoint, hooks, skills, worktree

summary:
- Document the clean-checkpoint-first design in explanatory project files.
- Prefer auditable local checkpoint commits over leaving mixed tracked dirty changes.

details:
- The recommended Codex App layering is: small `AGENTS.md` pointer, reusable skill for workflow, Stop hook for mechanical closeout checks, rules/permissions for dangerous commands, and worktrees for isolated fixes.
- The design is intentionally local-first: do not push unless the user explicitly asks for remote sync.
- `README.md` explains the design for scaffold readers; `SETUP_NEW_MACHINE.md` explains how to carry it into a new machine or copied project.

links:
- README.md
- SETUP_NEW_MACHINE.md
- codex://threads/019ef228-c9a3-7e12-975b-9d7644f5782d

## 2026-06-25T02:59:30 - Remove Gemini adapter from seed

type: decision
tags: agents, scaffold, gemini

summary:
- Keep the copied-project agent surface focused on Codex and Claude Code.
- Remove Gemini CLI entry-file generation and documentation from the seed.

details:
- `tools/project.py sync-agents` should regenerate only `CLAUDE.md` from `AGENTS.md`.
- Future project positioning should describe Codex and Claude Code support, not Gemini support.

links:
- README.md
- tools/project.py

## 2026-06-25T03:20:19 - Define lightweight status panel contract

type: decision
status: closed
tags: panel, hooks, ledger

summary:
- Status panels should be Chinese, compact, and triggered only for new-session entry or post-checkpoint handoff.
- Open requests, risks, and issues should use `status: open`; completed items should use `status: closed`.

details:
- The panel should read only stable project files and bounded git metadata, not scan the whole source tree or inspect large diffs.
- Each open group should show at most five deduplicated items.
- Git, worktree, branch, next-action, and risk lines should avoid repeating the same item in multiple places.

links:
- tools/panel.py
- .claude/hooks/panel_hook.py
- .codex/hooks.json
