# User Value Architect Method And Report Contract

This reference contains the detailed gates, report schema, and handoff rules for `user-value-architect`. Load it when producing a formal report, comparing many candidates, or converting analysis into task packages.

Private reports default to Chinese: 私有版正式报告的可见正文、标题、表格字段和 HTML UI 文案默认使用中文. 英文只保留在必要的技能名、文件名、代码标识符、指标名和行业术语中. Do not translate the whole report frame into English unless the user explicitly asks for an English report.

## Budget Envelope Contract

Budget is a coverage contract. It controls how much evidence and criticism must happen before the agent is allowed to recommend.

| Envelope | Minimum work |
|---|---|
| Normal | Define user value target, map one success path, generate candidates, run User-Perceived Value Gate, propose validation. |
| Deep | Normal + inspect available code/docs/product promise/UI or outputs/feedback/external references, identify structural value mechanisms, run persona critique, include rejected/deferred ideas. |
| Exhaustive | Deep + audit main user paths and failure/recovery paths, cross-check recent plans/reports/history, run external reference scan, anti-satisficing, competitive ceiling, proxy-metric challenge, stop ledger, and decision compression. |

When the user says token budget is large, "充分发挥模型能力", "全面核查工程", "追求上限", or similar, default to Exhaustive unless they ask for a lighter pass.

## Project Immersion Protocol

Deep and Exhaustive reports must prove project immersion before recommendations. A report that only lists files read is not deep enough.

Minimum evidence work:

- **Asset inventory**: inventory durable and user-visible assets: README, AGENTS, docs, reports, scripts, tests, examples, public release sources, UI/CLI/API/output artifacts, recent commits, and historical reports. Mark each as inspected, sampled, unavailable, or irrelevant.
- **User-visible surface inventory**: list the entry points, commands, pages, reports, HTML, prompts, agent defaults, error/recovery paths, exports, and generated artifacts users actually touch.
- **Path trace minimum**: trace at least **three concrete user paths**. If fewer than three meaningful paths exist, state why and trace every available path. Each path must include trigger, setup, first value, decision point, failure/recovery, trust cue, and evidence IDs.
- **Promise-reality check**: compare product promise, actual workflow, output artifact, and recovery path; look for promise not implemented, implemented but hidden, useful but high-friction, or technically correct but low-trust.
- **Coverage ledger**: state what coverage was reached, which high-signal surfaces were missing, and whether more exploration is likely to change the decision.

If Project Immersion Protocol is not complete, do not claim `recommend`, `switching reason`, `category-shift`, `3x+`, or `10x`. Downgrade to Value Scan or finish as `blocked_by_evidence` with the missing artifacts named.

## Fact Map Before Advice

Deep and Exhaustive reports must complete **Fact Map Before Advice** before recommendations. This is the minimum fact layer that grants or denies **recommendation permission**:

- scope assumption: target product/workflow, user segment, envelope, and material boundary;
- asset inventory summary: durable assets, user-visible assets, historical reports, public/private release sources, scripts, tests, and generated outputs;
- user-visible surface inventory summary: entry points, commands, pages, reports, HTML, prompts, agent defaults, error/recovery paths, exports, and generated artifacts;
- path trace summary: at least three concrete paths, or every available path if fewer exist;
- Evidence IDs: stable IDs for inspected paths, artifacts, commands, screenshots, reports, user feedback, and external references;
- promise-reality tensions: where promise, actual path, output, and recovery do not line up;
- coverage debt: missing evidence, unavailable runs, and which claims are blocked by those gaps.

Without recommendation permission, a candidate must remain `hypothesis`, `validate-first`, `defer`, or `blocked_by_evidence`. Do not disguise missing evidence with confident language.

**No Naked Recommendations**: Do not recommend abstract labels such as "intelligent routing", "automation", "memory layer", "dashboard", "unified platform", or "better UX" unless they are grounded in a current artifact, a current user path, a user-visible moment, a smallest validation slice, and a counterexample.

**Advice Atomicity Contract**: Every recommendation card must include user-visible moment, Evidence IDs, Current experience slice, After experience slice, structural value mechanism, fastest validation / disproof test, and rejected alternative. If any field is missing, downgrade the candidate instead of marking it `recommend`.

## Exhaustive Evidence Sweep

Exhaustive mode must actively seek user-value evidence instead of only reading convenient files.

