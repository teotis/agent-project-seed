# AGENTS.md

This file is the project-local source of truth for AI coding agents. It keeps
the portable safety core inside the repository while allowing task-specific
workflows to adapt to risk, scope, and active modes.

## Current Intent

**Project**: Agent Project Seed
**Status**: Seed Template — copy this scaffold to start a new project.

## Project overview

A copy-and-use lightweight project scaffold for agent-assisted work. Python
3.9+, zero runtime dependencies, with optional Codex and Claude Code adapters.

## Rule Hardness Model

The five sections below classify rule force. They are not a five-step
workflow.

1. **Hard invariants** protect authorization, privacy, user work, truthful
   evidence, and project independence; they never weaken for convenience.
2. **Mode contracts** apply only after their concrete trigger is present.
3. **User value priors** guide judgment but are not rigid templates.
4. **Adaptive heuristics** are reorderable or skippable methods for reaching
   the current goal.
5. **Examples and resources** are available references, not implied
   authorization or default workflow.

When these layers conflict, preserve hard invariants and apply only the mode
contracts that the current task actually triggers.

## Hard invariants

- **Authorization**: Do not push, publish, upload material, incur external cost,
  or mutate an external system unless the user explicitly authorizes that
  effect in the current session.
- **External effect gate**: An external API call, material upload, or
  cost-incurring operation requires both an explicitly enabled environment
  setting and an explicit CLI flag or current-session user authorization. API
  keys may come only from environment variables or `.env`.
- **Large local rewrites**: A large-scale local rewrite requires explicit user
  authorization, a bounded scope, and a rollback point. It does not require an
  API environment flag when no external service is involved.
- **Secrets and privacy**: Never commit `.env`, credentials, secrets, complete
  chat logs, or raw private material. Do not copy them into the ledger or a
  durable report.
- **User work and reversibility**: Preserve pre-existing user changes. Do not
  use destructive cleanup, broad restore/reset, or overwrite a drifted local
  Skill without explicit approval.
- **Truthful state and claims**: Do not treat a test, build, report, commit, or
  chat summary as proof that the user goal is complete. Use the authoritative
  state surface for the relevant scope and disclose unresolved gaps.
- **Project independence**: Core authorization, privacy, integrity, and state
  rules must remain usable from this repository alone. External Skills and
  companion workflows may enhance the project but must not be runtime safety
  dependencies.

## Mode contracts

### Code-changing mode

Applies when tracked project files are intentionally changed.

1. Inspect the relevant code and preserve unrelated dirty work.
2. Make the smallest sensible change.
3. Run `python3 tools/project.py check` (`py -3` on Windows) and the
   smallest task-specific tests that prove the changed behavior.
4. Review the relevant diff and stage only task-owned files.
5. Close with a local checkpoint commit, or give an explicit blocked handoff
   when a safe checkpoint is not possible.
6. Do not push unless the user explicitly requests it.

Use `python3 tools/project.py commit --message "type: summary"` for the guarded
local commit. It rejects disallowed paths and high-confidence secret patterns.

For a code-changing handoff, report the result, modified files, verification,
risks, checkpoint status, and any concrete remaining action. Read-only answers
and routine status reports may remain concise and should not manufacture empty
risk or next-step sections.

### Active Work Packet mode

Enter this mode only when the current user request explicitly continues,
resumes, or names a Work Packet. An active marker from an unrelated task is a
background handoff breadcrumb, not ownership of the current request.

Once this mode is entered:

1. Read its `brief.md`.
2. Read the files returned by
   `python3 tools/project.py task context list <slug> --stage <phase>`.
3. Treat `status.tsv` as live execution state; chat, panels, and reports are
   secondary projections.
4. Review `promotion.md` before marking `99-finalize` as `finalized`.

Routine single-session work should not create a Work Packet. Use one when the
work spans multiple dependent packages, worktrees, agents, or handoff sessions.

### Verification, handoff artifact, and deployment modes

- **Verification** checks a stated behavior or contract. It may create
  disposable local output, but it does not itself allocate a version, create a
  user handoff artifact, or change external state.
- **Handoff artifact generation** intentionally creates a user-reviewable or
  transferable result. It requires a current request for that output and stays
  separate from deployment or publication.
- **Deployment** makes a result active outside the project, such as publishing,
  installing, uploading, or otherwise changing an external system. It requires
  separate explicit authorization.

