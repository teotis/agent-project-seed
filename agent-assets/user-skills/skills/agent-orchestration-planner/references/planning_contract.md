# Planning Contract

This reference owns planning-time decisions for `agent-orchestration-planner`.
Read it when splitting work into packages, deciding projection ownership,
classifying non-autonomous work, or defining landing/fallback behavior.

### Orchestration Contract Projection Model

Treat an orchestration as one execution contract with multiple projections. Do not add new columns, files, or duplicated lifecycle rules until you know which projection owns the information.

| Projection | Owns | Must not own |
|---|---|---|
| `INDEX.md` | Human-readable goal, authorization, policy, landing strategy, capability gates, and intended dependency contract. | Runtime readiness, package evidence, retry history. |
| `launchers/package-graph.tsv` | Machine-readable package topology, dependency type, wave, branch/worktree assignment, manual/finalize flags. | Narrative rationale, human evidence, dynamic state. |
| `status/state.tsv` | Current scheduler snapshot: package state, launch/session identifiers, branch/worktree/commit pointers, verification summary, integration/cleanup summary, and blocking fields needed for readiness decisions. | Long event history, rich QA evidence, release notes, external artifacts, discussion threads. |
| `status/events.jsonl` | Append-only event history, terminal failure fingerprints, retry accounting, launch/scratch/state-change audit trail. | Current readiness by itself, human acceptance evidence. |
| `status/<package-id>.md` | Human-readable package evidence, risks, changed files, verification details, blocker diagnosis, and recovery notes. | Machine dispatch truth or dependency unlocks without matching `state.tsv`. |
| `launchers/agent-prompts.md` | Local package execution contracts and tail-call instructions. | Global scheduling decisions or hidden fallback policy. |
| `packages/99-finalize.md` and `FINAL_REPORT.md` | Local-to-global gluing judgment: verify package evidence, merge eligibility, task-level outcome, and final audit narrative. | Unverified agent claims or scheduler mutation outside the orchestrator. |
| `scratch/` | Temporary non-sensitive exchange material. | Scheduler truth, acceptance evidence, secrets, or release proof. |

Design rules:
- When adding information, first decide which projection owns it. Add a new `state.tsv` column only if the scheduler needs it to compute readiness, blocking, verification, integration, or cleanup.
- When adding an execution environment, model it as capability variation over the same package lifecycle and finalize rules. Do not copy a separate lifecycle for manual, Claude background, CI runner, or another agent platform.
- When projections disagree, report the orchestration as invalid or blocked until repaired. Do not silently infer success from the most optimistic artifact.
- A useful extension should pass a deformation test: adding one new state, runner, manual gate, failure class, or evidence channel should require bounded edits to the owning projection and its validators, not scattered changes across unrelated artifacts.

## Workflow

### 1. Inspect Or Create Package Materials

Before generating artifacts:
- Read the user request.
- Read existing plan/package docs if provided.
- Search the project planning location for recent related task-package folders, INDEX files, plan docs, status notes, or design notes before creating a new graph.
- Inspect enough local context to split work into concrete packages when package docs do not exist.
- Check current git status.
- Ensure every functional package has: Package ID, allowed/forbidden paths, dependencies, acceptance criteria, verification commands, expected evidence, branch/worktree policy, and unlock conditions.
- Apply the Projection Model before adding custom status fields, generated files, runner modes, evidence channels, or manual gates. Name the owning projection and the drift rule for each addition.
- Run a capability preflight before finalizing the graph: for every package, verification command, and acceptance criterion, identify whether Claude Code can execute it autonomously in the planned environment. Anything requiring a physical device, human visual judgment, external account approval, credential entry, proprietary console access, paid service approval, remote hardware, or user-only decision must not be assigned to an auto-launched functional package.
- Default to task packages that agents can complete themselves. If an `external-assist` item is essential to the goal, cannot be ignored, and has no agent-verifiable substitute, stop before generating the output kit and ask the user to choose whether to approve the manual gate, change scope, or abort the orchestration.
- Define a landing strategy before launching work: primary success path, preapproved fallback paths, explicit non-goals, abort conditions, and any packages that may remain valid as independent merge candidates if the main plan fails.

Planning-location search is not optional preamble. Check the repository's documented planning home first, such as `docs/plans/`, `codex/agent_plans/`, or any path named by AGENTS/CLAUDE/project docs. Recent package folders may already contain the problem statement, accepted constraints, prior attempts, failure evidence, and a package index that should be updated instead of replaced. If a relevant package exists, decide explicitly whether to amend it, create a follow-up package in the same folder, or start a new orchestration with links back to the prior one.

### Capability Preflight

Prevent non-autonomous work from becoming a surprise blocker. For each candidate package and acceptance criterion, classify it as:

| Class | Meaning | Orchestration treatment |
|---|---|---|
| `autonomous` | Claude Code can execute it with local tools and allowed permissions. | Put it in a normal functional package. |
| `agent-verifiable substitute` | Claude cannot perform the final real-world check, but can produce meaningful evidence such as tests, builds, APKs, logs, screenshots, emulator checks, or checklists. | Put the substitute in an implementation package and state what remains externally unverified. |
| `external-assist` | Requires a human, Codex multimodal/device access, physical hardware, credentials, external approval, or a service console Claude cannot access. | Predeclare it in the INDEX as external assistance or a manual release gate; do not auto-launch it as Claude work. |

Examples of `external-assist`: real-device camera UI validation, hardware-in-the-loop checks, app-store release approval, CAPTCHA/account onboarding, entering private API keys, visual QA that needs user-owned media, and security approval outside the repository.

Design rules:
- Do not make downstream implementation waves depend on external-assist validation unless the user explicitly says it is a mandatory release gate.
- If external validation is required before release, model it as a known manual gate from the first output, with owner, exact commands/checklist, expected evidence, and how to report results back. The automation may stop at "ready for external QA"; it must not pretend the gate passed.
- If the user has not already approved a blocking external-assist gate with owner and expected evidence, do not include it in the generated kit. Ask first, then generate artifacts only after the user's decision is clear.
- If external validation is not required for implementation progress, keep it outside the package graph or as `manual=1` documentation that does not block autonomous implementation waves.
- For Android or camera work, package agents should produce APK paths, install commands, logs, emulator checks, and focused tests; real-device pass/fail remains external evidence unless the active environment actually provides that device workflow.

### User-Visible Delta Planning

For packages that intentionally affect UI, copy, workflow, visual output, user
trust, or other user-facing behavior, include a **User-Visible Delta Ledger** in
the package doc. This is a discretion model, not a change freeze.

Classify the expected delta:

| Class | Meaning | Orchestration treatment |
|---|---|---|
| `none` | No user-visible behavior should change. | Normal verification is enough; unexpected visible drift should be recorded as risk. |
| `expected` | The visible change is the package goal. | Package may implement and verify it within allowed paths/surfaces. |
| `acceptable-adjacent` | Small neighboring changes are needed to solve the assigned problem. | Package may proceed if it records the rationale, changed surfaces, and preservation evidence. |
| `decision-required` | The change affects a protected primary workflow, first-screen composition, navigation model, release promise, or explicit non-goal. | Do not hide it inside the package outcome; split, downgrade, block for user/product decision, or use an approved fallback. |

Design rules:
- Give agents bounded discretion for small adjacent changes that improve the assigned user problem.
- Do not require manual approval for every minor layout, copy, or state adjustment.
- Do require explicit recording when implementation drifts beyond the target surface.
- Protected surfaces should be project-specific and concrete, such as "main camera first screen", "checkout completion flow", or "account deletion confirmation".
- `99-finalize` should review UX delta as `expected`, `acceptable-adjacent`, or `decision-required`; only the last class forces a product decision or split.

### Landing Strategy And Failure Plan

No orchestration plan is guaranteed to land. Treat non-landability as a first-class outcome, not as an embarrassing exception hidden inside a package status file.

Every orchestration must declare:
- **Primary landing path**: the complete outcome that counts as the main plan landing.
- **Preapproved fallback paths**: acceptable secondary plans, ordered by preference, with their own acceptance criteria. Do not invent a fallback during failure unless the user explicitly approves it or the INDEX already authorizes it.
- **Unacceptable degradation**: shortcuts that must not be shipped even if they make tests pass.
- **Abort conditions**: evidence that the current plan is no longer worth retrying, such as a false product assumption, missing platform capability, unavailable dependency, repeated identical failure fingerprint, or implementation cost outside the user's requested scope.
- **Independent merge candidates**: packages that can still be reviewed as standalone fixes if the main plan fails. Declare these before execution with why they are independent, their allowed paths, and their standalone verification.

Default policy:
- If the main plan fails and no fallback is preapproved, the orchestration outcome is `failed-no-merge`.
- If a preapproved fallback lands, the outcome is `landed-with-approved-fallback`, not plain success.
- If code is complete but a declared external release gate remains, the outcome is `ready-for-external-gate`.
- If the main plan fails but some packages look independently useful, `99-finalize` may list them only as `failed-with-candidate-independent-fixes`; it must not merge them automatically unless the INDEX predeclared them as independent merge candidates and their standalone verification passes.
- If no package is safely independent, preserve branches/worktrees, record the failure, and merge nothing.

When a package discovers that the plan assumption behind its work is wrong, it should mark itself `blocked` and classify the failure. Use concise categories such as: `capability-gap`, `invalid-requirement`, `external-dependency`, `verification-failure`, `merge-conflict`, `design-invalid`, `cost-out-of-scope`, or `unknown-needs-investigation`. The recovery hint should say whether to retry, launch an investigation package, switch to a named fallback, ask the user, or abort the orchestration.
