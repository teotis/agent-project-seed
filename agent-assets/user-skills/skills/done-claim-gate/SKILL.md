---
name: done-claim-gate
description: >
  用于存在非例行需求落地风险（delivery-risk moment）的场景：用户给出需要 agent 补全判断的宽泛目标，或明确但跨路径/高依赖的复杂落地（迁移、UI 行为、导出契约等）；或存在旧路径/fallback/模板替代新方案、近期同类不满纠偏、完成声明证据可能只覆盖工程 proxy 的风险。明确机械小改（精确改名、补配置、修 typo）不触发；明确但复杂的落地仍触发。
  两个模式：pre-delivery lens（风险交付前清零 + 五维 + 根因分类轻量自检）与 completion claim gate（高风险完成声明前 Delivery Contract + Gap Ledger + 完成等级强验收）。
  自动触发应保持精准：例行模板运行、明确机械小改、低影响文案、状态汇报、普通 final 摘要、内部维护且不改变外部契约时不触发，除非用户显式点名。
  强制把用户目标、落地解释空间、真实实现路径、验收证据和完成声明权限绑定起来，防止把局部实现、测试通过、构建/提交收口误当成用户目标达成。
---

# Done Claim Gate

## Mission

防止 agent 在「需求需要真实落地但解释空间较大」的情况下，把工程活动误报为用户目标达成；并在高风险交付当下，从用户视角轻量自检是否瞄准了正确角度。

这个 skill 不是完成口径润色器。它不负责重新设计产品方案；它负责确认已定方案是否真的落到正确路径、真实产物是否满足目标，以及最终回复是否有资格说「完成」。

## Two Modes

本 skill 有两个模式，按时机选择：

### pre-delivery lens（交付前轻量自检）

- **时机**：即将交付高风险用户/下游依赖产物，但还未声称完成；且任务不是例行模板运行或明确机械小改。
- **动作**：清零（放下「已做完」心态）→ 五维自检 → 偏差根因定位。
- **轻量含义**：少做 Delivery Contract / Gap Ledger 矩阵，**不是允许放行偏差**。发现偏差时，不得照常声称完成，必须降级到 completion claim gate 或先修正。
- **触发词**：「用户视角」「用户角度」「这样对吗」「用户会怎么用」「交付前检查」。

### completion claim gate（完成声明强验收）

- **时机**：准备对高风险落地任务说「完成 / 达标 / 已解决」，或用户质疑「目标远未达成却说完成」。
- **动作**：Delivery Contract → Plan-To-Implementation Map → Goal Realization Gate → Gap Ledger → Completion Claim Permission。
- **触发词**：「别只说测试通过」「是否完成」「为什么还是旧机制」「没有达到要求」。

### 模式选择

- **用户显式调用**：按触发词选模式，跑对应完整流程。
- **Agent active 自启用**：
  - 「高风险任务」= `prior-correction-risk` 或 `path-substitution-risk` 任一成立，或 baseline risk 三项全成立。
  - 默认跑 `pre-delivery lens`（1 轮轻量自检）。
  - 只有「高风险任务 **且** 即将使用 complete/达标/已解决 口径」时，允许 agent active 直接进入 `completion claim gate`，不必先跑 PDL 再升级。
  - 非高风险任务即便准备说完成，agent active 也只跑 PDL；发现偏差影响完成声明时再升级到 CCG。
- pre-delivery lens 发现偏差且偏差影响完成声明 → 升级到 completion claim gate。
- 只是例行操作、明确机械修改、状态汇报或普通 final 摘要 → 不自动触发；用户显式点名时再触发。

## When To Use

自动使用本 skill 只在出现 **非例行需求落地风险** 时。触发判定式（详见 `references/goal-delivery-contract.md` 0.0 节 Trigger Calculus）：

```
auto-trigger = explicit_user_invocation
             OR prior-correction-risk
             OR path-substitution-risk
             OR (non-routine_landing
                 AND interpretation-or-complexity
                 AND user-or-downstream_dependency)
```

前三项是 override risk（单独成立即触发）；最后一项是 baseline risk（三项 AND）。要点：

- `interpretation-or-complexity` 涵盖「宽泛方向需补判断」**和**「明确方案但跨路径/高依赖」两种（旧路径吞没风险归 `path-substitution-risk`）；
- 明确机械小改（精确改名、补配置、修 typo）不触发；明确但复杂的落地仍触发；
- 宽泛但低影响的小文案润色不触发。

