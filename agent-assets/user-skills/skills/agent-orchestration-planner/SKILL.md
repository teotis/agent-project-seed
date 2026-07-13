---
name: agent-orchestration-planner
description: >
  用于用户明确要求的中大型多 agent 工程落地，且需要项目内持久 DAG、任务尾部推进、worktree/分支管理、状态账本、重试恢复、Codex/Claude runner 选择或自动收口合并。
  即使输入来自用户、sweep、handoff 或轻量 planner，也要独立完成 raw claim 准确性、反证、值得执行、可行性和方案贴合判断，避免把未经证实的问题包装成 DAG。
  Use for explicit multi-agent execution that needs a project-owned DAG, durable coordinator state, branch/worktree control, Codex/Claude runner selection, recovery, and finalize workflows.
whenToUse: >
  仅当用户明确要求 orchestration control plane、状态账本、DAG 调度、worktree/分支管理、失败恢复、自动收口，或要求把多 agent 结果可靠落地到同一工程时使用。
  不要仅因用户提到 Claude Agents View、claude agents、claude --bg、Codex subagents 或普通独立并发任务而触发；这些优先使用对应平台原生能力。
disableModelInvocation: true
---

# Agent Orchestration Planner

## 使命

当用户明确要求中大型 multi-agent execution 时，把需求整理成完整 orchestration kit。kit 有两条入口：

- **Manual**：用户从 Markdown 复制 package prompts 到任意 agent 平台。
- **Script**：用户运行平台专用 launcher：`bash launchers/start-codex-app.sh` 或 `bash launchers/start-claude-code.sh`；两者都调用同一个 `orchestrate.sh` 状态机。

本 skill 不替代 Claude Code 或 Codex 的官方并发控制面。独立任务只需要启动、查看状态、读取日志或停止时，优先使用原生能力：Claude Code 用 Agent View（`claude agents`、`claude --bg`、`claude agents --json`）或 Dynamic Workflows；Codex App/CLI 用显式 subagent workflow（例如让 Codex spawn agents、等待并汇总）或 `/agent` 检查 agent threads。只有当项目需要可版本化的 DAG、持久状态账本、分支/worktree 策略、失败恢复和最终落地判断时，才生成 orchestration kit。

脚本不是 long-running watcher，而是 `start/advance/status/retry/finalize` 入口。第一次 `start` 只启动第一批 ready packages。每个 package prompt 末尾调用：

```bash
orchestrate.sh advance --from <package-id>
```

只有 `advance` 能决定是否启动 downstream packages 或 `99-finalize`。
tail call 返回后，package/finalize session 必须立即终止，不得继续输出总结、提问、生成 suggested reply 或停在交互式 prompt；blocker 与 recovery 信息只写入 coordinator artifacts。

生成模板通过 `ORCHESTRATION_RUNNER` 支持 runner variation。Runner 选择是用户/宿主平台意图的一部分，不是由 PATH 上碰巧存在的 CLI 决定：

- `codex`：当用户要求 Codex App、Codex runner、当前 Codex 工作流，或当前宿主明确是 Codex App 且用户未指定 Claude 时，把 `launchers/start-codex-app.sh` 作为主脚本路径。该 wrapper 显式设置 `ORCHESTRATION_RUNNER=codex`，先运行 `doctor --environment`，再从 package worktrees 启动本地 `codex exec --json` 后台进程；可用时记录 `codex-thread:<thread-id>`；证据来自 package JSONL logs、`status/state.tsv` 和 `status/events.jsonl`。这是项目自有 runtime 的 Codex CLI lane，不是 Codex App 原生 subagent UI 的复制品。
- `claude`：当用户要求 Claude Code、Agents View、`claude --bg`，或宿主是 Claude Code 时，把 `launchers/start-claude-code.sh` 作为主脚本路径。该 wrapper 显式设置 `ORCHESTRATION_RUNNER=claude`，由脚本用 `claude --bg --name` 启动 Claude Code background sessions，并附 `claude agents --cwd <repo-root>` 查看命令。裸 `bash .../orchestrate.sh start` 仍保留为无环境变量兼容入口，但不再作为用户首选启动脚本展示。
- Manual / App-native：用户只想留在 Codex App 内并使用原生 subagents 时，不要承诺脚本自动创建 App UI 里的子线程；把 `launchers/agent-prompts.md` 作为 prompt source，让当前 Codex App thread 按 ready package 显式 spawn subagents，或降级为 manual copy。需要项目内状态账本和自动 tail flow 时，使用 `ORCHESTRATION_RUNNER=codex` 脚本路径。