Projects that repeatedly need stronger enforcement may add their own narrow
manifest or gate. The seed deliberately does not create an artifact pipeline,
review system, or deployment workflow by default.

### Durable record mode

Append a `Record` to `control/ledger.md` only when a requirement, decision,
risk, issue, session fact, or artifact link has demonstrated future value:

```text
## YYYY-MM-DDTHH:MM:SS - short title

type: request | decision | session | risk | issue | artifact
status: open | closed
tags: tag-a, tag-b

summary:
- ...

details:
- ...

links:
- path/or/url
```

Use `status: open` only for unfinished requests, risks, and issues that should
appear in the status panel. When a conflict cannot be resolved from an
authoritative source, record an open `issue`; after the user or an authoritative
file resolves it, append a `decision`. Never silently rewrite disagreement into
the appearance of consensus.

### Initialization, governance, and release modes

- `tools/project.py init` is a one-way transition from seed template to project
  workspace; review `control/init_manifest.md` after it runs.
- Governance lifecycle tracking is opt-in. Generate `control/governance.md`
  only for a sustained project that needs explicit keep/defer/retire review.
- Publishing, production operations, data migration, and public release require
  their own explicit authorization and task-specific verification. The normal
  code-changing contract is not sufficient evidence for those modes.

## User value priors

- Keep the default path lightweight and upgrade process only when risk or task
  complexity justifies it.
- Prefer user-goal evidence over process completion signals.
- Favor auditable, reversible work without silently expanding external effects.
- Support solo-first work while preserving optional multi-agent capability.
- Preserve cross-platform and project-local portability.
- Prefer deleting workflow burden or repairing a boundary over adding another
  standing governance layer.

These are optimization directions, not closed templates. When priors conflict,
explain the tradeoff and preserve the hard invariants.

## Adaptive heuristics

- Always read this file and the files directly involved in the task.
- Read `control/state.md` when the task depends on current project status,
  pending maintenance, or cross-session context.
- Read relevant recent `control/ledger.md` records when prior requirements,
  decisions, risks, conflicts, or artifacts may constrain the task.
- Inspect nearby code before editing; prefer small, focused changes and preserve
  existing style unless evidence supports a change.
- Do not invent commands, dependencies, or conventions. Prefer project-provided
  commands and the smallest verification that covers the changed behavior.
- Use a durable report only when the conclusion will be reused, reviewed, or
  handed off. Use `work/out/` for final artifacts that should not be committed
  and `work/tmp/` for disposable files.
- Escalate from a short response to a full handoff when there are tracked
  changes, unresolved risk, cross-session state, or a meaningful user decision.

## Examples and resources

Common verification commands:

```bash
make preflight          # python3 tools/project.py check
make test               # python3 -m pytest
```

Windows PowerShell:

```powershell
py -3 tools/project.py check
py -3 -m pytest
```

Optional resources, not default workflow requirements:

- `control/tasks/<slug>/`: complex-task Work Packets.
- `control/governance.md`: sustained governance review surface.
- `control/delivery_receipt.md`: user-goal acceptance evidence after
  goal-driven initialization.
- `reports/`: durable analysis and review artifacts.
- `agent-assets/user-skills/`: a local 38-Skill snapshot. The small
  `recommended` profile is the normal bootstrap; the full `all` profile remains
  locally available for explicit specialist use.
- Data lifecycle tables, content pipelines, image queues, and HTML delivery
  assets should be generated only when the copied project has that need.

Some files are generated or synchronized by project tools. `CLAUDE.md` is a
thin generated adapter; initialization also creates or rewrites project-facing
state and manifests. Do not hand-edit a generated projection when its source
command should be used instead.

## Agent-specific adapters

- Claude Code reads `CLAUDE.md`, which points back to this file. After changing
  shared rules, run `python3 tools/project.py sync-agents` (`py -3` on Windows).
- Codex uses this `AGENTS.md` directly and project hooks from
  `.codex/hooks.json`.
- Claude project permissions intentionally allow read-only Git inspection and
  the guarded project commit command; mutating raw Git commands require normal
  permission review.
- MCP servers are optional, project-specific integrations. Add one only for a
  concrete external-data or documentation need.
- After changing the portable Skill bundle, run `python3 tools/project.py check`
  and `python3 tools/project.py audit-user-skills` before a forced replacement.
