---
name: abstraction-architect
description: >
  用于结构性架构分析：当复杂度可能来自缺失不变量、重复领域表示、不稳定边界、转换胶水、平台/配置分支、中心编排瓶颈、流程状态散落、交互流程复杂或控制面膨胀时使用。
  以工程证据、反例、迁移接缝和可证伪测试为基础，先判断 local deletion、boundary repair 还是 structural candidate 更合适；只有满足报告升级门时才产出交互式 HTML 架构报告。
  当用户要求架构审查、领域统一、API/边界重设计、平台/配置泛化、状态机或流程漂移分析、重复表示消除、控制面简化、非增量结构性简化时使用。
  不作为普通 bug 修复、紧急事故处置、小性能调优或以交付风险排序为主的技术债治理的唯一方法。
---

# 结构抽象架构师（Structural Abstraction Architect）

## 目的

分析软件系统里是否存在更好的 structural model，可以一次性删除整类 special cases、adapters、branching logic、lifecycle inconsistencies、人造边界、散落流程状态，或用户侧 workflow burden。

这个 skill 受 Grothendieck 式 structural / universal abstraction 方法启发，但不是历史文章，也不模仿人格。数学隐喻只有在能产生可验证的工程简化时才有价值。

默认高级动作不是寻找漂亮抽象，而是先做 **structural decision triage**：判断当前问题应该由 `local deletion wins`、`boundary repair wins`，还是 `structural candidate worth testing` 解决。

- **local deletion wins**：删除旧分支、合并局部重复、改交互文案、保留 status quo with evidence 就能消除痛点。
- **boundary repair wins**：收缩边界、澄清 ownership、修正 adapter/API 契约或减少转换胶水即可，不需要新 canonical object。
- **structural candidate worth testing**：低抽象路径无法解释同一 exception family、projection drift、caller compensation 或 workflow burden，且证据显示存在可命名 invariant。

**process spatialization** 是 advanced candidate，不是默认姿态。只有当复杂度确实表现为时间、顺序、状态漂移、重试、审批、编排或环境依赖行为，并且三分流把它判为 `structural candidate worth testing` 时，才追问这些动态是否应该被表示为稳定 workflow/state object；文档、日志、UI 状态、ledgers、prompts、reports 才被视为它的一致 projections。

**Anti-Beauty Gate**：如果候选主要因为“统一、优雅、一般化、概念漂亮”而显得诱人，但不能删除当前真实负担、减少 hot path 风险、降低用户/维护者操作成本或形成小验证闭环，必须降级为 `interesting but not actionable`。

好抽象不是因为更 general 而成立；它必须能证明自己在当前系统里更有用。候选抽象需要给出可证伪的 **Candidate Proof Route**，并用非绝对的 **Abstraction Fitness Score** 辅助排序：清晰例子、有效工具、跨场景连接、有限信息下的 practical sufficiency、hot path value、tiny complete loop。Fitness score 不是硬门槛，不得为了过分数机械造证据；它只帮助用户判断哪个候选更值得审阅、试点或推迟。

默认交付物是 **one-screen structural decision**：三分流结论、关键证据、最小下一步和不建议升级的理由。只有满足 Report Upgrade Gate（多候选需要审阅、证据账本/评审卡有价值、用户明确要正式报告、或需要长期归档/agent 交接）时，才生成 interactive HTML architecture report。不默认生成 Markdown 源报告，只有用户明确要求 agent 接力、源文件交付、或 HTML 无法生成时才补 Markdown。本 skill 默认只做分析，不修改生产代码、测试、配置、迁移或基础设施。只有用户在审阅 transition plan 后另行明确授权，才可进入实现。

## Model Adaptation And Candidate Competition

把本 skill 的规则按刚性分层使用：

