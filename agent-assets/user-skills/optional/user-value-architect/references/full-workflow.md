# User Value Architect Full Workflow

本 reference 保留完整执行手册、candidate model、gate、报告结构、chat-only schema 和完成标准。主入口见 `../SKILL.md`。

路由语义以主入口为准：本文件中的 `route-to`、联合 handoff 或 agent active 只表示轻量上下文中的 Standard 入口或生成建议；正在运行的 architect、sweep、Deep 或 Exhaustive workflow 不得自动启动另一个重型 skill。

## Mission

从用户可感知价值出发，寻找能让用户明显觉得“更好用、更可信、更省力、更能完成事”的高上限改进机会。

本 skill 默认只做分析，不修改代码、不生成实施计划、不启动 agent、不执行实验。除非用户明确要求 chat-only 或 no-files，分析完成后默认生成 reviewable HTML 评审面作为正式交付，并在最终回复提供报告路径和可点击 `file://` URL；只有在用户明确要求 agent 接力或源文件交付，或环境完全无法产出 HTML 时，才另写同名 Markdown 源报告。

核心问题是：

> 什么改变最可能让用户体验、主观感受、信任、效率或目标达成效果出现跃迁，而不是只让系统内部变得更整洁？

30% 改善是高上限候选进入认真分析的下限，不是目标线。分析必须继续追问是否存在 2x、3x 或数量级改善用户价值的可能，但不得为了跨过门槛把小改进包装成伪量化跃迁。

**Two-Track Candidate Model**：同时维护 **high-ceiling candidates** 和 **small high-certainty improvements**。30% entry line applies to high-ceiling recommendations；小而确定、用户能感知、投入很低的改进不需要伪装成 30%+ 或 2x，也不要因为达不到 ceiling 叙事而自动出局。Do not inflate 小改进的 floor/ceiling；do not automatically drop 它们，而是标为 `optimize`、`fast validation bet` 或局部体验修复，并说明它们不是 primary ceiling bet。

## 默认执行强度与询问门槛

本 skill 同时支持用户显式调用与 agent active 自启用。默认深度由调用来源决定：

- **用户显式调用**（用户点名本 skill、提出用户价值/体验跃迁/上限分析诉求、或同义触发词）：默认 **Deep Value Analysis**，覆盖核心证据面、structural value mechanism、persona critique、rejected ideas，并产出正式 HTML 评审面。
- **Agent active 自启用**（其他 agent / skill 在判断 user-value 信号成立后主动调用本 skill）：默认 **Standard / Value Scan**，覆盖目标、成功路径、候选 gate、最小验证与最高上限方向，但不强制做完整 anti-satisficing、competitive ceiling 或多轮证据浪潮；可在最终回复中提示「升级到 Deep / Exhaustive 需要用户确认」。
- **Exhaustive Value Analysis**：仅在用户明确要求「极致 / 全覆盖 / 充分发挥模型能力 / 多模态全面核查」时进入；不是默认值。

无论用户显式调用还是 agent active 自启用，调用即视为授权执行本 skill 在当前环境和既有安全边界内的对应原生工作流。在所选深度的 envelope 内**默认全力执行**：覆盖该深度对应的全部核心证据面、必修工作流和正式 HTML 报告；只有用户明确要求降级、缩小范围或聚焦时，才进一步降低预算、跳过适用证据面或收窄对象。

可从当前 workspace、用户消息、文件、截图、页面或已有上下文合理推断的 scope、target、persona、budget 和输出形态，直接推断并记录，不要询问用户。信息不足但仍能继续时，将其写入 `assumptions / unknowns / coverage debt`，并继续完成其余可执行工作。

只有完全无法识别分析对象，或下一步需要用户未授权的 implementation、实验、不可逆操作、账号状态变更、发布或推送时，才中断询问。多模态降级、生成报告、外部参照搜索、只读或常规验证、选择默认 budget 不需要额外确认。

## Output Language

私有版默认使用中文交付。保留必要英文关键词、技能名、命令、文件名、指标名和产品术语，例如 user-perceived value、ceiling、floor、rubric、Task Package Contract。

私有版正式报告的可见正文、标题、表格字段和 HTML UI 文案默认使用中文。英文只保留在必要的技能名、文件名、代码标识符、指标名和行业术语中；不要把主章节标题、推荐卡、按钮、状态标签或说明性段落整体写成英文。若用户明确要求英文报告，才切换为英文，并在报告 `Analysis Scope` 中记录该语言选择。

## When To Use

Use this skill when the user asks for:

