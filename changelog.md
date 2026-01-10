# Changelog

All notable changes to this project will be documented in this file.

This project follows Semantic Versioning.

## [Unreleased]

### Added
- Job discovery orchestrator: `automation/job-discovery/scripts/job_discovery_v1.py` that loads config, applies filters, and exports matched jobs to CSV.
- VS Code task "Run job discovery v1" in `.vscode/tasks.json`.

### PR Summary: Phase 3A Enrichment + Scoring (scaffold)
- Introduced enrichment transforms and scoring module:
	- `automation/enrichment/scripts/enrichment.py`
	- `automation/enrichment/scripts/scoring.py`
- Added `--enrich` flag to `automation/job-discovery/scripts/job_discovery_v1.py` to export:
	- Enriched JSON: `jobs_enriched_{YYYYMMDD_HHMMSS}.json`
	- Scored CSV: `jobs_scored_{YYYYMMDD_HHMMSS}.csv`
- Documented scoring/enrichment config examples in `config/env.sample.json` and usage in `docs/phase3A_enrichment_scoring.md`.
- Improved discoverability:
	- Top-level README highlights `--enrich` and artifacts
	- Added `automation/job-discovery/scripts/README.md` with quick usage
- Tests: Full suite passing (137 tests).

### Planned
- Bump to `v0.1.1` after adding more tests and features.

## [v0.3.0-Phase3C-Normalization] - 2026-01-10

"Phase 3C: Data Normalization Milestone"

### Added
- Shared normalization helpers in `automation/common/normalization.py`: `normalize_terms`, `ensure_str`, `ensure_int`, `ensure_float`.
- Deterministic ordering guarantees across enrichment outputs.
- Focused tests for normalization edge cases and deterministic enrichment behavior.

### Changed
- Consolidated normalization boundary: enrichment config lists (seniority patterns, stack patterns, keyword lists, role‑fit heuristics) are normalized once at load time, with defensive normalization at function entry.
- Removed ad‑hoc inline normalization and enforced type‑safe, pure functions at boundaries.

### Fixed
- Eliminated Pylance warnings by using typed helpers for all normalization boundaries.

## [v0.1.0] - 2026-01-08

"Stable dev environment baseline"

### Added
- Local `.venv` tasks to install dev requirements and run tests.
- `pytest.ini` for test discovery (`*_tests.py`) and short tracebacks.
- README snippet showing how to reuse the shared pytest problem matcher.

### Fixed
- `normalize_terms()` in `automation/job-discovery/scripts/filters.py` to skip `None`/empty values.

[Unreleased]: https://github.com/ecostratus/personal-operating-system-60d/compare/v0.3.2-Phase3D-Lever...HEAD
[v0.3.0-Phase3C-Normalization]: https://github.com/ecostratus/personal-operating-system-60d/releases/tag/v0.3.0-Phase3C-Normalization
[v0.3.2-Phase3D-Lever]: https://github.com/ecostratus/personal-operating-system-60d/releases/tag/v0.3.2-Phase3D-Lever
[v0.1.0]: https://github.com/ecostratus/personal-operating-system-60d/releases/tag/v0.1.0

## [v0.3.2-Phase3D-Lever] - 2026-01-10

"Phase 3D: Lever Adapter"

### Added
- Lever source adapter in `automation/job-discovery/scripts/source_lever_adapter.py` with deterministic mapping, canonical `job_id`, UTC `posted_at`, sorted outputs, and de-duplication.
- Unit and integration tests covering adapter mapping, gating, and cross-source determinism.
- Documentation updates in `docs/phase3D_extended_sources_transforms.md` describing config, mapping, and acceptance criteria.

### Configuration
- New opt-in keys in `config/env.sample.json`: `LEVER_ENABLED` (default `false`), `LEVER_API_URL` (string).

### Compatibility
- Adapter is disabled by default; existing flows and outputs remain unchanged unless explicitly enabled.
