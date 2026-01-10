# Phase 3B: Scheduling + Storage

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

## Module Scaffolding Plan
- `automation/scheduling/scheduler.py`
  - `compute_next_run(now_utc, config) -> datetime`
  - `should_run(now_utc, last_run_ts, config) -> bool`
- `automation/storage/sqlite_store.py`
  - `init_schema() -> None`
  - `insert_run(run_summary: dict) -> None`
  - `insert_jobs(run_ts: str, jobs: list[dict]) -> None`
  - `insert_enriched(run_ts: str, enriched: list[dict]) -> None`
  - `insert_scores(run_ts: str, scores: list[dict]) -> None`
  - `prune(config: dict) -> dict`
- `automation/storage/json_store.py`
  - `write_run(run_ts: str, summary: dict) -> str`
  - `write_jsonl(kind: str, run_ts: str, items: list[dict]) -> str`
  - `prune(config: dict) -> dict`
- `automation/job-discovery/scripts/orchestrator_hooks.py`
  - `run_enrichment_pipeline(jobs: list[dict], config: dict, ts: str) -> dict[str, list[dict]]`

## Config Surface Additions
- `scheduling.enabled: bool`
- `scheduling.mode: "interval" | "window"`
- `scheduling.interval_minutes: int`
- `scheduling.window_time: "HH:MM"`
- `storage.backend: "sqlite" | "json"`
- `storage.sqlite_path: "./data/jobs.db"`
- `retention.enabled: bool`
- `retention.days: int`
- `retention.keep_latest_n_runs: int`

## Test Plan
- Unit: scheduler helpers (interval/window), SQLite init idempotency, retention computation ordering
- Integration: freeze UTC time; end-to-end pipeline; single run timestamp reused; retention deletes expected runs
- Determinism: identical inputs → identical outputs; UTC-only calculations

## Acceptance Criteria
- Deterministic scheduling cadence; storage reads/writes validated
- Retention removes expected runs deterministically; current run protected
- Orchestrator defaults unchanged; scheduling/storage strictly opt-in

## Backward-Compatibility Constraints
- `--schedule` opt-in; default OFF
- Discovery CSV format unchanged; enrichment/scoring artifacts only with `--enrich`
- `--summary-only` behavior preserved

## Drift-Prevention Guardrails
- Pure functions for time/retention logic; no hidden state
- UTC-only; no DST/local conversions
- Versioned migrations; idempotent schema initialization
- Deterministic sorts by `run_timestamp_utc` for retention and queries

## Cross-Links
- Phase 3A: [docs/phase3A_enrichment_scoring.md](phase3A_enrichment_scoring.md)
- Overview: [README.md](../README.md)
- Config: [config/README.md](../config/README.md)