- 项目、产品、功能或工具如何大幅提升用户价值、用户体验、用户感受、目标达成效果；
- “充分探索”“追求上限”“30% 以上”“2x/10x 改善”“用户会明显感知到的优化”；
- 在功能优化、设计优化、交互流程、默认输出、反馈闭环、信任机制、长期能力建设之间寻找高杠杆方向；
- 对一个已有方案、PRD、产品、AI agent、技能、报告、App、网站或工作流做用户价值跃迁分析；
- 在进入 `ce-brainstorm`、`ce-plan`、`ce-optimize`、Task Package Contract 或 `agent-orchestration-planner` 之前，判断最值得押注的用户价值方向。

Do not use it as the primary skill when:

- 目标是纯内部重构、架构抽象、技术债治理、CI、测试、发布、代码质量或工程效率，且用户几乎感知不到；
- 用户只想修一个明确 bug，或只需要代码 review；
- 用户已经选定具体实现方案，只需要拆任务或执行；
- 问题核心是安全发布、遗留迁移、架构不变量或质量扫雷，应分别使用 `deep-flow-sweep`、`renewal-architect`、`abstraction-architect` 等。

内部优化只有在能清晰传导到用户可感知价值时才可纳入，例如：性能提升让等待显著减少，架构能力让用户获得原本做不到的结果，自动化减少用户操作负担。

## Relationship To Nearby Skills

| Nearby skill | Better when | Handoff signal |
|---|---|---|
| `ce-ideate` | 需要广泛生成许多想法 | 本 skill 发现价值方向仍太宽，需要先生成更多候选 |
| `ce-brainstorm` | 已选定一个用户价值方向，需要定义需求 | 某个候选通过 user value gate，需要写成 PRD/requirements |
| `product-sense-refiner` | 已有方案但默认输出、推荐框架、用户决策不够 sharp | 候选方向成立，但表达、默认体验或指标激励需要精炼 |
| `ce-optimize` | 已有可测量指标或 judge rubric，需要实验收敛 | 候选需要用硬指标或 LLM-as-judge 验证 |
| `abstraction-architect` | 用户价值提升依赖删除一类结构复杂度 | 用户痛点来自重复表示、流程状态散落、控制面膨胀 |
| `renewal-architect` | 用户价值提升依赖遗留迁移、采用路径、回滚试点或组织约束 | 价值方向成立，但成败取决于稳定性护栏、adoption economics 或可回滚 pilot |
| `deep-flow-sweep` | 主要问题是质量风险、主流程失效、稳定性或发布风险 | 价值上限被可靠性问题卡住，需要先扫雷 |
| Task Package Contract / `agent-orchestration-planner` | 分析后需要执行包装 | 候选已转为 Task Package Contract；复杂并发才升级 orchestration |

## Operating Modes

| Mode | Trigger | Output | Code changes |
|---|---|---|---|
| Value Scan (Standard) | Agent active 自启用默认；或用户给出宽泛目标但未要求高预算 | Reviewable HTML 评审面，包含候选地图、证据缺口、最高上限方向，并提供路径/URL | No |
| Full Value Analysis (Deep) | 用户显式调用默认 | Reviewable HTML 评审面，覆盖完整证据面、structural value mechanism、persona critique、rejected ideas，并提供路径/URL | No |
| Exhaustive Value Analysis | token 预算充足、用户明确要求充分发挥模型能力或全面核查工程 | Reviewable HTML 评审面，包含多证据面核查、persona critique、anti-satisficing、competitive ceiling、stop ledger，并提供路径/URL | No |
| Validation Handoff | 用户接受某个候选 | 验证计划、rubric、任务包或下游技能路由 | No |
| Authorized Follow-up | 用户另行要求实现 | 退出本 skill，转交相应实现/计划技能 | Not here |

任一 Mode 都可在用户明确要求时附带 Markdown 源报告（`.md`），用于 agent 接力或源文件交付；这是升级项，不是默认项。

## Budget Envelopes

默认值由调用来源决定：用户显式调用默认 **Deep**；agent active 自启用默认 **Normal / Value Scan**；只有用户明确要求 Exhaustive、极致、全覆盖、充分发挥模型能力时才进入 Exhaustive。预算决定最低证据面，不是装饰性标签。

| Envelope | Trigger | Required depth |
|---|---|---|
| Normal | 快速判断、单个方向、小型材料 | 用户价值目标、成功路径、候选 gate、最小验证 |
| Deep | “深入”“充分”“高预算”、项目材料较多 | Normal + 代码/文档/体验/反馈/外部参照证据面，structural value mechanism，persona critique，rejected ideas |
| Exhaustive | token 足够多、要求充分发挥模型能力、全面核查工程 | Deep + 主用户路径审计、近期计划/历史报告交叉核查、多模态体验检查、external reference scan、anti-satisficing、competitive ceiling、decision compression、stop condition |

