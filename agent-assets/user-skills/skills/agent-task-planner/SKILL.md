---
name: agent-task-planner
description: >
  用户显式调用的工程需求规划入口：用于用户点名需要轻量 repo-backed 任务计划、agent-ready prompts、branch/worktree 指引、验证步骤、clean checkpoint 收口，或对不清楚需求做快速 intake 判断。适合 direct、小到中型任务、少量并发和轻量状态记录；当用户意图、问题真实性或方案可靠性还不足以负责地写计划时，先按当前 repo 和 claim 类型现场生成检查角度，核查证据、反证、可修复性、值得修复性和方案风险，必要时只问一个澄清问题并给推荐答案；当包之间依赖重、跨多波次、工作量/执行难度/运行时间高，且轻量 lane 无法保护 dependency closure、恢复和最终落地时，才升级到 agent-orchestration-planner。
  也作为 planner route gate：先判断 direct、single-agent、small-parallel、native agent controls、manual/ledger-lite pack 或 full orchestration kit 哪个机制级别适配当前任务。
---

# Agent Task Planner

## Mission

把一个具体工程请求转成低成本、可执行、可恢复的轻量任务计划。它可以由主线程、单个 agent，或少量平台原生 agents 执行；默认不生成完整 orchestration control plane。

本 skill 仅支持用户显式调用，不接受 Claude/Codex agent active 自启用。普通工程任务中如果发现需要 task planning，只能直接执行当前任务、给出轻量 handoff 建议，或等用户点名 `$agent-task-planner` 后再进入本工作流。

默认产物是轻量 task pack：

