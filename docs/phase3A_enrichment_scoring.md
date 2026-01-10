# Phase 3A: Enrichment + Scoring Pipeline

Quick Links:
- Top-level overview: [README.md](README.md)
- Configuration details: [config/README.md](config/README.md)

## Goals
- Enrich canonical job records with derived features (e.g., normalized role keywords, seniority, tech stack hints, remote friendliness).
- Compute a composite score using configurable weights (role fit, company fit, location, growth, etc.).
- Produce deterministic enriched artifacts (CSV/JSON) and preserve UTC-safe timestamps.
- Keep orchestrators thin and scrapers safe; be fully config-driven.

## Architecture Sketch
- Flow: discovery → canonical jobs → enrichment transforms → scoring → export.
- Modules:
  - `enrichment`: pure transforms that take canonical job dicts and return enriched dicts.
  - `scoring`: compute numeric score from enriched dicts using config weights and thresholds.
  - `export`: reuse existing CSV/summary export; add optional enriched JSON export.
- Config:
  - `scoring.weights.*` and `scoring.thresholds.*` (existing keys); add `enrichment.*` profile keys (e.g., keyword lists, normalization rules).
- Determinism:
  - Pure, side-effect-free transforms; test with fixed inputs; single run timestamp reused across artifacts.

## Module Scaffolding Plan (no code changes yet)
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

## Test Plan
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

## Acceptance Criteria
- Enrichment produces deterministic outputs for fixed inputs.
- Scoring returns a stable numeric score and a bucket label.
- Artifacts include enriched JSON (optional) and scored CSV, with deterministic filenames.
- CLI and existing orchestrator remain backward-compatible; enrichment pipeline is opt-in.
- Full test coverage with unit + integration tests; no breaking changes to existing CSV format.

## Copilot-Ready Implementation Prompt
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

## Config Examples
Add Phase 3A scoring configuration in [config/env.sample.json](config/env.sample.json):

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

## CLI Usage
Enable enrichment + scoring exports with the orchestrator flag:

```bash
${PWD}/.venv/bin/python automation/job-discovery/scripts/job_discovery_v1.py --out-dir output --enrich
```

Artifacts (deterministic filenames using the run timestamp):
- Matched CSV: `jobs_discovered_{YYYYMMDD_HHMMSS}.csv`
- Enriched JSON: `jobs_enriched_{YYYYMMDD_HHMMSS}.json`
- Scored CSV: `jobs_scored_{YYYYMMDD_HHMMSS}.csv`
