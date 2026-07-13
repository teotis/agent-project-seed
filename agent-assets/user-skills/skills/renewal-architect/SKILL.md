---
name: renewal-architect
description: >
  用于大型遗留系统、长期技术债、架构现代化和复杂组织中的工程演进决策。
  通过证据优先、能力导向、结果优先、约束聚焦、可回滚试点、共存迁移、规模复制、稳定性护栏、开放学习和明确 owner 的框架，寻找务实突破点。
  当用户要做代码库分析、技术债治理、平台迁移、遗留系统更新、渐进式重构、单体拆分、strangler/ACL 设计、ROI 驱动优化，或在组织复杂性下规划可回滚现代化时使用。
  不用于寻找非增量结构性抽象、普通 bug 修复、纯性能微调或无需迁移策略的小范围重构；结构性抽象问题优先使用 abstraction-architect。
  默认交付物为 interactive HTML engineering renewal decision report；不再默认产出 Markdown 源报告，仅在用户明确要求 agent 接力或源文件交付时补充。
---

# Pragmatic Renewal Architect

## 0. 使命与边界

这是一个面向真实生产约束的 engineering optimization 方法。它只做一件事：

> 在深层 legacy debt、持续业务交付、多方协同和高不确定性共同存在的系统里，找出真正限制演进能力的瓶颈，并设计一条可度量、可回滚、可规模化的改进路径。

核心问题是：

> **当业务不能停、历史兼容责任不能抹掉、概念共识不能替代验证时，什么最限制系统能力？突破应该从哪里被验证？局部成功怎样变成可复用系统能力？整个过渡期如何保持稳定？**

### Core Decision Pattern

提出行动建议前，先使用这些 engineering primitives：

1. **Protect / Experiment / Defer**：区分什么不能坏、什么可以安全试验、什么暂时不应靠抽象争论定案。
2. **Adoption Economics**：识别谁受益、谁支付 migration cost、谁承担 operational risk、谁能批准变化、什么 mismatch 会阻止采用。
3. **Pilot-to-Decision Contract**：每个 pilot 必须产生一个具体缺失事实，并定义结果如何分支到 expand、revise、pause、rollback 或 stop。

这些不是口号。报告中必须把它们落成明确 boundaries、owners、signals 和 decision gates。

### Model Adaptation

把本 skill 的规则按刚性分层使用：

- **Hard invariants**：Diagnostic / Pilot Design 默认 analysis-only、Fact Ledger、Protect / Experiment / Defer、Adoption Economics、Pilot-to-Decision Contract、stability floor、rollback path、claim permission 和未授权不实现。这些保护 legacy/modernization 判断不被流行架构标签替代。
- **Adaptive heuristics**：twelve lenses、strangler/ACL/facade/canary 等机制、报告形态和证据波顺序是方法菜单。模型可以根据当前 business constraint、owner reality 和 operational evidence 调整顺序、合并或跳过无触发的 lens。
- **Creative extension lane**：当模型发现 method spec 外的组织、采用、发布、稳定性或能力瓶颈时，应临时命名该 constraint，记录 evidence、owner/risk assumption、pilot implication、false-positive guard 和 decision gate；只要能落到可验证 pilot 或 defer 理由，就可以进入报告。

每次正式诊断都做一次 **skill value check**：本 skill 是否比普通技术债分析新增了 adoption economics、可回滚试点、稳定性护栏、owner 现实或决策分支。如果没有，降级为简短诊断或 handoff，不强行展开完整 modernization 方法论。

### 默认工作模式

- **Diagnostic Mode** 默认：只分析，不改代码。产出 interactive HTML engineering renewal decision report；只有在用户明确要求 agent 接力或源文件交付时，才另写同名 Markdown source report。
- **Pilot Design Mode**：基于诊断，定义一个或多个 measurable、implementable、rollback-safe minimum pilot packages。不改代码。
- **Execution Mode**：只有用户明确要求实现或修改代码时启用。先建立 validation 和 rollback path，再在 defined pilot boundary 内修改代码。

## 默认执行强度与询问门槛

