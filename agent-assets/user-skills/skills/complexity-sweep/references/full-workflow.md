# Complexity Sweep Full Workflow

本 reference 保留完整执行手册、三层扫描规则、ledger、报告结构、常见错误和完成标准。主入口见 `../SKILL.md`。

路由语义以主入口为准：本文件中的 “hand off / escalate” 均表示生成建议与 capsule，不能自动启动另一个 architect、sweep、Deep 或 Exhaustive workflow。

## Mission

Deeply scan a codebase for inefficient structures, unnecessarily complex designs, and bloated code sections at three levels — micro (function/class), meso (module/package), and macro (architecture) — gather concrete evidence for every finding, rank by severity, and produce simplification task packages and escalation briefs. Never modify code directly.

This skill is the **complexity-focused counterpart** to `deep-flow-sweep`: it trades breadth of dimensions for depth on a single dimension — code complexity. Where deep-flow-sweep audits main flows, security, dependencies, git history, and agent surface all at once, complexity-sweep drills exclusively into structural and design complexity, going deeper on this one axis than any multi-dimensional sweep could afford.

## 默认执行强度与询问门槛

### 调用入口契约（user-invoked only）

本 skill 是 sweep 类深度审计，**只支持用户显式启动**，不支持 agent 主动 active 自启用：

- 必须由用户显式点名本 skill、使用 `When To Use` 中列出的触发关键词，或明确要求做复杂度审计 / 简化扫雷 / 全覆盖结构扫描时，才启动本 skill。
- 其他 agent / skill 在分析、规划、调试或落地过程中，即便发现复杂度信号，也**不得主动启用本 skill**；只能将判断写入 finding / handoff，等待用户授权。
- 不存在「partial sweep」「lightweight active 启动」之类的隐式入口。如果上下文不满足显式启动条件，应回到普通 code review、systematic-debugging、abstraction-architect 等更轻路径，并提示用户「如需复杂度扫雷请明确点名 complexity-sweep」。

### 默认执行强度

一旦满足显式启动条件，调用即视为授权执行本 skill 在当前环境和既有安全边界内的完整原生工作流。默认全力执行：使用 Exhaustive envelope、覆盖 micro / meso / macro 全部适用层级，并在有收益且工具可用时自动采用并发或长期分析形态；只有用户明确要求降级、缩小范围或聚焦时，才降低预算、跳过适用层级或收窄对象。

可从当前 workspace、用户消息、文件和已有上下文合理推断的 scope、target、budget、执行形态和输出方式，直接推断并记录，不要询问用户。信息不足但仍能继续时，将其写入 `assumptions / unknowns / coverage debt`，并继续完成其余可执行工作。

只有完全无法识别分析目标，或下一步需要用户未授权的 implementation、不可逆操作、账号状态变更、发布或推送时，才中断询问。并发分析、生成报告、运行只读或常规验证、选择默认 budget 不需要额外确认。

## Output Language

私有版默认使用中文交付。保留必要英文关键词、技能名、命令、文件名、代码标识、指标名、severity/confidence/disposition、Task Package Contract、complexity pattern 名称和原始证据名称。

私有版正式报告的可见正文、章节标题、表格字段、简化任务包、最终回复和 HTML UI 文案默认使用中文。不要因为本 SKILL.md、reference 文件、工具输出或公开英文版本包含英文，就把主报告、hotspot 卡片、状态标签、按钮或说明性段落整体写成英文。除非用户明确要求英文、目标交付物面向英文读者，或正在同步/审计公开英文版本，才切换为英文；切换时在报告 scope 中记录语言选择。

## When To Use

Use this skill when the user asks for signals like:

- "复杂度扫雷", "臃肿扫描", "低效结构", "结构简化", "简化机会"
- "哪里写得太复杂", "过度设计了", "过度工程", "代码太绕", "看不懂为什么这么复杂"
- "圈复杂度", "循环依赖", "死代码清理", "重复逻辑", "命名混乱"
- "complexity audit", "bloat scan", "simplification sweep", "over-engineering detection"
- "deep complexity analysis", "structural health check", "code health diagnostic"
- a broad request to find simplification opportunities, reduce cognitive load, or clean up accumulated cruft

Do not use this skill for:

- ordinary code review of a single PR or diff; use `requesting-code-review` or compound-engineering reviewers;
- urgent bug fixes or production incidents;
- structural abstraction design where the goal is to find a new canonical model; use `abstraction-architect`;
- legacy migration planning where rollout safety and adoption economics dominate; use `renewal-architect`;
- multi-dimensional quality sweeps covering security, dependencies, and main flows; use `deep-flow-sweep`;
- cosmetic cleanup or naming preferences without evidence of real comprehension cost.

## Budget Envelopes

