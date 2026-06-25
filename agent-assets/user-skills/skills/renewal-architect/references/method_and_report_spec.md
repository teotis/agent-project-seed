# renewal-architect Detailed Method and Report Specification

# Part I — Method Framework: Twelve Engineering Lenses

The principles form a sequence rather than a checklist:

- **See reality clearly:** lenses 1–4 prevent fashion, habit, and rhetoric from obscuring the system.
- **Create a breakthrough:** lenses 5–8 convert debate into facts and reusable outcomes.
- **Advance without losing control:** lenses 9–12 make evolution sustainable, governable, and owned.

For every significant finding, ask:

> **Is this a real capability bottleneck, or merely a contest of architecture narratives? What controlled pilot would allow results to decide?**

Also ask:

> **What must be protected, what can be experimented with, who must adopt the result, and what fact will decide the next step?**

---

## A. See Reality Clearly: Resist Empty Architecture Rhetoric

### 1. Evidence First — Map the Terrain Before Declaring a Transformation

**Engineering meaning:** Architecture diagrams, README files, and design intentions cannot substitute for system behavior. Begin with runtime paths, change hotspots, incidents, delivery friction, implicit contracts, and actual callers.

**Inspect for**
- whether declared layering matches actual call direction;
- modules repeatedly changed, repeatedly broken, or repeatedly bypassed;
- paths called “temporary compatibility” that have persisted for years;
- real operating rules exposed by tests, releases, data correction, and manual operations.

**Required outputs**
- A `Fact Ledger` separating evidence, inference, and unknowns;
- a map of actual critical flows, not just the aspirational architecture diagram;
- explicit `Requires Validation` markings wherever the evidence is incomplete.

**Misleading claims to reject**
- “This is best practice, so we should rewrite.”
- “The new architecture must be superior.”
- “Nobody understands this old module, so it can be removed.”

---

### 2. Capability Benefit — Judge Optimization by Capability Growth, Not Change Volume

**Engineering meaning:** Optimization is not making the code look modern. It is improving capability: faster delivery, fewer failures, easier evolution, less manual work, or stronger business experimentation.

**Candidate capability signals**
- lead time, deployment frequency, rollback time, mean time to recovery;
- latency, success rate, capacity, compliance, or security posture of a critical business flow;
- the change surface required to add a product, channel, region, tenant, or rule;
- engineering wait time, repeated manual operations, and cross-team coordination rounds;
- cost per delivered unit, infrastructure cost, and incident cost.

**Decision rule**
- Every proposed change must state which capability it releases.
- If no observable improvement signal can be defined, the proposal may appear only as a candidate hypothesis, not as a near-term evolution priority.

---

### 3. Outcomes Over Schools of Thought — Tools Are Judged by Results Under Constraints

**Engineering meaning:** Microservices, monoliths, serverless, build-versus-buy, synchronous versus asynchronous design, Rust, Java, and AI-generated code are all means, not identities. Judge them by whether they reliably achieve the intended outcome in this project's constraints.

**Operational rules**
- Compare disputed alternatives against the same result metrics and constraint set.
- Evaluate total migration cost, team competence, operational burden, and exit capability, not merely ideal performance.
- Prefer an existing stable tool when it can produce the breakthrough without introducing unnecessary novelty.
- New tools may be tried only in an isolated, observable, rollback-defined pilot.

**Anti-patterns**
- “We are a large company, therefore we must become microservices.”
- “This technology is old, therefore replacement comes before value.”
- “The industry is doing it, therefore business benefit need not be tested.”

---

### 4. Identify the Dominant Constraint — Relieve the Bottleneck That Expands Future Action

**Engineering meaning:** Large projects always contain hundreds of flaws. Equal effort across all flaws turns optimization into an endless backlog. First identify the constraint whose relief would materially enlarge the space of future action.

**Candidate dominant constraints**
- a central module that every new feature must edit;
- a testing, deployment, or approval chain that prevents frequent safe release;
- the source of globally inconsistent identity, permission, order-state, or data semantics;
- a shared dependency that prevents teams from delivering independently;
- a critical legacy domain that fails repeatedly but cannot be changed safely.

**Required answers**
- Why does this deserve priority over other technical debt?
- What opportunities become possible after it is relieved?
- If the diagnosis is wrong, can the loss be bounded?

---

## B. Create a Breakthrough: Let Small-Scale Facts Open Global Options

### 5. End Circular Debate with Validation — Turn Camps into Experiments

**Engineering meaning:** When debate remains at the level of “old versus new,” “buy versus build,” “monolith versus microservices,” or “framework A versus B,” do not let meetings consume the project. Rewrite disagreement as a testable hypothesis.

**Minimum experiment contract**
- **Hypothesis:** Within a stated boundary, what will the new approach improve?
- **Unknown:** Which missing fact will this pilot resolve?
- **Scope:** One flow, tenant, module, read path, or task class.
- **Signals:** What constitutes success or failure?
- **Timebox:** When is the review point?
- **Rollback:** How is the change quickly withdrawn if it fails?
- **Decision gates:** Expand, revise, pause, rollback, or stop according to the observed signal.

