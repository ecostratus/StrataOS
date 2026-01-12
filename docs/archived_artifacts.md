# Archived Artifacts

This section preserves superseded documents verbatim to maintain historical accuracy. Each entry includes a header with metadata.

## Progress‑to‑Launch Checklist & Timeline (Phase 3E)
- Original title: Progress‑to‑Launch Checklist & Timeline (Phase 3E)
- Superseded by: Progress‑to‑Launch Checklist & Timeline (Updated, PM-Friendly)
- Date archived: January 11, 2026

### Original Content (verbatim)

#### Progress‑to‑Launch Checklist & Timeline (Phase 3E)

Date: January 10, 2026

## Overview
Phase 3E delivers enrichment transforms, prompt wiring, a minimal deterministic renderer, CLI scripts for outreach/resume, a combined runner, and docs/tasks for discoverability. This document summarizes what’s done, what’s next, and how to run the flows.

## Objectives
- Expand enrichment (seniority, domain tags, stack, skills) with cloud, CI/CD, NoSQL, ML libraries coverage.
- Wire enriched context into outreach and resume prompts with deterministic rendering.
- Provide CLI scripts and a combined runner to generate timestamped outputs.
- Add config toggles and sample env keys for user context paths and output directories.
- Improve discoverability via docs and VS Code tasks.

## Completed
- Enrichment transforms expanded and applied post-dedup/order (toggle-aware).
- Prompt templates updated to consume enriched fields.
- Minimal prompt renderer implemented for `{{var}}` replacement and list joining.
- Outreach and resume CLI scripts render templates and save timestamped outputs.
- Combined runner orchestrates both flows with overrides.
- Config mappings and `env.sample.json` updated for user context and output directories.
- Docs updated; VS Code tasks added for common runs.
- Snapshot tests (base + enriched) added; deterministic outputs verified; full test suite green.
- Behavior-level JSONL logging (logs/events.jsonl) and metrics counters (logs/metrics.json) integrated; combined runner prints per-script timing and a metrics summary.
- Metrics CLI and tasks added (show/reset/open); Makefile utilities for logs-open-events, metrics-summary/reset, clean-cache, next-changelog draft.

## Pending
- Resume tailoring v1 full behavior and variants.
- Interview prep v1; consulting funnel ingestion; weekly review automation.
- Metrics aggregation/dashboarding and broader end-to-end validations.

## Timeline (Target)
- Week of Jan 12–16: Snapshot tests; behavior-level logging; metrics scaffolding.
- Week of Jan 19–23: Resume tailoring v1 behavior; prompt variants; integration validations.
- Week of Jan 26–30: Interview prep v1; consulting funnel ingestion; weekly review automation kickoff.
- Ongoing: Expand enrichment coverage; refine prompts; operational polish.

## How to Run
Use the combined runner to generate both prompts or run each individually.

### Combined runner
```bash
python3 automation/common/run_prompts.py \
  --outreach-context config/user/outreach_context.json \
  --outreach-output-dir out/outreach \
  --resume-context config/user/resume_context.json \
  --resume-output-dir out/resume
```

### Individual scripts
```bash
# Outreach
python3 automation/outreach/scripts/outreach_generator_v1.py \
  --context config/user/outreach_context.json \
  --output-dir out/outreach \
  --prompt prompts/outreach/outreach_prompt_v1.md

# Resume
python3 automation/resume-tailoring/scripts/resume_tailor_v1.py \
  --context config/user/resume_context.json \
  --output-dir out/resume \
  --prompt prompts/resume/resume_tailor_prompt_v1.md
```

### VS Code tasks
Open the tasks in the command palette: `Tasks: Run Task`.

- Prompts: Outreach (venv) / Resume (venv) / Combined (venv)
- Tests: Run All / Snapshot Tests
- Metrics: Show summary / Reset counters / Open JSON
- Logs: Open events (or run `make logs-open-events`)

## Logging & Metrics
- Events log: logs/events.jsonl (one JSON object per event). Open via task "Logs: Open events" or:

```bash
make logs-open-events
```

- Metrics counters: logs/metrics.json. View or reset via tasks or CLI:

