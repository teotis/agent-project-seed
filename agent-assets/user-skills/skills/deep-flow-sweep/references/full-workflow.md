# Deep Flow Sweep Full Workflow

本 reference 保留完整执行手册、profile、playbook、ledger、报告结构、常见错误和完成标准。主入口见 `../SKILL.md`。

路由语义以主入口为准：本文件中的 “hand off / escalate” 均表示生成建议与 capsule，不能自动启动另一个 architect、sweep、Deep 或 Exhaustive workflow。

## Mission

Deeply understand the project's main flows, recent changes, past intelligence, and long-term trends. Imagine where they will fail in real use, gather evidence from the widest relevant sources, rank the risks, and leave an honest analysis ledger with task packages for follow-up work.

This skill is the **flood irrigation** (大水漫灌) counterpart to the precise-irrigation skills: it trades compute and elapsed time for coverage. Use it when the user explicitly wants exhaustive breadth, is willing to spend a very large token budget, and prefers a long-running analysis pass before deciding what to fix. It is not an implementation skill: do not modify the project unless the user separately converts a specific finding into follow-up execution work.

## 默认执行强度与询问门槛

### 调用入口契约（user-invoked only）

本 skill 是 sweep 类大水漫灌深度审计，**只支持用户显式启动**，不支持 agent 主动 active 自启用：

- 必须由用户显式点名本 skill、使用 `When To Use` 中列出的触发关键词，或明确要求做主流程扫雷 / 全覆盖质量审计 / pre-release risk discovery 时，才启动本 skill。
- 其他 agent / skill 在分析、规划、调试或落地过程中，即便发现质量、稳定性或主流程风险信号，也**不得主动启用本 skill**；只能将判断写入 finding / handoff，等待用户授权。
- 不存在「partial sweep」「lightweight active 启动」之类的隐式入口。如果上下文不满足显式启动条件，应回到 systematic-debugging、ordinary code review、abstraction-architect 等更轻路径，并提示用户「如需大水漫灌质量扫雷请明确点名 deep-flow-sweep」。

### 默认执行强度

一旦满足显式启动条件，调用即视为授权执行本 skill 在当前环境和既有安全边界内的完整原生工作流。默认全力执行：使用 Exhaustive envelope、`balanced` 基线、全部适用风险面，并在有收益且工具可用时自动采用并发或长期分析形态；只有用户明确要求降级、缩小范围或聚焦时，才降低预算、跳过适用维度或收窄对象。

可从当前 workspace、用户消息、文件、运行环境和已有上下文合理推断的 scope、target、profiles、budget、执行形态和输出方式，直接推断并记录，不要询问用户。信息不足但仍能继续时，将其写入 `assumptions / unknowns / coverage debt`，并继续完成其余可执行工作。

只有完全无法识别分析目标，或下一步需要用户未授权的 implementation、不可逆操作、账号状态变更、发布或推送时，才中断询问。并发分析、生成报告、运行只读或常规验证、选择默认 profiles / budget 不需要额外确认。

## Output Language

私有版默认使用中文交付。保留必要英文关键词、技能名、命令、文件名、代码标识、指标名、severity/confidence/disposition、Task Package Contract、profile 名称和原始证据名称。

私有版正式报告的可见正文、章节标题、表格字段、任务包说明、最终回复和 HTML UI 文案默认使用中文。不要因为本 SKILL.md、reference 文件、工具输出或公开英文版本包含英文，就把主报告、发现卡片、状态标签、按钮或说明性段落整体写成英文。除非用户明确要求英文、目标交付物面向英文读者，或正在同步/审计公开英文版本，才切换为英文；切换时在报告 scope 中记录语言选择。

## When To Use

Use this skill when the user asks for signals like:

- "全面梳理", "深度排查", "主流程", "充分思考以后完善", "大水漫灌", "全覆盖"
- "预测性发现问题", "实测前排雷", "高预算覆盖", "极致覆盖", "仅分析不修复"
- "pre-release risk discovery", "pre-merge sweep", "main-flow QA", "find issues before testing"
- "近期改动落地是否恰当", "结合历史会话", "长期趋势", "架构漂移"
- "goal 模式", "协同 goal", "任务包拆分", "并发 launcher", "半小时以上分析"
- a broad request to understand the project, simulate failure cases, and improve reliability before real-world validation

Do not use this skill for:

- one known bug with reproduction steps; use a systematic debugging workflow instead;
- ordinary code review of a diff only;
- narrow architecture analysis where the user wants a single structural decision;
- cosmetic cleanup, naming preferences, or speculative rewrites;
- direct code fixing, PR cleanup, or implementation unless the user explicitly asks for a separate follow-up after the sweep;
- release claims that depend on unavailable external systems, physical devices, private accounts, or human-only judgment.

## Budget Envelopes

Budget tiers define the maximum affordable search space, not a fixed checklist. **Default envelope is Exhaustive** unless the user asks for a lighter pass, but methods are still selected by risk signal, completion confidence, and expected information gain.

