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
