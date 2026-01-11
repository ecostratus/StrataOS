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
- Progress-to-Launch Checklist & Timeline: [progress_to_launch_checklist_timeline.md](progress_to_launch_checklist_timeline.md)

## Releases
Latest release: [v0.3.5-Phase3E-CLI-PromptRendering](https://github.com/ecostratus/personal-operating-system-60d/releases/tag/v0.3.5-Phase3E-CLI-PromptRendering). See the top-level [changelog.md](../changelog.md) for detailed history.

## Logging & Metrics
- Events log: `logs/events.jsonl` — JSON Lines of prompt render events (category, timing, output path). Emitted by `outreach_generator_v1.py` and `resume_tailor_v1.py`.
- Metrics counters: `logs/metrics.json` — simple per-category counters (e.g., renders, errors). Updated automatically by scripts.
- CLI: `automation/common/metrics_cli.py` — `--summary` prints current metrics; `--reset` clears counters.
- VS Code tasks:
	- “Metrics: Show summary” — prints metrics via CLI
	- “Metrics: Reset counters” — clears counters via CLI
	- “Metrics: Open JSON” — prints raw `logs/metrics.json`