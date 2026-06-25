---
name: deep-flow-sweep
description: Use when a project needs a high-budget, analysis-only quality sweep across main flows, reliability, performance, tests, observability, security, governance, recent changes, long-term drift, and follow-up task packaging.
---

# Deep Flow Sweep

## Mission

Run a broad, evidence-backed quality sweep before the user decides what to fix.

This skill trades time and context for coverage. It maps the project's main flows, imagines realistic failure scenarios, gathers evidence from code, tests, docs, history, runtime probes, and release surfaces, then ranks risks and leaves follow-up task packages. It is an analysis skill, not an implementation skill.

The central question is:

> Where can the project fail in real use, what evidence supports that risk, and what should be verified or packaged next?

## Default Execution Intensity And Question Gate

This skill is **user-invoked only**: it must only be launched after an explicit user request (the user names this skill, asks for a deep flow sweep / wide-coverage quality audit, or uses a synonym trigger). Other agents and skills MUST NOT auto-launch this skill; they may surface a recommendation and wait for the user to authorize a full sweep. There is no "partial sweep" or lightweight active-launch entry.

Once explicitly launched, invocation authorizes the skill's full native execution mode within its existing safety and mutation boundaries. Default to full-strength **Exhaustive** coverage with the `balanced` focus, all applicable risk families, and concurrent or long-running analysis when useful. Only downgrade, narrow, or focus the run when the user explicitly requests it.

Infer the target, envelope, focus, and evidence plan from the current workspace and supplied context; do not ask the user when a reasonable inference is possible. Continue useful analysis despite gaps and record them as `assumptions, unknowns, or coverage debt`.

Interrupt only when the target cannot be identified at all or when the next action requires separate authorization for implementation, irreversible changes, account actions, publication, or pushing. Missing tools, credentials, devices, telemetry, or external access should become coverage debt rather than a blocking questionnaire.

## When To Use

Use this skill when the user asks for:

- exhaustive or high-budget quality analysis;
- pre-release risk discovery or pre-merge risk traversal;
- main-flow QA across user-visible or release-critical paths;
- reliability, recovery, state, concurrency, performance, test-effectiveness, observability, security, dependency, CI, release, or governance checks;
- recent-change archaeology, long-term drift analysis, or cross-session follow-up;
- evidence-backed task packages rather than immediate fixes.

Do not use it as the primary skill for:

- one known bug with reproduction steps;
- ordinary code review of a small diff;
- a narrow architecture decision;
- cosmetic cleanup or naming preference;
- direct implementation, PR cleanup, or refactoring unless the user separately authorizes follow-up execution after the sweep.

## Analysis-Only Contract

Invoking this skill latches the run into analysis-only mode.

- Do not modify product source, tests, configuration, migrations, dependency locks, generated product assets, or Git history.
- Allowed writes are analysis artifacts only: reports, manifests, sub-ledgers, evidence indexes, and task packages.
- A severe finding does not unlock implementation.
- Editing project files requires a new explicit user request after the sweep result is presented.

## Budget Envelopes

Use **Exhaustive** by default. Choose a lighter envelope only when the user explicitly requests a quick, focused, narrower, or lower-cost sweep.

| Envelope | Trigger | Minimum coverage |
|---|---|---|
| Normal | user explicitly requests a quick or focused sweep | main flow map, highest-risk scenarios, focused evidence, residual coverage debt |
| Deep | deep, broad, high-confidence analysis | Normal plus recent-change archaeology, root-cause evidence, cross-surface checks |
| Exhaustive | exhaustive, maximum coverage, long-running sweep | Deep plus long-term trends, cross-session intelligence, optional parallel sub-sweeps, and explicit stop ledger |

Default to Exhaustive. Deep and Normal are explicit downgrades. Budget buys optionality, not permission to run every possible tool.

## Focus Profiles

Default to `balanced`. If the user names a focus, prioritize one or two profiles without dropping main-flow and reliability baselines.

