# Phase 3B: Scheduling + Storage

Status: COMPLETE

Version: v0.3.0-Phase3C-Normalization

## Phase Boundary
- Completed in support of Phase 3C normalization
- No active work beyond this phase
- Downstream phases are FUTURE and out of scope

Canonical source: [Progress‑to‑Launch Checklist & Timeline](progress_to_launch_checklist_timeline.md)

## Goals
- Deterministic, config-driven scheduling with no external cron.
- Durable, queryable storage for discovery, enrichment, scoring, and run summaries.
- Predictable retention policy for pruning old runs and artifacts.
- Keep orchestrator thin; concentrate logic in pure helpers and storage backends.

## Architecture Outline
- Scheduler: In-process cadence, computed from UTC via pure helpers.
- Storage: Pluggable backend (SQLite preferred; JSON alternative), keyed by a single UTC run timestamp reused across artifacts.
- Pipeline: discovery → enrichment (opt-in) → scoring (opt-in) → persist → export → retention.
- Observability: Run summary with per-source metrics; deterministic filenames; persistence keyed by run timestamp.

## Scheduling Model
- Modes
  - Interval mode: `scheduling.mode="interval"`, `scheduling.interval_minutes=int`
  - Window mode: `scheduling.mode="window"`, `scheduling.window_time="HH:MM"` (UTC only)
- Rules
  - Pure helpers: `compute_next_run(now_utc, config)`, `should_run(now_utc, last_run_ts, config)`
  - No jitter; no local timezone conversions; determinism under frozen time
  - Missing `last_run_ts` → run immediately

## Storage Model
- SQLite (Preferred)
  - Tables: `runs`, `jobs`, `enriched`, `scores` with `run_timestamp_utc` linkage
  - Deterministic job IDs (e.g., hash of `source|url`); avoid autoincrement reliance
  - Idempotent `init_schema()` with versioned migrations via `meta(schema_version)`
  - Compact JSON for config snapshots and components
- JSON Store (Alternative)
  - Files per run (`*.jsonl` + `summary.json`) under run-keyed paths; index for discovery
  - Same retention rules and timestamp reuse

## Retention Policy
- Config keys: `retention.enabled`, `retention.days`, `retention.keep_latest_n_runs`
- Rules: Delete runs older than `days`; keep latest N; apply both deterministically; always protect current run; ascending purge order


## Cross-Links
- Phase 3A: [docs/phase3A_enrichment_scoring.md](phase3A_enrichment_scoring.md)
- Overview: [README.md](../README.md)
- Config: [config/README.md](../config/README.md)