以下信号对应公式中的 override term 或 baseline 输入，或指示应进入 completion claim gate：

- 用户指出「方案已经设计过」「为什么还是旧机制」「没有达到要求」「别只说测试通过」；
- 存在旧 fallback、旧渲染器、旧模板、旧数据流、旧报告骨架或外部改动覆盖新方案的风险；
- 任务有高用户可感知风险：视觉主效果、关键交互、公开/下游接口、导出格式、发布包、真实设备/真实输出、跨模块方案迁移；
- agent 准备对上述高风险任务声明完成，但证据可能只覆盖代码、测试、构建或提交；
- 之前同类任务出现过「局部补丁完成，用户目标没完成」或「功能完成但用户不满」的失败。

不用于：

- 从零产品探索或多方案发散：使用 `user-value-architect`、`product-sense-refiner` 或 `prototype`；
- 尚未定位根因的单点故障：使用 `diagnosing-bugs`；
- 多问题输入的分包和路由：使用 `package-issue`；
- 仅做提交、合入、脏工作区收口：使用 `clean-checkpoint-first`；
- 例行模板/固定流程运行，例如稳定报告模板换数据、固定导出流程、常规同步或状态查询；
- 用户给出明确机械小改且实现路径单一，例如精确改名、补一行配置、修 typo、按指定文本替换；
- 低影响文案润色、普通 final 摘要、命令输出转述；
- 内部维护或重构不改变用户/下游可见契约；
- 用户明确要求快速执行且不需要交付验收判断（全局不触发，无论判定式结果如何）。

## Hard Invariants

- 用户目标是主证据源。不得把「测试绿了」「构建成功」「生成 APK」「有 commit」替代为需求达成。
- 已定方案必须映射到真实实现路径。不得在旧 fallback、旧渲染器、旧状态机或弱替代路径上补装饰后宣称采用了新方案。
- 验收证据必须匹配目标类型。视觉目标需要真实图片/截图/样张或用户确认；发布目标需要 artifact identity；行为目标需要可复现流程；测试只能作为工程支撑证据。
- 完成声明有权限等级。关键验收未通过时，只能说「工程侧完成」「待验收」「部分完成」或「仍有缺口」，不能说「完成/达标/已解决」。
- **轻量不等于可忽略**。pre-delivery lens 只是少做矩阵，不是允许放行偏差。发现偏差时不得照常声称完成，必须降级表达或先修正。
- **人类终端适配性也是验收面**。若产物让用户必须记隐藏规则、走非直观入口、执行大量手工步骤、反复重建上下文或自行恢复失败，不能只因工程路径完成就声称用户目标完整达成。
- 如果发现方案无法由当前实现模型达成，先说明上限和缺口，再切换方案、升级架构路径或询问用户，不继续低价值修补。
- 目标实现门优先于回复措辞。用户已经质疑「目标远未达成却说完成」时，必须回到已定目标、真实产物和实现机制，而不是只承诺以后改说法。

## Core Workflow

### pre-delivery lens 流程

1. **清零**：放下「我已做完 / 规格已满足 / 测试已绿」心态；产出一句零基锚点「用户拿到这个产物，能达成什么真实目标」。
2. **五维自检**：目标触达 / 用户操作视角 / 决策可用性 / 真实场景深度 / 路径真实性。每维给出明确判断，不得跳过；用户操作视角必须检查入口、默认路径、操作数、判断数、上下文重建和恢复成本。
3. **偏差根因定位**：发现偏差时，标记维度 + 根因类型（`context-contamination` / `flow-misfit` / `legacy-rule-drift`），反馈用户并建议修正。
4. **偏差处置**：按 `references/goal-delivery-contract.md` 的 `must-upgrade / repair-before-final / safe-to-summarize` 判定偏差是否影响完成声明；影响时升级到 completion claim gate，不影响时输出偏差摘要并修正后交付。

详细自动触发门槛、五维判断标准、证据反模式和根因类型见 `references/goal-delivery-contract.md` 的 Pre-Delivery Lens 章节。

### completion claim gate 流程