两个 launcher 都必须随 kit 生成，所以一个应用出方案后，用户可以在另一个应用中直接运行对应 wrapper：Codex App 运行 `start-codex-app.sh`，Claude Code 运行 `start-claude-code.sh`。Codex 启动前必须用 `doctor --environment` 确认当前 Codex CLI 参数兼容、`CODEX_HOME`/`~/.codex` 可写；如果出现 state DB 只读、PATH 更新权限失败或 app-server 初始化失败，先修运行环境，不要把包标成实现失败。

## 适用边界

只有用户明确请求本 skill 或清楚要求 medium/large orchestration 时使用，例如：

- `agent-orchestration-planner`
- `orchestration skill`
- 多 agent 工程落地 / 自动派工并最终集成
- 状态账本 / DAG 调度 / worktree 管理 / 分支管理 / 自动收口
- 跨 session 恢复、package retry、证据收集、保守 merge/finalize

不要因为任务复杂、数量多，或用户只提到 Agent View / `claude --bg` 就自动触发。如果任务相互独立且官方 session/workflow 状态足够，直接使用 Agent View 或 Dynamic Workflows。少量手动执行事项使用 `docs/contracts/task-package-contract.md` 形成轻量 package，不再路由到已退役的 handoff skill。

## 核心契约

Orchestration kit 是 **tail-driven execution contract**。package agents 做自己的工作，更新 coordinator status，然后调用同一个 advancement command。它们不实现 scheduling logic，也不自行决定启动下游包。

上下文按角色和状态渐进加载：

- Functional package executor 默认只读取自己的 package doc、assigned status、graph/state 对应行和相关代码；只有发生 retry、policy conflict、fallback 判断或 capability uncertainty 时，才加载完整 INDEX、events 或 failure recovery 细节。
- Functional package prompt 不复制全局 merge、fallback selection、cleanup 或 task-level outcome 逻辑；这些由 `99-finalize` 和 INDEX 承担。
- Background executor 默认静默执行，不输出进度叙述、任务复述或中间总结；过程事实写入工具结果，最终证据一次性写入 coordinator artifacts。
- Runtime 继续保留完整命令与恢复能力；用户聊天只暴露当前可执行的最小命令面。
- Analysis-only 和 planning-only packages 产出的长期报告、计划、任务包、HTML review surface、`FINAL_REPORT.md` 与 coordinator summary 默认视为可合入主开发线的文档资产。`99-finalize` 应在基础自检、敏感内容排查、路径归类和冲突检查通过后，把它们合入 mainline 并在主/coordinator thread 汇总；不得把它们长期留在 package branch、watch/session 或 worker thread，除非 INDEX 明确声明隔离原因。
- 对用户可见行为、布局、文案、工作流或视觉输出，package 使用 **User-Visible Delta Ledger**：允许必要的小邻近调整，但必须记录目标外可见变化，并把主流程、第一屏构图、导航模型、发布承诺或 explicit non-goal 的变化归为 `decision-required`，交给用户决策、拆包、降级或已批准 fallback，而不是伪装成普通 bugfix。

上游 sweep、handoff 或用户方案提供结构化包时，先按 `docs/contracts/task-package-contract.md` 的 **Task Package Contract** 归一化，再生成 graph、package docs 和 prompts。每个 functional package 必须保留 **Falsification Ledger** 和 **Outcome Replay**：前者防止把弱证据、风格偏好或过期历史包装成执行项；后者记录 landed/blocked/false-positive/capability-gap 等结果，供后续 eval 和技能规则回放。