### 1. Product Promise And Reality

Compare:

- README, landing copy, PRD, strategy, issue labels, release notes, examples, screenshots;
- actual UI, CLI, API output, generated report, or agent behavior visible to users;
- tests and code only where they explain what the user actually experiences.

Record mismatch patterns:

- promise not implemented;
- implemented but not discoverable;
- useful but too slow, uncertain, or high-friction;
- technically correct but emotionally low-trust;
- internal capability exists but no user-facing path exposes it;
- user can complete the task, but only through remembered procedure or expert setup.

### 2. Main User Path Audit

For each important user path, trace:

- entry trigger and user intent;
- setup cost and prerequisite knowledge;
- first value moment;
- key decision points;
- output quality and actionability;
- failure, correction, retry, undo, and recovery;
- trust evidence and explainability;
- share/export/return-use loop;
- long-term learning or personalization.

The audit may be textual when no UI exists, but it must be concrete. Name files, docs, screens, commands, artifacts, or explicit missing evidence.

### 3. Multimodal Review

When screenshots, recordings, UI, slides, generated reports, images, or browser/device surfaces exist:

- inspect them directly with available visual tools;
- check hierarchy, readability, affordance, confidence cues, error states, empty states, and result inspection;
- distinguish visual polish from user-value leverage;
- mark visual claims as deferred when no visual artifact was inspected.

If the active model or environment cannot inspect visual artifacts directly, degrade without interrupting the analysis:

- continue the value scan using text, code, docs, DOM/accessibility tree, OCR, screenshot metadata, alt text, logs, and user descriptions;
- treat OCR, UI tree, and user descriptions as weaker evidence than direct visual inspection;
- label unsupported visual, emotional, and interaction claims as `visual_evidence_unavailable`, `unknown`, or `deferred`;
- add a short evidence limitation note to the report instead of asking the user to switch models first.

Do not invent visual findings from code or prose.

### 4. History And Plan Cross-Check

If available, inspect recent plans, reports, brainstorms, task packages, releases, commits, or session notes:

- identify repeated user-value ambitions that never became visible experience;
- check whether past recommendations were internal-only or user-visible;
- preserve past evidence only after checking whether it is still current;
- route recurring internal structure blockers to `abstraction-architect` or `renewal-architect` only when they block user-visible value.

### 5. User Feedback And External Expectation

Use any available reviews, support tickets, issue reports, analytics, interview notes, community discussion, competitor examples, or public benchmarks. When browsing or current market facts are needed, verify from primary or recent sources.

Classify external evidence as expectation-setting, direct user pain, competitor ceiling, or weak analogy.

### 6. External Reference Scan

Run this whenever user expectations are shaped by visible alternatives, adjacent tools, industry patterns, public benchmarks, or recent product changes. The scan is a ceiling calibration step, not a feature-copying step.

Classify references into:

- **Direct competitors / same-category best products**: products users would naturally compare against.
- **Adjacent excellence**: workflows, trust surfaces, default outputs, automation patterns, or feedback loops from neighboring domains that solve a similar user burden.
- **Failure patterns / anti-patterns**: public failures, dark patterns, over-automation, low-trust UX, proxy metrics, or feature bloat that should be avoided.

For each relevant reference, record:

| Field | Meaning |
|---|---|
| `reference_type` | direct competitor / adjacent excellence / anti-pattern / benchmark / user expectation |
| `user_expectation` | what users may now assume is normal |
| `ceiling_signal` | what higher-value experience becomes imaginable |
| `copy_risk` | what would be shallow imitation or parity only |
| `differentiation_path` | what could become hard-to-copy value for this product |
| `evidence_status` | observed / reported / inferred / hypothesis / unknown |

If current market or product facts matter, verify them from current sources. If verification is unavailable, keep the finding as `hypothesis` or `unknown`; do not use it to justify a category-shift claim.

## Value Theory / Project-Specific Leverage

Before generating recommendations, write the project-specific value theory. The purpose is to prevent generic advice from being dressed up as strategy.

Answer:

- What scarce user resource is this product really protecting or multiplying: time, attention, judgment, trust, recovery capacity, output quality, long-term compounding, or an impossible-to-manual capability?
- What unique assets does this project have: domain knowledge, historical reports, workflow depth, user preferences, data/context, reviewable deliverables, automation infrastructure, public/private release boundary, ecosystem position?
- Where is value leaking most: discovery cost, setup cost, waiting cost, judgment cost, trust cost, migration cost, reuse cost, non-actionable output, or failure recovery?
- Which directions amplify the project-specific leverage, and which are generic patterns that would be true for 任何同类项目都适用?