Budget tiers define the maximum affordable search space, not a mandatory checklist. **Default envelope is Exhaustive** unless the user requests a lighter pass, but even Exhaustive must select methods by risk signal and expected information gain.

| Envelope | Trigger keywords | Guaranteed baseline | Optional capacity | Typical scope |
|---|---|---|---|---|
| **Normal** | "轻量复杂度", "基础简化扫描", "快速复杂度检查" | lightweight probe + three-level map for the target + highest-value pattern checks | one or two low/medium-cost triggered weapons | 单模块/单包, ~150-400K tokens |
| **Deep** | "深度复杂度", "充分简化扫描", "全面臃肿分析" | Normal baseline + root-cause evidence + Git context | change coupling, variant search, architecture fitness, cognitive walkthrough, mutation sampling | 单项目, ~1.5M-4M tokens |
| **Exhaustive** | 默认, "极致复杂度", "全覆盖扫描", "极致简化" | Deep baseline across all critical structural areas | historical slices, cross-repository variants, analyzer triangulation, concurrent independent probes | 多仓库, ~50M+ tokens |

Use the largest method combination that is likely to finish within the envelope and materially improve the answer. Do not run a heavy method merely because budget remains. Read `references/analysis-arsenal.md` before selecting methods.

## Project Shape Lens

Before ranking hotspots, build a short **Complexity Risk Profile**. Shape signals are priors, not conclusions: they guide where to look and which weapons to choose, but they do not prove complexity by themselves. Low metric complexity does not equal low comprehension cost when a user must jump across many files, preserve subtle ordering, or understand implicit external contracts.

Use project shape to bias the three-level scan without hard-coding findings:

| Project shape | Complexity risks to prioritize |
|---|---|
| **Web / SaaS / API** | scattered auth/validation/error contracts, duplicated DTOs, route-to-service shotgun surgery, tenant concepts represented inconsistently, framework glue hiding domain flow |
| **Mobile / Android / Device** | lifecycle state spread across callbacks, permission/device-variant branches, UI/media/storage paths intertwined, release/debug behavior forks, asynchronous recovery logic |
| **Agent / Tooling / Automation** | command orchestration bloat, sandbox/approval assumptions scattered in prose and scripts, report/task-package schema drift, prompt/config/code duplicated across agent surfaces |
| **Library / Framework** | public API surface sprawl, compatibility shims, generic abstractions without consumers, examples/docs forcing awkward usage, dependency inversion that adds no isolation |
| **Split public/private repository** | duplicated release metadata, sync scripts with hidden policy, private/public terminology drift, generated public artifacts that diverge from private sources |

Record how the shape changes method selection. Examples: a low-line-count payment refund flow may still need cognitive walkthrough and change coupling when it crosses many directories; an Android camera feature may need lifecycle and device-variant mapping before judging whether branches are accidental complexity; an agent workflow may need docs-to-command parity checks before calling an orchestrator "bloated."

## Positioning: Cross-Skill Integration

Complexity Sweep is the deepest net for code structure complexity. It borrows detection patterns from `code-simplification` and other external references, matches findings against project-specific analysis skills, and packages appropriate follow-up paths.

| Finding pattern | Escalate to | Handoff signal |
|---|---|---|
| Same class of complexity found >3 times; repeated adapters, duplicated representations, scattered lifecycle logic | `abstraction-architect` | The pattern suggests a missing invariant, not just local cleanup |
| Complexity rooted in legacy compatibility, migration constraints, or organizational boundaries | `renewal-architect` | Simplification requires pilot cells, rollback plans, and adoption economics |
| Many independent simplification tasks discovered; suitable for parallel execution | Claude Code Agent View / Dynamic Workflows, or `agent-orchestration-planner` | Use official Claude concurrency for independent probes; use the planner when execution needs a durable DAG, status ledger, worktree/branch policy, or final integration |
| Findings suggest broader quality issues beyond complexity (security, main-flow bugs, agent gaps) | `deep-flow-sweep` | Complexity is only one dimension of a wider quality problem |

Conversely, when `deep-flow-sweep` or other skills find scattered complexity signals whose true scope is unknown, they should hand off to complexity-sweep for exhaustive depth on this dimension.

## Operating Principles

