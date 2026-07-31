# automation/core

Core SoR integration utilities shared across all automation modules.

## Purpose

This module provides the foundational interface between Python automation and the canonical 10-sheet System of Record (SoR). It handles:

- Error logging to the `FlowErrors` sheet
- Change tracking via the `ChangeLog` sheet
- Canonical sheet name validation
- ID generation utilities

## Modules

| File | Purpose |
|------|---------|
| `sor.py` | `log_flow_error()` and `log_change()` helpers |
| `ids.py` | Deterministic ID generation for SoR records |

## Usage

```python
from automation.core.sor import log_flow_error, log_change

# Log an automation error
log_flow_error(
    flow_name="job_discovery_v1",
    error_message="Source timeout",
    payload={"source": "indeed"}
)

# Log a structural change
log_change(
    sheet_name="Roles",
    field_name="Status",
    old_value="Identified",
    new_value="Applied",
    changed_by="job_discovery_v1"
)
```
