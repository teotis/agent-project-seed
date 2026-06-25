---
name: abstraction-architect
description: >
  Use for structural architecture analysis when complexity may come from missing invariants, duplicated domain representations, unstable boundaries, conversion glue, platform/configuration branching, or central orchestration bottlenecks.
  Grounds abstraction proposals in engineering evidence, counterexamples, migration seams, and falsifiable tests; produces an interactive HTML architecture report by default, with an optional Markdown source report on explicit request.
  Trigger for architecture review, foundational redesign, domain unification, API/boundary redesign, platform/configuration generalization, repeated state/model representations, and non-incremental simplification opportunities.
  Do not use as the sole method for ordinary bug fixes, urgent incident recovery, small performance tuning, or delivery-risk-dominated debt prioritization.
---

# Structural Abstraction Architect

## Purpose

Analyze a software system for opportunities where a better structural model can eliminate entire families of special cases, adapters, branching logic, lifecycle inconsistencies, artificial boundaries, scattered process state, or user-facing workflow burden.

This skill is **inspired by structural and universal abstraction methods associated with Grothendieck**, but it is not a historical essay and does not imitate a personality. Mathematical metaphors are only useful when they yield verifiable engineering simplification.

The central advanced move is **process spatialization**: when complexity appears as time, sequence, status drift, retries, approvals, orchestration, or environment-dependent behavior, ask whether those dynamics should instead be represented by one canonical structural object whose documents, logs, UI states, ledgers, prompts, and reports are consistent projections.

This move is not the default conclusion. Before searching for a canonical object, first run the **no new abstraction / local deletion wins** baseline: ask whether the work only needs delete obsolete branches, merge local duplication, improve interaction copy, or preserve the status quo with evidence. Escalate to a canonical model or process spatialization only when these lower-abstraction candidates cannot explain the same exception family, projection drift, or workflow burden, and the evidence points to a named invariant.

The default formal deliverable is an **interactive HTML architecture report** for user review, comparison, and feedback. A **Markdown source report** is an upgrade artifact and is produced only when the user explicitly requests an agent handoff or source-file delivery, or when HTML generation is infeasible. By default, this skill performs analysis only. It MUST NOT modify production code, tests, configuration, migrations, or infrastructure unless the user separately gives explicit authorization after reviewing a transition plan.

## Default Execution Intensity And Question Gate

This skill supports both **user-invoked** entry and **agent-active** auto-launch. The default depth is set by the entry source:

- **User-invoked** (the user names this skill, asks for an architecture review or abstraction analysis, or uses a synonym trigger): default to **Deep** depth. Run the full structural investigation, admissibility gate, candidate competition, and the formal HTML report.
- **Agent-active** (another agent or skill detects structural pressure and auto-launches this skill without an explicit user request): default to **Standard** depth. Cover the core pressure map, the highest-leverage candidate, and baseline competition; do not run Exhaustive-tier history archaeology, cross-repository variants, or long parallel investigations. Surface a hint that "upgrading to Deep requires user confirmation".
- **Exhaustive**: only when the user explicitly requests "exhaustive / full coverage / maximum effort" or equivalent; never the default.

Regardless of entry source, invocation authorizes the skill's full native execution mode for the chosen depth within its existing safety and mutation boundaries. Within that depth's envelope, **execute at full strength**: cover all core evidence faces, mandatory workflow steps, and the formal HTML report. Only downgrade, narrow, or focus the run when the user explicitly requests it.

Infer the target, scope, and evidence plan from the current workspace and supplied context; do not ask the user when a reasonable inference is possible. Continue useful analysis despite gaps and record them as `assumptions, unknowns, or coverage debt`.

Interrupt only when the target cannot be identified at all or when the next action requires separate authorization for implementation, migration, irreversible changes, account actions, publication, or pushing. Missing telemetry or partial context should reduce claim permission, not create a blocking questionnaire.

---

## Positioning: When to Use This Skill

### Strong fit

Use this skill when the system exhibits one or more of these structural signals:

- Many representations of what appears to be the same domain concept.
- Repeated adapters, conversions, schema mappers, mode switches, or platform branches.
- Boundaries that generate more glue than isolation value.
- A central orchestrator or God object coordinating logic that ought to compose locally.
- Workflow, orchestration, CI, approval, retry, or lifecycle state scattered across ledgers, logs, generated docs, dashboards, prompts, reports, or manual checklists.
- API pain revealed by many callers compensating for a provider's design.
- Similar workflows implemented separately across products, tenants, protocols, environments, or lifecycle stages.
- User workflows that require many commands, modes, handoffs, confirmations, training rules, or recovery loops because the system exposes controls rather than a task-level interaction model.
- A request for architecture review, domain unification, foundational refactoring, or non-incremental simplification.

### Weak fit or wrong first tool

Do not force this lens onto work whose primary constraint is operational urgency or implementation sequencing, such as:

- A production incident requiring immediate mitigation.
- A contained bug fix or localized performance bottleneck.
- A migration whose structural target is already known and whose remaining problem is rollout safety.
- Technical debt prioritization where ROI, blast radius, ownership, or delivery constraints dominate.

For these, use or hand off to **Pragmatic Renewal Architect**. The two skills are complements: this skill discovers higher-leverage structures; the pragmatic skill determines safe adoption paths.

---

## Invocation and Modes

When invoked:

1. Infer the target repository or directory from the current workspace; ask one minimal question only if no target can be identified.
2. Identify whether the request requires structural analysis, transition planning, or both.
3. Inspect the project only as deeply as evidence permits; clearly mark unavailable telemetry, history, runtime behavior, or business context.
4. Apply the Structural Abstraction method below.
5. Produce the report and provide its path plus a clickable `file://` URL. Open it only when the user requests a preview.

### Operating modes

| Mode | Default trigger | Deliverable | Modification permission |
|---|---|---|---|
| Structural Scan (Standard) | Agent-active default; or user explicitly requests a lighter scan; or evidence cannot support full analysis | Interactive HTML report with candidate map and missing-evidence list | No code changes |
| Full Architecture Analysis (Deep) | User-invoked default | Interactive HTML architecture report | No code changes |
| Exhaustive Architecture Analysis | User explicitly requests exhaustive / full-coverage / maximum-effort keywords | Interactive HTML report + multi-evidence cross-checks, history/cross-repository variants, parallel investigation | No code changes |
| Transition Handoff | User accepts one or more structural directions | Migration hypotheses for pragmatic evaluation | No code changes |
| Authorized Implementation | User explicitly approves implementation after reviewing a plan | Scoped code changes with verification | Only within explicit authorization |

Never silently jump from analysis to implementation.

---

## Investigation Kernel Adaptation

This skill follows the project Investigation Kernel, but this section is a standalone local adaptation: even when the single skill is copied out, it must still be able to perform structural investigation.

- **Concept version:** `investigation-kernel@v1`.
- **Derived from:** maintainer contract `investigation-kernel@v1`; this local section is self-contained and does not require the source contract at runtime.
- **Sync reference for maintainers:** the `abstraction-architect` registry row and `references/method_and_report_spec.md`.
- **Local projection:** Pressure Map, candidate competition, admissibility gate, and constraint reality filter.
- **Intentional differences:** this skill additionally requires the no-new-abstraction / local-deletion-wins baseline, process-spatialization counterexample competition, and the structural rewrite claim gate.
- **Fallback:** if the `reviewable-html-report` capability or repo-local report base is unavailable, use bundled `references/fallback.html` to deliver self-contained static HTML that preserves the core conclusion, TOC, stable section IDs, evidence appendix, Mermaid source fallback, and non-persistent feedback.