**Critical limit**
Validation does not mean skipping review for security, data consistency, compliance, privacy, or irreversible risk. Those are non-negotiable engineering facts.

---

### 6. Reversible Evolution — A Progressive Validation Path for High Uncertainty

**Engineering meaning:** In high-uncertainty legacy regions, no perfect route runs directly from a slide deck to the final state. Every step should increase knowledge, retain withdrawal capability, and make the next step less uncertain.

**Engineering practices**
- Add observability before changing behavior.
- Use shadow traffic, dual-write or dual-read comparison, or read-side bypass before cutting over a primary path.
- Establish a compatibility facade or strangler seam before replacing internals.
- Start with small datasets, small traffic, and a small owning team before expanding.
- Set continue, pause, rollback, and redirect gates at each step.

**Default safety toolbox — select only where relevant**

| Uncertainty or Risk | Preferred Validation Mechanism | Exit Action |
|---|---|---|
| Correctness of new calculation is unknown | shadow execution / dual-read result comparison | retain old result as authoritative |
| Capacity and stability of a new service are unknown | canary traffic plus SLO comparison | route traffic back to old path |
| Behavioral switch needs rapid withdrawal | feature flag / configuration gate | disable the new path immediately |
| Data model change has compatibility risk | expand-contract schema migration | pause contraction and retain old-field compatibility |
| New and old module semantics conflict | ACL / facade / strangler seam | redirect callers to the old core |

**Validation cadence:** Each formal pilot should produce its first verifiable signal within a normal planning cycle, usually 1–2 sprints. Where longer is unavoidable, state the reason, intermediate artifacts, and earlier loss-limiting gates.

**Questions to ask**
- What concrete fact does this step test?
- What reliable knowledge will exist after it?
- Will the following step be safer and clearer than the current one?

---

### 7. Isolated Pilot — Choose a Breakthrough Unit That Can Validate, Teach, and Replicate

**Engineering meaning:** The first pilot should be neither a decorative trivial module nor the highest-blast-radius core. It should contain real pain, have controllable boundaries, produce visible benefit, and represent enough of future difficulty to teach useful lessons.

#### `Pilot Cell`

Select a bounded module, flow, tenant, or traffic segment as the first optimization unit. Within it, apply new boundaries, tests, observability, and delivery rules. Outside it, isolate risk through an explicit compatibility boundary. The `Pilot Cell` is not a permanent privileged area; it is a temporary proving ground for a reusable global pattern.

**Pilot selection criteria**
- Pain intensity: Is the problem real and recurring?
- Boundary control: Can risk be isolated and rollback performed?
- Representativeness: Can the result transfer to other domains?
- Observability: Can improvement be proved?
- Organizational feasibility: Are owner and collaborators available?
- Adoption fit: Do the teams receiving benefit, paying migration cost, and owning operation have a workable agreement?
- Business timing: Does it align with near-term demand or maintenance windows?

**Typical candidates**
- A frequently changed and failure-prone business subdomain that can be isolated behind an interface.
- A shared capability repeatedly penetrated by new requirements, which can first be enclosed by a stable boundary.
- A data read or query path where shadow or comparison validation lowers cutover risk.
- An incremental path for a new channel, tenant, or region that avoids one-shot migration of existing traffic.

**Do not**
- use an irrelevant demo to claim a global route has been validated;
- cut over the most critical primary path broadly before loss-limiting mechanisms exist.

---

### 8. Replicate and Scale — A Pilot Is Valuable Only When Success Becomes Reusable

**Engineering meaning:** A migration completed once through heroics is not system evolution. Convert pilot learning into platform capability, migration templates, contracts, tooling, and ownership mechanisms.

#### Dual-Track Compatibility Boundary

During a substantial migration, new and old architecture often must coexist. Explicitly design `ACL / Facade / Strangler Seam / Translation Adapter` boundaries so the new path does not copy legacy semantic contamination, while the old core continues compatibility service until retirement criteria are reached. A compatibility layer must have an owner, observability, cost recording, and a retirement plan; otherwise it becomes permanent new debt.

**Replication assets**
- standardized interfaces, event contracts, and data migration protocols;
- ACL, Facade, or Strangler templates with retirement conditions;
- automated scaffolding, test suites, dashboards, and alerts;
- migration and rollback runbooks plus acceptance gates;
- responsibility boundaries between supporting and adopting teams;
- prioritized next candidate domains and budget.

**Scale gates**
- Pilot signals meet their thresholds over a sustained interval.
- Major failure modes have surfaced and been corrected.
- A second team that is not the original author team can apply the template.
- The second team has clear benefit, budget or capacity, approval path, and operational ownership.
- Expansion does not pierce the stability floor.

---

## C. Advance Safely: Increase Velocity Without Losing Control

### 9. Benefit, Pace, and Stability — Evolution Speed Must Match Absorptive Capacity

