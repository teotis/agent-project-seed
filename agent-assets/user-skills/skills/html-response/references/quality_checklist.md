# Quality Checklist

本 checklist 对齐 `SKILL.md` 的 Model Adaptation Contract。未标记的项是 **核心验收（hard invariants）**，必须满足；标记 `(adaptive)` 的项是可选可检查脚手架，在启用对应标注或需要机器可检查交付时才检查，强模型能隐式满足时可跳过。

## Understanding Gain

- [ ] The opening viewport has an explicit reader goal and one-sentence thesis.
- [ ] The thesis is a real conclusion, not a decorative title, and is traceable to evidence. `(adaptive: data-source-ref 或相邻 evidence link 是可选标注形式)`
- [ ] The first viewport contains a meaningful visual entry, not only prose or decorative metrics.
- [ ] At least one visual encodes relationships that source headings cannot.
- [ ] Static structure and runtime behavior are represented separately.
- [ ] Repeated scenarios are aligned through a matrix or small multiples.
- [ ] Important exceptions clarify system boundaries.
- [ ] `(adaptive)` 分层阅读深度被支持（默认 30秒/3分钟/10分钟/审计可作为起点，层数和粒度按材料调整）。
- [ ] `(adaptive)` 长页面包含可点击 section index 与稳定 anchor；形式可灵活。

## Information Fidelity

- [ ] Primary claims, relationships, flows, comparisons, risks, and uncertainties have stable IDs.
- [ ] Important items map to source/evidence references.
- [ ] Primary conclusions, including the thesis and recommendation sentences, can be traced to evidence IDs or the appendix.
- [ ] 重要信息的去向可说明（visible / interactive / appendix / 明确省略并说明原因）；无 primary item 被静默省略。
- [ ] `(adaptive)` coverage ledger 以机器可读 JSON 块记录上述去向（需要机器检查或交接下游 agent 时启用）。
- [ ] The appendix preserves audit detail without forcing it into the main reading path.
- [ ] Fact, inference, assumption, and recommendation are distinguishable where needed.

## Visual Semantics

- [ ] Every diagram has a title and accessible description.
- [ ] Every important arrow has direction and a relationship label.
- [ ] Colors, shapes, line styles, and sizes have explicit meaning.
- [ ] Color is not the only differentiator.
- [ ] A text summary or table equivalent exists for dense diagrams.
- [ ] `(adaptive)` 每个视觉声明 reader question、scope、encoding、relationship semantics、takeaway、source（`data-visual-question` 等是可选标注）。
- [ ] `(adaptive)` Dense diagrams can be enlarged or focused.

## Interaction Hierarchy

- [ ] Comprehension interactions are more prominent than review controls.
- [ ] Critical information is not hover-only or animation-only.
- [ ] Feedback is collapsed or visually secondary unless review is the primary task.
- [ ] JavaScript failure leaves the core explanation readable.
- [ ] Every complex interaction has a static fallback (`.static-fallback` 或 `<noscript>`；`data-static-fallback` 是可选标注).
- [ ] Controls are keyboard operable with visible focus.

## Reading Experience

- [ ] The page uses progressive zoom from overview to detail.
- [ ] Cards represent meaningful units, not every paragraph.
- [ ] Prose line length and spacing remain comfortable.
- [ ] Narrow screens preserve meaning, even if diagrams scroll horizontally.
- [ ] `(adaptive)` Navigation names reader questions or lenses, not generic chapter numbers.
- [ ] `(adaptive)` Print styles retain the explanation and hide nonessential controls.

## Engineering

- [ ] Correct `lang`, title, viewport, semantic landmarks, and heading order.
- [ ] Offline-first output has no undeclared remote dependency.
- [ ] Untrusted content is escaped; no `eval`, `new Function`, inline event handlers, or `javascript:` URLs.
- [ ] CSP is present or omission is justified.
- [ ] Reduced motion is respected.
- [ ] Large artifacts use a local bundle rather than an oversized single file.

## Validation (adaptive, optional)

`validate_html.py` 是可选自检工具，不阻塞交付；浏览器视觉验收更关键。需要机器可检查交付或自检不确定时运行：

```bash
python3 <skill-path>/scripts/validate_html.py <generated.html> --profile comprehension
```

架构解释可用 `--profile architecture`，额外要求 runtime flow 和 comparison matrix。脚本校验 opening thesis with evidence、clickable TOC、visual reader questions、relationship semantics、evidence appendix、coverage ledger、static fallback 等结构契约。校验失败时作为改进提示，不强制阻塞交付；若某项无法满足且不影响核心理解，在最终回复说明即可。

## Final Reader Test (hard invariant)

Ask a fresh reader, or simulate one without reopening the source:

1. What is the central model?
2. What are the main entities and boundaries?
3. What happens in one representative end-to-end scenario?
4. How do two important variants differ?
5. Where would you verify a disputed claim?

If the page does not make these answers easier than the source, it has failed regardless of visual polish.
