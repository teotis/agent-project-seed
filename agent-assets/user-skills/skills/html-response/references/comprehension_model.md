# Comprehension Model

## Purpose

Use this model between source analysis and HTML generation. It prevents source headings from becoming the page architecture by default.

## 1. Reader Contract

Write four sentences before designing:

1. `Reader starts with`: what they likely know now.
2. `Reader should leave knowing`: the durable mental model.
3. `Reader should be able to trace`: one representative path.
4. `Reader should be able to inspect`: the evidence and omitted detail.

If these cannot be stated, continue analyzing the source.

## 2. Semantic Inventory

Create a compact internal structure:

```json
{
  "reader_goal": "...",
  "thesis": "...",
  "claims": [
    {"id": "claim-boundary", "text": "...", "importance": "primary", "evidence": ["src-12"]}
  ],
  "entities": [
    {"id": "session", "label": "Session", "type": "orchestrator", "role": "Controls when work occurs"}
  ],
  "relationships": [
    {"id": "rel-mode-session", "from": "mode", "to": "session", "label": "submits capture strategy", "direction": "downstream", "evidence": ["src-18"]}
  ],
  "runtime_stories": [
    {"id": "flow-shutter", "question": "What happens after shutter press?", "steps": []}
  ],
  "comparisons": [
    {"id": "feature-paths", "dimensions": ["Settings", "Mode", "Session", "Device", "Media"], "items": []}
  ],
  "uncertainties": [],
  "evidence": [],
  "coverage": []
}
```

The HTML does not need to expose this exact JSON. The reasoning must contain equivalent structure.

## 3. Extraction Heuristics

### Find the governing model

Look for a sentence that explains many details with few concepts. Rewrite it in the user's language.

Example:

> Settings supplies parameters; Mode describes the capture strategy; Session coordinates timing; Device performs hardware work; Media processes the result.

This is more useful as the page thesis than “the project has seven core modules.”

### Separate static and dynamic structure

- Static: ownership, boundaries, dependencies, allowed directions.
- Dynamic: event order, messages, transformations, feedback loops.

Never use a static dependency stack as a substitute for a runtime path.

### Identify comparison dimensions

When several sections repeat the same categories, turn those categories into columns or lanes.

Example:

| Feature | Settings | Mode | Session | Device | Media |
|---|---|---|---|---|---|
| Auto flash | preference | pass-through | dispatch | decides/exposes | none |
| Night mode | frame policy | multi-frame strategy | sequences frames | captures | merges |

### Extract exceptions

Exceptions often teach boundaries better than normal cases:

- a UI-only feature bypasses Device and Media;
- video has a continuous lifecycle instead of one-shot capture;
- auto flash delegates the actual decision to the platform.

Show a small number of high-value exceptions near the main model.

## 4. Coverage Ledger

For every primary claim, relationship, runtime story, comparison, risk, and uncertainty, record its destination:

```json
{
  "id": "rel-session-device",
  "kind": "relationship",
  "importance": "primary",
  "disposition": "visible",
  "location": "#runtime-shutter",
  "source_refs": ["src-42", "src-51"]
}
```

Allowed dispositions:

- `visible`: default view;
- `interactive`: available through a labeled lens/filter;
- `appendix`: retained in evidence detail;
- `omitted`: excluded with a reason.

Rules:

- No primary item may be `omitted`.
- Every `omitted` item needs a reason.
- Summaries may combine details, but the ledger must retain the mapping.
- A source list without claim-to-source mapping is not traceability.

## 5. Compression Rules

Compress repetition, not meaning.

Safe to compress:

- repeated prose explaining the same ownership boundary;
- long class lists after representative examples are shown;
- implementation details that do not change the mental model.

Keep visible:

- governing invariants;
- relationship direction and intent;
- decision-critical exceptions;
- causal or runtime order;
- uncertainty and contradictory evidence.

Keep in appendix:

- full class/file inventories;
- raw tables and long quotations;
- secondary variants;
- source excerpts required for audit.

## 6. Self-Test

Before rendering, answer without looking at the source:

1. What is the central model?
2. What are the 5-9 entities a reader must remember?
3. Which arrows matter, and what do they mean?
4. What is the representative runtime story?
5. Which repeated sections should become a comparison?
6. What would be misleading if omitted?
7. Where can the reader verify each major claim?

If the answers are weak, HTML will only make weak analysis more polished.
