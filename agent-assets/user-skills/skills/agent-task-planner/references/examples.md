# Agent Task Planner Examples

Use these as shape examples, not templates to copy blindly. Keep real task packs
repo-specific and evidence-backed. Follow the user's language for user-facing
plan prose and Markdown headings; preserve paths, commands, lane values, and
status values.

## Example 1: Direct Bugfix

User asks: "Fix the settings save crash. I already have a failing test."

Correct behavior:

- Inspect repo instructions, `git status --short`, the failing test, and nearby
  settings code before planning.
- Choose lane `direct` when the change is narrow, the failing path is known, and
  no handoff is needed.
- Produce either a very small task pack or proceed in the main thread if the user
  asked for implementation.
- If the user asks in Chinese, produce a 中文计划 with localized headings while
  preserving file paths, commands, lane values, and status enums.

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
- Repair value: `fix-now`
- Evidence strength: failing test reproduces the crash

## Packages
| ID | Title | Owner | Depends On | Allowed Paths | Verification | State |
|---|---|---|---|---|---|---|
| 01-fix-settings-save | Fix null-name save crash | main-thread | none | `src/settings/store.py`, `tests/test_settings_save.py` | `pytest tests/test_settings_save.py` | ready |
```

## Example 2: Small Parallel Refactor

User asks: "There are three independent lint cleanup packages. Let separate
agents do them, but no full orchestration."

Correct behavior:

- Confirm the packages do not share edit paths or verification bottlenecks.
- Choose lane `small-parallel` only for 2-3 independent packages with low merge
  pressure.
- Give each package allowed paths, forbidden paths, verification, and checkpoint
  rule.

Plan shape:

```markdown
## Lane Decision
- Selected lane: `small-parallel`
- Why this lane: three independent modules, no shared files, each has a focused test
- Why not full orchestration: no durable DAG, retry automation, or finalizer state needed

## Packages
| ID | Title | Owner | Depends On | Allowed Paths | Verification | State |
|---|---|---|---|---|---|---|
| 01-api-lint | Clean API lint warnings | agent | none | `src/api/`, `tests/api/` | `pytest tests/api` | ready |
| 02-ui-lint | Clean UI lint warnings | agent | none | `src/ui/`, `tests/ui/` | `pytest tests/ui` | ready |
| 03-cli-lint | Clean CLI lint warnings | agent | none | `src/cli/`, `tests/cli/` | `pytest tests/cli` | ready |

## Execution Notes
- Branch/worktree strategy: one platform-native worktree or branch per package
- Checkpoint rule: each agent leaves a local checkpoint commit and updates `HANDOFF.md`
- Stop conditions: overlapping file edits, shared failure, or new product decision
```

## Example 3: Intake Or Exit

User asks: "Make onboarding better. Split it for agents."

Correct behavior:

- Inspect existing onboarding docs/code first if the repo has obvious paths.
- If the repo does not reveal the intended outcome, do not invent packages such
  as "improve UI" or "rewrite docs".
- Ask one blocking question with a recommended answer, or choose an exit path.

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

If the user instead asks for automatic multi-agent scheduling, persistent state,
retry, and final merge control, choose `upgrade-required` and name the needed
control-plane capability instead of generating a lightweight pack.

## Example 4: Chinese Request, Chinese Plan

User asks: "我刚 clone 一个项目，想马上修一个登录超时问题。模型比较弱，先帮我拆一下怎么做。"

Correct behavior:

- Use Simplified Chinese for the chat reply, plan body, package descriptions,
  handoff prose, and any clarifying question.
- Keep stable machine values such as `single-agent`, `TASK_PLAN.md`,
  `pytest tests/auth`, and `ready` unchanged.
- Do not copy English template headings into the Chinese-facing plan.

Response shape:

```markdown
## 目标
修复登录超时问题，并保留当前登录流程的既有行为。

## 当前事实
- Dirty state: <来自 `git status --short` 的结果>
- 已检查证据: <登录相关测试、日志或代码路径>

## 路线判断
- Selected lane: `single-agent`
- 为什么选择这条路线: 登录超时通常集中在认证链路，适合一个 agent 按证据推进。
- 为什么不需要完整 orchestration: 当前没有 durable DAG、retry automation 或 finalizer state 需求。

## 任务包
| ID | 标题 | Owner | Depends On | Allowed Paths | Verification | State |
|---|---|---|---|---|---|---|
| 01-login-timeout | 定位并修复登录超时 | agent | none | `src/auth/`, `tests/auth/` | `pytest tests/auth` | ready |
```
