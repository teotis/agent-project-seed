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

## 2026-06-25T03:31:15 - Treat init as project workspace transition

type: decision
status: closed
tags: init, residue-check, project-setup

summary:
- Initialization should turn a copied template into a new project workspace, not leave project-facing seed history behind.
- Project-facing files should be rewritten or checked so seed names, development records, and private thread links do not leak into the initialized project.

details:
- `tools/project.py init` rewrites README, AGENTS overview/state, resets the ledger, renames the package, activates settings, and writes an initialization manifest.
- `tools/project.py check` rejects obvious seed residue in initialized project-facing files.

links:
- tools/project.py
- README.md
- SETUP_NEW_MACHINE.md

## 2026-06-25T04:04:16 - Bundle portable user skills for environment bootstrap

type: decision
status: closed
tags: skills, bootstrap, codex, claude

summary:
- Carry selected user-installed skills in the seed so a cloned project can quickly rebuild a useful Codex or Claude environment.
- Treat skills as universal packages; install targets only choose the destination user skill root.

details:
- Store portable skill snapshots under `agent-assets/user-skills/`, governed by `agent-assets/user-skills/manifest.json`.
- Include a core migration set, the selected optional analysis/refinement set, and the complete local superpowers skill set.
- Provide `tools/project.py list-user-skills` and `tools/project.py install-user-skills` for inspection and installation.
- Do not migrate private machine-local config, API keys, MCP tokens, model provider settings, conversation logs, hook state, caches, or database files.

links:
- agent-assets/user-skills/manifest.json
- tools/project.py
- SETUP_NEW_MACHINE.md

## 2026-06-25T04:08:29 - Record Context7 MCP and checkpoint gate purpose

type: decision
status: closed
tags: mcp, context7, hooks, checkpoint

summary:
- Treat Context7 as the standard documentation MCP to verify when bootstrapping Codex and Claude environments.
- Explain the `clean-checkpoint-first` hook as a dirty-workspace closeout guard, not an auto-commit mechanism.

details:
- New-machine setup should verify Context7 with `codex mcp get context7` and `claude mcp get context7`.
- Context7 configuration, API keys, MCP tokens, and provider credentials remain user-level machine configuration, not project files.
- The checkpoint hook records a tracked dirty baseline and blocks Stop only when a session leaves additional tracked dirty files without a local checkpoint or explicit blocked handoff.

links:
- README.md
- SETUP_NEW_MACHINE.md
- AGENTS.md

## 2026-06-25T03:32:29 - Record project positioning

type: decision
status: closed
tags: positioning, init, template

summary:
- This repository is positioned as a GitHub-cloned project starter that helps a user create a clean new project workspace on a fresh machine.
- Its core promise is not only to provide agent collaboration tooling, but to initialize, rename, scrub template residue, and point the user to remaining project-specific edits.

details:
- A fresh clone should first guide the user to run initialization.
- Initialization should update names, project-facing docs, state, ledger, and package paths; it should record what changed and what still needs review.
- Project-facing checks should prevent stale seed names, seed development history, private thread links, or template-only instructions from leaking into the initialized project.
- Future changes should be judged against this positioning: make the template easier to convert into a clean user project, not merely easier to develop as the seed repo itself.

links:
- AGENTS.md
- README.md
- SETUP_NEW_MACHINE.md
- tools/project.py

## 2026-06-25T04:05:36 - Add optional complex task live state

type: decision
status: closed
tags: task-state, orchestration, template

summary:
- Keep the default initialized project lightweight.
- Add an opt-in `tools/project.py task init` command for complex multi-package work that needs a live state source of truth.

details:
- Complex task state is generated under `control/tasks/<slug>/` only when explicitly requested.
- The generated `status.tsv` owns package execution state; chat summaries, status panels, and final reports are secondary when they disagree.
- This preserves the OpenCamera orchestration lesson without defaulting new projects into a heavy `docs/plans/*/packages/status/launchers` layout.

links:
- tools/project.py
- README.md
- SETUP_NEW_MACHINE.md

## 2026-06-25T04:14:56 - Enable project-level clean checkpoint hook by default

type: decision
status: closed
tags: checkpoint, codex, hooks, init

summary:
- Initialized projects should automatically carry the clean-checkpoint Stop gate.
- The seed should preserve the OpenCamera lesson that new tracked dirty code must not quietly remain after agent work.

details:
- `.codex/hooks.json` should include SessionStart, PostToolUse, and Stop commands for `.codex/hooks/clean_checkpoint_first.py`.
- The hook records the tracked dirty baseline at session start and blocks Stop only for new tracked dirty paths beyond that baseline.
- The default hook must not auto-commit, push, delete, or rewrite files; optional notify-based assisted commits remain user-level configuration.

links:
- .codex/hooks.json
- .codex/hooks/clean_checkpoint_first.py
- tools/project.py

## 2026-06-25T04:28:52 - Add Windows bootstrap path

type: decision
status: closed
tags: windows, bootstrap, template

summary:
- The seed must support fresh Windows environments alongside macOS/Linux.
- New-project setup docs and agent hook examples should not assume `python3`, `make`, `cp`, `~/.codex`, or Unix-style absolute paths are available.

details:
- Provide Windows PowerShell command equivalents using `py -3`, `Copy-Item`, and `%USERPROFILE%\.codex`.
- Keep existing macOS/Linux examples, but add Windows-specific Codex and Claude example config files instead of forcing one mixed-platform command.
- Preflight should require the Windows example files so future template edits do not silently regress new-machine setup.

links:
- README.md
- SETUP_NEW_MACHINE.md
- AGENTS.md
- .codex/config.windows.example.toml
- .codex/hooks.windows.json
- .claude/settings.windows.example.json

## 2026-06-25T04:51:39 - Add lightweight agent task planner skill

type: decision
status: closed
tags: skills, planning, orchestration, bootstrap

summary:
- Add `agent-task-planner` as a core portable user skill for lightweight repo-backed task planning.
- Position it before `agent-orchestration-planner`: default to direct, single-agent, small-parallel, or manual task packs; upgrade only when a durable orchestration control plane is required.

details:
- The skill generates a lightweight task pack with `TASK_PLAN.md`, `AGENT_PROMPTS.md`, `status.tsv`, and `HANDOFF.md`.
- It keeps runtime scheduling, signed state, retry/finalize, launcher wrappers, and automatic cleanup out of scope.
- The seed carries the skill under `agent-assets/user-skills/core/` so fresh Codex or Claude environments can install it during bootstrap.

links:
- agent-assets/user-skills/core/agent-task-planner/SKILL.md
- agent-assets/user-skills/core/agent-task-planner/references/task-plan-contract.md
- agent-assets/user-skills/manifest.json