If project-specific leverage is weak or unknown, keep high-ceiling ideas as hypotheses and do not claim they are the primary bet.

## User-Perceived Value Gate

Every recommended candidate must pass this gate.

### Two-Track Candidate Model

Evaluate candidate value through two tracks before applying ceiling language:

- **high-ceiling candidates**: opportunities that plausibly reach 30%+, 2x, 3x, 10x, switching reason, or category-shift user value. These need floor, ceiling, path_to_ceiling, evidence strength, external calibration when visible alternatives shape expectations, and a disproof test.
- **small high-certainty improvements**: low-investment, low-risk, user-visible improvements with strong evidence, such as clearer copy, exposed existing capability, one fewer repeated step, better empty/error/recovery text, or a sharper default. These belong in `optimize`, `fast validation bet`, `do-now`, or a local fix list when they are useful.

30% entry line applies to high-ceiling recommendations. For small high-certainty improvements, do not inflate floor or ceiling claims to make them sound strategic, and do not automatically drop them because they lack 30%+/2x upside. Keep the tracks separate: a report may recommend a primary ceiling bet while also preserving certain local improvements as cheap user-visible wins.

| Obligation | What must be shown |
|---|---|
| User-visible moment | The exact point where the user notices the improvement. |
| User outcome path | How the candidate improves speed, confidence, quality, emotional relief, trust, success probability, or long-term benefit. |
| Value type | Function, design, workflow, default experience, feedback loop, trust, content, personalization, or long-term capability. |
| Friction removed | Steps, waiting, confusion, decisions, manual work, repeated input, failure recovery, low trust, or result uncertainty deleted or reduced. |
| Floor | Why the candidate plausibly clears the 30% improvement entry line. |
| Ceiling | The optimistic upper bound: 2x, 3x, 10x, or a qualitative jump such as impossible-to-possible. |
| Path to ceiling | Conditions required to approach the upper bound. |
| External position | Whether the candidate is table stakes, parity, switching reason, hard-to-copy advantage, or category-shift relative to external references. |
| Structural value mechanism | Which recurring user burden, failure path, trust gap, decision cost, or manual translation the candidate deletes or turns into a stable product object. |
| Evidence strength | Observed evidence, inference, hypothesis, and unknowns separated. |
| Disproof test | What would show users do not care, the value is smaller than expected, or the candidate is premature. |
| Internal-only filter | Why this is not merely engineering neatness, maintainability, cost reduction, or agent convenience. |
| Validation route | Fastest credible way to measure, judge, or learn whether user value improved. |

Hard reject a candidate as a recommendation when:

- users cannot perceive the benefit and no clear user outcome path exists;
- the proposal mainly improves internal architecture, tooling, tests, CI, maintainability, or agent execution convenience;
- it assumes user value from technical elegance without evidence;
- it optimizes a proxy metric that could improve while user success stays unchanged;
- the ceiling claim has no path_to_ceiling or disproof test;
- it claims 3x+, switching reason, or category-shift without external reference calibration when users have visible alternatives;
- it cannot name the recurring user burden or failure family it removes;
- it requires broad implementation before any user-value signal can be gathered.

Do not hard reject a small high-certainty improvement merely because it does not clear the 30% floor. Instead, classify it as `optimize`, `fast validation bet`, or `do-now` when it has a concrete user-visible moment, strong evidence, low risk, and low investment. Conversely, do not promote that local improvement into a high-ceiling recommendation unless the evidence supports the larger floor, ceiling, and path_to_ceiling claim.

## Structural Value Mechanism Gate

Use this gate for every candidate that reaches `recommend`, `validate-first`, or `strategic ceiling bet`. It borrows structural discipline from architecture analysis but stays anchored in user-perceived value.

Ask:

