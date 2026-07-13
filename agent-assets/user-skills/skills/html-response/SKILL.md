---
name: html-response
description: >
  用于把复杂、冗长、关系密集的分析、架构讲解、研究综合、计划、对比或文档输出重新编译成低理解门槛且信息可追踪的 HTML。
  Use when dense Claude Code or agent output needs a comprehension-first visual explanation, architecture map, runtime flow, comparison matrix, evidence atlas, or browser-readable decision surface; not for formal report review mechanics.
---

# Comprehension-First HTML Response

## 使命

把复杂输出编译成一个更容易形成心智模型的网页。它负责 content structure 和 reading path，不负责正式报告的 review infrastructure。

目标不是“把 Markdown 放进漂亮卡片”，而是让读者：

1. 迅速说出核心结论；
2. 看见关键实体及其关系；
3. 沿着一条真实路径理解系统如何运作；
4. 比较重要变体，而不必在段落间来回搜索；
5. 随时追溯到完整证据和未展示细节。

HTML 只有在显著提升 `orientation`、`comprehension`、`inspection` 或 `decision`
时才值得生成。复杂项目分析默认优先提升 comprehension；feedback 只能作为辅助层，不能成为本 skill 的主要理由。

## Model Adaptation Contract

本 skill 的规则按刚性分层使用。强模型只需守住 Hard Invariants；Adaptive Heuristics 可隐式覆盖或按需启用，是给弱模型或可检查交付的确定性脚手架，不构成封闭 checklist；Creative Extension Lane 鼓励按材料自由设计。

- **Hard invariants**：先建理解模型再写 HTML；首屏 thesis 是结论句且可追溯到 evidence；理解交互优先于审阅交互、feedback 默认折叠；正文摘要不能成为信息黑洞、关键事实可追溯；不把未覆盖信息默认为“已经总结”（coverage 诚实）；复杂交互必须有静态 fallback；引用失败要降级为 self-contained 静态可读 HTML；不接管正式报告机制（边界交给 `reviewable-html-report`）；不为每节复制同一种 card、不用装饰仪表盘感。这些保护理解质量和读者信任，不能被“充分发挥模型能力”绕过。
- **Adaptive heuristics**：coverage-ledger JSON 机器可读块、`data-comprehension-role` / `data-source-ref` / `data-visual-question` / `data-visual-relationships` 属性体系、四层阅读深度（30秒/3分钟/10分钟/审计）、可点击 TOC 与稳定 section id 的具体形式、`validate_html.py` 校验、各 reference 文件、生成流程步骤数，都是触发式脚手架。在需要机器可检查交付、交接给下游 agent、读者需要严格审计路径、或模型自检不确定时启用；强模型能隐式保证理解质量时不必机械套用。
- **Creative extension lane**：当材料具有内置分层之外的特有结构（非线性概念依赖、跨时间演化、多视角对比等）时，模型可自由设计阅读路径、视觉形式和分层方式，临时命名新的 lens 或 reading depth。只要守住 hard invariants，就不必受默认四层或内置 presentation mode 约束。

每次生成都做一次 **skill value check**：HTML 是否比直接读 chat 显著减少了读者的记忆、跳转和认知负担。若没有，降级为 chat 结论或明确建议不生成 HTML。

## Hard Invariants

- **先建理解模型，再写 HTML。** 先表达关系，再装饰容器。
- **首屏必须给出核心命题 thesis，thesis 是结论句而非装饰标题，并让 thesis 可追溯到 evidence。** “某某分析/说明/报告”不算 thesis。
- **正文摘要不能成为信息黑洞；关键事实必须能追溯到证据或附录。**
- **理解交互优先于审阅交互。** 高亮路径、切换视角、筛选、缩放、术语解释优先于评分和评论。
- **反馈控件默认折叠或置于文末。** 主要任务是审阅、批注、批准、导出 review notes 或持久化反馈时，使用 `reviewable-html-report`。
- **不把未覆盖信息默认为“已经总结”。** 重要信息的去向必须可说明（展示 / 交互可见 / 附录 / 明确省略并说明原因）。
- **引用失败要降级。** `reviewable-html-report`、模板、脚本或 reference 不可用时，仍交付 self-contained、静态可读的 HTML：核心结论、可导航结构、证据附录、Mermaid source fallback、折叠式反馈区；在最终回复说明缺失的增强能力。
- **复杂交互必须有静态 fallback。** 任何 lens switcher、筛选、路径高亮、缩放、review/export 控件都不能成为理解核心信息的唯一入口。
- **不要接管正式报告机制。** `html-response` 决定 thesis、理解路径和内容结构；复杂评审控件、Mermaid/lightbox、反馈导出基础设施由 `reviewable-html-report` 提供。
- **不要为每个原文章节复制同一种 card + radio + textarea；不要用无语义 KPI、彩色徽章、圆环图或装饰图标制造“仪表盘感”。**

