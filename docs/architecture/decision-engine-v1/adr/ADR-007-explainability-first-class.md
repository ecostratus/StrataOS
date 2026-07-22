# ADR-007: Explainability is a First-Class Requirement

## Status

Accepted

## Decision

Every recommendation must be traceable through:

- Observations
- Evidence
- Claims
- Policy
- Decision

No opaque inference, no black-box scoring, and no unexplained output are permitted in the decision layer.

## Rationale

- Explainability is a defining product attribute, not an optional UX feature.
- Deterministic and auditable behavior depends on causal traceability.
- Human trust and policy governance require transparent reasoning artifacts.

## Consequences

- Recommendation payloads must include structured drivers with claim references.
- Claims must include evidence references and resolvable provenance.
- Any future adaptive or probabilistic engine must preserve this traceability contract.