1. **User job kernel**: What stable user job or desired outcome explains the repeated pain?
2. **Burden family**: Which repeated burden appears across paths: setup, waiting, checking, interpreting, correcting, recovering, confirming, context reconstruction, result translation, trust formation, or repeated decisions?
3. **Candidate object**: What product object, interaction model, decision surface, feedback loop, memory/context layer, trust surface, or outcome-agent behavior would make the burden natural to handle?
4. **Exception classification**:
   - `absorbable`: cases that disappear because the new mechanism handles them naturally;
   - `real difference`: cases that must remain explicit because user goals, risk, permissions, domain rules, or trust needs differ;
   - `false alarm`: similar-looking cases outside this value mechanism.
5. **Whole-path deletion**: Which step, mode, handoff, manual translation, retry loop, or recovery path becomes unnecessary?
6. **Projection check**: Which user-visible artifacts become consistent projections of the same mechanism: UI, report, recommendation, status, explanation, preview, history, memory, export, or validation output?
7. **Route boundary**: If the mechanism depends on deep domain invariants, state machines, orchestration objects, or boundary redesign, route to `abstraction-architect` instead of pretending the value report contains the implementation design.

Do not recommend a candidate as high-leverage if it can only describe a feature addition but cannot describe the structural value mechanism that makes future user success easier.

## Specificity Gate

Every candidate with disposition `recommend`, `validate-first`, or `strategic ceiling bet` must pass this gate. Otherwise downgrade it to brainstorm, hypothesis, defer, or route.

Required fields:

| Field | Meaning |
|---|---|
| **2-5 specific artifacts** | Name concrete files, pages, reports, commands, screenshots, scripts, tests, issues, or outputs from this project. |
| **Current experience slice** | Describe the current user experience in 3-6 steps, tied to evidence IDs. |
| **After experience slice** | Describe the proposed future experience in 3-6 steps where the user visibly saves effort, gains trust, or achieves a better outcome. |
| **First validation slice** | The smallest credible slice that can learn whether users value the change before building the full platform. |
| **Genericity check** | Explain why this is not merely something that 任何同类项目都适用; name the project-specific evidence or leverage. |
| **Counterexample** | What observation would prove the idea sounds sophisticated but users do not care, the value is smaller, or a smaller option wins. |

Reject generic nouns as recommendations until they are grounded in a path and artifact. "Build orchestration", "add intelligent routing", "create memory", "make a dashboard", or "automate publishing" are only labels; the report must tie them to a current path, a user-visible output, and a validation slice.

## Ceiling Exploration Frames

Use these frames after a candidate passes the value gate:

1. **Ideal user state**: If the product worked perfectly for this user, what would disappear from their effort, anxiety, waiting, or decision burden?
2. **Outcome substitution**: Can the product move from helping the user operate tools to directly helping them achieve the result?
3. **Default magic**: What default output, recommendation, or next action would make the first try feel unusually right?
4. **Trust compression**: What evidence, preview, explanation, recovery, or control would let the user trust faster?
5. **Feedback compounding**: What can the system learn from use so that the tenth run is meaningfully better than the first?
6. **Context carryover**: What user context, preferences, history, assets, or goals should persist across tasks?
7. **Whole-path deletion**: Which entire step, mode, handoff, repeated input, or recovery loop can be removed?
8. **Emotional reversal**: Where can the experience move from anxious/confusing/tedious to calm/obvious/satisfying?
9. **Competitive escape**: If competitors also make ordinary improvements, what capability still feels categorically better?
10. **Non-consumption**: Which users currently avoid the product because the experience is too hard, slow, uncertain, or low-trust?
11. **Adjacent borrowing**: What mature pattern from another domain can be adapted without copying surface features?
12. **Structural deletion**: What stable product object would make several current user burdens disappear together?

## Anti-Satisficing Pass

Run this after the first ranked recommendation list, especially in Deep or Exhaustive mode.

For each recommended candidate, produce three stronger variants:

1. **Higher-ceiling version**: What would make this 2x/3x rather than 30%?
2. **Whole-burden deletion version**: What user step, decision, wait, recovery loop, or manual translation could disappear entirely?
3. **Outcome-agent version**: How would this shift from helping the user operate to helping the user achieve the result?
4. **External-ceiling version**: What would this become if it matched or exceeded the best external reference without becoming shallow parity?
5. **Structural-mechanism version**: What user-facing object, loop, or trust surface would delete the whole burden family instead of optimizing one point?

Then classify each stronger variant:

- `adopt`: replaces or upgrades the original recommendation;
- `validate-first`: too uncertain but high-upside enough to test cheaply;
- `defer`: strategically plausible but expensive or blocked;
- `reject`: attractive but not user-visible, not feasible, or likely harmful.

