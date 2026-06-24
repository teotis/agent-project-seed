# Simplification Safety Model

Use this model before recommending removal, collapse, consolidation, extraction, or boundary changes.

## Constraint Survival Test

For every non-trivial simplification candidate, record:

| Field | Question |
|---|---|
| Current role | What behavior, boundary, ownership, compatibility, or operational purpose does it serve now? |
| Original constraint | Why was it introduced: platform variation, public API, migration, transaction, security, test isolation, framework, or organizational boundary? |
| Evidence | Which code, test, history, document, or runtime artifact supports that explanation? |
| Still valid | Does the original constraint still apply in current callers, environments, and release paths? |
| Removal model | What is the smallest concrete model after deleting or collapsing it? |
| Counter-evidence | What would prove the candidate is necessary or that simplification increases risk? |
| Decision | retain / simplify / replace / investigate / defer |

Do not equate an unknown purpose with no purpose. When the original constraint cannot be recovered, lower confidence and prefer an investigation package over deletion.

## Behavior Preservation Vector

Every simplification task package must state how it preserves each relevant dimension:

- **Inputs**: accepted values, validation, normalization, defaults, and compatibility.
- **Outputs**: values, schemas, rendering, files, persisted state, and success signals.
- **Errors**: exception types, error codes, messages, retries, cancellation, and partial failure.
- **Side effects**: writes, network calls, events, notifications, logging, cleanup, and resource ownership.
- **Operation ordering**: sequencing, transaction boundaries, callbacks, and visible completion.
- **Concurrency semantics**: locking, idempotency, thread/async behavior, races, and re-entry.
- **Performance constraints**: latency, memory, throughput, I/O, startup, or size budgets.

Mark a dimension `N/A` only with a reason. “Tests pass” is not a complete behavior preservation argument when tests do not cover the vector.

## Finding Decision Dimensions

Record **Severity, Confidence, and Disposition** separately:

- **Severity**: P0-P3 impact if the complexity claim is true.
- **Confidence**: high / medium / low based on current evidence.
- **Disposition**: block / package / investigate / consider / info / drop.

Confirmed P0/P1 require direct current evidence. A long function, single implementation, historical label, or analyzer result may justify `investigate`, but cannot justify high severity by itself.

## Task Package Addendum

```markdown
## Constraint Survival
- Current role:
- Original constraint:
- Still valid:
- Removal model:
- Counter-evidence:
- Decision:

## Behavior Preservation
| Dimension | Current contract | Verification |

## Finding Decision
- Severity:
- Confidence:
- Disposition:
```