| Envelope | Trigger keywords | Guaranteed baseline | Optional capacity | Typical execution envelope |
|---|---|---|---|---|
| **Normal** | "轻量排查", "基础梳理", "快速扫雷" | lightweight probe + critical flow map + highest-risk scenarios | one or two low/medium-cost triggered weapons | one focused evidence wave; stop condition and coverage debt recorded |
| **Deep** | "深度", "充分", "全面", "高预算" | Normal baseline + Git/memory context + root-cause evidence | state models, fault injection, property checks, variant search, supply-chain review | multiple evidence waves until key unknowns close or information gain saturates |
| **Exhaustive** | 默认, "极致覆盖", "大水漫灌", "全覆盖", "极致" | Deep baseline across release-critical flows | mutation testing, fuzz introspection, cross-repository variants, long-term drift, concurrent independent probes | long-running or concurrent analysis with explicit goal/launcher authorization, provenance gates, and stop condition |

Use any additional method that is likely to finish within the envelope and materially improve discovery or confidence. Do not run heavy tools solely because budget remains. Read `references/analysis-arsenal.md` before selecting methods.

## Focus Profiles

Default to `balanced`. Map user emphasis to one or two composable profiles:

| User emphasis | Profile | Required playbook |
|---|---|---|
| 默认充分发挥 | `balanced` | `references/profile-balanced.md` |
| 主功能、主流程、UI/用户路径 | `main-flow` | `references/profile-main-flow.md` |
| 稳定性、恢复、并发、状态一致性 | `reliability` | `references/profile-reliability.md` |
| 性能、延迟、内存、CPU、电量、吞吐 | `performance` | `references/profile-performance.md` |
| 安全、权限、信任边界、漏洞、AI/LLM 风险 | `security` | `references/profile-security.md` |
| 日志、诊断、错误信息、告警 | `observability` | `references/profile-observability.md` |
| 测试覆盖、测试质量、flaky、回归保护 | `test-effectiveness` | `references/profile-test-effectiveness.md` |
| 项目治理、CI、发布、文档、agent parity、产物来源 | `project-governance` | `references/profile-project-governance.md` |
| 需求落实、计划/会话符合度、验收条件 | `requirement-conformance` |

**Focus does not remove baseline coverage.** Main-flow reachability, reliability, recovery, evidence quality, and analysis-only constraints always remain active. Read `references/focus-profiles.md` for routing and allocation, then read every required playbook for the selected common profile(s). The playbook completion gate is part of the sweep completion standard, not optional advice.

## Project Archetype Routing

Before selecting detailed checks, build a short **Project Risk Profile**. Archetype signals are priors, not conclusions: they raise or lower inspection priority, but every finding still needs reachable-flow evidence and every skipped check needs an applicability reason.

Record an **Applicability Disposition** for each triggered risk family:

| Disposition | Meaning |
|---|---|
| `applicable` | The project has a concrete surface where this check can be evaluated. |
| `possibly applicable` | Signals exist, but more code, config, account, device, or runtime context is needed. |
| `not applicable` | The surface is absent, and the reason is recorded. |
| `deferred` | The surface exists, but required credentials, devices, production data, or authorization are unavailable. |
| `untriaged` | Budget or scope prevented a confident applicability decision. |

Use archetypes to route attention without hard-coding project answers:

| Archetype signal | Triggered risk families |
|---|---|
| **Web / SaaS / API** | authentication, authorization, tenant isolation, API contracts, rate limits, CSRF/XSS/SSRF/injection, session/cookie handling, deployment and secret boundaries |
| **Mobile / Android / Device** | permissions, lifecycle transitions, device/OS variance, camera/media/storage paths, background work, release build behavior, battery/memory/latency, crash recovery |
| **Agent / Tooling / Automation** | workspace mutation boundaries, command/documentation parity, approval and sandbox assumptions, resumability, report provenance, prompt/skill/config drift |
| **Library / Framework** | public API compatibility, versioning, error contracts, examples/docs parity, integration surfaces, dependency constraints |
| **Public release / split repository** | private/public sync, tracked files, identity/secrets, generated artifacts, LICENSE/README parity, nested-repo state |

When multiple archetypes apply, compose them. Do not let a familiar archetype suppress unusual flows discovered in the actual code.

## Positioning: Cross-Skill Integration

Deep Flow Sweep is the broadest net. It may borrow thinking patterns from specialized analysis skills, then package the right follow-up path instead of fixing directly.

