# Source Profile: Greenhouse-hosted Boards

## Metadata

- Source name: Greenhouse
- Category: ATS-hosted careers
- Priority: P1
- Profile owner: Engineering
- Last reviewed: 2026-07-29
- Status: Existing

## Access and Integration

- Access model: Public JSON-style listings on many boards
- Authentication: Often none for listing feeds
- Rate limits: Moderate and site dependent
- Pagination model: Varies, often list endpoints
- Change frequency: Medium
- Webhook or push support: Not typical for external ingestion

## Terms and Compliance

- Terms URL: site and provider terms
- Data use constraints: review required
- Automation constraints: moderate
- Resume upload or apply automation constraints: restricted scope
- Attribution requirements: possible
- Regional compliance notes: standard privacy obligations

## Data Contract

- Core fields available: title, location, url, updated time
- Missing fields: salary frequently absent
- Field quality notes: relatively consistent for core fields
- Example payload shape: JSON list with role fields
- Known schema variability: medium

## Reliability

- Uptime expectations: good
- Common error classes: endpoint path changes, field renames
- Retry and backoff strategy: standard exponential
- Circuit-breaker recommendation: yes

## Product Fit

- Best use case: direct ATS jobs with clear application links
- Role and industry coverage: broad
- Geo coverage: broad
- Freshness quality: high

## Integration Recommendation

- Recommendation: Integrate
- Rationale: strong fit and existing adapter foundation
- Next step: strengthen normalization and metadata extraction

## Initial Scorecard

- Relevance quality: 4
- Data freshness: 4
- Data completeness: 3
- Parse stability: 4
- Integration complexity (5 easiest): 4
- Compliance confidence: 3
- Operational reliability: 4
- Weighted score: 3.85
