# Balanced Profile Playbook

## Objective

默认模式不是平均浏览所有目录，而是先保证 critical flow 可达与可恢复，再按风险信号扩展到测试有效性、性能、可观测性、安全、依赖和长期漂移。输出必须说明哪些维度已验证、为何投入、哪些仍是 coverage debt。

## Required Analysis Model

建立一张 **coverage matrix**：

| Dimension | Target | Dimension trigger | Evidence planned | Status |
|---|---|---|---|---|
| Critical flow | 用户目标到成功结果 | 用户/发布影响 | runtime/test/trace | verified/deferred/blocked |
| Reliability | state/retry/recovery | 外部边界、异步、持久化 | invariant/fault drill | ... |
| Test effectiveness | risk 到 assertion | 改动、历史缺陷、弱测试 | test map/mutation | ... |
| Performance | 用户可感知指标 | latency/resource signal | benchmark/profile | ... |
| Observability | symptom 到 cause/recovery | 失败难定位 | diagnostic drill | ... |
| Security/dependency | trust/release boundary | auth/input/release signal | focused audit | ... |
| History/drift | 回归和补偿性修复 | churn/session signal | Git/session evidence | ... |

矩阵用于调度，不是要求每个维度投入相同预算。

## Mandatory Questions

1. 哪些 critical flow 决定“项目可用”或“本次发布成立”？
2. 每条关键 flow 的 success oracle、失败面和恢复路径是什么？
3. 当前 diff、Git 历史和会话记录暴露了哪些 dimension trigger？
4. 哪个未知项最可能改变 release/quality 判断？
5. 哪些维度只有静态候选，尚无直接证据？
6. 哪些未检查面形成真实 coverage debt，而不是低价值尾项？

## Evidence Ladder

从强到弱：

1. 代表性环境中的可重复 runtime 结果、失败复现或可验证 trace。
2. 聚焦测试、benchmark、fault drill、mutation 或强静态证明。
3. Git/会话/日志中的一致历史证据。
4. scanner、regex、coverage 百分比或代码形态候选。
5. 无可观察路径的假设。

只有 1–2 可独立支持 P0/P1；3 需要当前代码证据；4–5 只能触发后续探查。

## Method Selection

- 必跑 `D0 → D1 → D2`。
- critical flow/state 风险优先读取 `profile-main-flow.md` 或 `profile-reliability.md`。
- 性能、测试信号出现时读取对应 playbook，不以通用静态扫描替代专项方法。
- 每轮只选择最可能关闭关键未知项的方法，并记录 run/defer/skip。
- 不因 Exhaustive 预算仍有剩余而运行无触发的重型工具。

## Severity Calibration

- P0/P1 必须绑定 reachable critical flow 与直接证据。
- 单纯缺测试、日志格式、TODO、复杂文件或模糊提交不能超过 P2。
- 多个 P2 若共享根因，形成结构性 escalation，不通过抬高单项 severity 表达重要性。
- coverage debt 单列，不伪装成已发现缺陷。

## Completion Gate

- critical flow 全部进入 coverage matrix，且没有未解释的 omitted flow。
- 每个被触发维度都有 evidence、defer reason 或 blocker。
- 至少对最高风险 flow 完成 runtime/测试/强静态验证之一。
- reliability 与 recovery 基线已执行。
- 报告列出 dimension coverage、coverage debt、剩余未知项和停止原因。

## Report Contract

```markdown
## Balanced Coverage
| Dimension | Trigger | Evidence | Confidence | Status |

## Critical Decisions
- <finding or clean result>: <why it changes release confidence>

## Coverage Debt
- <unverified dimension/flow>: <reason and next evidence>
```

## Anti-Patterns

- 每个维度机械分配相同篇幅。
- 用大量低价值 P2/P3 营造“全面”。
- 性能没有测量、测试没有 assertion 分析、可靠性没有状态/恢复模型。
- 省略维度却不记录 coverage debt。