| Focus | Use when |
|---|---|
| `balanced` | default full-project sweep |
| `main-flow` | user path, critical feature, UI, CLI, API, or release-critical workflow |
| `reliability` | recovery, retry, state consistency, concurrency, idempotency, partial failure |
| `performance` | latency, startup, throughput, memory, CPU, battery, capacity, regression |
| `security` | trust boundaries, authorization, input handling, secrets, supply chain, AI tool risk |
| `observability` | errors, logs, metrics, traces, diagnosability, recovery signals |
| `test-effectiveness` | regression protection, assertion quality, flaky tests, risk-to-test mapping |
| `project-governance` | CI, release, artifact provenance, docs, agent parity, ownership |
| `requirement-conformance` | user request, issue, plan, or acceptance criteria versus implementation |

Focus changes allocation and report ordering; it never permits skipping release-critical flows, evidence quality, recovery, or unverified-claim labeling.

## Project Archetype Routing

Before selecting detailed checks, build a short Project Risk Profile. Archetype signals are priors, not conclusions: they route attention and method choice, but every finding still needs evidence from a reachable project surface.

Record an applicability disposition for important risk families:

| Disposition | Meaning |
|---|---|
| `applicable` | A concrete project surface exists. |
| `possibly applicable` | Signals exist, but more context is needed. |
| `not applicable` | The surface is absent, with a recorded reason. |
| `deferred` | The surface exists, but credentials, devices, data, or authorization are unavailable. |
| `untriaged` | Scope or budget prevented a confident decision. |

Common archetypes include Web / SaaS / API, Mobile / Android / Device, Agent / Tooling / Automation, Library / Framework, and Public release / split repository. Compose archetypes when multiple signals apply, and do not let a familiar archetype suppress unusual flows discovered in the actual code.

## Workflow

### 1. Establish Scope And Manifest

Record:

- target repository, branch, current dirty state, and nested repositories;
- budget envelope and selected focus profiles;
- project risk profile: archetypes, triggered risk families, and important applicability dispositions;
- main user or release goals;
- available commands, environments, browsers, devices, credentials, and external blockers;
- artifact root for the sweep report.

If the worktree is dirty, preserve unrelated user changes and avoid drawing conclusions from files outside the requested scope unless they affect the sweep.

### 2. Build The Flow Map

Identify concrete main flows:

- entry points: screens, routes, CLI commands, background jobs, APIs, release scripts;
- lifecycle: initialize, configure, execute, persist, recover, teardown;
- data path: input, validation, transformation, storage, output, side effects;
- environment path: local, CI, browser, device, production-like dependency, nested repo;
- success oracle: the observable evidence that the flow actually completed.

For each flow, record key files, symbols, expected success signal, likely failure surfaces, and available verification commands.

### 3. Generate Failure Scenarios

For every important flow, consider:

- happy path;
- empty or first-run state;
- invalid input;
- skipped, repeated, canceled, or retried state transition;
- concurrency and timing;
- environment drift;
- missing or slow external dependency;
- regression from recent changes;
- weak observability;
- recovery after failure;
- agent or automation parity gaps.

A useful predicted failure must imply an observable check: command, test, trace, browser/device path, static proof, or explicitly deferred manual gate.

### 4. Run Evidence Waves

Use the cheapest reliable probes first:

- read tests around the flow and inspect assertion quality;
- run focused tests, builds, linters, type checks, scripts, benchmarks, or browser/device checks when available;
- inspect logs, reports, CI/workflow files, release scripts, dependency manifests, docs, and recent commits;
- use static searches only as candidate generators, then trace the reachable flow before ranking.

After each wave, record:

- new high-risk candidates;
- findings strengthened or weakened by evidence;
- unknowns closed;
- unscanned critical surfaces;
- whether another wave is likely to change the decision.

Stop expansion after two low-information waves unless a release-critical flow, trust boundary, or explicitly requested focus remains unexamined.

### 5. Recent-Change And History Review