If the original recommendation survives unchanged, explain why the stronger variants fail. Do not keep the original merely because it is easier.

## Persona Critique Pass

Use personas as adversarial reviewers, not as decorative empathy labels.

| Persona | Challenge |
|---|---|
| New user | Does this reduce time-to-first-value and setup confusion? |
| Heavy user | Does this compound over repeated use or remove recurring work? |
| Failed / churned user | Does this address the likely reason they abandoned the product? |
| Skeptical user | Does this increase trust, control, reversibility, or inspectability? |
| Competitor user | Is there a strong reason to switch, not just parity? |
| Accessibility / low-context user | Does the change rely on hidden knowledge, visual-only cues, or expert phrasing? |
| UX reviewer | Does it reduce cognitive load, mode confusion, errors, or recovery cost? |
| Engineering reality reviewer | Can a user-value signal be gathered before committing to a large build? |

Each persona should either strengthen, weaken, or change at least one candidate. If a persona adds no signal, record it as low-information rather than padding the report.

## Competitive Ceiling Pass

Run when the product has visible alternatives or user expectations are shaped by adjacent products.

Ask:

- What is table-stakes now?
- Which recommendation only reaches parity?
- Which recommendation creates a switching reason?
- Which recommendation creates a category-shift rather than a better local feature?
- Which recommendation competitors could copy quickly?
- Which recommendation depends on proprietary context, workflow depth, trust, data, personalization, or compounding advantage?
- Which adjacent-domain pattern raises the imagined ceiling even if no direct competitor has implemented it?
- Which anti-pattern should this product explicitly avoid because it would reduce trust or increase user work?
- If competitors also improve UX, what remains categorically better for the user?

Do not overfit to competitors when the user segment or job differs. Use competitor evidence to expand possible ceilings, not to copy features blindly. If external references are unavailable, say so and avoid claims like "best-in-class", "switching reason", or "category-shift" unless the argument is explicitly hypothetical.

## Proxy-Metric Challenge

Before recommending metrics or validation:

- Could the metric improve while user success does not?
- Does speed reduce quality or trust?
- Does automation remove control the user values?
- Does engagement reward confusion or rework?
- Does more output create more review burden?
- Does personalization become creepy, opaque, or hard to correct?
- Does conversion improve by hiding cost, risk, or limitations?

If a proxy is risky, pair it with a user-outcome or judge metric.

## Evidence Collection

Prefer evidence that reflects user reality:

- screenshots, recordings, live UI, onboarding flows, empty states, error states;
- user feedback, reviews, support tickets, issue reports, analytics, interviews;
- task completion time, abandonment, retry, correction, backtracking, export/share/use-after-output;
- product docs, promises, examples, demos, landing pages;
- existing code and tests only insofar as they explain user-visible behavior;
- competitor or adjacent product examples when they clarify expectation or possible ceiling.

Classify each evidence item:

- `observed`: directly inspected artifact or behavior;
- `reported`: user, issue, support, analytics, or prior report;
- `inferred`: reasoned from implementation, design, or workflow;
- `hypothesis`: plausible but not supported yet;
- `unknown`: important missing evidence.

## Candidate Decision Dimensions

Use separate dimensions instead of one blended score.

| Dimension | Values | Meaning |
|---|---|---|
| `value_upside` | low / medium / high / breakthrough | Potential user-perceived value if true |
| `floor` | below-30 / 30-plus / 2x / 3x-plus / impossible-to-possible | Conservative improvement hypothesis |
| `ceiling` | 30-plus / 2x / 3x-plus / 10x / category-shift | Optimistic upper bound |
| `confidence` | high / medium / low | Evidence strength, not enthusiasm |
| `user_visibility` | obvious / indirect / weak / none | How clearly users feel it |
| `time_to_signal` | hours / days / weeks / months | How quickly the value hypothesis can be tested |
| `investment` | small / medium / large / strategic | Cost and carrying burden |
| `risk` | low / medium / high | Risk to user trust, complexity, adoption, or delivery |
| `disposition` | recommend / validate-first / brainstorm / optimize / handoff / route / defer / drop | Next action |

