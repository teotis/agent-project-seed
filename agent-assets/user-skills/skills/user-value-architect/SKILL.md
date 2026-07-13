---
name: user-value-architect
description: >
  Use when a project, product, feature, tool, workflow, AI agent, PRD, report, or app needs high-budget, multimodal, analysis-only exploration of user-perceived value upside: user experience, trust, efficiency, goal completion, retention, default experience, feedback loops, feature/design/workflow improvements, or long-term capability building. Use when 30%+ is only the entry line and the user wants to pursue 2x, 3x, or category-shift value. Exclude internal-only optimization unless it clearly reaches users.
---

# User Value Architect

## Mission

从用户可感知价值出发，寻找能明显提升体验、信任、效率和目标达成的高上限方向，同时保留小而确定的用户可见改进。只分析，不修改产品。

## Invocation And Depth

本 skill 仅支持用户显式调用：

- 用户显式调用默认 **Deep Value Analysis**。
- Claude/Codex agent 不得自行 active 启动本 skill；普通任务中发现用户价值信号时，只输出最小价值观察、coverage debt 或 handoff 建议，等待用户点名 `$user-value-architect`。
- **Exhaustive** 仅在用户明确要求极致、全覆盖、充分发挥模型能力或多模态全面核查时进入。
- 从 workspace、材料和上下文能推断的 scope、persona、budget 和输出形态直接推断；完全无法识别对象，或下一步需要 implementation、实验、发布、迁移、不可逆操作时才询问。

不适用于纯内部重构、单一 bug、普通 code review、已选方案的任务拆解，或主要由安全发布、遗留迁移、架构不变量、质量扫雷主导的问题。

## Language And Safety

- 私有交付默认中文；保留必要英文术语、命令、标识符和证据原文。
- 启动后锁定 **analysis-only**。正式分析优先写入 `reports/user-value-architect/`。
- 只允许写报告、evidence ledger、candidate matrix、validation plan、task package 和 review export；不得修改产品代码、测试、配置、运行时或 Git 历史。
- 区分 observed evidence、inference、hypothesis、unknowns。
- 无 UI、截图、录屏或运行路径时继续文本降级分析，但必须标记 `visual_evidence_unavailable` 或 coverage debt。

## Value Model

**Two-Track Candidate Model**:

同时维护两条候选轨道：

- **High-ceiling candidates / high-ceiling candidates**：30% 是入场线，继续探索 2x、3x 或 category-shift；必须给出 floor、ceiling、path to ceiling、evidence strength 和 disproof test。
- **Small high-certainty improvements / small high-certainty improvements**：低投入、低风险、用户可见、证据确定；标记为 `optimize`、`fast validation bet` 或 `do-now`，不得伪装成高上限押注，也不得自动丢弃。

30% entry line applies to high-ceiling recommendations；small high-certainty improvements do not need to pretend to be ceiling bets. do not inflate 小改进的 floor/ceiling；do not automatically drop 它们。

高杠杆方向必须说明它删除哪一类反复出现的用户负担、失败路径、手工翻译、低信任或决策成本。用户不可感知的内部整洁不能单独成为推荐。

**Human Terminal Fit（人类终端适配性）** 是默认价值镜头：用户的注意力、记忆、上下文保持、判断力、操作耐心和信任预算都有限。候选不仅要问“用户能否感知”，还要问入口是否更简洁、默认路径是否更直观、完成目标需要的操作/判断/上下文重建是否减少，以及强能力是否真的进入用户可达路径。

## Model Adaptation Contract

把本 skill 的规则按刚性分层使用：

- **Hard invariants**：analysis-only、Project Immersion、Value Theory、Specificity Gate、Advice Atomicity、外部 ceiling 校准、naked recommendation 禁止、claim permission 和未授权不实现。这些保护用户价值判断不被通用产品套话替代。
- **Adaptive heuristics**：两轨候选、persona critique、competitive ceiling、报告形态、证据波和候选分类是方法菜单。模型可以根据用户材料、产品阶段和证据强度调整顺序和深度。
- **Creative extension lane**：当模型发现 workflow、trust、default experience、feedback loop 或长期能力上的新价值机制时，应临时命名该 mechanism，记录 user-visible moment、Evidence IDs、current/after slice、disproof test、counterexample 和 floor/ceiling；只要通过 gate，就可以成为候选，即使它不在 reference 的示例方向里。