## 1. 何时生成 HTML

### 必须生成

- 用户明确要求 HTML、网页、可视化讲解、浏览器报告或交互式审阅。
- 主要输入是复杂架构分析、跨模块流程、长篇研究综合、证据密集审查或视觉文档。
- 调用方 skill 明确要求 HTML artifact。

### 自适应生成

在用户未明确要求时，仅当浏览器页面能让用户少读、少记、少跳转并更快形成结构理解时生成。

以下情况通常保持 chat：

- 简短事实、确认、普通对话；
- 虽长但结构单一的线性说明；
- 没有关系、比较、证据导航或视觉检查需求的回答。
- 用户要的是正式审阅报告基础设施、review cards、Mermaid/lightbox、localStorage 持久化、逐项批注或 feedback export，而不是理解型讲解；此时使用 `reviewable-html-report`。

## 2. 建立 Comprehension Model

生成布局前，先建立中间理解模型（可参考 `references/comprehension_model.md`，按需读取）。至少提取：

```text
reader_goal       用户读完后应能回答什么
thesis            一句话核心模型
claims            3-7 个主张
entities          系统、模块、角色、概念、阶段
relationships     from / to / direction / label / evidence
runtime_stories   有顺序的协作流程及变体
comparisons       共享维度上的差异
uncertainties     假设、冲突、缺口、置信度
evidence          文件、代码、数据、原文段落或来源
coverage_ledger   每个重要信息被展示、折叠或附录保留的位置
```

不要直接把源标题映射成页面标题。先寻找：

- 反复出现的主干关系；
- 能解释大量细节的少数不变量；
- 用户最可能混淆的边界；
- 一个真实功能如何穿过静态结构；
- 哪些细节适合比较而不是逐段阅读。

## 3. 设计阅读路径

大型分析**建议**采用分层阅读深度，默认四层可作为起点，但层数和粒度应按材料调整：

1. **结论与全景**：一句话 thesis、3-5 个关键 takeaway、一个 system map 或核心对比。
2. **关键关系与运行故事**：静态结构如何协作、一个代表性 end-to-end flow、关键边界或约束。
3. **变体与局部放大**：feature matrix、before/after、state transition、风险或例外；可切换 lens 或路径高亮。
4. **审计：完整证据**：类、文件、引用、原始表格、未展示细节、coverage ledger。

页面从总览逐层放大，而不是从“第一章”滚到“最后一章”。材料简单时可少于四层，材料高度多维时可增加专门 lens。

## 4. 选择视觉语法

可参考 `references/visual_grammar.md`（按需读取）。优先选择最小且最有解释力的表示：

| 用户问题 | 首选表示 |
|---|---|
| 系统由什么组成，边界在哪里？ | context / container map、分层地图 |
| 谁依赖谁，关系含义是什么？ | labeled dependency graph |
| 一次请求、事件或功能如何运行？ | numbered dynamic flow、sequence、swimlane |
| 多个功能如何穿过同一架构？ | cross-layer matrix、small multiples |
| 状态如何变化？ | state map、transition table |
| 哪些选项不同？ | aligned comparison table/cards |
| 哪些因素共同导致结果？ | causal map、evidence chain |
| 证据分布在哪里？ | evidence index、annotated source map |

图形不是原文的缩略图。图形负责关系，文本负责解释、边界和证据。每个图应回答一个明确问题；没有问题的图不要画。