| Finding pattern | Escalate to | Handoff signal |
|---|---|---|
| Same class of bug found or fixed >3 times; repeated adapters/representations; scattered state or lifecycle logic | `abstraction-architect` | The pattern suggests a missing invariant, not missing guards |
| User-facing quality issues; default output not decision-useful; reward misalignment in tools/workflows | `product-sense-refiner` | The main flow is technically correct but the user still makes wrong decisions |
| Fixes would require dual-track compatibility; legacy migration; organizational approval; gradual rollout | `renewal-architect` | The risk is clear but the adoption path needs pilot cells, rollback, and adoption economics |
| Many independent work items discovered; suitable for parallel execution | Claude Code Agent View / Dynamic Workflows, or `agent-orchestration-planner` | Use official Claude concurrency for independent probes; use the planner when execution needs a durable DAG, status ledger, worktree/branch policy, or final integration |
| Past session findings remain unfixed; recurring patterns across sessions | Re-run sweep with Cross-Session Intelligence (Step 5) | The current sweep is a follow-up to verify past recommendations |

Conversely, when another skill finds scattered evidence of concrete bugs, missing guards, weak tests, or release risk but the true blast radius is unknown, it should hand off to deep-flow-sweep for exhaustive analysis and prioritization.

## Operating Principles

1. **Coverage over elegance.** In flood-irrigation mode, it is better to find 15 P2 issues than to perfectly describe 3 P0s. Breadth is the point.
2. **Main flows first, then radiate.** Spend most effort on the user-visible or release-critical flows. Expand outward as budget permits.
3. **Evidence before claims.** Each finding needs a concrete risk, code reference, failing or missing scenario, observed behavior, weak test, log, build failure, contract mismatch, or credible historical signal.
4. **Predict failures, then test the prediction.** A useful imagined scenario should imply an observable check: a test, command, runtime probe, browser/device path, or manual gate.
5. **Analyze, do not repair.** Convert clear bugs into evidence-backed task packages. Convert broad redesign pressure into cross-skill escalation recommendations.
6. **Verify what can be verified.** Do not imply that manual, device, account, production, or third-party checks passed unless they actually ran.
7. **Respect the worktree.** Read current status before analysis. Never overwrite unrelated user changes.
8. **Negative results are results.** If a sweep finds few or no issues, report honestly. A clean bill of health is valuable information, not a failure of the sweep.
9. **Past intelligence is evidence.** Before building the flow map from scratch, query relevant session history, memory, and prior findings.
10. **Budget buys optionality, not mandatory work.** Select each additional method because it closes a meaningful evidence gap.
11. **Reconnaissance is not proof.** Regex, inventories, scanners, and scores nominate areas to inspect; they do not independently establish a finding.

## Workflow

### Analysis-Only Mode Latch

Invoking this skill latches the run into analysis-only mode. Declare an **analysis artifact root** before the first write, preferably `reports/deep-flow-sweep/<run_id>/` when repository conventions permit.

- The run **must not modify product source**, tests, configuration, migrations, generated product assets, dependency locks, or Git history.
- Allowed writes are limited to the declared analysis artifact root: reports, manifests, sub-ledgers, evidence indexes, and task packages.
- A severe finding, task package, user urgency, or remaining budget does not unlock implementation.
- Editing project files requires **new explicit user authorization** after the analysis result is presented. Route that follow-up through the appropriate implementation or debugging skill.

### 0. Establish Scope And Budget

Infer the sweep target from the user request and repository context:

- target branch, current diff, project, feature area, release path, or "whole project";
- expected main flows and any explicitly named workflows;
- available budget envelope: default to Exhaustive; downgrade to Deep or Normal only if the user explicitly requests a lighter sweep;
- selected focus profile(s): default `balanced`; load `references/focus-profiles.md` for named emphasis;
- project risk profile: archetype signals, triggered risk families, and Applicability Disposition for checks that materially affect coverage;
- required playbook(s), their mandatory evidence, and their completion gates;
- whether concurrent execution is useful for independent sub-sweeps; default to using it when available and materially beneficial unless the user narrows the run.

Before writing findings, inspect:

- repository instructions (`AGENTS.md`, `CLAUDE.md`, `README`, docs);
- git status and existing uncommitted changes;
- project type, test commands, build commands, launch commands, and CI hints;
- recent plans, issues, TODOs, or project-specific validation notes if present;
- (Deep/Exhaustive) past session memory for this project;
- (Exhaustive) multi-repository boundaries and nested repo status.

Create a decision ledger before expanding:

- current highest-value unknown;
- candidate weapon from `references/analysis-arsenal.md`;
- cost and completion confidence;
- expected information gain;
- run/defer/skip decision and resulting artifact.

Create a run manifest in the analysis artifact root:

- `run_id`, `git_sha`, `dirty_state`, `scope`, selected profiles, budget envelope;
- project archetype signals, triggered risk families, and deferred or untriaged applicability decisions;
- `source_agent`, `started_at`, `finished_at`, `artifact_path`;
- tool availability, external blockers, and parent run for concurrent sub-ledgers.

Use the manifest for provenance and freshness checks. Reject or quarantine a sub-ledger when its `run_id`, `git_sha`, scope, or parent run does not match, or when its artifact predates the current run.

### 0.5 Coverage Matrix Before Findings

Before ranking issues or writing task packages, produce a **Coverage Matrix Before Findings** in the analysis artifact root or report draft. It is the local investigation kernel for this skill and must stay self-contained when the skill is copied alone.

