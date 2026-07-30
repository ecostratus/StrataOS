# Source Profile: Workday Career Sites

## Metadata

- Source name: Workday Career Sites
- Category: Corporate careers (ATS)
- Priority: P1
- Profile owner: Engineering
- Last reviewed: 2026-07-29
- Status: Planned

## Access and Integration

- Access model: Scraping or endpoint discovery by tenant
- Authentication: Usually public browsing for listings
- Rate limits: Site dependent
- Pagination model: Page or cursor-like APIs per tenant
- Change frequency: Medium to high
- Webhook or push support: None typical

## Terms and Compliance

- Terms URL: tenant specific
- Data use constraints: must be reviewed per employer site policy
- Automation constraints: bot detection common
- Resume upload or apply automation constraints: high policy sensitivity
- Attribution requirements: site dependent
- Regional compliance notes: country-specific legal notices vary

## Data Contract

- Core fields available: title, location, requisition id, url
- Missing fields: salary often absent
- Field quality notes: good role detail, inconsistent format
- Example payload shape: tenant-specific JSON responses
- Known schema variability: high

## Reliability

- Uptime expectations: generally stable, implementation varies
- Common error classes: anti-bot challenges, payload changes
- Retry and backoff strategy: conservative with low request rates
- Circuit-breaker recommendation: yes

## Product Fit

- Best use case: direct employer roles
- Role and industry coverage: broad across enterprises
- Geo coverage: broad
- Freshness quality: medium to high

## Integration Recommendation

- Recommendation: Pilot
- Rationale: strong value, but requires robust parser framework and policy checks
- Next step: build tenant pattern library and validation harness

## Initial Scorecard

- Relevance quality: 5
- Data freshness: 4
- Data completeness: 3
- Parse stability: 2
- Integration complexity (5 easiest): 2
- Compliance confidence: 3
- Operational reliability: 3
- Weighted score: 3.45
