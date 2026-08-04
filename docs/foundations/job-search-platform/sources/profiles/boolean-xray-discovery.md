# Source Profile: Boolean/X-ray Discovery via Search API + Enrichment API

## Metadata

- Source name: Boolean/X-ray discovery
- Category: Recruiter and hiring-manager discovery
- Priority: P2
- Profile owner: Product + Engineering
- Last reviewed: 2026-08-01
- Status: Proposed

## Access and Integration

- Access model: Hybrid
- Authentication: Search API key and enrichment API key
- Rate limits: Varies by provider and plan; requires throttling and quota management
- Pagination model: Query pagination plus enrichment batch limits
- Change frequency: Medium
- Webhook or push support: Not typical for this workflow

## Terms and Compliance

- Terms URL: Provider terms for the chosen search and enrichment services
- Data use constraints: Use only public-index results and approved enrichment data that the provider permits; avoid scraping LinkedIn or other protected endpoints directly
- Automation constraints: Keep requests rate-limited and provider-compliant; avoid bot-like behavior or bypassing access controls
- Resume upload or apply automation constraints: Not part of the discovery path
- Attribution requirements: Follow provider attribution and usage guidance
- Regional compliance notes: Review privacy and contact-data regulations for any enrichment payloads

## Data Contract

- Core fields available: person name, title, company, public profile preview URL, public search result URL, verified email where permitted, confidence, source metadata
- Missing fields: full profile content and complete employment history are often incomplete or unavailable
- Field quality notes: Search results are broad and often require normalization, deduplication, and confidence scoring
- Example payload shape: search_result -> enrichment_result -> canonical contact record
- Known schema variability: medium to high

## Reliability

- Uptime expectations: medium to high depending on provider
- Common error classes: quota exhaustion, rate limiting, stale index data, low-confidence matches
- Retry and backoff strategy: exponential backoff with jitter and per-source deduplication
- Circuit-breaker recommendation: yes

## Product Fit

- Best use case: discovering hiring managers and building targeted outreach lists for specific companies and roles
- Role and industry coverage: strong for technical, product, and GTM roles in well-indexed companies
- Geo coverage: broad but dependent on search index quality
- Freshness quality: moderate and provider-dependent

## Integration Recommendation

- Recommendation: Pilot
- Rationale: This pattern is structurally aligned with StrataOS discovery -> enrichment -> scoring and is materially different from direct scraping. It can be implemented with approved APIs that respect provider terms.
- Next step: define a sanctioned provider list, implement a source adapter around a search API plus an enrichment API, and add policy gating plus a contact-quality score.