即使上游已经做过 task planning，本 skill 也必须独立执行一次 orchestration 级别的 claim validation。重型控制面会放大错误问题的成本：一个未经证实的 raw claim 进入 DAG 后，可能错误解锁下游、制造无意义 worktree、或让 finalize 合并局部伪成果。不要把 `agent-task-planner` 的判断当成不可复核的事实；它可以作为 seed evidence，但 orchestration planner 必须能自己说明哪些 claim 被验证、降级、拒绝或只允许进入 discovery package。

## Model Adaptation Boundaries

把本 skill 的规则按刚性分层使用：

- **Hard invariants**：tail-driven advancement、script-owned state mutation、projection consistency、`state.tsv`/`events.jsonl` 权威边界、no launched unlock、capability preflight、external-assist gate、cleanup evidence 和 tail-call termination。这些是多 agent 落地安全边界，不能因为模型更强或平台更方便而绕过。
- **Adaptive heuristics**：是否生成完整 kit、如何拆包、runner choice、manual vs script entry、用户可见命令面、reference 加载和 recovery 展示都是可适配策略。更强模型或平台原生能力足够时，应优先选择更轻的官方 Agent View、Dynamic Workflows、Task Package Contract 或直接执行，而不是为了使用本 skill 生成重型控制面。
- **Creative extension lane**：当模型发现新的 runner、状态投影、验证通道或 package topology 更适合任务时，可以提出扩展，但必须通过 projection ownership、state lifecycle、verification ability、failure recovery 和 backward-compatible runtime checks；扩展不能把叙事证据塞进 scheduler truth，也不能削弱 finalize/cleanup gate。

生成 kit 前做一次 **orchestration value test**：项目是否真的需要版本化 DAG、持久状态账本、worktree/branch 策略、失败恢复和最终集成判断。若只需要并发执行、状态查看或少量独立任务，降级到官方平台能力、轻量 task package 或直接执行。

如果用户诉求落在中间态，例如需要可审计任务包、owner、verification、checkpoint 和轻量状态记录，但不需要自动 launch、tail-call advancement、`99-finalize`、runner wrapper、自动 merge 或 cleanup，则不要生成完整 orchestration kit。改用 `agent-task-planner` 的 `ledger-lite` / `manual-pack` lane，或把已有 Task Package Contract 保持为手动执行包。

Full kit 只有在至少一个轻量 lane 无法满足时才成立：项目自有 DAG 会驱动 dispatch、scheduler truth 要跨 session 解锁 downstream、失败恢复需要 retry/doctor/fingerprint、或最终集成需要 per-package worktree、integration branch、自动 finalize/cleanup。若理由只是“多 agent”“任务很多”“想看进度”，优先原生平台并发或轻量任务包。

生成 full kit 前必须给出 **Execution Contract Proof Route**：need proof、projection proof、unlock proof、capability proof、landing proof、cleanup proof 和 falsifier。若证明路线无法闭合，不得生成完整 orchestration kit；应降级到 `agent-task-planner` 的 `ledger-lite` / `manual-pack`、平台原生 agents，或先问一个阻塞决策。

在 Execution Contract Proof Route 前先完成 **Claim Readiness Proof**：claim proof、counter-evidence、fix-worthiness、feasibility、solution-fit、verification signal、integration visibility 和 falsifier。它回答“这些包是否应该进入 DAG”；Execution Contract Proof Route 回答“这些包是否需要 full kit”。两者都必须闭合，才允许生成完整 orchestration kit。

同时用非绝对的 **Orchestration Value Score** 支撑 orchestration value test：durable state need、dependency unlock value、recovery value、integration value、runner value、operator burden。它帮助判断 full kit 是否比原生平台/轻量包更有用户价值，但不替代 hard invariants，也不能为了分数制造重型控制面。

如果输入或生成的 package docs 包含 YAML/JSON/fenced structured package block，运行：

```bash
rtk python3 scripts/task_package_validator.py <package-or-index-file>
```

该 validator 是本仓库 `scripts/` 下的 repo-local deterministic gate，不是 standalone skill 包的硬依赖。若单独复制本 skill 或当前环境没有该脚本，仍保留 Task Package Contract 字段、Falsification Ledger 和 Outcome Replay，但必须把 deterministic package validation 标为 `missing evidence` / package contract gap；在 delegated execution 或 graph generation 前做人工结构审查，不得把“脚本不可用”当作验证通过。

