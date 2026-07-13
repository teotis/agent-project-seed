---
name: flow-realization-review
description: >
  用于已有工程、AI agent、工具工作流、模型/skill 落地设计或自动化流程，需要从用户意识、用户价值、核心对象、顶层设计、主流程、分支门禁、实现真实性和证据缺口审查其是否真正承接目标时使用。产出工程顶层设计与主流程审计报告、典型流程图谱、缺陷/缺口看板、ready / needs-supplement / design-gap / evidence-gap / not-ready 判断和补充任务包。Exclude: 不用于从零产品价值发散（用 user-value-architect）、纯页面跳转 UX journey review、纯 HTML 排版、全库质量扫雷或最终完成声明验收（用 done-claim-gate）。
---

# Flow Realization Review

## Mission

把一个已经存在的工程、方案、流程、agent、工具或 skill 设计，审成用户能判断的顶层设计与主流程图谱：它究竟替用户解决什么负担、核心价值是什么、用什么对象承接目标、主流程怎么走、哪些分支和门禁缺失、哪些只是设计、哪些已经实现、哪些需要证据或用户决策。

本 skill 不是从零发散产品方向，也不是最终完成声明门禁。它的核心问题是：

> 当前工程的顶层设计和主流程设计，是否真正把用户价值落到一条可理解、可审、可执行、可恢复、可补强的流程里？

正式产物应像一份“工程项目审计报告”或“典型流程审计图谱”，而不是一张孤立状态表。报告要先让用户看懂这个工程是什么、为什么有价值、主要流程如何承接价值，再指出设计缺陷、流程遗漏、风险门、实现边界和补充任务。

## Invocation And Boundary

- 用户显式要求“流程落地审阅”“典型流程报告”“顶层设计是否有缺陷”“主流程设计是否支撑需求”“帮我审这个 agent / workflow / skill 设计是否落地”时使用。
- 本 skill 仅支持用户显式调用，不接受 Claude/Codex agent active 自启用；上下文出现清晰 flow-realization 信号时，只给出一屏观察、关键缺口或 handoff 建议，等待用户点名 `$flow-realization-review`。
- 正式运行默认 analysis-only。只允许写报告、gap ledger、pending decision queue、task package 或 review export；不得修改产品代码、运行时配置、真实数据、生产流程或 Git 历史，除非用户另行明确授权。

不用于：

- 从零寻找用户价值上限：建议 `user-value-architect`。
- 已有方案的产品表达、默认答案、指标激励精修：建议 `product-sense-refiner`。
- 准备声称实现完成或用户质疑“为什么说完成”：使用 `done-claim-gate`。
- 全库质量、可靠性或发布风险扫雷：建议 `deep-flow-sweep`。
- 缺失不变量、重复表示或结构重构候选：建议 `abstraction-architect`。
- 单纯把已有内容做成好看的网页：使用 `html-response`；需要正式审阅控件时借用 `reviewable-html-report` mechanics。

## Core Workflow

1. **Name project thesis**：先用一句话说清“这个工程不是泛泛的 X，而是面向 Y 的 Z 系统/流程”。若无法命名，标记顶层设计缺口。
2. **Recover user value**：确定目标用户、真实负担、成功信号、用户最在意的信任/效率/控制/恢复/结果质量。不得让内部机制替代用户价值。
3. **Map demand scenarios**：列出 3-5 个主场景或需求入口，说明每个场景如何进入主流程，哪些场景只是未来愿景或需要授权。
4. **Name the core object**：找出流程围绕什么被批准、执行、恢复和解释，例如 package、run、case、task、session、artifact、decision manifest。若没有核心对象，标记 `design-gap`。
5. **Audit top-level design fit**：检查核心对象、目录/状态模型、证据层、权限边界、风险门和恢复面是否能承接用户价值。
6. **Trace the main flow**：从用户触发开始，串起 setup、first value、core loop、branching、risk gates、human decisions、execution、receipt、recovery 和 closeout。
7. **Build branch and status matrix**：每个主分支标记 `implemented`、`designed-only`、`manual`、`missing`、`needs-authorization` 或 `unknown`，并附 evidence IDs。执行 schema anti-leakage：状态不得比证据更强。
8. **Check design defects and readiness**：按用户目标、顶层设计适配性、核心对象、流程覆盖、证据充分性、用户决策点、恢复路径和实现真实性判定状态。
9. **Package gaps**：把缺口分成 `design defect`、`supplement task`、`pending decision`、`evidence request`、`route handoff` 或 `defer`，并标记属于 `review checkpoint`、`approval checkpoint`、`execution checkpoint` 还是 `recovery checkpoint`。不得把设计态画成已执行。
10. **Deliver review artifact**：小范围可 chat-only；分支多、需要审阅或长期归档时生成 HTML/Markdown 报告。正式报告优先写入 `reports/flow-realization-review/`。