当选择 Deep 或 Exhaustive 时，必须读取 `references/method-and-report.md` 的对应 sections，不要只执行主文件的轻量流程。

## Core Principles

1. **用户感知优先**：建议必须改变用户体验、感受、信任、效率、结果质量或目标达成概率。
2. **上限优先，不止达标**：30% 是 high-ceiling recommendations 的入场线；继续寻找 2x、3x 或数量级机会，同时保留 small high-certainty improvements，不用伪量化把它们说大。
3. **删除用户负担优先于优化内部形状**：优先找能删除等待、困惑、步骤、决策、失败、重复输入、低信任的改变。
4. **功能、设计和长期能力同等合法**：只要能传导到用户价值，建议可以是功能、交互、内容、默认体验、反馈闭环、信任机制、数据能力、个性化、agent 记忆或长期系统能力。
5. **证据和想象并存但分层**：大胆探索上限，但把 observed evidence、inference、hypothesis 和 unknowns 分开。
6. **不可感知内部优化出局**：维护性、代码美感、架构优雅、agent 便利性、CI 效率不能单独成为推荐理由。
7. **反证比口号重要**：每个高上限候选都要说明怎么证明它错了、过早了或用户不在乎。
8. **外部坐标校准上限**：当同类产品、相邻领域或公开案例会塑造用户期待时，不做 external reference scan 就不要声称 category-shift、switching reason 或 3x+ 上限。
9. **结构性价值优先于功能罗列**：高杠杆推荐必须说明它删除哪一类反复出现的用户负担、失败路径、手工翻译、低信任或决策成本，而不是只新增一个功能点。

## Workflow

### 0. Latch Analysis-Only Mode

声明本次默认仅分析。允许写报告、证据账本、验证计划和任务包；不修改产品代码、测试、配置、迁移、运行时行为或 Git 历史。

### 0.2 Investigation Kernel Adaptation

本 skill 参考项目级 Investigation Kernel，但本段是 standalone local adaptation：即使 single skill copied out，也必须能独立执行用户价值调查。

- **analysis artifact root**：正式分析写入被分析项目的 `reports/user-value-architect/`；只允许写 Markdown/HTML 报告、evidence ledger、candidate matrix、coverage debt、validation plan、task packages 和 review exports。
- **analysis-only boundary**：默认不得修改产品代码、测试、配置、迁移、依赖锁、运行时行为或 Git 历史。任何实现、实验、发布、迁移或 Git 操作都需要报告后的 **new explicit user authorization**。
- **evidence map**：先建立 value path / user success map，覆盖用户入口、first value、core loop、failure/recovery、trust formation、output artifacts、external expectation 和 long-term compounding，再生成推荐。
- **handoff ledger projection**：作为 producer/consumer，保留稳定 Evidence IDs，并至少记录 type、source artifact、observation、confidence、consumed recommendation/validation ID；接手其他 skill 的 ledger 时复用旧 ID，只追加新证据。
- **coverage debt**：无用户反馈、无 UI/截图、无运行路径、无外部参照或无历史使用证据时，必须写入 evidence gaps / coverage debt，不得伪装成已验证体验判断。
- **claim permission**：没有 Project Immersion Protocol、Value Theory、Specificity Gate 和外部/相邻 ceiling 校准时，不得声称 primary bet、3x+、switching reason、category-shift 或 breakthrough。
- **budget-aware stop review**：low-information wave 只触发停止复盘；Normal 可快速收敛，Deep 要覆盖核心 value path，Exhaustive 根据剩余关键未知、外部参照和 marginal information gain 决定是否继续。不是固定两轮停止。

### 0.3 Fact Map Before Advice

Deep/Exhaustive 模式下，先完成 **Fact Map Before Advice**，再生成推荐。事实地图不是长列表，而是推荐许可的前置证据层：

- scope assumption：本次默认分析对象、用户对象和材料边界；
- asset inventory summary：长期资产、用户可见资产、历史报告、公开/私有发布源、脚本、测试和输出物的覆盖状态；
- user-visible surface inventory summary：入口、命令、页面、报告、HTML、prompt、agent 默认行为、错误/恢复路径、导出物；
- path trace summary：至少三条 user path，或说明为什么少于三条并覆盖所有可用路径；
- Evidence IDs：给每条路径、产物、命令、截图、报告或外部参照分配稳定 evidence ID，后续候选必须回连这些 ID；
- promise-reality tensions：项目承诺、实际路径、输出形态和失败恢复之间的主要张力；
- coverage debt：缺失证据、未能运行/查看的材料，以及这些缺口会影响哪些 claim。

只有当 Project Immersion Protocol、Value Theory / Project-Specific Leverage、Specificity Gate 和必要外部参照共同支持时，候选才获得 **recommendation permission**。没有 permission 的内容只能标为 `hypothesis`、`validate-first`、`defer` 或 `blocked_by_evidence`。

