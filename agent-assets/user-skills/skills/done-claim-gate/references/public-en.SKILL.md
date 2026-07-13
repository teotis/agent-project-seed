---
name: done-claim-gate
description: Use before claiming completion on non-routine delivery-risk tasks where tests, commits, builds, reports, generated files, or partial implementation could be mistaken for the user's actual goal being achieved.
---

# Done Claim Gate

## Mission

Prevent an agent from reporting a user goal as complete when the evidence only proves engineering activity. This skill binds the user goal, intended solution, real implementation path, acceptance evidence, remaining gaps, and allowed completion wording.

It is not a copy-editing tool for final messages. It is a delivery check: did the chosen path actually reach the user-visible or downstream-visible goal?

## Modes

### Pre-Delivery Lens

Use before making a risky delivery claim when the task has interpretation space, cross-path dependencies, public or downstream impact, generated artifacts, UI behavior, release packaging, export contracts, or a risk that an old fallback path still dominates.

Run a light but real check across:

- goal reach;
- user operation view;
- decision usefulness;
- real scenario depth;
- path authenticity.

If the check finds a gap that affects the completion claim, upgrade to the completion claim gate or repair before finalizing.

### Completion Claim Gate

Use when you are about to say a high-risk task is complete, solved, ready, or delivered, or when the user challenges a previous completion claim.

Build:

- Delivery Contract;
- Plan-To-Implementation Map;
- Goal Realization Gate;
- Gap Ledger;
- Completion Claim Permission.

## Use When

Use this skill when:

- the user goal is broad enough that the agent must supply judgment;
- the implementation spans multiple paths, generated artifacts, UI states, reports, public packages, export formats, or downstream contracts;
- a legacy path, fallback, template, stale renderer, old data flow, or weak substitute might satisfy tests while missing the real goal;
- the user has recently corrected an agent for claiming completion too early;
- the evidence may only prove code changed, tests passed, a build succeeded, a report exists, or a commit was made.

Do not use it for exact mechanical edits, typo fixes, low-risk copy changes, ordinary status updates, or internal maintenance that does not change the user-visible or downstream-visible contract.

## Hard Invariants

- The user goal is the primary evidence source. Tests, builds, commits, generated files, and reports are support evidence, not the goal itself.
- The intended solution must map to the real code, data, UI, artifact, or workflow path.
- Do not report an old fallback, old renderer, stale template, or weak substitute as if it were the intended solution.
- Acceptance evidence must match the goal type. Visual work needs visual evidence or explicit user acceptance. Release work needs artifact identity. Behavior work needs a reproducible flow.
- Completion has levels. When acceptance evidence is missing, say engineering-complete, partial, blocked, or not-complete instead of complete.
- If a human approval, real device, external account, publish action, or user review is required, mark it as an external gate.

## Pre-Delivery Lens Workflow

1. **Reset the frame:** write one sentence describing what the user can actually do or decide with the delivered result.
2. **Goal reach:** does the artifact or behavior reach the real goal, or only a surface requirement?
3. **User operation view:** check entry point, default path, number of actions, number of decisions, context the user must reconstruct, and recovery cost.
4. **Decision usefulness:** can the user make the intended decision without hidden assumptions?
5. **Real scenario depth:** does the result cover a realistic use case rather than a narrow proxy?
6. **Path authenticity:** is the new intended path actually used, or is an old path still doing the work?
7. **Disposition:** choose `safe-to-summarize`, `repair-before-final`, or `must-upgrade`.

## Completion Claim Gate Workflow

### 1. Delivery Contract

Extract:

- user goal;
- intended solution;
- non-substitutable requirements;
- non-goals;
- success evidence;
- external acceptance gates.

### 2. Plan-To-Implementation Map

Map the intended solution to real paths:

- code path;
- data path;
- UI or artifact path;
- verification path;
- possible old-path traps.

### 3. Goal Realization Gate

Prove the current result satisfies the goal itself, not only a proxy. For each goal item, state whether it is `done`, `partial`, `not-done`, or `blocked`, with evidence.

### 4. Gap Ledger

Record remaining gaps and their effect on the final claim. Do not hide blocked validation in a success summary.

### 5. Completion Claim Permission

Choose the strongest honest status:

- `complete`: the user goal is achieved and required acceptance evidence exists;
- `engineering-complete`: implementation and local verification are done, but external acceptance remains;
- `partial`: meaningful progress exists, but some goal items are missing;
- `blocked`: progress cannot continue without external input or access;
- `not-complete`: the current result does not satisfy the goal.

## Output Shape

For a pre-delivery lens, report:

```text
User goal:
Goal reach:
User operation view:
Decision usefulness:
Real scenario depth:
Path authenticity:
Disposition:
Repair or next step:
```

For a completion claim gate, report:

```text
Delivery status:
User goal:
Intended solution:
Implementation map:
Goal realization:
Acceptance evidence:
Remaining gaps:
Completion claim permission:
Next step:
```

Keep the final answer concise, but make the completion level explicit.
