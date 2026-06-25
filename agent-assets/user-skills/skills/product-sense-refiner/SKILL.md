---
name: product-sense-refiner
description: >
  用于技术方案、工具设计、评估系统、报告、交互流程或工作流已经大致成立，但仍可能缺乏产品感、默认输出不清晰、用户决策价值不足、机制堆叠过多或容易奖励错误行为时。
  Use when a design needs sharper product fit, decision-useful output, user-facing defaults, recommendation framing, or optimization beyond technical correctness.
whenToUse: >
  当方案已经有雏形，需要提升产品适配度、用户决策价值、默认输出、推荐框架、交互流程、评估激励或从技术正确走向真实可用时使用。
  不用于从零构思、纯视觉设计、普通代码实现、数学学习、职业面试或架构债务治理。
---

# Product Sense Refiner

## Mission

Refine a technically plausible design into a decision-useful product design.

The core move is:

> Start from the user's decision and default answer, then work backward to the internal model.

Use this skill when a solution is reasonable but still feels generic, over-mechanized, too internally focused, too verbose by default, or not sharp enough for the user's real choice.

## When To Use

Use this skill when:

- A feature, report, workflow, scoring system, agent tool, or architecture plan is technically valid but not product-sharp.
- The user asks for deeper insight, better optimization, product sense, or why an earlier design lacked fit.
- A design exposes many mechanisms but does not make the user's next decision obvious.
- A default report/output is too detailed, too vague, or not action-oriented.
- A metric or ranking could reward the wrong behavior.
- Multiple valid strategies exist and the design must say what should be default, hidden, optional, or unsupported.

Do not use this skill for narrow bug fixes, emergency recovery, purely mechanical implementation, or already approved specs where product framing is intentionally fixed.

## Core Workflow

### 1. Name The User Decision

State the decision the user is trying to make. Do not describe the feature first.

Weak:

> This tool scores AI agents.

Better:

> This tool helps the user decide which agent is suitable for which class of real engineering task.

If the decision cannot be named, the design is not ready.

### 2. Write The Default Answer First

Before refining internals, draft what the user should see by default.

A good default answer is short, decision-oriented, and safe from false certainty.

Example:

```text
87 / 100
Suitable for low-risk implementation and existing-plan execution; not the first choice for open-ended architecture exploration.
Confidence: high
```

If the default answer is not useful, the internal model is probably solving the wrong problem.

### 3. Separate Fact, Judgment, And Expression

Classify every major piece of the design:

| Layer | Meaning | Examples |
|---|---|---|
| Fact | Raw observable material | diff, logs, tests, user input, timestamps, artifacts |
| Judgment | System interpretation | score, tier, rank, confidence, risk, incomparable reason |
| Expression | User-facing output | recommendation sentence, report row, dashboard summary |

Do not leak all judgments into default expression. Do not treat expression as evidence.

### 4. Pressure-Test Extreme Archetypes

Test the design against cases that expose product weakness:

- Stable but mediocre performer.
- High-upside but inconsistent performer.
- Verbose self-reporter with weak evidence.
- Small safe fix versus broad risky redesign.
- Result that solves the task but creates future maintenance cost.
- Result that reframes the problem and improves future work.
- Two results that are genuinely incomparable.
- Ambiguous task where user intent changes the ranking.

Ask: would the current default answer mislead the user?

### 5. Find Reward Misalignment

Identify what the system might accidentally reward:

- verbosity instead of evidence;
- effort instead of outcome;
- novelty instead of usefulness;
- low-risk conservatism when exploration is needed;
- impressive framing without solving the core problem;
- forced rankings where the real answer is incomparable;
- historical anchors that silently freeze bias;
- a metric that is easy to optimize but not decision-useful.

For each misalignment, decide whether to remove the metric, cap it, make it internal-only, or expose it with caveats.

### 6. Decide What Stays Internal

Good product design often hides complexity by default while preserving auditability.

Mark each detail as:

- `default`: shown in the normal answer;
- `detail`: available on request or in detailed mode;
- `audit`: persisted for traceability but not surfaced unless debugging;
- `discard`: not useful or incentives are wrong.

The default answer should usually contain only the minimum needed for the user's next decision.

### 7. Turn Descriptions Into Recommendations

Replace vague praise with fit guidance.

Weak:

> This result is excellent and well structured.

Better:

> Best suited for ambiguous refactoring tasks where structural insight matters more than first-pass predictability.

A recommendation sentence should include fit and non-fit when relevant.

## Product-Sense Questions

Use these questions to find better optimizations:

- What will the user do after reading this output?
- What is the shortest answer that still changes the user's decision?
- What should be hidden by default but retained for audit?
- Which metric would encourage bad behavior?
- What result would be great but non-standard?
- What result is valid but incomparable?
- What user goal changes the ranking?
- What must not enter the score even if it is measurable?
- What false certainty could this design create?
- Where does the design confuse internal reasoning with user-facing expression?

## Output Format

When using this skill, return a concise refinement report:

```markdown
## Product Frame
<User decision and corrected product purpose>

## Default Answer
<recommended default output shape or example>

## Keep
<parts of the current design that serve the user decision>

## Change
<internal model or workflow changes that improve product fit>

## Remove
<metrics, outputs, or mechanisms that create bad incentives or false clarity>

## Keep Internal
<analysis that should remain available but hidden by default>

## Recommendation Wording
<one or more actionable user-facing sentences>

## Risks
<ways the refined design could still mislead users>
```

For small tasks, compress the sections but preserve the logic: decision, default answer, changes, removals, recommendation.

## Common Mistakes

- Starting from available mechanisms instead of the user's decision.
- Treating a detailed internal model as a good default output.
- Adding more dimensions when the real fix is removing a misleading metric.
- Forcing a total order when the honest result is incomparable.
- Scoring cost, effort, or process just because they are measurable.
- Using anchor examples as hidden judges when full recomputation or direct comparison is more honest.
- Writing adjective-only profiles such as "excellent" or "strong" instead of actionable recommendations.

## Completion Check

Before finishing, verify:

- The user decision is explicit.
- The default answer is short and actionable.
- Fact, judgment, and expression are separated.
- At least one extreme archetype was pressure-tested.
- Misaligned incentives were removed, capped, or made internal-only.
- The recommendation tells the user what the result is suitable and unsuitable for when that matters.
