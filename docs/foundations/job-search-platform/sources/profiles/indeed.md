# Source Profile: Indeed

## Metadata

- Source name: Indeed
- Category: Job board
- Priority: P2
- Profile owner: Product + Engineering
- Last reviewed: 2026-07-29
- Status: Existing placeholder

## Access and Integration

- Access model: API and partner pathways
- Authentication: key-based for approved integrations
- Rate limits: tier dependent
- Pagination model: page and size
- Change frequency: Medium
- Webhook or push support: limited

## Terms and Compliance

- Terms URL: https://www.indeed.com/legal
- Data use constraints: strict program terms likely apply
- Automation constraints: non-approved automation may be restricted
- Resume upload or apply automation constraints: policy-sensitive
- Attribution requirements: possible
- Regional compliance notes: standard privacy requirements

## Data Contract

- Core fields available: title, company, location, url, date
- Missing fields: salary variability and consistency issues
- Field quality notes: broad coverage with mixed signal quality
- Example payload shape: API list or enveloped payload
- Known schema variability: medium

## Reliability

- Uptime expectations: good via official paths
- Common error classes: auth, quota, schema envelope differences
- Retry and backoff strategy: exponential and robust envelope parsing
- Circuit-breaker recommendation: yes

## Product Fit

- Best use case: high-volume top-of-funnel source
- Role and industry coverage: broad
- Geo coverage: broad
- Freshness quality: medium to high

## Integration Recommendation

- Recommendation: Pilot
- Rationale: large volume, but terms and quality controls are critical
- Next step: validate approved access and scoring quality thresholds

## Initial Scorecard

- Relevance quality: 3
- Data freshness: 4
- Data completeness: 3
- Parse stability: 3
- Integration complexity (5 easiest): 3
- Compliance confidence: 2
- Operational reliability: 4
- Weighted score: 3.25