**Engineering meaning:** Capability improvement is the objective; incremental change is a means; stable operation and trustworthy delivery are prerequisites. Do not use stability as an excuse never to act, and do not make production absorb unlimited risk in the name of modernization.

**Every recommendation must state**
- **Capability benefit:** What does it unlock?
- **Transition cost:** Engineering, training, dual-run, and operational cost.
- **Stability floor:** SLOs, data correctness, security, compliance, and critical business continuity.
- **Risk staging:** Blast radius during pilot, enlargement, and full replacement.
- **Exit route:** How can existing gains be retained if the route fails?

**Cadence rules**
- High risk and low knowledge: small steps, strong telemetry, strict rollback.
- Clear benefit and validated path: do not miss the window through abstract debate.
- Existing instability: repair the instability source before broadening change.

---

### 10. Acceleration and Guardrails Together — Build Delivery Capability and Governance Capability at the Same Time

**Engineering meaning:** One side builds developer effectiveness, platform reuse, fast experiments, and business release. The other builds testing, observability, security, permissions, data governance, cost control, and incident response. If either is absent, evolution eventually damages the system.

**Paired-capability checklist**

| Capability Release | Order and Safety Guardrail |
|---|---|
| self-service delivery, scaffolding, service templates | release gates, rollback, auditability |
| faster experiments, technology trials | dependency scanning, permission control, data isolation |
| service autonomy, domain separation | contract tests, SLOs, unified observability |
| external capability integration | supply-chain control, exit path, cost ceiling |

**Diagnostic signals**
- Velocity rises while incidents or security debt rise with it: guardrails are too weak.
- Governance grows heavy while delivery stalls and bypass behavior spreads: acceleration has been suffocated.

---

### 11. Open Learning — Absorb Mature Capability Instead of Recreating Debt in Isolation

**Engineering meaning:** Large projects should neither celebrate custom building as an identity nor treat procurement as escape from responsibility. Mature external tools, standards, cloud services, open-source components, and operating methods should be adopted where they reliably satisfy explicit constraints.

**Evaluation dimensions**
- Does the capability create genuine differentiation?
- What are the full lifecycle costs of purchasing, adopting open source, or building?
- What are the data, compliance, security, and supply-chain risks?
- What are lock-in, exit cost, and substitution paths?
- Can the team maintain the critical interfaces and operational responsibility?

**Required results**
- When selecting an external capability, design observable, contract-defined integration and an exit surface.
- When selecting custom construction, prove that external alternatives fail a critical boundary rather than rejecting learning through preference.

---

### 12. Ownership and Transfer — Evolution Requires Owners, Incentives, and Frontline Learning

**Engineering meaning:** A correct technology direction that has no owner, benefits nobody explicitly, or cannot be maintained will not land. Effective improvement often begins with engineers closest to the pain. Leadership responsibility is to identify, protect, validate, and turn local invention into repeatable mechanism.

**Must identify**
- a single accountable owner for each pilot;
- whether teams receiving benefit and teams bearing cost are aligned;
- who pays migration, training, dual-run, and on-call costs;
- who can approve adoption and who can block it;
- how cross-team dependencies will be arbitrated;
- maintenance ownership, on-call ownership, budget, and skill gaps;
- how pilot knowledge transfers to a second team instead of remaining bound to heroes.

**Report requirement**
- Include an `Ownership & Incentive Map`.
- State organizational actions required for scaling.
- Identify obstacles caused not by code but by responsibility, incentives, approvals, or resources.

---

# Part II — Analysis Rhythm: From Facts to System Renewal

## Phase 0: Define the Mission and What Must Not Be Lost

Before deep code inspection, record:

- the business mission: what the system must protect today;
- outcomes the user seeks to improve;
- non-interruptible flows and compliance, security, or data floors;
- protected floors that must not be crossed, experimentable variables that can be changed safely, and unresolved debates to defer until evidence exists;
- analysis mode or execution authorization boundary;
- available time, environments, testing, and deployment capability.

When these are unknown, do not stop analysis. List them in the report as `Assumptions Requiring Confirmation`, and avoid irreversible recommendations based on unverified assumptions.

---

## Phase 1: Build the Fact Ledger and Actual Operating Map

Explore first:

1. directory structure, build manifests, package or service boundaries, entry points, and deployment scripts;
2. critical business flows and their data, event, and invocation paths;
3. hot files, oversized modules, cyclic dependencies, copied logic, adapter layers, feature flags, and compatibility branches;
4. test distribution, CI/CD, environment differences, and rollback methods;
5. observability, alerts, incident clues, and manual compensation paths;
6. discrepancies between architecture documentation and code reality.

### Hotspot Evidence Collection — perform where repository access and permissions allow

- **Git churn:** recently high-change files, repeatedly reverted or hotfixed regions, ownership concentration.
- **Complexity:** oversized files or functions, cyclic dependencies, branching complexity, duplicated expansion points.
- **Operational drag:** incidents, alerts, SLO regressions, manual data correction or compensation, support tickets.
- **Delivery drag:** build or test duration, release blockage, cross-team waiting, repeated merge conflicts.
- **Business impact:** affected orders, requests, revenue, compliance obligations, or critical experience flows.