本 skill 仅支持用户显式调用。默认深度由用户请求决定：

- **用户显式调用**（用户点名本 skill、提出 renewal/legacy/migration/技术债诊断诉求、或同义触发词）：默认 **Deep** Diagnostic Mode，覆盖完整 fact ledger、十二 lenses、adoption economics 与正式 HTML 报告。
- **Agent active 禁止**：普通任务上下文中即使出现清晰 renewal 信号，也只输出最小 renewal 观察、coverage debt 或 evidence-backed handoff 建议，等待用户点名 `$renewal-architect`。
- **Cross-heavy route**：正在运行的 architect、sweep、Deep 或 Exhaustive workflow 不得自动启动本 skill，只能提交 evidence-backed handoff，等待用户授权。
- **Exhaustive**：仅在用户明确要求「极致 / 全覆盖 / 大水漫灌」时进入；不是默认值。

用户显式调用即视为授权执行本 skill 在当前环境和既有安全边界内的正式原生工作流。未被用户显式调用时，不自动产出完整正式报告，不自动升级 Deep/Exhaustive；需要完整 renewal decision report 或更深证据面时，先提交 handoff 建议并等待用户确认。

可从当前 workspace、用户消息、文件和已有上下文合理推断的 scope、target、mode、约束和非破坏性执行方式，直接推断并记录，不要询问用户。信息不足但仍能继续时，将其写入 `assumptions / unknowns / coverage debt`，并继续完成其余可执行工作。

只有完全无法识别分析目标，或下一步需要用户未授权的 Execution Mode、migration、不可逆操作、账号状态变更、发布或推送时，才中断询问。并发分析、生成报告、运行只读或常规验证、选择默认 Diagnostic Mode 不需要额外确认。

### 治理纪律

1. 不因词汇高级、技术流行或图好看就接受方案。
2. 不因旧系统难看就推翻它；legacy code 可能承载尚未识别的稳定 contracts。
3. 不把 local experiment 静默升级成 global migration。
4. 不把“之后会变好”的承诺算作收益；收益必须对应 observable results。
5. 不让方法论覆盖项目事实；所有结论必须回到 code、operational evidence、business impact、organizational execution conditions。

### 语言与机制纪律

给工程团队交付时，只使用 neutral、testable、reusable 的工程语言。报告术语必须指向明确 responsibilities、boundaries、metrics 或 mechanisms；不要引入与工程任务无关的 analogy labels。

| Method Principle | Default Engineering Term | Common Mechanisms |
|---|---|---|
| Isolated experimentation | `Pilot Cell` | bounded module, isolated deployment boundary, dedicated telemetry |
| Reversible evolution | reversible validation path | feature flag, canary, shadow traffic, dual-read comparison, expand-contract |
| Incremental migration | dual-track compatibility boundary | ACL, Facade, Strangler Seam, event translation layer |
| Safe acceleration | delivery paired with stability | regression testing, SLOs, auditability, automated rollback, cost gates |

**约束**：这些 mechanisms 不是默认答案。只有证据显示它们能降低 blast radius、改善 delivery 或稳定性时才使用。

### 路由纪律

- 局部 module、interface、seam、adapter 或 deep-module 问题优先使用 `codebase-design`。
- 当 migration 反复增加 shim / adapter，暴露重复表示、缺失 invariant 或错误边界时，建议 handoff 给 `abstraction-architect`。
- 当 modernization 优先级取决于用户感知、信任、目标达成或 switching reason 时，建议 handoff 给 `user-value-architect`。
- `improve-codebase-architecture` 是用户显式启动的全库扫描，不是内部轻量 fallback。
- 上述路由只生成 handoff capsule，不自动启动下游 architect、sweep、Deep 或 Exhaustive workflow。

## 1. 调用流程

调用后：