```bash
./.venv/bin/python automation/common/metrics_cli.py --summary
./.venv/bin/python automation/common/metrics_cli.py --reset
```

## Key Artifacts & Quick Links
- Combined runner: [automation/common/run_prompts.py](../automation/common/run_prompts.py)
- Prompt renderer: [automation/common/prompt_renderer.py](../automation/common/prompt_renderer.py)
- Enrichment transforms: [automation/job-discovery/scripts/enrichment_transforms.py](../automation/job-discovery/scripts/enrichment_transforms.py)
- Outreach script: [automation/outreach/scripts/outreach_generator_v1.py](../automation/outreach/scripts/outreach_generator_v1.py)
- Resume script: [automation/resume-tailoring/scripts/resume_tailor_v1.py](../automation/resume-tailoring/scripts/resume_tailor_v1.py)
- Outreach prompt: [prompts/outreach/outreach_prompt_v1.md](../prompts/outreach/outreach_prompt_v1.md)
- Resume prompt: [prompts/resume/resume_tailor_prompt_v1.md](../prompts/resume/resume_tailor_prompt_v1.md)
- VS Code tasks: [.vscode/tasks.json](../.vscode/tasks.json)
- Sample env config: [config/env.sample.json](../config/env.sample.json)
- Logging utility: [automation/common/logging.py](../automation/common/logging.py)
- Metrics module: [automation/common/metrics.py](../automation/common/metrics.py)
- Metrics CLI: [automation/common/metrics_cli.py](../automation/common/metrics_cli.py)
- Makefile utilities: [Makefile](../Makefile)

## Environment Notes
- Enrichment import path issues in direct Python REPL can occur when running outside the package layout; scripts use dynamic, file-based import fallbacks.
- Local pytest may require environment setup; CI should validate tests when dependencies are present.

## Release Context
- Phase 3E finalized in v0.3.5: deterministic renderer, enrichment wiring, CLI/runner, snapshot tests, and telemetry. See [releases/v0.3.5-Phase3E-CLI-PromptRendering.md](releases/v0.3.5-Phase3E-CLI-PromptRendering.md) for details and the Verification Checklist.

---

## Phase 3D → Phase 3E Release Plan
- Original title: Phase 3D → Phase 3E Release Plan
- Superseded by: Progress‑to‑Launch Checklist & Timeline (Updated, PM-Friendly)
- Date archived: January 11, 2026

### Original Content (verbatim)

#### Phase 3D → Phase 3E Release Plan

## Phase 3D Completion Criteria
- Lever, Greenhouse, Ashby, Indeed adapters implemented (opt-in by config)
- Optional adapters scaffolded (JobSpy, ZipRecruiter, Google Jobs, Glassdoor, Craigslist, GoRemote)
- Multi-source ingestion deterministic (canonical `job_id`, sorted, de-duplicated)
- Transform expansion complete; normalization boundaries upheld
- Config surfaces stable; structured logging consistent across sources
- v0.3.x release series complete

## Phase 3E Goals
- Outreach generation v1
- Resume tailoring v1
- Interview prep prompt engine
- Cross-behavior enrichment reuse
- Behavior-level metrics
- Behavior-level structured logging
- v0.4.0 release milestone

## Phase 3E Entry Conditions

---

## Phase 3A: Enrichment + Scoring — Archived Sections
- Original document name: docs/phase3A_enrichment_scoring.md (Archived Sections)
- Context: Phase 3A reference
- Superseded by: Phase 3C normalization boundary
- Date archived: January 11, 2026

### Original Content (verbatim)

#### Module Scaffolding Plan (no code changes yet)
- Files to add (in a future implementation step):
  - `automation/enrichment/scripts/enrichment.py`
    - `extract_features(job: Dict[str, str], config) -> Dict[str, Any]`
    - `normalize_title(title: str) -> str` (e.g., collapse whitespace, lowercasing)
    - `infer_seniority(title: str) -> str` (e.g., Junior/Mid/Senior)
    - `detect_stack(title: str, description?: str, config_keywords) -> List[str]`
  - `automation/enrichment/scripts/scoring.py`
    - `score_job(enriched: Dict[str, Any], weights: Dict[str, float], thresholds: Dict[str, float]) -> float`
    - `bucket_score(score: float, thresholds) -> str` (Exceptional/Strong/etc.)
  - `tests/phase3A_enrichment_tests.py`
    - Unit tests: feature extraction and normalization
    - Scoring tests: weight application, bucket thresholds
    - Integration tests: discovery → enrichment → scoring determinism
