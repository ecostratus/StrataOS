# How-To Instructions

## Run Job Discovery
1. Ensure the virtual environment exists:
   - `.venv/bin/python -V`
2. Run discovery with enrichment and scoring:
   - `.venv/bin/python automation/job-discovery/scripts/job_discovery_v1.py --out-dir output --enrich`
3. Review artifacts in `output/`:
   - `jobs_discovered_*.csv`
   - `jobs_enriched_*.json`
   - `jobs_scored_*.csv`
   - `jobs_discovered_*.summary.json`

## Use the Control Center UI
1. Start backend API (project-specific command).
2. Open the web frontend.
3. Click **Find Jobs**.
4. Use **Show low relevance jobs** toggle:
   - Off (default): hides jobs with empty role tags and weak relevance.
   - On: shows all jobs.

## Trigger Discovery via API
- Endpoint: `POST /api/runs/job-discovery`
- Result includes `run_id`, `status`, and `mirrored_jobs`.

## Search Jobs via API
- Endpoint: `POST /api/jobs/search`
- Default relevance filters are applied unless overridden.
- Useful override fields:
  - `include_low_relevance: true`
  - `require_role_tags: false`
  - `min_bucket: "Weak" | "Moderate" | "Strong" | "Exceptional"`
