# Delivery Plan

Canonical source: [Progress-to-Launch Checklist & Timeline](../../phases/progress_to_launch_checklist_timeline.md)

## Planning Horizon

- Horizon: 12 weeks
- Delivery style: iterative, milestone-based
- Cadence: weekly planning and review

## Milestones

1. Foundation (Weeks 1-2)
- Finalize product requirements for search criteria.
- Establish query and ranking architecture baseline.
- Create initial source research and prioritization list.

2. Core Search UX + API (Weeks 3-5)
- Add interactive filter model: title, keyword, company, location, work type, job type, salary.
- Add backend search endpoint and query builder.
- Add sorting and pagination.

3. Data Normalization + Ranking (Weeks 6-8)
- Normalize location and compensation fields.
- Add relevance scoring with explainability signals.
- Add index strategy and performance checks.

4. Source Expansion (Weeks 9-10)
- Add prioritized new source adapters with policy review.
- Add connector observability and failure handling.

5. Hardening + Governance (Weeks 11-12)
- Add QA matrix and regression tests for search/filter paths.
- Validate policy controls and decision records.
- Finalize release checklist and rollout notes.

## Workstreams

- Product and UX
- API and data
- Source integrations
- Reliability and observability
- Governance and compliance

## Entry and Exit Criteria

Entry:
- Requirements updated in product design doc.
- Any dependency captured in RAID.

Exit:
- Acceptance criteria met.
- Test evidence attached.
- Docs and decisions updated.

## Pivot Protocol

Pivot can be triggered by:

- Source access constraints
- Compliance constraints
- Material changes in user outcomes
- Technical complexity exceeding budget

When triggered:

1. Log pivot reason in RAID.
2. Update milestones and backlog priorities.
3. Publish scope impact in this plan.