- Config Extensions (future):
  - `enrichment.keywords.role` (e.g., ["engineer", "developer"]) 
  - `enrichment.keywords.stack` (e.g., ["python", "javascript", "aws"]) 
  - `enrichment.remote_aliases` (e.g., ["remote", "hybrid"]) 
  - `enrichment.seniority_patterns` (map of regex → level)

#### Test Plan
- Unit tests:
  - Title normalization (whitespace collapsing, case normalization).
  - Seniority inference with patterns.
  - Stack detection via config keywords.
- Scoring tests:
  - Deterministic score for known enriched inputs.
  - Threshold bucketing (Exceptional/Strong/Moderate/Weak).
- Integration tests:
  - A small pipeline from canonical jobs to enriched+scored outputs; verify deterministic artifacts and UTC timestamps.
- Negative tests:
  - Missing fields: transforms should default safely.
  - Empty keywords: scoring still computes with defaults.

#### Acceptance Criteria
- Enrichment produces deterministic outputs for fixed inputs.
- Scoring returns a stable numeric score and a bucket label.
- Artifacts include enriched JSON (optional) and scored CSV, with deterministic filenames.
- CLI and existing orchestrator remain backward-compatible; enrichment pipeline is opt-in.
- Full test coverage with unit + integration tests; no breaking changes to existing CSV format.

#### Copilot-Ready Implementation Prompt
Use this prompt in VS Code Copilot Chat to implement Phase 3A:

BEGIN PROMPT
You are implementing Phase 3A (Enrichment + Scoring) for the job discovery subsystem. Constraints:
- Keep orchestrators thin; scrapers safe; config-driven behavior.
- Preserve deterministic outputs and UTC-safe timestamps; do not break CSV format.
- All new code must include unit and integration tests.

Tasks:
1. Create `automation/enrichment/scripts/enrichment.py`:
   - Implement `extract_features(job, config)` to derive: normalized title, inferred seniority, stack tags, remote friendliness.
   - Implement helpers: `normalize_title`, `infer_seniority`, `detect_stack`. Keep pure and deterministic.
   - Read `enrichment.*` keys from config if present; default safely when absent.
2. Create `automation/enrichment/scripts/scoring.py`:
   - Implement `score_job(enriched, weights, thresholds)` using existing `scoring.weights.*` and `scoring.thresholds.*` from config.
   - Implement `bucket_score(score, thresholds)` to return a label.
3. Add tests `tests/phase3A_enrichment_tests.py`:
   - Unit tests for normalization, seniority inference, and stack detection.
   - Scoring tests for weight application and bucketing.
   - Integration test that takes a small canonical job list → enriched → scored; asserts deterministic outputs and UTC-safe timestamps.
4. Optional: Add an `--enrich` flag to orchestrator to run enrichment + scoring before export; default OFF to preserve backward compatibility.
5. Verify full test suite passes via venv:
   - `${PWD}/.venv/bin/python -m pytest -q --tb=short`
END PROMPT

Notes:
- Do not modify code until you run the implementation prompt intentionally.
- Keep behavior opt-in; default pipeline must remain unchanged.

#### Config Examples
Add Phase 3A scoring configuration in [config/env.sample.json](../config/env.sample.json):

