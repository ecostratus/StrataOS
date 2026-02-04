# StrataOS - Personal Operating System - 60 Day Execution Plan

[![GitHub Release](https://img.shields.io/github/v/release/ecostratus/personal-operating-system-60d)](https://github.com/ecostratus/personal-operating-system-60d/releases)
[![Current](https://img.shields.io/badge/release-v0.3.0--Phase3C--Normalization-blue)](https://github.com/ecostratus/personal-operating-system-60d/releases/tag/v0.3.0-Phase3C-Normalization)

A comprehensive, auditable system for executing a 60-day career development plan integrating job search, networking, and consulting opportunities through Microsoft 365, Copilot Studio, and Python automation.

## Overview

This repository provides a structured framework designed to be:

- **Auditable**: Every action tracked with complete audit trail
- **Reversible**: All changes can be rolled back with documentation
- **Manually Overridable**: Human approval gates at critical decision points
- **Production-Ready**: Compatible with Microsoft 365, Copilot Studio, and lightweight Python scripting

## Repository Structure

```
.
├── docs/                           # Core documentation and governance
│   ├── master-brief.md            # Overall objectives and approach
│   ├── operating-constraints.md   # System boundaries and rules
│   ├── weekly-cadence.md          # Weekly operating rhythm
│   ├── governance-model.md        # Decision-making framework
│   └── risk-map.md                # Risk assessment and mitigation
│
├── automation/                     # Python automation pipelines
│   ├── job-discovery/             # Job scraping and scoring
│   ├── resume-tailoring/          # AI-assisted resume customization
│   ├── outreach/                  # Personalized message generation
│   ├── consulting-funnel/         # Proposal generation
│   └── interview-prep/            # Interview preparation automation
│
├── copilot-flows/                  # Copilot Studio integration
│   ├── high-level-architecture.md # System architecture
│   ├── flows-diagram.md           # Flow visualizations
│   └── flow-definitions/          # JSON flow definitions
│       ├── job_discovery_flow.json
│       ├── resume_tailoring_flow.json
│       ├── outreach_flow.json
│       ├── consulting_flow.json
│       └── review_governance_flow.json
│
├── prompts/                        # AI prompt templates
│   ├── style-guide.md             # Prompt engineering standards
│   ├── resume/                    # Resume tailoring prompts
│   ├── outreach/                  # Outreach message prompts
│   ├── scoring/                   # Job scoring prompts
│   ├── consulting/                # Consulting proposal prompts
│   ├── interview/                 # Interview prep prompts
│   └── review/                    # Weekly review prompts
│
├── excel-templates/                # Excel-based system of record
│   ├── system-of-record-schema.md # Data schema documentation
│   ├── system-of-record-template.xlsx
│   └── dashboards/
│       ├── dashboard-spec.md      # Dashboard specifications
│       └── 60d_operating_dashboard.xlsx
│
├── config/                         # Configuration management
│   ├── README.md                  # Configuration documentation
│   ├── env.sample.json            # Environment template
│   └── endpoints.md               # API endpoints reference
│
└── tests/                          # Test suite
    ├── README.md                  # Testing framework docs
    ├── excel_io_validation.md     # Excel I/O validation
    ├── job_discovery_tests.py     # Job discovery tests
    ├── resume_tailoring_tests.py  # Resume tailoring tests
    └── outreach_flow_tests.py     # Outreach flow tests
```

## Quick Start

### 1. Developer Setup & Authentication

For complete setup instructions including GitHub CLI authentication, see **[Developer Setup Guide](docs/developer-setup.md)**.

Quick authentication:
```bash
# Authenticate with GitHub CLI
./scripts/setup_github_auth.sh

# Or manually
gh auth login
```

### 2. Review Core Documentation
Start by understanding the system:
```bash
# Read the master brief to understand objectives
cat docs/master-brief.md

# Review operating constraints
cat docs/operating-constraints.md

# Understand the governance model
cat docs/governance-model.md
```

### 3. Configure Your Environment
```bash
# Copy the sample configuration
cp config/env.sample.json config/env.json

# Edit with your API keys and settings
# IMPORTANT: Never commit env.json (it's in .gitignore)
```

### 4. Set Up Excel System of Record
1. Review the schema: `excel-templates/system-of-record-schema.md`
2. Copy the template: `excel-templates/system-of-record-template.xlsx`
3. Customize for your needs

### 5. Install Dependencies
```bash
# For job discovery
pip install -r automation/job-discovery/scripts/requirements.txt

# For resume tailoring
pip install -r automation/resume-tailoring/scripts/requirements.txt

# For outreach
pip install -r automation/outreach/scripts/requirements.txt
```

### 6. Run Your First Automation
```bash
# Example: Run job discovery
python automation/job-discovery/scripts/job_discovery_v1.py --out-dir ./output
```

## Key Features

### Job Discovery
- Automated job scraping from multiple sources
- Intelligent scoring based on role fit, company, compensation, location, and growth
- Excel integration for tracking
- Configurable filters and rate limiting

### Resume Tailoring
- AI-powered resume customization for specific jobs
- Maintains truthfulness and authenticity
- ATS-optimized output
- Keyword integration and relevance scoring

### Outreach Management
- Personalized message generation
- Platform-specific optimization (LinkedIn, email)
- Connection point identification
- Response tracking

### Consulting Funnel
- Professional proposal generation
- Scope definition and pricing guidance
- Multiple engagement types (discovery, implementation, retainer, training)
- Terms and conditions templates

### Interview Preparation
- Company research automation
- Anticipated question generation
- STAR story development
- Questions to ask preparation

### Weekly Review & Governance
- Automated metrics reporting
- Goal tracking and achievement analysis
- Strategy adjustment recommendations
- Audit log review

## Documentation

### Essential Reading
- **[Developer Setup Guide](docs/developer-setup.md)** - Complete setup instructions including GitHub CLI authentication

### Technical Documentation
- **[Copilot Flows Architecture](copilot-flows/high-level-architecture.md)** - System design
- **[Excel Schema](excel-templates/system-of-record-schema.md)** - Data structure
- **[API Endpoints](config/endpoints.md)** - External service integration
- **[Testing Guide](tests/README.md)** - How to test the system
 - **[Progress‑to‑Launch Checklist & Timeline (Updated, PM‑Friendly)](docs/progress_to_launch_checklist_timeline.md)** - Single source of truth for status and run steps
 - **[Archived Artifacts](docs/archived_artifacts.md)** (Archived) - Superseded checklists and planning narratives

### Specifications
Each automation module includes detailed specifications:
- `automation/job-discovery/scraper-spec.md`
- `automation/job-discovery/scoring-model.md`
- `automation/resume-tailoring/prompt-spec.md`
## Security & Privacy

- **No credentials in code**: Use environment variables
- **API key management**: Sample config provided, never commit actual keys
- **Data encryption**: Guidelines for sensitive data handling
- **Audit trail**: All actions logged for compliance
- **Privacy-first**: Design respects data privacy regulations

## Testing

Run the test suite to validate functionality:

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/job_discovery_tests.py -v

# Run with coverage
pytest --cov=automation tests/
```

See [tests/README.md](tests/README.md) for comprehensive testing documentation.

### VS Code Test Tasks
- Install dev tooling: run the task “Install dev requirements” (installs `pytest`).
- Run all tests: use “Run all tests” or “Run Python tests”. These tasks use `python3` and surface failures in the Problems panel via a shared matcher.

Add a new targeted test task by reusing the shared matcher and short tracebacks:

```json
{
    "label": "Run module X tests",
    "type": "shell",
    "command": "python3",
    "args": ["-m", "pytest", "tests/module_x_tests.py", "-q", "--tb=short"],
    "group": "test",
    "problemMatcher": ["$pytest-short"]
}
```

The matcher `"$pytest-short"` is defined once in [.vscode/tasks.json](.vscode/tasks.json) and can be referenced by any future test task.

## Job Discovery: Real Endpoints
- Configure API URLs and tokens in `.env` or `config/env.sample.json`:
    - `LINKEDIN_API_URL`, `LINKEDIN_API_TOKEN` (or `LINKEDIN_API_KEY`)
    - `INDEED_API_URL`, `INDEED_API_TOKEN` (or `INDEED_PUBLISHER_KEY`)
    - Rate limits/retries: `SCRAPER_RPM`, `SCRAPER_TIMEOUT`, `SCRAPER_MAX_RETRIES`, `SCRAPER_BACKOFF_BASE`, `SCRAPER_BACKOFF_MAX`, `SCRAPER_JITTER_MS`
- Enable structured logs to a JSONL file:
    - Set `LOG_TO_FILE=true` and run with `--out-dir` to write logs to `output/run-<timestamp>.jsonl`
- Run discovery:
    - `python3 automation/job-discovery/scripts/job_discovery_v1.py --out-dir ./output`
- Summary artifact:
    - After each run, `jobs_discovered_<timestamp>.summary.json` includes enabled sources, per-source job counts, retries, rate-limit events, and totals.

### Quickstart: Job Discovery
- Prepare config in `config/env.sample.json` or `.env`.
- Run: `python3 automation/job-discovery/scripts/job_discovery_v1.py --out-dir ./output`
- Optional: `--summary-only` prints/exports summary without CSV.

#### Enrichment + Scoring (Phase 3A)
- Enable enrichment + scoring artifacts with `--enrich`:
    - `python3 automation/job-discovery/scripts/job_discovery_v1.py --out-dir ./output --enrich`
- Artifacts (deterministic filenames):
    - Matched CSV: `jobs_discovered_{YYYYMMDD_HHMMSS}.csv`
    - Enriched JSON: `jobs_enriched_{YYYYMMDD_HHMMSS}.json`
    - Scored CSV: `jobs_scored_{YYYYMMDD_HHMMSS}.csv`
- Configure scoring and enrichment in [config/env.sample.json](config/env.sample.json) and see examples in [docs/phase3A_enrichment_scoring.md](docs/phase3A_enrichment_scoring.md).

### Logging and JSONL Emission
- Default logs print to stdout.
- To write logs to JSONL, set `LOG_TO_FILE=true`.
- To suppress stdout when JSONL is enabled, set `system.log_suppress_stdout_if_jsonl=true`.

### Metrics Glossary
- jobs_fetched: items retrieved per source.
- malformed_entries: invalid or incomplete items discarded.
- retries_attempted: total retry attempts.
- rate_limit_sleeps: total sleeps due to rate limiting.
- scraper_failures: number of source failures.

### Troubleshooting
-### How to Interpret Logs and Summary Artifacts
- Logs: Each line is structured JSON with `ts`, `level`, and `event`. When JSONL is enabled, inspect the file under `output/run-<timestamp>.jsonl`. Common events include `scraper_error`, `scraper_retry_error`, `rate_limit_sleep`, and `malformed_entry`.
- Summary: A human-readable preview is printed at the end of the run. It shows totals, enabled sources, per-source jobs, malformed counts, retries, rate-limit sleeps, and failures. The full JSON summary is saved to `jobs_discovered_<timestamp>.summary.json`.

## Documentation Index
- SOP: [docs/job_discovery_sop.md](docs/job_discovery_sop.md)
- Field Mapping Reference: [docs/field_mapping_reference.md](docs/field_mapping_reference.md)
- Fixtures Overview: [tests/fixtures/README.md](tests/fixtures/README.md)
- No results: verify endpoint URLs, tokens, and source enable flags.
- Low export count: adjust filters (keywords, locations, excludes).
- Slow runs: review rate limits and timeouts in config.
- Errors only in JSONL: disable suppression or inspect JSONL file.

## Technology Stack

- **Python 3.8+**: Automation scripts
- **Microsoft Excel**: System of record and dashboards
- **Copilot Studio**: Workflow orchestration
- **Microsoft 365**: Teams, Outlook, SharePoint integration
- **OpenAI API**: AI-powered content generation
- **pytest**: Testing framework

## Requirements

- Python 3.8 or higher
- Microsoft Excel (Office 365 or Desktop)
- API keys for external services (OpenAI, job boards, etc.)
- (Optional) Microsoft 365 account for Copilot Studio integration

## Contributing

This is a personal operating system, but the structure can be adapted for your use:

1. Fork the repository
2. Customize for your needs
3. Update configuration files
4. Adapt prompts and workflows
5. Share improvements back if desired

## Changelog

See [changelog.md](changelog.md) for version history and updates. Current release: [v0.3.0-Phase3C-Normalization](https://github.com/ecostratus/personal-operating-system-60d/releases/tag/v0.3.0-Phase3C-Normalization).
<!-- TODO: External link validation required for GitHub release tag URL; validate in CI with network access. -->

## License

See [LICENSE](LICENSE) file for details.

## Support

For questions or issues:
1. Check the documentation in `docs/`
2. Review specification files in each module
3. Consult the testing guide
4. Check configuration examples

## Success Metrics

Track these KPIs to measure system effectiveness:
- Application response rate (target: 20-30%)
- Outreach response rate (target: 20-30%)
- Interview conversion rate (target: 30-40%)
- Time saved through automation
- Goal achievement rate

See the dashboard specification for comprehensive metrics tracking.

---

**Built for**: Career development professionals who want a systematic, auditable approach to their 60-day execution plan.

**Philosophy**: Automate the repetitive, maintain human judgment on the critical.

## Enable Ashby and Indeed (Optional)

Both adapters are disabled by default to prevent behavioral drift.

- **Config keys (Ashby):** `ASHBY_ENABLED` (default `false`), `ASHBY_API_URL`, `ASHBY_API_KEY`
- **Config keys (Indeed):** `INDEED_ENABLED` (default `false`), `INDEED_API_URL`, `INDEED_API_KEY`
- **Activation:** Set `*_ENABLED` to `true` and provide the corresponding URL and key.
- **Determinism:** Canonical `job_id` = SHA‑256 of `title|company|url` (lower‑trim), truncated to 16 hex; outputs are sorted and de‑duplicated by `job_id`; `posted_at` defaults to UTC `YYYY‑MM‑DD` when missing.
- **Example (Ashby):**

```python
from automation.job-discovery.scripts.source_ashby_adapter import fetch_ashby_jobs

cfg = {
    "ASHBY_ENABLED": True,
    "ASHBY_API_URL": "https://api.ashbyhq.com/jobs",
    "ASHBY_API_KEY": "YOUR_KEY"
}

jobs = fetch_ashby_jobs(cfg)
for j in jobs:
    print(j["job_id"], j["title"], j["url"])  # deterministic order
```

- **Example (Indeed):**

```python
from automation.job-discovery.scripts.source_indeed_adapter import fetch_indeed_jobs

cfg = {
    "INDEED_ENABLED": True,
    "INDEED_API_URL": "https://api.indeed.com/jobs",
    "INDEED_API_KEY": "YOUR_KEY"
}

jobs = fetch_indeed_jobs(cfg)
for j in jobs:
    print(j["job_id"], j["title"], j["url"])  # deterministic order
```

## Enable Additional Sources (Optional)

These adapters are disabled by default to prevent behavioral drift.

- **ZipRecruiter:** keys `ZIPRECRUITER_ENABLED` (default `false`), `ZIPRECRUITER_API_URL`, `ZIPRECRUITER_API_KEY`
- **Google Jobs:** keys `GOOGLEJOBS_ENABLED` (default `false`), `GOOGLEJOBS_API_URL`, `GOOGLEJOBS_API_KEY`
- **Glassdoor:** keys `GLASSDOOR_ENABLED` (default `false`), `GLASSDOOR_API_URL`, `GLASSDOOR_API_KEY`
- **Craigslist:** keys `CRAIGSLIST_ENABLED` (default `false`), `CRAIGSLIST_API_URL`
- **GoRemote:** keys `GOREMOTE_ENABLED` (default `false`), `GOREMOTE_API_URL`

- **Activation:** Set `*_ENABLED` to `true` and provide the corresponding URL/key as applicable.
- **Determinism:** Canonical `job_id` = SHA‑256 of `title|company|url` (lower‑trim), truncated to 16 hex; outputs are sorted and de‑duplicated by `job_id`; `posted_at` defaults to UTC `YYYY‑MM‑DD` when missing.

## Scoring Configuration (Phase 3A)
- Configure scoring in [config/env.sample.json](config/env.sample.json) under `scoring.weights` and `scoring.thresholds`.
- Typical keys for Phase 3A:
    - `weights`: `role_fit`, `stack`, `remote` (proportions; sum not required to equal 1.0)
    - `thresholds`: `exceptional`, `strong`, `moderate`, `weak` in [0,1]
- See examples and details in [docs/phase3A_enrichment_scoring.md](docs/phase3A_enrichment_scoring.md).

Minimal example (see full sample in config/env.sample.json):

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
