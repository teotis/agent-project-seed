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

## 绝对规则

- **先建理解模型，再写 HTML。**
- **先表达关系，再装饰容器。**
- **首屏必须给出核心命题 thesis，并让 thesis 可追溯到 evidence。**
- **长页必须有可点击 TOC，所有链接指向稳定 section id。**
- **每个图必须回答一个明确问题；没有问题的图不要画。**
- **图中的箭头必须有方向和含义，颜色、形状、线型必须有图例或直接标签。**
- **正文摘要不能成为信息黑洞；关键事实必须能追溯到证据或附录。**
- **理解交互优先于审阅交互。** 高亮路径、切换视角、筛选、缩放、术语解释优先于评分和评论。
- **反馈控件默认折叠或置于文末。** 如果主要任务是审阅、批注、批准、导出 review notes 或持久化反馈，使用 `reviewable-html-report`。
- **长页面必须有章节索引。** comprehension-first HTML 必须提供可点击 section index / TOC，链接到稳定 `section id`。
- **默认打开浏览器。** 生成并验证 HTML 后，环境允许时用 `scripts/open_browser.py` 打开；失败时在最终回复说明。
- **不要接管正式报告机制。** `html-response` 决定 thesis、理解路径和内容结构；复杂评审控件、Mermaid/lightbox、反馈导出基础设施由 `reviewable-html-report` 提供。
- **引用失败要降级。** 如果 `reviewable-html-report`、模板、脚本或 reference 文件不可用，仍交付一个 self-contained、静态可读的 HTML：包含核心结论、TOC、稳定 section id、证据附录、Mermaid source fallback 和折叠式反馈区；同时在最终回复说明缺失的增强能力。
- **复杂交互必须有静态 fallback。** 任何 lens switcher、筛选、路径高亮、缩放、review/export 控件都不能成为理解核心信息的唯一入口。
- 不要为每个原文章节复制同一种 card + radio + textarea。
- 不要用大量无语义的 KPI、彩色徽章、圆环图或装饰图标制造“仪表盘感”。

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

生成布局前，按 `references/comprehension_model.md` 建立中间模型。至少提取：

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

大型分析默认采用四层阅读深度：

1. **30 秒：结论与全景**
   - 一句话 thesis；
   - 3-5 个关键 takeaway；
   - 一个 system map、concept map 或核心对比。
2. **3 分钟：关键关系与运行故事**
   - 静态结构如何协作；
   - 一个代表性 end-to-end flow；
   - 关键边界、循环或约束。
3. **10 分钟：变体与局部放大**
   - feature matrix、before/after、state transition、风险或例外；
   - 可切换 lens 或路径高亮。
4. **审计：完整证据**
   - 类、文件、引用、原始表格、未展示细节、coverage ledger。

页面不是从“第一章”滚到“最后一章”，而是从总览逐层放大。

## 4. 选择视觉语法

使用 `references/visual_grammar.md`。优先选择最小且最有解释力的表示：

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

图形不是原文的缩略图。图形负责关系，文本负责解释、边界和证据。

## 5. 信息保真与可追踪性

“不遗漏”不等于把每句话都放在首屏。使用三层保真：

- `foreground`：改变理解或决策的核心事实，直接展示；
- `on-demand`：支持核心事实的细节，通过局部展开、hover/focus 或 lens 显示；
- `audit`：完整类清单、长表、原始引用和边缘案例，放入附录。

每个关键 claim、relationship、flow 和 comparison 使用稳定 ID，并通过 `data-source-ref`
或相邻 evidence link 映射到来源。页面包含机器可读的 `coverage-ledger`：

```html
<script type="application/json" id="coverage-ledger">
{"claims":[...],"relationships":[...],"details":[...]}
</script>
```

coverage ledger 必须说明重要信息位于：

- `visible`：默认可见；
- `interactive`：通过视角或路径交互可见；
- `appendix`：完整保留在附录；
- `omitted`：确实省略，并说明原因。

不得把未覆盖信息默认为“已经总结”。

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

选择一个主要模式，必要时组合一个辅助模式。详见 `references/presentation_modes.md`。