**No Naked Recommendations**：不得直接推荐“智能路由”“自动化”“记忆层”“dashboard”“统一平台”“体验优化”等裸概念。每条推荐必须绑定当前项目的真实 artifact、真实路径、用户可见 moment、最小验证切片和反例；否则降级为 brainstorm label。

**Advice Atomicity Contract**：每张推荐卡必须同时包含 user-visible moment、Evidence IDs、Current experience slice、After experience slice、structural value mechanism、fastest validation / disproof test、rejected alternative。缺任一项时，不能写成 `recommend`。

### 0.4 Decision-First Output

调查机器是内部约束，不是默认主报告结构。正式报告必须用 **Decision-First Output**：先帮用户判断押注、风险和下一步，再把调查脚手架放到附录、折叠区或结构化 evidence ledger。

- **Evidence Compression Gate**：证据只有在改变推荐、优先级、置信度、风险判断、验证路径或 `blocked_by_evidence` 结论时，才进入主叙事；其余证据保留在 appendix / evidence ledger / HTML 折叠区。
- **Main Narrative Cap**：默认最多 3 个主推荐或战略押注。数量限制只限制主决策面，不限制候选生成、证据收集、rejected/deferred ideas 或 task packages。
- **Delete-The-Scaffold Rule**：默认不要在主报告摊开完整 Fact Map、Project Immersion Protocol 或 Coverage ledger；只有证据不足、结论争议大、用户要求审计过程，或需要解释 `blocked_by_evidence` 时才展开。
- **One-Screen Handoff Capsule**：给外部 agent 的交接必须压缩成一屏：recommendation ID、Evidence IDs、confidence、next action、blocked/deferred reason、validation command/artifact、owner skill。外部 agent 应能先读 capsule 再决定是否展开完整报告。

### 0.5 Resolve Scope Without Interrupting

默认不要用范围选择问题打断用户。除非用户明确要求先确认范围，否则按以下顺序自动确定分析范围：

- 用户消息指定了产品、功能、文件、截图、报告、PRD、页面或工作流时，严格以该范围为主，并只在必要时读取相邻上下文；
- 用户只说使用本 skill、做用户价值分析、做充分扫描或类似宽泛请求时，默认对当前仓库、当前产品或当前可见材料做整体用户价值扫描；
- 用户提供截图、录屏或具体现象时，把该材料作为高优先级证据，同时回到整体用户成功路径中判断它的价值影响；
- 当前仓库明显不是被分析对象，且用户也没有给出任何可分析材料时，才问一个最小澄清问题。

不要弹出“分析目标/范围选择”菜单。若范围是自动推断的，在报告开头用一句话说明 scope assumption，并继续执行；若之后发现范围不合适，再在 unknowns 或 validation 中标出。

### 1. Define The User Value Target

先明确：

- 用户是谁，处在什么真实场景；
- 用户想完成什么结果；
- 当前体验、感受或达成效果哪里不够好；
- 用户成功的可观察信号是什么；
- 30%+ 入场线如何定义；
- 理想上限是什么：2x、3x、10x，还是“从无法完成到可完成”。

如果用户价值对象细节不足，但当前仓库、产品名、文件线索或用户给出的材料足以形成合理范围，先按整体扫描推进，并把缺失信息标为 unknowns。只有在完全无法判断分析对象时，才提出一个最小澄清问题。

### 2. Gather Multimodal Evidence

根据材料可得性读取：

- 代码、README、PRD、roadmap、strategy、plans、reports；
- UI 截图、录屏、设计稿、页面、日志、错误信息、测试输出；
- 用户反馈、issue、support case、analytics、访谈摘录；
- 竞品或同类产品参考；
- 历史会话、既有 brainstorm、deep sweep 或 architecture report。

没有证据时可以做 hypothesis，但必须显式标记。视觉、交互或感受判断需要多模态材料；没有截图/录屏/可运行界面时，不要假装看过体验。

非多模态降级：如果当前模型或环境不能直接查看图片、录屏或 UI，不要因此中断整体扫描，也不要要求用户先换模型。继续读取文本、代码、文档、DOM/accessibility tree、OCR 输出、截图文件名/尺寸、alt text、日志和用户描述；把未直接检查的视觉判断标为 `visual_evidence_unavailable`、`unknown` 或 `deferred`。能通过工具生成 OCR、页面文本、UI tree 或截图摘要时，将其作为弱证据使用，并在报告中说明证据强度。

Deep/Exhaustive 模式下，不要停留在材料罗列；必须核查“承诺给用户的价值”和“用户实际路径”是否一致。至少覆盖 docs/product promise、main user path、visible UI or output、failure/recovery path、recent plans or reports 中可获得的证据面。

