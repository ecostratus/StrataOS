# Monday-Friday StrataOS Playbook (20-30 Minutes/Day)

This playbook is a lightweight operating loop for consistent weekly execution.

## Automation Option

You can run the same loop through a single wrapper script:

```bash
scripts/run_monday_friday_playbook.sh auto
```

Explicit day selection:

```bash
scripts/run_monday_friday_playbook.sh monday
scripts/run_monday_friday_playbook.sh tuesday
scripts/run_monday_friday_playbook.sh week
```

Environment flags:
- `STRATAOS_NO_SOURCES=true` for deterministic Tuesday prompt generation.
- `STRATAOS_RESET_METRICS=true` to reset metrics during Friday run.

## Prerequisites (one-time)
- Python environment exists at `.venv`
- Base config loaded from `config/env.sample.json`
- Context files available:
  - `config/outreach_context.sample.json`
  - `config/resume_context.sample.json`

If needed, initialize quickly:
```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -U pip -r dev-requirements.txt
```

## Monday (25-30 min): Build Opportunity Queue
Goal: Discover, enrich, score, and export this week's opportunity list.

Run:
```bash
./.venv/bin/python automation/job-discovery/scripts/job_discovery_v1.py --out-dir ./output --enrich
```

Review outputs:
- `output/jobs_discovered_*.csv`
- `output/jobs_enriched_*.json`
- `output/jobs_scored_*.csv`
- `output/jobs_discovered_*.summary.json`

Daily decision:
- Select top 3-5 roles from scored output for resume/outreach work.

## Tuesday (20-25 min): Generate Outreach + Resume Prompts
Goal: Generate actionable prompt artifacts for selected roles.

Run (normal mode):
```bash
./.venv/bin/python automation/common/run_prompts.py \
  --outreach-context config/outreach_context.sample.json \
  --outreach-output-dir output/outreach \
  --resume-context config/resume_context.sample.json \
  --resume-output-dir output/resume
```

If live sources are unstable, run deterministic fallback:
```bash
./.venv/bin/python automation/common/run_prompts.py \
  --outreach-context config/outreach_context.sample.json \
  --outreach-output-dir output/outreach \
  --resume-context config/resume_context.sample.json \
  --resume-output-dir output/resume \
  --no-sources
```

Review outputs:
- `output/outreach/outreach_prompt_*.txt`
- `output/resume/resume_prompt_*.txt`

## Wednesday (20-25 min): Validate Stability Before Execution
Goal: Catch regressions before scaling outreach/application activity.

Run:
```bash
./.venv/bin/python -m pytest -q --tb=short
```

Optional focused checks:
```bash
./.venv/bin/python -m pytest tests/job_discovery_import_tests.py -q --tb=short
./.venv/bin/python -m pytest tests/cli/test_orchestrator_cli.py -q --tb=short
```

## Thursday (20-25 min): Execute and Track
Goal: Send refined outreach and submit targeted applications.

Use Tuesday outputs to execute outreach and applications.

Quick health check:
```bash
./.venv/bin/python automation/common/metrics_cli.py --summary
```

Files to update manually for tracking/governance:
- `logs/events.jsonl`
- `logs/metrics.json`
- system-of-record conventions in `excel-templates/system-of-record-schema.md`

## Friday (25-30 min): Weekly Governance + Reset
Goal: Review results, document learnings, and prepare next week.

Run quality/documentation checks:
```bash
python3 scripts/ci/check_docs.py
./.venv/bin/python automation/common/metrics_cli.py --summary
```

Optional reset for a clean next week baseline:
```bash
./.venv/bin/python automation/common/metrics_cli.py --reset
```

Review docs:
- `docs/governance-model.md`
- `docs/progress_to_launch_checklist_timeline.md`
- `docs/weekly-cadence.md`

## Success Criteria (weekly)
- New qualified roles discovered and scored each Monday
- Fresh outreach/resume prompts generated each Tuesday
- Test suite remains green on Wednesday
- Outreach/application actions executed on Thursday
- Governance + metrics reviewed on Friday

## 5-Minute Fallback Plan (busy day)
If time-constrained, run this minimum command:
```bash
./.venv/bin/python automation/common/run_prompts.py --no-sources
```
Then execute one outreach action and one application action from latest artifacts.
