# Main-Flow Profile Playbook

## Objective

证明用户或系统的核心目标能从入口走到可观察成功结果，并在失败、重试和恢复后保持正确。重点是完整功能链路，而不是逐文件 review。

## Required Analysis Model

为每个目标建立 **goal-to-outcome flow graph**：

```text
user/system goal
  → entry
  → input and validation
  → state transition
  → domain action
  → external side effects
  → persistence
  → visible output
  → success oracle
  → recovery/re-entry
```

每个节点记录代码 owner、前置条件、输出契约、失败信号和验证方式。跨线程、进程、模块、仓库、UI/后台边界必须画出，不得用“调用 service”概括。

## Mandatory Questions

1. 用户真正要完成的目标是什么，success oracle 是什么？
2. clean start、已有状态、空输入、非法输入分别走哪条链？
3. UI 显示成功是否与持久化、上传、写盘或后台任务成功一致？
4. 哪些边界可能吞掉错误、重复副作用或返回假成功？
5. 中断、旋转、进程重启、网络恢复、重复点击后从哪里 re-enter？
6. alternate entry 是否共享同一契约，还是形成行为漂移？
7. 当前测试只覆盖节点，还是覆盖完整链路和最终结果？

## Evidence Ladder

1. 端到端运行结果与 success oracle 同时成立。
2. 跨边界 integration/contract test 证明关键副作用和最终状态。
3. 沿真实调用图的强静态 trace，所有分支和结果均可解释。
4. 单节点 unit test、截图或日志。
5. 文件名、route、screen、类结构等候选。

截图或“页面打开”不能单独证明功能链路完成。

## Method Selection

- `D0 → D1 → D2` 建图和场景。
- 有状态转换时追加 `D3`；外部副作用追加 `D4`；失败不可诊断追加 `D8`。
- Web 使用浏览器走用户可见行为；移动端优先 emulator/device + UI tree/log；CLI/API 运行真实命令或 contract request。
- 对跨模块链路，分别验证边界两侧，再验证一次端到端 success oracle。
- 已确认 broken chain 后才使用 `D6` 搜索其他入口变体。

## Severity Calibration

- P0：release-critical goal 无法完成、产生数据损失/安全暴露，且已观察或确定性证明。
- P1：正常用户可达的 broken chain、假成功、不可恢复状态或关键副作用缺失。
- P2：替代入口、边缘状态、弱反馈或缺少端到端回归保护。
- P3：不影响目标完成的结构或一致性问题。

## Completion Gate

- 所有 release-critical goal 都有 flow graph 和 success oracle。
- 入口、状态、外部副作用、持久化、输出和 recovery 均已定位。
- 至少验证 happy、invalid/interrupted、retry/recovery 三类路径。
- 每个 broken chain 有最短断点、上游输入、下游影响和 falsification path。
- 未运行的真实设备/账号/生产验证明确列为 external。

## Report Contract

```markdown
## Functional Chain
- Goal:
- Flow graph:
- Success oracle:
- Verified paths:
- Broken chain:
- Recovery result:
- External checks:
```

## Anti-Patterns

- 按目录或类逐项列问题，却没有 goal-to-outcome 图。
- 把 UI 可见、函数返回或日志打印当作最终成功。
- 只测 happy path，不测中断与重新进入。
- 用单元测试数量替代完整功能链路证据。

