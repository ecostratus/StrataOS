# Automation Guide

**Version:** 1.0  
**Last Updated:** 2026-01-07

---

## Overview

The `automation/` folder contains Python modules for each domain of the 60-day operating system. All modules read from and write to the canonical 10-sheet System of Record (SoR).

---

## Module Reference

| Module | Sheet(s) Used | Purpose |
|--------|---------------|---------|
| `job-discovery/` | Roles, Companies | Scrapes and scores job listings |
| `outreach/` | Outreach, Contacts | Generates personalized outreach |
| `resume-tailoring/` | Roles | Customizes resumes per role |
| `interview-prep/` | Interviews, Roles | Prepares interview materials |
| `consulting-funnel/` | Consulting, Companies | Manages consulting proposals |
| `enrichment/` | Roles, Companies | Enriches job records |
| `common/` | — | Shared utilities (normalization, logging) |
| `core/` | All sheets | SoR integration utilities |
| `sync/` | All sheets | SoR synchronization modules |
| `validation/` | All sheets | Schema and canonical compliance validators |

---

## Error Handling

All automation errors must be logged to the **FlowErrors** sheet:

```python
from automation.core.sor import log_flow_error

log_flow_error(
    flow_name="job_discovery_v1",
    error_message="Source timeout",
    payload={"source": "indeed", "url": "..."}
)
```

Fields written: `ErrorID`, `FlowName`, `Timestamp`, `ErrorMessage`, `Payload`, `Resolved`.

---

## Change Tracking

Structural changes must be recorded in the **ChangeLog** sheet:

```python
from automation.core.sor import log_change

log_change(
    sheet_name="Roles",
    field_name="Status",
    old_value="Identified",
    new_value="Applied",
    changed_by="job_discovery_v1"
)
```

Fields written: `ChangeID`, `SheetName`, `FieldName`, `OldValue`, `NewValue`, `ChangedBy`, `ChangedAt`.

---

## Running Automations

### Job Discovery

```bash
python3 automation/job-discovery/scripts/job_discovery_v1.py --out-dir ./output
python3 automation/job-discovery/scripts/job_discovery_v1.py --out-dir ./output --enrich
```

### Resume Tailoring

```bash
python3 automation/resume-tailoring/scripts/resume_tailor_v1.py
```

### Outreach

```bash
python3 automation/outreach/scripts/outreach_generator_v1.py
```

### Interview Prep

```bash
python3 automation/interview-prep/scripts/interview_prep_v1.py
```

### Consulting Funnel

```bash
python3 automation/consulting-funnel/scripts/consulting_offer_v1.py
```

---

## Validation

Before writing to the SoR, validate data against the canonical schema:

```bash
python3 automation/validation/schema_validator.py --sheet Roles --data output/roles.json
```

---

## Configuration

All modules read from `config/env.json`. See [config/README.md](../../config/README.md) for available keys.

---

## Shared Utilities (`automation/common/`)

| Module | Purpose |
|--------|---------|
| `normalization.py` | String and type normalization helpers |
| `logging.py` | Structured JSONL logging |
| `metrics.py` | KPI collection helpers |
| `prompt_renderer.py` | Renders prompt templates with context |

---

## References

- [docs/ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- [docs/SCHEMA.md](SCHEMA.md) — Canonical data model
- [config/validation-rules.json](../../config/validation-rules.json) — Validation rules
- [automation/validation/schema_validator.py](../../automation/validation/schema_validator.py) — Schema validator
