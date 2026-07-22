# Domain Model

This file defines canonical vocabulary for StrataOS v1.

## Core Terms

- Entity: top-level domain object with identity and lifecycle.
- Person: evaluated candidate profile.
- Opportunity: unit of evaluation (`FTE`, `CONTRACT` in v1).
- Observation: raw extracted fact from one source.
- Evidence: validated observation set with quality metadata.
- Claim: confidence-scored assertion derived from evidence.
- Capability: candidate ability inferred from claims.
- Problem Archetype: recurring enterprise problem pattern inferred from claims.
- Policy: optimization profile that configures trade-offs.
- Decision: immutable evaluation result for a person, opportunity, and policy.
- Recommendation: action label derived from decision outputs.
- Constraint: hard rule that can gate recommendation.

## Reasoning Pipeline

`Observation -> Evidence -> Claim -> Capability/Archetype -> Decision -> Recommendation`

## Relationship Summary

- A `Person` has many `Claims`.
- An `Opportunity` has many `Claims`.
- A `Claim` references one or more `Evidence` records.
- `Evidence` references one or more `Observations`.
- A `Policy` is applied to person/opportunity claims to produce one `Decision`.

## v1 Opportunity Types

- `FTE`
- `CONTRACT`