每次正式分析都做一次 **skill value check**：本 skill 是否比普通体验建议新增了用户路径证据、项目特有 leverage、候选分级、反例、验证切片或高上限探索。若没有，降级为 Value Scan、chat-only 结论或建议不用 full workflow。

## Formal Contract Snapshot

- 正式报告写入 authoritative workspace 的 `reports/user-value-architect/`，不要写到 `.claude/worktrees/`、临时 package branch 或 agent 子线程里长期滞留。报告命名保留 `reports/user-value-architect/user_value_architect_report_{YYYYMMDD}_{HHMM}.md` 与 `reports/user-value-architect/user_value_architect_report_{YYYYMMDD}_{HHMM}.html`。
- 私有版正式报告的可见正文、标题、表格字段和 HTML UI 文案默认使用中文；英文只保留在必要的技能名、文件名、代码标识符、指标名和行业术语中。
- HTML 评审面优先先读取 `../reviewable-html-report/SKILL.md` 和 `../reviewable-html-report/references/report_base.md`，保留 review-controls、data-card-id 和 feedback export。
- Deep/Exhaustive 必须先完成 Project Immersion Protocol：Asset inventory、User-visible surface inventory、three concrete user paths 和 evidence gaps；证据不足时标记 `blocked_by_evidence`。
- 推荐必须通过 Fact Map Before Advice、Value Theory / Project-Specific Leverage、Specificity Gate、No Naked Recommendations 和 Advice Atomicity Contract；每个推荐需要 2-5 specific artifacts、Evidence IDs、Current experience slice、After experience slice，并说明为什么不是“任何同类项目都适用”的泛化建议。
- 输出压缩遵守 Decision-First Output、Evidence Compression Gate、Main Narrative Cap、One-Screen Handoff Capsule 和 Delete-The-Scaffold Rule；recommendation permission 不足时降级为 hypothesis、validate-first、defer 或 handoff。

## Required References

执行前按需读取：

1. `references/full-workflow.md`：完整工作流、candidate model、gate、报告 schema、chat-only schema 和完成标准。
2. `references/method-and-report.md`：Deep / Exhaustive evidence protocol、Project Immersion、persona critique、报告与任务包细节。
3. `references/fallback.html`：`reviewable-html-report` capability 不可用时的本地静态模板。

维护时与 `docs/contracts/evidence-ledger.md`、`docs/contracts/output-modes.md` 和 `docs/contracts/architect-routing.md` 同步；单独复制本 skill 时仍以本地 reference 为运行时契约。

## Core Workflow

### 1. Resolve Scope And Target

确定用户、真实场景、目标结果、当前摩擦、成功信号、30% entry line 和理想上限。默认不中断询问；自动推断的 scope 在报告开头声明。

### 2. Build Fact Map

Deep/Exhaustive 在建议前完成：

- asset inventory；
- user-visible surface inventory；
- 至少三条具体 user paths，或覆盖项目全部可用路径；
- promise-reality tensions；
- stable Evidence IDs；
- evidence gaps / coverage debt。

Fact Map 是 recommendation permission 的前置层，不是主报告默认叙事。

### 3. Establish Value Theory

说明用户真正稀缺的资源、项目独特资产、最大价值泄漏和 project-specific leverage；同时显式判断当前体验如何消耗用户这个有限终端的注意力、记忆、操作耐心、判断力和信任预算。说不清独特杠杆时，只能输出探索性候选，不能把通用自动化、dashboard、记忆或“智能路由”包装成最高上限。

### 4. Gather Evidence And External Coordinates

读取适用的代码、文档、UI、输出、日志、测试、反馈、analytics、历史报告和外部参照。当最新产品事实、价格、benchmark 或公开评价影响 ceiling 时必须验证来源；无法验证则标记 unknown / hypothesis。

### 5. Map User Success

追踪 trigger、setup、first value、core loop、failure/recovery、trust formation 和 long-term compounding，定位等待、困惑、重复操作、认知负担、低信任和结果不确定性。对关键路径估算用户要做的操作数、判断数、上下文重建次数和手工恢复点；能把 10 个操作压成 1 个可靠动作的候选，优先进入高杠杆竞争。

### 6. Generate And Gate Candidates

候选可来自功能、设计、流程、默认体验、反馈、信任、长期能力和价值 framing。每个 `recommend`、`validate-first` 或 strategic bet 必须同时包含：

