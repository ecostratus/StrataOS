# ADR-002: Claims as Primary Reasoning Construct

## Status

Accepted

## Decision

Represent core intelligence as `Claim` objects supported by evidence.

## Rationale

- Improves explainability.
- Supports auditability and traceability.
- Decouples raw data extraction from inference.

## Consequences

- Scores become derived views.
- Recommendation payloads must include claim references.