1. **Depth over breadth on this dimension.** Complexity-sweep drills into code structure like a microscope, not a wide-angle lens. It is better to find 20 concrete complexity issues with evidence than to cursorily mention 50.
2. **Three-level traversal always.** Every scan must consider micro (function/class), meso (module/package), and macro (architecture) levels. A finding at one level often signals a deeper issue at the level above.
3. **Evidence before claims.** Each complexity finding needs: concrete code location (file:line), the specific anti-pattern, a measurable complexity signal (line count, nesting depth, dependency count, duplication rate), and a falsifiable claim about why it's harmful. Thresholds are investigation triggers, not findings.
4. **Root cause, not just symptom.** A long function is a symptom. Ask: is the root cause a missing abstraction, a scattered responsibility, a data structure that should be a type, or just accumulated cruft?
5. **Analyze, do not repair.** Convert findings into evidence-backed simplification task packages. Convert broad redesign pressure into cross-skill escalation recommendations.
6. **Verify what can be verified.** Run static analysis tools, complexity metrics, and dependency graphs when available. Mark unverified claims as such.
7. **Respect the worktree.** Read current status before analysis. Never overwrite unrelated user changes.
8. **Negative results are results.** If a codebase is genuinely simple and well-structured, report that honestly. A clean complexity bill of health is valuable information.
9. **Complexity is about comprehension cost, not line count.** A 5-line function can be more complex than a 20-line function if it packs dense logic into terse expressions. Measure cognitive load, not characters.
10. **Budget buys optionality, not mandatory work.** Select the next method by evidence gap, completion confidence, and expected information gain.
11. **Reconnaissance is not proof.** Heuristic probes and static analyzers nominate evidence; they do not create findings without contextual verification.

## Workflow

### Analysis-Only Mode Latch

Invoking this skill latches the run into analysis-only mode. Declare an **analysis artifact root** before the first write, preferably `reports/complexity-sweep/<run_id>/` when repository conventions permit.

- The run **must not modify product source**, tests, configuration, generated product assets, dependency locks, or Git history.
- Allowed writes are limited to the declared analysis artifact root: reports, manifests, sub-ledgers, evidence indexes, and task packages.
- A severe hotspot, obvious simplification, or remaining budget does not unlock implementation.
- Editing project files requires **new explicit user authorization** after the analysis result is presented.

### 0. Establish Scope And Budget

Infer the sweep target from the user request and repository context:

- target module, package, directory, feature area, or "whole project";
- expected scan depth and any explicitly named complexity concerns;
- complexity risk profile: project shape, dominant comprehension paths, implicit contracts, and the method choices those signals trigger;
- available budget envelope: default to Exhaustive; downgrade to Deep or Normal only if the user explicitly requests a lighter sweep;
- whether concurrent execution is useful for independent sub-sweeps; default to using it when available and materially beneficial unless the user narrows the run.

Before writing findings, inspect:

- repository instructions (`AGENTS.md`, `CLAUDE.md`, `README`, docs) for project conventions and known complexity rules;
- git status and existing uncommitted changes;
- project type, language, framework, and available static analysis tooling;
- (Deep/Exhaustive) past session memory for prior complexity findings;
- (Exhaustive) multi-repository boundaries and nested repo status.

Create a decision ledger before expanding:

- current highest-value unknown;
- candidate weapon from `references/analysis-arsenal.md`;
- cost and completion confidence;
- expected information gain;
- run/defer/skip decision and resulting artifact.

Create a run manifest in the analysis artifact root:

- `run_id`, `git_sha`, `dirty_state`, `scope`, budget envelope;
- project shape signals, dominant complexity risks, and method-routing decisions;
- `source_agent`, `started_at`, `finished_at`, `artifact_path`;
- tool availability, external blockers, and parent run for concurrent sub-ledgers.

Use it for provenance and freshness checks. Reject or quarantine stale sub-ledgers whose run, SHA, scope, parent, or timestamps do not match.

### 0.5 Coverage Matrix Before Findings

Before ranking findings or writing task packages, produce a **Coverage Matrix Before Findings** in the analysis artifact root or report draft. It is the local investigation kernel for this skill and must stay self-contained when the skill is copied alone.

For cross-skill handoff, treat each matrix row as an evidence-ledger producer/consumer entry: preserve a stable `evidence_id`, type, source artifact, observation, confidence, and consumed hotspot/package ID. Reuse incoming IDs and append new evidence instead of rewriting prior observations.

Minimum matrix columns:

- structural level: micro, meso, macro, history, verification, or cross-session;
- comprehension path: feature, command, data flow, module boundary, lifecycle, or developer path being traced;
- artifacts inspected: files, symbols, tests, docs, commits, metrics, commands, or reports;
- evidence status: observed, measured, inferred, unavailable, deferred;
- critical unknowns and coverage debt;
- next weapon decision and expected information gain.

**Path Completion Gate**: A P0/P1 finding, broad simplification claim, or task package needs a completed path from entry/feature through relevant files and contracts to concrete developer/user impact, direct evidence, falsification check, and behavior preservation vector. If that path is incomplete, keep the item as `investigate`, `defer`, or `coverage_debt`.

**Finding permission** is granted only after the coverage matrix plus direct evidence can explain why the issue increases comprehension cost, change cost, bug risk, onboarding drag, or coupling pressure. Do not ship generic simplification advice from line counts, scanner output, naming taste, or historical labels alone.

