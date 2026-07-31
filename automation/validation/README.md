# automation/validation

Schema validators that enforce canonical SoR compliance across automation outputs.

## Purpose

The `validation/` module ensures that records produced by automation scripts conform to the canonical 10-sheet System of Record schema before they are written to the SoR.

## Modules

| File | Purpose |
|------|---------|
| `schema_validator.py` | Validates record dicts against `config/schema.json` and `config/validation-rules.json` |

## CLI Usage

```bash
python3 automation/validation/schema_validator.py --sheet Roles --data output/roles.json
```

## Programmatic Usage

```python
from automation.validation.schema_validator import SchemaValidator

validator = SchemaValidator()
errors = validator.validate_record("Roles", {"RoleID": "R001", "Title": "Staff Engineer", "LastUpdated": "2026-01-07"})
if errors:
    for err in errors:
        print(err)
```
