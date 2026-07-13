---
name: agent-task-planner
description: Use when a concrete engineering request needs a lightweight repo-backed task plan, agent-ready prompts, verification steps, checkpoint expectations, or routing between direct work, one-agent work, small parallel work, native agent controls, ledger-lite planning, and heavier orchestration.
---

# Agent Task Planner

## Mission

Turn a concrete engineering request into a lightweight, executable, recoverable task plan. The plan should be small enough for the main agent, one agent, or a few independent agents to execute without a custom scheduler.

This skill is also a routing gate. Even when the user mentions multiple agents or parallel work, first decide whether the task truly needs a durable orchestration control plane. Upgrade only when lightweight planning cannot protect dependency closure, recovery, final integration, or status truth.

## Use When

Use this skill when:

- the user has a near-term engineering task and needs a repo-backed plan before implementation;
- the request needs quick evidence gathering before deciding how to proceed;
- a raw bug report, screenshot, acceptance note, or user claim should be validated before it becomes implementation work;
- branch, worktree, verification, or checkpoint expectations need to be explicit;
- the task is likely suitable for direct execution, one agent, two or three independent packages, platform-native agent controls, or a small ledger-lite plan.

Do not use it when the user explicitly asks for a full orchestration kit, durable DAG dispatch, automated retry/finalize behavior, generated launchers, automatic cleanup, issue-tracker slicing, PRD creation, or unresolved root-cause debugging.

## Planning Gate

Before writing a task pack, decide whether the request is plan-ready. Prefer discovering missing facts from repository instructions, git state, code, tests, logs, generated artifacts, and existing docs. Ask the user only when the missing answer would change package boundaries, acceptance criteria, execution permission, cost, policy, or risk.

A request is plan-ready when these are clear enough:

- the expected user-visible or engineering outcome;
- the relevant repository area or discovery path;
- constraints or non-goals that change the fix route;
- the verification signal;
- whether the output is for immediate execution, agent handoff, or a manual pack.

If missing information would not change the plan, state the assumption and continue. If it would change the plan and cannot be inferred from the repo, ask one blocking question and give the recommended default.

## Claim Validation Gate

Treat reported problems as raw claims until checked. Before generating ready implementation packages, perform the smallest useful validation:

- **Current evidence:** find direct evidence in the current repo, tests, logs, output, screenshots, or docs. If only the user report exists, mark it `reported-only`.
- **Counter-evidence:** check for branch drift, stale artifacts, existing fixes, disabled paths, duplicate reports, fixture issues, or version mismatch.
- **Fix-worthiness:** decide whether the impact, timing, and value justify a fix now.
- **Feasibility:** confirm that the agent can act within available paths, permissions, tools, devices, dependencies, and verification gates.
- **Solution fit:** if a candidate fix exists, check whether it addresses the root cause without hiding a product, compatibility, security, privacy, or release decision.
- **Proof route:** before marking a package ready, name the evidence that proves the claim, worth, feasibility, solution fit, verification path, integration visibility, and the falsifier that would make the package invalid.

If the claim is not proven, valuable, feasible, and verifiable enough, create a discovery or validation package, choose an exit path, or report the blocker instead of inventing ready implementation work.

## Lane Rules

Choose the lightest lane that protects the work:

- `direct`: one narrow change with clear verification.
- `single-agent`: one coherent package suitable for a short agent prompt.
- `small-parallel`: two or three independent packages with stable boundaries and low merge pressure.
- `native-agent-controls`: platform-native agents or background sessions are enough for launch, status, and logs.
- `ledger-lite`: durable package docs, status rows, owner, verification, checkpoint, and handoff are useful, but automated scheduling is unnecessary.
- `manual-pack`: the user wants durable instructions but no background execution.
- `upgrade`: the work needs durable DAG truth, multi-wave unlocks, retry/finalize automation, cross-runner launch wrappers, or final merge/cleanup control.
- `upgrade-unavailable-fallback`: the work needs heavier orchestration but that capability is unavailable. Use larger dependency-closed packages or stop with a handoff.

Do not upgrade merely because the task is important or has multiple parts. Name the control-plane capability that lightweight planning cannot provide.

## Task Pack Shape

When writing files, use the repository's planning home if it exists. Otherwise use:

```text
docs/plans/<date>-<slug>/
|-- TASK_PLAN.md
|-- AGENT_PROMPTS.md
|-- status.tsv
`-- HANDOFF.md
```

Each package should include:

- owner or intended executor;
- allowed paths and forbidden paths;
- acceptance criteria;
- verification command and expected evidence;
- checkpoint rule;
- integration target or visibility expectation;
- proof route;
- falsifier;
- dependencies and unlock conditions.

Keep packages dependency-closed. A slightly larger coherent package is safer than small packages that secretly depend on each other's unverified outputs.

## Output Shape

In chat, keep the summary short:

- plan directory path, if files were created;
- selected lane and reason;
- raw claim disposition: `validated`, `reported-only`, `downgraded`, `deferred`, or `rejected`;
- package list and dependencies;
- first command or prompt to run;
- verification, checkpoint, and integration expectations;
- exit path when no task pack was generated.

## Guardrails

- Preserve unrelated dirty work.
- Do not assign human-only, credential-only, device-only, approval-only, or external account work to an automated agent.
- Do not hide product, privacy, security, compatibility, release, or UX decisions inside implementation packages.
- Do not treat tests, commits, builds, generated files, or reports as proof that the user's actual goal is complete.
- Do not leave generated artifacts stranded on an agent branch without stating how they become visible on the target line.
