---
name: reviewable-html-report
description: >
  用于生成、改造或审查正式 HTML 报告的 review surface 和可复用基础设施。
  Use when an already-formed analysis, audit, plan, or artifact review needs Mermaid/topology report mechanics, review cards, local feedback persistence, or exportable review notes.
whenToUse: >
  当任务需要构建或审查 HTML 报告基础设施、Mermaid 图、拓扑对比、评审卡、反馈持久化、导出评审笔记或可交互技术报告模板时使用。
  不用于把复杂内容重新编译成理解型网页、一次性普通 HTML 回答、简单报告排版、或只需要选择是否生成 HTML 的场景；这些应使用 html-response。
---

# Reviewable HTML Report

## 使命

为密集技术报告构建可复用 review presentation layer。这个 skill 不做领域分析本身，也不重新设计读者的理解路径；它把已经成形的 analysis、plan、audit、comparison 或 artifact review，转成一个 self-contained HTML report，方便阅读、检查、批注，并交回给另一个 agent。

当 `abstraction-architect`、`renewal-architect`、`analyze-success` 等 skill 已经拥有自己的 report schema，只需要 interactive HTML review surface 时，把它作为报告 companion 使用。

如果输入本身还没有清晰的 thesis、读者路径、关系图、runtime story、比较矩阵或证据分层，应先使用 `html-response` 的 comprehension-first 方法整理内容结构，再按需要借用本 skill 的 review mechanics。

它不是唯一出口。调用方 skill 应把 `reviewable-html-report` 当作 capability 引用；当前仓库的 `references/report_base.md` 是 repo-local enhancement，不是 standalone skill 的硬依赖。若无法加载本 skill 或 `references/report_base.md`，必须降级生成可读的 self-contained HTML，而不是放弃交付：至少保留核心结论、TOC、稳定 section id、证据附录、Mermaid source fallback 和不依赖 localStorage 的折叠反馈区。

## 适用场景

当用户要求，或另一个 skill 需要以下内容时使用：

- interactive HTML report；
- 带 readable fallback 的 Mermaid topology diagrams；
- review cards、star ratings、status fields、comments 或 exportable feedback；
- architecture、renewal、success-pattern analysis、product review、implementation planning 的视觉化技术报告；
- 共享 report scaffold，避免每个 skill 重新实现 CSS、lightbox、review persistence、export logic。

不要用本 skill 处理：

- “把这段复杂内容变成更容易看懂的网页”；
- 没有既定 report schema、需要先决定 thesis 和阅读路径的材料；
- 一次性可视化讲解、concept map、runtime flow、decision board 或 evidence atlas。

这些属于 `html-response`。

不要用本 skill 决定报告的 domain conclusions。调用方 skill 拥有 analysis、evidence、recommendations、acceptance criteria。

## 核心边界

调用方 skill 拥有意义；本 skill 拥有报告机制。

| Layer | Owner |
|---|---|
| Domain evidence, findings, recommendation logic, scoring criteria | Calling skill |
| Thesis, reader goal, comprehension path, section order | Calling skill or `html-response` |
| Reviewable item IDs | Calling skill, using this skill's conventions |
| Mermaid import rules, lightbox behavior, review controls, feedback export, accessibility basics | `reviewable-html-report` |
| Final verification that the report renders and remains readable | Calling skill plus this skill's checklist |

## 工作流

1. 确认输入已经有 domain conclusions 和 report schema。若主要任务是重新组织复杂内容帮助理解，转用 `html-response`。
2. 识别 report mode：architecture review、renewal plan、success-pattern analysis、product review、artifact review 或 generic technical review。
3. 向调用方 skill 要稳定 reviewable units：finding IDs、proposal IDs、recommendation IDs、artifact page IDs 或 decision IDs。
4. 只有需要具体 CSS、JavaScript、Mermaid rules 或 review-control snippets 时，才加载 `references/report_base.md`。
5. 默认生成 self-contained HTML file；报告太大时，创建 local bundle，并提供清楚的 index。若 `references/report_base.md` 不可读，使用最小降级 shell，不阻塞调用方报告交付。
6. 高风险结论必须同时保留在 chat 或 source Markdown 中。HTML 可以改善 review，但不能成为唯一结论载体。
7. 交付前验证报告：
   - opening viewport 包含答案或 review task；
   - Mermaid source 在 CDN 加载失败时仍可读；
   - topology diagrams 有足够空间，并能用 lightbox 打开；
   - review controls 有 stable IDs，且不依赖 hidden state；
   - localStorage 和 clipboard operations 有 fallback；
   - feedback export 带足够上下文，方便 follow-up agent 使用。

## 必需报告特性

- 使用 semantic sections 和 headings，避免只有装饰标题的首屏。
- HTML 必须提供章节索引（TOC / section index），每个主章节使用稳定 `id`，索引链接使用 `href="#section-id"` 并可点击跳转；长报告应启用当前章节高亮。
- 每张 reviewable card 必须有 stable `data-card-id` 或等价 ID。
- 需要时本地持久化 review state，但 localStorage 访问必须包在 `try/catch`。
- feedback export 输出 Markdown 或 JSON，包含 report、item IDs、rating/status/comment fields、next-action note。
- Mermaid diagrams 遵循 `references/report_base.md` 的 compatibility rules。
- 远程 CDN 不可用时，提供可读 Mermaid source 或 explanatory fallback text。
- 本 skill 或 `report_base.md` 不可用时，调用方至少交付静态 HTML fallback，并在最终回复说明缺少 review persistence、lightbox、clipboard export 等增强能力。
- HTML 交付默认提供本地路径和可点击 `file://` URL；主动打开浏览器只是可选预览，不是完成标准。
- Calling skill 拥有正式交付策略；本 skill 只提供 reviewable HTML mechanics。当前 architect / renewal 类 skill 默认交付 HTML，只有用户明确要求 agent 接力 / 源文件交付或 HTML 不可生成时才追加同名 Markdown source report。不要用本 skill 覆盖 calling skill 的交付契约。

## Resource Map

以下路径相对本 `SKILL.md` 所在目录：

- `references/report_base.md`：共享 Mermaid initialization、topology CSS skeleton、lightbox JavaScript、review controls、localStorage pattern、export pattern、TOC linkage。

## Calling Skills 的迁移指南

迁移已有 analysis skill 时：

1. 保留该 skill 自己的 domain method 和 report schema。
2. 把内联 report infrastructure prose 替换为：“Use the `reviewable-html-report` capability for shared report mechanics; repo-local `references/report_base.md` is an optional enhancement.”
3. 明确该 skill 的正式收尾：由 calling skill 决定 HTML-only 默认、Markdown 升级项或双产物；若同时生成 `.md` 与 `.html`，使用同一 timestamp basename 并共享结论。
4. skill-specific colors、terminology、statuses、export directives 留在调用方 skill。
5. 不要因为共享 report layer 就合并 analysis skills。
