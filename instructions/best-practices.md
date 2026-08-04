# Best Practices

## Discovery and Filtering
- Keep policy-disallowed sources disabled when compliance enforcement is on.
- Use venv-backed commands for consistent dependencies.
- Keep `include_low_relevance` off in normal workflows to reduce noise.

## Scoring and Relevance
- Tune thresholds with production samples before changing defaults.
- Prefer config-driven filters over hardcoded logic in UI components.
- Validate relevance changes with both API tests and smoke runs.

## Operations
- Always preserve run artifacts (`output/`, `logs/`) for traceability.
- Use explicit toggles for advanced behavior so defaults remain safe.
- Keep source credentials out of committed files.

## Testing
- Add tests for new filter defaults and explicit override paths.
- Ensure both list and search endpoints enforce consistent relevance behavior.
