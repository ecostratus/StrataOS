# Schemas (v1)

## Canonical

- `person.schema.json`
- `opportunity.schema.json`
- `observation.schema.json`
- `evidence.schema.json`
- `claim.schema.json`

## Derived

- `decision.schema.json`
- `recommendation.schema.json`

## Operational

- `policy.schema.json`
- `trace_artifact.schema.json`

## Versioning Notes

- Additive fields are allowed in minor versions.
- Breaking schema changes require major version bump and migration ADR.

## Reproducibility Conventions

- `decision_model_version` is required in claim, decision, recommendation, and trace artifacts.
- Decision records include `inputs_hash`, `policy_hash`, `engine_hash`, and `fixture_hash`.
- Evidence provenance captures multi-stage lineage fields: parser, normalizer, evidence builder, and claim generator.