```json
{
  "scoring": {
    "comment": "Phase 3A enrichment+scoring uses normalized [0,1] scores and thresholds.",
    "weights": {
      "role_fit": 0.5,
      "stack": 0.3,
      "remote": 0.2,
      "comment": "Keys used in Phase 3A: role_fit, stack, remote."
    },
    "thresholds": {
      "exceptional": 0.85,
      "strong": 0.7,
      "moderate": 0.5,
      "weak": 0.0
    }
  },
  "enrichment": {
    "keywords": {
      "role": ["engineer", "developer"],
      "stack": ["python", "javascript", "aws"]
    },
    "remote_aliases": ["remote", "hybrid"],
    "seniority_patterns": {"\\b(sr|senior)\\b": "Senior", "\\b(jr|junior)\\b": "Junior"}
  }
}
```

Notes:
- Weights are proportions; sum can be 1.0 but does not need to be.
- Thresholds and scores operate in [0,1]. Buckets evaluate in order: Exceptional → Strong → Moderate → Weak.
- `enrichment.*` keys are optional; transforms default safely when absent.

#### CLI Usage
Enable enrichment + scoring exports with the orchestrator flag:

```bash
${PWD}/.venv/bin/python automation/job-discovery/scripts/job_discovery_v1.py --out-dir output --enrich
```

Artifacts (deterministic filenames using the run timestamp):
- Matched CSV: `jobs_discovered_{YYYYMMDD_HHMMSS}.csv`
- Enriched JSON: `jobs_enriched_{YYYYMMDD_HHMMSS}.json`
- Scored CSV: `jobs_scored_{YYYYMMDD_HHMMSS}.csv`

---

## Phase 3B: Scheduling + Storage — Archived Sections
- Original document name: docs/phase3B_scheduling_storage.md (Archived Sections)
- Context: Phase 3B reference
- Superseded by: Phase 3C normalization boundary
- Date archived: January 11, 2026

### Original Content (verbatim)

#### Module Scaffolding Plan
- `automation/scheduling/scheduler.py`
  - `compute_next_run(now_utc, config) -> datetime`
  - `should_run(now_utc, last_run_ts, config) -> bool`
- `automation/storage/sqlite_store.py`
  - `init_schema() -> None`
  - `insert_run(run_summary: dict) -> None`
  - `insert_jobs(run_ts: str, jobs: list[dict]) -> None`
  - `insert_enriched(run_ts: str, enriched: list[dict]) -> None`
  - `insert_scores(run_ts: str, scores: list[dict]) -> None`
  - `prune(config: dict) -> dict`
- `automation/storage/json_store.py`
  - `write_run(run_ts: str, summary: dict) -> str`
  - `write_jsonl(kind: str, run_ts: str, items: list[dict]) -> str`
  - `prune(config: dict) -> dict`
- `automation/job-discovery/scripts/orchestrator_hooks.py`
  - `run_enrichment_pipeline(jobs: list[dict], config: dict, ts: str) -> dict[str, list[dict]]`

#### Config Surface Additions
- `scheduling.enabled: bool`
- `scheduling.mode: "interval" | "window"`
- `scheduling.interval_minutes: int`
- `scheduling.window_time: "HH:MM"`
- `storage.backend: "sqlite" | "json"`
- `storage.sqlite_path: "./data/jobs.db"`
- `retention.enabled: bool`
- `retention.days: int`
- `retention.keep_latest_n_runs: int`

#### Test Plan
- Unit: scheduler helpers (interval/window), SQLite init idempotency, retention computation ordering
- Integration: freeze UTC time; end-to-end pipeline; single run timestamp reused; retention deletes expected runs
- Determinism: identical inputs → identical outputs; UTC-only calculations

#### Acceptance Criteria
- Deterministic scheduling cadence; storage reads/writes validated
- Retention removes expected runs deterministically; current run protected
- Orchestrator defaults unchanged; scheduling/storage strictly opt-in

#### Backward-Compatibility Constraints
- `--schedule` opt-in; default OFF
- Discovery CSV format unchanged; enrichment/scoring artifacts only with `--enrich`
- `--summary-only` behavior preserved

#### Drift-Prevention Guardrails
- Pure functions for time/retention logic; no hidden state
- UTC-only; no DST/local conversions
- Versioned migrations; idempotent schema initialization
- Deterministic sorts by `run_timestamp_utc` for retention and queries

---

