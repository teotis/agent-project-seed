# Complexity Analysis Arsenal

本文件是 `complexity-sweep` 的按需方法库。先运行基础武器，再由结构信号、证据缺口和预算选择触发武器。不要因为预算充足就机械运行全部方法。

## Contents

1. Selection Protocol
2. Baseline Weapons
3. Triggered Weapons
4. Heavy Weapons
5. Combination Recipes
6. Source Methods

## Selection Protocol

为每个候选武器记录：

| Field | Question |
|---|---|
| `unknown` | 当前最影响结论的未知项是什么？ |
| `trigger` | 哪条代码、指标、历史或测试信号触发它？ |
| `cost` | low / medium / high |
| `completion_confidence` | 在剩余预算和环境内完整运行的概率 |
| `expected_information_gain` | 能否新增重要发现、增强证据或关闭未知项？ |
| `artifact` | 运行后应留下什么可复核证据？ |
| `decision` | run / defer / skip，以及理由 |

选择规则：

1. 先运行 `C0` 和 `C1`，建立事实基线。
2. 优先选择能解释多个热点共同根因的武器。
3. 高成本武器必须有具体 trigger、可观察 artifact 和足够 completion confidence。
4. 若工具缺失，使用等价的静态/手工方法，并降低证据等级。
5. 连续两轮没有新增 P0/P1、没有显著增强证据、也没有关闭关键未知项时停止扩张。

## Baseline Weapons

### C0 Lightweight Structure Probe

- **Answers**: 哪些文件同时具备规模、分支、缩进、导入、TODO 和 churn 信号？
- **Cost**: low。
- **Run**:
  ```bash
  python3 <skill-dir>/scripts/complexity_probe.py <root> --pretty
  ```
- **Path**: `<skill-dir>` 是包含当前技能 `SKILL.md` 的目录。
- **Artifact**: JSON 文件事实与 hotspot 排序。
- **Limit**: 指标是跨语言启发式，不是 AST 级圈复杂度；只能用于确定阅读顺序。
- **Combine with**: `C1`, `C3`, `C6`。

### C1 Three-Level Structure Map

- **Answers**: 微观、模块和架构三层的复杂度集中在哪里？
- **Cost**: low-medium。
- **Method**: 从 probe 热点出发，补充符号、调用者、依赖方向、数据流和 orchestration 角色。
- **Artifact**: micro/meso/macro map，标注已检查与未检查区域。
- **False-positive guard**: 大文件、深调用链或高 churn 本身不是 finding，必须证明理解成本或变化风险。

### C2 Pattern Catalog Pass

- **Answers**: 已知复杂度反模式是否存在具体实例？
- **Cost**: medium。
- **Method**: 按 `complexity-patterns.md` 检查高优先级结构单元，不要求对低风险文件逐项打勾。
- **Artifact**: 带位置、指标、反例和可证伪主张的候选 findings。
- **Disable when**: structure map 已显示目标范围很小且不存在显著热点。

## Triggered Weapons

### C3 Change Coupling And Shotgun Surgery

- **Trigger**: 同一概念频繁跨多个模块修改；probe 显示高 churn；近期 feature commit 触及大量分散文件。
- **Answers**: 复杂度来自错误边界，还是只是活跃开发？
- **Cost**: medium。
- **Method**: 对提交构建 file co-change matrix；区分测试共改、生成文件和真正的概念耦合。
- **Artifact**: 高频共变文件组、代表 commit、共同变化原因。
- **False-positive guard**: monorepo version bump、formatter、批量 rename 不算概念耦合。
- **Combine with**: `C4` 查找同类散落逻辑，`C7` 判断是否值得抽象。

### C4 Variant Search

- **Trigger**: 已确认一个重复 guard、adapter、状态转换、DTO 或 pass-through layer。
- **Answers**: 这是孤例还是系统性模式？
- **Cost**: low-high，取决于范围。
- **Method**: 从语义结构提取可搜索特征，先文本/AST 搜索，再检查调用和数据流；有 CodeQL 时可写 query 并扩大到多仓库。
- **Artifact**: seed pattern、候选全集、真阳性/误报分类、覆盖范围。
- **False-positive guard**: 仅名称相似不算 variant；必须共享行为或结构不变量。
- **Combine with**: 发现 3 个以上同根变体时升级 `abstraction-architect`。

### C5 Architecture Fitness Rules

- **Trigger**: 层级穿透、循环依赖、internal import、模块职责漂移或规则只存在于文档。
- **Answers**: 哪些边界可以转化为可执行约束？
- **Cost**: medium。
- **Method**: 使用 ArchUnit、dependency-cruiser、import-linter、custom lint 或项目现有工具表达规则；遗留系统可冻结既有违规，只阻止新增。
- **Artifact**: 规则、当前 violation baseline、增量违规列表。
- **False-positive guard**: 不为审美偏好写规则；规则必须保护已声明的不变量或真实变化成本。
- **Combine with**: `C9` 检查规则漂移趋势。

