# Non-Functional Requirements (v1)

## Determinism

- Identical canonical inputs must produce identical recommendations.
- Determinism must be testable in CI using fixed fixtures.

## Performance Targets

- Single evaluation request p95 latency target: <= 300 ms (local baseline mode).
- Bulk evaluation throughput target: >= 50 evaluations per second in batch mode on baseline dev hardware.

## Explainability

- Every recommendation must include positive and negative drivers when both exist.
- Each driver must reference a claim, and each claim must reference evidence.

## Auditability

- Decision records are immutable and append-only.
- Every persisted decision must store `inputs_hash`, `policy_id`, and `engine_version`.

## Versioning

- Schemas use semantic versioning.
- Breaking schema changes require a major version bump and migration ADR.

## Security

- No secret material may be persisted in decision payloads.
- Input validation must reject malformed claims and policies before scoring.

## Privacy

- Personally identifying details must be limited to fields required for evaluation.
- Logs must avoid unnecessary duplication of sensitive source payloads.

## Observability

- Engine must emit structured logs for validation, scoring, and recommendation outcomes.
- Error events must include correlation identifiers for replay and diagnosis.

## Reproducibility

- Reproducibility tests must verify consistent outputs for fixed fixtures.
- Any recommendation drift must be attributable to changed inputs or versions.

## Extensibility

- Domain-specific behavior must be added via validated domain packs where possible.
- Core model contracts must remain stable across minor releases.
