# Discovery-First Job Ingestion Architecture

## Why this direction

StrataOS should abstract job source discovery and execution behavior, not only ATS families.
ATS is an important classifier output, but it is not the root abstraction.

This architecture shifts ingestion from source toggles to a staged, evidence-driven pipeline that can handle ATS, direct APIs, GraphQL backends, and HTML fallback paths consistently.

## Pipeline stages

1. Discovery
- Input: company domain or known career URL.
- Output: candidate career URLs and crawl hints.

2. Classification
- Input: discovered URL and fetched evidence.
- Output: provider class, confidence, and the exact detection signals used.

3. Resolution
- Input: classification result and source metadata.
- Output: executable endpoint strategy (not just one URL).

4. Extraction
- Input: execution strategy.
- Output: raw provider payloads plus extraction telemetry.

5. Normalization
- Input: raw payloads.
- Output: versioned canonical schema records.

6. Enrichment
- Input: canonical records.
- Output: derived metadata (skills, level, remote type, etc.).

7. Scoring
- Input: enriched records.
- Output: ranked jobs and confidence diagnostics.

## Evidence-based classification contract

Classification should store explicit signals so failures are diagnosable and heuristics can be tuned.

Example shape:

- provider: greenhouse
- confidence: 0.98
- signals:
  - boards.greenhouse.io
  - __GREENHOUSE_JOB_BOARD__
  - /v1/boards/
  - greenhouse.css

## Resolver output must be an execution plan

Resolver output is a strategy object that schedulers can execute without provider-specific branching.

Example fields:
- strategy: rest
- steps:
  - method
  - url
  - query params
  - pagination mode
  - rate limit policy
  - retry policy

## Capability negotiation

Do not hardcode feature flags per provider in downstream stages.
Use capability negotiation between:
- what a source can provide
- what enrichment and scoring require

Core capability set (initial):
- supports_salary
- supports_pagination
- supports_departments
- supports_remote
- supports_benefits
- supports_compensation_bands

## Provider lifecycle and health

Every provider should maintain operational state:
- healthy
- degraded
- deprecated
- broken
- blocked

Track at minimum:
- last_success_at
- last_failure_at
- rolling_success_rate
- average_latency_ms
- schema_drift_count

## Versioned canonical schemas

Add explicit schema versions now to prevent painful migrations later.
Initial contracts:
- CanonicalJobV1
- CanonicalJobV2
- CanonicalCompanyV1
- CanonicalEndpointV1

## Plugin contracts

Move from adapter-specific orchestration branches to plugin interfaces:
- DiscoveryPlugin
- ClassifierPlugin
- ResolverPlugin
- ExtractorPlugin
- NormalizerPlugin

This enables adding a new provider by registration, not by editing the orchestrator.

## Near-term implementation priorities

1. Career URL discovery with deterministic tests.
2. Evidence-based classifier with confidence and signal traces.
3. Resolver execution plans with pagination and rate-limit policies.
4. Schema drift detection and provider health scoring.
5. Incremental synchronization and dedupe hardening.
6. Provider fixtures and contract tests per pipeline stage.

## De-prioritized (intentional)

Company competitor/relationship graph is valuable, but should follow ingestion maturity.
Core investment first belongs in discovery, extraction reliability, and schema stability.
