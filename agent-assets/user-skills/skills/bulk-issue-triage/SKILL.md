---
name: bulk-issue-triage
description: >
  用于一次收到大量来自真机测试、用户反馈、验收清单、截图、录屏或日志的问题，需要在实施前做证据化初步核查，补全问题表现，并按领域、共享根因、依赖和修复复杂度整理为问题包时。
  Use when a heterogeneous issue batch must become reviewable upstream input for agent-orchestration-planner; not for single-bug deep diagnosis, direct repair, or orchestration control-plane generation.
---

# Bulk Issue Triage

## Mission

把大量问题转成可细化的问题包。保留编号，区分事实、判断与未知项，为 `agent-orchestration-planner` 提供输入。

只做初查和分包；不设计完整修复方案，不生成 DAG、worktree、ledger 或执行脚本，不修改产品代码。

## Invocation Contract

- 一次收到多个真机问题、用户反馈、截图、录屏、日志或验收项；
- 用户要求补充问题表现、初步分析并按领域或复杂度分包；
- 多个问题可能来自同一状态机、布局、媒体管线或能力声明；
- 结果将交给后续 agent 设计修复路径。

- 单个高难 bug 的深度根因诊断：使用 `diagnosing-bugs`；
- 代码复杂度的全库扫雷：使用 `complexity-sweep`；
- 已经具备明确任务包，准备生成多 agent 执行控制面：使用 `agent-orchestration-planner`；
- 用户明确要求立即修复：先完成必要核查，再切换到实现流程。

其他 agent 可建议使用，但不得未授权自动串联。

触发评测见 `evals/evals.json`。

## Evidence Rules

- 先读取目标仓库指导、Git 状态、相关代码、测试和验证脚本；保留无关脏改动。
- 图片、视频、日志和描述都是证据输入，但不能自动证明根因。
- 判断标记为 `已确认`、`高可能`、`待核查` 或 `信息不足`。
- 明确区分：
  - **观察事实**：用户可见行为或当前代码可直接证明的事实；
  - **初步判断**：基于证据的根因候选；
  - **未知项**：需要日志、设备、代码路径或复现补充的内容。
- 不把旧报告、注释或历史任务包当成当前实现真相。
- 不为整齐而强行合包。

## Workflow

### 1. Normalize The Intake

为每个原始问题建立稳定 ID。已有编号时保留，例如 `ISSUE-001` 对应原问题 1；没有编号时顺序生成。

每项至少提取：

- 原始描述；
- 补全后的问题表现；
- 期望行为；
- 触发条件、模式、设备或状态；
- 已有证据；
- 缺失证据；
- 初步领域标签。

保留用户原意；措辞不清时保留原文并另写规范化描述。

### 2. Establish Current Truth

在仓库可用时，核查：

- 相关模块与所有权边界；
- 当前 UI、状态机、能力声明或媒体处理路径；
- 邻近测试与验证脚本；
- 已知降级、占位实现或未接线能力；
- 可能影响多个问题的共享组件。

核查到足以合理分包为止；完整修复设计留给下游 planner。

### 3. Build A Shared-Root Map

先形成候选关联。优先考虑：

- 同一状态机或生命周期；
- 同一布局约束、预览几何或 overlay 层；
- 同一相机能力、变焦映射或设备适配；
- 同一设置数据源、快捷入口或信息架构；
- 同一媒体捕获、后处理、保存或相册语义；

只有确有不同所有权边界时才跨包，并明确主包与关联包；否则每个问题只归属一个包。

### 4. Estimate Complexity

使用相对复杂度，不伪装成精确工时：

| 级别 | 判断 |
|---|---|
| `S` | 单层局部行为或文案/UI 调整，边界清晰，验证简单 |
| `M` | 跨少量组件或状态，需补测试或设备验证 |
| `L` | 跨 UI、session、device、media 等多层，存在兼容与回归风险 |
| `XL` | 需要重新定义能力、数据模型、媒体格式或长期迁移路径 |

同时给出初查置信度：`高`、`中`、`低`。复杂度不等于优先级。

### 5. Form Problem Packages

按“共享根因候选 + 领域所有权 + 共同修复路径”分包，不按编号机械分组。

输出前读取 `references/problem-package-contract.md`。每包必须包含：

- 包 ID、标题与原始问题 ID；
- 问题表现与用户影响；
- 领域、复杂度、置信度和当前判断；
- 初步证据与分析；
- 共享根因候选及反证；
- 范围、依赖和明确排除项；
- 待补证据；
- 下游细化重点。

### 6. Check Coverage

所有原始问题必须：

- 恰好归入一个主包，或明确说明跨包主次；
- 在“问题表现”中保留用户可观察行为；
- 在“证据与未知”中说明当前核查边界；

生成文件后运行：

```bash
python3 <skill-dir>/scripts/validate_triage_report.py <report.md> \
  --issue-ids ISSUE-001,ISSUE-002
```

校验器只检查结构和覆盖。

### 7. Hand Off

文档末尾必须附上推荐使用方法：

> 在新 agent 窗口输入：  
> `/agent-orchestration-planner 针对如下外部 agent 已经初步分析的问题集合，进行核查确认，设计细化修复方案，制作好任务包。`  
> 然后粘贴一个完整问题包。

下游必须重新核查事实，不能继承初步根因判断。

## Output Contract

默认输出中文 Markdown。优先使用仓库已有规划目录；没有约定时使用：

```text
docs/plans/bulk-issue-triage-{YYYYMMDD}.md
```

用户明确要求 chat-only 时不写文件。结构以 `references/problem-package-contract.md` 为准。

## Completion Gate

完成前确认：

- 所有原始问题 ID 均被覆盖；
- 每个问题都有补全后的问题表现与期望行为；
- 事实、判断和未知项已分离；
- 分包依据是共享修复路径，不只是相邻编号或相似文案；
- 每个包都有领域、复杂度、置信度、依赖和排除项；
- 没有把初步分析写成已确认根因；
- 推荐的 `agent-orchestration-planner` 使用方法已附上；
- 未修改产品代码、Git 历史或无关用户改动；
- 无法核查的内容已明确标为待补证据。