For Deep and Exhaustive sweeps:

- compare recent commit subjects to actual diffs;
- look for compensating commits that fix bugs introduced shortly before;
- check whether tests evolved with production behavior;
- compare docs, AGENTS-style rules, and commands against reality;
- verify past findings before inheriting their severity.

Past severity is not current evidence. Re-rank every historical issue from current facts.

### 6. Rank Findings

Separate severity, confidence, and disposition.

| Dimension | Values | Meaning |
|---|---|---|
| Severity | `P0`, `P1`, `P2`, `P3` | impact if true |
| Confidence | `high`, `medium`, `low` | evidence strength |
| Disposition | `block`, `package`, `investigate`, `consider`, `info`, `drop` | next action |

Direct evidence is required for P0/P1:

- observed failure;
- reproducible runtime result;
- strong static proof on a reachable critical path;
- verified security exposure or release blocker.

Scanner matches, TODOs, weak logs, vague commits, low coverage, or architectural taste can nominate a candidate, but they do not establish P0/P1 alone.

### 7. Package Follow-Up Work

Convert actionable findings into task packages. Each package should include:

- problem statement;
- severity, confidence, and disposition;
- evidence and file references;
- expected user, release, reliability, security, or maintenance impact;
- proposed verification gate;
- falsification notes and false-positive risk;
- likely owner or module boundary when known;
- rollback or safety considerations when relevant.

Broad findings become escalation briefs:

- `abstraction-architect` for missing invariants or duplicated representations;
- `renewal-architect` for legacy migration, compatibility, rollout economics, or ownership constraints;
- `product-sense-refiner` for technically correct flows that still produce poor user decisions;
- `agent-orchestration-planner` when follow-up work needs durable multi-agent coordination.

## Output Contract

For formal sweeps, produce paired reports by default. An explicit user request for chat-only or no files may downgrade delivery, with unpersisted evidence and coverage debt stated in the response:

- Markdown source report: `deep_flow_sweep_report_{YYYYMMDD}_{HHMM}.md`
- HTML review surface: `deep_flow_sweep_report_{YYYYMMDD}_{HHMM}.html`

The Markdown report is the source of truth. The HTML report may visualize, filter, or collapse sections, but it must not introduce conclusions missing from the Markdown.

Use the `reviewable-html-report` capability when available. Otherwise use bundled `references/fallback.html` to produce self-contained HTML with a TOC, stable section IDs, evidence appendix, Mermaid source fallback, and non-persistent feedback. Provide the path and a clickable `file://` URL; do not actively open a browser unless the user requests a preview.

Required sections:

```markdown
## Sweep Summary
- Scope:
- Budget:
- Focus profiles:
- Main flows inspected:
- Findings by severity / confidence / disposition:
- Stop reason:

## Flow Map

## Evidence Waves

## Findings

## Task Packages

## Verification

## External Or Deferred Checks

## Residual Risks And Escalations
```

If no concrete finding survives the evidence gate, say that clearly. A clean bill of health is a valid outcome.

## Verification Ledger

End with commands and outcomes:

- tests/builds/checks run and key result;
- checks not run and why;
- browser, device, account, network, CI, or production checks marked external when unavailable;
- scripts or package validators run for structured task packages when applicable.

## Common Mistakes

- Fixing code during the sweep.
- Treating scanner output as a finding without flow evidence.
- Treating Exhaustive as an obligation to run every heavy method.
- Inheriting old P0/P1 labels from history without current evidence.
- Claiming browser, device, production, or account checks passed when they were not actually run.
- Padding a clean report with trivial issues.
- Using this broad sweep when a focused debugging, architecture, renewal, or product-sense skill would answer the user's real question faster.

## Completion Standard

A deep flow sweep is complete only when the scope, budget, focus profile, flow map, evidence waves, findings, verification, deferred checks, task packages or escalations, and stop reason are explicit. Every serious claim must have evidence, confidence, and a falsification or verification path.
