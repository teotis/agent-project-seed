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

## 2026-05-14T14:00:39 - Competitive positioning research

type: session
tags: positioning, github, promotion

summary:
- GitHub and web research found adjacent projects, but no exact match for a zero-dependency, copy-ready multi-agent governance scaffold with contract/state/ledger, safe commit, health check, and Codex/Claude/Gemini entry-point sync.
- Recommended positioning: lightweight project governance layer for AI coding agents, not a full agent framework or task orchestration system.

details:
- Adjacent projects include AGENTS.md instruction standard, agentkit-cli, agentseed, Microsoft Agentic Project Management, and general Claude/Gemini/Codex instruction-file practices.
- Strongest differentiators: single source of shared rules, unified structured ledger, safety-first commit allowlist, zero runtime dependencies, and multi-tool entry file generation.
- Promotion should avoid claiming no competitors; instead emphasize a narrow wedge: "turn any repo into a disciplined multi-agent workspace in minutes."

links:
- README.md

## 2026-05-14T14:11:25 - README simplified after feedback

type: artifact
tags: readme, simplification

summary:
- Simplified `README.md` to keep the overview concise and remove low-value detail.

details:
- Kept the homepage focused on positioning, quick start, core features, and a short comparison note.
- Removed longer explanatory sections that were better left to agent tooling or deeper documentation.

links:
- README.md
- AGENTS.md

## 2026-05-14T14:41:23 - Codex hook support added

type: artifact
tags: codex, hooks, git, panel

summary:
- Added Codex-friendly hook helpers for guarded end-of-turn commits and manual status panel printing.
- Updated agent entry sync, health checks, README guidance, and tests to cover Codex helper files.

details:
- `tools/hooks/codex_notify.py` reuses `tools/project.py commit` so Codex can share the same allowlist-based safe commit behavior as the Claude Code Stop hook.
- `.codex/config.example.toml` documents the user-level Codex notify configuration path.
- `tools/hooks/panel_print.py` exposes the existing panel generator for tools that cannot inject prompt context.

links:
- tools/hooks/codex_notify.py
- tools/hooks/panel_print.py
- .codex/config.example.toml

## 2026-05-14T14:03:35 - README repositioned for GitHub launch

type: artifact
tags: readme, promotion, positioning

summary:
- Reworked `README.md` into a GitHub-ready landing document focused on positioning, quick start, core workflow, differentiation, target users, and suggested topics.

details:
- Emphasized the project as a lightweight governance scaffold for AI-assisted repositories rather than an agent framework.
- Added comparison guidance against adjacent tools such as AGENTS.md, agentkit-style tooling, context generators, and heavier project-management frameworks.

links:
- README.md
