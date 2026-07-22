# ADR-006: Domain Pack Separation

## Status

Accepted

## Decision

Separate domain-specific knowledge into data packs loaded into a generic reasoning core.

## Rationale

- Reduces coupling between domain vocabulary and engine internals.
- Enables future domain expansion without rewriting core.

## Consequences

- Domain packs require schema validation.
- Core engine contract remains stable across packs.
