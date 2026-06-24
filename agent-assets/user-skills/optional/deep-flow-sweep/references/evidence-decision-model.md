# Evidence And Decision Model

Use this model when recovering change intent, ranking findings, or deciding whether a candidate becomes a task package.

## Intent Recovery Chain

Build the chain in this order:

| Stage | Evidence |
|---|---|
| Requirement or task source | user request, issue, plan, acceptance criteria, runbook, release goal |
| Test oracle | behavior, state, side effect, error, performance budget, or security control the tests claim to protect |
| Implementation | code path, configuration, migration, workflow, and dependency changes |
| Runtime evidence | test result, trace, log, artifact, benchmark, browser/device observation, or strong static proof |

Record gaps and source confidence at every stage.

- Do not treat tests as the complete specification when the requirement source contradicts or exceeds them.
- Do not infer intent solely from a commit subject; compare the diff, surrounding commits, issue/plan context, and observable behavior.
- When the original requirement is unavailable, label reconstructed intent as inferred and preserve competing interpretations.
- A mismatch may be requirement drift, stale tests, incomplete implementation, or weak runtime evidence. Identify which link failed before assigning blame.

## Finding Decision Dimensions

Record **Severity, Confidence, and Disposition** separately.

### Severity

Describe impact if the claim is true:

- `P0`: demonstrated catastrophic security, data, or release impact.
- `P1`: demonstrated critical-flow failure or strong static proof on a reachable path.
- `P2`: credible bounded risk, weak recovery, regression exposure, or partial contract failure.
- `P3`: maintainability or polish value with indirect user impact.

Confirmed P0/P1 still require the skill's direct-evidence gate. A potentially severe but weakly evidenced claim is a candidate, not a confirmed P0/P1.

### Confidence

- `high`: reproducible runtime evidence or closed strong static proof.
- `medium`: multiple consistent sources with a remaining verification gap.
- `low`: plausible hypothesis, scanner signal, historical report, metric threshold, or incomplete trace.

### Disposition

- `block`: report urgently; stop expansion when the confirmed impact requires it.
- `package`: create an executable Task Package Contract.
- `investigate`: collect the named missing evidence before ranking or packaging.
- `consider`: preserve as a bounded improvement opportunity.
- `info`: retain as context, coverage debt, or a clean/negative result.
- `drop`: reject as false positive, style preference, stale evidence, or immaterial risk.

Do not use severity to express urgency, confidence, or personal preference. Two findings with the same severity may have different confidence and disposition.

## Report Contract

```markdown
## Intent Recovery
| Requirement/Task | Test Oracle | Implementation | Runtime Evidence | Gap |

## Finding Decision
- Severity:
- Confidence:
- Disposition:
- Evidence still needed:
```
