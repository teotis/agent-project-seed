# Presentation Modes

## Selection Rule

Select the mode that matches the user's cognitive job, not the source document's format.

## Visual Explainer

Use for conceptual explanations, architecture overviews, research synthesis, or “help me understand” requests.

Default order:

1. thesis and orientation;
2. concept/system map;
3. representative runtime or causal story;
4. important variants or exceptions;
5. evidence appendix.

Primary interactions: lens switching, path highlighting, terminology, evidence reveal.

Avoid: chapter-by-chapter card conversion and default feedback forms.

## Architecture Atlas

Use for large project or system analysis with several valid views.

Required lenses:

- system boundaries and responsibilities;
- dependencies with labeled intent;
- one or more runtime stories;
- feature/scenario paths;
- evidence index.

The atlas may be a long single page or a local bundle, but every lens must share stable entity IDs and terminology.

## Decision Board

Use for recommendations, alternatives, trade-offs, prioritization, and approvals.

Opening: recommended option, decisive reason, caveat, pending decision.

Main units: aligned options, criteria, evidence, risks, reversibility.

Primary interactions: compare, sort, reveal evidence, and clarify the pending decision. If the page needs persistent prefer/defer/reject controls or approval notes, use `reviewable-html-report` mechanics.

## Evidence Dashboard

Use when measured values, trends, distributions, or evidence strength are central.

Opening: key finding and source status.

Main units: plots, tables, anomalies, assumptions, evidence quality.

Do not use dashboard conventions for qualitative architecture explanations without meaningful metrics.

## Action Plan

Use for roadmaps, migrations, execution plans, and checklists.

Opening: target outcome, current phase, blocker, next gate.

Main units: phases, dependencies, owners if known, acceptance evidence, rollback points.

## Technical Review

Use for comprehension-oriented code, architecture, incident, security, or quality findings where the reader needs a clearer map of what matters and why.

Opening: highest-leverage findings and overall risk.

Main units: finding, evidence, impact, affected area, recommended disposition.

Keep feedback controls collapsed or secondary. If the primary task is formal review, acceptance, comments, ratings, or feedback export, use `reviewable-html-report`.

## Artifact Explanation

Use for PDF, document, slide, image, or layout inspection when the goal is to understand structure, hierarchy, defects, or comparison patterns.

Main units: rendered pages/assets, annotated explanations, and evidence references.

For formal page-by-page annotation, persistent review comments, or feedback export, use `reviewable-html-report` mechanics. `artifact_review_spec.md` is now a lightweight/legacy reference for visual artifact handling, not the default owner of formal review workflows.

## Brief View

Use only when the user explicitly requests HTML for a short answer.

Avoid TOC, dashboards, diagrams without a real relationship, and extensive feedback mechanics.

## Shared Content Mapping

| Source meaning | Representation |
|---|---|
| Governing model | thesis + overview visual |
| Ownership/boundary | architecture map |
| Runtime collaboration | dynamic flow / sequence |
| Repeated feature descriptions | aligned matrix / small multiples |
| Cause and evidence | evidence chain |
| Long class/file list | evidence appendix |
| Uncertainty | visible assumption/caveat block |
| Raw source | referenced appendix, not duplicated into cards |