If commit history, production telemetry, or incident data cannot be obtained, state the evidence gap. Do not assume that the most complex code is the most worthwhile code to change first. In that case, a valid first pilot may be establishing observability and attribution capability.

### Fact Ledger Format

| ID | Verifiable Fact | Evidence Location | Capability Impact | Unknown / Required Validation |
|---|---|---|---|---|
| F-01 | Example: order-state transitions are spread across five entry points | `path:line`, call graph | one rule change requires synchronized edits | production exception frequency |

Rule: **Facts, interpretations, and recommendations must be separated. Never present inference as evidence.**

---

## Phase 2: Identify the Dominant Constraint Instead of Listing Every Debt Item

Classify findings as follows:

| Category | Meaning | Default Action |
|---|---|---|
| Capability-blocking debt | Directly blocks delivery, reliability, or new business capability | Find a breakthrough first |
| Stability-contract debt | Looks poor but carries real compatibility or reliability duties | Identify contracts before moving it |
| Scaling-obstacle debt | One team can solve it, but success cannot be replicated | Build templates, platform capability, or contracts |
| Adoption-mismatch constraint | Benefits, migration cost, authority, or operational ownership are misaligned | Redesign owner, budget, approval, or rollout economics |
| Tolerable legacy debt | Unattractive but barely interferes with capability | Do not invest now |
| Knowledge gap | No telemetry, no tests, or no explanatory ownership | Establish fact-generating capability first |

### Dominant Constraint Statement Template

> The constraint most worth relieving first is **[constraint]**, because evidence shows that it affects **[capabilities or flows]**, and its relief would open **[subsequent space]**. Its primary cause appears to be **[technical / procedural / incentive / risk / capability / knowledge]**. In contrast, **[tempting but lower-priority refactor]** has not yet shown comparable benefit. Confidence is **[high / medium / low]**, and the critical unknown is **[unknown]**.

---

## Phase 3: Propose Routes Only When They Can Become Pilots

Every candidate recommendation must answer:

1. **Real problem:** What is the evidence?
2. **Suppressed evolutionary capability:** What remains unavailable without change?
3. **Why the debt persists:** Is the cause technical, procedural, incentive-related, risk-related, capability-related, or an outdated assumption?
4. **Rejected empty argument:** Which plausible-sounding claim lacks proven value?
5. **First breakthrough boundary:** What is the minimum verifiable slice?
6. **Protect / Experiment / Defer:** What must not break, what can be safely varied, and what debate should wait for facts?
7. **Pilot-to-decision contract:** Which unknown will the pilot resolve, and what observed result leads to expand, revise, pause, rollback, or stop?
8. **Pilot contract:** Scope, signals, timebox, rollback, and stop conditions.
9. **Stability floor:** Data, security, compatibility, SLO, and cost constraints.
10. **Transition mechanism:** Should the pilot use a feature flag, canary, shadow execution, ACL, Facade, Strangler, or expand-contract approach, and why is it specifically applicable?
11. **Escape hatch:** What threshold triggers which fallback action, by whom?
12. **Scale route:** How will success be standardized and replicated?
13. **Adoption economics:** Who benefits, who pays migration and dual-run cost, who owns operational risk, who can approve, and what mismatch must be resolved?
14. **Ownership and collaboration:** Who owns the work, who benefits, and who bears migration burden?
15. **Evidence and confidence:** Which parts come from inspected evidence and which need measurement?

---

## Phase 4: Rank by Capability Benefit, Stability Risk, and Replicability

Score every recommendation from 1 to 5:

- `Development Benefit`: potential to release delivery, reliability, business, or cost capability.
- `Pilotability`: ability to make a bounded first step with reliable rollback.
- `Stability Risk`: production, data, security, compliance, and organizational continuity risk; 5 is highest risk.
- `Replicability`: ability for pilot learning to scale.
- `Evidence`: strength of current evidence.
- `Cost`: engineering, collaboration, and transition cost; 5 is highest cost.

A permissible prioritization heuristic, not false mathematical precision:

```text
Priority Potential = 2 * Development Benefit + Pilotability + Replicability + Evidence - Stability Risk - Cost
```

Any recommendation with `Stability Risk >= 4` and no reliable rollback route must not be classified as `Pilot Now`.

### Four Decision Labels

- **Pilot Now:** Benefit is material, boundary is controllable, and evidence is sufficient.
- **Gather Evidence Then Pilot:** Direction may be valuable, but telemetry, testing, or boundary clarification must come first.
- **Stage for Later:** Benefit is large, but current stability risk or organizational cost is too high.
- **Do Not Advance Now:** Primarily aesthetic modernization, technology preference, or insufficient return.

---

## Phase 5: Design the Route from One Breakthrough to Broad Capability

For each `Pilot Now` recommendation, provide a three-stage route.

