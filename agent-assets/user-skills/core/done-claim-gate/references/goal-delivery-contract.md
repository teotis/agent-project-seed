# Goal Delivery Contract

本参考文件用于把“目标明确但 agent 交付漂移”的任务变成可审查的交付矩阵。

## 1. Delivery Contract

先抽取以下字段。能从用户上下文可靠推断时不要打断用户；缺失字段会改变实现方向时，只问一个阻塞问题。

| field | question |
|---|---|
| `user_goal` | 用户真正要达成什么结果？ |
| `fixed_plan` | 哪个产品/设计/技术方案已经被选定？ |
| `must_preserve` | 哪些气质、行为、路径、数据、兼容性或约束不能被替代？ |
| `not_enough` | 哪些工程证据不能单独证明完成？ |
| `acceptance_evidence` | 需要什么真实产物、截图、样张、日志、测试、APK/source alignment 或用户确认？ |
| `external_gate` | 哪些验收必须由真机、账号、人工视觉判断、用户确认或发布审批完成？ |

## 2. Goal Realization Gate

这是本 skill 的核心门槛：判断目标是否真实实现，而不是判断回复措辞是否足够谨慎。

当用户质疑“目标远未达成却说完成”时，先回答四个问题：

| question | pass condition | fail signal |
|---|---|---|
| 目标是否仍是用户原目标？ | 输出直接对应用户指定的设计、效果、行为或发布结果 | 把目标降级成“有水印”“有 UI”“有测试”“有 commit” |
| 方案是否走了正确机制？ | 已定新方案触达最终运行/渲染/输出路径 | 继续在旧绘制函数、旧 fallback、旧 resolver 或弱替代路径上补装饰 |
| 证据是否来自最终产物？ | 样张、截图、录屏、真实文件、APK/source alignment、设备流程或用户确认能支撑目标 | 只拿中间对象、mock、单测、构建结果或存在性检查当证据 |
| 缺口是否改变完成等级？ | 缺口被记录并使声明降级到 `engineering-complete`、`partial`、`blocked` 或 `not-complete` | 最终表达仍让用户以为目标已经达成 |

视觉/多模态任务的额外要求：

- 必须查看或生成用户最终会看到的图像、视频、预览、最终样张或截图；
- 若无法视觉核验，标记 `visual_evidence_unavailable`，不得宣称“设计达标”；
- 若用户已经说“看起来不像设计图/不像目标效果”，优先检查实现机制是否错位，而不是继续微调旧参数；
- 如果当前技术路径表达上限不足，输出机制升级或 blocked decision，而不是把低价值修补包装成完成。

## 3. Plan-To-Implementation Map

把已定方案拆成可验证义务，而不是直接跳进现有函数补丁。

| plan item | implementation obligation | verification obligation | status |
|---|---|---|---|
| 用户可见主效果 | 必须触达最终渲染/输出/发布路径 | 最终产物可见，而不是只在预览或测试 fixture 可见 | `done/partial/not-done/blocked` |
| 新机制/新方案 | 必须经过新路径或明确升级后的路径 | 证明没有退回旧 fallback、旧 resolver、旧 renderer、旧 default | `done/partial/not-done/blocked` |
| 关键体验判断 | 必须保留用户要求的风格、语义或交互结果 | 样张、截图、录屏、真机或用户确认 | `done/partial/not-done/blocked` |
| 工程闭环 | 测试、构建、提交、APK/source alignment | 只证明工程可交付，不自动证明目标达成 | `done/partial/not-done/blocked` |

### 旧路径陷阱

遇到这些信号时，必须停下来证明方案路径正确：

- 用户说“明明已经设计了新方案，但看起来还是旧的”；
- 当前实现只改了已有 fallback、装饰函数、文案或参数；
- 预览/设置页有效，但最终产物无效或弱化；
- 测试只检查存在、尺寸、编译、节点创建，没有检查目标效果；
- agent 计划用“更深颜色、更多线条、更多断言”替代用户要求的新方案；
- 构建、APK 或 commit 已完成，但真实输出尚未核验。

## 4. Borrowing Filter

参考已有 skill 时只吸收适配本任务的局部机制。不得把下游 skill 的完整工作流、报告格式、预算档位或自动调用权限搬进本 skill。

