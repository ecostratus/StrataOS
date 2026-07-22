# ADR-005: Deterministic Recommendations

## Status

Accepted

## Decision

The decision layer is deterministic and reproducible for identical inputs.

## Rationale

- Essential for trust, testing, and debugging.
- Establishes stable baseline before adaptive inference layers.

## Consequences

- Decision inputs must be versioned and hashable.
- Recommendation generation must avoid nondeterministic ordering.
