# Acceptance Criteria (v1)

## Functional Criteria

1. Engine evaluates `FTE` and `CONTRACT` opportunities.
2. Recommendation action is one of the allowed six values.
3. Recommendation includes at least one positive and one negative driver when both exist.

## Explainability Criteria

1. Each driver includes a `claim_ref`.
2. Each claim reference resolves to a claim with non-empty `evidence_refs`.
3. Decision payload contains separate `evidence_confidence` and `prediction_confidence`.

## Reproducibility Criteria

1. Re-running evaluation with identical inputs yields identical recommendation.
2. Re-run output has same `inputs_hash` and same ordered driver list.
3. Any output change must correspond to changed inputs or engine version.
4. Every recommendation must be fully reconstructable from persisted artifacts.

Reconstruction inputs:

- Person
- Opportunity
- Observations
- Policy

Reconstruction outputs:

- Evidence
- Claims
- Decision
- Recommendation
- Trace artifact

## Governance Criteria

1. All claims, policies, and decisions validate against v1 schemas.
2. Evolution policy rules are followed for extension/modification/removal.
3. ADRs exist for all breaking conceptual shifts.