## 5. 信息保真与可追踪性

“不遗漏”不等于把每句话都放在首屏。使用三层保真：

- `foreground`：改变理解或决策的核心事实，直接展示；
- `on-demand`：支持核心事实的细节，通过局部展开、hover/focus 或 lens 显示；
- `audit`：完整类清单、长表、原始引用和边缘案例，放入附录。

每个关键 claim、relationship、flow 和 comparison 使用稳定 ID，并映射到来源——这是 hard invariant（关键事实可追溯）。

以下为 **Adaptive Heuristics（可选可检查脚手架）**，在需要机器可检查交付、交接下游 agent 或严格审计路径时启用；强模型能隐式满足追溯要求时不必机械标注：

- `data-source-ref` / `data-comprehension-role` 等属性标注来源与角色；
- 机器可读 `coverage-ledger` JSON 块：

```html
<script type="application/json" id="coverage-ledger">
{"claims":[...],"relationships":[...],"details":[...]}
</script>
```

  coverage ledger 应能说明重要信息位于 `visible` / `interactive` / `appendix` / `omitted`（并说明原因）。无论是否输出 JSON 块，“不把未覆盖信息默认为已经总结”都是 hard invariant。

## 6. 交互层级

按以下优先级添加交互：

1. **理解**：切换 static/runtime/feature lens，高亮路径，聚焦节点，术语解释。
2. **探索**：筛选、排序、展开证据、缩放大图。
3. **行动**：选择方案、确认优先级、导出计划。
4. **反馈**：评论、评分、复制反馈。

只有当交互改变用户看见的信息或降低认知负担时才添加。静态 HTML 必须仍然可读。

当 feedback 不是主要任务时：

```html
<details class="review-drawer">
  <summary>Review or comment on this report</summary>
  ...
</details>
```

需要复杂评审机制时，使用 `reviewable-html-report` 的 report mechanics，但不要让它决定内容结构。若用户主要任务是审阅而不是理解，直接转用 `reviewable-html-report`。
如果该 companion skill 或其 `report_base.md` 无法读取，内联最小降级机制：纯 CSS、无外部依赖、可点击 TOC、可读 Mermaid 源码块、每个 review item 使用稳定 `data-card-id`，反馈表单放在 `<details>` 中但不依赖 localStorage 或 clipboard。

## 7. Presentation Modes

选择一个主要模式，必要时组合一个辅助模式。可参考 `references/presentation_modes.md`（按需读取）。

- **Visual Explainer**：复杂概念、架构、研究综合；默认用于大型项目分析。
- **Architecture Atlas**：静态地图 + runtime stories + feature paths + evidence。
- **Decision Board**：选项、取舍、推荐和待决事项。
- **Evidence Dashboard**：指标、证据强弱、趋势和异常。
- **Action Plan**：阶段、依赖、门禁和风险。
- **Technical Review**：发现、证据、影响和处置。
- **Artifact Explanation**：页面、图片、文档布局的理解型讲解；正式逐项批注和反馈导出交给 `reviewable-html-report`。
- **Brief View**：用户明确要求短内容使用 HTML。

不要因为输入很长就使用 dashboard。架构讲解通常是 explainer，不是 dashboard。模式是起点而非封闭清单，材料需要时可组合或临时命名新模式（creative extension lane）。

## 8. 生成流程

以下为建议流程，可按材料跳步；强模型能隐式保证理解质量时不必机械走完每一步：

1. 读取完整源材料；区分最终回答、tool evidence、推理草稿和噪音。
2. 写出 `reader_goal` 和 `thesis`。
3. 建立 comprehension model 和 coverage ledger（形式可灵活，见第 5 节）。
4. 选择 2-4 个能回答不同问题的核心视觉，不要为每节配图。
5. 设计分层阅读路径，并为长页面建立 section index / TOC：稳定 `id`、`href="#section-id"`、读者问题式标签。首屏 thesis 与核心视觉可选用 `data-comprehension-role="thesis"`、`data-source-ref`、`data-visual-question`、`data-visual-relationships` 标注（adaptive heuristic）。
6. 选择 packaging：
   - `single-file-portable`：常规文本、SVG、小型数据；
   - `local-review-bundle`：大量图像、页面或大型数据集。
