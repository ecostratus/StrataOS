# ADR-001: Opportunity as Primary Object

## Status

Accepted

## Decision

Use `Opportunity` as the primary evaluable object rather than `Job`.

## Rationale

- Avoids lock-in to job-search-specific semantics.
- Supports v1 with `FTE` and `CONTRACT` types.
- Enables additive expansion later.

## Consequences

- Existing job ingestion maps into `Opportunity(type=FTE)`.
- Future opportunity types can be added without replacing core model.