## Status Model

- `ready`：核心用户流程、主要分支、证据和恢复路径都足以支持当前目标。
- `needs-supplement`：方向成立，但需要补模板、ledger、阈值、状态字段、任务包或局部工具。
- `design-gap`：核心对象、状态权威、分支规则或用户决策边界缺失。
- `evidence-gap`：设计声称可能成立，但缺真实路径、样例、日志、截图、artifact、测试或用户确认。
- `not-ready`：流程无法支撑承诺，或关键风险门缺失且会误导用户执行。

## Output Contract

默认输出：

```text
落地状态: ready | needs-supplement | design-gap | evidence-gap | not-ready
项目一句话判断:
用户价值:
需求场景:
顶层设计适配性:
核心对象:
主流程图谱:
分支/状态矩阵:
设计缺陷:
实现真实性:
用户决策点:
证据缺口:
补充任务包:
不建议做什么:
建议路由:
```

正式报告必须包含：

- one-screen decision summary with project thesis；
- user value and demand scenario section；
- top-level design fit: core object, state authority, evidence layer, permission boundary, recovery model；
- main flow map and typical flow audit graph；
- branch/status matrix；
- design defect board and missing scenario list；
- implemented vs designed-only vs missing vs authorization-required boundary；
- gap ledger and pending decisions；
- supplement task package；
- evidence appendix with stable IDs；
- review questions that let the user reject, accept, defer, or correct defaults.

Branch/status schema 必须满足：

- `implemented` 必须有代码、命令、测试、真实 artifact 或运行路径证据；
- `ready` 必须有当前目标范围内的端到端证据；
- 无 evidence ID 的分支只能是 `unknown`、`designed-only`、`manual`、`missing` 或 `evidence-gap`；
- `review-ready` 不得暗示 `execution-ready`。

Checkpoint 语言必须区分：

- `review checkpoint`：用户能否理解和审阅；
- `approval checkpoint`：用户是否需要明确授权或设置默认；
- `execution checkpoint`：是否已有 dry-run、执行路径和 receipt；
- `recovery checkpoint`：是否能解释、回滚、恢复或追责。

## Required Reference

读取 `references/method-and-report.md` 当以下任一情况成立：

- 用户要求正式报告、可视化流程图谱、低理解成本审阅页或任务包；
- 分支超过 5 个，或出现 implemented / designed-only / missing 混杂；
- 需要判定 `ready`、`design-gap`、`evidence-gap` 或补充任务优先级；
- 需要 HTML artifact design、review controls、evidence appendix 或 handoff package。

## Completion Gate

交付前确认：

- 用户目标没有被内部机制替代；
- 报告开头能让用户理解这个工程是什么、替谁解决什么、价值如何落到流程；
- 核心对象和典型流程已经命名；
- 顶层设计、主流程、分支门禁、恢复面之间的关系已经画清；
- 设计态、实现态、人工态、缺失态没有混写；
- 分支矩阵覆盖主干、风险门、恢复和用户决策点；
- `ready` 结论有真实证据支持；没有证据时降级为 `needs-supplement` 或 `evidence-gap`；
- 报告能帮助用户指出遗漏、不同意的默认处理、缺失设计或扩展性问题；
- 未经授权没有进入实现、迁移、删除、发布或真实数据操作。
