# Job Discovery Scripts

## Orchestrator
Run the v1 orchestrator to discover, filter, and export jobs:

```bash
python3 automation/job-discovery/scripts/job_discovery_v1.py --out-dir ./output
```

- Summary-only:
```bash
python3 automation/job-discovery/scripts/job_discovery_v1.py --summary-only
```

## Enrichment + Scoring (Phase 3A)
Generate enriched JSON and scored CSV artifacts with deterministic filenames:

```bash
python3 automation/job-discovery/scripts/job_discovery_v1.py --out-dir ./output --enrich
```

Artifacts:
- Matched CSV: `jobs_discovered_{YYYYMMDD_HHMMSS}.csv`
- Enriched JSON: `jobs_enriched_{YYYYMMDD_HHMMSS}.json`
- Scored CSV: `jobs_scored_{YYYYMMDD_HHMMSS}.csv`

Configuration:
- See scoring and enrichment examples in [docs/phase3A_enrichment_scoring.md](../../../docs/phase3A_enrichment_scoring.md)
- Sample config keys in [config/env.sample.json](../../../config/env.sample.json)

Notes:
- Deterministic timestamps are UTC-based and reused across artifacts.
- Enrichment transforms are pure and config-driven; defaults are safe when keys are absent.
