## Phase 3G: Interview Prep Hardening — Import Robustness + Determinism

### Summary
Ensures interview-prep modules run deterministically without requiring PYTHONPATH. Applies two-stage imports (dotted → dynamic fallback), function-scoped loaders, and repo-root-relative dynamic loading. Adds logging/metrics and tests (dynamic import + snapshots).

### Technical Changes (Planned)
- Two-stage imports across interview-prep scripts and shared utilities.
- Deterministic context + template selection.
- Logging + metrics events: start, context_loaded, variant_selected, rendered, saved.
- Snapshot tests for interview prompts.
- Dynamic import tests for interview modules.

### Validation
- Tests: `pytest -q --tb=short` (include snapshot + dynamic import).
- Docs CI: `python3 scripts/ci/check_docs.py`.
- Runner smoke test (interview-prep entry).

### Determinism Guarantees
- Imports resolve without PYTHONPATH.
- Deterministic prompt outputs given same inputs.
- No schema/flag/public API changes.

### Checklist
- [ ] Hardened imports
- [ ] Deterministic behavior ensured
- [ ] Logging + metrics added
- [ ] Tests added and passing
- [ ] Docs updated
- [ ] Release tagged
