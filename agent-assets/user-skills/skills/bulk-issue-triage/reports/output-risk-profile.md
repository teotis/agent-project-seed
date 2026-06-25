# Output Risk Profile

## Primary Risks

- Omission: an original issue disappears during normalization or grouping.
- False certainty: a screenshot or user description is presented as proof of root cause.
- Arbitrary grouping: issues are grouped by numbering or visual proximity instead of a coherent repair path.
- Premature implementation: the report invents code-level fixes before sufficient evidence exists.
- Handoff drift: downstream planning receives incomplete packages or treats preliminary analysis as confirmed fact.

## Controls

- Stable issue IDs and an explicit input coverage checklist.
- Required observation, hypothesis, counter-evidence, unknown, and confidence fields.
- One-primary-package ownership rule with explicit cross-package relationships.
- Relative complexity bands rather than precise effort estimates.
- A fixed downstream prompt that requires `agent-orchestration-planner` to re-verify facts.
- `scripts/validate_triage_report.py` for deterministic structure and coverage checks.

## Evaluation Note

The pre-skill baseline risk is represented by common unstructured outputs that summarize issues but omit manifestations, lose issue IDs, and jump directly to fixes. This is a recorded design baseline, not a live model-comparison claim. Trigger and output assertions in `evals/evals.json` cover the intended routing and report contract.
