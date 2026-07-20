# StrataOS Knowledge Hub

This is the central index for operational outputs, findings, dashboards, and weekly execution.

## Where Results Are Stored

### Runtime Outputs
- `output/`:
  - `jobs_discovered_*.csv`
  - `jobs_enriched_*.json`
  - `jobs_scored_*.csv`
  - `jobs_discovered_*.summary.json`
  - `outreach/outreach_prompt_*.txt`
  - `resume/resume_prompt_*.txt`

### Logs and Metrics
- `logs/events.jsonl`: structured event log for runs.
- `logs/metrics.json`: counters and summary metrics.
- CLI: `./.venv/bin/python automation/common/metrics_cli.py --summary`

### Strategy and Findings Documents
- `docs/weekly-cadence.md`: weekly operating rhythm.
- `docs/monday-friday-strataos-playbook.md`: 20-30 minute daily execution playbook.
- `docs/risk-map.md`: risk tracking and mitigations.
- `docs/governance-model.md`: decision and governance framework.
- `docs/progress_to_launch_checklist_timeline.md`: active program status and timeline.

## Dashboard Status

There is a dashboard specification and folder, plus a placeholder workbook reference:
- `excel-templates/dashboards/dashboard-spec.md`
- `excel-templates/dashboards/60d_operating_dashboard.xlsx`

Current state:
- The dashboard spec is defined.
- The workbook path currently contains placeholder instructions rather than a finalized live dashboard workbook.

## How To Start Weekly Strategy

Primary entrypoint:
- `docs/monday-friday-strataos-playbook.md`

Fast start commands:

```bash
# 1) Monday pipeline run (discovery + enrich + score)
./.venv/bin/python automation/job-discovery/scripts/job_discovery_v1.py --out-dir ./output --enrich

# 2) Tuesday prompt generation (deterministic fallback)
./.venv/bin/python automation/common/run_prompts.py \
  --outreach-context config/outreach_context.sample.json \
  --outreach-output-dir output/outreach \
  --resume-context config/resume_context.sample.json \
  --resume-output-dir output/resume \
  --no-sources

# 3) Wednesday validation gate
./.venv/bin/python -m pytest -q --tb=short

# 4) Thursday/Friday review
./.venv/bin/python automation/common/metrics_cli.py --summary
python3 scripts/ci/check_docs.py
```

## Recommended Weekly Knowledge Routine

1. Run Monday and Tuesday workflows and verify artifacts in `output/`.
2. Log execution evidence through `logs/events.jsonl` and `logs/metrics.json`.
3. Run Wednesday tests before operational changes.
4. On Friday, review metrics and capture strategy updates in docs.
5. Use `prompts/review/weekly_review_prompt_v1.md` to run a structured weekly review.