把一次 orchestration 看成一个 execution contract 的多个 projections：

- `INDEX.md`：静态 human intent、authorization、policy、landing strategy、capability gates。
- `launchers/package-graph.tsv`：机器可读 package topology。
- `status/state.tsv`：当前 scheduler snapshot，只能通过 `orchestrate.sh mark-state` 修改。
- `status/events.jsonl`：append-only audit history、retry accounting、failure fingerprints。
- `status/<package-id>.md`：人类可读的 package evidence 和 blocker diagnosis。
- `launchers/agent-prompts.md`：local package execution contracts 和 tail-call instructions。
- `packages/99-finalize.md` 与 `FINAL_REPORT.md`：global verification、merge judgment、task outcome、final narrative。
- `scratch/`：临时、gitignored、非权威 exchange material。

这些 projections 冲突时，必须报告 orchestration invalid 或 blocked，直到修复。不要根据最乐观的 artifact 推断成功。

## Reference Map

保持本 `SKILL.md` 作为 operating kernel。只有需要细节时才加载 references：

- 拆包、projection ownership、capability gates、landing/fallback behavior：读 `references/planning_contract.md`。
- 生成或修改 `package-graph.tsv`、`state.tsv`、`orchestrate.sh`、runner behavior、dependency unlock rules：读 `references/runtime_contract.md`。
- 处理 `blocked`、`stale`、`invalid`、retry、doctor、logs、scratch、non-landable plans：读 `references/failure_recovery.md`。
- 生成 `INDEX.md`、package prompts、`99-finalize`、最终用户命令摘要：读 `references/artifact_templates.md`。

`scripts/orchestrate-template.sh` 是已测试 runtime body。生成 kit 时复制为 `launchers/orchestrate.sh`；同时复制 `scripts/start-codex-app-template.sh` 为 `launchers/start-codex-app.sh`，复制 `scripts/start-claude-code-template.sh` 为 `launchers/start-claude-code.sh`。三个脚本都要运行 `bash -n`，再运行生成脚本的 `status` 做静态 preflight；不要凭记忆或 prose 重新写脚本。

`agent-prompts.md` 的 package 标题是 runtime parser key，不是展示性标题。每个 graph package 必须恰好有一个以下格式的二级标题，package id 必须与 `package-graph.tsv` 完全一致：

```markdown
## Package: <package-id> - <title>
```

不要简写为 `## <package-id>`。生成后必须通过 `bash launchers/orchestrate.sh status`，确认 prompt、graph、state 和 status projections 一致，再向用户提供 `start` 命令。

## 状态语义

允许的 package states：

```text
pending
ready
manual_required
launched
in_progress
completed
blocked
stale
invalid
finalizing
finalized
```

不要增加 runner-specific state columns。Claude、Codex、manual execution、CI runners 和其他平台都应建模为同一 lifecycle 下的 launch mechanism、permission mode、evidence channel、verification ability 差异。

Codex/runtime observations 映射如下：

- `pending_init` 或 `running`：仍是 active work，保持 `launched` / `in_progress`。
- `interrupted`：通常是可重试 `stale`，除非证据表明 deliberate blocker。
- `completed`：只有记录 evidence 并调用 `mark-state completed` 后，package 才可为 `completed`。
- `errored`：带 recovery context 的 `blocked` 或 `invalid`。
- `not_found`：缺少 launch identity 时为 `invalid`；丢失 active sessions 时为 `stale`。
- `shutdown`：只是 resource lifecycle，不代表成功。

`launched`、`in_progress`、`finalizing` 绝不能解锁 downstream packages、启动 `99-finalize` 或满足 acceptance criteria。Dependency checks 只能从 `completed` 或 `finalized` 解锁。

## 工作流

### 1. 检查或创建包材料

生成 artifacts 前：

