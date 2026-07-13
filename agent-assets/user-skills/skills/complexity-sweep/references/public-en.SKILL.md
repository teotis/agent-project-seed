---
name: complexity-sweep
description: Use for explicit analysis-only complexity sweeps across micro, meso, and macro code structure, with evidence-backed simplification findings, behavior-preservation checks, reviewable reports, and follow-up task packages. Do not refactor inside the sweep.
---

# Complexity Sweep

## Mission

Audit code complexity across micro, meso, and macro levels, identify structures that materially increase comprehension cost, change cost, onboarding drag, or bug risk, and package evidence-backed simplification work. This skill analyzes only. It does not directly refactor production code.

## Invocation Contract

Use this skill only when the user explicitly asks for a complexity audit, complexity sweep, simplification sweep, bloated-design scan, or similarly broad analysis. Do not auto-start it from ordinary debugging, planning, pull request review, or architecture work. If you notice a complexity signal outside an explicit sweep, record a concise handoff finding instead.

Ask the user only when the target scope cannot be identified or the next action would require implementation, irreversible operations, account changes, publishing, pushing, or another permission boundary.

## Safety

- Stay analysis-only unless the user separately authorizes implementation.
- Write only reports, manifests, evidence ledgers, task packages, review exports, or handoff notes.
- Do not modify product source, tests, configuration, dependency locks, generated assets, or git history during the sweep.
- Metrics and scanners are prioritization signals, not findings by themselves.
- High-severity findings require current direct evidence of real bug risk, repeated change cost, onboarding drag, broken contracts, or key-path coupling pressure.

## Budget Modes

- **Normal:** scope map plus high-value pattern checks.
- **Deep:** Normal plus root-cause analysis, history review, and constraint-survival checks.
- **Exhaustive:** Deep plus trend review, variants, and independent probes when the information gain remains high.

Budget buys method choice, not a requirement to run every analyzer. Stop expanding when repeated probes add little evidence, close no important unknowns, and reveal no new high-value candidates.

## Core Workflow

### 1. Establish Scope

Read repository instructions, git state, validation commands, relevant code, existing reports, and likely project boundaries. Record scope, budget, current state, dirty work, tools used, and blockers.

### 2. Build A Coverage Matrix

Before presenting findings, track:

- structural level: micro, meso, macro, history, verification;
- comprehension path or user flow;
- inspected artifacts;
- evidence status;
- unknowns and coverage debt;
- next method and expected information gain.

Incomplete paths should become investigation items, deferred checks, or coverage debt, not inflated findings.

### 3. Map Complexity Levels

Inspect at three levels:

- **Micro:** functions, classes, branches, nesting, parameters, side effects, naming, duplication.
- **Meso:** module dependencies, cycles, cohesion, duplicated validation, duplicated errors, config scattering, shotgun surgery.
- **Macro:** data flow, orchestration, boundaries, abstraction depth, lifecycle, workflow state, and cross-cutting consistency.

Use static probes when available, but interpret counts through real comprehension paths and change impact.

### 4. Collect Evidence And Root Causes

Choose methods based on evidence gaps: change-coupling review, variant search, architecture fitness checks, cognitive walkthroughs, abstraction economics, mutation sampling, or history comparison.

For each candidate, record:

- location and pattern;
- observed or measured signal;
- why it increases comprehension cost, change cost, defect risk, or onboarding drag;
- counter-evidence and false-positive guard;
- verification gap;
- likely root cause or compensation chain.

Project-specific complexity lenses are allowed. Name the lens, trigger, evidence artifact, false-positive guard, and disposition.

### 5. Rank And Falsify

Separate severity, confidence, and disposition. Every important finding needs a falsification route: what evidence would prove it is only style preference, a deliberate compatibility tradeoff, or lower priority than it first appeared.

Run behavior-preservation thinking before proposing simplification. A simplification package should state what behavior, compatibility, performance, data, or user contract must survive.

### 6. Package Simplification

Convert actionable hotspots into follow-up task packages. Each package should include:

- finding ID and evidence IDs;
- target paths and forbidden paths;
- expected simplification;
- behavior-preservation vector;
- verification gate;
- blast radius;
- rollback safety;
- falsification route;
- owner skill or recommended executor.

Do not implement inside the sweep.

### 7. Route Without Auto-Chaining

Suggest a next skill or workflow only as a handoff:

- local module or interface design: codebase design;
- duplicated representations or missing invariants: structural abstraction analysis;
- legacy migration and rollback economics: renewal planning;
- broad release quality risk: deep flow analysis;
- small concrete cleanup: ordinary implementation after user authorization.

Do not automatically start another heavy workflow.

## Output Contract

Use decision-first output. Default to three to five high-priority patterns, simplification directions, or hotspots unless active bugs or release blockers require more.

A saved sweep should include paired Markdown and HTML when practical. The Markdown is the source of truth. The HTML must not introduce conclusions absent from the Markdown.

In chat, include:

- verdict and scope;
- top findings with severity and confidence;
- strongest evidence;
- coverage debt;
- recommended task packages;
- verification or behavior-preservation gates;
- explicit statement that no refactor was performed unless separately authorized.

## Completion Gate

Before finishing, confirm that scope, budget, evidence, coverage debt, findings, false-positive guards, behavior-preservation requirements, task packages, and stop reason are recorded. If no concrete finding survives evidence review, say so directly and provide a clean complexity bill of health for the inspected scope.
