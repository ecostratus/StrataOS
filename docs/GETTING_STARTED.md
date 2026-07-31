# Getting Started with StrataOS

**Version:** 1.0  
**Last Updated:** 2026-01-07

---

## Prerequisites

- Python 3.8 or higher
- Microsoft Excel (Office 365 or Desktop)
- API keys for external services (OpenAI, job boards)
- (Optional) Microsoft 365 account for Copilot Studio integration

---

## 1. Clone the Repository

```bash
git clone https://github.com/ecostratus/StrataOS.git
cd StrataOS
```

---

## 2. Configure Your Environment

```bash
# Copy the sample configuration
cp config/env.sample.json config/env.json

# Edit with your API keys and settings
# IMPORTANT: Never commit env.json — it is listed in .gitignore
```

Key environment variables in `config/env.json`:

| Key | Description |
|-----|-------------|
| `OPENAI_API_KEY` | OpenAI API key for AI-powered prompts |
| `LINKEDIN_API_URL` | LinkedIn job listings endpoint |
| `INDEED_API_URL` | Indeed job listings endpoint |
| `SCORING_WEIGHTS` | Job scoring weight configuration |

See [config/README.md](../config/README.md) and [config/endpoints.md](../config/endpoints.md) for the full list.

---

## 3. Install Dependencies

```bash
# Install all development dependencies (includes pytest)
pip install -r dev-requirements.txt

# Per-module dependencies
pip install -r automation/job-discovery/scripts/requirements.txt
pip install -r automation/resume-tailoring/scripts/requirements.txt
pip install -r automation/outreach/scripts/requirements.txt
pip install -r automation/interview-prep/scripts/requirements.txt
pip install -r automation/consulting-funnel/scripts/requirements.txt
```

---

## 4. Set Up the System of Record (SoR)

1. Open `excel-templates/system-of-record-template.xlsx` in Microsoft Excel.
2. Review the 10 canonical sheets: Roles, Companies, Contacts, Outreach, Interviews, Consulting, Metrics, StatusHistory, FlowErrors, ChangeLog.
3. Save a working copy — do **not** rename or delete any sheets.
4. See [docs/SCHEMA.md](SCHEMA.md) for field definitions.

---

## 5. Run Your First Automation

### Job Discovery

```bash
python3 automation/job-discovery/scripts/job_discovery_v1.py --out-dir ./output
```

### Resume Tailoring

```bash
python3 automation/resume-tailoring/scripts/resume_tailor_v1.py
```

### Outreach Generation

```bash
python3 automation/outreach/scripts/outreach_generator_v1.py
```

---

## 6. Run the Test Suite

```bash
# Run all tests
pytest tests/ -v

# Run schema validation tests only
pytest tests/schema-validation/ -v

# Run with coverage
pytest --cov=automation tests/
```

See [docs/TESTING.md](TESTING.md) for the full testing guide.

---

## 7. Launch the Control Center (Optional)

```bash
# Single-port mode: UI + API on http://127.0.0.1:8811
./run.sh

# Development mode with hot reload
./run.sh --dev
```

---

## Next Steps

- Read [docs/ARCHITECTURE.md](ARCHITECTURE.md) to understand the system design.
- Review [docs/SCHEMA.md](SCHEMA.md) for the canonical data model.
- Explore [automation/README.md](../automation/README.md) for automation module details.
- Check [REPO_NORMALIZATION.md](../REPO_NORMALIZATION.md) for compliance standards.
