# Task Plan Contract

创建 `agent-task-planner` 轻量 task pack 时使用本合同。目标是让任务能安全开始，而不是生成完整 scheduler。

## TASK_PLAN.md

```markdown
# <Task Title> - Task Plan

## Goal
<一个具体结果>

## Current Truth
- Repo:
- Branch:
- Dirty state:
- Relevant files/docs inspected:
- Existing related plan or status:

## Lane Decision
- Selected lane: `direct | single-agent | small-parallel | native-agent-controls | ledger-lite | manual-pack | upgrade`
- Why this lane:
- Why not full orchestration:
- Upgrade trigger if conditions change:

## Exit Path
- Exit outcome: `none | no-viable-plan | needs-user-decision | blocked-with-handoff | defer | upgrade-required`
- Evidence checked:
- Why continuing would be unsafe or wasteful:
- Smallest useful next action:

## Fix-Worthiness
- Raw claim:
- Claim disposition: `validated | reported-only | downgraded | deferred | rejected`
- Problem-specific checks derived:
- Current evidence:
- Counter-evidence checked:
- User impact:
- Evidence strength:
- Repair value: `fix-now | worth-fixing-needs-evidence | needs-user-decision | defer | no-fix`
- Feasibility: `agent-fixable | needs-discovery | blocked-external | not-feasible`
- Solution fit:
- Solution risks checked:
- Main uncertainty:
- Complexity / boundary risk:

## Plan / Package Proof Route
- Claim proof:
- Worth proof:
- Feasibility proof:
- Solution-fit proof:
- Verification proof:
- Integration proof:
- Falsifier / downgrade trigger:

## Plan Fitness
- Startability:
- Evidence strength:
- Scope containment:
- Verification strength:
- Integration visibility:
- Cognitive load:
- Recovery clarity:
- Decision:

## Packages
| ID | Title | Owner | Depends On | Allowed Paths | Verification | Integration Target | State |
|---|---|---|---|---|---|---|---|
| 01-... | ... | main-thread/agent/manual | none | ... | ... | main/current target branch | ready |

## Execution Notes
- Branch/worktree strategy:
- Checkpoint rule:
- Integration visibility rule:
- External gates:
- Explicit non-goals:
- Stop conditions:
```

## AGENT_PROMPTS.md

每个 prompt 都应该短到较弱模型也能照着执行。

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
- If this package creates translated, generated, exported, or reviewable user-facing files, those files are visible on the integration target branch, or the blocker and merge command are recorded.

Verification:
- <command>

Before finishing:
- write changed files, verification result, risks, and blocker if any to HANDOFF.md
- leave a local checkpoint commit when authorized by the repo rules
- if working on a branch/worktree, merge or prepare the package so required artifacts are visible on the agreed integration target; do not claim delivery from an isolated branch alone
```

## status.tsv

使用极小 status table。它是 coordination memory，不是 scheduler truth。

```text
id	title	owner	state	branch_or_worktree	integration_target	verification	next
01-example	Example package	agent	ready	agent/example	main	pytest tests/example	continue
```

允许状态：

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

## Integration Visibility
- Target branch:
- Visible on target: yes/no/not applicable
- If no, blocker and next merge step:

## Verification
- `<command>`: pass/fail/not run

## Risks
- No new risks found.

## Next Steps
- <concrete next action>
```

如果没有风险，必须原样写 `No new risks found.`。

## Escalation Checklist

出现以下情况时升级到 `agent-orchestration-planner`：

- 需要跨 session 的 persistent DAG state；
- package 会自动 unlock downstream work；
- retry/finalize/cleanup 必须脚本化；
- 每个 package 需要独立 worktree，并且需要 final merge control；
- multiple runner wrappers 是任务价值的一部分；
- 某个 artifact 声称成功时，必须和 scheduler state 交叉校验。