- 读取用户请求和已有 plan/package docs。
- 搜索项目文档指定的 planning home，例如 `docs/plans/`、`codex/agent_plans/`，或 AGENTS/CLAUDE/project docs 命名的路径。
- 检查足够本地上下文，把工作拆成具体 packages。
- 检查当前 git status。
- 把用户、sweep、handoff、测试反馈、截图、日志或已有 package docs 中的问题描述先视为 `raw claim`；根据当前 repo、证据来源、影响面和候选方案，现场生成会推翻 claim 或推翻方案的检查角度。
- 独立完成 claim validation：检查当前证据、反证、值得执行、agent 可行性、方案贴合、验证信号和集成可见性；如果只能引用上游转述，标记 `reported-only`，不得把实现包标成 ready。
- 对未被验证但可能有价值的问题，只生成 discovery / validation package；对被反证、低价值、不可行或缺少外部门禁的问题，降级为 rejected / deferred / blocked，而不是放进 functional DAG。
- 确保每个 functional package 都有 package id、allowed/forbidden paths、dependencies、acceptance criteria、verification commands、expected evidence、branch/worktree policy、unlock conditions。
- 确保每个 imported package 保留 **Task Package Contract** 字段、**Falsification Ledger** 和 **Outcome Replay** stub；缺字段时先修 package，不要靠 agent prompts 临场解释。
- 每个 functional package 的 **Falsification Ledger** 必须包含 claim disposition（`validated`、`reported-only`、`downgraded`、`deferred`、`rejected`）、反证检查、solution-fit risk 和会阻止进入 DAG 的 falsifier。
- 运行 Execution Contract Proof Route，并记录为什么 full kit 相比平台原生并发、Task Package Contract、ledger-lite 或 direct execution 更合适。
- 使用 Orchestration Value Score 辅助判断 full kit 是否值得：durable state、dependency unlock、recovery、integration、runner、operator burden。
- 对会改变用户可见行为、布局、文案、工作流或视觉输出的 package，补齐 **User-Visible Delta Ledger**；不要对纯内部包强制增加这层负担。
- 运行 capability preflight：把每个 package 或 gate 分类为 `autonomous`、`agent-verifiable substitute` 或 `external-assist`。
- 默认只生成 agent 可自行完成的任务包；`external-assist` 只能作为非阻塞补充证据、release gate 或用户已明确批准的 manual gate 出现。
- 如果判断 real-device QA、真人视觉验收、外部审批、凭证输入等 `external-assist` 对目标必不可少、不可忽略且没有 agent-verifiable substitute，必须在制造输出任务包前中断流程，向用户说明不可替代原因、影响面和可选决策，等待用户批准 gate、改 scope 或放弃该 orchestration；不要先生成一个会被真人任务卡住的 kit。
- 启动前定义 landing strategy：primary path、preapproved fallbacks、explicit non-goals、abort conditions、independent merge candidates。
- 对只新增或更新长期分析/规划文档的 package，landing strategy 默认应声明 `mainline-documentation-landing`：通过隐私/敏感内容检查、路径归类、格式/链接自检和冲突检查后自动合入 mainline。不要因为它来自独立 agent 或 worktree 就默认留在分支里。

详细 projection、capability、landing/failure planning 规则见 `references/planning_contract.md`。

### 2. 生成 Orchestration Kit

在计划目录下创建：

```text
docs/plans/<plan-name>/
├── INDEX.md
├── packages/
│   ├── 01-<name>.md
│   ├── 02-<name>.md
│   └── 99-finalize.md
├── launchers/
│   ├── agent-prompts.md
│   ├── package-graph.tsv
│   ├── orchestrate.sh
│   ├── start-codex-app.sh
│   └── start-claude-code.sh
├── status/
│   ├── README.md
│   ├── state.tsv
│   ├── events.jsonl
│   ├── package-status-template.md
│   ├── <package-id>.md
│   └── 99-finalize.md
├── scratch/
│   └── .gitignore
└── FINAL_REPORT.md
```

精确 graph/state headers、runtime commands、runner behavior、no-`launched`-unlock 规则见 `references/runtime_contract.md`。长 Markdown templates 和最终聊天输出形状见 `references/artifact_templates.md`。

### 3. 必需脚本命令

生成的 `launchers/orchestrate.sh` 必须暴露：

