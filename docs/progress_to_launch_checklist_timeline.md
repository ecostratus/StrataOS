# Progress‑to‑Launch Checklist & Timeline (Updated, PM-Friendly)

Date: January 11, 2026

## Overview
This is the single source of truth for status, phase boundaries, artifacts, and run steps. It reflects canonical normalization boundaries and current version tags.

Canonical source: Progress‑to‑Launch Checklist & Timeline (Updated, PM‑Friendly)

## Phase Status & Versions
- Phase 1 — Foundations: Done — v0.1.0
- Phase 2A — Early Pipeline: Done — v0.1.1
- Phase 2C — Discovery/Filters: Done — v0.2.0
- Phase 3 — Active: Current = Phase 3C (Normalization) — v0.3.0-Phase3C-Normalization
- Phase 4 — Future: Not Started

## Phase Boundaries (Canonical)
- Phase 3C (Normalization) defines stable boundaries and defensive normalization for config and inputs. All downstream features must respect these boundaries.
- Phase 3A (Enrichment + Scoring) and Phase 3B (Scheduling + Storage) remain in-scope for Phase 3, aligned to the 3C normalization contract.
- Phase 3D/3E features are FUTURE-only (post-Phase 3C); see Archived Artifacts for superseded narratives and plans.

## Current Artifacts (Phase 3C)
- Normalization helpers: [automation/common/normalization.py](../automation/common/normalization.py)
- Config loader and samples: [config/config_loader.py](../config/config_loader.py), [config/env.sample.json](../config/env.sample.json)
- Field mapping reference: [docs/field_mapping_reference.md](field_mapping_reference.md)
- Job discovery orchestrator: [automation/job-discovery/scripts/job_discovery_v1.py](../automation/job-discovery/scripts/job_discovery_v1.py)

## Run Steps (Stable)
Use the job discovery script with deterministic outputs:

```bash
python3 automation/job-discovery/scripts/job_discovery_v1.py --out-dir ./output
```

Optional flags:
- `--summary-only`: export only the run summary
- `--enrich`: opt-in enrichment/scoring when available under Phase 3A

## Timeline (Target)
- Week of Jan 12–16: Validation of normalization boundaries across modules; summary-only flows.
- Week of Jan 19–23: Phase 3A scaffolding alignment to normalization; initial tests.
- Week of Jan 26–30: Phase 3B scheduling/storage helpers; retention policy drafts.
- Ongoing: Preserve determinism; expand coverage under normalization; operational polish.

## Version & Tags
- v0.1.0 (Phase 1)
- v0.1.1 (Phase 2A)
- v0.2.0 (Phase 2C)
- v0.3.0-Phase3C-Normalization (current)

## Recent Completions
- v0.3.6: Import Hardening (sources.py, dynamic adapters) — Combined runner and job-discovery now work without PYTHONPATH.

## Notes
- All features must uphold Phase 3C normalization boundaries.
- Superseded Phase 3D/3E narratives are preserved under [Archived Artifacts](archived_artifacts.md) (Archived).