- **Visual Explainer**：复杂概念、架构、研究综合；默认用于大型项目分析。
- **Architecture Atlas**：静态地图 + runtime stories + feature paths + evidence。
- **Decision Board**：选项、取舍、推荐和待决事项。
- **Evidence Dashboard**：指标、证据强弱、趋势和异常。
- **Action Plan**：阶段、依赖、门禁和风险。
- **Technical Review**：发现、证据、影响和处置。
- **Artifact Explanation**：页面、图片、文档布局的理解型讲解；正式逐项批注和反馈导出交给 `reviewable-html-report`。
- **Brief View**：用户明确要求短内容使用 HTML。

不要因为输入很长就使用 dashboard。架构讲解通常是 explainer，不是 dashboard。

## 8. 生成流程

1. 读取完整源材料；区分最终回答、tool evidence、推理草稿和噪音。
2. 写出 `reader_goal` 和 `thesis`。
3. 建立 comprehension model 和 coverage ledger。
4. 选择 2-4 个能回答不同问题的核心视觉，不要为每节配图。
5. 设计 30 秒、3 分钟、10 分钟、审计四层阅读路径，并为长页面建立 section index / TOC：稳定 `id`、`href="#section-id"`、读者问题式标签。首屏 thesis 使用 `data-comprehension-role="thesis"` 和 `data-source-ref`，核心视觉使用 `data-visual-question` 和必要的 `data-visual-relationships`。
6. 选择 packaging：
   - `single-file-portable`：常规文本、SVG、小型数据；
   - `local-review-bundle`：大量图像、页面或大型数据集。
7. 使用 `templates/visual_explanation_base.html` 或适合的专用模板。模板不可用时，手写最小 self-contained HTML shell，不停止交付。
8. 按 `references/html_system_spec.md` 实现 semantic HTML、响应式、离线和安全要求。
9. 按 `references/quality_checklist.md` 进行理解验收。
10. 运行：

```bash
python3 scripts/validate_html.py <report.html> --profile comprehension
```

架构地图、runtime flow 和跨场景矩阵属于交付核心时，使用更严格的：

```bash
python3 scripts/validate_html.py <report.html> --profile architecture
```

11. 在真实浏览器检查首屏、全页、窄屏和交互。浏览器不可用时，明确记录未完成视觉验收。
12. 默认打开生成的 HTML：

```bash
python3 scripts/open_browser.py <report.html>
```

打开失败时不要静默成功；最终回复列出 HTML 路径并说明浏览器打开缺口。

## 9. Completion Gate

交付前必须能肯定回答：

- 读者在 30 秒内能复述 thesis、主要实体和一条主路径吗？
- 至少一个视觉表达了原文中无法靠标题层级表达的关系吗？
- 静态结构和 runtime behavior 是否被明确区分？
- 多个变体是否在共享维度上对齐比较？
- 每个重要箭头、颜色和形状是否有语义？
- 关键结论是否能追溯到 evidence？
- coverage ledger 是否揭示所有重要信息的去向？
- 首屏 thesis 是否位于 `main` 之前或 opening viewport，并带有 `data-source-ref`？
- 每个核心视觉是否声明 reader question，关系型视觉是否声明 relationship semantics？
- 所有复杂交互是否有静态 fallback 或 `<noscript>` 可读路径？
- 首屏是否几乎没有与理解无关的表单？
- 是否存在可点击章节索引，且每个链接都跳到稳定 section？
- 删除 CSS 后，文档结构是否仍然成立？
- 与原文相比，用户是否减少了记忆和跳转，而不只是减少了字数？

任何一项为否，继续修改。

## 10. Resources

路径均相对本技能目录：

- `references/comprehension_model.md`：语义提取、coverage ledger 和信息分层。
- `references/visual_grammar.md`：图形选择、架构图、动态流程和比较矩阵规范。
- `references/presentation_modes.md`：页面模式和章节结构。
- `references/html_system_spec.md`：HTML shell、布局、无障碍、离线和安全。
- `references/quality_checklist.md`：理解增益与工程质量验收。
- `references/feedback_spec.md`：仅用于轻量、折叠、辅助性的反馈；正式 review controls、持久化和导出优先用 `reviewable-html-report`。
- `references/artifact_review_spec.md`：PDF、文档、图片的理解型检查和轻量区域说明；正式批注工作流优先用 `reviewable-html-report`。
- `templates/visual_explanation_base.html`：comprehension-first 起始模板。
- `templates/interactive_response_base.html`：需要轻量反馈时的旧模板或降级模板；正式审阅优先用 `reviewable-html-report`。
- `scripts/validate_html.py`：结构、安全和 comprehension profile 校验。
