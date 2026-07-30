# Source Profile: ZipRecruiter

## Metadata

- Source name: ZipRecruiter
- Category: Job board
- Priority: P1
- Profile owner: Product + Engineering
- Last reviewed: 2026-07-29
- Status: Existing placeholder

## Access and Integration

- Access model: API and partner options
- Authentication: key-based for official paths
- Rate limits: tier dependent
- Pagination model: page and limit
- Change frequency: Medium
- Webhook or push support: limited

## Terms and Compliance

- Terms URL: https://www.ziprecruiter.com
- Data use constraints: depends on access agreement
- Automation constraints: controlled for non-official automation
- Resume upload or apply automation constraints: requires explicit permission
- Attribution requirements: likely
- Regional compliance notes: standard privacy handling

## Data Contract

- Core fields available: title, company, location, url, post date
- Missing fields: salary may vary
- Field quality notes: generally usable with normalization
- Example payload shape: API object list
- Known schema variability: medium

## Reliability

- Uptime expectations: good with official API
- Common error classes: auth and quota errors
- Retry and backoff strategy: exponential with bounded retries
- Circuit-breaker recommendation: yes

## Product Fit

- Best use case: broad listing expansion
- Role and industry coverage: broad
- Geo coverage: strong in major markets
- Freshness quality: medium to high

## Integration Recommendation

- Recommendation: Pilot
- Rationale: promising source; verify access path and terms first
- Next step: validate API access model and payload contract

## Initial Scorecard

- Relevance quality: 3
- Data freshness: 4
- Data completeness: 3
- Parse stability: 3
- Integration complexity (5 easiest): 3
- Compliance confidence: 3
- Operational reliability: 4
- Weighted score: 3.35
