# Output Risk Profile

## Primary Risks

- Omission: an original problem disappears during normalization or grouping.
- False certainty: a screenshot, user description, or code clue is presented as proof of root cause.
- Fragmented dependency closure: tightly coupled changes or verification paths are split into separate packages for cosmetic size limits.
- Arbitrary grouping: problems are grouped by numbering, visual proximity, or equal size instead of a coherent modification and verification boundary.
- Routing inflation: orchestration is recommended merely because the batch or a package is large.
- Handoff drift: downstream work cannot trace claims back to stable evidence.

## Controls

- Stable source issue IDs and an explicit input coverage checklist.
- Stable `EV-*` records with source, observation, and confidence.
- Package-to-evidence references rather than duplicated evidence prose.
- Dependency-closure-first grouping with explicit split criteria.
- A required `next_route` for every package.
- A required orchestration reason when durable coordination is recommended.
- A decision-first summary before package details.
- `scripts/validate_package_issue_report.py` for deterministic structure, coverage, evidence-reference, and route checks.

## Evaluation Note

The pre-skill baseline risk is represented by unstructured outputs that lose source IDs, fragment dependent work, omit evidence provenance, and jump from a large issue list directly to orchestration. This is a design baseline, not a live model-comparison claim. Trigger and output assertions in `evals/evals.json` cover the intended routing and report contract.