### 0.6 Decision-First Output

The investigation machine is internal scaffolding. Use **Decision-First Output** for the report: lead with the decision surface, then preserve full fidelity in structured ledgers, task packages, or appendix.

- **Evidence Compression Gate**: evidence enters the main narrative only when it changes severity, confidence, disposition, root-cause grouping, verification route, or escalation. Other evidence stays in appendix, evidence ledger, or collapsible HTML details.
- **Decision Surface Cap**: default the main narrative to 3-5 complexity patterns, simplification directions, or high-priority hotspots. This cap limits the reader-facing decision surface, not the investigation inventory.
- **Critical findings are not capped**: every P0/P1, active bug risk, release blocker, data-loss risk, or major developer-velocity blocker must appear in the main report even if the cap is exceeded.
- **Cluster before appendix**: when many findings exist, cluster by root cause, comprehension path, or simplification mechanism before moving lower-priority duplicate evidence to appendix.
- **Delete-The-Scaffold Rule**: do not expand the full Coverage Matrix, Structure Map, or weapon ledger in the main narrative by default. Expand them only when coverage is disputed, evidence is insufficient, the result is `coverage_debt`, or the user asks to audit the process.
- **One-Screen Handoff Capsule**: provide a compact handoff for external agents: finding/package ID, evidence IDs, severity, confidence, disposition, next action, blocked/deferred reason, verification command/artifact, and owner skill.

For very large budgets, recommend one of these execution shapes:

- **Goal mode** when the user wants the agent to continue across a long analysis budget and resume naturally after context compaction.
- **Task package split** when the result should become a set of human- or agent-executable simplification work items.
- **Concurrent launcher** when the structure map exposes independent modules that can be audited in parallel.

### 1. Build The Structure Map

Map the codebase structure at all three levels before hunting for issues:

Start with the lightweight fact probe when Python is available:

```bash
python3 <skill-dir>/scripts/complexity_probe.py <root> --pretty
```

Resolve `<skill-dir>` to the directory containing this `SKILL.md`. The probe's branch, indent, and hotspot values are approximate triage signals. Use them to choose reading order, then verify important claims with language-aware tools or direct code inspection.

**Micro-level mapping:**
- Use functions/methods longer than 30 lines (stronger signal >50) as investigation triggers;
- Use files longer than 300 lines (stronger signal >500) as investigation triggers;
- Use nesting depth >= 3, >= 4 parameters, or >10 public methods as investigation triggers;
- Record cyclomatic complexity hotspots if tooling is available.

**Meso-level mapping:**
- Map the dependency graph between modules/packages;
- Identify circular dependency chains;
- Identify modules with >20 incoming or >20 outgoing dependencies;
- Map feature-to-file trace: for each major feature, count how many files it touches;
- Identify files that change together frequently (git log --format=oneline --follow);
- Map config/environment variable usage across modules.

**Macro-level mapping:**
- Trace the data flow for each major use case: how many layers does data pass through?
- Map abstraction layers: count interfaces, abstract classes, and their implementations;
- Identify orchestration/coordinator modules and their value-add;
- Map cross-cutting concerns (logging, auth, validation, error handling) — are they centralized or scattered?

Write a short internal structure map before ranking findings. For each structural unit, record:

- key files and their role;
- dependency profile (what it depends on, what depends on it);
- complexity signals (size, nesting, coupling, churn rate);
- shape-specific comprehension path (which files, states, commands, devices, routes, or docs must be followed to understand the behavior);
- likely improvement opportunities.

The full complexity pattern catalog is in `references/complexity-patterns.md`. Read the relevant sections before evidence collection; do not mechanically apply every pattern to every low-risk file.

### 2. Select Weapons And Collect Evidence

Use `references/analysis-arsenal.md` to select a method combination for the current evidence gaps. Always perform baseline structure mapping; add change coupling, variant search, architecture fitness, cognitive walkthrough, abstraction economics, mutation sampling, historical comparison, or cross-repository analysis only when their trigger is present.

After each wave, record:

- new P0/P1 candidates;
- existing findings whose evidence became materially stronger or weaker;
- critical unknowns closed;
- critical areas still unscanned;
- whether another weapon is likely to change the conclusion.

Two consecutive low-information waves trigger a stop review, not an automatic stop. Continue only when remaining budget plus an unscanned critical structural path is likely to change severity, confidence, or disposition; otherwise stop with explicit coverage debt and residual unknowns.

Within the selected structural units, scan for complexity patterns. The pattern catalog in `references/complexity-patterns.md` organizes patterns by level:

