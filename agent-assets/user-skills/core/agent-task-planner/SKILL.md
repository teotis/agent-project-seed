---
name: agent-task-planner
description: >
  Use when a user has an engineering task to start soon, especially in a new
  or lower-capability agent environment, and needs a lightweight repo-backed
  task plan, agent-ready prompts, branch/worktree guidance, verification steps,
  clean checkpoint closure, or a quick intake check for unclear requirements.
  Fits small to medium work; ask one clarifying question when user intent is not
  plan-ready, and escalate to agent-orchestration-planner only when durable DAG
  scheduling, custom runtime state, retry/finalize automation, or multi-wave
  merge control is required.
---

# Agent Task Planner

## Mission

Turn a concrete engineering request into a low-cost, executable task plan that
can be handled by the main thread, one agent, or a small set of platform-native
agents without generating a full orchestration control plane.

The default output is a lightweight task pack:

```text
docs/plans/<date>-<slug>/
|-- TASK_PLAN.md
|-- AGENT_PROMPTS.md
|-- status.tsv
`-- HANDOFF.md
```

Use existing project planning locations when the repo defines them. In this
seed, prefer `docs/plans/<date>-<slug>/` for generated task packs and
`control/tasks/<slug>/` only when the user explicitly wants live task state.

## Use When

- A project was just cloned or initialized and the user wants to start work.
- The request needs quick repo-backed analysis before implementation.
- The user's request may be underspecified and needs one focused intake question
  before a responsible plan can exist.
- The work can likely be done directly, by one agent, or by 1-3 independent
  platform-native agents.
- Branch/worktree isolation, verification, and checkpoint rules matter, but a
  custom scheduler would be too heavy.
- Model speed or capability is limited and the next agent needs a short,
  explicit execution contract.

## Do Not Use When

- The user explicitly asks for a full orchestration control plane.
- The task needs durable DAG dispatch, tail-call advancement, retry recovery,
  generated launchers, `99-finalize`, or automatic cleanup.
- A single hard bug still needs root-cause diagnosis before planning.
- The user only wants issue tracker slicing, PRD creation, or issue triage.
- Blocking human/device/account approval is essential and not yet authorized.

## Intake Gate

Before writing a task pack, decide whether the request is plan-ready. If code,
docs, git state, or existing project status can answer the missing detail, inspect
those first. Ask the user only for product, scope, credential, cost, policy, or
preference decisions that cannot be inferred responsibly.

Default to moving forward with reasonable assumptions. Ask only when the missing
answer would change package boundaries, acceptance criteria, execution
permission, or risk level; when the next step is blocked; or when continuing
would likely waste work. When asking, use the `grilling` pattern: ask exactly one
question, explain why it blocks planning, and include your recommended answer.
Do not ask a batch of questions. After the answer, either produce the task pack
or choose an exit path.

A request is plan-ready only when these are clear enough:

- desired user-visible or engineering outcome;
- relevant repo area or discovery path;
- non-goals or constraints that would change the repair;
- verification signal;
- whether work should execute now, be handed to an agent, or remain a manual pack.

If missing information would not change the decomposition, verification, or
permissions, state your assumption and continue. If it would change one of those
things and the repo cannot answer it, return `needs-user-decision` with the first
clarifying question instead of inventing packages.

## Workflow

1. Read the repo instructions, current git state, relevant project status, and
   nearby code or docs.
2. Run the intake gate: inspect before asking, then ask one question or exit if
   the request is not plan-ready.
3. Classify the lane: direct main-thread work, one platform-native agent, small
   parallel agents, manual task pack, or escalate to `agent-orchestration-planner`.
4. Check fix-worthiness and evidence quality before committing work to a plan.
5. Split by shared edit and verification boundaries, not by equal size.
6. Write the lightweight task pack using `references/task-plan-contract.md`.
7. Give each package an owner, allowed paths, forbidden paths, acceptance
   criteria, verification command, expected evidence, and checkpoint rule.
8. If implementation starts in the same session, follow `clean-checkpoint-first`
   before claiming closure.

For examples of `direct`, `small-parallel`, and `needs-user-decision` /
`upgrade-required` behavior, read `references/examples.md`.

## Lightweight Engineering Method

Use only the method needed to keep a weaker model on track:

- **Simplicity first**: choose the smallest change that can satisfy the goal;
  avoid speculative features, one-use abstractions, and generic configurability.
- **Surgical changes**: touch only files that trace directly to the task; mention
  unrelated cleanup opportunities instead of folding them into the plan.
- **Root cause before repair**: for bugs or failing tests, require evidence of
  the failing path before proposing implementation work.
- **Test-shaped goals**: turn each package into success criteria plus the
  smallest meaningful verification command.
- **Isolation by risk**: use the current checkout for narrow safe work, but
  recommend a branch or worktree when the repo is dirty, the change is broad, or
  multiple agents may edit concurrently.
- **Checkpoint early**: prefer a small local checkpoint with disclosed limits over
  leaving new tracked work dirty.

These principles are adapted from the bundled superpowers planning/debugging/
worktree skills and from lightweight Claude-style guidance such as think first,
simplicity first, surgical changes, and goal-driven verification. Keep them as
guardrails, not a long process.

## Lane Rules

- `direct`: one narrow change, clear verification, no agent handoff needed.
- `single-agent`: one coherent package that benefits from a short prompt.
- `small-parallel`: 2-3 independent packages with stable boundaries and little
  merge pressure.
- `manual-pack`: user wants durable instructions but not background execution.
- `upgrade`: use `agent-orchestration-planner` when scheduler truth, multi-wave
  dependencies, retry/finalize automation, or cross-runner launch wrappers are
  the actual value.

Do not choose `upgrade` merely because the task is important or has several
items. Name the specific control-plane capability that is required.

## Exit Paths

Not every task deserves or permits an implementation plan. If the request cannot
be turned into a credible task pack, return one of these outcomes instead of
forcing fake work:

- `no-viable-plan`: no implementable path is supported by current repo evidence.
- `needs-user-decision`: product, design, scope, credential, cost, or policy
  choice blocks responsible planning.
- `blocked-with-handoff`: a real path exists, but the current agent environment
  lacks required access, tools, device, network, dependency, or permission.
- `defer`: the issue has weak evidence, low value, duplicated work, or a bad
  timing fit for the current goal.
- `upgrade-required`: the work is viable only with full orchestration control
  plane capabilities.

Each exit must include: evidence checked, why continuing would be unsafe or
wasteful, the smallest useful next action, and any artifacts or commands already
available.

## Output Shape

After writing a task pack, report only:

- plan directory path;
- selected lane and why;
- package list with dependencies;
- first command or prompt to run;
- verification and checkpoint expectation;
- exit path when no task pack should be generated;
- any external gate or blocked decision.

Keep recovery and alternative lanes brief unless they are immediately relevant.

## Guardrails

- Preserve unrelated dirty work and do not stage broad changes.
- Do not assign human-only, device-only, credential, or approval work to an
  auto-launched agent.
- Do not hide product or user-visible decision points inside implementation
  packages.
- Do not generate custom scripts unless deterministic repetition already exists.
- Do not present tests, commits, APKs, or reports as proof of the user goal when
  they are only proxy evidence.
- Do not turn vague user input into fake precision. Ask one blocking question or
  choose an exit path.