## Phase 3D: Extended Sources & Enrichment Transforms — Archived Sections
- Original document name: docs/phase3D_extended_sources_transforms.md (Archived Sections)
- Context: Phase 3D reference
- Superseded by: Phase 3C normalization boundary
- Date archived: January 11, 2026

### Original Content (verbatim)

#### Phase 3D: Extended Sources & Enrichment Transforms

Note: Downstream phases (3D/3E) are FUTURE-only (post-Phase 3C). See the canonical checklist for the current state: [progress_to_launch_checklist_timeline.md](progress_to_launch_checklist_timeline.md).

## Quick Links
- [Combined Runner README](../automation/common/README.md)
- [Combined Runner Script](../automation/common/run_prompts.py)
- [Outreach Prompt](../prompts/outreach/outreach_prompt_v1.md)
- [Resume Prompt](../prompts/resume/resume_tailor_prompt_v1.md)
- [Outreach Script](../automation/outreach/scripts/outreach_generator_v1.py)
- [Resume Script](../automation/resume-tailoring/scripts/resume_tailor_v1.py)

## Goals
- Add new job sources and expand enrichment transforms while reusing the stable normalization boundary from Phase 3C.
- Maintain deterministic behavior, pure functions, and backward compatibility.

## Scope
- In-scope: new sources, additional transforms, expanded config surfaces (opt-in), and tests.
- Out-of-scope: orchestrator flag changes, storage schema changes, and breaking config changes.

## Normalization Boundary Reuse
- Continue normalizing config lists at load-time with defensive normalization at function entry.
- Use shared helpers from `automation/common/normalization.py` (`normalize_terms`, `ensure_int`, `ensure_float`, `ensure_str`).

## Candidate Sources
- LinkedIn API (rate-limited)
- Indeed/Greenhouse/Lever (JSON feeds)
- Company RSS/job boards

### Lever Adapter Details
- Mapping: `title` (Lever `text`/`title`), `company`, `location` (from `categories.location`), `url` (Lever `hostedUrl`), `source="lever"`.
- Determinism: `job_id` = SHA-256 of `title|company|url` (lower+trim) truncated to 16 hex chars; outputs sorted and de-duplicated by `job_id`.
- Config: `LEVER_ENABLED` (bool, default false), `LEVER_API_URL` (string).
- Normalization: Use `ensure_str` for all fields; apply `strip().lower()` only in `job_id` canonicalization.
- Tests: Unit tests validate mapping, normalization, dedup, gating; integration tests validate multi-source ingestion determinism.

### Source Integration Guidelines
- Deterministic `job_id` generation (hash of canonical fields)
- Retry/backoff with bounded jitter; structured logging
- Type-safe mappings with validation; discard malformed entries deterministically

## Orchestrator Contract (Phase 3D)
- Function: `fetch_all_sources(cfg)` in `automation/job-discovery/scripts/sources.py`.
- Behavior:
  - Config‑gated activation per source (e.g., `LEVER_ENABLED`, `GREENHOUSE_ENABLED`, etc.).
  - Cross‑source de‑duplication by canonical `job_id`.
  - Deterministic ordering by `job_id`.
  - Returns a single canonical list with fields: `job_id`, `title`, `company`, `location`, `url`, `source`, `posted_at`.

  ### Enrichment Contract (Phase 3E)
  - Enrichment is applied post-dedup and ordering via pure transforms in [automation/job-discovery/scripts/enrichment_transforms.py](../automation/job-discovery/scripts/enrichment_transforms.py).
  - Added fields (deterministic, stable):
    - `seniority`: one of `intern`, `junior`, `mid`, `senior`, `staff`, `principal`, `lead`, `manager`.
    - `domain_tags`: array of tags inferred from role (e.g., `backend`, `frontend`, `mobile`, `data`, `devops`, `security`).
    - `stack`: array of technologies/frameworks/cloud providers inferred from role text.
    - `skills`: array inclusive of `stack` plus soft skills like `Leadership`, `Agile` when present.
  - Inputs used: `title` and optional `description` when available; transforms are resilient to missing fields.
  - Determinism: same inputs → same enriched outputs; ordering within arrays is stable and sorted.

## Phase 3E: Enrichment → Prompt Rendering Contract

