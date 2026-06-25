# Observability Profile Playbook

## Objective

验证关键失败能否从用户 symptom 追到 cause，并给出安全 recovery 路径。关注 error、log、metric、trace 和 status artifact 是否共同支持诊断，而不是统计日志数量或格式一致性。

## Required Analysis Model

建立 **symptom-to-recovery map**：

| Failure | User symptom | Error/log/metric/trace | Correlation | Cause localization | Recovery signal |
|---|---|---|---|---|---|
| boundary/state failure | visible behavior | available evidence | request/job/session ID | component/operation | retry/cleanup/success |

同时记录 sensitive data policy、signal ownership、retention/availability 和失败后的 diagnostic drill。

## Mandatory Questions

1. 用户或 operator 首先看到的 symptom 是什么？
2. error、log、metric、trace 和 status artifact 中哪个信号连接到 cause？
3. 跨线程、进程、服务或后台任务是否有稳定 correlation？
4. 日志是否泄露 secrets、PII、tokens、payload 或内部实现细节？
5. 错误信息是否区分用户可行动信息与内部诊断信息？
6. partial failure、retry、cleanup 和最终 recovery 是否留下可验证状态？
7. 告警是否基于用户 symptom/SLO，而不是噪音较高的内部 cause？
8. diagnostic drill 能否在代表性失败中定位问题，无需隐式人工知识？

## Evidence Ladder

1. 受控 diagnostic drill：注入代表性失败并从 symptom 追到 cause 和 recovery。
2. runtime timeline 结合 correlation、state artifact 和重试结果。
3. 沿 reachable path 的 logging/error/metric/trace 强静态证明。
4. 存在日志、统一格式、dashboard 或告警规则等表面信号。
5. “日志看起来太少/太多”的主观判断。

## Method Selection

- 从 `D1/D2` 的关键 flow 与失败场景开始，使用 `D8` 执行 diagnostic drill。
- 外部边界或恢复语义不明确时先用 `D4` 注入 timeout、partial result 或 permission failure。
- 检查 symptom/cause 分离、correlation propagation、structured fields、sensitive data redaction、status artifact 和 retry outcome。
- 参考 latency、traffic、errors、saturation，但只选择能解释当前用户目标的信号。
- 无法启动 runtime 时使用静态 trace 降级，并明确不能证明实际 diagnosability。

## Severity Calibration

- P0：诊断面本身造成 secrets/PII 大规模暴露，或关键故障完全静默并直接导致不可逆数据/安全影响。
- P1：release-critical failure 无法定位或误报成功，导致无法安全恢复、发布判断失真或严重事故响应阻断。
- P2：correlation 缺口、弱错误信息、缺少 recovery signal、告警噪音或敏感数据控制不足。
- P3：低风险字段、格式和维护改进。

## Completion Gate

- 每条 release-critical flow 至少选择一个代表性失败完成 diagnostic drill 或明确 blocker。
- symptom、cause、recovery 和 success signal 已连接。
- 跨边界 correlation、sensitive data、partial failure 和 retry outcome 已检查。
- 日志存在或格式统一没有被单独用作充分证据。
- 未运行的生产 telemetry、告警和 retention 检查标记 external/deferred。

## Report Contract

```markdown
## Observability Case
- Failure and user symptom:
- Diagnostic drill:
- Error/log/metric/trace evidence:
- Correlation:
- Cause localization:
- Sensitive data check:
- Recovery signal:
- External limits:
```

## Anti-Patterns

- 用日志行数、结构化格式或 dashboard 存在证明可观测性充分。
- 只检查 cause 日志，不检查用户 symptom 和 recovery。
- 为了“更详细”记录 secrets、PII 或完整 payload。
- 只列缺失 metric，不执行代表性 diagnostic drill。
- 把日志格式不统一直接提升为 P0/P1。