#### Project Immersion Protocol

Deep/Exhaustive 报告在进入推荐前必须完成项目沉浸。不要把“读了 README 和若干文件”当作深入项目；必须先形成可审计的证据覆盖。

- **Asset inventory**：盘点当前项目的长期资产和用户可见资产，例如 README、AGENTS、docs、reports、scripts、tests、examples、公开发布源、UI/CLI/API/output artifacts、近期提交和历史报告；说明哪些已读、抽样、不可用或不相关。
- **User-visible surface inventory**：列出用户实际接触的入口、命令、页面、报告、HTML、prompt、agent 默认行为、错误/恢复路径和导出物；若没有 UI，也要追踪用户可见文本输出和工作流产物。
- **Path trace minimum**：至少 trace **three concrete user paths**；若项目确实少于 3 条主路径，说明原因并 trace 所有可用路径。每条路径必须包含 trigger、setup、first value、decision point、failure/recovery、trust cue、evidence IDs。
- **Promise-reality check**：把项目承诺、实际路径、输出形态和失败恢复逐项对照，找出 promise not implemented、implemented but hidden、useful but high-friction、technically correct but low-trust。
- **Coverage ledger**：在报告中说明覆盖到什么程度、哪些高信号面缺失、继续探索是否可能改变结论。

若 Deep/Exhaustive 报告没有完成 Project Immersion Protocol，不得给出 `recommend`、`switching reason`、`category-shift`、`3x+` 或 `10x` 结论；必须降级为 Value Scan，或以 `blocked_by_evidence` 收尾并列出缺失材料。

### 3. Run External Reference Scan

当用户期待受同类产品、相邻工具、行业默认体验或公开案例影响时，必须建立外部坐标。外部参照不是复制竞品功能，而是校准用户已经见过什么、什么只是 table stakes、什么才可能构成 switching reason。

至少区分：

- **Direct competitors / same-category best products**：同类最佳体验、功能、报告或工作流；
- **Adjacent excellence**：相邻领域已经成熟的交互、信任、自动化、默认输出或反馈闭环；
- **Failure patterns / anti-patterns**：看似高级但可能增加用户负担、降低信任或奖励错误指标的做法。

若需要最新市场事实、产品能力、价格、benchmark、公开评价或案例，必须验证当前来源；无法联网或材料不足时，把 competitive ceiling 标为 `unknown` 或 `hypothesis`，不要把内部想象包装成外部事实。

### 4. Map The User Success Path

画出用户从动机到达成结果的路径：

- trigger：用户为什么来；
- setup：用户需要准备什么；
- first value：首次感到有用的时刻；
- core loop：重复使用的主循环；
- failure and recovery：失败、困惑、撤回、重试、求助；
- trust formation：用户什么时候相信系统；
- long-term compounding：使用越久是否越懂用户、越省力、越能产出结果。

标出摩擦、等待、低信任、认知负担、重复劳动、情绪挫败和结果不确定性。

### 5. Generate High-Upside Value Candidates

候选来源包括：

- 功能优化：让用户完成原本完成不了、很难完成或低质量完成的事；
- 设计优化：让用户更快理解、更少犹豫、更少错误、更有信心；
- 流程重构：删除步骤、模式切换、手工确认、重复输入和恢复成本；
- 默认体验优化：让第一次输出、默认路径、推荐动作天然更贴近用户目标；
- 反馈闭环：让系统从用户行为、结果和纠错中变好；
- 信任机制：让用户知道系统为什么这样做、哪里可靠、哪里需要人工判断；
- 长期能力建设：记忆、上下文、个性化、历史学习、跨任务复用、生态或平台能力；
- 价值重新 framing：从“提供工具”升级为“帮用户达成结果”。

至少区分：

- **Incremental improvements**：可能有价值，但主要改善一个步骤；
- **Step-function opportunities**：删除整段用户负担或改变成功路径；
- **Ceiling bets**：证据不一定充分，但乐观情况下用户价值上限很高。

### 5.5 Apply The Two-Track Candidate Model

候选必须先分轨，避免把所有价值都挤进 30%/2x/3x 叙事：

- **high-ceiling candidates**：目标是 30%+、2x、3x、10x、switching reason 或 category-shift。它们需要 floor、ceiling、path_to_ceiling、external ceiling、disproof test 和更严格的 evidence strength。
- **small high-certainty improvements**：目标是低投入、低风险、用户可见、证据确定的局部体验改进，例如减少一个误解点、修正文案、暴露已有能力、减少一步重复操作、提升错误恢复清晰度。它们可以进入 `optimize`、`fast validation bet`、`do-now` 或局部修复列表。

