# Execution Backlog

This backlog maps Phase 1 and source-research foundations into execution-ready tasks.

## Estimation Scale

- XS: <= 0.5 day
- S: 1 day
- M: 2-3 days
- L: 4-5 days
- XL: > 5 days

## Epic A: Search API and Data Layer

| Task ID | Task | Owner | Estimate | Depends On | Deliverable |
| --- | --- | --- | --- | --- | --- |
| A-01 | Define SearchRequest and SearchResponse models | Backend Eng | S | None | Request and response schema in backend |
| A-02 | Add jobs schema migration for normalized fields | Backend Eng | M | A-01 | Migration path and startup migration checks |
| A-03 | Add index creation and validation | Backend Eng | S | A-02 | Query performance baseline indexes |
| A-04 | Implement /api/jobs/search endpoint | Backend Eng | M | A-01, A-02 | Functional search API with diagnostics |
| A-05 | Add query compiler and input guards | Backend Eng | M | A-04 | Safe, deterministic SQL query generation |
| A-06 | Add backend tests for search endpoint | QA + Backend Eng | M | A-04, A-05 | Passing unit and integration tests |

## Epic B: Search-first Frontend

| Task ID | Task | Owner | Estimate | Depends On | Deliverable |
| --- | --- | --- | --- | --- | --- |
| B-01 | Design filter panel interaction model | Product + Frontend Eng | S | A-01 | UI state schema and interaction spec |
| B-02 | Implement search form controls | Frontend Eng | M | B-01 | Title, company, location, salary, type controls |
| B-03 | Implement sort and pagination controls | Frontend Eng | S | A-04 | User-controlled result ordering and paging |
| B-04 | Add result chips and applied filter summary | Frontend Eng | S | B-02 | Transparent filter state UX |
| B-05 | Add frontend tests for search interactions | QA + Frontend Eng | M | B-02, B-03 | Regression-safe UI behavior |

## Epic C: Source Research and Governance

| Task ID | Task | Owner | Estimate | Depends On | Deliverable |
| --- | --- | --- | --- | --- | --- |
| C-01 | Complete top-10 source profile validation | Product + Eng | L | None | Updated profile docs with verified terms notes |
| C-02 | Build source scorecard summary table | Product Ops | M | C-01 | Ranked source priority matrix |
| C-03 | Perform terms and compliance review for P1 sources | Reviewer | M | C-01 | Approved or conditioned source decisions |
| C-04 | Define source onboarding checklist in PR template | Eng Lead | S | C-03 | Repeatable governance control |

## Epic D: Release and Hardening

| Task ID | Task | Owner | Estimate | Depends On | Deliverable |
| --- | --- | --- | --- | --- | --- |
| D-01 | Add feature flag and rollout plan | Backend Eng | S | A-04 | Controlled enablement path |
| D-02 | Run performance test for search endpoint | QA + Backend Eng | M | A-06 | Baseline latency and throughput report |
| D-03 | Validate no regressions in prompt generation workflows | QA | S | B-03 | Regression evidence |
| D-04 | Update RAID and release notes | Product + Eng | S | D-01, D-02, D-03 | Governance-complete rollout package |

## Dependency Highlights

- Frontend integration depends on stable search request contract.
- Performance testing should run after index creation.
- P1 source enablement is gated by compliance review.

## Suggested Sprint Allocation

- Sprint 1: A-01 to A-03, B-01, C-01 kickoff
- Sprint 2: A-04 to A-06, B-02 to B-03
- Sprint 3: B-04 to B-05, C-02 to C-04, D-01
- Sprint 4: D-02 to D-04 and hardening
