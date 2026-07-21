# v0.3.6  Phase 3F: Runner + Sources Import Hardening

Date: January 11, 2026

## Summary
Fullsources mode now runs without requiring PYTHONPATH. All jobdiscovery modules were hardened with a twostage import strategy (dotted import  dynamic fallback) and reporootrelative dynamic loading. Hyphenated directory names (e.g., `job-discovery`) no longer cause import failures under direct script execution.

## Import Hardening (v0.3.6)
- Hardened `sources.py` and local imports (`scrape_utils`, `filters`, `mapping`, `logging_utils`).
- Replaced hyphenated `importlib.import_module("automation.job-discovery...")` calls with `load_module_from_path()` using reporootrelative paths.
- Ensured `fetch_all_sources()` works without PYTHONPATH.
- Preserved public schema, orchestrator flags, and config surfaces.

## Tests & Validation
- Added `tests/job_discovery_import_tests.py` to validate dynamic imports and adapter discovery.
- Verified combined runner endtoend in fullsources mode: both prompts render with no `ModuleNotFoundError` or `SyntaxError`.

## Determinism Guarantees
- Imports resolve deterministically regardless of execution context.
- No reliance on environmentspecific path hacks.
- Dynamic loading uses reporootrelative paths only.

## Next Steps
- Continue operational polish and increase coverage.
- Monitor CI for regressions and expand adapter integrations as needed.

## Status
- PR #13 (Phase 3F: v0.3.6 Import Hardening  sources + dynamic adapters) merged.
- Docs CI passes. Full test suite green post-merge.
