# Quality Checklist

## Understanding Gain

- [ ] The opening viewport has an explicit reader goal and one-sentence thesis.
- [ ] The thesis is a real conclusion, not a decorative title, and it carries `data-source-ref` or an adjacent evidence link.
- [ ] The first viewport contains a meaningful visual entry, not only prose or decorative metrics.
- [ ] At least one visual encodes relationships that source headings cannot.
- [ ] Static structure and runtime behavior are represented separately.
- [ ] Repeated scenarios are aligned through a matrix or small multiples.
- [ ] Important exceptions clarify system boundaries.
- [ ] The 30-second, 3-minute, 10-minute, and audit reading depths are supported.
- [ ] Long or comprehension-first pages include a clickable section index with stable anchor targets.

## Information Fidelity

- [ ] Primary claims, relationships, flows, comparisons, risks, and uncertainties have stable IDs.
- [ ] Important items map to source/evidence references.
- [ ] Primary conclusions, including the thesis and recommendation sentences, can be traced to evidence IDs or the appendix.
- [ ] A coverage ledger records `visible`, `interactive`, `appendix`, or justified `omitted` disposition.
- [ ] No primary item is silently omitted.
- [ ] The appendix preserves audit detail without forcing it into the main reading path.
- [ ] Fact, inference, assumption, and recommendation are distinguishable where needed.

## Visual Semantics

- [ ] Every visual states its reader question, scope, encoding, relationship semantics, takeaway, and source.
- [ ] Every diagram has a title and accessible description.
- [ ] Every important arrow has direction and a relationship label.
- [ ] Colors, shapes, line styles, and sizes have explicit meaning.
- [ ] Color is not the only differentiator.
- [ ] Dense diagrams can be enlarged or focused.
- [ ] A text summary or table equivalent exists.

## Interaction Hierarchy

- [ ] Comprehension interactions are more prominent than review controls.
- [ ] Critical information is not hover-only or animation-only.
- [ ] Feedback is collapsed or visually secondary unless review is the primary task.
- [ ] JavaScript failure leaves the core explanation readable.
- [ ] Every complex interaction has a static fallback (`data-static-fallback`, `.static-fallback`, or `<noscript>`).
- [ ] Controls are keyboard operable with visible focus.

## Reading Experience

- [ ] The page uses progressive zoom from overview to detail.
- [ ] Cards represent meaningful units, not every paragraph.
- [ ] Prose line length and spacing remain comfortable.
- [ ] Navigation names reader questions or lenses, not generic chapter numbers.
- [ ] Narrow screens preserve meaning, even if diagrams scroll horizontally.
- [ ] Print styles retain the explanation and hide nonessential controls.

## Engineering

- [ ] Correct `lang`, title, viewport, semantic landmarks, and heading order.
- [ ] Offline-first output has no undeclared remote dependency.
- [ ] Untrusted content is escaped; no `eval`, `new Function`, inline event handlers, or `javascript:` URLs.
- [ ] CSP is present or omission is justified.
- [ ] Reduced motion is respected.
- [ ] Large artifacts use a local bundle rather than an oversized single file.

## Validation

Run:

```bash
python3 <skill-path>/scripts/validate_html.py <generated.html> --profile comprehension
```

架构解释使用 `--profile architecture`，额外要求 runtime flow 和 comparison matrix。

The script is a minimum structural gate. It enforces the core contract: opening thesis with evidence, clickable TOC, visual reader questions, relationship semantics for maps, evidence appendix, coverage ledger, and static fallback for complex interactions. Also inspect the rendered page at desktop and narrow widths.

## Final Reader Test

Ask a fresh reader, or simulate one without reopening the source:

1. What is the central model?
2. What are the main entities and boundaries?
3. What happens in one representative end-to-end scenario?
4. How do two important variants differ?
5. Where would you verify a disputed claim?

If the page does not make these answers easier than the source, it has failed regardless of visual polish.
