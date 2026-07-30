# Job Search Platform Foundations

This hub establishes the baseline product, architecture, delivery, and governance model for improving StrataOS job discovery into a full search experience.

## Objectives

- Build a flexible search product that supports fast iteration and pivoting.
- Improve quality and coverage of job sources.
- Introduce disciplined planning and risk management.
- Keep delivery lean with clear checkpoints.

## Scope

- UX and search workflow improvements
- Backend query and ranking capabilities
- Data model normalization for filtering and sorting
- Source adapter strategy for public and partner integrations
- Governance, policies, and decision records

## Document Index

- [00-charter.md](00-charter.md)
- [01-delivery-plan.md](01-delivery-plan.md)
- [02-raid-log.md](02-raid-log.md)
- [03-product-design.md](03-product-design.md)
- [04-technical-architecture.md](04-technical-architecture.md)
- [05-governance-operating-model.md](05-governance-operating-model.md)
- [06-development-policies.md](06-development-policies.md)
- [07-source-research-backlog.md](07-source-research-backlog.md)
- [08-idea-backlog.md](08-idea-backlog.md)
- [09-phase1-technical-implementation.md](09-phase1-technical-implementation.md)
- [10-execution-backlog.md](10-execution-backlog.md)
- [11-source-priority-matrix.md](11-source-priority-matrix.md)
- [sources/README.md](sources/README.md)

## Working Cadence

- Weekly planning update: refresh priorities and dependencies.
- Weekly RAID update: add new risks, assumptions, issues, and decisions.
- Bi-weekly architecture review: validate scalability, compliance, and source strategy.
- Monthly pivot check: verify roadmap still aligns with outcomes.

## Definition of Ready for Implementation

A feature is ready to implement when:

- Search behavior is defined in [03-product-design.md](03-product-design.md).
- Data and API impact is documented in [04-technical-architecture.md](04-technical-architecture.md).
- Dependencies, constraints, and owners are captured in [02-raid-log.md](02-raid-log.md).
- Governance and policy checks are satisfied.

## Definition of Done for Each Iteration

- Acceptance criteria met and documented.
- Tests added or updated for critical paths.
- Docs updated in this hub.
- Any decisions recorded in the RAID log.
