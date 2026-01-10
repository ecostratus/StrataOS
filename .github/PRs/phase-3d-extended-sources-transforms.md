# Phase 3D: Extended Sources & Enrichment Transforms

## Summary
Introduce new job sources and expand enrichment transforms while preserving the Phase 3C normalization boundary and deterministic behavior. All additions are opt-in via config, maintaining backward compatibility.

## Technical Changes (Planned)
- New sources (e.g., LinkedIn, Indeed/Greenhouse/Lever, RSS job boards) with type-safe mappings and deterministic `job_id`.
- Enrichment expansions: role taxonomy, stack detection aliases, remote/hybrid inference, optional company signals.
- Reuse shared helpers: `normalize_terms`, `ensure_str`, `ensure_int`, `ensure_float`.

## Normalization Boundary
Config lists normalized at load-time with defensive normalization at function entry; outputs remain deterministically sorted where applicable.

## Backward Compatibility
No orchestrator flag changes; existing behavior unchanged when new features are disabled. Config additions are optional and documented.

## Testing
Unit tests for each new source mapping and transform; determinism tests; property-based tests for normalization edge cases.

## Checklist
- [ ] Implement source adapters (deterministic, typed)
- [ ] Add enrichment expansions (pure, deterministic)
- [ ] Extend config surfaces (opt-in, documented)
- [ ] Add tests (unit + determinism)
- [ ] Update docs (config, usage)

## Scope
In-scope: new sources, transforms, config expansions, tests. Out-of-scope: storage schema changes, breaking flags.