High ceiling plus low confidence is not a bad result. Preserve it as `validate-first` if the validation can be cheap and the upside is large.
Small high-certainty improvements are not a bad result either. Preserve them as `optimize`, `fast validation bet`, or `do-now` when users can perceive the benefit and the evidence is strong; do not inflate them into high-ceiling candidates, and do not automatically drop them for lacking category-shift upside.

## Decision Compression

After broad exploration, compress the answer into a small decision set:

- **Primary bet**: highest user-value ceiling with credible path and validation.
- **Fast validation bet**: highest learning per effort, even if not final direction.
- **Strategic ceiling bet**: largest upside if assumptions prove true.
- **Small certainty improvements**: cheap, user-visible fixes that should not masquerade as strategic bets.
- **Do-not-do list**: internal-only, low-visibility, proxy-gaming, or premature ideas.

For each bet, include the user-visible moment, external position, structural value mechanism, fastest disproof test, and route. Avoid giving the user ten equal recommendations. A high-budget report should make the next decision easier, not prove that many ideas were considered.

## Decision-First Output

The investigation machine is an internal quality constraint, not the default shape of the main report. Use **Decision-First Output** so the reader sees the decision surface before the scaffolding.

- **Evidence Compression Gate**: evidence enters the main narrative only when it changes a recommendation, priority, confidence, risk judgment, validation route, handoff route, or `blocked_by_evidence` conclusion. Other evidence stays in appendix, evidence ledger, or collapsible HTML details.
- **Main Narrative Cap**: default to at most three primary recommendations or strategic bets in the main narrative. This cap does not limit candidate generation, evidence collection, rejected/deferred ideas, validation notes, or task packages.
- **Delete-The-Scaffold Rule**: do not expand the full Fact Map, Project Immersion Protocol, or Coverage ledger in the main narrative by default. Expand them only when evidence is insufficient, the conclusion is controversial, the user asks to audit the process, or the result is `blocked_by_evidence`.
- **One-Screen Handoff Capsule**: provide a compact handoff for external agents: recommendation ID, Evidence IDs, confidence, next action, blocked/deferred reason, validation command/artifact, and owner skill.

The main report should compress judgment; appendix and structured ledgers preserve fidelity.

## Formal Report Schema

Formal reports must be written under the analyzed project's durable report directory:

```text
reports/user-value-architect/user_value_architect_report_{YYYYMMDD}_{HHMM}.md
reports/user-value-architect/user_value_architect_report_{YYYYMMDD}_{HHMM}.html
```

Create `reports/user-value-architect/` first if it does not exist. Resolve this path against the authoritative workspace, not automatically against the current shell directory. If the current path is inside `.claude/worktrees/`, `.worktrees/`, or another agent worktree, first use the project `AGENTS.md` authoritative workspace / Authoritative workspace field, the user-provided main project path, or the Git common dir to identify the real project root. Do not leave formal reports in the worktree's own `reports/`, the repository root, the current shell directory, `.tmp/`, an agent worktree root, or a system temporary directory. If authoritative workspace project `reports/` is not writable, explicitly report the fallback path and reason in the final response.

不得省略正式 schema 的主章节。If a section has no available evidence or no generated task packages, keep the section and state `无可用证据`, `未生成任务包`, or `不适用`, instead of silently deleting it. This protects follow-up agents from guessing whether a pass was omitted or intentionally found no signal.

Markdown source report (upgrade artifact; produced only on explicit user request or HTML fallback):