```bash
start
advance [--from <package-id>]
status
retry <package-id>
finalize
cleanup --mainline <branch>
mark-state <package-id> <state> [fields...]
repair-state
doctor [--environment]
collect-logs <package-id>
verify-package <package-id>
verify-finalize
scratch-path <package-id>
```

核心行为：

- `start` 和 `advance` 获取 lock、验证 graph/state、计算 readiness，只启动 eligible packages。
- ready package 队列必须使用独立文件描述符，不能绑定到 dispatch loop 的 stdin；runner launch、logs postflight 或 health check 即使读取 stdin，也不得吞掉同 wave 的后续 package id。
- 所有读取完整 kit 的命令先验证 `agent-prompts.md`：graph 中每个 package 必须恰好有一个 `## Package: <package-id> - <title>` 标题；缺失、重复、未知或 malformed 标题必须在创建 worktree 或修改状态前失败。
- Package agents 只能通过 `mark-state` 修改 `state.tsv`。
- `retry` 只接受 `blocked`、`stale`、`invalid`，保留 prior recovery context，并遵守 three-strike fingerprint breaker。
- `doctor` 检查一致性和 runner/session health，不启动工作。
- `doctor --environment` 必须暴露 runner-specific preflight 事实；Codex runner 至少输出 CLI version、`codex exec` 是否支持 approval policy flag、sandbox/approval 配置、Codex home 和 home writability。
- Runner selection 必须跨 tail calls 持久化：首次显式 `ORCHESTRATION_RUNNER=<runner>` 启动时记录到 coordinator `status/runner`；后续没有环境变量的 `advance`、`retry`、`finalize` 使用该记录。不要依赖 Claude/Codex 工具子进程继承 shell 环境，否则 Codex package 的裸 `advance` 会回退到默认 Claude runner。
- `99-finalize` 只在全部 functional packages 为 `completed` 后运行；随后验证 evidence、保守 merge、报告结果；只有成功后调用 `cleanup --mainline <branch>`。cleanup 未完成时不得 `mark-state 99-finalize finalized`。
- 对 analysis-only / planning-only 产物，`99-finalize` 的默认动作是合入 mainline 并把结论带回主 coordinator thread；仅在敏感内容、未批准发布、路径越界、验证失败、冲突或用户明确隔离时保留分支并记录 blocker。
- `99-finalize` 更新每个 package 的 **Outcome Replay**：landed、partial、blocked、failed-no-merge、false-positive 或 external gate，并把可复用教训写入 `FINAL_REPORT.md`。
- `start-codex-app.sh` 和 `start-claude-code.sh` 必须是 thin wrappers：默认执行 `doctor --environment`、`start`、`status`，其余 orchestration 子命令透传给 `orchestrate.sh`，且不得复制调度、状态或 finalize 逻辑。

### 4. 给用户的输出

生成 kit 后，只展示立即可执行入口：

- Plan directory path。
- Mainline branch、integration branch、max parallel agents。
- First wave packages 和 final package `99-finalize`。
- Manual path：从 `launchers/agent-prompts.md` 复制 prompts。
- Script path：按 selected runner 只展示一个主启动脚本，同时给出另一个平台的完整 alternative runner 命令，避免把两套 runner 都伪装成默认路径。
- Script path：必须同时展示 Codex App 和 Claude Code 两个平台的可复制启动命令。按 selected runner 标注一个主路径：Codex 主路径展示 `bash <plan>/launchers/start-codex-app.sh`、JSONL/thread-id inspection；Claude 主路径展示 `bash <plan>/launchers/start-claude-code.sh` 和 `claude agents`。另一个平台作为 alternative runner 同样给出完整启动命令，不要只口头提到。命令必须使用绝对路径。
- 恢复命令按当前状态按需展示：只在 `blocked`、`stale`、`invalid`、runner/environment failure、日志诊断或 shell-less manual advancement 实际发生时，给出唯一相关命令和具体 package id。
- `advance`、`finalize`、`cleanup`、`verify-finalize` 和 `scratch-path` 属于自动 tail flow、finalizer 或 authoring surface，默认不向用户倾倒。
- External-assist gates、owners、是否阻塞 release、需要的 exact evidence。
- Landing strategy summary。