7. 使用 `templates/visual_explanation_base.html` 或适合的专用模板。模板不可用时，手写最小 self-contained HTML shell，不停止交付。
8. 按 `references/html_system_spec.md`（按需读取）实现 semantic HTML、响应式、离线和安全要求。
9. 按 `references/quality_checklist.md`（按需读取）进行理解验收。
10. **可选校验**：交付前可运行 `validate_html.py` 做结构、安全和 comprehension profile 自检，不阻塞交付；浏览器视觉验收更关键。

```bash
python3 scripts/validate_html.py <report.html> --profile comprehension
# 架构地图、runtime flow 和跨场景矩阵属于交付核心时，可用更严格的 --profile architecture
```

11. 在真实浏览器检查首屏、全页、窄屏和交互。浏览器不可用时，明确记录未完成视觉验收。
12. 默认打开生成的 HTML：

```bash
python3 scripts/open_browser.py <report.html>
```

打开失败时不要静默成功；最终回复列出 HTML 路径并说明浏览器打开缺口。

## 9. Completion Gate

交付前必须能肯定回答以下 **核心验收**（hard invariants）：

- 读者在 30 秒内能复述 thesis、主要实体和一条主路径吗？
- thesis 是否是结论句，而不是 H1/title 的复述或“某某分析/说明/报告”式装饰标题？
- 至少一个视觉表达了原文中无法靠标题层级表达的关系吗？
- 静态结构和 runtime behavior 是否被明确区分？
- 多个变体是否在共享维度上对齐比较？
- 关键结论是否能追溯到 evidence？
- coverage 是否诚实揭示所有重要信息的去向（不把未覆盖当总结）？
- 所有复杂交互是否有静态 fallback 或 `<noscript>` 可读路径？
- 首屏是否几乎没有与理解无关的表单？
- 删除 CSS 后，文档结构是否仍然成立？
- 与原文相比，用户是否减少了记忆和跳转，而不只是减少了字数？

任何一项为否，继续修改。

以下为 **可选脚手架验收**（adaptive heuristics，启用 coverage-ledger JSON / data-* 标注或严格审计交付时才检查）：

- `coverage-ledger` JSON 是否可解析，且 primary item 没有 `omitted`、每个 `omitted` 都有 reason、每个 ledger item 都有 disposition？
- 首屏 thesis 是否位于 `main` 之前或 opening viewport，并带有 `data-source-ref`？
- 每个核心视觉是否声明 reader question，关系型视觉是否声明 relationship semantics？
- 是否存在可点击章节索引，且每个链接都跳到稳定 section？
- 每个重要箭头、颜色和形状是否有语义？

## 10. Resources

路径均相对本技能目录。所有 reference 均为**按需参考**，不要求生成前全量读取；仅在需要对应细节时加载。

- `references/comprehension_model.md`：语义提取、coverage ledger 和信息分层。
- `references/visual_grammar.md`：图形选择、架构图、动态流程和比较矩阵规范。
- `references/presentation_modes.md`：页面模式和章节结构。
- `references/html_system_spec.md`：HTML shell、布局、无障碍、离线和安全。
- `references/quality_checklist.md`：理解增益与工程质量验收。
- `references/feedback_spec.md`：仅用于轻量、折叠、辅助性的反馈；正式 review controls、持久化和导出优先用 `reviewable-html-report`。
- `references/artifact_review_spec.md`：PDF、文档、图片的理解型检查和轻量区域说明；正式批注工作流优先用 `reviewable-html-report`。
- `references/dependencies.md`：本 skill 的依赖与边界声明。
- `templates/visual_explanation_base.html`：comprehension-first 起始模板。
- `templates/interactive_response_base.html`：需要轻量反馈时的旧模板或降级模板；正式审阅优先用 `reviewable-html-report`。
- `scripts/validate_html.py`：结构、安全和 comprehension profile 校验（可选自检，不阻塞交付）。
- `scripts/open_browser.py`：生成后默认打开浏览器。
