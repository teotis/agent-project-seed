# Reliability Profile Playbook

## Objective

验证系统在重复、并发、部分失败、资源压力、进程中断和恢复后仍保持核心 invariant，并能安全继续服务或明确降级。

## Required Analysis Model

为每条关键 flow 建立：

1. **State model**：状态、允许转换、终止状态、重入点。
2. **Invariant ledger**：每一步之后必须成立的数据、资源和用户可见条件。
3. **Fault matrix**：边界 × timeout/exception/partial result/duplicate/cancel/restart。
4. **Recovery model**：cleanup、retry、resume、rollback、idempotency 和 residual state。

区分 correctness、availability、durability、recoverability 和 diagnosability，不把“没有崩溃”当作可靠。

## Mandatory Questions

1. 哪些操作可能重复、交错、取消、超时或在提交中途退出？
2. retry 是否有预算、退避、幂等键和终止条件？
3. 部分成功后，数据、文件、锁、线程、连接和 UI 状态是否一致？
4. 进程/设备/worker 重启后，系统如何识别 unfinished work？
5. 并发 schedule 是否会造成 lost update、double side effect 或 stale result？
6. 下游变慢或失败时是否形成队列堆积、资源耗尽或 cascading failure？
7. recovery 是自动、用户可操作，还是需要隐式人工清理？

## Evidence Ladder

1. 可重复 fault injection、并发 schedule 或 restart drill 违反/保持 invariant。
2. stateful/property test 得到最小失败序列。
3. 真实日志与持久状态证明部分失败或恢复结果。
4. 沿 reachable path 的强静态证明。
5. broad catch、sleep、共享可变状态等候选。

## Method Selection

- `D1 → D3 → D4 → D8` 是默认链。
- 输入空间大或序列复杂时追加 `D5`。
- 已确认缺陷可能复制时追加 `D6`；测试长期漏检时追加 `D10`。
- 对网络/队列系统检查 overload、retry amplification、backpressure 和 load shedding。
- 工具不可用时，手工生成短动作序列和故障点，但必须保存状态前后证据。

## Severity Calibration

- P0：已证明的数据不可逆损失、安全暴露或系统性 release blocker。
- P1：正常条件可达的不可恢复状态、重复关键副作用、持久化损坏或 cascading failure。
- P2：有限边缘条件下的恢复脆弱、资源泄漏、弱重试或诊断缺口。
- P3：没有当前失败路径的防御性改进。

## Completion Gate

- 每条 critical flow 有 state model 和至少一个核心 invariant。
- 每个外部边界至少评估 timeout、partial failure 和 retry。
- 至少完成一次 interruption/restart 或 equivalent recovery drill。
- 并发或异步 flow 有 schedule/race 分析。
- residual state、cleanup、retry result 和诊断信号被记录。
- 所有未执行 fault 均有明确 blocker，不写成“已覆盖”。

## Report Contract

```markdown
## Reliability Case
- State model:
- Invariants:
- Fault injected:
- Observed residual state:
- Retry/recovery:
- Confidence and external limits:
```

## Anti-Patterns

- 只搜索 broad catch、sleep、null 和锁。
- 只验证进程不崩溃，不验证数据与副作用。
- 注入故障后不检查 cleanup 和第二次执行。
- 把 setup/权限失败误判为产品可靠性缺陷。

## Method Sources

- [Google SRE: Testing for Reliability](https://sre.google/sre-book/testing-reliability/)：压力、故障和恢复测试用于建立系统信心。
- [Google SRE: Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/)：overload、retry amplification、queue growth 与 load shedding。
