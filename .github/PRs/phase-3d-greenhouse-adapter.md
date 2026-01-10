# Phase 3D: Greenhouse Adapter

## Summary
Implements the Greenhouse source adapter with deterministic ingestion, canonical `job_id`, UTC `posted_at`, sorted outputs, and de-duplication. Defaults are opt-in and disabled to preserve existing behavior.

## Technical Changes
- Added `automation/job-discovery/scripts/source_greenhouse_adapter.py`:
  - `fetch_greenhouse_jobs(config)` with config gating (`GREENHOUSE_ENABLED`) and `GREENHOUSE_API_URL` placeholder.
  - Canonical field mapping: `title`, `company`, `location`, `url`, `source="greenhouse"`, `posted_at` (UTC fallback).
  - Deterministic `job_id`: SHA-256 of `title|company|url` (lower+trim), truncated to 16 hex.
  - Deterministic ordering and de-duplication by `job_id`.
  - Structured logging events: `pipeline.ingest.greenhouse.*`.
- Tests in `tests/sources/test_greenhouse_adapter.py`:
  - Mapping correctness, normalization, deterministic ID, config gating, malformed handling, deterministic ordering.
  - Cross-source compatibility: identical `job_id` for matching `title|company|url` across Greenhouse and Lever.
- Config placeholders in `config/env.sample.json`:
  - `GREENHOUSE_ENABLED` (default `false`), `GREENHOUSE_API_URL`, `GREENHOUSE_API_KEY`.
- Documentation:
  - Short README section "Enable Lever (Optional)" clarifying activation, determinism, and example usage (for parity and discoverability).

## Normalization Boundary
- Use shared helpers from `automation/common/normalization.py` (`ensure_str`, `normalize_terms`).
- Normalize only at boundaries; preserve pure functions and deterministic behavior.

## Backward Compatibility
- Adapter is opt-in (`GREENHOUSE_ENABLED=false` by default).
- No orchestrator or behavior drift when disabled; existing flows remain unchanged.

## Testing
- Unit tests validate mapping/dedup/determinism and malformed handling.
- Integration-style check ensures cross-source `job_id` compatibility.
- Full test suite remains green.

## Checklist
- [x] Config placeholders added (disabled by default)
- [x] Deterministic `job_id` and ordering
- [x] De-duplication by `job_id`
- [x] Unit tests for adapter
- [x] Docs updated for enablement and determinism
- [x] No orchestrator drift
- [x] Full suite passing

## Future Scope
- Implement actual Greenhouse fetch using `GREENHOUSE_API_URL` and `GREENHOUSE_API_KEY` with rate limits.
- Add field mapping reference updates and source-specific transforms if needed.
- Extend multi-source reconciliation and reporting artifacts.
