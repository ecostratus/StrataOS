# StrataOS Architecture

**Version:** 1.0  
**Status:** Authoritative  
**Last Updated:** 2026-01-07

---

## Overview

StrataOS is a 60-day personal operating system for career development. It integrates job discovery, networking, consulting, and interview preparation through a governed System of Record (SoR) backed by Python automation, Copilot Studio flows, and a React-based control center.

---

## System of Record (SoR)

The SoR is the canonical data backbone. It consists of exactly **10 sheets**:

| # | Sheet | Purpose |
|---|-------|---------|
| 1 | **Roles** | Target job roles and position definitions |
| 2 | **Companies** | Organizations of interest |
| 3 | **Contacts** | Professional network and relationships |
| 4 | **Outreach** | Communication tracking and follow-ups |
| 5 | **Interviews** | Interview pipeline and scheduling |
| 6 | **Consulting** | Consulting opportunities and engagements |
| 7 | **Metrics** | KPIs and performance indicators |
| 8 | **StatusHistory** | Historical state tracking |
| 9 | **FlowErrors** | Automation error logging |
| 10 | **ChangeLog** | Audit trail of system modifications |

> **No additional sheets are permitted.** See [SCHEMA.md](SCHEMA.md) for full field definitions.

---

## Folder Architecture

```
StrataOS/
├── docs/                    # Documentation and architecture guides
├── automation/              # Python automation modules
├── copilot-flows/           # GitHub Copilot workflow definitions
├── prompts/                 # AI prompt templates and instructions
├── excel-templates/         # Template files for the SoR
├── dashboards/              # Visualization and reporting configs
├── config/                  # System configuration files
├── tests/                   # Validation and test suites
├── LICENSE
├── README.md
└── REPO_NORMALIZATION.md
```

---

## Component Architecture

### 1. Automation Layer (`automation/`)

Python modules organized by domain:

- **`job-discovery/`** — Scrapes and scores job listings from multiple sources.
- **`outreach/`** — Generates personalized outreach messages.
- **`resume-tailoring/`** — Customizes resumes for specific roles.
- **`interview-prep/`** — Prepares interview materials per role.
- **`consulting-funnel/`** — Manages consulting proposals and engagements.
- **`enrichment/`** — Enriches job records with additional metadata.
- **`common/`** — Shared utilities (normalization, logging, metrics).
- **`core/`** — Core SoR integration utilities.
- **`sync/`** — SoR synchronization modules.
- **`validation/`** — Schema and canonical compliance validators.

### 2. Copilot Flows (`copilot-flows/`)

GitHub Copilot / Copilot Studio workflow definitions in YAML and JSON:

- `outreach-flow.yml` — Guides outreach generation against the Outreach sheet.
- `interview-prep-flow.yml` — Guides interview preparation against the Interviews sheet.
- `metrics-update-flow.yml` — Updates the Metrics sheet from computed KPIs.
- `flow-definitions/` — JSON definitions for Copilot Studio integration.

### 3. Prompts Library (`prompts/`)

Structured AI prompts aligned to canonical SoR sheets:

- `outreach-email.md` — Templates for Outreach sheet records.
- `interview-research.md` — Research prompts for Interviews sheet records.
- `resume-tailor.md` — Resume customization prompts for Roles sheet records.

### 4. Excel Templates (`excel-templates/`)

- `system-of-record-template.xlsx` — Canonical 10-sheet Excel template.
- `system-of-record-schema.md` — Field-level schema documentation.
- `dashboards/` — Dashboard configurations and specs.

### 5. Config (`config/`)

- `schema.json` — Canonical SoR schema as a machine-readable JSON document.
- `validation-rules.json` — Validation rules for each sheet and field.
- `env.sample.json` — Environment variable template.

### 6. Dashboards (`dashboards/`)

- `metrics-dashboard.json` — KPI visualization configuration.
- `pipeline-view.json` — Role/application pipeline view configuration.

### 7. Tests (`tests/`)

- `schema-validation/` — Tests that verify canonical schema compliance.
- `integration/` — End-to-end flow integration tests.
- `fixtures/` — Test data using canonical sheet structures.

---

## Data Flow

```
Job Sources → automation/job-discovery → Roles + Companies (SoR)
                                       ↓
                              automation/enrichment
                                       ↓
                    automation/resume-tailoring + automation/outreach
                                       ↓
                              Outreach + Interviews (SoR)
                                       ↓
                         automation/interview-prep
                                       ↓
                              StatusHistory + Metrics (SoR)
                                       ↓
                              dashboards/ (visualization)
```

All errors are logged to **FlowErrors**. All structural changes are tracked in **ChangeLog**.

---

## Canonical Principles

1. **Schema Consistency** — All sheet references use canonical names only.
2. **Documentation Alignment** — All markdown references canonical sheets.
3. **Automation Normalization** — Scripts log errors to `FlowErrors`, changes to `ChangeLog`.
4. **Prompt & Flow Alignment** — Copilot flows reference canonical sheets only.
5. **Test Validation** — Tests validate against canonical schema; no deprecated fixtures.

---

## References

- [SCHEMA.md](SCHEMA.md) — Full field definitions
- [REPO_NORMALIZATION.md](../../REPO_NORMALIZATION.md) — Normalization audit and compliance
- [excel-templates/system-of-record-schema.md](../../excel-templates/system-of-record-schema.md) — Excel schema
- [config/schema.json](../../config/schema.json) — Machine-readable schema
