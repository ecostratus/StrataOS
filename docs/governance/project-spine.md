# Project Spine: Job Discovery Subsystem

## Current Phase
- v0.2.0Phase2E (stable, documented, fully tested)

## Completed Phases
- Phase2A: First behavior
- Phase2B: Hardening + integration
- Phase2C: Observability + deterministic behavior
- Phase2D: Real ingestion + JSONL logging
- Phase2E: Documentation, SOPs, mapping references, toggles, CLI refinements, full test coverage

## Phase3 Goals
- Enrichment and scoring pipeline
- Scheduling/automation + persistent storage
- Extended sources + configurable transformations
- Log/metrics aggregation + rotation
- Multibehavior orchestration (discovery  enrichment  outreach)

## Phase3 Milestones
- 3A: Enrichment + Scoring
  - Goals: enrich canonical jobs (skills/keywords), compute scores via config weights, export enriched artifacts.
  - Constraints: deterministic transforms and UTC timestamps; no external deps that break tests.
  - Deliverables: enrichment module, scoring config, enriched CSV/JSON; unit + integration tests.
- 3B: Scheduling + Automation + Persistent Storage
  - Goals: scheduled runs (daily), store artifacts in SQLite/JSON; retention policy.
  - Constraints: configdriven schedule; CLI defaults unchanged.
  - Deliverables: scheduler tasks/scripts, storage layer, retention controls; tests for schedule hooks and storage writes.
- 3C: Extended Sources + Configurable Transformations
  - Goals: add 12 sources; introduce configurable field transforms and normalization profiles.
  - Constraints: scrapers safe (never throw); strict canonical mapping.
  - Deliverables: new fetchers, transform config, fixtures; mapping/transform tests.
- 3D: Log/Metrics Aggregation + Rotation
  - Goals: aggregate logs/metrics across runs; rotate JSONL; provide summary dashboards.
  - Constraints: configdriven rotation; preserve structured log format.
  - Deliverables: aggregator utilities, rotation policy, dashboards; tests for aggregation/rotation.
- 3E: MultiBehavior Orchestration
  - Goals: orchestrate discovery  enrichment  optional outreach; keep orchestrators thin.
  - Constraints: avoid coupling scrapers with enrichment/outreach logic.
  - Deliverables: orchestration pipeline, CLI flags, E2E tests; deterministic artifacts.

## Governance Rules
- Keep orchestrators thin; scrapers safe; configdriven behavior.
- Preserve backwardcompatible CSV format and public APIs.
- Maintain deterministic outputs and UTCsafe timestamps.
- Require comprehensive tests and documentation for all new features.

## DriftPrevention Guardrails
- Strict canonical field mapping; normalize dates to YYYYMMDD.
- Fixturebacked tests for new sources and transforms.
- Document any new config keys; align `env.sample.json` with mappings.
- Ensure JSONL logging and metrics remain structured and aggregable.