For cross-skill handoff, treat each matrix row as an evidence-ledger producer/consumer entry: preserve a stable `evidence_id`, type, source artifact, observation, confidence, and consumed finding/package ID. Reuse incoming IDs and append new evidence instead of rewriting prior observations.

Minimum matrix columns:

- flow or risk family: main flow, failure/recovery, trust boundary, environment path, release path, history, verification, or focus profile;
- reachable path: trigger, setup, key files/symbols, state/data boundary, success signal, and failure surface;
- artifacts inspected: docs, code, tests, commands, logs, screenshots, commits, reports, configs, or generated outputs;
- evidence status: observed, reproduced, measured, inferred, unavailable, deferred;
- critical unknowns and coverage debt;
- next weapon decision and expected information gain.

**Path Completion Gate**: A P0/P1 finding, broad reliability claim, or task package needs a completed path from user/release trigger through relevant files and boundaries to concrete failure scenario, direct evidence, user/release impact, and verification or falsification route. If that path is incomplete, keep the item as `investigate`, `defer`, or `coverage_debt`.

**Finding permission** is granted only after the coverage matrix plus direct evidence can explain why the issue threatens a reachable flow, recovery path, trust boundary, release boundary, or user-visible result. Do not promote scanner matches, historical labels, weak logs, missing tests, or architectural taste into findings by themselves.

### 0.6 Decision-First Output

The investigation machine is internal scaffolding. Use **Decision-First Output** for the report: lead with the decision surface, then preserve full fidelity in structured ledgers, task packages, or appendix.

- **Evidence Compression Gate**: evidence enters the main narrative only when it changes severity, confidence, disposition, release/user impact, verification route, or escalation. Other evidence stays in appendix, evidence ledger, or collapsible HTML details.
- **Decision Surface Cap**: default the main narrative to 3-5 core risks, failure families, or release/user-impact findings. This cap limits the reader-facing decision surface, not the investigation inventory.
- **Critical findings are not capped**: every P0/P1, security/trust boundary issue, data-loss risk, release blocker, or unusable critical flow must appear in the main report even if the cap is exceeded.
- **Cluster before appendix**: when many findings exist, cluster by failure family, reachable flow, trust boundary, or recovery mechanism before moving lower-priority duplicate evidence to appendix.
- **Delete-The-Scaffold Rule**: do not expand the full Coverage Matrix, Flow Map, scenario ledger, or weapon ledger in the main narrative by default. Expand them only when coverage is disputed, evidence is insufficient, the result is `coverage_debt`, or the user asks to audit the process.
- **One-Screen Handoff Capsule**: provide a compact handoff for external agents: finding/package ID, evidence IDs, severity, confidence, disposition, next action, blocked/deferred reason, verification command/artifact, and owner skill.

For very large budgets, recommend one of these execution shapes:

- **Goal mode** when the user wants Codex to continue across a long analysis budget and resume naturally after context compaction.
- **Task package split** when the result should become a set of human- or agent-executable follow-up work items.
- **Concurrent launcher** when the flow map exposes independent dimensions that can be audited in parallel for 30+ minutes.

### 1. Build The Flow Map

Identify the main flows in concrete terms:

Start with the lightweight reconnaissance probe when Python is available:

```bash
python3 <skill-dir>/scripts/flow_probe.py <root> --pretty
```

Resolve `<skill-dir>` to the directory containing this `SKILL.md`. Its entry-point, boundary, and risk matches are candidates only. Confirm important surfaces by tracing real code, tests, configuration, and runtime behavior.

- entry points: CLI commands, app screens, HTTP routes, background jobs, public APIs, build/release scripts;
- lifecycle: initialize, configure, execute, persist, recover, teardown;
- data path: inputs, validation, transformation, storage, output, side effects;
- environment path: local, CI, dev server, emulator/device, production-like dependencies;
- ownership boundaries: modules, packages, generated files, nested repos, public/private split.

Write a short internal map before ranking findings. For each main flow, record:

- start trigger;
- key files and symbols;
- expected success signal;
- likely failure surfaces;
- available verification commands.

### 2. Generate Failure Scenarios

For each main flow, traverse at least these scenario classes when relevant:

| Class | Questions |
|---|---|
| Happy path | Does the documented main path actually run from a clean checkout? |
| Empty/minimal input | What happens with no config, no data, first run, missing cache, empty list, or no-op input? |
| Invalid input | Are bad inputs rejected at the right boundary with useful errors? |
| State transition | Can lifecycle states be skipped, repeated, resumed, cancelled, or retried safely? |
| Concurrency/timing | Are async work, background jobs, UI events, file writes, and retries race-prone? |
| Environment drift | Do local, CI, device, browser, OS, path, permission, and dependency differences change behavior? |
| External dependency | What fails when network, account, API, database, filesystem, or hardware assumptions are absent? |
| Regression surface | Which recent changes, weak tests, or duplicated contracts make a future break likely? |
| Observability | Will a failure be diagnosable from logs, errors, status files, screenshots, or artifacts? |
| Recovery | After failure, can the user retry without cleanup, data loss, or corrupted state? |
| **Agent/automation surface** | Are there user-accessible operations that an agent cannot perform? Does the project violate agent-native parity? |
| **Cross-cutting consistency** | Do error handling, logging, auth, input validation, and configuration patterns stay consistent across modules? |

