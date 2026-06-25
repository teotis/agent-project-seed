# Deep Flow Analysis Arsenal

本文件是 `deep-flow-sweep` 的组合方法库。预算决定可用上限，风险和证据缺口决定实际启用的方法。不要把 Exhaustive 理解为“所有工具必须运行”。

## Contents

1. Selection Protocol
2. Baseline Weapons
3. Triggered Weapons
4. Heavy Weapons
5. Combination Recipes
6. Source Methods

## Selection Protocol

每轮维护：

| Field | Question |
|---|---|
| `unknown` | 哪个未知项最可能改变 release/quality 判断？ |
| `trigger` | 哪条 flow、diff、历史、日志或边界信号触发方法？ |
| `cost` | low / medium / high |
| `completion_confidence` | 在剩余预算、权限和环境内跑完并解释结果的概率 |
| `expected_information_gain` | 预计新增发现、增强证据或关闭未知项的程度 |
| `artifact` | 运行后可复核的 test/log/trace/report |
| `decision` | run / defer / skip，以及理由 |

运行规则：

1. 先执行 `D0-D2`，建立入口、关键 flow 和高风险场景基线。
2. 依据状态、外部边界、历史重复、供应链或覆盖信号选择下一张卡。
3. 高成本工具只有在能完整运行、结果可 triage、且可能改变结论时启用。
4. 工具不可用不等于跳过问题：使用手工 failure injection、模型比较或静态 variant search 降级。
5. 连续两轮没有新增 P0/P1、没有显著增强证据、也没有关闭关键未知项时停止；release-critical 未覆盖面除外。

## Baseline Weapons

### D0 Lightweight Flow Probe

- **Answers**: 项目有哪些入口、测试、CI、manifest、配置、脚本、外部边界、风险信号和 churn 热点？
- **Cost**: low。
- **Run**:
  ```bash
  python3 <skill-dir>/scripts/flow_probe.py <root> --pretty
  ```
- **Path**: `<skill-dir>` 是包含当前技能 `SKILL.md` 的目录。
- **Artifact**: JSON reconnaissance inventory。
- **Limit**: regex 命中是候选，不是 finding；必须回到真实 flow 验证。
- **Combine with**: `D1`, `D2`, `D7`。

### D1 Attack Surface And Execution Path Map

- **Answers**: 输入从哪里进入，经过哪些信任边界、状态和副作用，最终产生什么成功信号？
- **Cost**: low-medium。
- **Method**: 参考 OWASP WSTG 的 entry point、execution path 和 architecture mapping，但扩展到 CLI、后台任务、移动端、构建发布和 agent 工具。
- **Artifact**: flow map、trust boundaries、critical side effects、不可用外部依赖。
- **False-positive guard**: 仅存在 route/command 不代表 release-critical；按用户和业务影响排序。

### D2 Scenario Matrix

- **Answers**: 每条关键 flow 在 happy、empty、invalid、state、timing、environment、dependency、recovery 等场景下可能如何失败？
- **Cost**: medium。
- **Method**: 从 flow map 生成少量高价值情景；每个情景必须对应 observable probe。
- **Artifact**: scenario → prediction → verification path 矩阵。
- **Disable when**: 不允许只有抽象猜测而没有可观察检查。

## Triggered Weapons

### D3 Stateful Model And Invariants

- **Trigger**: lifecycle 可重复、恢复、取消、重试；状态分散；顺序相关 bug。
- **Answers**: 哪些动作序列会违反“每一步之后都必须成立”的 invariant？
- **Cost**: medium-high。
- **Method**: 定义 primitive actions、preconditions、model state 和 invariants；工具可用时使用 Hypothesis/QuickCheck state machine，否则手工生成短序列。
- **Artifact**: 最小失败动作序列、被违反 invariant、可复现测试。
- **False-positive guard**: 模型必须体现真实允许状态，不能把产品未承诺行为当 invariant。

### D4 Fault Injection And Recovery

- **Trigger**: 网络、文件、进程、数据库、硬件或第三方边界；恢复语义不明确。
- **Answers**: 部分失败、超时、中断、重复执行后是否可诊断并安全恢复？
- **Cost**: medium。
- **Method**: 在明确边界注入 timeout、exception、partial write、process exit、permission denied；检查 cleanup、retry、idempotency 和 residual state。
- **Artifact**: injection point、observed behavior、cleanup state、retry result。
- **False-positive guard**: 环境不具备依赖时标记 external，不把 setup 失败误判为产品 bug。

### D5 Property And Metamorphic Testing

- **Trigger**: 输入空间大；没有简单 oracle；转换、序列化、排序、归一化或编译流程。
- **Answers**: 哪些跨输入关系应始终成立？
- **Cost**: medium。
- **Method**: 定义 round-trip、idempotence、monotonicity、permutation invariance、model equivalence 等 property。
- **Artifact**: property、生成策略、最小反例。
- **False-positive guard**: property 必须来自契约，而不是为了方便测试臆造。

### D6 Variant Search

- **Trigger**: 已确认一个 bug、危险模式、缺失 guard 或错误状态处理。
- **Answers**: 同类缺陷是否出现在其他 flow、语言或仓库？
- **Cost**: low-high。
- **Method**: 从已确认 seed 提取语义特征，文本/AST/data-flow 搜索并逐个 triage；有 CodeQL 时可扩大查询范围。
- **Artifact**: seed、候选全集、真阳性、误报和覆盖声明。
- **False-positive guard**: 未确认 seed 前不做大规模扩散。

