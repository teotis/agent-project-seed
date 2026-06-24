---
name: deep-flow-sweep
description: >
  大水漫灌式全维度质量扫雷。用于预算极其充足时，对项目主流程、功能链路、稳定性、性能、测试覆盖、日志/输入治理、近期改动、历史会话发现、架构漂移、依赖健康、安全面、Agent 自动化面、长期趋势和跨仓库边界做长时间、全覆盖、仅分析的深度审计，构造失败场景，证据驱动地产出可审阅报告、任务包和后续分工建议。
  Use for high-budget exhaustive analysis-only quality sweeps, pre-release risk discovery, multi-dimensional auditing, and evidence-backed task packaging.
---

# Deep Flow Sweep

## Mission

以极高预算覆盖项目主流程和相关风险面，预测真实失败场景，验证关键推断，产出证据充分的风险报告与后续任务包。只分析，不修改产品代码。

## Invocation Contract

本 skill 是 sweep 类深度审计，**只支持用户显式启动**，不支持 agent active 自启用：

- 用户点名 `deep-flow-sweep`，或明确要求“大水漫灌、全覆盖质量审计、主流程扫雷、pre-release risk discovery”时，进入正式 sweep；默认 `Exhaustive + balanced`，只有用户明确要求轻量、缩小范围或聚焦时才降级。
- 其他 agent / skill 即便发现质量、稳定性、主流程或发布风险信号，也不得主动启动本 skill；只能写入 finding / one-screen handoff capsule，等待用户明确授权。
- 其他正在运行的 architect、sweep、Deep 或 Exhaustive workflow 只能写入 handoff 建议，**不得自动串联启动**本 skill。
- 完全无法识别目标，或下一步需要 implementation、不可逆操作、账号状态变更、发布或推送时才询问。

不适用于单一已知 bug、普通 diff review、单点架构决策、直接修复或仅需局部模块解释的任务。

## Output Language

私有版默认使用中文交付：报告正文、任务包、最终回复和 HTML UI 文案优先中文。保留必要的英文术语、命令、标识符、profile 名称和证据原文。只有用户明确要求英文、目标交付物面向英文读者，或正在维护公开英文版本时，才切换为英文。

## Safety

- 启动后锁定 **analysis-only**。首个写入前声明 artifact root，优先使用 `reports/deep-flow-sweep/<run_id>/`。
- 只允许写报告、manifest、evidence ledger、task package 和 review export；不得修改产品源码、测试、配置、依赖锁、生成资产或 Git 历史。
- 严格区分 observed、measured、inferred、unavailable、deferred。
- P0/P1 必须有当前、直接、可达路径证据；scanner、历史标签、缺测试或架构偏好不能单独授权高严重度结论。

## Budget And Profiles

| Envelope | Baseline |
|---|---|
| Normal | 关键流程图、最高风险场景、轻量证据波 |
| Deep | Normal + Git / memory / root-cause evidence |
| Exhaustive | Deep + 长期趋势、跨仓边界、并发独立 probes |

默认 profile 为 `balanced`。用户强调主流程、可靠性、性能、安全、可观测性、测试有效性或项目治理时，加载对应 profile playbook。Focus 不得移除主流程、恢复、证据质量和 analysis-only 基线。

## Model Adaptation Contract

把本 skill 的规则按刚性分层使用：

- **Hard invariants**：analysis-only、observed/measured/inferred 区分、P0/P1 直接可达路径证据、coverage debt、Falsification Ledger、Outcome Replay、未授权不修复，以及不把 UI/日志/旧报告当成真实完成证据。这些保护发布判断和用户信任，不能被“充分发挥模型能力”绕过。
- **Adaptive heuristics**：focus profile、failure scenario classes、arsenal weapons、Git/memory/trend/cross-repo probes、报告展开和并发策略都是触发式菜单。它们应由 flow signal、evidence gap、completion probability、expected information gain 和 false-positive guard 触发，不因预算高而平均铺开，也不构成封闭 checklist。
- **Creative extension lane**：当模型识别到 profile 外的项目特有风险面、失败机制或成功 oracle 时，应临时命名该 lens，记录 trigger、reachable path、evidence artifact、counterexample / false-positive guard、stop condition 和 disposition；只要能证据化，就可以进入 finding、coverage debt 或 task package。高质量新增 lens 必须与内置 profile / failure scenario 候选同台竞争，而不是因为未写入 reference 被压掉。

每次正式 sweep 都做一次 **skill value check**：本 skill 是否比普通分析新增了端到端 flow coverage、失败场景建模、证据纪律、可回放任务包或 release-risk 判断。若没有，降级为用户已授权范围内的 targeted / chat-only 结论，或明确建议不用 full sweep。

如果内置 profile、failure-scenario 模板或报告结构会诱导错误结论，必须拒绝模板，说明原因，并改用证据驱动的新 lens、降级路径或 handoff。

## Required References

执行前按需读取：

1. `references/full-workflow.md`：完整工作流、archetype、报告 schema、并发模型、错误清单和完成标准。
2. `references/analysis-arsenal.md`：按触发信号、成本、完成概率和 information gain 选择方法。
3. `references/evidence-decision-model.md`：severity / confidence / disposition 与直接证据门槛。
4. `references/focus-profiles.md`：profile 路由；再读取被选 profile 的 playbook。
5. `references/fallback.html`：`reviewable-html-report` capability 不可用时的本地静态模板。