Phase 3E introduces a contract between the enrichment layer and the prompt rendering layer.

### Enriched job fields

Each job object passed into outreach and resume behaviors may include:

- `seniority`: inferred string (e.g., "junior", "mid", "senior", "lead")
- `domain_tags`: list of domain tags (e.g., ["cloud", "ml", "data-platform"]) 
- `stack`: list of inferred technologies (e.g., ["AWS", "Kubernetes", "Terraform"]) 
- `skills`: list of extracted skills, including CI/CD, data, ML, and frameworks

These fields are:

- added deterministically by `enrich_job(job)`
- derived from normalized title + description + metadata
- stable for a given input job

### Prompt rendering integration

- `outreach_generator_v1.py` and `resume_tailor_v1.py` build a context dict from enriched job fields.
- Prompts (`prompts/outreach/outreach_prompt_v1.md`, `prompts/resume/resume_tailor_prompt_v1.md`) are rendered via a minimal renderer.
- Templates treat enriched context as optional: when fields are missing, prompts still render cleanly.

### Config toggle

- Enrichment is controlled by `ENRICHMENT_ENABLED` (default: true).
- When disabled, jobs flow through without enrichment, and prompts receive only basic fields (title, company, location).

### End-to-end assertions

End-to-end tests assert that:

- domain tags such as `cloud` and `ml` appear for matching roles
- enriched fields are present in the rendered prompts when enabled
- behavior remains deterministic across runs for the same input

### CLI usage (Phase 3E)

Outreach prompt:

```
python3 automation/outreach/scripts/outreach_generator_v1.py \
  --context ./config/outreach_context.sample.json \
  --output-dir ./output/outreach
```

Resume tailoring prompt:

```
python3 automation/resume-tailoring/scripts/resume_tailor_v1.py \
  --context ./config/resume_context.sample.json \
  --output-dir ./output/resume
```

Flags:
- `--context`: path to user context JSON (optional)
- `--output-dir`: directory to save rendered prompt (optional)
- `--prompt`: override template path (optional)
- `--no-sources`: skip job discovery (optional; uses sample job)

Quick note: For a one-command workflow that runs both outreach and resume prompt generation, see the combined runner README at [automation/common/README.md](../automation/common/README.md).

### Adapter Registry
Orchestrator maintains a stable registry mapping enable keys to adapter fetch functions. New adapters can be added without changing orchestrator semantics if they follow the canonical mapping and opt‑in gating.

## Enrichment Transform Expansions
- Role taxonomy expansion: synonyms and seniority refinements
- Stack detection: language/framework/cloud providers; aliases normalized
- Remote/Hybrid inference: normalized alias lists
- Company signals (size, funding, industry) via optional lookups (pure cacheable transforms)

## Configuration Surfaces (Opt-in)
- `enrichment.keywords.role` / `stack` additions
- `enrichment.remote_aliases` extended
- `enrichment.seniority_patterns` refinements
- Optional `enrichment.company_signals` lookup toggles (off by default)

### Lever Config Keys
- `LEVER_ENABLED`: Set to true to enable Lever adapter.
- `LEVER_API_URL`: URL for Lever postings feed (e.g., `https://api.lever.co/postings/<company>`).

## Determinism & Testing
- Unit tests for each new source mapping and transform boundary
- Repeat-run determinism tests; sorted outputs where applicable
- Property-based tests for normalization edge cases

## Acceptance Criteria
- New sources produce consistent schema aligned to existing pipeline
- Enrichment outputs unchanged for existing inputs when new features disabled
- All tests pass; zero Pylance warnings for added modules

### Lever Acceptance
- Adapter returns deterministic, de-duplicated outputs with required fields when enabled.
- Disabled state returns empty list.

## Rollout Plan
- Feature-gate new sources and transforms via config (disabled by default)
- Document usage in `config/README.md` with minimal examples
- Prepare PR: “Phase 3D: Extended Sources & Transforms”
- Canonical job objects stable
- Deterministic tags (stack, domain, seniority)
- Multi-source ingestion validated
- No normalization drift
- No orchestrator drift
