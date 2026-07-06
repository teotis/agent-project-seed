# Ledger

Unified record ledger. Requirements, decisions, sessions, risks, issues, and artifacts are all appended here as Records.

## 2026-05-14T00:00:00 - Template initialized

type: decision
tags: scaffold, governance

summary:
- Use a unified ledger for long-term useful records.
- Do not create complex domain directories prematurely.

details:
- When a category of records naturally grows large, split `control/ledger.md` into monthly or domain-specific files.
- Copied projects should keep project-specific decisions here, but should not store complete chat logs, credentials, raw private data, or machine-local paths.

links:
- AGENTS.md

## 2026-07-06T00:00:00+0800 - Keep seed ledger public-clean

type: decision
status: closed
tags: public-release, scaffold, ledger

summary:
- Keep the seed repository ledger as a clean starter artifact instead of publishing local development-session records.
- Treat historical seed development notes and generated analysis reports as non-essential to copied-project bootstrap.

details:
- `tools/project.py init` continues to reset `control/ledger.md` for copied projects.
- Public seed history should explain the ledger format without carrying internal thread links, local report paths, or machine-specific context.

links:
- README.md
- tools/project.py
