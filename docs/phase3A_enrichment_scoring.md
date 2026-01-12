# Phase 3A: Enrichment + Scoring Pipeline

Status: COMPLETE

Version: v0.3.0-Phase3C-Normalization

## Phase Boundary
- Completed in support of Phase 3C normalization
- No active work beyond this phase
- Downstream phases are FUTURE and out of scope

Canonical source: [Progress‑to‑Launch Checklist & Timeline](progress_to_launch_checklist_timeline.md)

Quick Links:
- Top-level overview: [docs/README.md](README.md)
- Configuration details: [config/README.md](../config/README.md)

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
