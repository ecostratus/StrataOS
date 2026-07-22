# ADR-004: Split Confidence Model

## Status

Accepted

## Decision

Maintain two separate confidence dimensions:

- `evidence_confidence`
- `prediction_confidence`

## Rationale

- Data completeness and conversion likelihood are different signals.
- Improves debugging and user trust.

## Consequences

- Decision schema must store both values.
- Recommendation UI must display both values distinctly.
