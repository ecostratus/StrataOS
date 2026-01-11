# Phase 3D: Extended Sources & Enrichment Transforms

## Quick Links
- [Combined Runner README](automation/common/README.md)
- [Combined Runner Script](automation/common/run_prompts.py)
- [Outreach Prompt](prompts/outreach/outreach_prompt_v1.md)
- [Resume Prompt](prompts/resume/resume_tailor_prompt_v1.md)
- [Outreach Script](automation/outreach/scripts/outreach_generator_v1.py)
- [Resume Script](automation/resume-tailoring/scripts/resume_tailor_v1.py)

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
	- Enrichment is applied post-dedup and ordering via pure transforms in [automation/job-discovery/scripts/enrichment_transforms.py](automation/job-discovery/scripts/enrichment_transforms.py).
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

Quick note: For a one-command workflow that runs both outreach and resume prompt generation, see the combined runner README at [automation/common/README.md](automation/common/README.md).

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