### Stage One: Controlled Pilot

- one accountable owner;
- limited scope, traffic, tenants, or functionality;
- observe first, then switch behavior;
- withdrawal possible through a single release or clearly defined steps;
- explicit unknown, success branch, failure branch, and pause condition;
- capture both success and failure facts.

### Stage Two: Standardized Replication

- convert manual pilot knowledge into contracts, templates, tools, and automated tests;
- enable a second team to reproduce success without excessive dependence on original authors;
- confirm that the second team receives visible benefit and has capacity, approval, and operating responsibility;
- account for the cost of dual running, compatibility layers, and temporary flags.

### Stage Three: Scale-Out and Old-Path Retirement

- prioritize the next migration domains by risk and benefit;
- maintain a migration dashboard, stability floors, and exit gates;
- explicitly retire the old path once coverage and reliability thresholds have been reached, avoiding permanent coexistence.

---

## Phase 6: Execution Mode Constraints

Enter Execution Mode only when the user explicitly requests code modifications. During execution:

1. Change only the confirmed pilot boundary; never expand local authorization into repository-wide transformation.
2. Record baselines, validation methods, and rollback methods before change.
3. Prefer adding observability, contract tests, feature flags, compatibility seams, or migration scaffolding before behavioral cutover.
4. Explain which pilot hypothesis each change implements.
5. Run feasible tests, builds, and static checks, and honestly report anything not validated.
6. Stop expansion and return to diagnosis and correction if a stability floor is breached.
7. Do not defend a route merely because investment has already been made.

---

# Part III — Multi-Lens Cross-Review

For the 3–7 highest-impact recommendations, complete at least the following cross-review:

| Lens | Required Question |
|---|---|
| Evidence First | What hard evidence supports the conclusion, and what remains unknown? |
| Capability Benefit | Who becomes faster, safer, or less costly, and how will it be observed? |
| Outcomes Over Schools | Is a technology label causing overvaluation or undervaluation? |
| Dominant Constraint | Why change this first instead of a more visually attractive refactor? |
| Protect / Experiment / Defer | What must not break, what can be tested, and what should wait for evidence? |
| Reversible Validation | How does the first small step validate rather than merely explore? |
| Stability | What can fail, what will be damaged, and how is loss limited? |
| Acceleration and Guardrails | Are acceleration and governance mechanisms being built together? |
| Open Learning | Can mature external capability be reliably used? |
| Pilot-to-Decision Contract | Which missing fact does the pilot produce, and how do results change the next step? |
| Replication and Scale | Can success be reproduced without heroes? |
| Ownership and Transfer | Who has authority, accountability, capacity, benefit, and adoption cost? |

---

# Part IV — Pseudo-Optimizations to Avoid

This skill must not output any of the following unless it also supplies facts, boundaries, and a validation route:

1. **Slogan rewrite:** “Move everything to microservices,” “move everything to cloud,” or “rebuild the platform” without a first value slice.
2. **Aesthetics replacing capability:** Code becomes prettier but no improvement to delivery, reliability, or business capacity is demonstrated.
3. **Stability as permanent inaction:** Risk is used to reject all bounded, reversible validation.
4. **Risk portrayed as courage:** Core systems are switched without identifying compatibility, data, SLO, or compliance impact.
5. **Fake pilot:** A demo with no real pain or no representation of scale-out difficulty is used as proof.
6. **Hero engineering:** Success relies on a single irreplaceable person.
7. **Permanent dual running:** A new platform is introduced without retirement plans or cost accounting for the old path.
8. **Technology camp debate:** A solution is selected by identity rather than common outcome criteria.
9. **Ignoring organizational constraints:** The report assumes responsibility, budget, approvals, on-call duties, and training solve themselves after code is merged.
10. **Certainty without evidence:** Absolute conclusions are stated without inspecting code, configuration, or metrics.

---

# Part V — Markdown/HTML Report Specification: Pragmatic Engineering Renewal Decision Map

## 1. Report Objective

The default final deliverable is a single offline-browsable HTML report that allows project decision makers and frontline engineers to answer together:

- What is the actual capability bottleneck?
- Which point is most worth breaking through first?
- How can a pilot safely prove the route?
- How can a local result become system capability?
- Which stability floors must never be crossed?
- How should review feedback feed the next implementation round?

A Markdown source report is an upgrade artifact for follow-up agent handoff or source-file delivery. It is produced only when the user explicitly requests it, or when HTML generation is infeasible.

Default filenames:

- `pragmatic_renewal_architect_report_{YYYYMMDD}_{HHMM}.html` (default formal deliverable)
- `pragmatic_renewal_architect_report_{YYYYMMDD}_{HHMM}.md` (upgrade artifact; generated on explicit request or as HTML fallback)

Include timestamp to prevent overwrites across multiple runs. When a Markdown source report is produced, HTML and Markdown must share the same Fact Ledger, candidate IDs, pilot IDs, decision gates, and conclusions. HTML may add visual navigation, review controls, and feedback export, but it must not introduce judgments absent from the underlying analysis or Markdown source.

