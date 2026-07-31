# Testing Guide

**Version:** 1.0  
**Last Updated:** 2026-01-07

---

## Overview

The `tests/` directory contains all test suites for StrataOS. Tests validate automation logic, schema compliance, and end-to-end flow integration.

---

## Test Structure

```
tests/
├── README.md
├── schema-validation/          # Canonical schema compliance tests
│   ├── test_canonical_schema.py
│   └── README.md
├── integration/                # End-to-end flow tests
│   ├── test_enriched_flows.py
│   ├── test_multi_source_ingestion.py
│   └── test_multi_source_orchestrator.py
├── fixtures/                   # Test data using canonical sheet structures
│   ├── README.md
│   ├── indeed_payload.json
│   ├── linkedin_payload.json
│   └── v1/
├── sources/                    # Per-source adapter tests
├── enrichment/                 # Enrichment pipeline tests
├── common/                     # Shared utility tests
├── storage/                    # Storage layer tests
├── scheduling/                 # Scheduler tests
└── webapp/                     # Control center API tests
```

---

## Running Tests

### All Tests

```bash
pytest tests/ -v
```

### Schema Validation Only

```bash
pytest tests/schema-validation/ -v
```

### Integration Tests

```bash
pytest tests/integration/ -v
```

### With Coverage

```bash
pytest --cov=automation tests/
```

### Short Tracebacks (CI Mode)

```bash
pytest tests/ -q --tb=short
```

---

## Schema Validation Tests

The `tests/schema-validation/` suite enforces canonical compliance:

- Verifies all 10 canonical sheet names are defined in `config/schema.json`.
- Verifies no prohibited sheet names (`Jobs`, `Applications`, `Weekly_Goals`, `Audit_Log`, `Dashboard`) appear in any configuration or automation file.
- Validates that `config/validation-rules.json` covers all canonical sheets.

```bash
pytest tests/schema-validation/test_canonical_schema.py -v
```

---

## Writing Tests

### Canonical Fixtures

Test fixtures must use canonical sheet names only. Example fixture path:

```
tests/fixtures/v1/high-fit-low-upside/opportunity.json
```

Do **not** create fixtures referencing prohibited sheet names.

### Test File Naming

| Scope | Convention |
|-------|-----------|
| Unit tests | `test_<module>.py` or `<module>_tests.py` |
| Integration tests | `test_<flow>.py` in `tests/integration/` |
| Schema tests | `test_canonical_*.py` in `tests/schema-validation/` |

---

## Test Configuration

`pytest.ini` at the repository root configures test discovery. All test files matching `test_*.py` or `*_tests.py` are collected automatically.

---

## References

- [docs/ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- [docs/SCHEMA.md](SCHEMA.md) — Canonical data model
- [config/validation-rules.json](../config/validation-rules.json) — Validation rules
- [tests/README.md](../tests/README.md) — Test suite overview