- **Hard invariants**：analysis-only、evidence map、no-new-abstraction baseline、constraint reality filter、admissibility gate、observational adequacy、local-to-global certificate、claim permission 和未授权不实现。这些保护结构判断不被审美、数学隐喻或模型自信替代。
- **Adaptive heuristics**：process spatialization、base-change、projection、canonical object、IR-vs-domain-model fork、discovery patterns、fitness score 和报告形态是候选生成与排序工具，不是固定路线。证据更支持局部删除、交互文案、边界修复或 status quo 时，应优先保留这些低抽象答案。
- **Creative extension lane**：每次 Deep/Exhaustive 分析允许模型提出一个或多个 skill 未预写的结构解释，只要它们能说明 trigger、deleted complexity、preserved differences、counterexamples、separating probes 和 transition seam。新解释必须和低抽象 baseline、既有 method candidates 同台竞争，而不是因为没有出现在 reference 中被压掉。

Candidate competition 是主机制，不是附加章节。默认先产出三分流：`local deletion wins`、`boundary repair wins` 或 `structural candidate worth testing`。推荐任何结构前，至少比较低抽象 baseline、边界修复解释、一个主结构候选和一个 rival explanation；推荐 structural rewrite 前必须给出 candidate proof route。证据不足时应选择 `unproven`、`defer`、`boundary repair wins` 或 `local deletion wins`，而不是按方法论偏好选最宏大的抽象。

## 默认执行强度与询问门槛

本 skill 同时支持用户显式调用与 agent active 自启用。默认深度由调用来源决定：

- **用户显式调用**（用户点名本 skill、提出架构审查/抽象分析诉求、或同义触发词）：默认 **Deep** 深度，跑结构调查、admissibility gate 和 candidate competition；Deep 是证据深度，不等于默认生成正式 HTML 报告。
- **Agent active 自启用**（普通任务上下文中直接出现清晰结构信号，且没有另一个重型分析 workflow 正在运行）：只进入 **Low-Budget Scan**，覆盖最小 pressure map、最高杠杆 candidate、no-new-abstraction 基线、coverage debt 和 handoff 建议；升级到 Deep 需要用户显式确认。
- **Cross-heavy route**：正在运行的 architect、sweep、Deep 或 Exhaustive workflow 不得自动启动本 skill，只能提交 evidence-backed handoff，等待用户授权。
- **Exhaustive**：仅在用户明确要求「极致 / 全覆盖 / 大水漫灌」时进入；不是默认值。

用户显式调用即视为授权执行本 skill 在当前环境和既有安全边界内的正式原生工作流。agent active 自启用只授权低预算轻量诊断，不自动产出完整正式报告，不自动升级 Deep/Exhaustive；需要完整 HTML 架构报告或更深证据面时，先提交 handoff 建议并等待用户确认。

可从当前 workspace、用户消息、文件、已打开材料或已有上下文合理推断的 scope、target、mode、输出形态和非破坏性执行方式，直接推断并记录，不要询问用户。信息不足但仍能继续时，将其写入 `assumptions / unknowns / coverage debt`，并继续完成其余可执行工作。

只有完全无法识别分析目标，或下一步需要用户未授权的 implementation、migration、不可逆操作、账号状态变更、发布或推送时，才中断询问。并发分析、生成报告、运行只读或常规验证、选择默认 mode 不需要额外确认。

## 输出语言

私有版默认使用中文交付：报告正文、章节标题、审查说明、结论和建议优先写中文。保留必要的英文关键词、代码标识、文件名、命令、API 名、架构术语和原文证据名称，例如 structural abstraction、process spatialization、admissibility gate、projection、shim、workflow、runtime path。

只有当用户明确要求英文、目标交付物必须面向英文读者，或正在同步公开英文版本时，才切换为英文。即使参考文件或方法规范使用英文，最终私有报告也应翻译和组织为中文，而不是直接沿用英文段落。

## 适用场景

### 强适合

系统出现以下结构信号时使用：

- 多个表示看起来描述同一个 domain concept。
- 反复出现 adapters、conversions、schema mappers、mode switches、platform branches。
- 边界产生的 glue 多于隔离价值。
- central orchestrator 或 God object 在协调本可局部组合的逻辑。
- workflow、orchestration、CI、approval、retry、lifecycle state 散落在 ledgers、logs、generated docs、dashboards、prompts、reports 或人工 checklists 中。
- 许多调用方都在补偿某 provider 设计，暴露出 API pain。
- 相似 workflow 在 products、tenants、protocols、environments 或 lifecycle stages 间重复实现。
- 用户 workflow 需要过多 commands、modes、handoffs、confirmations、training rules 或 recovery loops，因为系统暴露的是 controls 而不是 task-level interaction model。
- 用户要求 architecture review、domain unification、foundational refactoring 或 non-incremental simplification。