1. 建立 `Delivery Contract`：提取用户目标、已定方案、不可替代要求、排除项、成功证据和外部验收门槛。
2. 运行 `Borrowing Filter`：只按触发信号吸收 `user-value-architect`、`product-sense-refiner`、`abstraction-architect` 的局部机制，不自动串联重流程。
3. 做 `Plan-To-Implementation Map`：列出方案必须触达的代码路径、数据路径、UI/产物路径和验证路径，显式标记旧路径陷阱。
4. 运行 `Goal Realization Gate`：证明当前实现满足目标本身，而不是只满足「有输出、测试绿、可构建、已提交」等代理指标；视觉/多模态目标必须对最终样张、截图、录屏或用户确认负责。
5. 执行实现时维护 `Gap Ledger`：每个目标项标记 `done`、`partial`、`not-done`、`blocked`，并附当前证据。
6. 验证真实产物：优先检查用户会看到的最终形态；只有当证据能支持目标时，才把测试、构建、提交作为辅助。
7. 运行完成声明门槛：根据 `references/goal-delivery-contract.md` 判定可说 `complete`、`engineering-complete`、`partial`、`blocked` 或 `not-complete`。
8. 若还需要提交或收口，再使用 `clean-checkpoint-first`；提交不能反过来提高完成等级。

## Output Contract

### pre-delivery lens 输出

```text
用户视角自检: pass | 偏差
用户目标: <零基锚点>
目标触达: <触达 / 表面规格 / 未触达>
用户操作视角: <无明显问题 / 具体问题>
操作负担: <入口 / 默认路径 / 操作数 / 判断数 / 上下文重建 / 恢复成本>
决策可用性: <清晰 / 模糊点>
真实场景深度: <真实 / 套话>
路径真实性: <真实路径 / 旧路径陷阱>
偏差: <无 / 偏差维度 + 根因类型>
升级判定: must-upgrade | repair-before-final | safe-to-summarize
建议修正: <具体修正>
```

偏差时可附根因记录到 memory（若 `engineering-memory` 可用）供跨会话 pattern 识别。无偏差时输出 pass 即可，不强制造问题。

### completion claim gate 输出

```text
交付状态: complete | engineering-complete | partial | blocked | not-complete
用户目标:
已定方案:
实现映射:
目标实现门:
验收证据:
仍有缺口:
完成声明权限:
Borrowing Absorption Check: <未借鉴 / 借鉴机制及其落入的输出字段>
下一步:
```

长任务可把完整矩阵写入项目文档，但最终回复仍必须明确完成等级、关键证据和不能宣称完成的原因。

## Invocation And Depth

本 skill 支持用户显式调用与 agent active 自启用：

- **用户显式调用**：按触发词选模式，跑对应完整流程。
- **Agent active 自启用**：仅在非例行需求落地风险成立时触发（Trigger Calculus 见 `references/goal-delivery-contract.md` 0.0 节，模式选择见上文）。默认跑 `pre-delivery lens`（1 轮轻量自检）；只有「高风险任务且即将使用 complete/达标/已解决 口径」时允许直接进入 `completion claim gate`，否则偏差影响完成声明时再升级。不自动串联 user-value-architect 等重型 skill。
- **Cross-heavy route**：已有重型 workflow 正在运行时，不自动启动本 skill，只提 handoff。

偏差累积成跨会话 pattern 时，建议用户显式调用 `user-value-architect`（重型价值分析），不自行升级。

## Resource Map

- `references/goal-delivery-contract.md`：交付契约、旧路径陷阱、证据矩阵、完成声明规则；含 Pre-Delivery Lens 章节（五维自检 + 根因分类 + 证据反模式）。
- `references/failure-lessons.md`：从近期水印/设计落地失败中提炼的可复用教训。
- `evals/evals.json`：触发与输出 smoke cases。

## Completion Gate

在最终回复前确认：

- 用户目标和已定方案没有被工程 proxy 替换；
- 每个关键目标都有实现映射和证据状态（completion claim gate）或五维已全部执行（pre-delivery lens）；
- pre-delivery lens 发现偏差时已给出升级判定，且 `must-upgrade` 没有被降级成普通摘要；
- 旧路径陷阱已检查，未把弱替代路径当作方案落地；
- 目标实现门已检查，未把「改了说法」「多写检查清单」「测试通过」当作真实交付；
- 完成等级与证据一致；
- 未把需要用户、真机、视觉或发布确认的事项写成已完成；
- pre-delivery lens 发现偏差时未照常声称完成。
- 实际借鉴其他 skill 局部机制时，已通过 Borrowing Absorption Check 证明它进入交付门或完成等级判断。
