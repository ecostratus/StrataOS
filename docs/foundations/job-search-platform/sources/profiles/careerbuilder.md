# Source Profile: CareerBuilder

## Metadata

- Source name: CareerBuilder
- Category: Job board
- Priority: P2
- Profile owner: Product + Engineering
- Last reviewed: 2026-07-29
- Status: Planned

## Access and Integration

- Access model: partner channels expected
- Authentication: agreement dependent
- Rate limits: agreement dependent
- Pagination model: standard paging expected
- Change frequency: Medium
- Webhook or push support: unknown

## Terms and Compliance

- Terms URL: https://www.careerbuilder.com
- Data use constraints: requires review of licensing terms
- Automation constraints: likely strict for non-partner scraping
- Resume upload or apply automation constraints: high sensitivity
- Attribution requirements: likely
- Regional compliance notes: standard privacy constraints

## Data Contract

- Core fields available: title, company, location, url
- Missing fields: salary variability
- Field quality notes: broad but uneven relevance by persona
- Example payload shape: API-dependent
- Known schema variability: medium

## Reliability

- Uptime expectations: unknown until validated
- Common error classes: access and schema differences
- Retry and backoff strategy: standard exponential
- Circuit-breaker recommendation: yes

## Product Fit

- Best use case: broad market coverage
- Role and industry coverage: broad
- Geo coverage: broad
- Freshness quality: medium

## Integration Recommendation

- Recommendation: Defer
- Rationale: lower expected fit than P1 sources
- Next step: validate only if coverage gaps remain

## Initial Scorecard

- Relevance quality: 3
- Data freshness: 3
- Data completeness: 3
- Parse stability: 3
- Integration complexity (5 easiest): 2
- Compliance confidence: 3
- Operational reliability: 3
- Weighted score: 2.90