Prefer scenarios that would cause real validation failure, data corruption, user-visible breakage, nondeterminism, or blocked release work.

### 3. Select Weapons And Run The Evidence Sweep

Use `references/analysis-arsenal.md` to choose methods for the current flow risks and evidence gaps. Baseline flow mapping and scenarios are required; stateful models, fault injection, property testing, variant search, supply-chain checks, mutation testing, fuzzing, and cross-repository analysis require their documented trigger.

After each evidence wave, record:

- new P0/P1 candidates;
- existing findings whose evidence became materially stronger or weaker;
- critical unknowns closed;
- release-critical flows still unscanned;
- whether another weapon is likely to change the conclusion.

Two consecutive low-information waves trigger a stop review, not an automatic stop. Continue only when remaining budget plus an unscanned critical flow or trust boundary is likely to change severity, confidence, or disposition; otherwise stop with explicit coverage debt and residual unknowns.

Gather evidence with the cheapest reliable probes first. The evidence source pool expands with budget envelope:

**All tiers:**
- run focused existing tests, builds, linters, type checks, or scripts that cover the main flows;
- read tests around the flow and identify missing assertions for failure scenarios;
- search for TODO/FIXME, brittle error handling, broad catches, ignored results, sleeps/timeouts, unchecked nulls, duplicated state names, and path assumptions;
- if UI or local web behavior is in scope, start the app and inspect with a browser when feasible;
- if mobile/device/hardware behavior is in scope, produce install/build/log artifacts and mark real-device checks as external unless actually available.

**Deep/Exhaustive only:**
- security and dependency signals: when triggered, load `references/profile-security.md`; do not substitute a generic checklist for trust-boundary and exploitability evidence;
- diagnostic signals: when triggered, load `references/profile-observability.md`; do not infer diagnosability from the mere presence of logs;
- documentation parity: do AGENTS.md, CLAUDE.md, README, and inline docs match actual code behavior and available commands?
- agent-native parity: can an agent perform the same operations a human user can, or are there tool gaps, approval gaps, or environment assumptions that block agents?

When a command fails, decide whether it reveals a product defect, environment gap, or unavailable capability. Do not blindly patch environment-only failures into code.

### 4. Git Archaeology Sweep (Deep/Exhaustive)

When budget is Deep or higher, audit recent changes for landing appropriateness:

- **Intent recovery**: Load `references/evidence-decision-model.md` and trace requirement/task source → test oracle → implementation → runtime evidence before judging whether a change landed correctly.
- **Intent vs. effect**: For each recent commit (default: last 20-30), check whether the stated change matches the actual diff. Are there unrelated changes bundled in? Does the commit message describe the effect accurately?
- **Compensation patterns**: Look for sequences where commit B fixes a bug introduced by commit A, especially if both are by the same author in a short window. These signal insufficient pre-commit validation.
- **Silent regression risk**: For each changed file, check whether its callers, dependents, or configuration consumers were updated accordingly. A one-sided change is a regression time bomb.
- **Invariant drift**: Compare recent changes against declared project invariants (in AGENTS.md, architecture docs, type boundaries). Has any invariant been silently relaxed or broken?
- **Worktree hygiene**: Check for unintended file additions (IDE config, temp files, AppleDouble, Python cache) in recent commits.
- **Test co-evolution**: For each functional change, verify that corresponding tests were added or updated. A production change without test change is a coverage gap.

Report findings in the ledger with commit SHAs as evidence.

### 5. Cross-Session Intelligence (Deep/Exhaustive)

When budget is Deep or higher, query past session memory before finalizing the finding list:

- Search for prior deep-flow-sweep findings, architecture reviews, or bug reports about this project.
- For each past P0/P1 finding, verify whether it was actually fixed and re-rank it from current evidence. **Past severity is not inherited automatically.**
- Identify recurring issue patterns: if the same class of problem appears across multiple sessions, it signals a process, abstraction, or renewal gap (escalate to `abstraction-architect` or `renewal-architect` when the evidence supports that route).
- Cross-reference past recommendations with current code state. If a past recommendation was ignored but the code evolved, check whether the new code made the recommendation obsolete or more urgent.

Use available memory or session-history tools to gather past intelligence, such as `ce-sessions`, `memory_smart_search`, or `memory_recall` when present. If no session tool is available, search local docs, reports, run ledgers, issues, and commit messages instead. Tag findings sourced from history distinctly in the ledger.

### 6. Rank Findings

Classify every candidate before packaging:

Load `references/evidence-decision-model.md`. Record **Severity, Confidence, and Disposition** separately so impact, evidence strength, and next action do not collapse into one label.

#### Severity And Evidence Gate

P0/P1 require **direct evidence** tied to a reachable flow. Scanner matches, code smell, historical labels, weak logs, vague commits, missing coverage, or architectural taste cannot establish P0/P1 alone.

| Rank | Evidence gate | Default Action |
|---|---|---|
| P0 | observed or deterministically demonstrated data loss, security exposure, release-blocking breakage, or unusable critical flow | stop expanding and report urgently |
| P1 | reproducible likely user failure, broken enforced contract, unrecoverable state, or strong static proof on a reachable critical path | package as high-priority follow-up |
| P2 | credible risk with partial evidence: edge case, weak diagnostic, brittle recovery, missing regression protection, documentation drift | report with falsification path |
| P3 | maintainability or polish issue with indirect quality value | include only if it clarifies a larger pattern |

Discard or defer findings that are only style preferences, speculative architecture taste, broad rewrites, or unrelated cleanup.

When 3 or more findings share the same root cause pattern, stop classifying individually and escalate to the appropriate specialized skill (see Positioning table).

### Task Package Contract And Falsification

Before emitting follow-up work, convert each actionable finding into the shared **Task Package Contract** in `docs/contracts/task-package-contract.md`. Include the contract fields in the Markdown report, or in a fenced YAML block, so manual executors or `agent-orchestration-planner` can consume the package without reinterpreting prose.

Each task package must include a **Falsification Ledger**: counter-evidence checked, false-positive risk, style-preference guard, verification gap, and keep/downgrade/defer/drop decision. Do not package a P0/P1 from scanner output, historical severity, weak logs, or architectural taste unless the ledger preserves direct current evidence tied to a reachable flow.

Include the finding's Severity, Confidence, and Disposition plus any missing evidence named by the decision model.

Each package also starts an **Outcome Replay** stub naming the evidence that should be collected after execution. When a later run reports landed, blocked, rejected, false-positive, capability-gap, or verification-failed outcomes, fold that replay into future evals or skill contract tests.

When a structured package block exists, run:

```bash
rtk python3 scripts/task_package_validator.py <report-or-package-file>
```

This validator is a repo-local deterministic gate, not a hard dependency of a standalone skill copy. If the skill is copied without the repository `scripts/` directory or the script is unavailable, keep the Task Package Contract fields, Falsification Ledger, and Outcome Replay in the report, mark deterministic package validation as `missing evidence` / package contract gap, and require manual structural review before handoff or orchestration.

### 7. Produce Task Packages And Escalation Briefs

Do not edit project files as part of this skill. Convert findings into precise packages that a later implementation pass can pick up.

Each task package should include:

- every required field from the **Task Package Contract**;
- problem statement and severity;
- confidence and disposition;
- evidence: files, commands, logs, screenshots, commits, session references, or missing tests;
- expected user or release impact;
- proposed verification gate;
- likely owner or module boundary;
- estimated execution shape: single patch, test-first bugfix, architecture analysis, renewal plan, or parallel subtask;
- dependencies, blocked checks, and rollback considerations if applicable.

Task packages may recommend these follow-up actions, but should not perform them:

- missing validation or guardrails at clear boundaries;
- incorrect state handling, retry behavior, cleanup, or error propagation;
- missing focused tests for high-risk scenarios;
- diagnostics that make main-flow failure actionable;
- script/doc corrections needed to make validation commands truthful;
- removal of dead or contradictory behavior only when proven unused or harmful.

When a finding is too broad for a task package, write an escalation brief instead:

- `abstraction-architect`: missing invariant, duplicated representation, scattered lifecycle state.
- `product-sense-refiner`: technically correct flow still leads to poor user decisions.
- `renewal-architect`: legacy migration, compatibility, rollout economics.
- Claude Code Agent View / Dynamic Workflows: many independent analysis probes that need only native dispatch and result tracking.
- `agent-orchestration-planner`: implementation packages that need dependencies, durable coordinator state, worktree/branch policy, retries, or final integration.

### 8. Verification Ledger

Run verification proportional to the analysis claims and risk:

- focused tests that confirm or falsify predicted failure scenarios;
- broader tests/builds for shared contracts, lifecycle logic, generated files, or release scripts;
- static checks/lint/type checks when available and relevant;
- browser/device/manual checks only when the environment supports them.

End with a concise ledger:

