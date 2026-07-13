# Agent Task Planner Examples

这些是输出形状示例，不是逐字模板。真实 task pack 必须结合当前 repo evidence。

## Example 1: Direct Bugfix

用户说："Fix the settings save crash. I already have a failing test."

正确行为：

- 先检查 repo instructions、`git status --short`、失败测试和附近 settings 代码。
- 当改动很窄、failing path 已知、不需要 handoff 时选择 `direct`。
- 如果用户要求实现，可以直接在主线程执行；如果用户只要计划，则生成很小的 task pack。

Plan shape:

```markdown
## Goal
Fix the settings save crash without changing unrelated settings behavior.

## Current Truth
- Dirty state: clean
- Evidence checked: failing test `tests/test_settings_save.py::test_save_null_name`
- Relevant files: `src/settings/store.py`, `tests/test_settings_save.py`

## Lane Decision
- Selected lane: `direct`
- Why this lane: one failing path, one likely module, one verification command
- Why not full orchestration: no package dependencies or merge control needed

## Fix-Worthiness
- Raw claim: settings save crashes when name is null
- Claim disposition: `validated`
- Current evidence: failing test `tests/test_settings_save.py::test_save_null_name`
- Counter-evidence checked: no existing null-name guard in `src/settings/store.py`
- Repair value: `fix-now`
- Evidence strength: failing test reproduces the crash

## Packages
| ID | Title | Owner | Depends On | Allowed Paths | Verification | Integration Target | State |
|---|---|---|---|---|---|---|---|
| 01-fix-settings-save | Fix null-name save crash | main-thread | none | `src/settings/store.py`, `tests/test_settings_save.py` | `pytest tests/test_settings_save.py` | current branch | ready |
```

## Example 2: Small Parallel Refactor

用户说："There are three independent lint cleanup packages. Let separate agents do them, but no full orchestration."

正确行为：

- 先确认 packages 不共享 edit paths，也没有共享 verification bottleneck。
- 只有 2-3 个独立包、边界稳定、merge pressure 低时选择 `small-parallel`。
- 每个 package 都要写清 allowed paths、forbidden paths、verification 和 checkpoint rule。

Plan shape:

```markdown
## Lane Decision
- Selected lane: `small-parallel`
- Why this lane: three independent modules, no shared files, each has a focused test
- Why not full orchestration: no durable DAG, retry automation, or finalizer state needed

## Packages
| ID | Title | Owner | Depends On | Allowed Paths | Verification | Integration Target | State |
|---|---|---|---|---|---|---|---|
| 01-api-lint | Clean API lint warnings | agent | none | `src/api/`, `tests/api/` | `pytest tests/api` | integration branch | ready |
| 02-ui-lint | Clean UI lint warnings | agent | none | `src/ui/`, `tests/ui/` | `pytest tests/ui` | integration branch | ready |
| 03-cli-lint | Clean CLI lint warnings | agent | none | `src/cli/`, `tests/cli/` | `pytest tests/cli` | integration branch | ready |

## Execution Notes
- Branch/worktree strategy: one platform-native worktree or branch per package
- Checkpoint rule: each agent leaves a local checkpoint commit and updates `HANDOFF.md`
- Integration visibility rule: package is not delivered until changed files are merged or prepared for the integration branch
- Stop conditions: overlapping file edits, shared failure, or new product decision
```

## Example 3: Intake Or Exit

用户说："Make onboarding better. Split it for agents."

正确行为：

- 如果 repo 有明显路径，先检查现有 onboarding docs/code。
- 如果 repo 证据无法说明用户要的结果，不要发明 "improve UI" 或 "rewrite docs" 这类包。
- 问一个阻塞问题并给推荐答案，或选择 exit path。

Response shape:

```markdown
Exit outcome: `needs-user-decision`

Evidence checked:
- `rg -n "onboarding|signup|first run" README.md docs src tests`
- No current onboarding flow or acceptance criteria found.

Why continuing would be unsafe or wasteful:
- "Better onboarding" could mean activation UX, docs, account setup, sample data,
  error recovery, or analytics. These imply different files and verification.

Question:
- Which onboarding outcome should this plan optimize first?

Recommended answer:
- Start with first-run activation: a new user can complete setup and reach the
  first successful action without manual support.

Smallest useful next action:
- After that choice, inspect the matching flow and produce a direct or
  small-parallel task pack.
```

## Example 4: Raw Claim Needs Validation

用户说："用户反馈导出页面坏了，拆一个修复包给 agent。"

正确行为：

- 先把反馈当作 `raw claim`，查当前代码、测试、日志、截图或可复现路径。
- 如果只能确认“有人报告过”，但没有当前证据，不把修复包标成 `ready`。
- 可以生成 discovery / validation package，或选择 `needs-user-decision` / `defer`。

Plan shape:

```markdown
## Fix-Worthiness
- Raw claim: export page is broken
- Claim disposition: `reported-only`
- Current evidence: no current failing test, screenshot, log, or reproducible route found
- Counter-evidence checked: export route and existing smoke test still pass locally
- Repair value: `worth-fixing-needs-evidence`
- Feasibility: `needs-discovery`
- Main uncertainty: missing failing path and affected surface

## Packages
| ID | Title | Owner | Depends On | Allowed Paths | Verification | Integration Target | State |
|---|---|---|---|---|---|---|---|
| 01-validate-export-claim | Reproduce or falsify export-page report | agent | none | `src/export/`, `tests/export/`, `docs/plans/...` | `pytest tests/export` plus reproduction notes | current branch | ready |

## Execution Notes
- Stop conditions: do not implement a UI or export rewrite until the failing path is reproduced or user supplies current evidence.
```

## Example 5: Generated Translation Files Must Reach Target

用户说："让 agent 在分支上补完公开英文翻译文件，然后我在 main 上要能看到。"

正确行为：

- 明确 integration target 是 `main` 或用户指定的集成分支。
- `HANDOFF.md` 不能只写 agent 分支生成了文件；必须记录是否已合入目标分支并能在目标分支看到。
- 如果因为冲突、权限或用户不允许合并而不能合入，输出 `blocked-with-handoff` 或把 package 状态保留为 `blocked`，不要声称交付完成。

Plan shape:

```markdown
## Packages
| ID | Title | Owner | Depends On | Allowed Paths | Verification | Integration Target | State |
|---|---|---|---|---|---|---|---|
| 01-sync-public-translation | Generate and integrate public English translation files | agent | none | `skills/*/references/public-en.SKILL.md`, `public/teotis-skills/` | `grep -R -n '[一-鿿]' public/teotis-skills/<skill>/` | `main` | ready |

## Execution Notes
- Branch/worktree strategy: work on a feature branch if needed, then merge or prepare a merge into `main`.
- Integration visibility rule: finish only when the generated translation files are visible from `main`; otherwise record branch name, blocker, and next merge step in `HANDOFF.md`.
```

如果用户要求自动多 agent 调度、persistent state、retry 和最终 merge control，选择 `upgrade-required`，并说清楚需要的 control-plane capability，而不是生成轻量 task pack。
