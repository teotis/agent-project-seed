# Agent Task Planner Examples

Use these as shape examples, not templates to copy blindly. Keep real task packs
repo-specific and evidence-backed.

## Example 1: Direct Bugfix

User asks: "Fix the settings save crash. I already have a failing test."

Correct behavior:

- Inspect repo instructions, `git status --short`, the failing test, and nearby
  settings code before planning.
- Choose lane `direct` when the change is narrow, the failing path is known, and
  no handoff is needed.
- Produce either a very small task pack or proceed in the main thread if the user
  asked for implementation.

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
