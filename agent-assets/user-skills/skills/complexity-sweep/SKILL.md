---
name: complexity-sweep
description: >
  极致深度的代码复杂度扫雷。用于预算充足时，对代码工程的低效复杂结构、低效复杂设计、低效臃肿环节做 micro / meso / macro 三层全覆盖、仅分析的深度审计，证据驱动地查找过度嵌套、循环依赖、散落逻辑、过度抽象、死代码、配置分散、数据流迂回和编排臃肿，产出可审阅报告、简化任务包和交叉升级建议。
  Use for exhaustive analysis-only complexity sweeps and evidence-backed simplification task packaging.
---

# Complexity Sweep

## Mission

深入扫描 micro、meso、macro 三层复杂度，识别真正增加理解成本、变更成本和 bug 风险的结构，产出证据充分的简化任务包。只分析，不直接重构。

## Invocation Contract

本 skill 是 sweep 类高预算分析工具，**仅支持用户显式启动**：

- 用户点名 `complexity-sweep`，或明确要求复杂度审计、臃肿扫描、全覆盖简化扫雷时，进入正式 sweep；默认 `Exhaustive` 并覆盖三层，只有用户明确要求轻量、缩小范围或聚焦时才降级。
- Agent 不得在普通分析、规划、调试、PR review 或 architect workflow 中自行启动本 skill；即便发现清晰复杂度信号，也只能记录 highest-leverage finding、证据入口、coverage debt 和 one-screen handoff，等待用户显式授权。
- 其他正在运行的 architect、sweep、Deep 或 Exhaustive workflow 只能写 handoff，**不得自动串联启动**。
- 完全无法识别目标，或下一步需要 implementation、不可逆操作、账号状态变更、发布或推送时才询问。

不适用于单个 PR review、紧急 bug、局部命名润色、纯架构建模、遗留迁移规划或多维质量扫雷。

## Output Language

- 私有交付默认中文；保留必要的英文术语、命令、标识符和 evidence 原文。

## Safety

- 启动后锁定 **analysis-only**。首个写入前声明 artifact root，优先使用 `reports/complexity-sweep/<run_id>/`。
- 只允许写报告、manifest、evidence ledger、task package 和 review export；不得修改产品源码、测试、配置、依赖锁、生成资产或 Git 历史。
- 指标阈值、scanner、历史标签和命名偏好只是调查信号，不能单独建立 finding。
- P0/P1 必须有当前直接证据，证明真实 bug 风险、重复变更成本、onboarding drag、broken contract 或关键路径耦合压力。

## Budget

| Envelope | Baseline |
|---|---|
| Normal | 目标范围三层地图 + 高价值 pattern checks |
| Deep | Normal + root cause、Git、constraint survival |
| Exhaustive | Deep + 趋势、跨仓 variants、并发独立 probes |

预算购买的是方法选择空间，不是强制运行全部 analyzer。每轮按 evidence gap、completion probability 和 expected information gain 选下一方法。
连续两轮低信息增益只触发 stop review：若没有新增高价值候选、没有增强证据、没有关闭关键未知项，就记录 saturation reason 并停止扩张，而不是为了花完预算运行全部工具。

## Model Adaptation Contract

把本 skill 的规则按刚性分层使用：

- **Hard invariants**：analysis-only、当前直接证据门槛、P0/P1 claim permission、Falsification Ledger、Behavior Preservation Vector、Outcome Replay、task package 边界和未授权不实现。这些不能因为模型更强、预算更高或目录清单未覆盖而放松。
- **Adaptive heuristics**：三层地图、pattern catalog、arsenal weapons、Git archaeology、趋势分析、报告展开和停止策略是触发式菜单。它们按 evidence gap、expected information gain、false-positive risk 和 stop condition 被选择或跳过，不是封闭 ontology，也不是必须逐项完成的合规清单。
- **Creative extension lane**：当模型从项目事实中发现 catalog 外的新复杂度方向时，应临时命名该 lens，记录 trigger、expected information gain、evidence artifact、counterexample / false-positive guard、stop condition 和 disposition；只要能通过证据、反例和行为保持检查，就必须进入与内置 pattern / arsenal 的候选竞争，可成为 finding、coverage debt 或 task package。不得因为方向未写入 `complexity-patterns.md` 就压掉高质量发现。

每次正式 sweep 都做一次 **skill value check**：本 skill 是否相对普通分析增加了 coverage、证据纪律、任务包、反例检查、报告可审阅性或 replay 价值。若没有，降级为用户已授权范围内的 targeted scan、chat-only 结论或建议不用 full sweep。

如果内置 pattern catalog、复杂度指标、报告结构或历史模板会诱导错误结论，必须拒绝模板，说明它误导在哪里，并改用更贴近当前系统约束的 lens、降级路径或 no-finding disposition。

## Required References

执行前按需读取：

1. `references/full-workflow.md`：完整三层流程、project shape、报告 schema、并发模型、错误清单和完成标准。
2. `references/analysis-arsenal.md`：方法触发条件、成本和停止复盘。
3. `references/complexity-patterns.md`：micro / meso / macro pattern catalog。
4. `references/simplification-safety.md`：severity / confidence / disposition、Constraint Survival Test 和 Behavior Preservation Vector。
5. `references/fallback.html`：`reviewable-html-report` capability 不可用时的本地静态模板。

维护时与 `docs/contracts/evidence-ledger.md`、`docs/contracts/output-modes.md` 和 `docs/contracts/architect-routing.md` 同步；单独复制本 skill 时仍以本地 reference 为运行时契约。

## Core Workflow

### 1. Establish Scope

