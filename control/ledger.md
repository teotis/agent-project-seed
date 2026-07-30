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

## 2026-07-10T05:07:42+0800 - Refresh portable skill snapshot and checkpoint safety

type: decision
status: closed
tags: scaffold, skills, codex, claude, safety

summary:
- Refreshed the portable skill bundle from the current local Codex and Claude installations.
- Reduced the default install profile to the high-frequency engineering core and added a drift audit command.
- Replaced Claude Stop auto-commit with the shared baseline-aware clean-checkpoint gate.

details:
- The manifest now distinguishes a 9-skill default profile from a 38-skill specialist snapshot; retired, unlisted Superpowers aliases were removed from the bundle.
- `tools/project.py audit-user-skills` reports synced, drifted, or missing installations before a forced replacement.
- The optional MCP policy was subsequently clarified in the Context7 retirement decision below.

links:
- reports/scaffold-health/2026-07-10-seed-architecture-review.html
- agent-assets/user-skills/manifest.json
- tools/project.py
- .claude/settings.json

## 2026-07-10T05:07:42+0800 - Retire Context7 as a seed prerequisite

type: decision
status: closed
tags: scaffold, mcp, documentation, optionality

summary:
- Do not prescribe Context7 as a standard MCP or setup check for copied projects.

details:
- MCP integrations are project-specific and must be selected only when a concrete external-data or documentation need justifies their permissions, credentials, and maintenance cost.
- The portable seed remains usable without an MCP server; projects may document an explicitly chosen integration later.

links:
- AGENTS.md
- README.md
- SETUP_NEW_MACHINE.md

## 2026-07-10T06:59:20+0800 - Make project intent and delivery evidence the default path

type: decision
status: closed
tags: scaffold, onboarding, user-value, handoff

summary:
- Goal-driven initialization now turns a brief or four terminal prompts into a shared project intent.
- Status panels now lead with user-goal status and delivery evidence before process metadata.

details:
- `init --brief` and `init --interactive` can capture target user, core problem, project goals, and acceptance criteria, then generate the corresponding project-facing context.
- A goal-defined project receives `control/delivery_receipt.md`; its acceptance checks, evidence, gaps, and next user decision are the handoff source shown by `tools/panel.py`.

links:
- tools/project.py
- tools/panel.py
- control/delivery_receipt.md
- README.md

## 2026-07-14T00:50:40+0800 - Analyze Trellis mechanisms for solo-first seed evolution

type: artifact
status: closed
tags: trellis, architecture, harness, solo-development

summary:
- Confirmed `mindfold-ai/Trellis` as the recently popular agent harness and assessed which mechanisms fit Project Seed.
- Recommended inheriting a curated context and knowledge-promotion loop through the existing optional complex-task surface, without adopting Trellis's collaboration platform by default.

details:
- The preferred structural candidate is a solo-first Work Packet that extends `control/tasks/` with curated context, task-aware breadcrumb, verification evidence, and a knowledge promotion review.
- Channel runtime, broad platform adapters, per-developer journals, mandatory task creation, and automatic session-record commits remain outside the default seed.
- Trellis is AGPL-3.0-only; any future implementation should use clean-room behavior contracts instead of copied source, templates, schemas, or skill prose.

links:
- reports/trellis-analysis/2026-07-14-trellis-primary-research.md
- reports/abstraction-architect/structural_abstraction_architect_report_20260714_0050.html

## 2026-07-14T01:15:00+0800 - Add solo-first Work Packets for complex tasks

type: decision
status: closed
tags: tasks, context, breadcrumb, knowledge-promotion

summary:
- Extended the optional complex-task control surface into a solo-first Work Packet.
- Added curated task context, worktree-scoped active-task breadcrumbs, and a lightweight knowledge-promotion review without adding a collaboration runtime.

details:
- `context.jsonl` uses one entry per repo-relative text file and stage (`plan`, `implement`, or `check`), with a required reason; `project.py check` validates the manifests.
- Active task state is stored under Git-private worktree-scoped storage and projected by the status panel as task, phase, next action, and first unchecked acceptance gap.
- `promotion.md` keeps long-term learning selective by routing candidates to tests/hooks/lint, module documentation, the ledger, task-local notes, or discard.
- The default path remains lightweight: routine tasks do not create or activate a Work Packet.

links:
- tools/project.py
- tools/panel.py
- README.md
- reports/abstraction-architect/structural_abstraction_architect_report_20260714_0050.html

## 2026-07-14T02:55:59+08:00 - Adapt project rules to stronger agent autonomy

type: decision
status: closed
tags: governance, agent-rules, safety, portability

summary:
- Classify the shared contract as hard invariants, mode contracts, user value priors, adaptive heuristics, and optional resources instead of one universal workflow.
- Keep the complete 38-Skill snapshot local while retaining the small recommended profile as the normal bootstrap.
- Preserve project-local authorization, privacy, integrity, truthful-state, and independence boundaries.

details:
- Code-changing tasks still require proportional verification and a local checkpoint or explicit blocked handoff; read-only tasks no longer manufacture full completion templates.
- Safe commit now expands untracked directories to file-level paths and blocks high-confidence secret patterns before staging.
- Claude project defaults allow read-only Git inspection and the guarded project commit command; raw mutating Git commands return to normal permission review.
- External API, upload, and cost effects retain environment plus explicit-authorization gating. Large local rewrites instead require explicit scope and rollback without an unrelated API environment flag.
- The Chinese HTML overview remains a project-facing asset; initialization updates and escapes its project identity, while preflight compares its managed capability block with the project-owned renderer.
- Migration baseline: local tag `rules-pre-adaptation-20260714` at `adb32070bdc18a47c502eecac8b2381e549dd26b`.

links:
- AGENTS.md
- README.md
- README.zh.html
- SETUP_NEW_MACHINE.md
- tools/project.py
- tests/test_project_tool.py
- agent-assets/user-skills/manifest.json

## 2026-07-30T00:00:00+08:00 - Keep Work Packets intent-triggered and delivery states separate

type: decision
status: closed
tags: workflow, work-packet, verification, delivery

summary:
- Enter a Work Packet only when the current user explicitly continues, resumes, or names it.
- Keep verification, handoff artifact generation, and external deployment as separate modes.
- Retain a lightweight seed: project-specific review surfaces or enforcement manifests remain opt-in.

details:
- An unrelated active Work Packet marker is background handoff context and must not take ownership of a new request.
- Verification may produce disposable local output but cannot imply handoff artifact creation, publication, installation, upload, or other external state change.
- The user accepted this boundary after a read-only comparison of current project practices.

links:
- AGENTS.md
- CONTEXT.md
- docs/adr/0001-intent-triggered-work-packets-and-delivery-states.md
