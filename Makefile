# Project utility targets

.PHONY: logs-open-events metrics-summary metrics-reset clean-cache next-changelog

logs-open-events:
	@if [ -f logs/events.jsonl ]; then cat logs/events.jsonl; else echo "No events log found (logs/events.jsonl)"; fi

metrics-summary:
	@./.venv/bin/python automation/common/metrics_cli.py --summary || true

metrics-reset:
	@./.venv/bin/python automation/common/metrics_cli.py --reset || true

clean-cache:
	@find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	@rm -rf .pytest_cache
	@echo "Cache cleared (.__pycache__, .pytest_cache)"

next-changelog:
	@mkdir -p docs/releases
	@echo "# v0.3.6 - Draft\n\n## Summary\n- Placeholder for upcoming features\n\n## Planned Work\n- Snapshot test expansion\n- Metrics aggregation and dashboarding\n- Resume Tailoring v1 behavior extensions\n\n## Notes\n- TBD" > docs/releases/v0.3.6-draft.md
	@echo "Draft release notes created: docs/releases/v0.3.6-draft.md"
