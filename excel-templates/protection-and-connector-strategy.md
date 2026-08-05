# Protection and Connector Strategy (Audit Sheets)

This document defines the append-buffer protection approach and where the implementation lives.

## Objective

Keep audit sheets tamper-resistant for manual edits while preserving reliable connector appends.

Target sheets:
- StatusHistory
- FlowErrors
- ChangeLog

## Approach

1. Lock entire sheet.
2. Unlock only:
   - Existing table data body range (optional, for row-add compatibility).
   - A bounded append buffer below current used rows (for connector appends).
3. Protect sheet with filtering/sorting allowed.
4. Re-run script periodically to roll the append buffer forward.

## Implementations

- Office Script: excel-templates/office-scripts/protect-audit-sheets-append-buffer.ts
- VBA Macro: excel-templates/vba/ProtectAuditSheetsAppendBuffer.bas

## Operational Notes

- If connector writes by table append action, protection is often compatible.
- If connector writes by range address, buffer sizing and unlocked range are critical.
- Re-test DateTime write semantics after any connector or flow change.

## Validation

Use the checklist:
- excel-templates/live-write-connector-test-checklist.md
