# Performance Profile Playbook

## Objective

用可重复测量确认用户可感知或系统约束上的性能问题，定位主要瓶颈并区分回归、容量边界和环境噪音。静态代码形态只能提出假设。

## Required Analysis Model

先建立 **metric contract**：

| Field | Required value |
|---|---|
| Operation | startup/capture/request/render/job 等具体动作 |
| User-visible boundary | 测量起点、终点和 success oracle |
| Metric | latency/throughput/CPU/memory/I/O/battery/frame time |
| Statistic | median、p90/p95/p99、max 或 steady-state rate |
| Workload | 输入规模、数据状态、并发度和持续时间 |
| Environment | device/OS/build/compiler/network/power/thermal |
| Lifecycle state | cold/warm/hot、cache、login、first run |
| Repetitions | warm-up、sample count、discard rule |
| Comparator | baseline、previous commit、budget/SLO |

同时建立 symptom → measurement → profiler evidence → bottleneck hypothesis → confirming experiment → remeasure → regression guard 链。

## Mandatory Questions

1. 哪个用户动作或容量目标变慢，阈值和 comparator 是什么？
2. cold/warm/hot、平均值/tail latency、微基准/端到端是否被混淆？
3. 是否使用 release-like build，debug、emulator、thermal throttling 或后台负载造成了偏差？
4. warm-up、sample count、输入和环境是否足以复现？
5. profiler/trace 显示时间或资源实际花在哪里？
6. 微基准中的热点是否真的支配端到端用户体验？
7. 内存增长是 peak、steady-state、leak、cache 还是 GC/allocator 行为？
8. 改动前后差异是否超过 run-to-run variance？
9. 哪个 benchmark、budget、telemetry 或 CI gate 会阻止同类 regression 再次进入？

## Evidence Ladder

1. 受控环境下重复 benchmark，差异超过方差且绑定用户 success oracle。
2. trace/profiler 与 benchmark 同时指向同一瓶颈。
3. 生产/设备 telemetry 在明确 cohort 中显示稳定 regression。
4. 单次 timing、debug build、emulator 或不可复现实验。
5. 循环、分配、文件大小、复杂度等静态猜测。

P0/P1 性能结论通常需要 1–3；4–5 只能形成 measurement task。

## Method Selection

- 先跑端到端 baseline，再选择 profiler；不要先看到可疑代码再设计指标。
- 用户交互、启动、滚动、拍照等使用 macro/end-to-end benchmark。
- 可隔离的 CPU hot loop、转换或布局成本使用 microbenchmark，并证明其端到端占比。
- Android 优先 release-like Macrobenchmark/Perfetto/Profiler；Web 使用浏览器 trace 与稳定 workload；服务端使用 request/load profile 和 percentile。
- 内存使用 allocation/heap timeline + lifecycle repetition；battery/power 需要足够长 workload 和设备条件。
- 比较提交时保持 workload、build、device 和 lifecycle state 一致。
- 即使本次只分析不修复，也要为任务包定义 remeasure 条件与 regression guard；没有 guard 的局部优化容易在后续改动中回退。

## Severity Calibration

- P0：性能退化使 release-critical flow 实际不可用或触发系统性崩溃/资源耗尽。
- P1：可重复的明显用户阻断、SLO/预算违反、ANR/jank/尾延迟或容量回归。
- P2：已测得但影响有限的回归、局部热点或缺少性能回归门。
- P3：无 measurement 的优化机会。

## Completion Gate

- metric contract 完整，包含 baseline、workload、环境、warm-up、样本和 comparator。
- 报告同时给出原始统计、方差/置信限制和 trace/profiler artifact。
- 端到端症状与局部瓶颈有因果确认实验，或明确标记尚未归因。
- 任务包包含同环境 remeasure 方法和可持续 regression guard。
- cold/warm、median/tail、micro/macro 的适用边界已说明。
- 不可用设备或生产 telemetry 被列为 external，未用静态推测替代。

## Report Contract

```markdown
## Performance Case
- Metric contract:
- Baseline / comparator:
- Samples and variance:
- Trace/profiler evidence:
- Bottleneck attribution:
- User impact:
- External limits:
```

## Anti-Patterns

- 在 debug build 或一次手工 timing 上下结论。
- 只给平均值，不看 tail latency 与方差。
- 把 microbenchmark 改善等同于用户链路改善。
- 看到循环、分配或大文件就标记性能 P1。
- 没有 warm-up、环境和输入记录，无法复现。
- 只证明一次优化有效，却没有定义 regression guard。

## Method Sources

- [Android Benchmark overview](https://developer.android.com/topic/performance/benchmarking/benchmarking-overview)：区分用户交互 Macrobenchmark 与隔离代码 Microbenchmark，并要求先识别真实瓶颈。
- [Android Macrobenchmark](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview)：受控启动、交互、trace 和重复测量。
