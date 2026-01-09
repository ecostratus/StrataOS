# Changelog

All notable changes to this project will be documented in this file.

This project follows Semantic Versioning.

## [Unreleased]

### Added
- Job discovery orchestrator: `automation/job-discovery/scripts/job_discovery_v1.py` that loads config, applies filters, and exports matched jobs to CSV.
- VS Code task "Run job discovery v1" in `.vscode/tasks.json`.

### Planned
- Bump to `v0.1.1` after adding more tests and features.

## [v0.1.0] - 2026-01-08

"Stable dev environment baseline"

### Added
- Local `.venv` tasks to install dev requirements and run tests.
- `pytest.ini` for test discovery (`*_tests.py`) and short tracebacks.
- README snippet showing how to reuse the shared pytest problem matcher.

### Fixed
- `normalize_terms()` in `automation/job-discovery/scripts/filters.py` to skip `None`/empty values.

[Unreleased]: https://github.com/ecostratus/personal-operating-system-60d/compare/v0.1.0...HEAD
[v0.1.0]: https://github.com/ecostratus/personal-operating-system-60d/releases/tag/v0.1.0
