# Phase 3D: Extended Sources & Enrichment Transforms

## Goals
- Add new job sources and expand enrichment transforms while reusing the stable normalization boundary from Phase 3C.
- Maintain deterministic behavior, pure functions, and backward compatibility.

## Scope
- In-scope: new sources, additional transforms, expanded config surfaces (opt-in), and tests.
- Out-of-scope: orchestrator flag changes, storage schema changes, and breaking config changes.

## Normalization Boundary Reuse
- Continue normalizing config lists at load-time with defensive normalization at function entry.
- Use shared helpers from `automation/common/normalization.py` (`normalize_terms`, `ensure_int`, `ensure_float`, `ensure_str`).

## Candidate Sources
- LinkedIn API (rate-limited)
- Indeed/Greenhouse/Lever (JSON feeds)
- Company RSS/job boards

### Source Integration Guidelines
- Deterministic `job_id` generation (hash of canonical fields)
- Retry/backoff with bounded jitter; structured logging
- Type-safe mappings with validation; discard malformed entries deterministically

## Enrichment Transform Expansions
- Role taxonomy expansion: synonyms and seniority refinements
- Stack detection: language/framework/cloud providers; aliases normalized
- Remote/Hybrid inference: normalized alias lists
- Company signals (size, funding, industry) via optional lookups (pure cacheable transforms)

## Configuration Surfaces (Opt-in)
- `enrichment.keywords.role` / `stack` additions
- `enrichment.remote_aliases` extended
- `enrichment.seniority_patterns` refinements
- Optional `enrichment.company_signals` lookup toggles (off by default)

## Determinism & Testing
- Unit tests for each new source mapping and transform boundary
- Repeat-run determinism tests; sorted outputs where applicable
- Property-based tests for normalization edge cases

## Acceptance Criteria
- New sources produce consistent schema aligned to existing pipeline
- Enrichment outputs unchanged for existing inputs when new features disabled
- All tests pass; zero Pylance warnings for added modules

## Rollout Plan
- Feature-gate new sources and transforms via config (disabled by default)
- Document usage in `config/README.md` with minimal examples
- Prepare PR: “Phase 3D: Extended Sources & Transforms”