推断目标模块、budget、project shape、主要 comprehension paths 和并发收益。读取仓库指导、Git 状态、验证命令、静态工具、历史报告和跨仓边界。建立 manifest，记录 `run_id`、SHA、dirty state、scope、时间、工具可用性和 blocker。

### 2. Build Coverage Matrix

在 finding 前记录：

- structural level：micro、meso、macro、history、verification；
- comprehension path；
- inspected artifacts；
- evidence status；
- unknowns / coverage debt；
- next weapon 与 expected information gain。

每行使用稳定 `evidence_id`，复用输入 ledger 的 ID，只追加新证据。路径不完整时只能标记 `investigate`、`defer` 或 `coverage_debt`。

### 3. Build Three-Level Structure Map

- **Micro**：函数、类、分支、嵌套、参数、side effects、命名与重复。
- **Meso**：模块依赖、循环、cohesion、config/validation/error duplication、shotgun surgery。
- **Macro**：数据流、orchestration、boundary、abstraction depth 和跨切面一致性。

可用时先运行：

```bash
python3 <skill-dir>/scripts/complexity_probe.py <root> --pretty
```

Probe 只用于排序。行数、嵌套和依赖数必须结合真实 comprehension path 与变更影响解释。

### 4. Collect Evidence And Root Causes

按 `analysis-arsenal.md` 选择 change coupling、variant search、architecture fitness、cognitive walkthrough、abstraction economics、mutation sampling 或 historical comparison。每轮记录证据变化、已关闭未知、未扫描关键路径和继续收益。

Pattern catalog 和 arsenal 之外的项目特有 lens 必须加入本轮候选竞争，但必须留下与内置 weapon 同等级的选择理由、证据产物、反例检查、stop condition 和 disposition。

Deep/Exhaustive 必须：

- 使用 `simplification-safety.md` 执行 Constraint Survival Test；
- 查明复杂度来源与 compensation chain；
- 做 Git complexity archaeology；
- 复核历史 finding，不继承旧 severity。

Exhaustive 还要评估 complexity growth、hotspot migration、simplification frequency 和 test-to-complexity ratio。

### 5. Rank And Falsify

分别记录 severity、confidence、disposition。每个 finding 必须说明：

- 具体 location 和 pattern；
- measured / observed signal；
- 对理解、变更、缺陷或 onboarding 的实际影响；
- counter-evidence、style-preference guard 和 false-positive risk；
- verification gap；
- Constraint Survival Test 与 Behavior Preservation Vector。

### 6. Package Simplification

把可执行 hotspot 转换为 `docs/contracts/task-package-contract.md` 兼容的 task package，并包含 Falsification Ledger、blast radius、rollback safety 和 Outcome Replay stub。不得在 sweep 内进入实现。

### 7. Route Without Auto-Chaining

路由是建议，不是内部调用：

- 局部 module、interface、seam、adapter 或 deep-module 问题：优先建议 `codebase-design`。
- 重复表示、缺失 invariant、散落状态：建议 `abstraction-architect`。
- 遗留兼容、迁移、pilot、rollback、adoption economics：建议 `renewal-architect`。
- 复杂度只是更广质量问题的一部分：建议 `deep-flow-sweep`，等待用户显式授权。
- `improve-codebase-architecture` 仅在用户明确想做全库架构机会扫描时建议，绝不自动启动。
- 任何 architect、sweep、Deep 或 Exhaustive 路径都只输出 one-screen handoff capsule。

### 8. Synthesize And Deliver

主叙事使用 Decision-First Output：

- 默认 3-5 个 complexity patterns、simplification directions 或 high-priority hotspots；
- P0/P1、active bug、数据丢失和 release blocker 不受 cap 限制；
- 证据只在改变结论时进入主叙事；
- 完整 coverage / structure / weapon ledger 下沉到 appendix；
- handoff capsule 包含 finding/package ID、evidence IDs、severity、confidence、disposition、next action、验证入口和 owner skill。

## Output Contract

正式 sweep 默认 `paired`：

- Markdown：`complexity_sweep_report_{YYYYMMDD}_{HHMM}.md`
- HTML：`complexity_sweep_report_{YYYYMMDD}_{HHMM}.html`

只有用户明确要求 `chat-only` / `no-files` 时降级，并记录 coverage debt。Markdown 是事实源，HTML 不得引入新结论。默认提供路径和可点击 `file://` URL，不主动打开浏览器。

优先使用 `reviewable-html-report` capability。若不可用，使用 `references/fallback.html` 生成 self-contained 静态 HTML，至少保留 TOC、稳定 section IDs、evidence appendix、Mermaid source 和非持久反馈区。

## Completion Gate

完成前确认：

- scope、budget、artifact root、manifest 和 stop reason 已记录；
- project shape 与方法路由已记录；
- coverage matrix 先于 findings；
- micro、meso、macro 均按预算覆盖；
- Deep+ 完成 root cause、Constraint Survival、Git 与历史证据核查；
- Exhaustive 完成趋势核查；
- 每个 finding 有 evidence、severity、confidence、disposition 和 falsification route；
- 每个简化建议有 behavior preservation、verification gate、blast radius 和 rollback 判断；
- catalog 外新增 lens 已记录 trigger、证据产物、false-positive guard 和为何保留或放弃；
- 每个后续动作已成为 task package、handoff 或 deferred check；
- 报告遵守 Decision Surface Cap、Evidence Compression 和 Delete-The-Scaffold；
- 未验证事项明确标为 external、deferred 或 not run；
- 没有具体 finding 时诚实给出 clean complexity bill of health。
