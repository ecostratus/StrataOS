## Summary
This PR advances Phase3D by adding deterministic, configgated adapters for multiple job sources, expanding documentation, and aligning field mappings. All adapters follow the same canonical mapping and normalization boundary with zero orchestrator drift.

## Technical Changes
- Added adapters: Lever, Greenhouse, Ashby, Indeed, ZipRecruiter, Google Jobs, Glassdoor, Craigslist, GoRemote
- All adapters: pure functions, deterministic `job_id`, sorted output, crossrun repeatability
- Config placeholders added (all disabled by default) in `config/env.sample.json`
- Unit tests for Lever/Greenhouse/Ashby/Indeed; scaffolds untouched for orchestrator until `fetch_all_sources` exists
- Updated documentation: README enablement notes; expanded Field Mapping Reference to include all sources
- Structured logging events per adapter (e.g., `pipeline.ingest.<source>.*`)

## Normalization Boundary
- Inbound fields normalized once per adapter using shared helpers (`ensure_str`) and consistent patterns
- Canonical mapping enforced: `title`, `company`, `location`, `url`, `source`, `posted_at (YYYYMMDD)`
- Deterministic `job_id` = SHA256 of `title|company|url` (lowertrim), truncated to 16 hex
- No orchestrator changes or side effects; functions remain pure

## Backward Compatibility
- No orchestrator changes; multisource orchestrator test remains skipbased until introduced
- Config surfaces are optin and disabled by default (`*_ENABLED=false`)
- No behavioral drift across existing modules
- Full test suite remains green

## Testing
- Unit tests for Lever/Greenhouse/Ashby/Indeed: mapping, gating, determinism, malformed handling
- Crosssource `job_id` compatibility validated between Lever and Greenhouse
- Full suite passes; repeat runs produce identical outputs

## Checklist
- [x] Branch created
- [x] Config placeholders added
- [x] Adapters implemented/scaffolded
- [x] Unit tests added (where applicable)
- [x] Documentation updated (README, Field Mapping Reference)
- [ ] PR opened
- [ ] Merge once green

## Future Scope (Phase3D)
- Implement real HTTP fetches for all adapters (respecting rate limits and retries)
- Add multisource orchestrator and integration tests once `fetch_all_sources` exists
- Extend enrichment transforms (skills, domain tags, seniority heuristics)
- Prepare Phase3E integrations across outreach, resume tailoring, and interview prep
