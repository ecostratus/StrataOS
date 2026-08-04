# Source Research Backlog

Track candidate sources for jobs, recruiter discovery, and optional apply workflows.

## Evaluation Dimensions

- Access model: public API, partner API, feed, or scraping
- Terms and compliance constraints
- Coverage relevance to target roles
- Data quality and freshness
- Integration complexity
- Operational reliability

## Priority Queue

| Priority | Source | Category | Access Model | Primary Use | Policy Review Needed | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | LinkedIn | Job board and network | API and web | Jobs and recruiter discovery | Yes | In progress | Existing partial support; expand query model |
| P1 | Workday company career pages | Corporate careers | Web and possible feeds | Direct employer roles | Yes | Planned | Standardize tenant-specific parsers |
| P1 | Greenhouse-hosted boards | ATS-hosted careers | Public JSON endpoints on many sites | Job postings | Yes | Existing | Improve schema normalization |
| P1 | Lever-hosted boards | ATS-hosted careers | Public JSON endpoints on many sites | Job postings | Yes | Existing | Improve coverage and metadata |
| P1 | ZipRecruiter | Job board | API and partner options | Broader posting coverage | Yes | Existing placeholder | Validate current access path |
| P2 | Indeed | Job board | API and partner options | Broad volume source | Yes | Existing placeholder | Validate contract and data use |
| P2 | Dice | Job board | Public/partner channels | Tech-heavy jobs | Yes | Planned | Evaluate role-quality signal |
| P2 | Monster | Job board | Public/partner channels | Broad volume source | Yes | Planned | Validate terms and API options |
| P2 | CareerBuilder | Job board | Partner channels | Broad source diversity | Yes | Planned | Evaluate feed consistency |
| P2 | Wellfound | Startup jobs | Public web and partner | Startup opportunities | Yes | Planned | Evaluate location metadata quality |
| P2 | Built In | Tech job board | Public web | Regional tech jobs | Yes | Planned | Consider geo coverage strategy |
| P3 | Company career microsites | Corporate careers | Web scraping by pattern | Niche targeted companies | Yes | Planned | Build reusable extractor toolkit |
| P3 | Recruiter directories | Recruiter discovery | Public and paid sources | Outreach list building | Yes | Discovery | Define acceptable usage boundaries |
| P2 | Boolean/X-ray discovery via search API + enrichment API | Recruiter discovery | API and partner | Hiring-manager discovery and contact enrichment | Yes | Proposed | Use a search API for public-index lookups and an approved enrichment API for contact resolution; avoid scraping LinkedIn directly |

## Deep Research Backlog

1. Build source profile template
- Access method and auth requirements
- Terms and allowed use matrix
- Fields available and gaps
- Rate limits and anti-abuse controls
- Example payload and parser notes

2. Build source scorecard
- Relevance score
- Freshness score
- Parse reliability score
- Legal and compliance risk score
- Integration effort estimate

3. Build connector strategy
- API-first connectors
- Feed connectors
- Scraping connectors with strict safeguards
- Fallback behavior and disable switches

## Apply and Resume Posting Capabilities

Track separately because policy risk is higher.

| Capability | Candidate Sources | Feasibility | Policy Risk | Notes |
| --- | --- | --- | --- | --- |
| One-click apply links | Most job boards and ATS pages | High | Low | Start with link-outs only |
| Resume upload automation | Selected boards with partner APIs | Medium | Medium | Needs explicit policy and consent design |
| Automated application submission | Board-dependent | Low to Medium | High | Do not implement without legal and policy review |

## Next Research Actions

1. Create top-10 source profile documents.
2. Validate terms for each P1 source.
3. Run a small payload collection for parser prototyping.
4. Prioritize integrations by relevance and compliance fit.
