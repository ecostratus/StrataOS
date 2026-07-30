# Development Policies

## Engineering Principles

- Keep source adapters independent and testable.
- Preserve deterministic behavior for ingestion pipelines.
- Favor additive schema migrations over destructive changes.
- Include observability with every critical change.

## Source Integration Policy

Before enabling a new source:

1. Confirm terms permit intended use.
2. Prefer official APIs over scraping.
3. Define rate limits and retry strategy.
4. Add parser contract tests using representative payloads.
5. Add feature flag for controlled rollout.

## Data Quality Policy

- Normalize key fields before indexing.
- Track parse failures and malformed records.
- Do not silently drop critical errors.

## Security Policy

- Never commit real API keys or tokens.
- Use local secrets and environment variables.
- Rotate leaked or exposed credentials immediately.

## Testing Policy

- Unit tests for query parsing and filtering.
- Contract tests for each source adapter.
- Integration tests for end-to-end search workflow.
- Performance checks for query latency on representative data.

## Documentation Policy

- Update docs in this hub when behavior changes.
- Record major decisions in RAID.
- Keep backlog priorities visible and current.