```text
docs/plans/<date>-<slug>/
|-- TASK_PLAN.md
|-- AGENT_PROMPTS.md
|-- status.tsv
`-- HANDOFF.md
```

若仓库已有 planning home，优先遵守仓库约定。没有约定时使用 `docs/plans/<date>-<slug>/`。只有用户明确需要 live task state 时，才建议使用项目工具生成 `control/tasks/<slug>/` 这类状态面。

本 skill 也是重型 planner 的前置适配层。即使用户说“多 agent”或“并行”，也先判断任务是否真的需要项目自有 scheduler；不要把普通并发、短期状态查看、少量手动包或平台原生 agents 过早升级为 `agent-orchestration-planner`。

用户显式调用本 skill 后，从本 skill 进入 planner 决策。升级到重型 planner 的原因不是“任务看起来大”，而是轻量包已经无法保证依赖正确性、长时间执行的恢复能力或最终集成判断。典型信号包括：包之间存在多波次 unlock；下游必须等待上游 commit、验证结果或生成产物；失败需要 retry / stale / invalid 诊断；多个 worktree 的合并和 cleanup 会影响完成声明；或人工推进会很容易漏掉状态转换。

如果当前环境无法使用 `agent-orchestration-planner`（例如 skill 未安装、被项目策略禁止、runner 缺失或用户不批准重型控制面），不要继续把强依赖任务拆成看似独立的小包。改用更粗的 dependency-closed package、`ledger-lite` 或 `manual-pack`，把必须一起理解、一起验证、一起落地的内容放进同一包，并记录 `upgrade-capability-missing` / `blocked-with-handoff`。包变大可以接受；目标是避免 agent 执行到一半才发现隐藏依赖、漏掉上游产物或产生不可合入的局部结果。

好计划不是因为拆得细而成立；它必须证明 package 能安全开始、值得开始、失败后知道怎么退。生成 ready package 前使用 **Plan / Package Proof Route**：claim proof、worth proof、feasibility proof、solution-fit proof、verification proof、integration proof 和 falsifier。若证明路线缺关键证据，只能生成 discovery / validation package、选择 exit path，或降级为 `reported-only` / `needs-user-decision`，不得把它包装成 ready implementation package。

同时使用非绝对的 **Plan Fitness Score** 辅助 lane 和 package 排序：startability、evidence strength、scope containment、verification strength、integration visibility、cognitive load、recovery clarity。它是决策辅助，不是总分门禁；不要为了填分数扩大 task pack，也不要让评分表淹没用户真正需要的第一个可执行动作。

## Use When

- 项目刚 clone、刚初始化，用户想马上开始工程工作。
- 请求需要先做快速 repo-backed 分析，再决定怎么实现。
- 用户请求可能还不够清楚，需要一个聚焦的 intake 问题，才能形成负责任的计划。
- 任务大概率可以由主线程、一个 agent，或 1-3 个相互独立的平台原生 agents 完成。
- branch/worktree 隔离、验证和 checkpoint 很重要，但自定义 scheduler 太重。
- 模型速度或能力有限，下一位 agent 需要短、明确、可执行的合同。

## Do Not Use When

- 用户明确要求完整 orchestration control plane。
- 任务需要 durable DAG dispatch、tail-call advancement、retry recovery、generated launchers、`99-finalize` 或自动 cleanup。
- 单个困难 bug 还没有完成根因诊断。
- 用户只想做 issue tracker 切片、PRD、或 issue triage。
- human/device/account approval 是阻塞条件，但尚未被用户批准。

## Intake Gate

写 task pack 之前，先判断请求是否 plan-ready。如果代码、文档、git state 或现有项目状态能回答缺失信息，就先查这些证据。只有产品、scope、credential、cost、policy 或 preference 决策无法被负责任地推断时，才问用户。

默认带着合理假设继续推进。只有缺失答案会改变拆包边界、验收标准、执行权限或风险等级，下一步已经被卡住，或继续做很可能浪费工作时，才提问。提问时参考 `grilling` 模式：一次只问一个问题，说明它为什么阻塞 planning，并给出你的推荐答案。不要一次问一组问题。用户回答后，要么生成 task pack，要么选择明确 exit path。

只有以下信息足够清楚时，请求才算 plan-ready：

- 期望的用户可见结果或工程结果；
- 相关 repo 区域或 discovery path；
- 会改变修复路线的 non-goals 或约束；
- verification signal；
- 本轮是现在执行、交给 agent，还是只产出 manual pack。

如果缺失信息不会改变拆解、验证或权限，说明你的假设并继续推进。如果缺失信息会改变其中之一，而且 repo evidence 也无法回答，返回 `needs-user-decision` 和第一个阻塞问题，不要发明 implementation packages。

## Claim Validation Gate

把用户提供的问题、截图、日志、验收意见、测试反馈或翻译缺失描述，默认视为未经核实的 `raw claim`，不是自动成立的 task package。不要把下面几项当作穷尽 checklist；每次都要先根据当前 claim 的类型、证据来源、涉及模块和候选方案，现场生成一组可能推翻问题或推翻方案的检查角度。

写 package 前必须完成最小核查：

- **Current evidence**：找到当前 repo、测试、日志、生成产物、截图或文档里的直接证据；如果只能引用用户转述，标为 `reported-only`。
- **Counter-evidence**：检查能推翻或降级该问题的反证，例如目标分支已有文件、生成脚本已修、配置禁用了对应路径、问题属于旧版本或重复项。
- **Fix-worthiness**：判断用户影响、修复价值、时机和替代方案；低价值、重复、证据弱或风险大时选择 `defer`、`needs-user-decision` 或 `no-fix`。
- **Feasibility**：确认 agent 能在允许路径、权限、设备、依赖和 verification 条件内修复；缺少外部门禁时用 `blocked-with-handoff`。
- **Solution fit**：如果已经有候选方案，检查它是否解决根因、是否过度扩大范围、是否隐藏产品决策、是否破坏相邻工作流、是否能被现有验证信号证明。
- **Plan / Package Proof Route**：写 ready package 前证明 claim、worth、feasibility、solution fit、verification、integration visibility 都闭合，并命名会推翻该 package readiness 的 falsifier。

生成检查角度时至少覆盖这些问题，但允许按当前任务增删：

- 这个问题是否在当前分支、当前版本、当前配置下存在？
- 证据是否可能是旧状态、误读、重复问题、测试夹具问题、环境问题、生成产物未同步，或用户期望与产品决策不一致？
- 受影响边界是否清楚，还是需要先定位模块、复现路径、数据流、平台条件或目标用户？
- 候选修复是否比问题更大，是否引入迁移、兼容性、性能、安全、隐私、发布、文案或 UX 侧影响？
- 验证是否能证明用户目标，而不只是证明某个 proxy artifact 生成成功？

只有同时满足“问题当前存在、值得修、可被本轮或明确 handoff 修复、且有可观察验收信号”时，才能进入 `Packages`。如果需要先设计方案才能判断，把方案探索列为 discovery / validation package，不要把修复包标成 `ready`。

## Workflow

1. 读取 repo instructions、当前 git state、相关项目状态、附近代码或文档。
2. 运行 intake gate：先查证据再提问；如果请求还不是 plan-ready，就问一个问题或退出。
3. 判断 lane：`direct`、`single-agent`、`small-parallel`、`native-agent-controls`、`ledger-lite`、`manual-pack`，或升级到 `agent-orchestration-planner`；如果应升级但不可用，选择 dependency-closed coarse package 或 `blocked-with-handoff`。
4. 运行 claim validation gate：现场生成检查角度，把 raw claim 和候选方案升级、降级或退出。
5. 对候选 lane 和 packages 做非绝对 Plan Fitness 评估，优先选择第一步能产生真实信号、认知负担低、恢复清楚的路线。
6. 按共享 edit boundary 和 verification boundary 拆包，不按大小平均拆。
7. 按 `references/task-plan-contract.md` 写轻量 task pack。
8. 每个 package 必须有 owner、allowed paths、forbidden paths、acceptance criteria、verification command、expected evidence、checkpoint rule、integration target、proof route 和 falsifier。
9. 如果生成翻译、导出文件、报告或其他用户要查看的 artifact，完成定义必须包括：artifact 已在目标集成分支/主工作线可见，或明确记录尚未合入的 branch、原因和下一步。
10. 如果同一会话继续实现，收口前遵守 `clean-checkpoint-first`。

如需参考 `direct`、`small-parallel`、`needs-user-decision` / `upgrade-required` 的输出形状，读取 `references/examples.md`。

## Lightweight Engineering Method

只保留能帮助较弱模型稳定执行的关键工程方法：

- **Simplicity first**：选择能满足目标的最小改动；避免 speculative features、one-use abstractions 和未被要求的 generic configurability。
- **Surgical changes**：只触碰能直接回连到用户请求的文件；发现无关清理机会时记录，不顺手塞进本轮计划。
- **Root cause before repair**：bug 或测试失败类任务，必须先有 failing path 证据，再提出实现包。
- **Raw claim before package**：用户报告先当作线索；完成 evidence、counter-evidence、fix-worthiness、feasibility 和 solution-fit 判断后，才升级为 ready package。
- **Derive checks, do not memorize them**：用户给的角度只是 seed examples；每次都从当前 repo 证据、claim 类型和候选方案里推导最可能出错的检查点。
- **Proof route before ready**：ready package 必须能说明为什么问题成立、为什么值得修、为什么 agent 能修、为什么方案贴合、如何验证、如何在目标分支可见，以及什么证据会推翻 readiness。
- **Fitness score as routing aid**：Plan Fitness 只用于选择 lane、压缩 scope 和排序 first package；它不替代 claim validation，也不强迫输出噪音评分表。
- **Test-shaped goals**：把每个 package 转成成功标准和最小有意义 verification command。
- **Isolation by risk**：窄而安全的任务可以在当前 checkout；仓库脏、改动广、多 agent 并发时建议 branch/worktree。
- **Dependency closure over small packages**：当依赖关系、共享验证或集成顺序会让小包互相卡住时，宁可做大一点的内聚包，也不要为了并行度拆出会产生隐藏依赖的假独立包。
- **Checkpoint early**：宁可留下一个披露限制的本地 checkpoint，也不要让新的 tracked dirty work 悬空；如果 agent 分支生成了用户需要的文件，checkpoint 后还必须说明如何合入目标分支并验证可见。

这些原则吸收自本项目已有 superpowers planning/debugging/worktree 方法，以及轻量 Claude-style 指导里的 think first、simplicity first、surgical changes 和 goal-driven verification。它们是护栏，不是长流程。

## Lane Rules

- `direct`：一个窄改动，验证清晰，不需要 agent handoff。
- `single-agent`：一个内聚 package，适合交给短 prompt 执行。
- `small-parallel`：2-3 个独立 packages，边界稳定，merge pressure 低。
- `manual-pack`：用户要 durable instructions，但不需要后台执行。
- `native-agent-controls`：任务可由 Claude Agent View / Dynamic Workflows、Codex App subagents 或类似平台原生能力完成；需要并发启动、状态查看或日志，但不需要项目内 scheduler truth。
- `ledger-lite`：需要 durable package docs、轻量 `status.tsv`、owner/verification/checkpoint 记录或人工推进，但不需要自动 launch、tail-call advancement、`99-finalize`、cleanup 或 runner wrapper。
- `upgrade`：需要 scheduler truth、多波次依赖、retry/finalize automation、cross-runner launch wrappers、自动收口合并或 cleanup 时，使用 `agent-orchestration-planner`。
- `upgrade-unavailable-fallback`：按 value gate 应升级，但重型 planner、runner 或授权不可用；用 dependency-closed coarse package / `ledger-lite` / `manual-pack` 保住依赖闭包，并把缺失的 control-plane capability 写入 handoff。

不要因为任务重要或项目多就升级；必须说清楚具体需要哪种 control-plane capability。

### Full Orchestration Value Gate

升级到 `agent-orchestration-planner` 前，必须能指出至少一个轻量 lane 无法满足的机制需求：

- 项目自有 DAG 或多波次依赖会影响下游 dispatch。
- `completed/finalized` 这类 scheduler truth 必须跨 session 保存并驱动 unlock。
- 需要自动 retry、stale/invalid 诊断、runner health check 或 failure fingerprint。
- 需要每包 worktree/branch 策略、integration branch 和最终自动 merge/cleanup。
- 需要 Codex/Claude script runner wrapper，并且平台原生 agent controls 不足以表达状态账本。

如果只是“多个 agent 同时做事”、只需要查看状态/日志、或只需 1-3 个独立任务，把它路由到 `native-agent-controls`、`small-parallel` 或 `ledger-lite`，并说明没有生成重型 kit 的原因。

如果 value gate 指向 full orchestration，但无法实际使用 `agent-orchestration-planner`，不要伪装成 full kit，也不要拆成会丢依赖的小包。选择 `upgrade-unavailable-fallback`：合并强依赖包、收紧 allowed paths 和 verification、标明缺少的 DAG / retry / finalize / merge control，并给出恢复到重型 planner 的最小条件。

## Exit Paths

不是每个请求都应该被强行写成实现计划。如果当前请求无法形成可信 task pack，返回一个明确 exit outcome，而不是制造假任务：

- `no-viable-plan`：当前 repo evidence 不支持任何可实现路径。
- `needs-user-decision`：产品、设计、scope、credential、cost 或 policy 决策阻塞负责任的规划。
- `blocked-with-handoff`：存在真实路径，但当前 agent 环境缺少必要 access、tool、device、network、dependency 或 permission。
- `defer`：证据弱、价值低、重复、或与当前目标时机不合。
- `upgrade-required`：任务可行，但必须使用完整 orchestration control plane。
- `upgrade-unavailable-fallback`：任务本应使用完整 orchestration control plane，但当前不可调用；只能生成依赖闭包更大的轻量/手动包，或交接缺失能力后暂停。

每个退出都必须写明：已检查证据、为什么继续做不安全或浪费、最小有用下一步、已有 artifact 或 command。

## Output Shape

写完 task pack 后，只展示：

- plan directory path；
- selected lane 和原因；
- raw claim disposition：`validated | reported-only | downgraded | deferred | rejected`；
- package list 与 dependencies；
- 第一个要运行的 command 或 prompt；
- verification、checkpoint 与 integration visibility expectation；
- 没有生成 task pack 时的 exit path；
- external gate 或 blocked decision。
- 关键 proof route / fitness 判断只展示影响 lane 或 package readiness 的结论；详细评分留在 task pack 内部，不默认展开。

除非 recovery 或 alternative lane 立刻相关，否则保持简短。

## Guardrails

- 保留 unrelated dirty work，不做 broad staging。
- 不把 human-only、device-only、credential 或 approval 工作分配给 auto-launched agent。
- 不把 product 或 user-visible decision point 藏进 implementation package。
- 不生成自定义脚本，除非 deterministic repetition 已经真实存在。
- 不把 tests、commits、APKs 或 reports 当成用户目标已经完成的证明；它们通常只是 proxy evidence。
- 不把模糊用户输入包装成假精确。先问一个阻塞问题，或选择明确 exit path。
- 不把 agent/worktree 分支上的生成文件当作已交付；除非它们已合入目标集成分支并可被用户在主工作线看到，否则只能说“已生成，待合入”。
