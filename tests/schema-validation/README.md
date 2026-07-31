# tests/schema-validation

Tests that enforce canonical SoR schema compliance across the repository.

## Purpose

- Verifies all 10 canonical sheet names are defined in `config/schema.json`.
- Verifies no prohibited sheet names appear in any configuration or automation file.
- Validates `config/validation-rules.json` covers all canonical sheets.
- Tests the `SchemaValidator` class against known-good and known-bad records.

## Running

```bash
pytest tests/schema-validation/ -v
```
