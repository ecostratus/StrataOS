# Job Discovery Standard Operating Procedure (SOP) — v1.0

1. Purpose and Scope
--------------------
This document defines the operational procedure for automated job discovery workflows. It prescribes deterministic steps for configuration, execution, monitoring, and handoff. The SOP applies to automation modules under `automation/job-discovery/` and any adapter that supplies job listings to the platform. All activities shall be auditable and traceable to the SoR and `ChangeLog` as described in `REPO_NORMALIZATION.md`.

2. Definitions and Assumptions
-----------------------------
- "SoR": System of Record defined by `REPO_NORMALIZATION.md` (canonical sheets).
- "Adapter": any component that fetches or maps external job listings into the platform schema.
- "Run": a single execution of the job discovery workflow that produces output artifacts.
- Assumptions: configuration is managed via `config/` and environment variables; secrets are never checked into source control; outputs are written to a versioned `output/` path.

3. Roles and Decision Ownership
-------------------------------
- Platform Owner (PO): is responsible for SOP maintenance, scheduling, and overall acceptance of discovery outputs.
- Workflow Operator (WO): shall execute runs, validate outputs, and publish artifacts to the SoR.
- Adapter Owner (AO): is responsible for adapter correctness, observability, and change approvals for their adapter.
- Security & Compliance Owner (SCO): is responsible for approving credential handling and privacy controls.

4. Discovery Triggers and Entry Criteria
----------------------------------------
Discovery shall start only when all entry criteria are met: (a) configuration validated (`config/` static checks pass), (b) required credentials present in environment variables and approved by SCO, (c) scheduled window or manual trigger by WO, and (d) latest tests for adapters pass in CI. If any entry criteria fail, the run must not start and the WO shall log the failure to `FlowErrors` and create a `ChangeLog` entry if relevant.

5. Execution Steps (Chronological, Deterministic)
------------------------------------------------
1. Validate configuration: run `config_loader` validation; abort on any schema mismatch.
2. Lock run id and create run directory: `output/run-<YYYYMMDDTHHMMSS>-<id>/`.
3. For each enabled adapter (ordered by config):
   a. Verify adapter healthcheck endpoint; fail the adapter and continue to next if healthcheck fails.
   b. Execute fetch; write raw adapter output to `raw/<adapter>.jsonl`.
   c. Run mapping to canonical SoR schema; write `mapped/<adapter>.jsonl`.
   d. Validate mapped records against schema; mark malformed records and increment `malformed_entries` metric.
4. Apply deterministic filtering rules from `config/filters.json`; record `filtered_out` counts.
5. Aggregate per-source metrics and write `jobs_discovered_<timestamp>.summary.json` and `jobs_discovered_<timestamp>.summary.csv` if export enabled.
6. Publish accepted records to SoR or downstream queue; create `ChangeLog` entry for major schema-impacting changes.
7. Emit final structured run log and close the run directory.

6. Risk Classification and Control Mapping
-----------------------------------------
Controls are mapped to risks in `docs/risk-map.md` as follows (control → risk):
- Configuration validation and schema checks → Automation Failure, Quality Degradation
- Environment-only secrets and SCO approval → Privacy Breach, Compliance Violation
- Per-adapter healthchecks and continued-run-on-failure policy → Over-Automation, Time Management
- Rate limiting configuration and shared throttling → API Rate Limiting
- Raw + mapped output retention and backups → Data Loss
- Human review gate for high-impact outputs → Quality Degradation, Wrong Focus

All controls shall be implemented such that evidence is produced (logs, metrics, artifacts) and traceable to the risk category.

7. Exception Handling and Escalation
-----------------------------------
- If an adapter reports authentication failure, AO shall remediate within 4 business hours; WO must escalate to PO and SCO immediately if the adapter supports critical sources.
- For systemic automation failures (>=50% adapters failing or CI regression), PO shall trigger an incident review and rollback to last known-good adapter configuration. This escalation must follow the Risk Response Plan in `docs/risk-map.md`.
- Any suspected data loss or privacy breach must be escalated to SCO within 1 hour and recorded in `FlowErrors` and `ChangeLog`.

8. Evidence, Artifacts, and Auditability
---------------------------------------
Each run shall produce the following artifacts and retain them for the configured retention period:
- `output/run-<id>/raw/<adapter>.jsonl` — raw adapter output
- `output/run-<id>/mapped/<adapter>.jsonl` — mapped records
- `output/run-<id>/jobs_discovered_<timestamp>.summary.json` — per-run summary
- Structured log file `output/run-<id>/run.jsonl` — includes `ts`, `level`, `event`, `run_id`, and metrics
- `FlowErrors` entries for all adapter-level failures and notable exceptions

9. Change Management and Versioning
----------------------------------
- Any change to an adapter or to mapping rules shall be accompanied by: unit tests, CI passing, and an explicit `ChangeLog` entry describing the change, owner, and rollback plan.
- Versioning: adapters and mapping rules shall carry semantic version tags. The SOP file is versioned as `v1.0`; changes to the SOP shall follow repository change management and be recorded in `ChangeLog`.

10. Exit Criteria and Handoff
----------------------------
The run is complete when: (a) all enabled adapters have finished processing (success, partial success, or failed with recorded FlowErrors), (b) summary artifacts are written, and (c) WO has validated and published artifacts to SoR or downstream consumers. Handoff to downstream teams requires publishing the summary and updating the SoR `ChangeLog` with the run id and status.

Appendix: Metrics (deterministic names)
- `jobs_fetched`, `malformed_entries`, `retries_attempted`, `rate_limit_sleeps`, `scraper_failures`, `filtered_out`, `exported`

References: `REPO_NORMALIZATION.md`, `docs/risk-map.md`, `config/`, `automation/job-discovery/`.