**Micro-level (function/class)** — scan every significant function and class for:
- Structural: deep nesting, long functions, long parameter lists, boolean flags, nested ternaries, switch-on-type, god objects, feature envy, inappropriate intimacy
- Naming: generic names, abbreviations, misleading names, inconsistent terminology
- Control flow: callback hell, excessive branching, hidden side effects, exception swallowing, retry-without-backoff
- Redundancy: duplicated logic blocks, magic numbers/strings, dead code, commented-out code, redundant comments
- Abstraction: mixed abstraction levels, primitive obsession, data clumps, refused bequest, speculative generality

**Meso-level (module/package)** — scan every module boundary and package for:
- Coupling: circular dependencies, excessive imports, import-internals, shotgun surgery pattern, divergent change pattern
- Cohesion: scattered feature logic, god modules, mixed unrelated concerns, config duplication
- Layering: pass-through layers, unnecessary indirection, unbalanced abstraction depth, interface-with-single-implementation
- Duplication: duplicated validation, duplicated DTOs/types, copy-paste across modules, parallel class hierarchies

**Macro-level (architecture)** — scan the system architecture for:
- Data flow:迂回 data paths, unnecessary serialization/deserialization chains, data passing through layers without transformation
- Orchestration: coordinator bloat, orchestration-without-value, God orchestrator, scattered workflow state
- Boundaries: wrong boundaries (glue > isolation), missing boundaries (everything-in-one-module), boundary violations
- Abstraction: over-abstraction (too many layers), under-abstraction (missing domain concepts), leaky abstractions

For each detected pattern, collect concrete evidence:
- file path and line numbers;
- measurable metrics (nesting depth, line count, dependency count, duplication %);
- git log showing change frequency and author concentration;
- test coverage of the affected code;
- if the pattern causes real bugs, find or construct a concrete failure scenario.

### 3. Complexity Root Cause Analysis (Deep/Exhaustive)

When budget is Deep or higher, go beyond pattern detection to root cause analysis:

- Load `references/simplification-safety.md`. Run its **Constraint Survival Test** before recommending removal, collapse, consolidation, or boundary changes.
- **Why did this complexity arise?** Check git blame for each hotspot. Was it: time pressure, organic growth, a misunderstood requirement, a workaround for an external constraint, or a premature abstraction?
- **Compensation chains:** Look for sequences where commit A added complexity, commit B worked around it, and commit C added a comment saying "TODO: clean this up". These chains are the strongest evidence that complexity is actively harmful.
- **Hotspot evolution:** Track the complexity trajectory of each hotspot over the last 6-12 months. Is it getting more complex (growing functions, deepening nesting, more dependencies) or stable? Growing complexity without corresponding feature growth is a red flag.
- **Author concentration:** Files with a single dominant author and high complexity are bus-factor risks. Files with many authors and high complexity suggest design disagreement or unclear ownership.

### 4. Git Complexity Archaeology (Deep/Exhaustive)

When budget is Deep or higher, audit git history specifically for complexity signals:

- **Complexity-introducing commits:** Search for commits that add large blocks of code (200+ lines), deeply nested logic, or new inter-module dependencies without corresponding simplification.
- **Simplification-that-wasn't:** Search for commits claiming to "simplify", "refactor", or "clean up" — then check if they actually reduced complexity metrics or just moved the complexity around.
- **Revert patterns:** Commits that were reverted and then re-applied in modified form signal design uncertainty — the code may be complex because the right approach was never settled.
- **Fix-after-fix:** Sequential commits fixing bugs in the same function within a short window signal that the function's complexity makes it error-prone.

Report git archaeology findings with commit SHAs as evidence.

### 5. Cross-Session Intelligence (Deep/Exhaustive)

Query past session memory for complexity-related findings:

- Search for prior complexity-sweep findings, code reviews, or simplification discussions about this project.
- Historical findings are investigation priority signals. For each past finding, verify whether it was addressed and re-rank it from current evidence. **Past severity is not inherited automatically.**
- Identify recurring complexity patterns: if the same anti-pattern appears across multiple sessions, it signals a missing convention, linting rule, or review gate.

Use available memory tools (`memory_smart_search`, `memory_recall`, `ce-sessions`) when present. Tag findings sourced from history distinctly in the ledger.

### 6. Rank Findings

Classify every complexity finding before packaging:

Record **Severity, Confidence, and Disposition** separately using `references/simplification-safety.md`. A high-impact hypothesis with weak evidence remains `investigate`, not a confirmed P0/P1.

| Rank | Meaning | Default Action |
|---|---|---|
| P0 | Complexity causing active bugs, data corruption, or blocking development velocity today | package as urgent simplification with minimal safe scope |
| P1 | Complexity that predictably causes bugs, significantly slows feature work, or creates real onboarding friction | package as high-priority simplification |
| P2 | Meaningful complexity that increases cognitive load but has not yet caused observable harm | report with concrete simplification path |
| P3 | Minor complexity that is technically suboptimal but not measurably harmful | include only if it clusters with other findings into a pattern |