### C6 Cognitive Walkthrough

- **Trigger**: 指标不高但代码仍难理解；命名、隐式状态、时序或跨层跳转可能造成认知负担。
- **Answers**: 完成一个真实改动需要在脑中保持多少状态和跳转？
- **Cost**: medium。
- **Method**: 选择一个代表性 bugfix/feature，从入口开始记录跳转、隐藏前提、术语切换、必须同时理解的变量和文件。
- **Artifact**: comprehension trace、阻塞点、错误预测。
- **False-positive guard**: 熟悉度低不等于设计复杂；用第二条相似任务或历史 onboarding 证据复核。
- **Combine with**: `C3` 验证 walkthrough 中的跳转是否也表现为 change coupling。

### C7 Abstraction Economics

- **Trigger**: 单实现 interface、factory chain、pass-through service、泛型框架或插件点很多。
- **Answers**: 抽象实际删除了多少变化成本，又新增了多少理解和维护成本？
- **Cost**: medium。
- **Method**: 统计实现数、调用者、替换历史、分支差异、测试隔离价值和胶水比例；构造“删除抽象后的最小模型”作反例。
- **Artifact**: benefit/cost ledger 与保留、折叠或升级建议。
- **False-positive guard**: 测试替身、平台边界、公开 API 稳定性可能证明单实现抽象合理。

### C8 Test Fragility And Mutation

- **Trigger**: 高复杂度代码覆盖率看似充分，但 bug 反复出现或断言过弱。
- **Answers**: 测试是否真的约束了复杂分支和边界？
- **Cost**: medium-high。
- **Method**: 先审查分支-断言映射；工具可用时运行 mutation testing，检查存活 mutant 是否集中在热点。
- **Artifact**: 未受约束的行为、存活 mutant、缺失断言。
- **False-positive guard**: equivalent mutants、日志和不可观察实现细节不应转为缺陷。
- **Combine with**: `C1` 的高复杂度 + 低测试有效性形成最高优先级组合。

## Heavy Weapons

### C9 Historical Slice Comparison

- **Trigger**: 当前快照无法解释复杂度成因或演化方向。
- **Cost**: high。
- **Method**: 选择 3-5 个有意义历史切片，比较文件规模、依赖、结构规则、热点和测试比率；不要对每个 commit 重跑全量。
- **Artifact**: 趋势、拐点 commit、补偿链和复杂度迁移。

### C10 Cross-Repository Variant Analysis

- **Trigger**: 同一库、模板或复制代码存在于多个仓库，且本地已确认 seed pattern。
- **Cost**: high。
- **Method**: 使用 CodeQL MRVA 或受控的跨仓库搜索运行 seed query；先小样本验证 precision。
- **Artifact**: repository coverage、variant 分布、误报率。
- **Disable when**: seed pattern 尚未稳定，或没有权限/数据库/时间完成结果 triage。

### C11 Architecture Violation Baseline

- **Trigger**: 项目已有大量架构违规，无法一次清零，但继续增长会恶化。
- **Cost**: high at setup, low recurring。
- **Method**: 冻结已知违规，新增 CI gate 只拒绝新违规；本 sweep 只评估可行性和 baseline，不直接改代码。
- **Artifact**: frozen baseline、允许例外、未来收缩策略。

### C12 Differential Analyzer Triangulation

- **Trigger**: 单一静态工具给出大量结果或存在明显语言盲区。
- **Cost**: high。
- **Method**: 用两种独立方法测量同一性质，例如 AST complexity + cognitive walkthrough、dependency graph + Git co-change。
- **Artifact**: 一致结果、冲突结果和解释。
- **Stop rule**: 若第二种方法不改变排序或证据等级，不再增加第三种同类工具。

## Combination Recipes

| Signal cluster | Recommended combination |
|---|---|
| 高 churn + 跨模块共改 + 散落 validation | `C0 → C3 → C4 → abstraction-architect` |
| 单实现接口 + 多层 delegate + 无替换历史 | `C1 → C7 → C8` |
| 文档声明分层但 internal import 增长 | `C1 → C5 → C9` |
| 指标普通但新成员持续误改 | `C6 → C3 → C5` |
| 高复杂度 + 高覆盖率 + bug 仍复发 | `C1 → C8 → C4` |

## Source Methods

- [ArchUnit User Guide](https://www.archunit.org/userguide/html/000_Index.html): architecture rules, frozen violations, architecture metrics.
- [GitHub CodeQL multi-repository variant analysis](https://docs.github.com/en/code-security/concepts/code-scanning/multi-repository-variant-analysis): query-driven variant search at scale.
- [PIT mutation testing basic concepts](https://pitest.org/quickstart/basic_concepts/): test effectiveness through injected behavioral mutations.
