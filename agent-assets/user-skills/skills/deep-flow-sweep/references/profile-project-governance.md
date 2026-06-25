# Project Governance Profile Playbook

## Objective

验证 CI、发布、产物来源、文档命令和 agent 可操作性是否形成可信的交付控制面。安全、可观测性和测试有效性使用各自专项 playbook，本 profile 只汇总它们对 release confidence 的结论，不重复执行低质量 checklist。

## Required Analysis Model

建立 **governance matrix**：

| Area | Contract | Evidence | Drift/Risk | Owner/Gate |
|---|---|---|---|---|
| CI | 可重复 test/build/static gates | workflow + local equivalent | declared gate 未执行或结果不可追溯 | CI gate |
| Release | 权限、审批、回滚和环境契约 | workflow/runbook/release artifact | 过权、不可回滚、环境漂移 | release gate |
| Artifact provenance | source → build → package → publish 链 | digest/signature/build metadata | 来源不可审计、二进制漂移 | provenance gate |
| Docs/agent parity | 文档操作可被人和 agent 重放 | doc-to-command trace | documentation drift/tool gap | docs gate |
| Ownership | gate 失败有 owner 和处置路径 | CODEOWNERS/runbook/issues | 无人负责、长期豁免 | ownership gate |
| Specialist conclusions | security/observability/test evidence | 专项 profile ledger | 专项 gate 未满足 | routed gate |

## Mandatory Questions

1. CI 实际执行哪些 test/build/lint/security commands，是否与文档和报告声称一致？
2. release workflow 的权限、审批、环境、回滚和失败恢复是否明确？
3. artifact provenance 能否从发布物追溯到 source SHA、依赖锁、构建环境和发布动作？
4. README/AGENTS/runbook 中的关键命令能否通过 doc-to-command trace 重放？
5. 人类可完成的关键操作是否也有 agent tool、权限和可观察结果？
6. gate 失败、豁免和长期 drift 是否有明确 owner？
7. 安全、可观测性和测试问题是否应路由到专项 playbook，而不是在治理扫描里重复猜测？

## Evidence Ladder

1. 运行 CI/release-equivalent gate 并检查 artifact、digest、权限和回滚证据。
2. doc-to-command trace、human-to-agent parity drill、artifact provenance trace。
3. workflow、manifest、lock、runbook、ownership 和最近提交的强静态证据。
4. CI 绿灯、存在 release 脚本、存在 README 等单点信号。
5. “项目看起来缺规范”的主观判断。

## Method Selection

- 先运行 `D0` 收集 workflow、manifest、scripts、docs 和 release boundary。
- CI/release 与 supply-chain governance 使用 `D7`；文档和 agent parity 使用 `D9`。
- 测试证据读取 `profile-test-effectiveness.md`，不在本 profile 重新用覆盖率猜测测试质量。
- 安全证据读取 `profile-security.md`，不把依赖版本或输入形态直接升级为漏洞。
- 诊断证据读取 `profile-observability.md`，不把日志数量当作 diagnosability。
- 每个治理 finding 必须回连 release confidence、artifact trust、关键操作可重放性或长期 gate 失效。

## Severity Calibration

- P0：已证明的不可审计发布、凭证暴露、恶意或错误产物进入发布链、关键回滚完全失效。
- P1：关键 CI/release gate 不可信，导致无法判断发布物是否来自预期源码或是否通过必要验证。
- P2：重要 documentation drift、agent parity gap、权限过宽、provenance 缺字段或 owner 缺失。
- P3：不影响交付判断的局部维护改进。

## Completion Gate

- governance matrix 覆盖 CI、release、artifact provenance、docs/agent parity、ownership 和 specialist conclusions。
- 每个 area 至少有 evidence、deferred reason 或 external blocker。
- CI/release 声称有命令或 workflow 证据；artifact provenance 至少追踪一个代表性发布物。
- 文档漂移通过 doc-to-command trace 证明；agent parity 有实际工具/权限检查。
- security、observability、test-effectiveness 的触发项已路由到对应 playbook 或明确 deferred。

## Report Contract

```markdown
## Project Governance
| Area | Contract | Evidence | Risk | Gate |

## Delivery Confidence
- CI:
- Release:
- Artifact provenance:
- Docs/agent parity:
- Ownership:
- Specialist gates:
```

## Anti-Patterns

- 把 governance 做成包含安全、日志、测试全部细节的巨型 checklist。
- 看到 CI 绿灯就宣布 gate 可信，却没有核对实际执行命令和 artifact。
- 只确认“有发布脚本”，不检查权限、回滚和 artifact provenance。
- 把文档差异直接标成 P1，却没有 doc-to-command trace。
- 在本 profile 重复执行 security、observability 或 test-effectiveness 的弱化版本。
