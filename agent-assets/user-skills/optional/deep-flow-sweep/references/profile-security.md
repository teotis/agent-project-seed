# Security Profile Playbook

## Objective

从真实 trust boundary、攻击者能力和可达 execution path 出发，识别可利用的安全缺陷。优先证明 exploitability、影响和现有控制是否失效，不把通用 best practice 缺失直接当作漏洞。

## Required Analysis Model

建立 **threat-to-control matrix**：

| Asset/Flow | Trust boundary | Attacker capability | Exploitation scenario | Existing control | Proof |
|---|---|---|---|---|---|
| protected action/data | user/API/file/tool/model | anonymous/authenticated/tenant/admin | input → sink → impact | validation/authz/sandbox | runtime/static/deferred |

覆盖适用的 authentication、authorization、input handling、data protection、secrets、third-party integration、supply-chain 和 AI / LLM 边界。

## Mandatory Questions

1. 哪些资产、操作和数据跨越 trust boundary？
2. authentication 与 authorization 是否分开验证，是否存在 IDOR、tenant escape 或权限提升？
3. 外部 input 是否到达 SQL、shell、HTML、URL fetch、file path、deserializer 或 agent tool 等危险 sink？
4. secrets、PII、tokens 和内部错误是否进入代码、日志、artifact 或模型上下文？
5. webhook、OAuth、redirect、upload 和 third-party callback 是否验证来源、完整性、时效与重放？
6. AI / LLM 输出是否被当作不可信输入，权限是否由代码而非 prompt 强制，tool scope、确认、token/rate/recursion limit 是否存在？
7. Critical/High 候选是否有 proof of exploitability 或可信 exploitation scenario，而不是 scanner label？

## Evidence Ladder

1. 可重复 proof of exploitability，证明未授权动作、数据暴露、注入或跨边界影响。
2. 沿 reachable path 的强静态证明，source、missing control、sink 和 impact 全部闭合。
3. 受控安全测试、dependency/workflow evidence 与明确攻击前提。
4. scanner、CVE、危险 API、缺 header 或 best practice 候选。
5. 理论威胁，没有可达路径或攻击者模型。

## Method Selection

- 从 `D1` 的 attack surface 和 trust boundary map 开始，再用 `D2` 构造 attacker scenario。
- 输入空间大或 parser/normalization 复杂时使用 `D5/D11`；已确认 seed 后才用 `D6/D12` 搜索 variants。
- supply-chain 与 workflow 权限使用 `D7`，但低分或过期依赖只是调查信号。
- 对 authentication、authorization、tenant isolation、SSRF、injection、secret handling 和 AI/LLM tool execution 做与项目相关的 focused audit。
- PoC 必须使用安全、非破坏性输入；无法实际利用时记录 proof gap，不夸大结论。

## Severity Calibration

- P0：当前环境可远程或低门槛利用，导致大规模数据泄露、任意代码执行、跨租户控制或发布链完全失陷。
- P1：存在可信 exploitation scenario，可造成显著未授权访问、敏感数据暴露、权限提升或高影响完整性破坏。
- P2：条件受限的安全缺陷、重要 defense-in-depth 缺口、缺少 regression protection。
- P3：没有当前 exploitation path 的 hardening 建议。

## Completion Gate

- release-critical flow 的 trust boundary、asset 和 attacker capability 已记录。
- 每个 P0/P1 都有 proof of exploitability 或 source-to-sink 强静态证明与明确攻击前提。
- authentication、authorization、input、secrets、data exposure、third-party 和适用的 AI / LLM 风险已评估。
- scanner/CVE 结果完成 reachability 与控制面 triage。
- 未运行的生产、账号或破坏性验证明确标记 external/deferred。

## Report Contract

```markdown
## Security Case
- Asset and trust boundary:
- Attacker capability:
- Exploitation scenario:
- Source/control/sink:
- Proof of exploitability:
- Impact and severity:
- Existing mitigations:
- External limits:
```

## Anti-Patterns

- 把 OWASP checklist 每一项都当作 finding。
- 仅凭 scanner severity、CVE 分数或危险函数名给出 P0/P1。
- 混淆 authentication 与 authorization。
- 把 system prompt 当作安全边界，或默认模型输出可信。
- Critical/High 没有 exploitation scenario、攻击前提和 impact。
