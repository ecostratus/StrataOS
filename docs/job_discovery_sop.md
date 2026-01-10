# Job Discovery SOP

This SOP covers environment setup, endpoint configuration, running discovery, logs, metrics, summary artifacts, failure modes, and adding new sources.

## Environment Setup
- Create a virtual environment and install test dependencies.
- Configure `config/env.sample.json` and optionally a `.env` for overrides.
- Ensure `SYSTEM_OUTPUT_DIRECTORY` exists or pass `--out-dir`.

## Configure Real Endpoints
- LinkedIn: `LINKEDIN_API_URL`, `LINKEDIN_API_TOKEN` (or `LINKEDIN_API_KEY`).
- Indeed: `INDEED_API_URL`, `INDEED_API_TOKEN` (or `INDEED_PUBLISHER_KEY`).
- Rate/retry: `SCRAPER_RPM`, `SCRAPER_TIMEOUT`, `SCRAPER_MAX_RETRIES`, `SCRAPER_BACKOFF_BASE`, `SCRAPER_BACKOFF_MAX`, `SCRAPER_JITTER_MS`.
- Enable with `LINKEDIN_ENABLED` / `INDEED_ENABLED`.

## Run Discovery
- Default run (exports CSV + summary):
  - `python3 automation/job-discovery/scripts/job_discovery_v1.py --out-dir ./output`
- Summary-only mode (no CSV export):
  - `python3 automation/job-discovery/scripts/job_discovery_v1.py --out-dir ./output --summary-only`

## Logging & JSONL
- Structured logs emit JSON lines.
- To write logs to a JSONL file: set `LOG_TO_FILE=true`.
- To suppress stdout logs when JSONL is enabled: set `system.log_suppress_stdout_if_jsonl=true`.
- Logs write to `output/run-<timestamp>.jsonl` when enabled.

## Metrics Glossary
- `jobs_fetched`: number of items retrieved per source.
- `malformed_entries`: entries discarded due to missing/invalid fields.
- `retries_attempted`: total number of retry attempts.
- `rate_limit_sleeps`: total sleep events due to rate limiting.
- `scraper_failures`: number of source-level failures (exceptions).

## Summary Artifacts
- File: `jobs_discovered_<timestamp>.summary.json`.
- Contains enabled sources, counts (`total_discovered`, `filtered_out`, `exported`), and per-source metrics.
- Human-readable preview is printed via the pretty printer.

## Interpreting Logs
- Each log line includes `ts`, `level`, `event`, and fields.
- Errors/warnings appear; with JSONL enabled, logs are in the file.
- Use the JSONL for analysis or ingestion.

## Common Failure Modes
- Misconfigured endpoints (bad URL or token) → zero results; check `scraper_failures`.
- Aggressive filters → high `filtered_out` and low `exported`.
- Network timeouts → increased `retries_attempted`.
- Rate limits → increased `rate_limit_sleeps`.

## Adding New Sources
- Implement fetcher in `automation/job-discovery/scripts/sources.py`.
- Add mapping helper in `automation/job-discovery/scripts/mapping.py`.
- Extend config keys in `config/config_loader.py` and `config/env.sample.json`.
- Instrument with `structured_log` and metrics.
- Write fixtures and tests ensuring mapping and observability.
