# StrataOS Vision (v1)

StrataOS v1 is a single-user decision engine for evaluating career opportunities.

It is not an ATS keyword matcher. It is an evidence-based reasoning system that produces explainable recommendations.

## What StrataOS Is

- A deterministic decision engine for opportunity prioritization.
- A capability and problem-archetype reasoning system.
- A policy-driven evaluator that can optimize for different objectives.
- A platform designed with an extensible core and focused implementation.

## What StrataOS Is Not (v1)

- A multi-user platform.
- A generic decision platform for all domains.
- An opaque machine-learning ranker.
- A replacement for human judgment.

## v1 Product Scope

- Persona scope: one `Person` (James Naphen).
- Opportunity scope: `FTE` and `CONTRACT` opportunities.
- Decision actions: `APPLY_IMMEDIATELY`, `HIGH_PRIORITY_REVIEW`, `NETWORK_FIRST`, `MONITOR`, `IGNORE`, `RESEARCH_COMPANY`.

## Non-Negotiable Rule

Every recommendation must be reproducible.

Given the same:

- Person
- Opportunity
- Policy
- Observations
- Evidence

the engine must produce the same:

- Claims
- Decision
- Recommendation
