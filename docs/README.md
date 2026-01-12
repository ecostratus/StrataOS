# Documentation

This folder contains all documentation related to the 60-day personal operating system.

## Purpose

The docs folder serves as the central knowledge base for:
- System architecture and design decisions
- User guides and how-to documentation
- Process documentation and workflows
- Best practices and conventions
- System overview and onboarding materials

## Contents

- Architecture documentation
- API and integration guides
- User manuals and tutorials
- Change logs and version history
- Reference materials

This documentation supports the 60-day operating system by providing clear, accessible information for understanding and using the system effectively.

## Quick Links
- Progress‑to‑Launch Checklist & Timeline (Updated, PM‑Friendly): [progress_to_launch_checklist_timeline.md](progress_to_launch_checklist_timeline.md)
- Archived Artifacts: [archived_artifacts.md](archived_artifacts.md) (Archived)

## Releases
Current: [v0.3.0-Phase3C-Normalization](https://github.com/ecostratus/personal-operating-system-60d/releases/tag/v0.3.0-Phase3C-Normalization)

Historical releases:
- [v0.1.0 (Phase 1)](https://github.com/ecostratus/personal-operating-system-60d/releases/tag/v0.1.0)
- [v0.1.1 (Phase 2A)](https://github.com/ecostratus/personal-operating-system-60d/releases/tag/v0.1.1)
- [v0.2.0 (Phase 2C)](https://github.com/ecostratus/personal-operating-system-60d/releases/tag/v0.2.0)
- [v0.3.2 (Phase 3D – Lever)](https://github.com/ecostratus/personal-operating-system-60d/releases/tag/v0.3.2-Phase3D-Lever)
- [v0.3.3 (Phase 3D – Extended Sources)](https://github.com/ecostratus/personal-operating-system-60d/releases/tag/v0.3.3-Phase3D-ExtendedSources)
- [v0.3.4 (Phase 3E – Enrichment)](https://github.com/ecostratus/personal-operating-system-60d/releases/tag/v0.3.4-Phase3E-Enrichment)
- [v0.3.5 (Phase 3E – CLI/Prompt Rendering)](https://github.com/ecostratus/personal-operating-system-60d/releases/tag/v0.3.5-Phase3E-CLI-PromptRendering)

See the top-level [changelog.md](../changelog.md) for detailed history.

<!-- TODO: External link validation required for GitHub release tag URLs; validate in CI with network access. -->

## Logging & Metrics
- Events log: `logs/events.jsonl` — JSON Lines of prompt render events (category, timing, output path). Emitted by `outreach_generator_v1.py` and `resume_tailor_v1.py`.
- Metrics counters: `logs/metrics.json` — simple per-category counters (e.g., renders, errors). Updated automatically by scripts.
- CLI: `automation/common/metrics_cli.py` — `--summary` prints current metrics; `--reset` clears counters.
- VS Code tasks:
	- “Metrics: Show summary” — prints metrics via CLI
	- “Metrics: Reset counters” — clears counters via CLI
	- “Metrics: Open JSON” — prints raw `logs/metrics.json`

## Try It
Jump into observability quickly:

```bash
# Open the events log via Makefile utility
make logs-open-events

# Show metrics summary via CLI
./.venv/bin/python automation/common/metrics_cli.py --summary

# Reset metrics counters
./.venv/bin/python automation/common/metrics_cli.py --reset
```

See the “Logging & Metrics” section above for paths and task shortcuts.

Tip: Open the command palette and run "Tasks: Run Task" → "Metrics: Show summary" (or "Metrics: Reset counters" / "Logs: Open events").