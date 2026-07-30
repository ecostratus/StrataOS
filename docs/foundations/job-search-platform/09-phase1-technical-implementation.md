# Phase 1 Technical Implementation Pack

This document turns architecture intent into executable engineering scope for search-first capabilities.

## Phase 1 Objective

Deliver interactive search capabilities for the existing webapp with minimal disruption to current run and prompt flows.

## In-Scope

- New search API endpoint with structured filtering.
- Jobs schema extension for core searchable fields.
- Query builder with safe SQL construction.
- Sorting and pagination.
- Frontend search panel integration.

## Out-of-Scope

- Automated application submission.
- Partner-only source integrations requiring external contracts.
- Advanced machine-learned ranking.

## API Contract (Proposed)

Endpoint:

- POST /api/jobs/search

Request body:

- query: string
- keywords_exclude: list[string]
- companies_include: list[string]
- companies_exclude: list[string]
- location: { country, state_region, city }
- salary: { min, max, currency }
- job_type: list[string]
- work_type: list[string]
- posted_within_days: integer
- sort: relevance | posted_date | salary_desc | salary_asc | company_asc
- page: integer
- page_size: integer

Response body:

- items: list[job]
- page: integer
- page_size: integer
- total: integer
- applied_filters: object
- diagnostics: { query_ms, sort_mode }

## Schema Additions (jobs table)

- country_code TEXT
- state_region TEXT
- city TEXT
- salary_min REAL
- salary_max REAL
- salary_currency TEXT
- job_type TEXT
- work_type TEXT
- company_normalized TEXT
- title_normalized TEXT
- posted_at_utc TEXT
- search_document TEXT

## Index Plan

- idx_jobs_posted_at_utc on posted_at_utc
- idx_jobs_location on country_code, state_region, city
- idx_jobs_job_type_work_type on job_type, work_type
- idx_jobs_company_normalized on company_normalized
- idx_jobs_title_normalized on title_normalized
- FTS virtual table for title, company, search_document (or LIKE fallback if FTS unavailable)

## Backend Changes by File

- webapp/backend/app.py
  - Add search request model and route handler.
  - Add query compiler for filters.
  - Add pagination and diagnostics payload.

- webapp/backend/schemas.py
  - Add SearchRequest and SearchResponse models.

- webapp/backend/database.py (new optional module)
  - Add migration helpers and index creation utilities.

## Frontend Changes by File

- webapp/frontend/src/App.jsx
  - Add search state model.
  - Add filter panel UI controls.
  - Replace direct list call with search call.
  - Add sort and pagination controls.

## Data Backfill Strategy

- Backfill normalized fields from existing raw_json and fallback columns.
- Set unknown values to null and keep records queryable.
- Run backfill idempotently on startup migration path.

## Rollout Strategy

1. Deploy backend schema and API behind feature flag.
2. Enable frontend controls for internal testing.
3. Validate query performance and result quality.
4. Enable by default after test pass.

## Test Plan

- Unit tests
  - Query parser and filter compiler.
  - Sorting and pagination behavior.

- Integration tests
  - Endpoint with mixed filters.
  - Empty-result and edge-case handling.

- Regression tests
  - Existing job discovery, resume, and outreach endpoints unaffected.