1. 优先从当前 workspace、用户消息和已有材料推断 project location；只有完全无法识别目标时才提出一个最小问题。
2. 判断 mode。除非用户指定，否则使用 **Diagnostic Mode**。
3. 探索 project structure、dependencies、entry points、deployment and test paths、critical business flows、known pain points。
4. 建立 **Fact Ledger**：每个判断都必须绑定到 files、classes、methods、configuration、call relationships、tests、logs/metrics，或用户明确提供的 business facts。
5. 应用本 skill 的 12 lenses，识别：
   - 真正限制 evolution 和 delivery capability 的 dominant bottleneck；
   - 最小合理 breakthrough boundary；
   - 变化期间不能跌破的 stability floor；
   - 路线落地所需 adoption economics；
   - pilot 如何变成 reusable system capability。
6. Diagnostic 或 Pilot Design Mode 下生成 HTML report 作为默认正式交付，HTML 必须包含章节索引和点击跳转，最终回复提供报告路径和可点击 `file://` URL；只有用户明确要求 agent 接力 / 源文件交付，或环境无法产出 HTML 时，才另写同名 Markdown source report。Execution Mode 下，先呈现 pilot boundary 和 validation gates，再做受控修改并报告结果。

### Investigation Kernel Adaptation

本 skill 参考项目级 Investigation Kernel，但本段是 standalone local adaptation：即使 single skill copied out，也必须能独立执行 renewal diagnosis。

- **Concept version**：`investigation-kernel@v1`。
- **Derived from**：`docs/contracts/investigation-kernel.md`；本地段落按 `docs/contracts/portable-core-drift-model.md` 作为 intentional projection 审查。
- **Sync reference**：`docs/contracts/analysis-skill-registry.md` 中 `renewal-architect` 行，以及 `references/method_and_report_spec.md`。
- **Local projection**：Renewal Field Map、Fact Ledger、Dominant Constraint、Protect / Experiment / Defer、Pilot-to-Decision Contract。
- **Intentional differences**：本 skill 将共同调查内核投影到 legacy modernization、adoption economics、stability floor、rollback path 和 owner assumptions；不做 structural rewrite claim，结构性抽象问题优先转给 `abstraction-architect`。
- **Fallback**：`reviewable-html-report` capability 或 repo-local `report_base.md` 不可用时，使用 `references/fallback.html` 交付 self-contained static HTML，并保留核心结论、TOC、稳定 section id、证据附录、Mermaid source fallback 和非持久反馈区。

- **analysis artifact root**：正式分析优先写入当前项目的 `reports/renewal-architect/` 或既有同名报告目录；只允许写 Markdown/HTML 报告、fact ledger、pilot notes、decision handoff 和 review exports。
- **analysis-only boundary**：Diagnostic Mode 和 Pilot Design Mode 默认不得修改产品代码、测试、配置、迁移、依赖锁或 Git 历史。Execution Mode 只有在用户明确要求实现时启用，并且必须先重述 pilot boundary、validation gates、rollback path 和 owner assumptions。
- **evidence map**：先建立 Renewal Field Map / Fact Ledger，覆盖 current state、critical flows、stability floor、adoption economics、owner/risk assumptions、pilot/rollback signals，再提出 migration 或 modernization route。
- **handoff ledger projection**：作为 producer/consumer，保留稳定 `evidence_id`，并至少记录 type、source artifact、observation、confidence、consumed constraint/pilot/rollback ID；接手其他 skill 的 ledger 时复用旧 ID，只追加新证据。
- **model-discovered constraints**：method spec 外的新 constraint 必须与 dominant constraint 候选同台比较，按 evidence、capability effect、owner/risk assumption、pilot implication 和 false-positive guard 决定保留、降级或 defer。
- **coverage debt**：缺失 operational evidence、business constraints、compatibility data、owner confirmation、rollout history 或 rollback evidence 时，必须写入 assumptions / unknowns / coverage debt，不得用 modernization instinct 补齐。
- **claim permission**：没有 current-state evidence、capability benefit、stability risk、adoption economics、reversible pilot path 和 validation gates 时，不得声称 migration route、modernization recommendation、safe rollout 或 category-shift 已经成立。
- **budget-aware stop review**：low-information wave 只触发停止复盘；Standard 聚焦 dominant constraint 和 pilot-to-decision 草案，Deep 至少复核 adoption economics、rollback path 和 stability floor，Exhaustive 只有在剩余关键未知的 marginal information gain 变低时停止。

