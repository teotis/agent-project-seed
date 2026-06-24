# Discovery Patterns for Structural Abstraction

Use this reference when a structural analysis is open-ended, when the first
candidate abstraction feels obvious but weak, or when the codebase shows several
different pressure signals at once. The goal is to generate better candidate
structures before the Admissibility Gate judges them.

Do not paste this reference into the final report. Use it to guide discovery,
then report only evidence-backed findings.

## Discovery Passes

Run these passes before recommending a high-leverage abstraction. They are
different ways to probe the same system.

### 1. Data Lifecycle Pass

Trace one representative entity or event from creation to final consumption.

Look for:
- repeated representations of the same semantic object;
- conversions that lose or re-infer meaning;
- lifecycle transitions encoded in unrelated layers;
- validation rules repeated after every projection;
- fields whose meaning changes across storage, API, UI, jobs, and reports.

Candidate structures often found:
- canonical domain object;
- explicit lifecycle state machine;
- event log plus projections;
- typed boundary contract;
- projection registry with one authority per invariant.

Disproof signals:
- the variants only share names, not rules;
- each stage has genuinely different ownership or failure semantics;
- the proposed model makes critical local rules harder to see.

### 2. Caller Reality Pass

Study how callers use, wrap, avoid, or compensate for the API or module.

Look for:
- repeated pre-processing before calls;
- repeated defensive checks after calls;
- call ordering assumptions not expressed in the API;
- impossible states that callers must filter out;
- wrappers that make the provider usable.

Candidate structures often found:
- API redefined from caller intent;
- capability-oriented interface;
- richer return/result type;
- structure-preserving transformation protocol;
- task object or operation object.

Disproof signals:
- caller workarounds are unrelated local preferences;
- a provider-side abstraction would erase necessary caller-specific rules;
- the proposed API makes simple callers pay for rare cases.

### 3. Failure And Recovery Pass

Trace incidents, retries, compensating jobs, manual repair instructions, and
status mismatches.

Look for:
- recurring failure families handled by patches;
- repair scripts that know hidden invariants;
- states that mean different things in different artifacts;
- retries that need context not present in the state model;
- manual recovery steps that could be local-to-global gluing rules.

Candidate structures often found:
- explicit recovery state machine;
- canonical process object;
- append-only event stream plus current snapshot;
- failure taxonomy with retry policy;
- local consistency rules before global completion.

Disproof signals:
- failures are independent operational issues, not one missing invariant;
- the proposed recovery model needs a central coordinator for everything;
- retry/recovery rules depend on external judgment that cannot be encoded safely.

### 4. Environmental Variation Pass

Compare behavior across platforms, tenants, protocols, runners, permission
modes, dependency versions, or deployment environments.

Look for:
- duplicated lifecycle logic per environment;
- branch families that differ only by capability;
- config values that imply hidden policy;
- platform-specific adapters that reimplement the same transformation;
- tests copied with only environment-specific setup changes.

Candidate structures often found:
- base-change capability model;
- policy object;
- plugin boundary with invariant-preserving core;
- generated configuration from a canonical source;
- runner/environment projection of one workflow object.

Disproof signals:
- environment differences are essential product differences;
- the abstraction hides security, ownership, or compliance distinctions;
- the shared core becomes weaker than the variants it replaces.

### 5. Observational Probe Pass

Before treating two representations as one concept, or choosing between rival
structural explanations, check whether the available evidence can actually
distinguish them.

List the relevant probes:
- callers and call ordering;
- tests and failure injection;
- queries, serializers, reports, and UI projections;
- telemetry and operational alerts;
- authorization and policy checks;
- repair scripts, retries, compensation, and recovery paths.

For each candidate, ask:
- Relative to which observer, operation, or context do the objects appear
  equivalent?
- Which meaningful differences are visible to current probes, and which remain
  unobserved?
- What information is lost during projection or conversion, and is that loss
  allowed, traceable, or recoverable?
- Which important invariant has no probe capable of validating it?
- What separating probe would expose a difference in lifecycle, ownership,
  ordering, failure, security, or recovery semantics?

A compact `Candidate × Probe` matrix is often enough:

| Probe | Candidate A | Candidate B | Distinguishing power |
|---|---|---|---|
| Caller ordering | Precondition owned by caller | Ordering enforced internally | Strong |
| Recovery script | Shared repair rule | Context-specific repair rule | Strong |
| Serialization | Same fields | Same fields | Weak |
| UI status | Both show complete | Both show complete | None |

Candidate structures often found:
- observation-relative equivalence contract;
- missing lifecycle or failure dimension;
- bounded contexts that only look identical through low-resolution projections;
- a separating test, runtime probe, or recovery scenario needed before unification.

Disproof signals:
- the proposed probe cannot observe the claimed invariant;
- all available probes are derived from the same lossy projection;
- the analyst selects a candidate by elegance when current evidence cannot
  distinguish the rivals.

## Candidate Competition

For high-value pressure sites, generate at least two plausible structural
explanations before recommending one. A candidate is an explanation of why the
complexity exists, not just a proposed implementation.

Compare candidates on:
- evidence fit: which concrete files, callers, states, tests, or incidents it
  explains;
- deletion power: which representations, adapters, branches, coordinators, or
  workflow steps disappear;
- difference preservation: which similar cases remain intentionally separate;
- deformation power: what future change becomes cheap;
- transition seam: how it can be piloted without a broad rewrite;
- disproof signal: what would prove it wrong.
- observational adequacy: which probes distinguish the candidates, which
  blind spots remain, and whether a separating probe is still required.

Common competing explanations:

| Pressure | Candidate A | Candidate B | Candidate C |
|---|---|---|---|
| Many status enums | Canonical lifecycle object | Bounded contexts should stay separate | Event log with projections |
| Adapter mesh | Canonical representation | Transformation protocol | Boundary should be collapsed |
| God coordinator | Local-to-global composition | Central policy is genuinely required | Process object plus projections |
| Platform branches | Base-change capability model | Plugin boundary | Separate products with shared utilities |
| UI control sprawl | Task object | Direct manipulation surface | Guided state machine |
| Workflow drift | Canonical process object | Event stream plus snapshot | Manual gate made explicit |

Recommend a candidate only after explaining why the nearest rival is weaker,
too risky, or missing evidence. If the candidates delete different complexity,
report them as separate proposals instead of forcing one winner.
When current probes cannot distinguish the nearest rivals, classify the result
as unproven and name the separating evidence required instead of choosing by
preference.

## Definition Quality Checks

A strong structural definition should make future work feel obvious.

Ask:
- What is the object now called, and what invariant defines it?
- What are its legitimate projections?
- What local facts can compose into a global fact?
- Which differences are parameters, and which are separate concepts?
- What branch, adapter, status, or manual step disappears?
- What future variant becomes a trivial projection?
- What counterexample would force us to split the object again?
- Which observer or probe can distinguish this definition from its nearest
  rival, and which invariant remains in an observation blind spot?

If the answers are vague, the proposal is not ready for recommendation. Put it
in `Promising but unproven hypothesis` or `False abstraction risk`.
