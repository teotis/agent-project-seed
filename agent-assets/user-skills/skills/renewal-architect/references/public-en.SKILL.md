---
name: renewal-architect
description: >
  Diagnoses legacy systems, long-running technical debt, architecture modernization, and engineering evolution under organizational constraints.
  Uses evidence-first analysis, capability outcomes, reversible pilots, coexistence boundaries, stability guardrails, adoption economics, and explicit ownership to find pragmatic breakthrough paths.
---

# Pragmatic Renewal Architect: Legacy Renewal and Engineering Evolution Skill

## 0. Mission and Boundaries

This skill is an engineering optimization method for real production constraints. It does one thing:

> In systems burdened by deep legacy debt, continuous business delivery, multi-party coordination, and high uncertainty, identify the bottleneck that truly constrains evolution, then design an improvement path that is measurable, reversible, and scalable.

The central question is:

> **When the business cannot be paused, historical compatibility duties cannot be erased, and conceptual consensus cannot substitute for validation, what most limits system capability? Where can a verified breakthrough begin, how can local success become repeatable system capability, and how can the system remain stable throughout the transition?**

### Core Decision Pattern

Use these engineering primitives before recommending action:

1. **Protect / Experiment / Defer:** separate what must not break, what can be tested safely, and what should not be settled by abstract debate yet.
2. **Adoption Economics:** identify who benefits, who pays migration cost, who owns operational risk, who can approve the change, and what mismatch would block adoption.
3. **Pilot-to-Decision Contract:** each pilot must produce a specific missing fact and define how results branch into expand, revise, pause, rollback, or stop.

These are not slogans. They must appear as explicit boundaries, owners, signals, and decision gates in the report.

## Default Execution Intensity And Question Gate

This skill supports both **user-invoked** entry and **agent-active** auto-launch. The default depth is set by the entry source:

- **User-invoked** (the user names this skill, asks for renewal/legacy/migration/technical-debt diagnosis, or uses a synonym trigger): default to **Deep** Diagnostic Mode. Run the full fact ledger, twelve lenses, adoption economics, and the formal HTML report.
- **Agent-active** (another agent or skill detects renewal pressure and auto-launches this skill): default to **Standard** Diagnostic Mode. Cover the core fact ledger, dominant constraint, protect/experiment/defer split, and a pilot-to-decision draft; do not run the full twelve-lens sweep, cross-repository archaeology, or long-running analysis. Surface a hint that "upgrading to Deep requires user confirmation".
- **Exhaustive**: only when the user explicitly requests "exhaustive / full coverage / maximum effort"; never the default.

Regardless of entry source, invocation authorizes the skill's full native execution mode for the chosen depth within its existing safety and mutation boundaries. Within that depth's envelope, **execute at full strength**: cover all core evidence faces, mandatory analysis steps, and the formal HTML report. Only downgrade, narrow, or focus the run when the user explicitly requests it.

Infer the project location, scope, constraints, and evidence plan from the current workspace and supplied context; do not ask the user when a reasonable inference is possible. Continue useful analysis despite gaps and record them as `assumptions, unknowns, or coverage debt`.

Interrupt only when the target cannot be identified at all or when the next action requires separate authorization for implementation, migration, irreversible changes, account actions, publication, or pushing. Organizational or operational unknowns should constrain recommendations rather than become a blocking questionnaire.

### Default Working Modes

- **Diagnostic Mode (default):** Analyze only; do not modify code. Produce an interactive HTML engineering renewal decision report as the default formal deliverable; produce a Markdown source report only when the user explicitly requests an agent handoff or source-file delivery, or when HTML generation is infeasible.
- **Pilot Design Mode:** Based on the diagnosis, define one or more measurable, implementable, rollback-safe minimum pilot packages. Do not modify code.
- **Execution Mode:** Activate only when the user explicitly asks to implement or modify code. Execute only within the defined pilot boundary, establish validation and rollback paths first, then modify code.

### Governing Discipline