- 2-5 个具体 artifacts 与 Evidence IDs；
- user-visible moment；
- Current experience slice；
- After experience slice；
- Human Terminal Fit delta（入口、默认路径、操作数、判断数、上下文重建、恢复成本和能力可达性的变化）；
- structural value mechanism；
- First validation / disproof slice；
- rejected alternative 与 counterexample。

缺任一项时降级为 brainstorm、hypothesis、defer 或 `blocked_by_evidence`。禁止 naked recommendations。

Reference 示例之外的新价值机制允许进入候选池，但必须和 high-ceiling / small high-certainty 两轨同台竞争，并满足相同证据、反例和验证要求。

### 7. Explore Ceiling And Critique

对通过 gate 的候选探索删除整段负担、从工具到结果代理、长期复利和 adjacent excellence 的更高版本。Deep/Exhaustive 从新用户、重度用户、流失用户、竞品用户、UX 与 engineering reality 视角批判，然后压缩为：

- Primary bet；
- Fast validation bet；
- Strategic ceiling bet；
- Do-not-do list。

### 8. Route Without Auto-Chaining

路由是建议，不是内部调用：

- 局部 module、interface、seam、adapter 或 deep-module 问题：优先建议 `codebase-design`。
- 用户价值依赖缺失 invariant、重复表示或散落状态：建议 `abstraction-architect`。
- 价值依赖遗留迁移、pilot、rollback 或 adoption economics：建议 `renewal-architect`。
- 价值上限被主流程可靠性卡住：建议 `deep-flow-sweep`，等待用户显式授权。
- `improve-codebase-architecture` 仅在用户明确想做全库架构机会扫描时建议，绝不自动启动。
- 任何 architect、sweep、Deep 或 Exhaustive 路径都只输出 one-screen handoff capsule。

## Claim Permission

以下结论必须同时获得 Project Immersion、Value Theory、Specificity Gate 和必要外部 ceiling 校准支持：

- primary bet；
- 3x+；
- switching reason；
- category-shift；
- breakthrough。

证据不足时只能标记 `hypothesis`、`validate-first`、`defer` 或 `blocked_by_evidence`。Small high-certainty improvement 不需要伪造百分比，但必须证明用户可见、证据强、风险低和投入小。

## Decision-First Output

- 主叙事默认最多 3 个主推荐或战略押注。
- 证据只在改变推荐、优先级、置信度、风险或验证路径时进入主叙事。
- 完整 Fact Map、Project Immersion 和 coverage ledger 下沉到 appendix / collapsible section。
- handoff capsule 包含 recommendation ID、Evidence IDs、confidence、next action、blocked/deferred reason、validation artifact 和 owner skill。

## Output Contract

正式分析默认产出 reviewable HTML；需要 agent 接力、源文件交付，或 HTML 无法生成时再附同名 Markdown。只有用户明确要求 `chat-only` / `no-files` 时不落盘。

报告命名：

```text
reports/user-value-architect/user_value_architect_report_{YYYYMMDD}_{HHMM}.html
reports/user-value-architect/user_value_architect_report_{YYYYMMDD}_{HHMM}.md
```

默认提供路径和可点击 `file://` URL，不主动打开浏览器。优先使用 `reviewable-html-report` capability；不可用时使用 `references/fallback.html`，保留 TOC、稳定 section IDs、Evidence appendix、Mermaid source 和非持久反馈区。

## Completion Gate

完成前确认：

- 用户、场景、目标、成功信号和 scope assumption 明确；
- Deep/Exhaustive 已完成 Fact Map 与 Project Immersion，或明确降级；
- Value Theory 能解释 project-specific leverage；
- Human Terminal Fit 已纳入价值判断：入口、默认路径、操作负担、认知负担和能力可达性没有被内部机制叙事吞掉；
- high-ceiling 与 small high-certainty 两轨均得到诚实处理；
- 每个推荐通过 User-Perceived Value Gate、Specificity Gate 和 Advice Atomicity；
- 外部期待影响 ceiling 时已校准，或明确 unavailable；
- 每个高上限候选有 floor、ceiling、path、evidence strength 和 disproof；
- 输出压缩为 primary、fast validation、strategic ceiling 和 do-not-do；
- rejected/deferred ideas 可解释；
- 未经新授权没有进入 implementation；
- 报告遵守 Main Narrative Cap、Evidence Compression 和 Delete-The-Scaffold；
- HTML 可审阅，或明确说明 fallback / Markdown 降级。