30% entry line applies to high-ceiling recommendations. 对 small high-certainty improvements：do not inflate floor/ceiling，不要写成“可能 2x”来获得重视；do not automatically drop 它们，只要它们有明确 user-visible moment、低风险、低投入和可信证据。报告中应明确区分“押注上限”和“确定性局部收益”，不要让小改进挤掉 strategic ceiling bet，也不要让上限追求吞掉确定性收益。

### 6. Define Value Theory And Project-Specific Leverage

生成候选前先写出 **Value Theory / Project-Specific Leverage**。它解释为什么这个项目有机会产生高用户价值，而不是直接进入通用改进清单。

必须回答：

- 用户真正稀缺的资源是什么：时间、注意力、判断力、信任、恢复能力、结果质量、长期复利，还是某种无法靠普通工具获得的能力？
- 项目的独特资产是什么：领域知识、历史报告、工作流深度、用户偏好、数据/上下文、可审阅交付、自动化基础设施、公开/私有边界、生态位置？
- 当前最大价值泄漏点是什么：发现成本、设置成本、等待成本、判断成本、信任成本、迁移成本、复用成本、输出不可行动，还是失败恢复成本？
- 哪些方向会放大项目独特资产，哪些只是任何同类项目都适用的通用优化？

如果无法说清 project-specific leverage，只能输出探索性候选，不得把智能路由、自动化、记忆层、仪表盘、AI 总结等通用模式包装成最高上限建议。

### 7. Identify The Structural Value Mechanism

对进入推荐竞争的候选，先追问它背后的稳定用户价值机制：

- 用户真正反复要完成的 job / outcome 是什么，当前系统是否把它拆成了过多工具、命令、报告、选择或人工判断？
- 哪一类用户负担在多个路径中重复出现：setup、等待、检查、解释、修正、恢复、确认、上下文重建、结果转译、信任建立？
- 有没有一个更合适的 interaction object、task object、decision surface、feedback loop、memory/context layer 或 trust surface，可以让这些负担成为同一结构的自然投影？
- 哪些例外应该被新机制吸收，哪些是真实差异必须保留，哪些只是弱相似的 false alarm？
- 这个机制能删除整类用户步骤或失败路径，还是只改善一个局部点？

如果用户价值提升依赖更深的 domain invariant、状态对象、流程空间化、边界重构或重复表示删除，把候选标为 route-to-`abstraction-architect` 或联合 handoff，而不是在本 skill 内伪装成完整实现方案。

### 8. Apply The User-Perceived Value Gate

每个候选必须回答：

- 用户会在哪里明确感知到变好？
- 用户会更快、更稳、更轻松、更有信心，还是获得更好结果？
- 改善属于功能、设计、流程、默认体验、反馈、信任还是长期能力？
- 为什么它不只是轻微 polish？
- 它相对外部参照是 table stakes、parity、switching reason，还是 category-shift？
- 它删除的是哪一类反复出现的用户负担或失败路径？
- 如果用户完全感知不到，这个候选是否应该剔除？
- 最小验证方式是什么？

未通过 gate 的候选降级为 internal-only、deferred 或 route-to-other-skill。

Gate 结果必须保留分轨：高上限推荐需要说明 30%+ floor 和 ceiling；small high-certainty improvements 只需证明用户可见、证据强、风险低、投入小、不会与更高上限方向冲突。不要为了让小改进通过 gate 而写伪精确百分比。

### 9. Apply The Specificity Gate

每个 `recommend`、`validate-first` 或 `strategic ceiling bet` 候选必须通过 **Specificity Gate**，否则降级为 brainstorm/hypothesis。

必须包含：

- **2-5 specific artifacts**：点名当前项目中 2-5 个具体文件、页面、报告、命令、截图、脚本、测试、issue 或输出作为证据；不要只写“代码/文档/用户路径”。
- **Current experience slice**：用 3-6 步描述用户现在如何经历这个问题，必须能回连到 evidence IDs。
- **After experience slice**：用 3-6 步描述改后用户会怎样具体感到更省力、更可信或更能完成事。
- **First validation slice**：给出第一个可验证切片，范围小到可以先学习价值信号，而不是先建设完整平台。
- **Genericity check**：如果这条建议换到任何同类项目都适用，必须说明本项目的特殊证据和独特杠杆；说不清时降级。
- **Counterexample**：说明什么观察会证明它只是听起来高级、实际用户不在乎或价值不如更小方案。

不要推荐只停留在“建立管线”“智能路由”“加记忆层”“做 dashboard”“增加自动化”的抽象名词。必须把抽象能力压到当前项目的一个真实路径、真实产物和真实验证切片上。

### 10. Run Ceiling Exploration

对通过 gate 的候选继续追问上限：