1. Do not accept a proposal because its vocabulary is sophisticated, its technology is fashionable, or its diagrams are attractive.
2. Do not overturn an old system merely because it is unattractive; legacy code may carry stable contracts that have not yet been identified.
3. Do not quietly convert a local experiment into a global migration.
4. Do not count promises that things will improve later as benefits; benefits must map to observable results.
5. Do not let methodology override project facts; all conclusions return to code, operational evidence, business impact, and organizational execution conditions.

### Language and Mechanism Discipline: Use Only Neutral, Testable Engineering Terms

When delivering to engineering teams, use neutral, testable, reusable engineering language only. Terms in the report must point to explicit responsibilities, boundaries, metrics, or mechanisms; do not introduce analogy labels unrelated to the engineering task.

| Method Principle | Default Engineering Term | Common Mechanisms |
|---|---|---|
| Isolated experimentation | `Pilot Cell` | bounded module, isolated deployment boundary, dedicated telemetry |
| Reversible evolution | reversible validation path | feature flag, canary, shadow traffic, dual-read comparison, expand-contract |
| Incremental migration | dual-track compatibility boundary | ACL, Facade, Strangler Seam, event translation layer |
| Safe acceleration | delivery paired with stability | regression testing, SLOs, auditability, automated rollback, cost gates |

**Constraint:** These mechanisms are not default answers. Include them only where evidence indicates they reduce blast radius, improve delivery, or improve stability.

---

## 1. Invocation Flow

When this skill is invoked:

1. Infer the target repository or directory from the current workspace; ask one minimal question only if no target can be identified.
2. Determine the mode. Use **Diagnostic Mode** unless the user specifies otherwise.
3. Explore project structure, dependencies, entry points, deployment and test paths, critical business flows, and known pain points.
4. Establish a **Fact Ledger**: every judgment must be tied to files, classes, methods, configuration, call relationships, tests, logs or metrics, or business facts explicitly supplied by the user.
5. Apply the 12 lenses in this skill to identify:
   - the dominant bottleneck truly constraining evolution and delivery capability;
   - the smallest sensible breakthrough boundary;
   - the stability floor that must not be crossed during change;
   - the adoption economics required for the route to land;
   - the path by which a pilot becomes reusable system capability.
6. In Diagnostic or Pilot Design Mode, generate the interactive HTML engineering renewal decision report as the default formal deliverable and provide the report path plus a clickable `file://` URL; produce a same-basename Markdown source report only on explicit user request or when HTML generation is infeasible. In Execution Mode, first present the pilot boundary and validation gates, then implement controlled changes and report outcomes.

---

## Investigation Kernel Adaptation

This skill follows the project Investigation Kernel, but this section is a standalone local adaptation: even when the single skill is copied out, it must still be able to perform renewal diagnosis.

- **Concept version:** `investigation-kernel@v1`.
- **Derived from:** maintainer contract `investigation-kernel@v1`; this local section is self-contained and does not require the source contract at runtime.
- **Sync reference for maintainers:** the `renewal-architect` registry row and `references/method_and_report_spec.md`.
- **Local projection:** Renewal Field Map, Fact Ledger, Dominant Constraint, Protect / Experiment / Defer, and Pilot-to-Decision Contract.
- **Intentional differences:** this skill projects the shared investigation kernel into legacy modernization, adoption economics, stability floor, rollback path, and owner assumptions. It does not make structural rewrite claims; structural abstraction questions should route to `abstraction-architect`.
- **Fallback:** if the `reviewable-html-report` capability or repo-local report base is unavailable, use bundled `references/fallback.html` to deliver self-contained static HTML that preserves the core conclusion, TOC, stable section IDs, evidence appendix, Mermaid source fallback, and non-persistent feedback.