Provide the saved report path and a clickable `file://` URL. Open the report only
when the user requests a preview or the environment explicitly supports
interactive preview without CI, SSH, or headless side effects.

---

## 2. Visual Design and Layout

- Default dark theme with a background near `#15191f`; avoid harsh pure-black and pure-white contrast.
- Titles should be concise and practical; do not write the report as a manifesto or non-engineering narrative.
- Left-side sticky table of contents with scroll-linked current-section highlighting.
- Present key content through cards, badges, and grouped tables.
- Badge semantics:
  - `Breakthrough Value`: green;
  - `Stability Risk`: red;
  - `Pilot`: blue;
  - `Evidence Needed`: yellow;
  - `Do Not Advance`: gray.
- Every recommendation begins with a decision conclusion, followed by evidence and details.

---

## 3. Mandatory Report Structure

### 0. Cover and One-Sentence Decision

- Project, analysis scope, date, mode, and evidence completeness.
- One-sentence conclusion: current dominant constraint and recommended first breakthrough point.
- Explicit statement that a diagnostic report is not authorization to implement.

### 1. Executive Summary: What Should Be Done Now

- Up to three `Pilot Now` recommendations.
- Up to three `Gather Evidence Then Pilot` recommendations.
- Up to three `Do Not Advance Now` recommendations.
- Stability floors.
- Leadership decisions or resources required.

The executive summary must present scannable decisions before detailed evidence. Place long evidence, code extracts, and metric details in collapsible areas or evidence appendices so methodological completeness does not conceal action.

### 1A. Tactical Entry Map: Hotspot × Churn × Business Impact

Where evidence is available, include a compact hotspot table or scatter view showing candidate scopes with high change rate, high complexity or incident drag, and significant business impact. Clearly mark the recommended first `Pilot Cell`. Where data is not available, show missing evidence and how to collect it; never impersonate hotspot analysis with subjective ordering.

### 2. Fact Ledger and Actual System Map

- File, module, business-flow, deployment, and testing overview.
- Fact Ledger.
- Unknowns and analysis blind spots.

### 3. Global Matrix: Capability Benefit × Stability Risk

Use CSS Grid or SVG to render a scatter matrix:

- X axis: `Stability Risk / Transition Cost`, low to high.
- Y axis: `Development Benefit`, low to high.
- Each recommendation is a clickable point that scrolls to its card.
- Mark the priority region: high benefit, low or controllable risk, strong pilotability.

A point label or tooltip may additionally display `Pilotability` and `Evidence`.

### 4. Dominant Constraint Judgment

- Why this is a real problem.
- Why another more visible refactoring theme is not prioritized.
- Affected flows.
- Opportunity cost of inaction.
- Confidence and falsification conditions.

### 5. Detailed Recommendation Cards

Each card must include:

- Title and decision label: `Pilot Now / Gather Evidence Then Pilot / Stage for Later / Do Not Advance Now`.
- Quantified badges: `Development Benefit`, `Pilotability`, `Stability Risk`, `Replicability`, `Cost`, `Evidence`.
- Lens traceability badges, such as `Evidence First`, `Reversible Validation`, and `Acceleration and Guardrails`.
- **Evidence and impact:** paths, classes, functions, configuration, or metric evidence.
- **Why it has persisted:** technical and organizational causes stated separately.
- **Rejected empty proposal:** why a plausible broad idea cannot simply be adopted.
- **Protect / Experiment / Defer:** protected floors, safe variables, and unresolved debates.
- **Current vs Breakthrough** two-column comparison: red current state and green first breakthrough.
- **Pilot-to-decision contract:** unknown to resolve, scope, owner, metrics, timebox, first validation checkpoint, result branches, rollback, stop conditions.
- **Selected transition mechanism:** for example `feature flag / canary / shadow / ACL / Facade / Strangler / expand-contract`, with explanation of why it applies.
- **Escape hatch:** fallback threshold, executor, operational path, and acceptable loss.
- **Stability floors.**
- **Adoption economics:** beneficiaries, cost bearers, approval authority, operational owner, blockers, and required resource or responsibility changes.
- **Route from local to broad capability:** standardization assets, second-team adoption economics, next expansion domains, and old-path retirement conditions.
- **Falsification and blind spots:** what evidence would reverse the recommendation.
- Collapsible detail areas: evidence extracts, call chains, pseudocode, and migration steps.

### 6. Pilot Evolution Board

Display phases:

- `0–1`: gather evidence and establish observability;
- `1–2`: controlled pilot;
- `2–3`: reproduction by a second team;
- `3–4`: scale-out and retirement of the old path.

For each phase list:

- intended result;
- responsible role;
- acceptance signal;
- stability gate;
- rollback or stop action.

### 7. Ownership & Incentive Map

Show:

- who is owner;
- who bears transition cost;
- who receives benefit;
- who controls approvals or key dependencies;
- required changes to responsibility, budget, process, training, or on-call ownership.

### 8. Self-Review

