## Phase 3D: Multi‑Source Orchestrator + Integration Tests

### Summary
Implements the multi‑source ingestion orchestrator and integration tests to lock the Phase 3D contract before enrichment expansion. Produces a single canonical job list with deterministic ordering and cross‑source de‑duplication.

### Technical Changes
- Added `fetch_all_sources(cfg)` in `automation/job-discovery/scripts/sources.py`:
  - Stable adapter registry (Lever, Greenhouse, Ashby, Indeed, ZipRecruiter, Google Jobs, Glassdoor, Craigslist, GoRemote)
  - Config‑gated activation per source
  - Cross‑source de‑duplication by `job_id`
  - Deterministic ordering by `job_id`
- Integration tests:
  - `tests/integration/test_multi_source_orchestrator.py` injects identical canonical jobs across Lever and Greenhouse to verify de‑duplication and determinism
- Documentation:
  - Added Orchestrator Contract to `docs/phase3D_extended_sources_transforms.md`

### Contract
- Canonical fields: `job_id`, `title`, `company`, `location`, `url`, `source`, `posted_at`
- `job_id` = SHA‑256 of lower‑trimmed `title|company|url`, truncated to 16 hex
- Sorted output and de‑duplication by `job_id`
- Functions are pure; adapters disabled by default via config

### Backward Compatibility
- No orchestrator changes to existing flows outside of the new function
- Adapters remain opt‑in; disabled by default to prevent drift

### Testing
- Deterministic repeat runs validated
- Cross‑source `job_id` compatibility validated (Lever ↔ Greenhouse)
- Full suite passing

### Checklist
- [x] Implement orchestrator
- [x] Add integration tests
- [x] Update docs
- [x] Run test suite
- [ ] Open PR
- [ ] Merge once green

### Next Steps (Phase 3D → 3E)
- Expand enrichment transforms (skills, domain tags, seniority heuristics, stack inference)
- Wire enriched fields into outreach and resume tailoring once transforms are stable
