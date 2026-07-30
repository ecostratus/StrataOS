# Source Profile: Monster

## Metadata

- Source name: Monster
- Category: Job board
- Priority: P2
- Profile owner: Product + Engineering
- Last reviewed: 2026-07-29
- Status: Planned

## Access and Integration

- Access model: partner and public pathways
- Authentication: program dependent
- Rate limits: program dependent
- Pagination model: standard paging expected
- Change frequency: Medium
- Webhook or push support: unknown

## Terms and Compliance

- Terms URL: https://www.monster.com
- Data use constraints: verify platform agreements
- Automation constraints: likely restrictive without approved API use
- Resume upload or apply automation constraints: high review required
- Attribution requirements: likely
- Regional compliance notes: standard privacy requirements

## Data Contract

- Core fields available: title, company, location, url, date
- Missing fields: salary often inconsistent
- Field quality notes: broad but variable signal quality
- Example payload shape: API-dependent
- Known schema variability: medium

## Reliability

- Uptime expectations: unknown until validated
- Common error classes: auth and response variance
- Retry and backoff strategy: standard exponential
- Circuit-breaker recommendation: yes

## Product Fit

- Best use case: broader top-of-funnel intake
- Role and industry coverage: broad
- Geo coverage: broad
- Freshness quality: medium

## Integration Recommendation

- Recommendation: Defer
- Rationale: useful but lower priority than ATS-native sources
- Next step: revisit after P1 and P2 pilots

## Initial Scorecard

- Relevance quality: 3
- Data freshness: 3
- Data completeness: 3
- Parse stability: 3
- Integration complexity (5 easiest): 3
- Compliance confidence: 3
- Operational reliability: 3
- Weighted score: 3.00
