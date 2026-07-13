@AGENTS.md

# Claude Code adapter

This repository uses `AGENTS.md` as the shared source of truth for AI coding agents.

Claude Code-specific notes:

- Follow `AGENTS.md` first.
- Keep this file short and Claude-specific.
- Do not duplicate shared project rules here.
- When a repeated mistake is discovered, suggest whether it should become a hook, test, lint rule, or CI check instead of adding another reminder here.
- The project-level Claude Stop hook uses the same baseline-aware clean-checkpoint gate as Codex; agents create the local commit deliberately after review.
