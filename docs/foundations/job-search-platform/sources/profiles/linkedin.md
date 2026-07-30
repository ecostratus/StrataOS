# Source Profile: LinkedIn

## Metadata

- Source name: LinkedIn
- Category: Job board and recruiter network
- Priority: P1
- Profile owner: Product + Engineering
- Last reviewed: 2026-07-29
- Status: In progress

## Access and Integration

- Access model: Hybrid
- Authentication: Partner APIs and authenticated sessions depending on path
- Rate limits: Varies by access tier
- Pagination model: Cursor or page-based depending on endpoint
- Change frequency: High
- Webhook or push support: Limited for typical job search use cases

## Terms and Compliance

- Terms URL: https://www.linkedin.com/legal
- Data use constraints: Must follow platform terms and API program limits
- Automation constraints: High restrictions for scripted interactions
- Resume upload or apply automation constraints: Requires strict review
- Attribution requirements: Potentially required depending on data path
- Regional compliance notes: Follow local privacy obligations

## Data Contract

- Core fields available: title, company, location, url, post date
- Missing fields: salary often inconsistent
- Field quality notes: strong company metadata, variable compensation data
- Example payload shape: API-dependent
- Known schema variability: medium

## Reliability

- Uptime expectations: high for official API paths
- Common error classes: auth, rate limit, permission
- Retry and backoff strategy: exponential with jitter
- Circuit-breaker recommendation: yes

## Product Fit

- Best use case: high-value roles and recruiter visibility
- Role and industry coverage: broad
- Geo coverage: broad
- Freshness quality: high

## Integration Recommendation

- Recommendation: Pilot
- Rationale: high value but compliance and access constraints are non-trivial
- Next step: map approved access paths and terms-compliant ingestion approach

## Initial Scorecard

- Relevance quality: 5
- Data freshness: 5
- Data completeness: 4
- Parse stability: 3
- Integration complexity (5 easiest): 2
- Compliance confidence: 2
- Operational reliability: 4
- Weighted score: 3.85