### D7 Supply-Chain And Workflow Governance

- **Trigger**: release、公开仓库、依赖更新、CI 权限、二进制产物、第三方 action 或自动发布。
- **Answers**: 构建和发布链是否存在不可审查、未固定、过权或已知脆弱环节？
- **Cost**: medium。
- **Method**: 参考 OpenSSF Scorecard 检查危险 workflow、依赖更新、分支保护可见证据、binary artifacts、token permissions、pinned dependencies 和 fuzzing adoption。
- **Artifact**: check、证据位置、工具限制、remediation direction。
- **False-positive guard**: Scorecard 风格的低分是风险信号，不自动等于可利用漏洞。

### D8 Observability And Recovery Drill

- **Trigger**: 用户报告“失败但不知道为什么”；日志分散；状态文件可能残留；重试前需人工清理。
- **Answers**: 失败能否被定位、归因和安全重试？
- **Cost**: medium。
- **Method**: 对代表性失败运行诊断 drill，检查错误信息、correlation、状态快照、artifact、cleanup 和 retry。
- **Artifact**: failure timeline、可见信号、缺失诊断、恢复步骤。

### D9 Documentation And Agent Parity

- **Trigger**: README/AGENTS/CLI 命令漂移；人能通过 GUI 完成但 agent 无工具；自动化依赖隐式本机状态。
- **Answers**: 文档、工具和实际行为是否一致？agent 是否具备与人类等价的可操作面？
- **Cost**: low-medium。
- **Method**: 对关键操作执行 doc-to-command trace 和 human-to-agent parity matrix。
- **Artifact**: documented command、actual result、missing capability、approval/environment dependency。

## Heavy Weapons

### D10 Mutation Testing

- **Trigger**: 关键 flow 测试通过但历史上缺陷复发；覆盖率无法证明断言有效。
- **Cost**: high。
- **Method**: 对关键模块运行 PIT、mutmut、Stryker 或同类工具；限制 mutation scope，优先条件边界、返回值和调用删除。
- **Artifact**: killed/survived mutants、timeout、equivalent mutant triage。
- **Disable when**: 测试基线不稳定，或剩余预算不足以解释存活 mutant。

### D11 Coverage-Guided Fuzzing And Introspection

- **Trigger**: parser、协议、文件格式、反序列化、边界输入；已有 fuzz target 但覆盖长期停滞。
- **Cost**: high。
- **Method**: 使用现有 fuzzer；比较静态可达性和动态 coverage，寻找 blocker；维护最小高覆盖 seed corpus。
- **Artifact**: coverage、reachability gap、crash corpus、最小复现。
- **False-positive guard**: timeout/OOM/flaky crash 必须可复现和分类。
- **Disable when**: 没有可隔离 target，或预算不足以完成 corpus/coverage 分析。

### D12 Cross-Repository Variant Analysis

- **Trigger**: 共享模板、库、复制实现或同类已知缺陷跨仓库传播。
- **Cost**: high。
- **Method**: 先在 2-5 个仓库验证 query precision，再使用 CodeQL MRVA 或受控搜索扩大范围。
- **Artifact**: repository coverage、variant distribution、triage rate。
- **Disable when**: seed 未确认或权限/数据库不足。

### D13 Longitudinal Drift Analysis

- **Trigger**: 当前快照健康，但补偿性修复、流程脆弱度或自动化人工介入可能持续上升。
- **Cost**: high。
- **Method**: 选择有意义历史切片，比较 compensatory fix ratio、critical-flow churn、test co-evolution、dependency/security posture 和 agent intervention。
- **Artifact**: 趋势、拐点、漂移方向、证据限制。

## Combination Recipes

| Signal cluster | Recommended combination |
|---|---|
| retry/cancel/resume 状态复杂 | `D0 → D1 → D3 → D4` |
| parser 或文件导入边界 | `D1 → D5 → D11` |
| 已知 bug 可能复制扩散 | `D2 → seed verification → D6 → D12` |
| CI/release 权限和依赖风险 | `D0 → D7 → D4` |
| 测试全绿但缺陷复发 | `D2 → D10 → D6` |
| 失败难诊断且重试需清理 | `D4 → D8 → D9` |

## Source Methods

- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/): attack surface, execution path, business logic, error handling, API testing.
- [Hypothesis stateful testing](https://hypothesis.readthedocs.io/en/latest/stateful.html): generated action sequences, preconditions, model comparison, invariants.
- [PIT mutation testing](https://pitest.org/quickstart/basic_concepts/): testing whether assertions detect injected behavioral faults.
- [OSS-Fuzz ideal integration](https://google.github.io/oss-fuzz/advanced-topics/ideal-integration/): minimal high-coverage seed corpora and robust fuzz integration.
- [OSS-Fuzz Fuzz Introspector](https://google.github.io/oss-fuzz/advanced-topics/fuzz-introspector/): static reachability versus dynamic coverage and blocker discovery.
- [OpenSSF Scorecard checks](https://github.com/ossf/scorecard/blob/main/docs/checks.md): workflow, dependency, review, binary artifact and fuzzing risk signals.
- [NIST SSDF](https://csrc.nist.gov/pubs/sp/800/218/final): recurring vulnerability root-cause prevention across the SDLC.
- [GitHub CodeQL multi-repository variant analysis](https://docs.github.com/en/code-security/concepts/code-scanning/multi-repository-variant-analysis): query-driven variant search across repositories.
