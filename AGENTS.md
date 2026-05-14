# Repository Instructions

<!-- Generated from control/contract.md. Do not edit directly. -->

Shared engineering rules are in:

`control/contract.md`

Codex should read this file before starting a task, then read `control/state.md`, `control/ledger.md`, and task-related files.

## Codex Notes

- After modifying shared rules, run `python3 tools/project.py sync-agents`.
- `AGENTS.md` is the Codex entry point; do not copy shared rules into this file.
- For guarded end-of-turn commits in Codex, copy `.codex/config.example.toml` into your user `~/.codex/config.toml` and update the absolute path.
