# automation/sync

SoR synchronization modules for keeping automation outputs in sync with the canonical System of Record.

## Purpose

The `sync/` module provides utilities for:

- Reading canonical sheet data from the Excel SoR
- Writing enriched records back to canonical sheets
- Detecting and resolving conflicts between local state and the SoR
- Emitting `ChangeLog` entries for every write operation

## Modules

| File | Purpose |
|------|---------|
| `sor_sync.py` | Read/write helpers for canonical SoR sheets |

## Usage

```python
from automation.sync.sor_sync import read_sheet, write_rows

roles = read_sheet("Roles", sor_path="excel-templates/system-of-record-template.xlsx")
write_rows("Outreach", rows=[...], sor_path="excel-templates/system-of-record-template.xlsx")
```

All write operations automatically generate a `ChangeLog` entry via `automation.core.sor`.