Defer findings that are purely aesthetic, style preferences, or "I would have written it differently" without evidence of harm.

P0/P1 require **direct evidence** of current bug risk, repeated change cost, measured onboarding friction, broken structural contract, or strong static proof on a reachable critical path. Historical labels, thresholds, scanner output, line counts, single-implementation interfaces, and naming preferences cannot establish P0/P1 alone.

When 3 or more findings share the same root cause (e.g., "missing validation abstraction", "scattered auth logic"), stop classifying individually and escalate to the appropriate specialized skill (see Positioning table).

### Task Package Contract And Falsification

Before emitting simplification work, convert each actionable hotspot into the shared **Task Package Contract** in `docs/contracts/task-package-contract.md`. The contract is the bridge from this sweep to manual execution or `agent-orchestration-planner`; use it instead of prose-only task lists when the user may delegate or schedule the work.

Each package must include a **Falsification Ledger**: counter-evidence checked, false-positive risk, style-preference guard, verification gap, and keep/downgrade/defer/drop decision. For complexity findings, the style-preference guard is especially important: prove comprehension cost, change cost, bug risk, onboarding drag, or coupling pressure before proposing work.

Each package must also include the **Constraint Survival Test** and **Behavior Preservation Vector** from `references/simplification-safety.md`.

Each package also starts an **Outcome Replay** stub naming what later execution should report back. Repeated replay outcomes such as `scope_wrong`, `evidence_weak`, or `false_positive` should become future eval prompts or skill contract tests.

When a structured package block exists, run:

```bash
rtk python3 scripts/task_package_validator.py <report-or-package-file>
```

This validator is a repo-local deterministic gate, not a hard dependency of a standalone skill copy. If the skill is copied without the repository `scripts/` directory or the script is unavailable, keep the Task Package Contract fields, Falsification Ledger, Outcome Replay, Constraint Survival Test, and Behavior Preservation Vector in the report, mark deterministic package validation as `missing evidence` / package contract gap, and require manual structural review before handoff or orchestration.

### 7. Produce Simplification Task Packages And Escalation Briefs

Do not edit project files. Convert findings into precise simplification packages.

Each task package should include:

- every required field from the **Task Package Contract**;
- complexity pattern identified and severity;
- confidence and disposition;
- evidence: file:line references, metrics, git history, test gaps;
- simplification approach: what specifically to change (extract function, invert dependency, consolidate config, remove dead code, rename, etc.);
- verification gate: how to confirm inputs, outputs, errors, side effects, operation ordering, concurrency semantics, and performance constraints are preserved;
- estimated blast radius: files and callers affected;
- rollback safety: is this a reversible simplification?

Task packages may recommend:

- extract function/class/module to split responsibilities;
- introduce a missing type, interface, or data structure to replace primitives;
- invert a dependency to break a circular chain;
- consolidate scattered config, validation, or error handling;
- remove dead code, unused abstractions, or pass-through layers;
- rename for clarity where evidence shows onboarding repeatedly confused by the current names;
- add static analysis rules to prevent the same complexity from recurring.

When a finding is too broad for a task package, write an escalation brief:

- `abstraction-architect`: missing invariant, duplicated representation, scattered lifecycle state whose simplification requires a new structural model.
- `renewal-architect`: complexity constrained by legacy compatibility, migration phases, or organizational boundaries.
- Claude Code Agent View / Dynamic Workflows: many independent analysis probes that need only native dispatch and result tracking.
- `agent-orchestration-planner`: implementation packages that need dependencies, durable coordinator state, worktree/branch policy, retries, or final integration.
- `deep-flow-sweep`: complexity is only one dimension of wider quality issues.

### 8. Verification Ledger

Run verification proportional to the analysis claims:

- static analysis tools (linters, complexity metrics, dependency analyzers) to confirm measurements;
- existing test suite to establish behavioral baseline before proposing changes;
- targeted test runs on complexity hotspots to confirm current behavior is understood;
- automated refactoring safety checks where tooling supports it (e.g., IDE extract-function verification).

End with a concise ledger:

```markdown
## Sweep Summary
- Budget tier: <Normal|Deep|Exhaustive>
- Complexity Risk Profile: <project shape, dominant comprehension paths, method-routing decisions>
- Modules scanned: <count and names>
- Total findings: <severity counts; confidence counts; disposition counts>
- Simplification task packages produced: <count>
- Escalations recommended: <skill names>
- Weapons run: <weapon IDs and reasons>
- Weapons skipped/deferred: <weapon IDs and reasons>
- Stop reason: <coverage complete|information gain saturated|budget boundary|external blocker>

## Structure Map
- Micro: <file count, functions flagged, classes flagged>
- Meso: <module count, circular deps, coupling hotspots>
- Macro: <data flow paths traced, abstraction layers found>

## Complexity Hotspots Found
- [P1/high/package] <hotspot>: <anti-pattern, file:line evidence, measured signal>
- [P2/medium/investigate] <hotspot> (memory): <past session reference, current state>

## Git Complexity Archaeology (Deep+)
- <commit SHA>: <complexity signal>

## Cross-Session Findings (Deep+)
- <past finding reference>: <current status>

## Simplification Task Packages
- [P1] <package title>: <Task Package Contract fields, Falsification Ledger, Outcome Replay stub>

## Verification
- `<static analysis command>`: <metrics and key findings>
- `<test command>`: <pass/fail on affected modules>

## External Or Deferred Checks
- <complexity analysis that requires runtime profiling, production data, or human judgment>

## Residual Risks & Simplification Escalations
- <remaining complexity that can't be solved by local simplification>
- Recommended escalation: <skill> because <reason>
```

If no concrete complexity findings survive evidence checks, say so clearly. A codebase with low structural complexity is a positive finding.

## Concurrent Execution Model (Exhaustive)

When the sweep scope spans multiple independent modules, packages, or repositories, split into parallel agents:

**Parallelizable activities:**
- Independent module/package complexity scans (different directories with low coupling)
- Independent repository scans (nested repos, submodules)
- Independent level scans (one agent per level: micro, meso, macro — when modules are loosely coupled)
- Independent evidence probes (static analysis, dependency graphing, test coverage on different modules)

**Must remain sequential:**
- Structure Map construction (must complete before pattern detection)
- Root cause analysis (depends on pattern detection results)
- Ranking and deduplication (must complete before task packaging)
- Cross-skill escalation (depends on full finding list)

**Execution pattern:**
1. Build the full Structure Map in the main session.
2. Split independent scan tasks into prompt files.
3. Use Claude Code Agent View for manually supervised independent sessions, or Dynamic Workflows when Claude should generate and track a bounded concurrent workflow. Use `agent-orchestration-planner` only when the run needs a project-owned execution contract with DAG scheduling, durable status, worktree/branch policy, retries, and final integration.
4. Each agent produces a sub-ledger carrying the parent `run_id`, current `git_sha`, exact scope, timestamps, `source_agent`, and `artifact_path`.
5. Verify provenance and freshness before merging.
6. Merge accepted sub-ledgers, deduplicate findings, resolve cross-module conflicts, and produce unified task packages.

Launch concurrent analysis automatically when it is available, materially beneficial, and remains inside the analysis-only boundary. Do not request a separate confirmation.

## Complexity Trend Analysis (Exhaustive)

When budget is Exhaustive, supplement the snapshot analysis with trajectory data:

- **Complexity growth rate:** Use git history to measure how function lengths, file sizes, nesting depths, and dependency counts have changed over time. A codebase where these metrics grow faster than feature commits grow is accumulating structural debt.
- **Simplification frequency:** What percentage of commits are pure simplification (no feature changes, only structural improvements)? Below 5% suggests simplification debt is accumulating unaddressed.
- **Hotspot migration:** Track which files/directories accumulate the most complexity over the last 6-12 months. Are new features always adding complexity to already-complex areas?
- **Test-to-complexity ratio:** Compare complexity hotspots against test coverage. High complexity + low coverage is the highest-risk combination.

Report trends as a separate section. Trends are observational, not prescriptive.

## Stop Conditions

Stop and report instead of continuing when:

- the user asks to convert the sweep into implementation work; pause and confirm follow-up mode;
- a recommended simplification would require broad architecture migration; escalate instead;
- commands repeatedly fail due to environment setup outside the project;
- unrelated user changes prevent reliable analysis of the target scope;
- the sweep finds so many complexity issues that individual classification loses meaning — at this point, the project needs an architectural intervention, not task packages;
- two consecutive low-information waves trigger a stop review, and remaining budget is better spent synthesizing because no critical structural path remains likely to change severity, confidence, or disposition;
- the token budget is approaching exhaustion but critical modules remain unscanned;
- (Concurrent mode) a background agent returns results that change the shared Structure Map assumption.

## Completion Standard

A complexity sweep is complete only when:

