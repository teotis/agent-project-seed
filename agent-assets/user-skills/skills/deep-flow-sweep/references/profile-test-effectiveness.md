# Test-Effectiveness Profile Playbook

## Objective

判断测试是否能发现 critical flow 的真实回归，而不是只统计测试数量或行覆盖率。重点覆盖风险、断言质量、隔离性和失败检测能力。

## Required Analysis Model

建立 **risk-to-test matrix**：

| Flow/risk | Failure oracle | Test level | Assertion quality | Coverage provenance | Gap |
|---|---|---|---|---|---|
| critical action | 可观察错误结果 | unit/integration/e2e | behavior/state/side effect | tool+scope+denominator | none/weak/missing |

`coverage provenance` 必须记录工具、目标模块、构建变体、分母、排除项和采集命令。覆盖率只说明代码被执行，不说明 assertion 能检测错误。

同时建立 **test topology map**：

```text
risk → production unit → system boundary → lowest sufficient test level
     → internal mocks → shared mutable state → setup/runtime cost
     → failure localization
```

`internal mocks` 指对同一产品内部 collaborator、私有函数或实现层的替身；外部 API、数据库、时钟、文件系统和硬件等系统边界替身单独记录。

## Mandatory Questions

1. 每条 critical flow 的 happy、failure、state、recovery 风险由哪个测试保护？
2. assertion 验证用户行为、状态和副作用，还是只验证 mock 调用/不抛异常？
3. 测试是否会在关键条件、返回值或副作用被删除时失败？
4. integration/contract/e2e 是否覆盖单元测试无法证明的边界？
5. flaky、sleep、共享状态、顺序依赖和环境依赖是否削弱可信度？
6. coverage 缺口对应可达风险吗，还是生成代码/不可执行路径？
7. 最近功能改动是否有 test co-evolution，历史缺陷是否有回归测试？
8. 测试基线是否稳定，失败是否可诊断？
9. bug 或历史回归是否有 Prove-It test：在修复前能稳定失败、修复后通过？
10. 当前测试是否位于能捕获该行为的 lowest test level，而不是用高成本 E2E 替代可充分证明行为的 unit/integration test？
11. 是否需要 mock 多个内部 collaborator 才能测试一个行为，暗示职责或边界过度耦合？
12. shared mutable state、巨大 fixture、全局 setup 或顺序依赖是否使测试无法独立运行？
13. 测试失败能否快速定位到行为边界，还是只能得到一个昂贵 E2E 的模糊失败？

## Evidence Ladder

1. mutation、故意破坏或历史回归重放证明测试能/不能捕获关键错误。
2. risk-to-test matrix + assertion inspection + 聚焦测试结果。
3. test topology map + 独立运行/失败定位证据 + 稳定的 branch/path coverage provenance。
4. 行覆盖率、测试数量、文件命名或 CI 绿灯。
5. “看起来测试很多/很少”的印象。

## Method Selection

- 先完成 critical flow/risk map，再读取测试；禁止从测试目录反推产品风险全集。
- 对每个高风险点执行 assertion quality review。
- 测试层级遵循 lowest test level that captures the behavior：纯逻辑优先 unit，跨边界优先 integration，critical user flow 才使用 E2E。
- 用 test topology map 识别 high mock pressure、shared mutable state、重复的高层测试和难以定位的失败。大量 internal mocks 是设计调查信号，不自动等于产品缺陷。
- 优先在真实系统边界使用 fakes/stubs；不要为了“单元化”而 mock 同一模块内部实现细节。
- 对已知 bug 或可重放历史缺陷，要求 Prove-It test 或等价 detection probe 先在当前缺陷状态失败；无法制造失败时，不得声称回归测试有效。
- 历史缺陷复发或 assertion 可疑时使用 scoped mutation testing。
- 状态序列使用 `D3/D5`；大输入空间使用 property testing；外部契约使用 integration/contract test。
- flaky 分析至少包含重复运行、seed/order、共享资源、时间和环境信号。
- coverage 工具不可用时，用静态 test-to-symbol map 降级，但明确不是数值覆盖率。

## Severity Calibration

- P0：通常不因“缺测试”单独成立；必须已有直接 release/security/data failure。
- P1：critical flow 已有高概率回归面，且测试被实验证明无法捕获，或 CI 基线不可信并阻断发布判断。
- P2：高风险路径缺失/弱 assertion、survived mutant、flaky 或 contract gap。
- 测试拓扑问题通常为 P2/P3；只有它已实验证明关键回归无法被捕获或 CI 失去发布判断能力时才可成为 P1。
- P3：低风险覆盖、命名、重复测试和组织问题。

## Completion Gate

- 所有 critical flow 风险进入 risk-to-test matrix。
- 每个 P0/P1 产品风险都标出当前 test protection 和 assertion oracle。
- coverage 数字均有 coverage provenance；没有 provenance 的百分比不进入结论。
- 至少对最高风险区域完成 mutation、故意破坏或等价 detection probe。
- 已知 bug 的 Prove-It test 记录修复前失败证据；测试层级选择有明确理由。
- test topology map 记录 internal mocks、系统边界、shared mutable state、setup/runtime cost 和 failure localization。
- flaky/隔离风险有重复运行或证据；未运行则列为 deferred。
- 报告区分 missing test、weak assertion、wrong level、flaky 和 untestable boundary。

## Report Contract

```markdown
## Test Effectiveness
| Flow/Risk | Existing Test | Oracle | Detection Evidence | Gap |

## Coverage Provenance
- command/tool/build/scope/denominator/exclusions:

## Mutation Or Detection Probe
- injected change:
- expected failure:
- actual result:

## Test Topology
- production unit and boundary:
- lowest sufficient level:
- internal mocks:
- shared mutable state:
- setup/runtime cost:
- failure localization:
```

## Anti-Patterns

- 用行覆盖率或测试数量直接评判质量。
- 只看测试是否通过，不看 assertion 是否能失败。
- 全仓 mutation，却没有 scope 和 survived mutant triage。
- 把 flaky 测试简单删除或重试隐藏。
- 把缺少低风险测试抬成 P1。
- 默认用 E2E 覆盖所有风险，造成慢、脆弱且定位困难的测试组合。
- 把所有 mock 都视为坏味道；系统边界替身可能是正确隔离手段。
- 看到 internal mocks 很多就直接要求重构，却没有证明理解、变化或回归成本。

## Method Sources

- [PIT Mutation Testing basic concepts](https://pitest.org/quickstart/basic_concepts/)：以存活 mutation 检查测试是否真正检测行为变化。
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)：测试用户可见行为、隔离性和稳定 locator，而非实现细节。
