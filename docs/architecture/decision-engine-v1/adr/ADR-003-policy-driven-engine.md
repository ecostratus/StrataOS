# ADR-003: Policy-Driven Decision Engine

## Status

Accepted

## Decision

Use configurable policies to determine optimization behavior and trade-offs.

## Rationale

- Supports multiple optimization intents without code forks.
- Keeps engine stable while behavior changes via data.

## Consequences

- Policy schema becomes a first-class contract.
- Defaults are provided, but runtime policy selection is required for decisions.