### 弱适合或不是第一工具

不要把这个 lens 强套到以运营紧急性或实施顺序为主的问题上：

- 需要立即缓解的 production incident。
- 局部 bug fix 或小型 performance bottleneck。
- 结构目标已经明确，剩下主要是 rollout safety 的 migration。
- ROI、blast radius、ownership 或 delivery constraints 主导的 technical debt prioritization。

局部 module、interface、seam、adapter 或 deep-module 问题优先使用 `codebase-design` 词汇分析。若结构目标已经明确而迁移、兼容、pilot、rollback 或 adoption economics 主导，建议 handoff 给 **Pragmatic Renewal Architect**；若结构价值主要取决于用户感知、信任或目标达成，建议 handoff 给 `user-value-architect`。这些都是路由建议，不自动启动下游重型 skill。

`improve-codebase-architecture` 是用户显式启动的全库扫描与交互筛选 workflow，不是本 skill 的轻量前置或内部 fallback。

## 调用与模式

调用后：

1. 优先从当前 workspace、用户消息和已有材料推断 target；只有完全无法识别目标时才提出一个最小问题。
2. 判断请求需要 structural analysis、transition planning，还是两者都要。
3. 只根据证据深入检查项目；缺失 telemetry、history、runtime behavior 或 business context 时明确标记。
4. 应用下面的 Structural Abstraction method。
5. 生成 HTML 架构报告（默认唯一正式交付物）；HTML 必须有章节索引和点击跳转，最终回复提供报告路径和可点击 `file://` URL。只有用户明确要求 Markdown 源报告或环境无法产出 HTML 时，才补对应 `.md`。

### Operating modes

| Mode | Default trigger | Deliverable | Modification permission |
|---|---|---|---|
| Low-Budget Structural Scan | Agent active 自启用默认；或用户明确要求轻量扫描；或证据不足以支持完整分析 | 一屏三分流诊断、candidate map、coverage debt 和 handoff 建议；满足 Report Upgrade Gate 时才升级 HTML report | No code changes |
| Full Architecture Analysis (Deep) | 用户显式调用默认 | 深度三分流结论、evidence-backed candidate competition、handoff；满足 Report Upgrade Gate 时生成 interactive HTML report | No code changes |
| Exhaustive Architecture Analysis | 用户明确要求 "极致 / 全覆盖 / 大水漫灌" 等关键词 | 多证据面交叉、历史/跨仓库变种、并行调查；通常满足 Report Upgrade Gate，可生成 interactive HTML report | No code changes |
| Transition Handoff | 用户接受一个或多个结构方向 | Migration hypotheses for pragmatic evaluation | No code changes |
| Authorized Implementation | 用户审阅计划后明确授权实现 | Scoped code changes with verification | Only within explicit authorization |

任一 Mode 都可在用户明确要求时附带 Markdown 源报告（`.md`），用于 agent 接力或源文件交付；这是升级项，不是默认项。

不要静默从 analysis 跳到 implementation。

### Investigation Kernel Adaptation

本 skill 参考项目级 Investigation Kernel，但本段是 standalone local adaptation：即使 single skill copied out，也必须能独立执行结构调查。

- **Concept version**：`investigation-kernel@v1`。
- **Derived from**：`docs/contracts/investigation-kernel.md`；本地段落按 `docs/contracts/portable-core-drift-model.md` 作为 intentional projection 审查。
- **Sync reference**：`docs/contracts/analysis-skill-registry.md` 中 `abstraction-architect` 行，以及 `references/method_and_report_spec.md`。
- **Local projection**：Pressure Map、candidate competition、admissibility gate、constraint reality filter。
- **Intentional differences**：本 skill 额外要求 no new abstraction / local deletion wins 基线、process spatialization 反例竞争和 structural rewrite claim gate。
- **Fallback**：只有已通过 Report Upgrade Gate 且需要 HTML 时，才使用 `reviewable-html-report` capability 或 repo-local `report_base.md`。若这些不可用，使用 `references/fallback.html` 交付 self-contained static HTML，并保留核心结论、TOC、稳定 section id、证据附录、Mermaid source fallback 和非持久反馈区。

