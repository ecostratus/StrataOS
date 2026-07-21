# StrataOS Control Center

Local control center for orchestrating StrataOS automation scripts through a single web UI.

## What it does

- Runs job discovery through the real script at automation/job-discovery/scripts/job_discovery_v1.py.
- Mirrors run results into data/jobs.db and exposes them over REST endpoints.
- Generates resume and outreach prompts for a specific job via --job-json.
- Streams recent activity from logs/events.jsonl.

## Run

From repository root:

./run.sh

For UI hot reload during development:

./run.sh --dev

## API quick checks

- GET /api/health
- POST /api/runs/job-discovery
- GET /api/jobs
- POST /api/prompts/resume
- POST /api/prompts/outreach
- GET /api/activity