```markdown
# User Value Architect Report

## Executive Recommendation
- <1-3 highest-upside recommendations>
- <why these matter to users>
- <what to validate first>

## One-Screen Handoff Capsule
| ID | Evidence IDs | Confidence | Next action | Blocked/deferred reason | Validation command/artifact | Owner skill |
|---|---|---|---|---|---|---|

## Analysis Scope
- Target:
- User segment:
- Materials inspected:
- Multimodal evidence available:
- Evidence gaps:

## Project Immersion Protocol
- Asset inventory:
- User-visible surface inventory:
- Three concrete user paths:
- Promise-reality check:
- Coverage ledger:

## Fact Map Before Advice
- Scope assumption:
- Asset inventory summary:
- User-visible surface inventory summary:
- Path trace summary:
- Evidence IDs:
- Promise-reality tensions:
- Coverage debt:
- Recommendation permission:
- No Naked Recommendations / Advice Atomicity Contract exceptions:

## User Value Target
- User job / desired outcome:
- Current user success path:
- Current friction:
- Trust and emotional state:
- 30% entry line:
- Ideal ceiling:

## Evidence Ledger
| ID | Type | Source | Summary | Strength |
|---|---|---|---|---|

## Value Theory / Project-Specific Leverage
- Scarce user resource:
- Unique project assets:
- Largest value leakage:
- Leverage thesis:
- Genericity risk:

## User Success Path Map
- Trigger:
- Setup:
- First value:
- Core loop:
- Failure and recovery:
- Trust formation:
- Long-term compounding:

## Candidate Matrix
| ID | Candidate | Value type | User visibility | Floor | Ceiling | Confidence | Time to signal | Disposition |
|---|---|---|---|---|---|---|---|---|

## Exhaustive Evidence Sweep
- Product promise vs reality:
- Main user paths audited:
- Multimodal artifacts inspected:
- History / plan cross-check:
- User feedback / external expectations:

## External Reference Map
| ID | Reference | Type | User expectation | Ceiling signal | Copy risk | Differentiation path | Evidence status |
|---|---|---|---|---|---|---|---|

## Structural Value Mechanisms
| ID | User job kernel | Burden family | Candidate object / loop | Absorbable cases | Real differences | Whole-path deletion | Route |
|---|---|---|---|---|---|---|---|

## Specificity Gate Results
| ID | 2-5 specific artifacts | Current experience slice | After experience slice | First validation slice | Genericity check | Counterexample | Decision |
|---|---|---|---|---|---|---|---|

## Recommendation Cards
### UVA-01: <title>
- User-visible moment:
- Current friction:
- Proposed change:
- Floor:
- Ceiling:
- Path to ceiling:
- External position:
- Structural value mechanism:
- Whole-burden deletion:
- Evidence:
- Disproof test:
- Validation route:
- Risks:
- Handoff:

## Ceiling Bets
<High-upside, low-certainty hypotheses worth validating cheaply.>

## Anti-Satisficing Results
| Original | Stronger variant | Decision | Reason |
|---|---|---|---|

## Persona Critique
| Persona | Candidate affected | Effect | Note |
|---|---|---|---|

## Competitive Ceiling
- Table stakes:
- Parity risks:
- Switching reasons:
- Category-shift candidates:
- Copyable improvements:
- Hard-to-copy value:
- Adjacent references:
- Anti-patterns to avoid:

## Decision Compression
- Primary bet:
- Fast validation bet:
- Strategic ceiling bet:
- Do-not-do list:

## Rejected Or Deferred Ideas
| Idea | Reason | Route |
|---|---|---|

## Validation Plan
- Metrics:
- Judge rubric:
- Sample:
- Pass signal:
- Fail signal:
- Fastest learning path:

## Task Packages
<Optional fenced YAML compatible with Task Package Contract.>

## Handoff Routing
- `ce-brainstorm`:
- `ce-optimize`:
- `product-sense-refiner`:
- `abstraction-architect`:
- Task Package Contract / `agent-orchestration-planner`:

## Residual Risks And Unknowns

## Stop Ledger
- Coverage reached:
- Low-information passes:
- Remaining evidence gaps:
- Why analysis can stop now:
```

HTML report (default formal deliverable):

- The HTML reviewable surface is the default formal deliverable. Unless the user explicitly asks for chat-only or no-files, every formal analysis must produce this reviewable HTML report and provide its saved path plus a clickable `file://` URL.
- A Markdown source report is an upgrade artifact and is generated only when the user explicitly requests an agent handoff or source-file delivery, or when HTML generation is infeasible. When a Markdown source exists, HTML must derive from the same evidence IDs, candidate IDs, recommendations, and dispositions.
- Must include a clickable section index / TOC with stable section IDs and `href="#section-id"` links for every major section.
- 生成 HTML 前，按 `reviewable-html-report` capability 确认 companion skill boundary；仓库内的 `skills/reviewable-html-report/references/report_base.md` 仅作为可选增强，不构成独立运行时硬依赖。
- Must include reviewable units for recommendation cards and high-risk decisions: `review-controls`, stable `data-card-id`, status/comment controls, and feedback export. If local persistence is used, wrap localStorage in fallback-safe code.
- May add visual filtering, candidate cards, evidence expanders, and review controls.
- Must not introduce conclusions missing from the underlying analysis or Markdown source when one is produced.
- 先读取 `../reviewable-html-report/SKILL.md` and use `../reviewable-html-report/references/report_base.md` when building an interactive review surface. If it is unavailable, fall back to self-contained static HTML with a TOC, stable section IDs, evidence appendix, Mermaid source fallback, and a non-persistent feedback area.
- Open the report only when the user requests a preview or the environment explicitly supports interactive preview without CI, SSH, or headless side effects.

