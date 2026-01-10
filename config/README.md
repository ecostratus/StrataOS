# Configuration

This folder contains configuration files for the 60-day personal operating system.

## Purpose

The config folder stores:
- System configuration files
- Environment-specific settings
- Integration configurations
- User preferences and defaults
- Application settings

## Contents

- YAML/JSON configuration files
- Environment variable templates
- API keys and credentials (reference only)
- Feature flags and toggles
- System parameters and constants

## Security Note

Never commit sensitive information like passwords or API keys. Use environment variables or secure secret management solutions.

## Usage

Configuration files centralize system settings, making the 60-day operating system easier to maintain, deploy, and customize across different environments.

## Scoring & Enrichment Configuration (Phase 3A)
Configure scoring under `scoring.weights` and `scoring.thresholds` and enrichment under `enrichment.*`.

- Weights (proportions; sum not required to equal 1.0): `role_fit`, `stack`, `remote`
- Thresholds (normalized [0,1]): `exceptional`, `strong`, `moderate`, `weak`
- Enrichment keys (optional, safe defaults):
	- `keywords.role` (e.g., ["engineer", "developer"]) 
	- `keywords.stack` (e.g., ["python", "javascript", "aws"]) 
	- `remote_aliases` (e.g., ["remote", "hybrid"]) 
	- `seniority_patterns` (regex → level)

Minimal example (see full sample in [config/env.sample.json](env.sample.json)):

```json
{
	"scoring": {
		"weights": { "role_fit": 0.5, "stack": 0.3, "remote": 0.2 },
		"thresholds": { "exceptional": 0.85, "strong": 0.7, "moderate": 0.5 }
	},
	"enrichment": {
		"keywords": { "role": ["engineer", "developer"], "stack": ["python", "aws"] },
		"remote_aliases": ["remote", "hybrid"],
		"seniority_patterns": { "\\b(sr|senior)\\b": "Senior", "\\b(jr|junior)\\b": "Junior" }
	}
}
```

See detailed guidance in [docs/phase3A_enrichment_scoring.md](../docs/phase3A_enrichment_scoring.md).

## Normalization Milestone (Phase 3C)
Phase 3C consolidates the normalization boundary and introduces shared typed helpers to ensure clean, deterministic inputs across enrichment and scoring. Enrichment config lists (seniority patterns, stack patterns, keyword lists, role‑fit heuristics) are normalized once at load time, with defensive normalization at function entry. Release details: [v0.3.0-Phase3C-Normalization](https://github.com/ecostratus/personal-operating-system-60d/releases/tag/v0.3.0-Phase3C-Normalization).
