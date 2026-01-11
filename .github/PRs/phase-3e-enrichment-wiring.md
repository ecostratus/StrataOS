## Phase 3E: Enrichment Transforms + Orchestrator Integration + Outreach/Resume Wiring

### Summary
Activates Phase 3E by adding deterministic enrichment transforms and integrating them into the multi-source orchestrator. Wires enriched fields into outreach and resume tailoring scripts to enable downstream personalization and tailoring.

### Technical Changes
- Enrichment transforms in `automation/job-discovery/scripts/enrichment_transforms.py`:
  - `seniority`: inference from role/title (intern/junior/mid/senior/staff/principal/lead/manager)
  - `domain_tags`: inferred areas (backend/frontend/mobile/data/devops/security)
  - `stack`: languages/frameworks/cloud providers (Python, React, AWS, Docker, etc.)
  - `skills`: union of `stack` plus soft skills (Leadership, Agile) when present
  - All transforms are pure and deterministic.
- Orchestrator integration in `automation/job-discovery/scripts/sources.py`:
  - Apply `enrich_job()` after cross-source de-duplication and deterministic ordering by `job_id`.
  - Safe import via `importlib.util` to support hyphenated package paths.
- Outreach wiring in `automation/outreach/scripts/outreach_generator_v1.py`:
  - Demonstrates consuming enriched fields for prompt context.
- Resume wiring in `automation/resume-tailoring/scripts/resume_tailor_v1.py`:
  - Demonstrates using enriched fields to guide tailoring focus.

### Contract Updates (Phase 3E)
- Enrichment is applied post-dedup/order; the canonical job schema is extended with:
  - `seniority`, `domain_tags[]`, `stack[]`, `skills[]`
- Determinism: identical inputs yield identical enriched outputs; arrays sorted for stability.
- Adapters remain pure and config-gated; enrichment does not change adapter outputs pre-enrichment.

### Testing
- Unit tests added in `tests/enrichment/test_enrichment_transforms.py` covering seniority, tags, stack, skills, and `enrich_job` determinism.
- Full test suite passes locally.

### Backward Compatibility
- Enrichment is additive; base canonical fields unchanged.
- Orchestrator behavior (gating, dedup, order) remains identical pre-enrichment.

### Docs
- Enrichment contract documented in `docs/phase3D_extended_sources_transforms.md` under “Enrichment Contract (Phase 3E)”.

### Checklist
- [x] Add transforms module
- [x] Unit tests for transforms
- [x] Integrate transforms into orchestrator
- [x] Wire enriched fields into outreach/resume scripts
- [x] Update docs
- [x] Run full test suite
- [ ] Merge once CI is green
- [ ] Tag `v0.3.4-Phase3E-Enrichment` and publish release

### Next Steps
- Expand keyword aliases and domain coverage based on real data.
- Incorporate optional `description` field from adapters to improve inference.