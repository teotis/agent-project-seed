# Visual Grammar for Complex Explanations

## Core Rule

Choose a visual because its geometry carries meaning. Do not use a visual merely to make the page look less textual.

Each visual must declare:

- `question`: what the reader should learn;
- `scope`: what is included and excluded;
- `relationships`: the relationship types, arrow meanings, or comparison semantics the visual encodes;
- `encoding`: what position, color, shape, line, and size mean;
- `takeaway`: the interpretation in one sentence;
- `source_ref`: evidence supporting the visual.

Use semantic markup:

```html
<figure
  data-visual-purpose="system-map"
  data-source-ref="claim-architecture"
  data-visual-question="Which modules own the important responsibilities and dependencies?"
  data-visual-relationships="frontend calls API; API persists state; worker retries failed jobs">
  <svg role="img" aria-labelledby="map-title map-desc">
    <title id="map-title">...</title>
    <desc id="map-desc">...</desc>
  </svg>
  <figcaption>...</figcaption>
</figure>
```

## 1. Architecture Map

Use for system composition, boundaries, ownership, or dependencies.

Required:

- title, scope, legend;
- named elements with type/role;
- labeled relationships, also summarized in `data-visual-relationships`;
- arrow direction matching the relationship;
- visible system or platform boundary;
- no unexplained color or shape.

Prefer 5-9 primary nodes. Group lower-level elements rather than showing an unreadable graph.

For larger systems, provide lenses:

- `responsibility`: what each part owns;
- `dependency`: compile-time or data dependency;
- `runtime`: messages and order;
- `platform`: pure domain vs platform adapter.

Do not combine all relationship types in one diagram unless line style and labels make them unmistakable.

## 2. Dynamic Flow

Use for a user story, feature, request, event, or failure path.

Required:

- one explicit scenario;
- ordered interactions;
- actors aligned as lanes or stable nodes;
- messages labeled with verbs;
- start and outcome;
- branching only when it changes understanding.

Use numbered steps when free-form layout could obscure order. A vertical prose timeline is not enough when the important information is who communicates with whom.

Select representative flows:

- the most common path;
- the most architecturally revealing path;
- one exception that clarifies a boundary.

Do not draw a sequence for every feature. Use a comparison matrix for repeated patterns.

## 3. Cross-Layer Matrix

Use when several features, options, findings, or scenarios share dimensions.

Rows are items; columns are stable dimensions. Keep cells terse and action-oriented.

Useful encodings:

- filled cell: active participation;
- muted cell: pass-through;
- dash: deliberately not involved;
- numbered marker: order;
- outlined cell: delegated outside the modeled system.

Always include a legend and a short takeaway. Do not rely on color alone.

When the matrix is too wide:

- allow horizontal scroll;
- freeze row labels when practical;
- provide per-item small multiples on narrow screens;
- preserve a text table fallback.

## 4. State and Lifecycle Map

Use when state transitions, gates, retries, or loops are central.

Required:

- named states;
- trigger on every transition;
- terminal/error states;
- distinction between state and action;
- explicit retry or recovery loops.

Do not use a state diagram for a simple linear process.

## 5. Evidence Chain

Use for audits, root-cause analysis, research synthesis, and recommendations.

Structure:

```text
Evidence -> Observation -> Interpretation -> Consequence -> Recommendation
```

Visually distinguish fact, inference, assumption, and decision. Each interpretation must point backward to evidence.

## 6. Small Multiples

Use when several items share the same structure but differ in path or emphasis. Keep the scale and layout identical so differences are perceptible.

Good:

- auto flash vs night mode vs Live Photo across the same five layers;
- current vs proposed architecture;
- three failure scenarios through the same pipeline.

Bad:

- one unrelated decorative diagram per section;
- differently scaled charts that imply false comparisons.

## 7. Interaction Patterns

Useful:

- click/focus a node to highlight incoming and outgoing relationships;
- switch between static, runtime, and feature lenses;
- select a feature to emphasize its path through a shared matrix;
- open evidence linked to a claim;
- zoom or lightbox a dense diagram.

Avoid:

- animation needed to reveal the answer;
- hover-only facts;
- filters that start with critical information hidden;
- generic carousels;
- interactions whose only effect is decorative motion.

Every complex interaction must have a static fallback. Use `data-static-fallback`, `.static-fallback`, or `<noscript>` to preserve the same facts as text, table, Mermaid source, or an always-visible summary.

## 8. Visual Density

- One dominant visual per viewport is usually enough.
- Use whitespace to separate reasoning stages, not to inflate card count.
- A card should represent a meaningful unit, not every paragraph.
- Prefer direct labels over legends when space permits.
- Keep prose measure around 60-75 characters for explanation text.
- Large diagrams may use the full content width; explanatory prose should remain narrower.

## 9. Diagram Review

For every diagram verify:

- Can a reader name its type and scope?
- Does every element have a name and role?
- Does every relationship have a label?
- Are direction, colors, shapes, borders, and sizes explained?
- Is there a textual takeaway and accessible description?
- Is the reader question explicit through `data-visual-question` or an adjacent caption?
- Are relationship semantics explicit through labels and, for relationship maps, `data-visual-relationships`?
- Does it add information that headings and paragraphs do not?

## Design Provenance

These rules adapt durable ideas from:

- [C4 model diagrams](https://c4model.com/diagrams): use explicit abstraction levels and only the zoom levels that add value.
- [C4 dynamic diagrams](https://c4model.com/diagrams/dynamic): show runtime collaboration for a specific feature or story with explicit ordering.
- [C4 diagram review checklist](https://c4model.com/diagrams/checklist): name scope, elements, relationship intent, direction, notation, and legend.
- [GitHub Primer progressive disclosure](https://primer.style/product/ui-patterns/progressive-disclosure/): hide detail sparingly and preserve the reader's context.
- [GitHub Primer data visualization](https://primer.style/product/ui-patterns/data-visualization/): label charts, constrain visual complexity, and never rely on color alone.
- [Quarto dashboards](https://quarto.org/docs/dashboards/): compose responsive rows, columns, cards, tables, plots, and narrative rather than forcing one content type everywhere.

Use these as design principles, not as permission to add dashboard chrome or diagrams without a reader question.