| source skill | borrow when | borrow only | do not borrow |
|---|---|---|---|
| `user-value-architect` | 目标是否达成取决于用户可感知价值、信任、默认体验或主效果 | `User-Perceived Value Gate`：用户最终看到/感受到的结果是否支持目标；把不可见工程整洁降级为辅助证据 | 不启动 Deep Value Analysis；不重新发散高上限候选；不把已定方案改写成新产品方向 |
| `product-sense-refiner` | agent 可能把事实证据写成判断结论，或默认回复会误导用户 | `Fact / Judgment / Expression`：事实是测试/构建/截图，判断是完成等级，表达是最终回复措辞 | 不重做产品方案；不加入评分、排名或推荐框架；不把输出扩成产品设计报告 |
| `abstraction-architect` | 用户指出新方案仍像旧机制，或当前实现模型表达上限不足 | `Mechanism Ceiling Gate`：低抽象基线、旧路径反证、候选升级条件、可证伪测试 | 不生成完整架构报告；不默认寻找宏大抽象；不未经授权实施迁移或重构 |

### Adaptation Rules

- 先看触发信号，再借机制；没有触发信号时不借。
- 借来的机制必须服务于完成声明权限，而不是扩大分析范围。
- 如果借鉴会让 agent 停止交付、重新发散或隐藏当前缺口，拒绝借鉴。
- 如果当前任务已经需要完整价值分析、产品重构或结构抽象报告，只输出 handoff 建议，等待用户授权调用对应 skill。

## 5. Evidence Matrix

用证据类型匹配目标，不把低层证据抬高成高层结论。

| target type | strong evidence | weak evidence |
|---|---|---|
| 视觉/设计主效果 | 真实样张、截图、对照图、用户确认、像素/视觉回归加人工判断；并能说明用户可感知目标如何达成 | 单测绿、颜色常量变更、预览层截图 |
| 最终输出/成片 | 最终文件、真实后处理路径、artifact hash、metadata/source alignment | 中间 bitmap、mock、resolver 单测 |
| 关键交互 | 录屏、UI 自动化、真实设备流程、可复现步骤 | ViewModel 单测、截图静态存在 |
| 架构/机制切换 | 新路径被调用、旧 fallback 被绕开或删除、接口/数据流证据；旧模型表达上限已被反证或新路径必要性已证明 | 在旧函数里新增分支或注释 |
| 发布/交付包 | APK/包路径、SHA、source alignment、发布前审批状态 | 构建成功、版本号变化 |

## 6. Gap Ledger

每个关键目标项必须落入以下之一：

- `done`：实现映射和目标匹配证据都存在；
- `engineering-done`：代码、测试或构建完成，但用户可见目标仍缺真实验收；
- `partial`：只覆盖部分方案，或证据不足以支持整体目标；
- `blocked`：需要用户、设备、账号、素材、审批或外部环境；
- `not-done`：目标项尚未实现。

记录格式：

```text
目标项:
当前状态:
实现证据:
验收证据:
缺口/反证:
下一步:
```

## 7. Completion Claim Permission

最终回复只能使用与证据相称的完成等级。

| level | allowed wording | required condition |
|---|---|---|
| `complete` | “已完成/已达成” | 所有关键目标 `done`，外部验收已完成或用户明确授权无需等待 |
| `engineering-complete` | “工程侧已完成，待真实验收/用户确认” | 代码、测试、构建或包齐全，但真实目标仍需外部验收 |
| `partial` | “已完成其中 X，Y 仍未完成” | 部分关键目标缺实现或证据 |
| `blocked` | “当前被 X 阻塞，不能宣称完成” | 缺不可替代输入、设备、账号、审批或用户判断 |
| `not-complete` | “尚未完成” | 核心方案未落地、走错路径或证据反向 |

禁止口径：

- 用“测试通过”直接推出“需求完成”；
- 用“有水印/有 UI/有节点”直接推出“设计达标”；
- 用“本地 commit/API 返回成功/生成 APK”直接推出“用户目标已实现”；
- 把“后续需要用户确认”的任务写成“已经闭环”。

### Fact / Judgment / Expression Check

最终回复前做一次三层拆分：

| layer | example | rule |
|---|---|---|
| Fact | 已修改文件、测试命令、截图、样张、APK SHA、设备结果 | 只能陈述观察到的证据 |
| Judgment | `complete`、`engineering-complete`、`partial`、`blocked`、`not-complete` | 必须由 Evidence Matrix 和 Gap Ledger 推出 |
| Expression | “工程侧已完成，视觉仍待真机确认” | 必须让用户不会误解为目标已完全达成 |

如果表达比判断更乐观，降级表达；如果判断比事实更乐观，降级判断。

## 8. Final Response Template

```markdown
交付状态: engineering-complete

用户目标: ...
已定方案: ...
实现映射: ...
目标实现门: ...
验收证据: ...
仍有缺口: ...
完成声明权限: 只能说工程侧完成；不能说视觉/真机/发布已完成。
下一步: ...
```

如果验证失败或无法运行，优先继续修复；无法继续时明确失败命令、最高信号错误和当前完成等级。
