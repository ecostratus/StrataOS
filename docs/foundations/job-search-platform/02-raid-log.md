# RAID Log

Track risks, assumptions, issues, and decisions for the job search platform upgrade.

## Risks

| ID | Date | Risk | Impact | Likelihood | Mitigation | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | 2026-07-29 | Public sources change payloads without notice | High | High | Add schema guards, contract tests, fallback parsers | Eng | Open |
| R-002 | 2026-07-29 | Some sources prohibit scraping or automation | High | Medium | Terms-of-service review before integration | Product + Eng | Open |
| R-003 | 2026-07-29 | Ranking quality may degrade with mixed-source data | Medium | Medium | Weighted scoring with explainability and A/B checks | Eng | Open |

## Assumptions

| ID | Date | Assumption | Validation Method | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| A-001 | 2026-07-29 | Users need multi-field filters (location, salary, type, work mode) | User testing + usage analytics | Product | Open |
| A-002 | 2026-07-29 | Source diversity improves quality of opportunities | Compare relevance across source mixes | Product + Eng | Open |
| A-003 | 2026-07-29 | Search-first UX improves conversion to resume/outreach generation | Funnel metrics before/after redesign | Product | Open |

## Issues

| ID | Date | Issue | Severity | Workaround | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| I-001 | 2026-07-29 | Current UI is run-centric and filter-limited | Medium | Config-based filters in discovery pipeline | Product + Eng | Open |

## Decisions

| ID | Date | Decision | Rationale | Alternatives Considered | Owner |
| --- | --- | --- | --- | --- | --- |
| D-001 | 2026-07-29 | Use a dedicated foundations hub under docs/foundations/job-search-platform | Keeps planning artifacts discoverable and maintainable | Distribute docs across existing folders | Product + Eng |
| D-002 | 2026-07-29 | Prioritize search UX and query API before source expansion | Delivers immediate user value and stronger integration base | Add more sources first | Product + Eng |

## Update Rules

- Update this file at least weekly.
- Add entries instead of rewriting history.
- Link major decisions to implementation PRs when available.