- 如果不受当前实现限制，用户理想体验是什么？
- 哪个改变能删除整段用户负担，而不是改善一个步骤？
- 能否从“帮用户操作”升级到“替用户达成结果”？
- 能否从“一次性功能”升级到“持续学习用户偏好、上下文和目标”？
- 如果竞争产品也做了常规优化，什么能力仍让用户明显感到不同？
- 如果借鉴相邻领域最佳体验，当前候选的更高阶版本是什么？
- 达到上限需要哪些产品、数据、设计、模型、工作流或组织条件？

记录：

```text
User Value Upside:
- floor: 为什么至少可能超过 30%
- ceiling: 乐观情况下可能达到多大改善
- path_to_ceiling: 逼近上限的条件
- evidence_strength: 当前证据是否足以支持这个上限判断
```

Exhaustive 模式下，必须再运行 anti-satisficing pass：对每个推荐候选写出“更高上限版本”“删除整段用户负担版本”“从工具到结果代理版本”，并说明为什么采用或拒绝。

### 11. Classify Evidence And Decision

对每个候选分别记录：

- `value_upside`: low / medium / high / breakthrough；
- `confidence`: high / medium / low；
- `user_visibility`: obvious / indirect / weak / none；
- `time_to_signal`: hours / days / weeks / months；
- `investment`: small / medium / large / strategic；
- `disposition`: recommend / validate-first / brainstorm / optimize / handoff / defer / drop。

不要用一个总分掩盖差异。高上限低证据的候选应保留为 validation-first，而不是被低风险小优化挤掉。
小而高确定性的候选应保留为 optimize / fast validation bet / do-now，而不是因为缺少 30%+ ceiling 自动出局；但它也不能伪装成 primary bet、category-shift 或 3x+。

### 11.5 Critique, Compress, And Stop

Deep/Exhaustive 模式下，运行多视角批判：

- 新用户：是否更容易首次获得价值？
- 重度用户：是否减少重复劳动并提高长期收益？
- 流失用户：是否解决离开的核心原因？
- 竞品用户：是否有足够强的 switching reason？
- UX reviewer：是否降低认知负担、错误和低信任？
- Engineering reality reviewer：是否能先验证再大投入？

批判后必须把输出压缩成可决策集合：

- **Primary bet**：最值得押注的用户价值方向；
- **Fast validation bet**：最快产生学习信号的验证方向；
- **Strategic ceiling bet**：证据可能不足但上限最大的长期方向；
- **Do-not-do list**：内部爽感、低可见性、竞品 parity、proxy-gaming 或过早大投入的方向。

停止条件：

- 主用户路径和关键失败/恢复路径已覆盖到当前材料允许的程度；
- Project Immersion Protocol 已完成，或明确降级为 Value Scan / `blocked_by_evidence`；
- Value Theory / Project-Specific Leverage 能解释推荐为何不是任何同类项目都适用；
- 推荐候选都通过 user-perceived value gate；
- 推荐候选都通过 Specificity Gate，包含 2-5 个具体证据 artifact、当前/改后体验切片和反例；
- 外部参照已校准 table stakes / parity / switching reason / category-shift，或明确标为 unavailable；
- 高杠杆推荐已说明 structural value mechanism 和删除的用户负担类别；
- 每个高上限候选都有反证路径和最快验证路径；
- 已执行 anti-satisficing，连续一轮没有发现更高上限版本；
- rejected/deferred ideas 能解释为什么不是用户价值最高押注。

### 12. Produce Report And Handoff

除非用户明确要求 chat-only 或 no-files，正式分析和扫描默认产出 reviewable HTML 评审面作为唯一正式交付，并在最终回复提供报告路径和可点击 `file://` URL。只有用户明确要求 Markdown 源（agent 接力 / 源文件交付），或环境完全无法产出 HTML 时，才另写同名 Markdown 源报告，与 HTML 共享同一 evidence IDs、candidate IDs、recommendation IDs 和结论。

报告必须落在被分析项目的长期报告目录中：优先使用 authoritative workspace 的项目根目录 `reports/user-value-architect/`，目录不存在时先创建。若当前路径位于 `.claude/worktrees/`、`.worktrees/` 或其他 agent worktree，先从项目 `AGENTS.md` 的 authoritative workspace / Authoritative workspace 字段、用户消息中的主项目路径、或 Git common dir 判断真实项目根；不要把正式报告留在 worktree 自己的 `reports/`、仓库根目录、当前 shell 目录、`.tmp/`、agent worktree 根目录或系统临时目录。若当前上下文无法写入 authoritative workspace 的项目 `reports/`，必须在最终回复中明确说明降级路径和原因。

报告命名：

