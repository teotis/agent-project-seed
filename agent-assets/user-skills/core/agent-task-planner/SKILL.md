---
name: agent-task-planner
description: >
  Use when a user has an engineering task to start soon, especially in a new
  or lower-capability agent environment, and needs a lightweight repo-backed
  task plan, agent-ready prompts, branch/worktree guidance, verification steps,
  and clean checkpoint closure. Fits small to medium work; escalate to
  agent-orchestration-planner only when durable DAG scheduling, custom runtime
  state, retry/finalize automation, or multi-wave merge control is required.
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

## Workflow

1. Read the repo instructions, current git state, relevant project status, and
   nearby code or docs.
2. Classify the lane: direct main-thread work, one platform-native agent, small
   parallel agents, manual task pack, or escalate to `agent-orchestration-planner`.
3. Check fix-worthiness and evidence quality before committing work to a plan.
4. Split by shared edit and verification boundaries, not by equal size.
5. Write the lightweight task pack using `references/task-plan-contract.md`.
6. Give each package an owner, allowed paths, forbidden paths, acceptance
   criteria, verification command, expected evidence, and checkpoint rule.
7. If implementation starts in the same session, follow `clean-checkpoint-first`
   before claiming closure.

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