- Areas not read or not validated.
- Conclusions based on inference rather than fact.
- Business constraints the user must supply.
- Places where this round is most likely to be wrong.

### 9. Interactive Review and Export

Each recommendation card can be scored, assigned a review status, and commented on. Store review state in `localStorage` and export it as Markdown for the next round.

---

## 4. Mermaid Topology Diagram Requirements

### Mermaid Import — Must Be Included in `<head>`

Use the Mermaid initialization pattern provided by the `reviewable-html-report` capability. In this repository, `skills/reviewable-html-report/references/report_base.md` is an optional reference, not a standalone dependency. This skill's theme uses:

```html
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
mermaid.initialize({
  startOnLoad: true,
  theme: 'dark',
  themeVariables: {
    fontSize: '16px',
    primaryColor: '#334155',
    primaryTextColor: '#e2e8f0',
    primaryBorderColor: '#64748b',
    lineColor: '#94a3b8',
    secondaryColor: '#1e293b',
    tertiaryColor: '#334155',
    nodeBorder: '#64748b',
    clusterBkg: '#1e293b',
    clusterBorder: '#475569',
    titleColor: '#e2e8f0',
    edgeLabelBackground: '#1e293b'
  }
});
</script>
```

Follow the Mermaid compatibility rules from the `reviewable-html-report` capability when available; otherwise preserve readable Mermaid source and disclose the rendering limitation.

### Topology Comparison for Each Key Recommendation

For every `Pilot Now` or `Stage for Later` recommendation, generate two full-width Mermaid diagrams below the comparison card, not inside the cramped two-column area:

1. **Current Blocked Topology:** Show how legacy debt produces coupling, waiting, manual compensation, concentrated risk, or blocked evolution.
2. **Breakthrough and Rollout Topology:** Show the pilot boundary, protection mechanism, observability and rollback, scale-out interface, and direction of old-path retirement.

Required HTML structure:

```html
<div class="topology-compare">
  <div class="topology-diagram current">
    <div class="label">Current Blocked Topology</div>
    <div class="mermaid">...</div>
  </div>
  <div class="topology-diagram elevated">
    <div class="label">Breakthrough and Rollout Topology</div>
    <div class="mermaid">...</div>
  </div>
</div>
```

### Strict Mermaid Compatibility Rules

1. Do not use emoji inside Mermaid code. Node labels must use ASCII or ordinary text without badge icons.
2. Use `flowchart TB`, `flowchart LR`, or `flowchart TD`; never use `graph`.
3. Do not use `linkStyle` directives.
4. Use `subgraph g1["Display Label"]` formatting.
5. Avoid complex punctuation and special path symbols inside node text; simplify displayed paths.
6. Do not add `%%{init:...}%%` blocks in individual diagrams; use only the global theme initialization.
7. `.topology-diagram .mermaid` must have `min-height: 380px; width: 100%;`.
8. Use red semantic borders for the Current diagram and green semantic borders for the Breakthrough diagram.
9. Every topology diagram must be clickable to open a full-screen lightbox and support `Escape` to close.

### Required Topology CSS

```css
:root {
  --topo-bg: #15191f;
  --topo-current-label-bg: rgba(248,81,73,0.15);
  --topo-current-label-color: #f85149;
  --topo-current-border: rgba(248,81,73,0.25);
  --topo-elevated-label-bg: rgba(63,185,80,0.15);
  --topo-elevated-label-color: #3fb950;
  --topo-elevated-border: rgba(63,185,80,0.25);
  --lb-backdrop: rgba(0,0,0,0.88);
  --lb-content-bg: #15191f;
}
@media (prefers-color-scheme: light) {
  :root {
    --topo-bg: #f4f6f8;
    --topo-current-label-bg: rgba(220,53,69,0.1);
    --topo-current-label-color: #dc3545;
    --topo-current-border: rgba(220,53,69,0.18);
    --topo-elevated-label-bg: rgba(25,135,84,0.1);
    --topo-elevated-label-color: #198754;
    --topo-elevated-border: rgba(25,135,84,0.18);
    --lb-backdrop: rgba(255,255,255,0.94);
    --lb-content-bg: #ffffff;
  }
}
.topology-compare { display: flex; flex-wrap: wrap; gap: 20px; margin-top: 24px; }
.topology-diagram { flex: 1; min-width: 340px; cursor: pointer; }
.topology-diagram .mermaid { min-height: 380px; width: 100%; background: var(--topo-bg); }
.topology-diagram .label { font-size: 14px; font-weight: 600; margin-bottom: 8px; padding: 4px 12px; border-radius: 4px; display: inline-block; }
.topology-diagram.current .label { background: var(--topo-current-label-bg); color: var(--topo-current-label-color); }
.topology-diagram.current .mermaid { border: 2px solid var(--topo-current-border); border-radius: 8px; padding: 16px; }
.topology-diagram.elevated .label { background: var(--topo-elevated-label-bg); color: var(--topo-elevated-label-color); }
.topology-diagram.elevated .mermaid { border: 2px solid var(--topo-elevated-border); border-radius: 8px; padding: 16px; }
.lightbox { display: none; position: fixed; inset: 0; z-index: 9999; background: var(--lb-backdrop); cursor: pointer; }
.lightbox.active { display: flex; align-items: center; justify-content: center; }
.lightbox .mermaid { min-width: 700px; min-height: 500px; max-width: 94vw; max-height: 92vh; overflow: auto; background: var(--lb-content-bg); border-radius: 8px; padding: 24px; }
```