```text
reports/user-value-architect/user_value_architect_report_{YYYYMMDD}_{HHMM}.html
# 仅在用户明确要求 Markdown 源或 HTML 无法生成时，附加：
reports/user-value-architect/user_value_architect_report_{YYYYMMDD}_{HHMM}.md
```

生成 HTML 前，优先使用 `reviewable-html-report` capability，确认本报告只复用 review surface mechanics，不把 domain conclusions 交给 companion skill。当前仓库可把 `skills/reviewable-html-report/references/report_base.md` 作为 TOC linkage、review-controls、stable `data-card-id`、feedback export、localStorage fallback、Mermaid fallback/lightbox 的可选增强；至少每个推荐卡和高风险决策卡都应是 reviewable unit。若无法读取该能力或 repo-local reference，使用 `references/fallback.html` 降级为 self-contained static HTML，并在最终回复说明缺少哪些 review mechanics。

HTML 必须包含章节索引和点击跳转：每个主章节使用稳定 `id`，顶部或侧栏 TOC 用 `href="#section-id"` 链接到对应章节。若共享引用不可用，降级报告至少保留核心结论、TOC、稳定 section id、证据附录、Mermaid source fallback，以及不依赖 localStorage 的反馈区。主动打开浏览器只作为用户要求或明确 GUI 环境下的可选预览，不是完成标准；如果 HTML 完全无法生成，必须以 Markdown 兜底交付，并在最终回复中说明缺口。

详细报告结构、gate 和任务包字段见 `references/method-and-report.md`。需要正式报告或任务包时先读取该 reference。

## Required Output For Explicit Chat-Only Analysis

只有用户明确要求不落盘、只在聊天中回答时，才使用这个轻量输出。否则使用上面的 HTML 评审面收尾（必要时附带 Markdown 升级源）。

小型分析可直接在聊天里输出：

```markdown
## Recommendation
<最高用户价值上限的 1-3 个方向>

## User Value Target
<用户、目标、当前摩擦、30% 入场线和理想上限>

## Candidate Comparison
| Candidate | User visibility | Floor | Ceiling | Confidence | Next step |
|---|---|---|---|---|---|

## Reject / Defer
<用户不可感知、证据弱、假杠杆或应转交其他技能的方向>

## Validation
<最小验证方式、指标或 judge rubric>
```

## Completion Standard

- 用户价值对象明确。
- 区分 observed evidence、inference、hypothesis、unknowns。
- Deep/Exhaustive 报告在建议前完成 Fact Map Before Advice；没有 recommendation permission 的内容不得写成推荐。
- 正式报告遵守 Decision-First Output、Evidence Compression Gate、Main Narrative Cap、Delete-The-Scaffold Rule 和 One-Screen Handoff Capsule。
- Deep/Exhaustive 报告完成 Project Immersion Protocol；否则降级为 Value Scan 或 `blocked_by_evidence`。
- 包含 Value Theory / Project-Specific Leverage，说明建议为何不是任何同类项目都适用。
- 至少一个候选追求 30% 以上的上限；若没有，明确说没有发现高上限机会。
- 使用 Two-Track Candidate Model，区分 high-ceiling candidates 与 small high-certainty improvements；30% entry line applies to high-ceiling recommendations，不要 inflate 小改进，也不要 automatically drop 小改进。
- 每个推荐候选通过 User-Perceived Value Gate。
- 每个推荐候选通过 Specificity Gate，点名 2-5 specific artifacts，并给出 Current experience slice、After experience slice、First validation slice 和 Counterexample。
- 每个推荐候选遵守 No Naked Recommendations 和 Advice Atomicity Contract，显式连接 Evidence IDs、用户可见 moment、验证/反证和 rejected alternative。
- 当外部参照会影响用户期待时，包含 competitive / adjacent / anti-pattern 坐标；没有证据时明确降级。
- 高杠杆推荐包含 structural value mechanism：删除哪类用户负担、保留哪些真实差异、为什么不是局部功能罗列。
- 不把内部优化当作推荐，除非传导路径清晰。
- 同时列出 floor、ceiling、path_to_ceiling 和 evidence strength。
- 最终推荐压缩为 primary bet、fast validation bet、strategic ceiling bet 和 do-not-do。
- 包含 rejected/deferred ideas，防止报告只奖励想象力。
- 给出最小验证方式或下游技能路由。
- 未经用户另行授权，不修改代码或进入实现。
- 正式分析以 HTML 评审面落盘到项目 `reports/user-value-architect/`，HTML 有章节索引和锚点跳转，最终回复提供路径和可点击 `file://` URL；用户明确要求 Markdown 源或环境无法产出 HTML 时，再附加同名 `.md`。
- HTML 评审面使用 `review-controls`、stable `data-card-id` 和 feedback export，或明确说明 reviewable-html 降级原因。
