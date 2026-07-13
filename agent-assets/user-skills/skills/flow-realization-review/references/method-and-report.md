# Flow Realization Review Method And Report

## Table Of Contents

- [Purpose](#purpose)
- [Value And Design Audit Model](#value-and-design-audit-model)
- [Realization Model](#realization-model)
- [Project Thesis Test](#project-thesis-test)
- [Core Object Test](#core-object-test)
- [Top-Level Design Fit](#top-level-design-fit)
- [Typical Flow Pattern](#typical-flow-pattern)
- [Branch Matrix](#branch-matrix)
- [Evidence Rules](#evidence-rules)
- [Schema Anti-Leakage](#schema-anti-leakage)
- [Readiness Gate](#readiness-gate)
- [Review Checkpoints](#review-checkpoints)
- [Report Schema](#report-schema)
- [HTML Artifact Guidance](#html-artifact-guidance)
- [Supplement Task Package](#supplement-task-package)
- [Near-Neighbor Routing](#near-neighbor-routing)
- [Common Failure Modes](#common-failure-modes)

## Purpose

Use this reference when a user needs to inspect whether an engineering design, workflow, agent, tool, or skill truly carries user value into a coherent top-level design and executable main flow. The review should make the system legible enough that the user can say:

- this is the real user value;
- this project identity is right or wrong;
- this top-level design fits or does not fit the value;
- this main flow carries the value or drops it;
- this default is right;
- this branch is missing;
- this is only designed, not implemented;
- this needs a threshold or decision queue;
- this should become a follow-up task.

The intended artifact is a project audit report or typical-flow audit map, not a generic status spreadsheet. Lead with project meaning and user value, then make the main process and its defects reviewable.

Do not produce a broad project overview when the user's real need is to understand one typical flow. Prefer one representative story with branch expansion over a full inventory that does not help review. Conversely, when the user asks whether the top-level design is defective, do not collapse the answer into branch readiness alone.

## Value And Design Audit Model

Use this sequence for formal reports:

```text
project thesis
-> user value and success signal
-> demand scenarios
-> core object
-> top-level design fit
-> main flow
-> branch/default/risk gates
-> implementation reality
-> defects, decisions, supplements
-> evidence appendix
```

The report should help the user audit two questions at once:

1. **Value fit**：does the engineering design actually serve the user's burden, trust requirement, speed requirement, control requirement, or recovery requirement?
2. **Flow fit**：does the main process turn that value into an inspectable and executable path, including branches, gates, evidence, and recovery?

If either layer is missing, mark the gap explicitly. A flow can be technically executable but value-misaligned; a value thesis can be attractive but not realized in the process.

## Realization Model

Track ten layers:

| Layer | Question | Failure signal |
|---|---|---|
| Project thesis | What is this engineering object really trying to be? | The report describes components but cannot name the product/workflow identity. |
| User goal | What user burden or decision is this flow supposed to solve? | Internal mechanism replaces the user need. |
| Demand scenarios | Which real situations enter the flow? | Future vision, rare branches, and current supported paths are mixed. |
| Top-level design | Do core objects, state, evidence, permissions, and recovery match the value? | Architecture optimizes implementation convenience but loses user trust/control. |
| Core object | What unit is approved, executed, recovered, and explained? | State scatters across chat, logs, docs, files, and tools. |
| Typical flow | What happens from user trigger to closeout? | The report is a feature list, not a story. |
| Branches | Which variants, exceptions, and risk gates exist? | Edge cases are hidden in prose or omitted. |
| Evidence | What proves each status or claim? | Designed branches are shown as implemented. |
| Decisions | Where must the user approve, defer, reject, or set defaults? | Agent invents policy where the user needs a choice. |
| Supplements | What must be added before the flow is reliable? | Gaps are described but not packaged into next actions. |

## Project Thesis Test

Start formal reports with a sharp thesis:

```text
This project is not a generic <near neighbor>; it is a <specific system/workflow>
for <user burden>, where success means <observable result>.
```

Good thesis examples:

- "not a generic photo manager, but a media-debt processing system for phone/cloud cleanup";
- "not a prompt library, but a reviewable skill factory for turning conversations into reusable agent behavior";
- "not a dashboard, but an approval and recovery surface for risky batch operations".

Use the thesis to catch top-level design defects:

- If the thesis says "trust" but the flow lacks evidence, approval, or recovery, record a design defect.
- If the thesis says "batch relief" but each branch interrupts the user with micro-decisions, record a flow defect.
- If the thesis says "agent autonomy" but all decisions live in chat memory, record a state-authority defect.
- If the thesis cannot distinguish the project from a generic tool category, ask for or infer a stronger value thesis and mark uncertainty.

## Core Object Test

Before recommending new implementation, ask whether the system has a stable work unit:

- What receives the user's goal?
- What owns the evidence index?
- What records approval and risk boundaries?
- What can be resumed after interruption?
- What explains why a branch was taken?
- What produces receipts or audit trails?

If the answer is "several unrelated files and chat memory", mark `design-gap` or `needs-supplement`. A core object can start as a lightweight manifest; do not overbuild a database or workflow engine unless evidence shows the thin package cannot hold the flow.

## Top-Level Design Fit

Audit whether the design's main objects and boundaries serve the user value.

| Design element | Review question | Common defect |
|---|---|---|
| Core object | What carries goal, scope, evidence, approval, decisions, receipt, and recovery? | The user cannot resume, audit, or hand off because the work unit is implicit. |
| State authority | Which file, database, ledger, manifest, or service is authoritative for status? | Multiple surfaces disagree or chat prose becomes the source of truth. |
| Evidence layer | What does the system know before it acts, and how can the user inspect it? | Risky actions are based on opaque inference or unreviewed summaries. |
| Permission boundary | Where are user authorization, account access, destructive actions, and external side effects gated? | Risky actions are treated as ordinary flow steps. |
| Recovery surface | How can the user undo, resume, explain, or audit the result? | The system can act but cannot leave a receipt or rollback path. |
| Scenario boundary | Which scenarios are current support, design-only, future vision, or user-authorized extension? | The report sells future architecture as current capability. |

Use a "design defect" label for mismatches at this level. Do not hide them as generic TODOs.

## Typical Flow Pattern

Use this skeleton and rename steps for the domain:

```text
trigger -> input/scope -> preflight -> evidence build -> review surface
        -> branch/default selection -> risk gate -> decision/approval
        -> dry-run or preview -> execution -> receipt -> recovery/closeout
```

For agent or skill designs, translate the same pattern:

```text
user request -> scope resolution -> source reading -> reasoning path
             -> artifact generation -> review/decision -> handoff or implementation gate
```

## Branch Matrix

For each branch, record:

- branch id;
- trigger condition;
- default handling;
- owner object or state authority;
- implementation status: `implemented`, `designed-only`, `manual`, `missing`, `needs-authorization`, `unknown`;
- evidence ID;
- user-visible consequence;
- required supplement or decision.

Use a matrix when the user needs review. Use prose only for tiny flows.

Schema guard: never let the status column claim more than the evidence column supports. If evidence is absent, stale, indirect, or only design-level, the status must degrade.

## Evidence Rules

Use stable evidence IDs:

```text
E01 docs: path and observed rule
E02 code: command or function and observed behavior
E03 artifact: report, screenshot, manifest, package, receipt
E04 user: explicit decision or preference from current conversation
E05 unknown: evidence not available
```

Evidence can support only what it shows:

- A design document supports `designed-only`, not `implemented`.
- A command existence supports `implemented` only for the command path, not the full user flow.
- A passing test supports an engineering path, not user approval or final readiness.
- A report can expose gaps; it does not by itself close them.

## Schema Anti-Leakage

This skill borrows the schema anti-leakage lesson from research-skill manifests: a structured field should prevent unsupported claims from leaking into user-facing conclusions.

Apply these rules:

- If `evidence_id` is empty or points to `unknown`, branch status cannot be `implemented`, `ready`, or `execution-ready`.
- If evidence is only a design document, branch status is at most `designed-only`.
- If evidence is only a review page, branch status is at most `review-ready`; risky execution remains `not-ready` until approval, dry-run, receipt, and recovery evidence exist.
- If a claim depends on user preference, branch status cannot be `approved` until the user decision is recorded.
- If the recovery path is absent, destructive or irreversible branches cannot be `ready` even when execution tooling exists.
- If the status and evidence conflict, status loses. Write the conflict into the gap ledger instead of smoothing it over.

Use explicit downgrade language:

```text
claimed status: implemented
supported status: designed-only
reason: evidence is an ADR, not a real command/test/artifact path
gap type: evidence
checkpoint: execution checkpoint
```

## Readiness Gate

Use this decision order:

1. If no user goal or core object can be named, status is `design-gap`.
2. If the typical flow cannot be traced end to end, status is `design-gap` or `needs-supplement`.
3. If key implementation claims lack direct evidence, status is `evidence-gap`.
4. If main flow works but missing templates, thresholds, ledgers, queues, or UI review affordances block confident use, status is `needs-supplement`.
5. If risk gates are absent for destructive, irreversible, downstream, or high-trust actions, status is `not-ready` for those actions even when review is ready.
6. Use `ready` only when the current goal, not the future vision, is supported by evidence.

## Review Checkpoints

Use checkpoint language to make follow-up work easier to approve, split, and verify.

| Checkpoint | Question | Typical evidence | Typical gap |
|---|---|---|---|
| `review checkpoint` | Can the user understand and inspect the flow? | flow map, branch matrix, review page, summary report | the report is too broad, hidden defaults, missing branch labels |
| `approval checkpoint` | Does the user need to choose, authorize, or set a policy? | recorded decision, pending decision queue, approval manifest | agent invents defaults, unclear interruption policy |
| `execution checkpoint` | Can the system safely run the intended path? | command, dry-run, test, output contract, receipt | designed-only tool, missing downstream proof, old fallback path |
| `recovery checkpoint` | Can the result be explained, resumed, reverted, or audited? | audit range, receipt, recovery manifest, rollback note | state scattered across chat/logs, no restore path |

Do not collapse checkpoint types. A flow can pass review while failing execution, or pass execution while failing recovery.

## Report Schema

Formal reports should use this structure:

1. **Project Thesis And Decision Summary**：one screen with the project identity, status, main reason, top defects, and next action.
2. **User Value**：what burden, trust need, efficiency gain, control need, or result quality the engineering system should create.
3. **Demand Scenarios**：the main real-world entries into the flow, including current support, design-only scenarios, and authorization-dependent scenarios.
4. **Top-Level Design Fit**：core object, state authority, evidence layer, permission boundary, recovery model, and scenario boundary.
5. **Main Flow Map**：one representative story from user trigger to closeout.
6. **Branch And Status Matrix**：meaningful variants, defaults, risk gates, evidence labels, and "what the user can audit" questions.
7. **Implementation Reality**：implemented / designed-only / manual / missing / authorization-required.
8. **Risk Gates And Human Decisions**：where the user must approve, defer, or set defaults.
9. **Design Defect And Gap Ledger**：top-level design defects, flow defects, evidence gaps, supplement tasks, pending decisions, and deferred items.
10. **Task Package**：small follow-up slices with owner skill suggestions.
11. **Evidence Appendix**：stable IDs with file paths, commands, screenshots, reports, or unknowns.

For a low-understanding-cost report, add a "30 seconds" section with 5-7 named objects or concepts. Example categories:

- user input/source;
- work package or case;
- evidence layer;
- candidate/decision layer;
- risk gate;
- receipt/recovery surface.

## HTML Artifact Guidance

Use HTML when it materially helps review: many branches, user feedback, long-term handoff, or visual flow comprehension.

Keep the page quiet and review-focused:

- opening viewport should show the project thesis, user value, and main flow, not a decorative hero;
- include a short concept map such as `user input -> work package -> evidence -> branch/default -> gate -> result`;
- make the report read path explicit: user value, demand scenarios, design fit, main flow, branch matrix, gaps, evidence;
- use a single strong flow diagram before dense detail;
- keep branch matrices compact and include a "review question" column;
- show implemented / designed-only / missing / authorization-required with distinct labels;
- put feedback controls or pending-decision prompts after the user has seen the evidence;
- avoid generic hero pages, decorative gradients, and repeated card grids.

Recommended HTML sections:

```text
header: thesis + concise status + visual purpose
30 seconds: key objects and relationships
user value: what the engineering system should create for the user
demand scenarios: current, designed-only, authorization-required
top-level design: core object, state authority, evidence, permissions, recovery
main flow: representative end-to-end process
branch matrix: input/evidence, default judgment, handling, risk gate, audit question
risk gates: actions that cannot be hidden behind "ready"
implementation boundary: implemented, designed, missing, needs authorization
pending decisions: user choices or policy defaults
evidence appendix: source map and missing evidence
```

Borrow `html-response` for comprehension structure and `reviewable-html-report` for formal review controls. Those skills do not own the flow-realization judgment.

## Supplement Task Package

Each follow-up task should include:

```text
id:
gap type: supplement | decision | evidence | route | defer
checkpoint: review | approval | execution | recovery
why it matters:
user-visible effect:
input artifacts:
output contract:
acceptance evidence:
owner skill:
not included:
```

Do not turn every gap into implementation work. Some gaps belong in pending decisions, evidence requests, or handoff recommendations.

## Near-Neighbor Routing

| Situation | Route |
|---|---|
| The user asks what value the product could create or how to reach a higher ceiling. | `user-value-architect` |
| The design exists but default answer, scoring, ranking, or user decision framing is weak. | `product-sense-refiner` |
| The agent is about to claim a high-risk task is complete. | `done-claim-gate` |
| The problem is structural duplication, missing invariant, or boundary repair. | `abstraction-architect` |
| The user wants exhaustive quality or release risk discovery. | `deep-flow-sweep` |
| The user only wants a readable webpage from already-formed content. | `html-response` |

## Common Failure Modes

- Producing a whole-project overview when the user needs one typical flow.
- Producing only a status matrix when the user needs a project/design audit report.
- Starting from internal modules instead of the user's burden, trust, control, or result-quality need.
- Failing to state the project thesis, so the user cannot judge whether the design is serving the right object.
- Treating top-level design defects as ordinary implementation TODOs.
- Treating design docs as implementation evidence.
- Hiding branch defaults in prose instead of a matrix.
- Making every uncertainty a blocking question instead of a pending decision.
- Overbuilding a workflow engine when a lightweight package or manifest would test the model.
- Reporting "ready" for review while implying risky execution is also ready.
- Letting unsupported statuses leak through a schema because the prose sounds confident.
- Collapsing review, approval, execution, and recovery into one vague "next step".
- Auto-starting downstream heavy skills instead of giving a handoff capsule.
