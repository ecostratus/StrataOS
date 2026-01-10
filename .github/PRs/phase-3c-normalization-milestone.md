# Phase 3C: Data Normalization Milestone

## Summary
Consolidates the data normalization boundary and introduces shared helpers to ensure clean, deterministic inputs across the pipeline. Refactors enrichment functions to normalize configuration lists at boundaries (module load and function entry), removes ad-hoc inline normalization, and enforces deterministic sorting of outputs—preserving behavior while improving type-safety and clarity.

## Technical Changes
- Shared utilities: Introduced a normalization module:
  - [automation/common/normalization.py](automation/common/normalization.py)
  - Helpers: `normalize_terms(items)`, `ensure_int(val, default)`, `ensure_float(val, default)`, `ensure_str(val, default="")`
- Filters & Sources: Refactored to consume shared helpers for consistent input handling and type-safety.
  - [automation/job-discovery/scripts/filters.py](automation/job-discovery/scripts/filters.py)
  - [automation/job-discovery/scripts/sources.py](automation/job-discovery/scripts/sources.py)
- Enrichment Pipeline: Normalization applied at function boundaries; removed inline `.lower()`/`.strip()` loops and enforced deterministic ordering.
  - [automation/enrichment/scripts/enrichment.py](automation/enrichment/scripts/enrichment.py)
  - Key functions reviewed: `normalize_title`, `infer_seniority`, `detect_stack`, `detect_role_tags`, `is_remote_friendly`, `extract_features`

## Testing
- Added focused tests for normalization determinism and enrichment boundary behavior:
  - [tests/common/test_normalization_terms.py](tests/common/test_normalization_terms.py)
  - [tests/enrichment/test_enrichment_normalization.py](tests/enrichment/test_enrichment_normalization.py)
- Validates:
  - Edge-case handling (mixed case, punctuation, whitespace, None inputs)
  - Deterministic, repeatable outputs across runs
  - Preservation of existing enrichment semantics with normalized inputs

## Phase 3C Checklist & Test Matrix
- [x] Shared normalization helpers implemented in a centralized module
- [x] Filters and sources refactored to use shared helpers
- [x] Enrichment functions normalized at boundaries (module + function entry)
- [x] Removed ad-hoc inline normalization within loops
- [x] Deterministic ordering enforced in enrichment outputs
- [x] Added unit tests for normalization and enrichment behavior
- [x] Verified repeat-run determinism with normalized inputs
- [x] Maintained backward compatibility and existing CLI flags

### Test Matrix (high-level)
- Input Types
  - [x] Lists with mixed case and whitespace
  - [x] Optional/None inputs for term lists
- Transformation Logic
  - [x] String normalization (trim, case-fold) via shared helpers
  - [x] Deterministic sorting of outputs
- Enrichment
  - [x] Seniority inference with sanitized patterns
  - [x] Stack and role tag detection with normalized config lists
  - [x] Remote-friendly flags processed through normalized aliases

## Scope
This PR is the Phase 3C normalization milestone. It centralizes normalization, refactors enrichment boundaries, and adds validation tests without changing orchestrator flags or external behavior.

## Note for Future Scope
Extended normalization for additional sources, new enrichment transforms, and expanding configuration surfaces are out of scope for this PR and will follow in a subsequent change set.