```markdown
## Sweep Summary
- Run ID and manifest: <run_id, path>
- Budget tier: <Normal|Deep|Exhaustive>
- Focus profiles: <profiles and allocation>
- Project Risk Profile: <archetypes, triggered risk families, applicability disposition summary>
- Main flows inspected: <count and names>
- Total findings: <severity counts; confidence counts; disposition counts>
- Task packages produced: <count>
- Escalations recommended: <skill names>
- Weapons run: <weapon IDs and reasons>
- Weapons skipped/deferred: <weapon IDs and reasons>
- Stop reason: <coverage complete|information gain saturated|budget boundary|external blocker>

## Flow Map
- <main flow>: <entry, critical files, success signal>

## Issues Found
- [P1/high/package] <issue>: <evidence and file reference>
- [P2/medium/investigate] <issue> (memory): <past session reference, current state>

## Git Archaeology Findings (Deep+)
- <commit SHA>: <finding>

## Cross-Session Findings (Deep+)
- <past finding reference>: <current status>

## Task Packages
- [P1] <package title>: <Task Package Contract fields, Falsification Ledger, Outcome Replay stub>

## Verification
- `<command>`: <pass/fail and key output>

## External Or Deferred Checks
- <manual/device/account/production check not run and why>

## Residual Risks & Escalations
- <remaining risk or design pressure>
- Recommended escalation: <skill> because <reason>
```

If no concrete findings survive evidence checks, say so clearly and provide the strongest predicted failure scenarios plus verification recommendations. A clean sweep with no findings is a valid and valuable outcome.

## Concurrent Execution Model (Exhaustive)

When the sweep scope spans multiple independent modules, repositories, or dimension classes, split the work with Claude Code's official Agent View or Dynamic Workflows:

**Parallelizable activities:**
- Independent module main-flow sweeps (different packages, services, or apps in the same repo)
- Independent repository sweeps (nested repos, submodules, public/private split)
- Independent scenario class sweeps (security audit, dependency audit, documentation parity can run in parallel)
- Independent evidence probes (linting, test running, type checking against different modules)

**Must remain sequential:**
- Flow Map construction (must complete before scenario generation)
- Scenario generation (must complete before evidence sweep against those scenarios)
- Ranking and deduplication (must complete before task packaging)
- Final synthesis (must merge evidence, conflicts, and blocked checks in the main session)

**Execution pattern:**
1. Build the full Flow Map and scenario plan in the main session.
2. Create the parent run manifest, then split independent tasks into the same run directory.
3. Use Agent View for manually supervised independent sessions, or Dynamic Workflows when Claude should generate and track a bounded concurrent workflow. Use `agent-orchestration-planner` only when the run needs a project-owned execution contract with DAG scheduling, durable status, worktree/branch policy, retries, and final integration.
4. Each agent produces a sub-ledger carrying the parent `run_id`, current `git_sha`, exact scope, timestamps, `source_agent`, and `artifact_path`.
5. Verify provenance and freshness before merging. Do not reuse an old report merely because its filename or topic looks relevant.
6. Merge accepted sub-ledgers, deduplicate findings, resolve conflicts, and produce task packages from the main session.

Launch concurrent analysis automatically when it is available, materially beneficial, and remains inside the analysis-only boundary. Do not request a separate confirmation.

## Long-Term Trend Analysis (Exhaustive)

When budget is Exhaustive, supplement the snapshot analysis with trajectory data:

- **Complexity trends**: Use git history to check whether file sizes, cyclomatic complexity, coupling density, and test-to-code ratios are improving or degrading over time.
- **Fix-mode trends**: Classify recent commits as preventive (adding guards/tests for anticipated issues), corrective (fixing reported bugs), or compensatory (fixing bugs introduced by recent changes). A rising compensatory ratio signals process degradation.
- **Hotspot migration**: Track which files/directories receive the most changes over the last 6-12 months. Are hotspots moving toward or away from critical-path code?
- **Agent intervention drift**: If session history is available, check whether certain flows require more agent manual intervention over time — a signal of growing automation gaps.

Report trends as a separate section in the ledger. Trends are observational, not prescriptive; they inform the residual risks assessment.

## Stop Conditions

Stop or report instead of continuing when:

- the user asks to convert the sweep into implementation work; pause and confirm the follow-up mode or skill;
- a recommended action would require product approval or broad architecture migration;
- the main risk depends on unavailable credentials, hardware, accounts, or production data;
- commands repeatedly fail due to environment setup outside the project;
- unrelated user changes prevent reliable analysis of the target scope;
- the sweep finds many unrelated defects and needs prioritization;
- two consecutive low-information waves trigger a stop review, and remaining budget is better spent synthesizing because no critical flow or trust boundary remains likely to change severity, confidence, or disposition;
- the token budget is approaching exhaustion but critical flows remain uninspected;
- (Concurrent mode) a background agent returns results that invalidate the shared Flow Map assumption.

## Completion Standard

A deep flow sweep is complete only when:

