# Architecture Review Checklist

Use this checklist for every pull request that touches the decision model or its execution engine.

## Core Impact

- Does this change introduce a new entity?
- Does this change alter a canonical schema?
- Does this change modify claim semantics?
- Does this change alter decision or recommendation semantics?

## Governance

- Is a new ADR required?
- Does an existing ADR become superseded?
- Does this require schema version bumping?
- Is migration guidance needed for persisted artifacts?

## Determinism and Reproducibility

- Could this change affect deterministic behavior?
- Are replay, order-independence, and idempotence tests still passing?
- Does this change affect `inputs_hash`, `policy_hash`, `engine_hash`, or `fixture_hash` semantics?
- Can the same persisted artifacts still reconstruct identical outputs?

## Explainability and Traceability

- Does the recommendation still include claim-linked drivers?
- Is the full provenance chain preserved:
  Observation -> Evidence -> Claim -> Decision -> Recommendation?
- Is trace artifact output still complete and machine-readable?

## Fixture and Contract Discipline

- Does this change modify a frozen fixture under `tests/fixtures/v1`?
- If fixture behavior changed intentionally, was a new fixture version added instead of mutating v1?
- Were snapshot/golden expectations updated only with explicit reviewer sign-off?

## API and Integration

- Does this change alter API contracts?
- Are downstream consumers impacted?
- Are compatibility and rollout notes documented?

## Security and Data Handling

- Does this change introduce sensitive fields into persisted artifacts or logs?
- Are schema validations still enforcing safe and expected payload shapes?

## Reviewer Decision

- Approve as-is.
- Approve with required follow-up items.
- Request ADR and/or schema versioning changes before merge.
