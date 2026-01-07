# Personal Operating System - 60 Day Execution Plan

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

### 1. Review Core Documentation
Start by understanding the system:
```bash
# Read the master brief to understand objectives
cat docs/master-brief.md

# Review operating constraints
cat docs/operating-constraints.md

# Understand the governance model
cat docs/governance-model.md
```

### 2. Configure Your Environment
```bash
# Copy the sample configuration
cp config/env.sample.json config/env.json

# Edit with your API keys and settings
# IMPORTANT: Never commit env.json (it's in .gitignore)
```

### 3. Set Up Excel System of Record
1. Review the schema: `excel-templates/system-of-record-schema.md`
2. Copy the template: `excel-templates/system-of-record-template.xlsx`
3. Customize for your needs

### 4. Install Dependencies
```bash
# For job discovery
pip install -r automation/job-discovery/scripts/requirements.txt

# For resume tailoring
pip install -r automation/resume-tailoring/scripts/requirements.txt

# For outreach
pip install -r automation/outreach/scripts/requirements.txt
```

### 5. Run Your First Automation
```bash
# Example: Run job discovery
python automation/job-discovery/scripts/job_scraper_v1.py
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
1. **[Master Brief](docs/master-brief.md)** - Start here to understand the overall approach
2. **[Operating Constraints](docs/operating-constraints.md)** - System boundaries and rules
3. **[Governance Model](docs/governance-model.md)** - How decisions are made
4. **[Weekly Cadence](docs/weekly-cadence.md)** - Your operating rhythm
5. **[Risk Map](docs/risk-map.md)** - Risks and mitigation strategies

### Technical Documentation
- **[Copilot Flows Architecture](copilot-flows/high-level-architecture.md)** - System design
- **[Prompt Style Guide](prompts/style-guide.md)** - AI prompt best practices
- **[Excel Schema](excel-templates/system-of-record-schema.md)** - Data structure
- **[API Endpoints](config/endpoints.md)** - External service integration
- **[Testing Guide](tests/README.md)** - How to test the system

### Specifications
Each automation module includes detailed specifications:
- `automation/job-discovery/scraper-spec.md`
- `automation/job-discovery/scoring-model.md`
- `automation/resume-tailoring/prompt-spec.md`
- `automation/outreach/prompt-spec.md`
- `automation/consulting-funnel/prompt-spec.md`
- `automation/interview-prep/prompt-spec.md`

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

See [changelog.md](changelog.md) for version history and updates.

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