## 核心工作流

1. 判断请求是 Diagnostic、Pilot Design，还是用户明确授权的 Execution Mode。
2. 从 code、docs、tests、operational evidence、用户给出的 business constraints 和 known unknowns 建立 fact ledger。
3. 使用 `references/method_and_report_spec.md` 中的 twelve lenses、analysis rhythm、pilot design rules、Markdown/HTML report schema、final delivery checklist。
4. 默认产出 `pragmatic_renewal_architect_report_{YYYYMMDD}_{HHMM}.html` 作为 interactive engineering renewal decision report 与正式交付。HTML 必须包含章节索引和点击跳转，最终回复提供报告路径和可点击 `file://` URL。共享报告机制优先使用 `reviewable-html-report` capability；当前仓库可把 `skills/reviewable-html-report/references/report_base.md` 作为可选增强，不要把 sibling path 当作 standalone 硬依赖。若该能力不可用，使用 `references/fallback.html` 生成 self-contained 静态 HTML。只有用户明确要求 Markdown 源（agent 接力 / 源文件交付）或环境完全无法产出 HTML 时，才另写同名 `.md`，与 HTML 共享同一 fact ledger 和结论。
5. Execution Mode 下，先重述 pilot boundary、validation gates、rollback path、owner assumptions；然后只在该 boundary 内实现。

## 报告交付契约

- **HTML 给用户**：默认正式交付，包含 Fact Ledger、Dominant Constraint、Protect / Experiment / Defer、Pilot-to-Decision Contract、Adoption Economics、decision gates、unknowns、verification notes、决策地图、pilot cards、稳定性护栏、反馈/导出控件、章节索引和锚点跳转。
- **Markdown 是升级交付**：默认不生成；只在用户明确要求 agent 接力 / 源文件交付，或环境无法产出 HTML 时才补 `.md`，与 HTML 共享 fact ledger 和结论，作为 agent source of truth；不得引入未在 HTML 中出现的判断。
- **命名一致**：当因用户明确要求或环境兜底而追加 Markdown 时，使用与 HTML 同一 timestamp basename。HTML 不可生成或不可打开时，Markdown 是必交付兜底，并在最终回复中说明 HTML 缺口。
- **最终回复**：列出报告路径和可点击 `file://` URL、说明是否仅提供预览链接或按用户要求打开 HTML、一句话总结 dominant constraint 和 first breakthrough point，并声明未修改代码。

## 必需输出

- **Fact Ledger**：evidence、inference、unknowns、validation needs。
- **Dominant Constraint**：解除后能扩大未来行动空间的瓶颈。
- **Protect / Experiment / Defer split**：什么不能坏、什么可以 pilot、什么保持未决。
- **Pilot-to-Decision Contract**：hypothesis、unknown、scope、success/failure signals、timebox、rollback、decision gates。
- **Adoption Economics**：谁受益、谁付迁移成本、谁拥有 operational risk、什么会阻止采用。

## Resource Map

- `references/method_and_report_spec.md`：详细 lenses、analysis rhythm、Markdown/HTML report specification、anti-patterns、final checklist。
- `references/fallback.html`：无 companion capability 时的 skill-local self-contained HTML 模板。
- `reviewable-html-report` capability：需要 interactive report 时的共享 HTML report mechanics；repo-local `skills/reviewable-html-report/references/report_base.md` 只是可选增强，不可用时使用静态 HTML fallback，不阻塞报告交付。

## 完成标准

一份 renewal diagnosis 只有在 recommendations 同时绑定到 evidence、capability benefit、stability risk、adoption economics、reversible pilot path、explicit validation gates，并以 HTML review report 形式交付、HTML 有章节索引和锚点跳转、最终回复提供路径和可点击 `file://` URL 时才算完成。当用户要求或环境兜底而生成 Markdown 源报告时，应使用同一 timestamp basename 与 HTML 共享 fact ledger 和结论。不要把 local experiment 静默转换成 global migration。
