# Deep Flow Focus Profiles

用户指定侧重点时读取本文件。Profile 改变证据预算和报告排序，不取消主流程、可靠性、证据门和 analysis-only 基线。

## Routing

| User wording | Profile | Required playbook |
|---|---|---|
| 未指定侧重、默认充分发挥 | `balanced` | `profile-balanced.md` |
| 主功能、核心功能、主流程、用户路径、UI 落地 | `main-flow` | `profile-main-flow.md` |
| 稳定性、可靠性、崩溃、恢复、并发、状态一致性 | `reliability` | `profile-reliability.md` |
| 性能、速度、延迟、内存、CPU、电量、吞吐 | `performance` | `profile-performance.md` |
| 安全、权限、信任边界、漏洞、AI/LLM 风险 | `security` | `profile-security.md` |
| 日志、可观测性、诊断、错误信息、告警 | `observability` | `profile-observability.md` |
| 测试覆盖、测试质量、回归保护、flaky | `test-effectiveness` | `profile-test-effectiveness.md` |
| 项目治理、CI、发布、文档、agent parity、产物来源 | `project-governance` | `profile-project-governance.md` |
| 需求落实、计划符合度、会话要求、验收条件 | `requirement-conformance` |

可组合最多两个 primary profiles。用户列出三个以上侧重点时使用 `balanced`，把点名维度作为显式检查项，避免过度稀释。

## Shared Allocation

- 单一 focus：约 50% 证据预算投入该 profile，35% 保留主流程与可靠性基线，15% 用于其余高风险信号。
- 双 focus：每个约 30%，主流程与可靠性基线至少 30%，其余 10% 自适应分配。
- Profile 只影响优先级，不允许跳过 release-critical flow、信任边界、直接证据或恢复检查。
- 报告先呈现 focus findings，再列 baseline findings 和 deferred dimensions。

## Common Profile Contract

- 路由到 common profile 后必须读取对应 playbook，执行其 Required Analysis Model、Mandatory Questions、Evidence Ladder 和 Completion Gate。
- `balanced` 不是退化路径：它必须建立 dimension coverage matrix，并在触发专项风险时加载对应 playbook。
- 双 profile 同时满足两份 completion gate；共享证据可以复用，但不能用一份报告标题假装另一门已完成。
- 工具不可用时按 playbook 的降级路径收集较弱证据，并把未满足 gate 的部分标为 deferred/external。

## Lightweight Profiles

### `requirement-conformance`

- 建立 requirement → implementation → test → runtime evidence 矩阵。
- 来源可包括用户原始要求、计划、issue、验收条件和历史会话；记录来源定位和时间。
- 会话或记忆工具无结果时，明确标记 unavailable，不得用 Git 猜测替代后宣称已核验会话要求。
- 需求漂移按用户影响与验收失败排序，不按文本差异数量排序。

## Method Sources

- [Google SRE: Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)：symptom/cause 区分与 latency、traffic、errors、saturation 信号。
- [GitHub CodeQL query suites](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-query-suites)：统一引擎下用 default、extended 和 custom suites 调节覆盖与误报。
- [Agent Skills Specification](https://agentskills.io/specification)：主技能保持精简，专项方法按需从 references 加载。
