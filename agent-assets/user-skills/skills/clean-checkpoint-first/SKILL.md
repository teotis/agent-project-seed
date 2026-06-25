---
name: clean-checkpoint-first
description: Use when the user asks Codex to fix, implement, repair, close out, land, merge, or handle one or more code issues and expects the workspace to end in an auditable local checkpoint instead of uncommitted tracked changes. Also use when a task mentions dirty worktrees, commits, main integration, Codex App worktrees, or subagent/worktree orchestration.
---

# Clean Checkpoint First

## Purpose

Prefer an imperfect local checkpoint commit over leaving newly changed tracked files dirty. Dirty workspaces destroy auditability; local commits can be inspected, amended, reverted, cherry-picked, or merged.

This skill is a closure contract for implementation sessions. It does not authorize pushing, destructive cleanup, or committing unrelated pre-existing user work.

## Default Contract

When the user asks for a code fix or implementation and does not explicitly say analysis-only/no-commit:

1. Capture `git status --short` before editing.
2. Preserve unrelated pre-existing dirty files.
3. Make the smallest sensible fix.
4. Run proportional verification.
5. Stage only files that belong to this task.
6. Create a local checkpoint commit even if verification is incomplete or failing, as long as the commit message and final response clearly disclose the state.
7. Integrate into local `main` when it is safe and clearly within the user's requested outcome.
8. Do not push unless the user explicitly asks.

## Hard Invariants

- Never use `git add .` in a dirty workspace. Stage exact paths or hunks.
- Never commit files that were dirty before the task unless the task explicitly targets them or the user approves.
- Never hide failing tests. A checkpoint with disclosed failing verification is better than dirty, untracked uncertainty.
- Never use destructive commands such as `git reset --hard`, broad `git checkout --`, broad `git restore`, or deleting worktrees without explicit approval.
- Never commit secrets, local credentials, ignored caches, build outputs, APKs, `.DS_Store`, AppleDouble `._*` files, or generated evidence unless the user explicitly requests that artifact.
- Never push, force-push, publish, or update a remote branch unless the user explicitly asks.
- If the repository supplies agent instructions, verification scripts, or release gates, follow those before inventing generic commands.

## Main And Worktree Policy

Use local `main` as the final landing place when all of these are true:

- The user asked for a fix, implementation, or cleanup rather than just investigation.
- The current branch/worktree relationship is clear.
- The task's files are isolated from unrelated pre-existing dirty work.
- Verification has run or the blocker is clearly documented.
- Merging does not require discarding or overwriting someone else's changes.

If the Codex App session is in a detached worktree, a temporary branch, or a branch created for an isolated issue, first create a checkpoint commit there. Then either merge/cherry-pick into local `main` when safe, or leave a precise handoff with commit hash, branch/worktree path, verification, and why main integration was not safe.

For multiple independent issues, prefer separate worktrees or sessions with one checkpoint commit per issue, then a finalizer pass that merges/cherry-picks each clean checkpoint into local `main` and reruns an integration check.

## Subagent Policy

Subagents are useful for read-heavy exploration, independent diagnosis, test review, or code review. Do not rely on subagents as the authority for committing or merging. The main agent owns staging, checkpoint commits, main integration, and final disclosure.

When the user explicitly asks for parallel/subagent handling, split tasks so each worker can produce a narrow patch or diagnosis. Reconcile in the main thread before committing.

## Handling Dirty Workspaces

Classify `git status --short` before editing:

- `baseline`: already dirty before the task; preserve unless relevant.
- `task-owned`: changed by this task; should be staged and checkpointed.
- `blocked`: cannot safely classify; stop before staging and explain exactly what is ambiguous.

If unrelated dirty files overlap with the files needed for the task, inspect the diff carefully. Use hunk staging or ask the user only when the overlap makes a safe checkpoint impossible.

## Verification

Run the smallest meaningful check that covers the changed behavior. Use repository-provided scripts when available.

If verification fails:

- Fix it if it is in scope and feasible.
- Otherwise checkpoint the current task-owned changes if they are still useful or necessary.
- Include the failing command and the highest-signal error in the final response.

If verification cannot run because of environment limits, checkpoint and disclose the limitation.

## Final Response Checklist

Before claiming completion, report:

- Local checkpoint commit hash, or the exact reason no commit was made.
- Whether the change is landed on local `main`, left on a branch/worktree, or blocked.
- Verification command and result.
- Any preserved dirty files or remaining task-owned dirty files.
- Push status: normally `not pushed`.
- Concrete next step only when there is a real remaining action.