- **Analysis artifact root:** write formal analysis under `reports/abstraction-architect/` or an existing paired report directory; only write Markdown/HTML reports, evidence ledgers, candidate notes, transition handoffs, and review exports.
- **Analysis-only boundary:** by default do not modify production code, tests, configuration, migrations, dependency locks, or Git history. Implementation, migration, rewrite, or Git operations require new explicit user authorization after the report.
- **Evidence map:** build the structural pressure map first, covering key runtime paths, domain representations, workflow state, boundary glue, constraint evidence, and user-facing workflow burden before competing candidates.
- **Baseline before abstraction:** candidate competition must include the no-new-abstraction / local-deletion-wins baseline. If deleting obsolete branches, merging local duplication, or clarifying copy/interaction removes the pain, report that before escalating to a canonical object.
- **Coverage debt:** missing telemetry, history, runtime behavior, user context, external constraints, or migration evidence must be recorded as unknowns / coverage debt instead of being filled by structural intuition.
- **Claim permission:** without observed evidence, constraint reality filtering, admissibility gate results, and counterexample competition, do not claim that a structural rewrite, canonical model, 3x simplification, or whole category of complexity removal is established.
- **Budget-aware stop review:** a low-information wave triggers a stop review. Normal mode converges quickly, Deep mode rechecks the core pressure map, and Exhaustive mode stops only when marginal information gain for the remaining key unknowns becomes low.

---

## Core Workflow

1. Establish the target repository, requested mode, and evidence limits.
2. Inspect enough code, docs, tests, runtime paths, and user-supplied context to build an evidence ledger.
3. Use the detailed structural method in `references/method_and_report_spec.md` when evaluating candidates, especially for process spatialization, admissibility, candidate competition, and report requirements.
4. Produce the formal deliverable: write `structural_abstraction_architect_report_{YYYYMMDD}_{HHMM}.html` as the user-facing interactive review surface. Use the `reviewable-html-report` capability for shared report mechanics instead of reimplementing HTML infrastructure; repo-local `skills/reviewable-html-report/references/report_base.md` is an optional enhancement, not a standalone dependency. If that capability is unavailable, use bundled `references/fallback.html`. Only when the user explicitly requests a Markdown source for agent handoff / source-file delivery, or when HTML generation is infeasible, also write the same-basename `structural_abstraction_architect_report_{YYYYMMDD}_{HHMM}.md` sharing the same evidence ledger, proposal IDs, and conclusions.
5. If the user wants implementation after the report, switch only after explicit authorization and keep changes inside the accepted transition boundary.

## Report Delivery Contract

- **HTML is the default formal deliverable:** include the executive summary, evidence ledger, pressure map, candidate/proposal IDs, admissibility results, rejected/deferred abstractions, transition handoff, unknowns, verification notes, topology/process visuals, proposal cards, filters, expandable evidence, review/export controls, section index, and user feedback path.
- **Markdown is an upgrade artifact:** not produced by default; only when the user explicitly requests an agent handoff / source-file delivery, or when HTML generation is infeasible. When produced, it shares the same timestamp basename and the same evidence ledger, proposal IDs, and conclusions as the HTML.
- **Consistent naming:** when both are produced, formal reports use the same timestamp basename. If HTML cannot be generated, deliver Markdown as the fallback and state the HTML limitation.
- **Final response:** list the report path(s), provide a clickable `file://` URL for HTML, summarize the highest-leverage structural opportunity in one sentence, and state that no code was modified. Active browser opening is optional preview behavior.

## Resource Map

- `references/method_and_report_spec.md` — full structural method, admissibility gate, evidence rhythm, Markdown/HTML report schema, anti-goals, and execution flow.
- `references/discovery_patterns.md` — discovery prompts for unclear pressure maps or weak candidates.
- `references/fallback.html` — bundled self-contained HTML fallback.
- `reviewable-html-report` capability — shared HTML report mechanics when an interactive report is required; repo-local `skills/reviewable-html-report/references/report_base.md` is optional.

## Completion Standard

- Separate observed evidence, inference, and unknowns.
- Classify each proposal through the admissibility gate.
- Include rejected or deferred abstractions when relevant.
- When a Markdown source report is produced, keep it aligned with the HTML on the same evidence ledger, proposal IDs, and conclusions.
- Do not modify production code, tests, configuration, migrations, or infrastructure unless the user explicitly authorizes implementation after reviewing a transition plan.