维护时与 `docs/contracts/evidence-ledger.md`、`docs/contracts/output-modes.md` 和 `docs/contracts/architect-routing.md` 同步；单独复制本 skill 时仍以本地 reference 为运行时契约。

## Core Workflow

### 1. Establish Scope

推断目标、主流程、budget、profiles、project archetype 和并发收益。读取仓库指导、Git 状态、验证命令、近期计划和既有报告。建立 manifest，记录 `run_id`、SHA、dirty state、scope、时间、工具可用性与 blocker。

### 2. Build Coverage Matrix

在 finding 前记录：

- flow / risk family；
- trigger 到 success / failure surface 的 reachable path；
- inspected artifacts；
- evidence status；
- unknowns / coverage debt；
- next weapon 与 expected information gain。

每行使用稳定 `evidence_id`，复用输入 ledger 的 ID，只追加新证据。路径不完整时只能标记 `investigate`、`defer` 或 `coverage_debt`。

### 3. Map Flows And Failure Scenarios

映射 entry point、lifecycle、data path、environment path 和 ownership boundary。对适用主流程覆盖 happy path、空/坏输入、状态转换、并发、环境漂移、外部依赖、回归面、可观测性、恢复、agent parity 和跨模块一致性。

可用时先运行：

```bash
python3 <skill-dir>/scripts/flow_probe.py <root> --pretty
```

Probe 只用于候选排序，不能直接生成 finding。

### 4. Run Evidence Waves

先用最低成本可靠方法，再按 `analysis-arsenal.md` 追加工具。每轮记录新高风险候选、证据增减、已关闭未知、未覆盖关键流和继续收益。连续两轮低信息增益只触发 stop review。

Profile playbook 之外的项目特有 lens 允许加入证据波；新增 lens 必须说明它改变了哪条 reachable flow、success oracle、risk family 或 release decision，并进入同一 risk ranking / disposition 竞争。

Deep/Exhaustive 必须包含 Git archaeology 与 cross-session intelligence；Exhaustive 还要评估趋势、热点迁移和跨仓边界。

### 5. Rank And Falsify

分别记录 severity、confidence、disposition。每个 finding 必须说明：

- 可达失败路径和影响；
- 当前直接证据；
- counter-evidence / false-positive risk；
- verification 或 falsification route；
- coverage gap。

### 6. Package Follow-Up

把可执行项转换为 `docs/contracts/task-package-contract.md` 兼容的 task package，并包含 Falsification Ledger 与 Outcome Replay stub。不得在 sweep 内进入修复。

### 7. Route Without Auto-Chaining

路由是建议，不是内部调用：

- 局部模块、interface、seam 或 deep module 问题：优先建议 `codebase-design`。
- 缺失 invariant、重复表示、散落状态：建议 `abstraction-architect`。
- 遗留兼容、迁移、pilot、rollback、adoption economics：建议 `renewal-architect`。
- 用户价值上限或决策体验：建议 `user-value-architect`。
- `improve-codebase-architecture` 仅在用户明确想做全库架构机会扫描时建议，绝不自动启动。
- 任何 architect、sweep、Deep 或 Exhaustive 路径都只输出 one-screen handoff capsule，等待用户授权。

### 8. Synthesize And Deliver

主叙事使用 Decision-First Output：

- 默认 3-5 个核心风险或 failure families；
- P0/P1、安全、数据丢失、release blocker 不受 cap 限制；
- 证据只在改变结论时进入主叙事；
- 完整 coverage / scenario / weapon ledger 下沉到 appendix；
- handoff capsule 包含 finding/package ID、evidence IDs、severity、confidence、disposition、next action、验证入口和 owner skill。

## Output Contract

正式 sweep 默认 `paired`：

- Markdown：`deep_flow_sweep_report_{YYYYMMDD}_{HHMM}.md`
- HTML：`deep_flow_sweep_report_{YYYYMMDD}_{HHMM}.html`

只有用户明确要求 `chat-only` / `no-files` 时降级，并记录 coverage debt。Markdown 是事实源，HTML 不得引入新结论。默认提供路径和可点击 `file://` URL，不主动打开浏览器。

优先使用 `reviewable-html-report` capability。若不可用，使用 `references/fallback.html` 生成 self-contained 静态 HTML，至少保留 TOC、稳定 section IDs、evidence appendix、Mermaid source 和非持久反馈区。

## Completion Gate

完成前确认：

- scope、budget、profiles、artifact root、manifest 和 stop reason 已记录；
- project risk profile 与关键 applicability disposition 已记录；
- coverage matrix 先于 findings；
- 所选 profile playbook completion gate 已通过；
- 主流程、恢复路径和高风险场景已覆盖到预算允许程度；
- Deep+ 完成 Git 与历史证据核查；Exhaustive 完成趋势核查；
- 每个 finding 有 evidence、severity、confidence、disposition 和 falsification route；
- profile 外新增 lens 已记录 trigger、reachable path、证据产物、false-positive guard 和保留/放弃理由；
- 每个后续动作已成为 task package、handoff 或 deferred check；
- 报告遵守 Decision Surface Cap、Evidence Compression 和 Delete-The-Scaffold；
- 未验证事项明确标为 external、deferred 或 not run；
- 没有具体 finding 时诚实给出 clean bill of health。