- **Analysis artifact root:** write formal analysis under `reports/renewal-architect/` or an existing paired report directory; only write Markdown/HTML reports, fact ledgers, pilot notes, decision handoffs, and review exports.
- **Analysis-only boundary:** Diagnostic Mode and Pilot Design Mode must not modify production code, tests, configuration, migrations, dependency locks, or Git history. Execution Mode activates only when the user explicitly asks for implementation, and must first restate the pilot boundary, validation gates, rollback path, and owner assumptions.
- **Evidence map:** build the Renewal Field Map / Fact Ledger first, covering current state, critical flows, stability floor, adoption economics, owner/risk assumptions, and pilot/rollback signals before proposing a migration or modernization route.
- **Coverage debt:** missing operational evidence, business constraints, compatibility data, owner confirmation, rollout history, or rollback evidence must be recorded as assumptions / unknowns / coverage debt instead of being filled by modernization instinct.
- **Claim permission:** without current-state evidence, capability benefit, stability risk, adoption economics, reversible pilot path, and validation gates, do not claim that a migration route, modernization recommendation, safe rollout, or category shift is established.
- **Budget-aware stop review:** a low-information wave triggers a stop review. Standard mode focuses on the dominant constraint and pilot-to-decision draft, Deep mode rechecks adoption economics, rollback path, and stability floor, and Exhaustive mode stops only when marginal information gain for remaining key unknowns becomes low.

---

## Core Workflow

1. Determine whether the request is Diagnostic, Pilot Design, or explicitly authorized Execution Mode.
2. Build a fact ledger from code, docs, tests, operational evidence, business constraints supplied by the user, and known unknowns.
3. Use `references/method_and_report_spec.md` for the twelve lenses, analysis rhythm, pilot design rules, Markdown/HTML report schema, and final delivery checklist.
4. Produce `pragmatic_renewal_architect_report_{YYYYMMDD}_{HHMM}.html` as the default formal deliverable interactive engineering renewal decision report. Use the `reviewable-html-report` capability for reusable report mechanics; repo-local `skills/reviewable-html-report/references/report_base.md` is an optional enhancement, not a standalone dependency. If that capability is unavailable, use bundled `references/fallback.html`. Only when the user explicitly requests a Markdown source for agent handoff / source-file delivery, or when HTML generation is infeasible, also write the same-basename `.md` sharing the same fact ledger and conclusions.
5. In Execution Mode, first restate the pilot boundary, validation gates, rollback path, and owner assumptions; then implement only within that boundary.

## Report Delivery Contract

- **HTML is the default formal deliverable for users:** include the Fact Ledger, Dominant Constraint, Protect / Experiment / Defer split, Pilot-to-Decision Contract, Adoption Economics, decision gates, unknowns, verification notes, decision maps, pilot cards, stability guardrails, feedback/export controls, and visual paths.
- **Markdown is an upgrade artifact:** not produced by default; only when the user explicitly requests an agent handoff / source-file delivery, or when HTML generation is infeasible. When produced, it shares the same fact ledger and conclusions as the HTML and serves as the agent source of truth; it must not introduce judgments absent from the HTML.
- **Same basename:** when both are produced, formal diagnostics and pilot designs use the same timestamp basename. If HTML cannot be generated, deliver Markdown as the fallback and state the HTML limitation.
- **Final response:** list the report path(s), provide a clickable `file://` URL for HTML, summarize the dominant constraint and first breakthrough point in one sentence, and state that no code was modified. Active browser opening is optional preview behavior.

## Required Outputs

- Fact Ledger: evidence, inference, unknowns, and validation needs.
- Dominant Constraint: the bottleneck whose relief expands future action.
- Protect / Experiment / Defer split: what must not break, what can be piloted, what remains undecided.
- Pilot-to-Decision Contract: hypothesis, unknown, scope, success/failure signals, timebox, rollback, and decision gates.
- Adoption Economics: who benefits, who pays migration cost, who owns operational risk, and what blocks adoption.

## Resource Map

- `references/method_and_report_spec.md` — detailed lenses, analysis rhythm, Markdown/HTML report specification, anti-patterns, and final checklist.
- `references/fallback.html` — bundled self-contained HTML fallback.
- `reviewable-html-report` capability — shared HTML report mechanics when an interactive report is required; repo-local `skills/reviewable-html-report/references/report_base.md` is optional.

## Completion Standard

A renewal diagnosis is complete only when recommendations are tied to evidence, capability benefit, stability risk, adoption economics, a reversible pilot path, explicit validation gates, and an HTML review report (with a same-basename Markdown source only when the user explicitly requests it or HTML generation is infeasible). Do not quietly convert a local experiment into a global migration.