- the budget tier and scope are explicitly stated;
- the focus profiles and analysis artifact root are explicitly stated;
- the project risk profile lists archetype signals, triggered risk families, and applicability dispositions for important skipped or deferred checks;
- every selected common profile passes the completion gate in its required playbook;
- the run manifest passes provenance and freshness checks;
- the selected weapons, skipped heavy methods, and stop reason are recorded;
- Coverage Matrix Before Findings is recorded before findings, and the Path Completion Gate grants or denies finding permission for P0/P1 claims and task packages;
- the report uses Decision-First Output, Evidence Compression Gate, Decision Surface Cap, Cluster before appendix, Delete-The-Scaffold Rule, and One-Screen Handoff Capsule without hiding critical findings;
- the main flows inspected are named;
- high-risk failure scenarios were considered across all budget-appropriate classes;
- (Deep+) Git archaeology findings are reported with commit evidence;
- (Deep+) Cross-session intelligence is queried and findings are cross-referenced;
- (Exhaustive) Long-term trends and architecture drift indicators are assessed;
- every finding has evidence, severity, and an explicit verification or falsification path;
- every proposed follow-up is packaged as a task, escalation brief, or deferred check;
- every unverified claim is explicitly marked as external, deferred, or not run;
- cross-skill escalations are recommended when the pattern exceeds direct task packaging;
- unrelated cleanup is avoided;
- the final answer helps the user decide whether the project is safer to test or release;
- if the sweep found few or no issues, this is stated honestly as a positive outcome ("clean bill of health"), not padded with trivialities.

## Output Options

正式 sweep 默认 `paired`，即 Markdown source report + HTML review surface；只有用户明确要求 `chat-only` / `no-files` / 快速聊天结论时才降级为聊天输出，并必须记录 coverage debt。维护时与 `docs/contracts/output-modes.md` 同步，但运行时不依赖该文件。

| Budget | Default output | Enhanced output |
|---|---|---|
| Normal | Markdown source report + interactive HTML report using `reviewable-html-report` | Task packages when findings are actionable |
| Deep | Markdown source report + interactive HTML report using `reviewable-html-report` | Sub-ledgers and task packages |
| Exhaustive | Markdown source report + interactive HTML report | Sub-ledgers + concurrent launch manifest + task packages + escalation brief |

## Report Delivery Contract

- **Markdown is the source report**: generate `deep_flow_sweep_report_{YYYYMMDD}_{HHMM}.md` for formal sweeps. It must contain the sweep summary, flow map, scenarios, issues, task packages, verification ledger, external/deferred checks, and escalations in a compact shape suitable for follow-up agents.
- **HTML is the review surface**: generate `deep_flow_sweep_report_{YYYYMMDD}_{HHMM}.html` from the same issue IDs, evidence, severity labels, task package IDs, and residual risks for every formal sweep. It must include a clickable section index with stable section IDs, and should include clickable finding-to-code navigation, color-coded severity, and collapsible sections for each dimension.
- **No split conclusions**: HTML may visualize and filter, but it must not introduce judgments absent from Markdown.
- **Package validation**: when task packages are emitted as YAML/JSON or fenced structured blocks, run `rtk python3 scripts/task_package_validator.py <markdown-report>` and report failures as package contract gaps. If the repo-local validator is unavailable, mark deterministic validation as `missing evidence`, preserve the structured contract fields, and require manual structural review before handoff.
- **Parity check**: when both files exist, run `python3 <skill-dir>/scripts/report_pair_validator.py <markdown-report> <html-report>` to verify that structured finding IDs such as `DFS-*` and task IDs such as `TP-*` appear in both outputs.
- **HTML preview**: provide the report path and clickable `file://` URL by default. Active browser opening is optional preview behavior only when the user asks or the environment is clearly GUI-capable.
- **Fallback**: if HTML cannot be generated or opened, still deliver Markdown and state the limitation.

Include timestamp to prevent overwrites across multiple runs. Use the `reviewable-html-report` capability for shared report mechanics; repo-local `skills/reviewable-html-report/references/report_base.md` is an optional enhancement, not a standalone dependency. If that capability is unavailable, use `references/fallback.html` for self-contained static HTML with TOC, stable section IDs, evidence appendix, Mermaid source fallback, and non-persistent feedback.

## Common Mistakes

- Editing code during the sweep instead of producing evidence-backed task packages.
- Treating a focus profile as permission to ignore baseline main-flow or reliability coverage.
- Treating archetype routing as a fixed checklist or as proof that a risk exists before tracing the actual project surface.
- Continuing into fixes after the report without new explicit user authorization.
- Inheriting P0/P1 from a historical report without current direct evidence.
- Merging stale concurrent artifacts without matching run manifest fields.
- Treating the skill as a normal review when the user wants high-budget flood irrigation.
- Treating Exhaustive as an obligation to run every heavy tool despite weak triggers or insufficient time to interpret results.
- Promoting probe or scanner matches directly into findings without tracing the real flow.
- Running a Deep sweep but skipping Git archaeology or memory cross-reference.
- Launching concurrent agents without a shared Flow Map — each agent drifts and findings become incomparable.
- Claiming a sweep is "complete" when critical flows were never mapped.
- Padding the ledger with trivialities when the project is genuinely in good shape.
- Using flood-irrigation mode when a precise-irrigation skill would be more appropriate.
- Ignoring past session findings — the same bug found twice is a process failure, not two wins.
