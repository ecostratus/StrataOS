# Technical Architecture: Job Search Platform

## Architecture Goals

- Support rich filtering and relevance ranking.
- Keep source adapters modular and replaceable.
- Preserve backward compatibility with existing workflows.
- Enable safe pivoting as source constraints evolve.

## Proposed Layers

1. Source Ingestion Layer
- Existing and new adapters for APIs or controlled scraping.
- Normalization contracts for canonical job fields.
- Per-source health and schema validation.

2. Normalization and Enrichment Layer
- Canonicalize company, title, location, compensation.
- Derive searchable fields and quality signals.

3. Search and Ranking Layer
- Query parser and filter compiler.
- Full-text search on title, company, and description.
- Scoring model: text relevance + freshness + fit score.

4. API Layer
- Dedicated search endpoint with structured payload.
- Filter metadata endpoint for UI facets.
- Saved search endpoints.

5. UI Layer
- Search-first experience with faceted filtering.
- Result explanation and action panel.

## Data Model Extensions

Candidate fields to add to jobs storage:

- country_code
- state_region
- city
- salary_min
- salary_max
- salary_currency
- job_type
- work_type
- seniority
- company_normalized
- title_normalized
- posted_at_utc
- search_document

## API Contract Direction

Search request payload should include:

- query: string
- companies_include: list
- companies_exclude: list
- locations: country, state, city
- salary: min, max, currency
- job_type: list
- work_type: list
- posted_within_days
- pagination: limit, offset
- sort: relevance, date, salary

## Observability

- Query latency percentiles
- Source adapter success and failure rates
- Parsing and normalization error counts
- Result quality diagnostics

## Security and Compliance

- Do not store secrets in repo-managed config.
- Respect source terms and robots controls.
- Add explicit policy checks before enabling new source adapters.