当 Codex 是 selected runner 时，主命令必须是 `start-codex-app.sh`，并把 evidence 描述为 JSONL logs 加 recorded thread/process identifiers，而不是 Claude Agents View；同时给出 Claude Code 的 `start-claude-code.sh` 启动命令作为可选替代。当 Claude 是 selected runner 时反向处理：Claude 命令是主路径，Codex App/Codex runner 命令仍作为可选替代输出。不要把两套命令都伪装成默认；明确哪条是本次主路径，哪条是可选替代。

## Guardrails

- 用户未明确要求 orchestration 时，不要使用本 skill。
- 不要把用户报告、sweep 结论、handoff package、截图或日志转述直接当成已验证事实；先做 orchestration 级 claim validation，再决定进入 DAG、discovery、defer、reject 或 blocked。
- 只有独立并发、启动审计、session 状态、日志或停止需求时，不要生成自定义 manifest/runtime；使用 Claude Code Agent View / Dynamic Workflows，或 Codex App/CLI 原生 subagent workflow。
- 需要 durable package docs 和轻量状态记录，但不需要自动调度和收口时，不要生成 full kit；改用 `agent-task-planner` 的 `ledger-lite` 或 `manual-pack`。
- 不要根据 PATH 上可用 CLI 自动切换 runner；可以根据用户明确选择或当前宿主平台选择主路径。Codex App 场景下选择 Codex runner 时，必须展示 `start-codex-app.sh`；Claude Code 场景展示 `start-claude-code.sh`。不要把裸 `orchestrate.sh start` 当作新 kit 的主启动入口。
- 不要把 `orchestrate.sh` 设计成 long-running watcher。
- 不要在 package prompts 里复制 scheduling logic；prompts 只调用 `advance`。
- 不要让 package agents 编辑 `INDEX.md`、其他 package status file，或手动编辑 `state.tsv`。
- `state.tsv` 由 `mark-state` 自动 HMAC 签名（`status/.state.sig`），下次 `preflight_all` 会校验；直接编辑 `state.tsv` 会触发签名不匹配并被拒绝。
- `validate_events_cleanup` 交叉校验：`99-finalize` 为 `finalized` 时，`events.jsonl` 必须包含 `cleanup_succeeded` 事件，且所有 `cleanup` 字段必须为 `removed`，否则所有入口命令拒绝继续。
- `doctor` 和 `advance` 调用 `preflight_state_signature` 校验 `state.tsv` 未在 `mark-state` 外被篡改。
- 不要把 worktree-local status 当 coordinator truth。
- 不要让 package agent 直接启动 downstream packages。
- 不要把 real-device QA、external approvals、credential entry、human-only visual judgment 等非 autonomous 工作分配给 auto-launched packages。
- 不要把 external-assist requirements 藏在 acceptance criteria 里。
- 不要在用户尚未批准阻塞性 external-assist gate 时输出完整任务包；先暂停并请求决策。
- failure handling 时，不要发明 INDEX 未预先批准、用户也未批准的 fallback paths。
- 主计划失败后，不要 merge 任何东西，除非它是预声明的 independent merge candidate 且有 standalone verification。
- 不要给 `state.tsv` 增加 narrative evidence、retry history、QA links、release tickets 或 reviewer comments columns。
- 不要为每种 runner 或 agent platform 复制独立 lifecycle states 或 finalize logic。
- 不要通过相信最乐观 artifact 来解决 projection drift。
- 不要把 `scratch/` 当 scheduler truth、final evidence 或 secrets 存放处。
- finalize 未完全成功前，不要 cleanup branches/worktrees。
- 不要删除未记录为本 orchestration 创建的资源。

## 与轻量手动执行的关系

用户只需要 1-3 个手动执行事项时，不生成完整 orchestration kit；直接用 `docs/contracts/task-package-contract.md` 写清 package、验收标准和验证命令。用户需要 durable package docs、owner/verification/checkpoint 和人工推进状态时，优先交给 `agent-task-planner` 的 `ledger-lite` / `manual-pack` lane。用户要求 multi-agent orchestration control plane、状态账本驱动 dispatch、DAG、失败恢复、runner wrappers、自动收口或 cleanup 时，才使用 `agent-orchestration-planner`。
