# Task Plan Contract

Use this contract when creating a lightweight task pack for `agent-task-planner`.
The goal is enough structure to start safely, not a full scheduler.

## TASK_PLAN.md

```markdown
# <Task Title> - Task Plan

## Goal
<one concrete outcome>

## Current Truth
- Repo:
- Branch:
- Dirty state:
- Relevant files/docs inspected:
- Existing related plan or status:

## Lane Decision
- Selected lane: `direct | single-agent | small-parallel | manual-pack | upgrade`
- Why this lane:
- Why not full orchestration:
- Upgrade trigger if conditions change:

## Fix-Worthiness
- User impact:
- Evidence strength:
- Repair value: `fix-now | worth-fixing-needs-evidence | needs-user-decision | defer | no-fix`
- Main uncertainty:

## Packages
| ID | Title | Owner | Depends On | Allowed Paths | Verification | State |
|---|---|---|---|---|---|---|
| 01-... | ... | main-thread/agent/manual | none | ... | ... | ready |

## Execution Notes
- Branch/worktree strategy:
- Checkpoint rule:
- External gates:
- Explicit non-goals:
- Stop conditions:
```

## AGENT_PROMPTS.md

Each prompt should be short enough for a weaker model to follow.

```markdown
# Agent Prompts

## Package: <id> - <title>

Read:
- <absolute or repo-relative task pack path>/TASK_PLAN.md
- files listed in this package

Mission:
- <specific package outcome>

Allowed paths:
- <paths>

Forbidden without approval:
- <paths/actions>

Acceptance:
- <criteria>

Verification:
- <command>

Before finishing:
- write changed files, verification result, risks, and blocker if any to HANDOFF.md
- leave a local checkpoint commit when authorized by the repo rules
```

## status.tsv

Use a tiny status table. It is coordination memory, not scheduler truth.

```text
id	title	owner	state	branch_or_worktree	verification	next
01-example	Example package	agent	ready	agent/example	pytest tests/example	continue
```

Allowed states:

- `pending`
- `ready`
- `in_progress`
- `completed`
- `blocked`
- `deferred`

## HANDOFF.md

```markdown
# Handoff

## Results
- ...

## Modified Or New Files
- ...

## Verification
- `<command>`: pass/fail/not run

## Risks
- No new risks found.

## Next Steps
- <concrete next action>
```

If there are no risks, write `No new risks found.` exactly.

## Escalation Checklist

Escalate to `agent-orchestration-planner` when any of these becomes necessary:

- persistent DAG state is needed across sessions;
- packages unlock downstream work automatically;
- retry/finalize/cleanup must be scripted;
- each package requires its own worktree plus final merge control;
- multiple runner wrappers are part of the value;
- one artifact claiming success must be cross-checked against scheduler state.