- the budget tier and scope are explicitly stated;
- the analysis artifact root and run manifest are explicitly stated;
- the complexity risk profile records project shape signals and how they changed method selection;
- the selected weapons, skipped heavy methods, and stop reason are recorded;
- Coverage Matrix Before Findings is recorded before findings, and the Path Completion Gate grants or denies finding permission for P0/P1 claims and task packages;
- the report uses Decision-First Output, Evidence Compression Gate, Decision Surface Cap, Cluster before appendix, Delete-The-Scaffold Rule, and One-Screen Handoff Capsule without hiding critical findings;
- all three levels (micro, meso, macro) have been scanned at the depth appropriate to the budget;
- the structure map has been built and recorded;
- (Deep+) Git complexity archaeology findings are reported with commit evidence;
- (Deep+) Root cause analysis is complete for all P0/P1 hotspots;
- (Deep+) Cross-session intelligence is queried and findings are cross-referenced;
- (Exhaustive) Complexity trends and hotspot migration are assessed;
- every finding has evidence, severity, and a concrete simplification or escalation path;
- every proposed simplification has a verification gate and blast radius estimate;
- every unverified claim is explicitly marked as external, deferred, or not run;
- cross-skill escalations are recommended when the pattern exceeds local simplification;
- unrelated cleanup is avoided;
- the final answer helps the user decide where simplification effort will have the highest impact;
- if the codebase is genuinely simple, this is stated honestly as a positive outcome.

## Output Options

正式 complexity sweep 默认 `paired`，即 Markdown source report + HTML review surface；只有用户明确要求 `chat-only` / `no-files` / 快速聊天结论时才降级为聊天输出，并必须记录 coverage debt。维护时与 `docs/contracts/output-modes.md` 同步，但运行时不依赖该文件。

| Budget | Default output | Enhanced output |
|---|---|---|
| Normal | Markdown source report + interactive HTML report using `reviewable-html-report` | Simplification task packages when findings are actionable |
| Deep | Markdown source report + interactive HTML report using `reviewable-html-report` | Sub-ledgers and simplification task packages |
| Exhaustive | Markdown source report + interactive HTML report | Sub-ledgers + concurrent launch manifest + simplification task packages + escalation briefs |

## Report Delivery Contract

- **Markdown is the source report**: generate `complexity_sweep_report_{YYYYMMDD}_{HHMM}.md` for formal sweeps. It must contain the sweep summary, structure map, findings, task packages, verification ledger, external/deferred checks, and escalation briefs in an agent-readable shape.
- **HTML is the review surface**: generate `complexity_sweep_report_{YYYYMMDD}_{HHMM}.html` from the same finding IDs, severity labels, evidence, and task package IDs for every formal sweep. It must include a clickable section index with stable section IDs, and should include clickable finding-to-code navigation, color-coded severity, collapsible sections for each level, and complexity metric visualizations.
- **No split conclusions**: HTML can filter, visualize, and collect feedback, but Markdown remains the factual source for other agents.
- **Package validation**: when simplification packages are emitted as YAML/JSON or fenced structured blocks, run `rtk python3 scripts/task_package_validator.py <markdown-report>` and report failures as package contract gaps. If the repo-local validator is unavailable, mark deterministic validation as `missing evidence`, preserve the structured contract fields, and require manual structural review before handoff.
- **HTML preview**: provide the report path and clickable `file://` URL by default. Active browser opening is optional preview behavior only when the user asks or the environment is clearly GUI-capable.
- **Fallback**: if HTML cannot be generated or opened, still deliver Markdown and state the limitation.

Include timestamp to prevent overwrites across multiple runs. Use the `reviewable-html-report` capability for shared report mechanics; repo-local `skills/reviewable-html-report/references/report_base.md` is an optional enhancement, not a standalone dependency. If that capability is unavailable, use `references/fallback.html` for self-contained static HTML with TOC, stable section IDs, evidence appendix, Mermaid source fallback, and non-persistent feedback.

## Common Mistakes

- Editing code during the sweep instead of producing evidence-backed simplification task packages.
- Continuing into simplification without new explicit user authorization.
- Inheriting P0/P1 from historical findings, scanner output, or metric thresholds.
- Only scanning at one level (e.g., finding long functions but missing that they're symptoms of a missing module boundary).
- Confusing style preference with complexity — a pattern is only complex if it measurably increases cognitive load or change cost.
- Treating project shape as a fixed finding template instead of a routing prior that must be confirmed by code, history, tests, or user-visible comprehension paths.
- Treating line-count reduction as the goal — the goal is lower comprehension cost, which sometimes means more lines with clearer structure.
- Treating Exhaustive as permission to run every analyzer regardless of signal, completion probability, or triage cost.
- Promoting heuristic probe output directly into findings without inspecting the relevant code and context.
- Skipping root cause analysis in Deep/Exhaustive mode — finding a long function without understanding why it grew long produces weak task packages.
- Launching concurrent agents without a shared Structure Map.
- Claiming a sweep is "complete" when critical modules were never mapped.
- Padding the ledger with trivialities when the codebase is genuinely well-structured.
- Recommending abstractions that add more complexity than they remove.