## Task Package Guidance

Only create task packages for follow-up work after the analysis has a clear candidate or validation action. Use `docs/contracts/task-package-contract.md`.

Map fields as follows:

- `source_skill`: `user-value-architect`
- `finding_id`: candidate ID such as `UVA-01`
- `severity`: usually `P2` or `P3`; reserve `P1` for demonstrated critical user-value failure in a core flow
- `problem_statement`: user-visible problem or opportunity
- `evidence`: user evidence and inspected artifacts
- `root_cause`: current best explanation of why user value is limited
- `proposed_change`: validation, brainstorm, design change, experiment, or implementation package
- `expected_user_value`: user-perceived value improvement hypothesis
- `falsification`: include counter-evidence, false-positive risk, style guard, verification gap, decision
- `outcome_replay`: start as pending so future execution can teach the skill

Do not create execution packages for broad strategic bets that need product approval. Create a validation or brainstorming package instead.

## Completion Check

Before finalizing a formal report, verify:

- every recommended candidate has a user-visible moment;
- Deep/Exhaustive reports complete Fact Map Before Advice before advice, and candidates without recommendation permission are downgraded;
- reports use Decision-First Output, Evidence Compression Gate, Main Narrative Cap, Delete-The-Scaffold Rule, and One-Screen Handoff Capsule;
- Deep/Exhaustive reports completed Project Immersion Protocol or downgraded to Value Scan / `blocked_by_evidence`;
- the report includes Value Theory / Project-Specific Leverage and explains why recommendations are not generic advice that 任何同类项目都适用;
- every recommended candidate passes Specificity Gate with 2-5 specific artifacts, Current experience slice, After experience slice, First validation slice, and Counterexample;
- every recommendation card satisfies No Naked Recommendations and Advice Atomicity Contract, including Evidence IDs, validation/disproof, and rejected alternative;
- the report uses the Two-Track Candidate Model, separates high-ceiling candidates from small high-certainty improvements, treats the 30% entry line as applying to high-ceiling recommendations, and does not inflate or automatically drop small improvements;
- every high-ceiling claim has floor, ceiling, path_to_ceiling, and evidence strength;
- internal-only improvements are rejected, deferred, or routed elsewhere;
- Deep/Exhaustive reports include evidence sweep coverage and stop ledger;
- Exhaustive reports include anti-satisficing, persona critique, competitive ceiling, and proxy-metric challenge;
- at least one disproof test exists for each recommendation;
- the validation plan can learn before committing to a large build;
- downstream routing is explicit;
- code was not modified under this skill.
- the formal HTML report was written under `reports/user-value-architect/`, or a fallback path was explicitly explained;
- when a Markdown source report was produced (explicit user request or HTML fallback), it shares the same report data with the HTML, uses the same timestamp basename, and the HTML has section-index navigation.
- private report visible text is Chinese by default, with English limited to necessary technical identifiers and industry terms.
- HTML used `review-controls`, stable `data-card-id`, and feedback export from the `reviewable-html-report` capability, or explicitly documented the fallback.

## Stop Conditions

Stop analysis and synthesize when:

- the user-value target is explicit enough to judge candidates;
- Project Immersion Protocol is complete, or the report is downgraded / `blocked_by_evidence`;
- Fact Map Before Advice is complete, and every recommendation has recommendation permission;
- Value Theory / Project-Specific Leverage explains the project-specific leverage;
- all available high-signal evidence surfaces for the selected envelope were inspected or marked unavailable;
- main user path and failure/recovery path are mapped;
- every recommendation passed the value gate;
- every recommendation passed Specificity Gate;
- anti-satisficing produced no adopted higher-ceiling replacement, or replacements are included;
- persona critique and competitive ceiling no longer change the top decision set;
- validation routes can distinguish real user value from proxy improvement;
- further exploration is likely to add examples, not change the decision.

If these conditions are not met but budget or evidence runs out, finish with `blocked_by_evidence` and name the missing artifacts.
