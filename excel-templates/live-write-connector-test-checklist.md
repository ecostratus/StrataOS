# Live Write Connector Test Checklist

Purpose: Validate runtime behavior for protected audit sheets, append-only write flows, and DateTime correctness.

Scope:
- Workbook: excel-templates/system-of-record-template.xlsx
- Sheets under test: StatusHistory, FlowErrors, ChangeLog
- Connector paths: Power Automate Excel connector and/or Copilot Studio Excel write action

## 1) Preconditions

- Use a dedicated test copy of the workbook.
- Ensure table names exactly match sheet names.
- Ensure protection strategy has been applied (append-buffer approach).
- Capture current row counts for the three audit sheets.
- Record timestamp of test start (UTC and local).

## 2) Test Matrix

Run each operation once per audit sheet:

1. Append row through connector action that targets the table.
2. Append row through connector action that targets a range (if used in production).
3. Update existing row (if production flow ever edits historical rows; expected result may be blocked).
4. Manual edit attempt in locked region (should fail).
5. Manual edit attempt in unlocked append buffer (should succeed only if this is allowed by your governance policy).

## 3) Payloads

### StatusHistory row payload
- HistoryID: HIST-TEST-0001
- EntityType: Role
- EntityID: ROLE-TEST-0001
- OldStatus: Applied
- NewStatus: Interviewing
- ChangedBy: connector-test
- ChangedAt: 2026-08-04T12:34:56Z

### FlowErrors row payload
- ErrorID: ERR-TEST-0001
- FlowName: connector-test
- Timestamp: 2026-08-04T12:35:56Z
- ErrorMessage: synthetic test error
- Payload: {"test":true}
- Resolved: No

### ChangeLog row payload
- ChangeID: CHG-TEST-0001
- SheetName: Roles
- FieldName: Status
- OldValue: Applied
- NewValue: Interviewing
- ChangedBy: connector-test
- ChangedAt: 2026-08-04T12:36:56Z

## 4) Pass/Fail Assertions

### A. Protection and append behavior
- PASS if connector append succeeds on all three sheets.
- PASS if manual edits to locked cells are rejected.
- PASS if row appends land in expected table region.
- FAIL if connector writes are blocked by protection in production write mode.

### B. DateTime storage correctness
For each DateTime column (ChangedAt, Timestamp):

1. In a helper cell, evaluate ISNUMBER(targetCell).
2. In a helper cell, evaluate TEXT(targetCell,"yyyy-mm-dd hh:mm:ss").
3. Sort ascending by DateTime and verify chronological order.

Expected:
- ISNUMBER = TRUE for connector-written DateTime cells.
- Display format matches workbook format (yyyy-mm-dd hh:mm).
- Sorting behaves as true date/time ordering.

FAIL indicators:
- ISNUMBER = FALSE (connector wrote text string).
- Lexicographic-looking sort anomalies.
- Mixed serial/text values in same DateTime column.

### C. Validation behavior
- Invalid ID prefix should be rejected by validation (or logged by flow and not committed).
- Duplicate ID insertion should fail validation (COUNTIF uniqueness rule).
- FK helper columns should evaluate to OK for valid references.

## 5) Evidence to Capture

- Screenshot or export of flow run results.
- Before/after row counts per sheet.
- Sample cell values and formulas for DateTime checks.
- Any connector error messages and action metadata.
- Final verdict per sheet: PASS/FAIL with reason.

## 6) Remediation Rules

If DateTime arrives as text:
- Convert in flow before write (preferred), or
- Write serial-compatible value and preserve workbook number format, or
- Add a normalization step in ingestion to coerce ISO strings to serial date values.

If append fails under protection:
- Increase unlocked append buffer rows, or
- Ensure flow writes to table append action, not arbitrary locked range, or
- Adjust protection allowances and retest.

## 7) Release Gate

Do not promote workbook changes to production until:
- All three audit sheets pass append and protection checks.
- DateTime values are confirmed numeric serials in at least 3 sampled rows per sheet.
- Evidence package is attached to the release notes / change record.
