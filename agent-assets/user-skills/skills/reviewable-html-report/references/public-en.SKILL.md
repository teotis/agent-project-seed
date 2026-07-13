---
name: reviewable-html-report
description: Use when an already-formed analysis, audit, plan, or artifact review explicitly needs reviewable HTML mechanics such as Mermaid/topology views, review cards, local feedback persistence, or exportable review notes.
---

# Reviewable HTML Report

## Mission

Build the reusable review presentation layer for dense technical reports. This skill does not perform the domain analysis itself and does not redesign the reader's comprehension path; it only turns an already-formed analysis, plan, audit, comparison, or artifact review into a self-contained HTML report when the content is worth upgrading into a formal review surface.

Use it as the report companion for skills such as `abstraction-architect`, `renewal-architect`, and `analyze-success` when they already own the report schema and have passed their Report Upgrade Gate.

If the input still needs a thesis, reader path, relationship map, runtime story, comparison matrix, or evidence layering, first use a comprehension-first HTML approach such as `html-response`, then borrow this skill's review mechanics only when needed.

It is not the default delivery path. Calling skills should treat `reviewable-html-report` as a review capability, not as proof that thinking was deep. If a calling skill has already passed the Report Upgrade Gate but cannot load this skill or `references/report_base.md`, it must degrade to a readable self-contained HTML report instead of dropping the artifact. The fallback should preserve the core conclusion, TOC, stable section IDs, evidence appendix, Mermaid source fallback, and a non-persistent collapsible feedback area.

## When To Use

Use this skill when the user asks for, or another skill's Report Upgrade Gate requires:

- an interactive HTML report;
- Mermaid topology diagrams with readable fallbacks;
- review cards, star ratings, status fields, comments, or exportable feedback;
- a visual technical report for architecture, renewal, success-pattern analysis, product review, or implementation planning;
- a shared report scaffold instead of each skill reimplementing CSS, lightbox, review persistence, and export logic.

### Report Upgrade Gate

Upgrade ordinary analysis to HTML only when at least one condition holds:

- more than three findings or candidates need comparison, filtering, or comments;
- an evidence ledger, proposal cards, review comments, or feedback export would change the next decision;
- the artifact must be handed to another agent, reviewed by a team, archived long term, or prepared for release review;
- the user explicitly requests formal HTML, an interactive report, Mermaid topology, review cards, or exportable comments.

Do not use this skill for:

- turning complex material into an easier-to-understand webpage;
- "think deeply about this" when there is no review, archival, or interaction need;
- material that has no established report schema and still needs a thesis or reading path;
- one-off visual explainers, concept maps, runtime flows, decision boards, or evidence atlases.

Do not use this skill to decide the report's domain conclusions. The calling skill owns the analysis, evidence, recommendations, and acceptance criteria.

## Core Boundary

The calling skill owns meaning. This skill owns report mechanics.

| Layer | Owner |
|---|---|
| Domain evidence, findings, recommendation logic, scoring criteria | Calling skill |
| Thesis, reader goal, comprehension path, section order | Calling skill or a comprehension-first HTML skill |
| Reviewable item IDs | Calling skill, using this skill's conventions |
| Mermaid import rules, lightbox behavior, review controls, feedback export, accessibility basics | `reviewable-html-report` |
| Final verification that the report renders and remains readable | Calling skill plus this skill's checklist |

## Workflow

1. Confirm that the input already has domain conclusions and a report schema, and that it passed the Report Upgrade Gate. If the main task is to reorganize complex material for understanding, use a comprehension-first HTML skill instead; if the task only needs a one-screen answer or handoff, do not generate HTML.
2. Identify the report mode: architecture review, renewal plan, success-pattern analysis, product review, artifact review, or generic technical review.
3. Ask the calling skill for the stable reviewable units: finding IDs, proposal IDs, recommendation IDs, artifact page IDs, or decision IDs.
4. Load `references/report_base.md` only when you need concrete CSS, JavaScript, Mermaid rules, or review-control snippets.
5. After the upgrade gate passes, generate a self-contained HTML file unless the report is too large; for large reports, create a local bundle with sibling assets and an obvious index. If `references/report_base.md` is unavailable, use a minimal fallback shell and do not block report delivery.
6. Preserve all high-stakes conclusions in the chat or source Markdown as well. The HTML can improve review, but it must not be the only place where the conclusion exists.
7. Verify the report before delivering it:
   - the opening viewport contains the answer or review task;
   - Mermaid source is readable even if CDN loading fails;
   - topology diagrams have enough space and can open in a lightbox;
   - review controls have stable IDs and do not depend on hidden state;
   - localStorage and clipboard operations have fallbacks;
   - feedback export contains enough context for a follow-up agent.

## Required Report Features

- Use semantic sections and headings. Avoid decorative title-only first screens.
- Every HTML report must include a clickable TOC / section index with stable section IDs and `href="#section-id"` links. Long reports should highlight the active section. The TOC must be either a sidebar or a compact top bar: a sticky top TOC must not occupy more than 60% of the opening viewport, must not freeze a large title box over the first screen, and should provide collapsible / collapse behavior, a sidebar mode, or a non-sticky fallback when it needs more than two rows or when narrow screens lack space.
- Every reviewable card must have a stable `data-card-id` or equivalent ID.
- Persist review state locally when useful, but wrap localStorage access in `try/catch`.
- Export feedback as Markdown or JSON that names the report, item IDs, rating/status/comment fields, and a next-action note.
- For Mermaid diagrams, follow the compatibility rules in `references/report_base.md`.
- Provide readable Mermaid source or explanatory fallback text when remote CDN loading is unavailable.
- If this skill or `report_base.md` is unavailable, the caller must still deliver a static HTML fallback and report that review persistence, lightbox behavior, clipboard export, or similar enhancements were omitted.
- HTML delivery should provide the local path and a clickable `file://` URL. Opening a browser is optional preview behavior, not a completion standard.
- The calling skill owns its formal delivery policy. This skill only provides reviewable HTML mechanics. Do not use this skill to override that policy or to make HTML the default completion form for all deep analysis.

## Resource Map

All paths below are relative to this SKILL.md file's directory.

- `references/report_base.md` — shared Mermaid initialization, topology CSS skeleton, lightbox JavaScript, review controls, localStorage pattern, export pattern, and TOC linkage.

## Migration Guidance For Calling Skills

When migrating an existing analysis skill:

1. Keep the skill's domain method and report schema in that skill.
2. Replace inline report infrastructure prose with: "Use the `reviewable-html-report` capability for shared report mechanics; repo-local `references/report_base.md` is an optional enhancement."
3. Let the calling skill default to a one-screen conclusion or structured handoff, and generate HTML only after its Report Upgrade Gate passes. When both Markdown and HTML are produced, use the same timestamp basename and shared conclusions.
4. Keep skill-specific colors, terminology, statuses, and export directives local to the calling skill.
5. Do not merge analysis skills merely because they share this report layer.
