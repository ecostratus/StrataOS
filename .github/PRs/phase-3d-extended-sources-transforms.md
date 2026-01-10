## Summary
This PR introduces the foundational scaffolding for Phase 3D, enabling the system to expand into multiple new data sources and enrichment transforms. It establishes the adapter pattern, config surfaces, and test harness that all future sources will follow.

## Technical Changes
- Added new source adapter skeleton (`new_source_adapter.py`)
- Added unit tests for mapping, normalization, determinism, and config gating
- Added opt‑in config placeholders (`NEW_SOURCE_ENABLED`, `NEW_SOURCE_API_URL`, `NEW_SOURCE_API_KEY`)
- Ensured all new code uses shared normalization helpers (`ensure_str`, `normalize_terms`)
- Added Phase 3D documentation scaffold outlining goals, scope, and acceptance criteria

## Normalization Boundary
- All inbound fields normalized once at adapter entry
- Canonical mapping enforced (`title`, `company`, `location`, `url`, `source`)
- Deterministic `job_id` generation using SHA‑256 truncated hash
- No inline `.lower()` / `.strip()` logic
- Pure, deterministic functions with no side effects

## Backward Compatibility
- No orchestrator changes
- No config surface changes beyond opt‑in placeholders
- No behavioral drift
- All existing tests remain green

## Testing
- Added unit tests for the new adapter
- Verified deterministic outputs across repeated runs
- Confirmed config-driven enable/disable behavior
- Full suite passes

## Checklist
- [x] Branch created
- [x] Config placeholders added
- [x] Adapter skeleton created
- [x] Unit tests added
- [x] Documentation scaffold added
- [ ] PR opened
- [ ] Merge once green

## Future Scope (Phase 3D)
- Implement real source adapters
- Expand enrichment transforms (skills, domain tags, seniority heuristics)
- Add integration tests for multi-source ingestion
- Prepare for Phase 3E (Outreach + Resume + Prep behaviors)