- **analysis artifact root**：正式分析优先写入当前项目的 `reports/abstraction-architect/` 或既有同名报告目录；只允许写 Markdown/HTML 报告、evidence ledger、candidate notes、transition handoff 和 review exports。
- **analysis-only boundary**：默认不得修改产品代码、测试、配置、迁移、依赖锁或 Git 历史。任何 implementation、migration、rewrite 或 Git 操作都需要报告后的 **new explicit user authorization**。
- **evidence map**：先建立 structural pressure map，覆盖关键 runtime path、domain representations、workflow state、boundary glue、constraint evidence 和 user-facing workflow burden，再竞争 candidates。
- **handoff ledger projection**：作为 producer/consumer，保留稳定 `evidence_id`，并至少记录 type、source artifact、observation、confidence、consumed proposal/admissibility ID；接手其他 skill 的 ledger 时复用旧 ID，只追加新证据。
- **decision triage before abstraction**：candidate competition 必须先给出 `local deletion wins`、`boundary repair wins` 或 `structural candidate worth testing`。局部删除、合并重复、删除旧分支、文案/交互澄清或边界修复能消除痛点时，优先报告这些结果，而不是升级为 canonical object。
- **candidate proof route**：推荐 structural rewrite 或 canonical model 前，必须说明 family proof、difference proof、preservation proof、future deformation proof 和 falsifier。若 proof route 缺关键证据，候选最多为 `promising but unproven`。
- **abstraction fitness score**：对候选做非绝对评分，覆盖 clear examples、tool yield、cross-context link、practical sufficiency、hot path value 和 tiny complete loop。评分只辅助排序与用户决策，不得替代 admissibility gate 或作为一票否决。
- **IR vs domain model fork**：当压力来自多个 reports、ledgers、artifacts、workflows 或 callers 之间的转换/同步时，必须问一次：缺的是最终 domain model，还是一个稳定 intermediate representation、projection registry 或 transformation protocol。
- **anti-beauty gate**：模型临时提出的新结构候选必须进入同一 competition table，按 evidence、deleted complexity、hot path value、preserved differences、counterexamples、separating probes 和 transition seam 评估；不得因为候选概念漂亮、统一或高级就推荐，也不得因为候选未在 reference 中预定义而自动排除。
- **coverage debt**：缺失 telemetry、history、runtime behavior、user context、外部约束或迁移风险时，必须写入 unknowns/coverage debt，不得用结构直觉补齐。
- **claim permission**：没有 observed evidence、constraint reality filter、admissibility gate 和反例竞争时，不得声称 structural rewrite、canonical model、3x simplification 或删除整类复杂度已经成立。
- **budget-aware stop review**：low-information wave 只触发停止复盘；Normal 倾向快速收敛，Deep 至少复核核心 pressure map，Exhaustive 只有在剩余关键未知的 marginal information gain 变低时停止。不是固定两轮停止。

## 核心工作流

