# Source Profile: Lever-hosted Boards

## Metadata

- Source name: Lever
- Category: ATS-hosted careers
- Priority: P1
- Profile owner: Engineering
- Last reviewed: 2026-07-29
- Status: Existing

## Access and Integration

- Access model: Public listing feeds on many sites
- Authentication: Usually none for listing endpoints
- Rate limits: Moderate and site dependent
- Pagination model: list or page-based depending on endpoint
- Change frequency: Medium
- Webhook or push support: Not typical for this use case

## Terms and Compliance

- Terms URL: provider and employer-specific
- Data use constraints: review required
- Automation constraints: moderate
- Resume upload or apply automation constraints: sensitive
- Attribution requirements: possible
- Regional compliance notes: standard privacy constraints

## Data Contract

- Core fields available: title, location, url, department
- Missing fields: salary often absent
- Field quality notes: good consistency for canonical job fields
- Example payload shape: JSON list with postings
- Known schema variability: medium

## Reliability

- Uptime expectations: good
- Common error classes: schema drift and URL changes
- Retry and backoff strategy: standard exponential
- Circuit-breaker recommendation: yes

## Product Fit

- Best use case: direct employer opportunities
- Role and industry coverage: broad
- Geo coverage: broad
- Freshness quality: high

## Integration Recommendation

- Recommendation: Integrate
- Rationale: strong fit and existing adapter foundation
- Next step: add richer normalization and extraction fields

## Initial Scorecard

- Relevance quality: 4
- Data freshness: 4
- Data completeness: 3
- Parse stability: 4
- Integration complexity (5 easiest): 4
- Compliance confidence: 3
- Operational reliability: 4
- Weighted score: 3.85