### Required Lightbox JavaScript

Use the lightbox behavior from the `reviewable-html-report` capability when available. Otherwise provide a self-contained static fallback without making browser-only behavior a completion requirement.

---

## 5. Interactive Review System — Mandatory Vanilla JavaScript Implementation

### Each Recommendation Card Must Include

- A comment `<textarea>`.
- A 1–5 star acceptance score.
- Status tags:
  - `[Agree to Pilot]`
  - `[Direction Accepted; Gather Evidence First]`
  - `[Concerned About Stability Risk]`
  - `[Already Exists / False Positive]`
  - `[Not Aligned with Business Priority]`
- Persist all feedback through `localStorage` so it survives refresh.

### Export Feedback FAB

Add a fixed bottom-right button: `Export Review for Next Round`.

When clicked:

1. Iterate through every recommendation card containing a rating, status, or comment.
2. Concatenate Markdown containing the card title, recommendation decision, rating, status, and review text.
3. Append the following directive **exactly and in full** at the very end of the Markdown:

```text
[Next Round Action Directive] Incorporate my review from the perspective of pragmatic engineering renewal: do not advance a proposal merely because it is conceptually elegant, and do not stop action merely because the legacy system is complex. First revise the dominant-constraint judgment according to evidence, then re-rank the recommendations by capability benefit, pilotability, stability floor, replication and scale cost, accountable ownership, and rollback capability. For directions I approved that already have sufficient evidence and safety boundaries, provide a minimum executable pilot package, acceptance metrics, rollback plan, and path from local validation to scaled adoption. Only modify code directly within a scope I have explicitly authorized for implementation. For directions I challenged, clearly state why they are retained, revised, or abandoned.
```

4. Use `navigator.clipboard.writeText(markdown)` to write the output to the clipboard.
5. Show a Toast or alert: `Copied. Paste directly into AI for the next pragmatic renewal review round.`

### Table-of-Contents Scroll Linkage

Use `IntersectionObserver` to highlight the active left-side TOC section during scroll. Anchor clicks must scroll smoothly.

---

# Part VI — Report Voice and Output Standard

## The Report Should Read Like

- An engineering evolution proposal written by a chief architect accountable for real production outcomes.
- A document that states facts and key judgments before explaining concepts.
- A plan that sees long-term capability and first-step feasibility at the same time.
- A report that admits unknowns and provides validation methods.
- A review that answers opposition with pilots, boundaries, and results rather than labels.

## The Report Must Not Read Like

- A quotation collection.
- A manifesto to overthrow the existing system entirely.
- A document that turns every technical debt item into a strategic opportunity.
- A plan that abandons architectural direction in the name of short-term execution.
- A plan that rejects all improvement in the name of stability.
- An instruction to modify code without authorization.

---

# Part VII — Final Delivery Checklist

In Diagnostic Mode or Pilot Design Mode, the final response must include:

1. The HTML report file path or clickable link (default formal deliverable).
2. The Markdown source report path or clickable link, only when produced (user explicitly requested an agent handoff / source-file delivery, or HTML generation was infeasible).
3. A one-sentence summary of the dominant constraint and preferred first breakthrough point.
4. The largest unknown or risk in the current analysis.
5. A statement that no code has been modified.

In Execution Mode, the final response must additionally include:

1. The list of files actually changed.
2. The mapping from modifications to pilot hypotheses.
3. Validations run and their results.
4. Validations not run and why.
5. Rollback instructions.
6. Whether pilot expansion is recommended, and on what evidence.

---

# Execution Summary

1. Explore the project and establish the Fact Ledger.
2. Combine churn, complexity, incident or delivery drag, and business impact to identify the dominant constraint that truly suppresses capability.
3. Distinguish stability-carrying legacy contracts from capability-blocking debt that deserves priority action.
4. Compare candidate routes using outcome standards rather than technology identity.
5. Choose a controllable, observable, reversible, replicable first `Pilot Cell`.
6. Design applicable transition mechanisms, such as flags, canaries, shadows, ACLs, or Strangler seams, together with escape hatches, stability floors, ownership, and replication paths.
7. Generate the interactive HTML engineering renewal decision report as the default formal deliverable. Generate a Markdown source report only when the user explicitly requests an agent handoff or source-file delivery, or when HTML generation is infeasible; when both exist, they share the same facts and decisions.
8. Modify code only after the user explicitly authorizes execution within the pilot boundary.
9. Let pilot facts determine correction, scaling, or termination rather than defending an existing idea.