1. 明确 target repository、requested mode 和 evidence limits。
2. 检查足够的 code、docs、tests、runtime paths 和用户上下文，建立 evidence ledger。
3. 对继承约束做真实度过滤：列出当前系统感受到的约束（兼容性、命名、包结构、既有实现形状、迁移恐惧等），区分真实约束（公开 API、持久化数据、已文档化集成、用户承诺、部署约束、合规要求）和惯性约束（内部调用方、过时命名、旧包结构、"diff 太大"等）。只对真实约束保留兼容路径；为惯性约束保留 shim 的，必须命名它保护的具体契约。详见 `references/method_and_report_spec.md` 的 Constraint Reality Filter 章节。
4. 评估 candidates 时使用 `references/method_and_report_spec.md`，尤其是 process spatialization、observational adequacy、local-to-global certificate、admissibility、candidate competition、report requirements。
5. 默认输出一屏 structural decision：三分流结论、最高杠杆候选或不升级理由、关键证据、coverage debt 和最小下一步。
6. 只有满足 Report Upgrade Gate 时，才产出 HTML 架构报告：写 `structural_abstraction_architect_report_{YYYYMMDD}_{HHMM}.html` 作为 user-facing interactive review surface。HTML 必须包含章节索引和点击跳转，最终回复提供报告路径和可点击 `file://` URL。共享报告机制优先使用 `reviewable-html-report` capability；当前仓库可把 `skills/reviewable-html-report/references/report_base.md` 作为可选增强，不要把 sibling path 当作 standalone 硬依赖。若该能力不可用，使用 `references/fallback.html` 生成 self-contained 静态 HTML。只有用户明确要求 Markdown 源（agent 接力 / 源文件交付），或环境完全无法产出 HTML 时，才另写同名 `.md` 作为 agent-readable source of truth，并与 HTML 共享同一 evidence ledger、proposal IDs 和结论。
7. 如果用户在报告或 handoff 后要求实现，必须先得到明确授权，并把修改限制在已接受 transition boundary 内。

## 报告交付契约

- **HTML 是升级交付，不是深度思考的证明**：只有当候选超过 3 个、证据账本/评审卡会改变用户判断、用户明确要求正式报告、或需要长期归档/agent 交接时才生成。HTML 包含 executive summary、evidence ledger、pressure map、candidate/proposal IDs、admissibility gate 结果、rejected/deferred abstractions、transition handoff、unknowns 和 verification notes；同时提供拓扑/流程可视化、proposal cards、筛选、展开证据、review/export controls、章节索引、锚点跳转和用户反馈路径。
- **Markdown 是升级交付**：默认不生成；只在用户明确要求 agent 接力 / 源文件交付，或环境无法产出 HTML 时才补 `.md`，使用同一 timestamp basename 与 HTML 共享 evidence ledger、proposal IDs 和结论。
- **命名一致**：当因用户明确要求或环境兜底而追加 Markdown 时，使用与 HTML 同一 timestamp basename。如果环境无法生成 HTML，必须交付 Markdown 兜底，并在最终回复中说明 HTML 缺口。
- **最终回复**：默认先给一屏三分流结论和最小下一步；若生成 HTML，再列出报告路径和可点击 `file://` URL、说明是否仅提供预览链接或按用户要求打开 HTML，并声明没有修改代码。

## Resource Map

- `references/method_and_report_spec.md`：完整 structural method、admissibility gate、evidence rhythm、Markdown/HTML report schema、anti-goals、execution flow。
- `references/discovery_patterns.md`：pressure map 不清或 candidates 偏弱时的 discovery prompts。
- `references/fallback.html`：无 companion capability 时的 skill-local self-contained HTML 模板。
- `reviewable-html-report` capability：需要 interactive report 时的共享 HTML report mechanics；repo-local `skills/reviewable-html-report/references/report_base.md` 只是可选增强，不可用时使用静态 HTML fallback，不阻塞报告交付。

## 完成标准

- 区分 observed evidence、inference、unknowns。
- 每个 proposal 都通过 admissibility gate 分类。
- 推荐候选包含 candidate proof route；fitness score 作为展开细节或 candidate card 维度呈现，不把评分噪音放进默认结论。
- candidate competition 至少覆盖低抽象 baseline、主候选、rival explanation，并保留或驳回模型临时提出的新候选。
- 必要时包含 rejected 或 deferred abstractions。
- 默认输出三分流结论：`local deletion wins`、`boundary repair wins` 或 `structural candidate worth testing`，并说明不升级/升级理由。
- 满足 Report Upgrade Gate 时，HTML 交互报告包含可点击章节索引；最终回复提供报告路径和可点击 `file://` URL，主动打开只作为用户要求或明确 GUI 环境下的可选预览。
- 当用户要求或环境兜底而生成 Markdown 源报告时，与 HTML 共享同一 evidence ledger、proposal IDs 和结论。
- 未经用户在 transition plan 后明确授权，不修改 production code、tests、configuration、migrations 或 infrastructure。
