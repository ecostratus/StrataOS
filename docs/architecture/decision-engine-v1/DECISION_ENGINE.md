# Decision Engine Specification (v1)

## Purpose

Produce deterministic recommendations for a `(person, opportunity, policy)` tuple using evidence-backed claims.

## Inputs

- `person_claims[]`
- `opportunity_claims[]`
- `policy`
- `constraints[]`

## Determinism Contract

The engine must produce identical output for identical canonicalized inputs.

Determinism requirements:

- Canonical JSON serialization of all input objects.
- Stable sort for any collection before scoring.
- Hash persisted as `inputs_hash` in decision records.
- No nondeterministic RNG in scoring path.

## High-Level Algorithm

1. Validate policy and claims against schemas.
2. Canonicalize and sort inputs.
3. Evaluate hard constraints.
4. Compute weighted scoring contributions from claims.
5. Compute `evidence_confidence` from evidence quality and coverage.
6. Compute `prediction_confidence` from model/rule certainty.
7. Map score + constraints to recommendation action.
8. Emit positive and negative drivers with claim references.
9. Persist immutable decision record.

## Output

The output contract is defined by:

- `schemas/decision.schema.json`
- `schemas/recommendation.schema.json`
