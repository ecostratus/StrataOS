# Excel I/O Validation

## Overview

This document outlines validation procedures for Excel file I/O operations in the personal operating system.

**Schema Version**: Canonical 10-Sheet System of Record (SoR) v1.0

## Purpose

Ensure that:
1. Data is read correctly from Excel files
2. Data is written correctly to Excel files
3. Data integrity is maintained across the **10 canonical sheets**
4. No data corruption occurs
5. File format is preserved
6. Foreign key relationships are validated
7. Audit trails (StatusHistory, FlowErrors, ChangeLog) function correctly

## Canonical 10-Sheet Schema

The System of Record consists of exactly **10 sheets**:

1. **Roles** — Tracks all target roles under consideration
2. **Companies** — Tracks companies associated with roles, outreach, or consulting
3. **Contacts** — Tracks people associated with companies, outreach, or referrals
4. **Outreach** — Tracks all outbound messages and follow-ups
5. **Interviews** — Tracks interview stages and preparation
6. **Consulting** — Tracks consulting opportunities and engagements
7. **Metrics** — Stores computed KPIs and summary metrics
8. **StatusHistory** — Tracks every status change across all entities
9. **FlowErrors** — Captures automation and Copilot Studio flow errors
10. **ChangeLog** — Tracks structural changes to the SoR

## Tools Required

- Microsoft Excel (or compatible)
- Python with openpyxl library
- Test data files

## Validation Procedures

### 0. Schema Compliance Validation

#### Test: Verify 10 Canonical Sheets Exist
**Objective**: Ensure workbook contains exactly the 10 canonical sheets

**Steps**:
1. Open System of Record workbook
2. List all sheet names
3. Verify exactly 10 sheets exist
4. Verify sheet names match canonical schema

**Expected**: 
- Exactly 10 sheets
- Sheet names: `Roles`, `Companies`, `Contacts`, `Outreach`, `Interviews`, `Consulting`, `Metrics`, `StatusHistory`, `FlowErrors`, `ChangeLog`

**Python Example**:
```python
from openpyxl import load_workbook

wb = load_workbook('system-of-record.xlsx')
sheet_names = wb.sheetnames

expected_sheets = [
    'Roles', 'Companies', 'Contacts', 'Outreach', 
    'Interviews', 'Consulting', 'Metrics', 
    'StatusHistory', 'FlowErrors', 'ChangeLog'
]

assert len(sheet_names) == 10, f"Expected 10 sheets, found {len(sheet_names)}"
assert set(sheet_names) == set(expected_sheets), f"Sheet names mismatch"
```

#### Test: Verify Excel Table Names
**Objective**: Ensure each sheet has an Excel Table with matching name

**Steps**:
1. For each sheet, verify Excel Table exists
2. Verify Table name matches sheet name

**Expected**: Each sheet has a table named exactly after the sheet

**Python Example**:
```python
for sheet_name in expected_sheets:
    ws = wb[sheet_name]
    tables = ws.tables
    assert len(tables) == 1, f"Sheet {sheet_name} should have exactly 1 table"
    table_name = list(tables.keys())[0]
    assert table_name == sheet_name, f"Table name {table_name} should match sheet {sheet_name}"
```

#### Test: Verify Required Columns - Roles Sheet
**Objective**: Ensure Roles sheet has all required columns

**Required Columns**: `RoleID`, `Title`, `Seniority`, `Function`, `Source`, `FitScore`, `Status`, `CompanyID`, `LastUpdated`

**Steps**:
1. Open Roles sheet
2. Read header row
3. Verify all required columns present

**Expected**: All required columns exist

#### Test: Verify Required Columns - Companies Sheet
**Objective**: Ensure Companies sheet has all required columns

**Required Columns**: `CompanyID`, `Name`, `Industry`, `Location`, `Size`, `Website`, `Notes`

#### Test: Verify Required Columns - Contacts Sheet
**Required Columns**: `ContactID`, `Name`, `Role`, `CompanyID`, `Email`, `LinkedIn`, `RelationshipStrength`, `Notes`

#### Test: Verify Required Columns - Outreach Sheet
**Required Columns**: `OutreachID`, `ContactID`, `CompanyID`, `RoleID`, `Channel`, `MessageType`, `SentDate`, `ResponseDate`, `ResponseType`, `NextActionDate`, `Notes`

#### Test: Verify Required Columns - Interviews Sheet
**Required Columns**: `InterviewID`, `RoleID`, `CompanyID`, `Stage`, `ScheduledDate`, `CompletedDate`, `Outcome`, `Notes`

#### Test: Verify Required Columns - Consulting Sheet
**Required Columns**: `ConsultingID`, `CompanyID`, `Type`, `Status`, `ValueEstimate`, `NextActionDate`, `Notes`

#### Test: Verify Required Columns - Metrics Sheet
**Required Columns**: `MetricName`, `MetricValue`, `LastUpdated`

#### Test: Verify Required Columns - StatusHistory Sheet
**Required Columns**: `HistoryID`, `EntityType`, `EntityID`, `OldStatus`, `NewStatus`, `ChangedBy`, `ChangedAt`

#### Test: Verify Required Columns - FlowErrors Sheet
**Required Columns**: `ErrorID`, `FlowName`, `Timestamp`, `ErrorMessage`, `Payload`, `Resolved`

#### Test: Verify Required Columns - ChangeLog Sheet
**Required Columns**: `ChangeID`, `SheetName`, `FieldName`, `OldValue`, `NewValue`, `ChangedBy`, `ChangedAt`

### 1. Read Operations Validation

#### Test: Read Single Cell
**Objective**: Verify reading a single cell value

**Steps**:
1. Open test Excel file with known data from Roles sheet
2. Read specific cell (e.g., A2 for first RoleID)
3. Verify value matches expected

**Expected**: Exact match of cell value

**Python Example**:
```python
from openpyxl import load_workbook

wb = load_workbook('system-of-record.xlsx')
ws = wb['Roles']
value = ws['A2'].value  # First RoleID
assert value is not None, "RoleID should not be empty"
```

#### Test: Read Range
**Objective**: Verify reading a range of cells

**Steps**:
1. Open test Excel file
2. Read range (e.g., A1:C10)
3. Verify all values

**Expected**: All values match expected

#### Test: Read Entire Sheet
**Objective**: Verify reading entire sheet

**Steps**:
1. Open test Excel file
2. Read all rows and columns
3. Verify row count and column count
4. Spot check random cells

**Expected**: Correct dimensions and values

#### Test: Read Multiple Sheets
**Objective**: Verify reading from different canonical sheets

**Steps**:
1. Open workbook with all 10 canonical sheets
2. Read from Roles, Companies, Contacts sheets
3. Verify correct sheet accessed
4. Verify data structure matches schema

**Expected**: Data from correct sheets with proper structure

### 2. Write Operations Validation

#### Test: Write Single Cell
**Objective**: Verify writing to single cell

**Steps**:
1. Open Excel file
2. Write value to cell
3. Save file
4. Reopen and verify value

**Expected**: Written value persists

**Python Example**:
```python
from openpyxl import load_workbook

wb = load_workbook('test.xlsx')
ws = wb.active
ws['A1'] = 'New Value'
wb.save('test.xlsx')

# Verify
wb = load_workbook('test.xlsx')
assert wb.active['A1'].value == 'New Value'
```

#### Test: Write Range
**Objective**: Verify writing to range

**Steps**:
1. Open Excel file
2. Write values to range
3. Save file
4. Reopen and verify all values

**Expected**: All written values persist

#### Test: Append Row
**Objective**: Verify appending new row

**Steps**:
1. Open Excel file with N rows
2. Append new row
3. Save file
4. Reopen and verify N+1 rows
5. Verify new row content

**Expected**: New row added correctly

#### Test: Update Existing Row
**Objective**: Verify updating existing row

**Steps**:
1. Open Excel file
2. Update values in existing row
3. Save file
4. Reopen and verify changes
5. Verify other rows unchanged

**Expected**: Only target row updated

### 3. Data Type Validation

#### Test: String Values
**Objective**: Verify string handling

**Test Values**:
- Simple string: "Test"
- String with spaces: "Test String"
- String with special chars: "Test@#$%"
- Empty string: ""
- Long string: 1000+ characters

**Expected**: Strings preserved exactly

#### Test: FitScore Range Validation
**Objective**: Verify FitScore values are in valid range

**Test Values**: Numbers 0-100

**Steps**:
1. Read all FitScore values from Roles sheet
2. Verify all values are between 0 and 100
3. Flag any out-of-range values

**Expected**: All FitScores in valid range (0-100)

#### Test: Date Values
**Objective**: Verify date handling across sheets

**Test Values**:
- Date: 2024-01-15
- DateTime: 2024-01-15 14:30:00

**Sheets with Date Fields**:
- Roles: LastUpdated
- Outreach: SentDate, ResponseDate, NextActionDate
- Interviews: ScheduledDate, CompletedDate
- Consulting: NextActionDate
- Metrics: LastUpdated
- StatusHistory: ChangedAt
- FlowErrors: Timestamp
- ChangeLog: ChangedAt

**Expected**: Dates/times preserved correctly

**Note**: Be aware of Excel's date serial number format

#### Test: Boolean Values
**Objective**: Verify boolean handling

**Test Values**:
- True
- False

**Expected**: Booleans preserved

#### Test: Null/None Values
**Objective**: Verify null handling

**Test Values**:
- None/NULL
- Empty cell

**Expected**: Nulls handled without error

#### Test: Formula Values
**Objective**: Verify formula handling

**Test Values**:
- Simple formula: =A1+B1
- Complex formula: =SUM(A1:A10)

**Expected**: 
- Formula preserved (not calculated value)
- Or calculated value read if reading values only

### 4. Format Preservation Validation

#### Test: Cell Formatting
**Objective**: Verify cell format preserved

**Checks**:
- Font (name, size, color)
- Background color
- Borders
- Alignment
- Number format

**Expected**: Formatting unchanged after write

#### Test: Column Width
**Objective**: Verify column widths preserved

**Steps**:
1. Note column widths
2. Perform write operation
3. Verify widths unchanged

**Expected**: Widths preserved

#### Test: Row Height
**Objective**: Verify row heights preserved

**Steps**:
1. Note row heights
2. Perform write operation
3. Verify heights unchanged

**Expected**: Heights preserved

#### Test: Merged Cells
**Objective**: Verify merged cells handled

**Steps**:
1. Create file with merged cells
2. Read and write data
3. Verify merges preserved

**Expected**: Merges intact

### 5. Error Handling Validation

#### Test: File Not Found
**Objective**: Verify graceful handling

**Steps**:
1. Attempt to open non-existent file
2. Verify appropriate error raised

**Expected**: Clear error message, no crash

#### Test: Invalid Sheet Name
**Objective**: Verify error handling

**Steps**:
1. Try to access non-existent sheet
2. Verify appropriate error

**Expected**: Clear error message

#### Test: Read-Only File
**Objective**: Verify handling of locked file

**Steps**:
1. Open file as read-only
2. Attempt to write
3. Verify error or warning

**Expected**: Appropriate error

#### Test: Corrupted File
**Objective**: Verify handling of bad file

**Steps**:
1. Attempt to open corrupted Excel file
2. Verify error handling

**Expected**: Clear error, no crash

#### Test: Invalid Cell Reference
**Objective**: Verify error handling

**Steps**:
1. Try to access invalid cell (e.g., ZZZ99999)
2. Verify appropriate handling

**Expected**: Error or empty value

### 6. Performance Validation

#### Test: Large File Read
**Objective**: Verify performance with large files

**Steps**:
1. Create file with 10,000+ rows
2. Time read operation
3. Verify reasonable performance

**Expected**: Completes in < 10 seconds

#### Test: Large File Write
**Objective**: Verify write performance

**Steps**:
1. Write 10,000+ rows
2. Time operation
3. Verify performance

**Expected**: Completes in < 30 seconds

#### Test: Memory Usage
**Objective**: Verify no memory leaks

**Steps**:
1. Monitor memory before operation
2. Perform multiple read/write cycles
3. Monitor memory after
4. Verify memory released

**Expected**: Memory doesn't grow indefinitely

### 7. Foreign Key Validation

#### Test: Validate Roles.CompanyID FK
**Objective**: Verify foreign key references are valid

**Steps**:
1. Read all CompanyID values from Roles sheet
2. Read all CompanyID values from Companies sheet
3. Verify all Roles.CompanyID exist in Companies.CompanyID
4. Flag any orphaned references

**Expected**: All FK references are valid

**Python Example**:
```python
wb = load_workbook('system-of-record.xlsx')
roles_ws = wb['Roles']
companies_ws = wb['Companies']

# Get valid CompanyIDs
valid_company_ids = set()
for row in companies_ws.iter_rows(min_row=2, values_only=True):
    if row[0]:  # CompanyID is first column
        valid_company_ids.add(row[0])

# Check Roles.CompanyID references
for row in roles_ws.iter_rows(min_row=2, values_only=True):
    company_id = row[7]  # CompanyID is 8th column
    if company_id and company_id not in valid_company_ids:
        print(f"Invalid FK: RoleID {row[0]} references non-existent CompanyID {company_id}")
```

#### Test: Validate Contacts.CompanyID FK
**Objective**: Verify Contacts.CompanyID references exist in Companies

**Steps**: Similar to above, validate Contacts.CompanyID against Companies.CompanyID

#### Test: Validate Outreach Foreign Keys
**Objective**: Verify Outreach sheet FKs are valid

**Foreign Keys to Validate**:
- Outreach.ContactID → Contacts.ContactID
- Outreach.CompanyID → Companies.CompanyID
- Outreach.RoleID → Roles.RoleID

**Expected**: All FK references are valid

#### Test: Validate Interviews Foreign Keys
**Foreign Keys**:
- Interviews.RoleID → Roles.RoleID
- Interviews.CompanyID → Companies.CompanyID

#### Test: Validate Consulting.CompanyID FK
**Foreign Key**:
- Consulting.CompanyID → Companies.CompanyID

### 8. Audit Sheet Validation

#### Test: StatusHistory Logging
**Objective**: Verify StatusHistory captures status changes

**Steps**:
1. Record initial status of a Role
2. Change status (e.g., from "Identified" to "Applied")
3. Verify StatusHistory has new entry with:
   - EntityType = "Role"
   - EntityID = RoleID
   - OldStatus = "Identified"
   - NewStatus = "Applied"
   - ChangedAt timestamp

**Expected**: Status change logged correctly

#### Test: FlowErrors Logging
**Objective**: Verify FlowErrors captures automation errors

**Steps**:
1. Simulate flow error (or check existing errors)
2. Verify FlowErrors sheet has entry with:
   - ErrorID (unique)
   - FlowName
   - Timestamp
   - ErrorMessage
   - Resolved status

**Expected**: Errors logged with all required fields

#### Test: ChangeLog Logging
**Objective**: Verify ChangeLog captures schema changes

**Steps**:
1. Make a schema change (e.g., add validation rule)
2. Verify ChangeLog has entry with:
   - ChangeID (unique)
   - SheetName
   - FieldName
   - OldValue, NewValue
   - ChangedAt timestamp

**Expected**: Schema changes logged

### 9. Data Type Validation

#### Test: Multiple Readers
**Objective**: Verify multiple processes can read

**Steps**:
1. Open file in multiple processes
2. Read simultaneously
3. Verify all succeed

**Expected**: All reads successful

#### Test: Write Conflict
**Objective**: Verify write locking

**Steps**:
1. Open file for writing
2. Attempt to write from second process
3. Verify appropriate handling

**Expected**: Second write fails or waits

### 12. Integration Tests

#### Test: Role Discovery Integration
**Objective**: Verify role discovery automation can write to Roles sheet

**Steps**:
1. Run role discovery automation script
2. Verify new roles written to Roles sheet
3. Verify all required fields populated:
   - RoleID (unique)
   - Title
   - Status = "Identified"
   - FitScore (if calculated)
   - CompanyID (FK valid)
   - LastUpdated
4. Verify data types correct
5. Verify StatusHistory has entry for new role

**Expected**: Roles written correctly with valid data

#### Test: Status Change Integration
**Objective**: Verify status updates trigger StatusHistory logging

**Steps**:
1. Change a Role status from "Identified" to "Applied"
2. Verify Roles sheet updated
3. Verify StatusHistory sheet has new entry:
   - EntityType = "Role"
   - EntityID matches RoleID
   - OldStatus = "Identified"
   - NewStatus = "Applied"
   - ChangedAt has current timestamp
4. Verify foreign key integrity maintained

**Expected**: Status change logged in StatusHistory

#### Test: Outreach Tracking Integration
**Objective**: Verify outreach logging works

**Steps**:
1. Log test outreach message
2. Verify written to Outreach sheet
3. Verify all fields correct:
   - OutreachID (unique)
   - ContactID (FK valid)
   - CompanyID (FK valid)
   - RoleID (FK valid if applicable)
   - Channel (valid dropdown value)
   - MessageType (valid dropdown value)
   - SentDate
4. Verify foreign keys reference existing records

**Expected**: Outreach logged correctly with valid FKs

#### Test: Interview Scheduling Integration
**Objective**: Verify interview scheduling works

**Steps**:
1. Schedule test interview
2. Verify written to Interviews sheet
3. Verify all fields correct:
   - InterviewID (unique)
   - RoleID (FK valid)
   - CompanyID (FK valid)
   - Stage (valid dropdown value)
   - ScheduledDate
4. Verify FKs reference existing Roles and Companies

**Expected**: Interview scheduled with valid data

#### Test: Flow Error Logging Integration
**Objective**: Verify FlowErrors captures automation errors

**Steps**:
1. Trigger automation error (or simulate)
2. Verify error logged to FlowErrors sheet
3. Verify all required fields populated:
   - ErrorID (unique)
   - FlowName
   - Timestamp
   - ErrorMessage
   - Resolved = "No"
4. Verify error can be marked as resolved

**Expected**: Errors logged and resolvable

#### Test: Metrics Calculation Integration
**Objective**: Verify Metrics sheet populated by automation

**Steps**:
1. Populate source sheets with test data
2. Run metrics calculation automation
3. Verify Metrics sheet updated with:
   - Computed KPIs (e.g., TotalRolesIdentified)
   - Weekly activity counts
   - Conversion rates
4. Verify LastUpdated timestamp

**Expected**: Metrics calculated and stored correctly

#### Test: Dashboard Data Integration
**Objective**: Verify dashboard reads canonical sheets correctly

**Steps**:
1. Populate all 10 canonical sheets with test data
2. Open dashboard workbook
3. Verify dashboard pulls data from:
   - Roles sheet (for role funnel, FitScore distribution)
   - Companies sheet (for company analysis)
   - Outreach sheet (for outreach metrics)
   - Interviews sheet (for interview tracking)
   - Consulting sheet (for pipeline value)
   - Metrics sheet (for KPIs)
   - StatusHistory sheet (for trend analysis)
   - FlowErrors sheet (for system health)
4. Verify metrics calculated correctly
5. Verify charts display correctly
6. Verify no references to legacy sheets

**Expected**: Dashboard reflects canonical schema data accurately

## Validation Checklist

Use this checklist for comprehensive validation of the **Canonical 10-Sheet SoR**:

### Schema Compliance
- [ ] Exactly 10 sheets exist (no more, no fewer)
- [ ] Sheet names match canonical schema
- [ ] Each sheet has Excel Table with matching name
- [ ] All required columns present in each sheet
- [ ] No legacy sheets (Jobs, Applications, Weekly_Goals, Audit_Log, Dashboard)

### Read Operations
- [ ] Single cell read works
- [ ] Range read works
- [ ] Full sheet read works
- [ ] Multi-sheet read works (all 10 canonical sheets)
- [ ] Empty cells handled
- [ ] All data types read correctly

### Write Operations
- [ ] Single cell write works
- [ ] Range write works
- [ ] Append row works
- [ ] Update row works
- [ ] All data types write correctly
- [ ] Changes persist after save

### Data Integrity
- [ ] No data corruption
- [ ] All values match expected
- [ ] Data types preserved
- [ ] Formulas handled correctly
- [ ] Null values handled
- [ ] FitScore values in range (0-100)

### Foreign Key Validation
- [ ] Roles.CompanyID → Companies.CompanyID
- [ ] Contacts.CompanyID → Companies.CompanyID
- [ ] Outreach.ContactID → Contacts.ContactID
- [ ] Outreach.CompanyID → Companies.CompanyID
- [ ] Outreach.RoleID → Roles.RoleID
- [ ] Interviews.RoleID → Roles.RoleID
- [ ] Interviews.CompanyID → Companies.CompanyID
- [ ] Consulting.CompanyID → Companies.CompanyID

### Dropdown Validation
- [ ] Roles.Status dropdown works
- [ ] Contacts.RelationshipStrength dropdown works
- [ ] Outreach dropdowns (Channel, MessageType, ResponseType) work
- [ ] Interviews dropdowns (Stage, Outcome) work
- [ ] Consulting dropdowns (Type, Status) work
- [ ] StatusHistory.EntityType dropdown works
- [ ] FlowErrors.Resolved dropdown works

### Audit Sheet Functionality
- [ ] StatusHistory logs status changes
- [ ] FlowErrors logs automation errors
- [ ] ChangeLog logs schema changes
- [ ] Audit sheets populated automatically
- [ ] Audit data integrity maintained

### Format Preservation
- [ ] Cell formatting preserved
- [ ] Column widths preserved
- [ ] Row heights preserved
- [ ] Merged cells preserved
- [ ] Sheet structure intact
- [ ] Conditional formatting works

### Error Handling
- [ ] File not found handled
- [ ] Invalid sheet name handled
- [ ] Read-only file handled
- [ ] Corrupted file handled
- [ ] Invalid references handled
- [ ] Invalid FK references detected

### Performance
- [ ] Large files handled efficiently
- [ ] Memory usage reasonable
- [ ] No memory leaks
- [ ] Operations complete in reasonable time

### Integration
- [ ] Automation scripts can read/write
- [ ] Data flows between canonical sheets
- [ ] Foreign keys maintained
- [ ] Dashboard reads canonical sheets correctly
- [ ] No references to legacy sheets in automation
- [ ] Metrics sheet populated by automation
- [ ] StatusHistory populated on status changes
- [ ] FlowErrors populated on automation errors

## Automated Testing

### Pytest Example
```python
import pytest
from openpyxl import load_workbook, Workbook

class TestExcelIO:
    """Test Excel I/O operations for Canonical 10-Sheet SoR."""
    
    def test_canonical_sheets_exist(self, tmp_path):
        """Test that all 10 canonical sheets exist."""
        # Load the System of Record workbook
        wb = load_workbook('system-of-record.xlsx')
        sheet_names = wb.sheetnames
        
        expected_sheets = [
            'Roles', 'Companies', 'Contacts', 'Outreach',
            'Interviews', 'Consulting', 'Metrics',
            'StatusHistory', 'FlowErrors', 'ChangeLog'
        ]
        
        assert len(sheet_names) == 10, f"Expected 10 sheets, found {len(sheet_names)}"
        assert set(sheet_names) == set(expected_sheets), f"Sheet names mismatch"
    
    def test_roles_sheet_columns(self):
        """Test Roles sheet has required columns."""
        wb = load_workbook('system-of-record.xlsx')
        ws = wb['Roles']
        
        headers = [cell.value for cell in ws[1]]
        required_columns = [
            'RoleID', 'Title', 'Seniority', 'Function', 
            'Source', 'FitScore', 'Status', 'CompanyID', 'LastUpdated'
        ]
        
        for col in required_columns:
            assert col in headers, f"Missing required column: {col}"
    
    def test_companies_sheet_columns(self):
        """Test Companies sheet has required columns."""
        wb = load_workbook('system-of-record.xlsx')
        ws = wb['Companies']
        
        headers = [cell.value for cell in ws[1]]
        required_columns = [
            'CompanyID', 'Name', 'Industry', 'Location', 
            'Size', 'Website', 'Notes'
        ]
        
        for col in required_columns:
            assert col in headers, f"Missing required column: {col}"
    
    def test_foreign_key_validity_roles_company(self):
        """Test Roles.CompanyID references valid Companies.CompanyID."""
        wb = load_workbook('system-of-record.xlsx')
        roles_ws = wb['Roles']
        companies_ws = wb['Companies']
        
        # Get valid CompanyIDs
        valid_company_ids = set()
        for row in companies_ws.iter_rows(min_row=2, values_only=True):
            if row[0]:  # CompanyID is first column
                valid_company_ids.add(row[0])
        
        # Check Roles.CompanyID references
        invalid_fks = []
        for row in roles_ws.iter_rows(min_row=2, values_only=True):
            role_id = row[0]
            company_id = row[7]  # CompanyID is 8th column
            if company_id and company_id not in valid_company_ids:
                invalid_fks.append((role_id, company_id))
        
        assert len(invalid_fks) == 0, f"Invalid FK references: {invalid_fks}"
    
    def test_fitScore_range(self):
        """Test FitScore values are in valid range (0-100)."""
        wb = load_workbook('system-of-record.xlsx')
        ws = wb['Roles']
        
        invalid_scores = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            role_id = row[0]
            fit_score = row[5]  # FitScore is 6th column
            if fit_score is not None:
                if not (0 <= fit_score <= 100):
                    invalid_scores.append((role_id, fit_score))
        
        assert len(invalid_scores) == 0, f"Invalid FitScores: {invalid_scores}"
    
    def test_status_history_logging(self, tmp_path):
        """Test StatusHistory captures status changes."""
        # Create test file
        wb = Workbook()
        
        # Create Roles sheet
        roles_ws = wb.create_sheet('Roles')
        roles_ws.append(['RoleID', 'Status'])
        roles_ws.append(['ROLE001', 'Identified'])
        
        # Create StatusHistory sheet
        history_ws = wb.create_sheet('StatusHistory')
        history_ws.append(['HistoryID', 'EntityType', 'EntityID', 'OldStatus', 'NewStatus', 'ChangedBy', 'ChangedAt'])
        
        file_path = tmp_path / "test_status.xlsx"
        wb.save(file_path)
        
        # Simulate status change
        wb = load_workbook(file_path)
        roles_ws = wb['Roles']
        history_ws = wb['StatusHistory']
        
        # Change status
        roles_ws['B2'] = 'Applied'
        
        # Log to StatusHistory
        history_ws.append(['HIST001', 'Role', 'ROLE001', 'Identified', 'Applied', 'Automation', '2024-01-15 10:00:00'])
        
        wb.save(file_path)
        
        # Verify
        wb = load_workbook(file_path)
        history_ws = wb['StatusHistory']
        assert history_ws['B2'].value == 'Role'
        assert history_ws['C2'].value == 'ROLE001'
        assert history_ws['D2'].value == 'Identified'
        assert history_ws['E2'].value == 'Applied'
    
    def test_no_legacy_sheets(self):
        """Test that no legacy sheets exist in workbook."""
        wb = load_workbook('system-of-record.xlsx')
        sheet_names = wb.sheetnames
        
        legacy_sheets = ['Jobs', 'Applications', 'Weekly_Goals', 'Audit_Log', 'Dashboard']
        
        for legacy in legacy_sheets:
            assert legacy not in sheet_names, f"Legacy sheet '{legacy}' should not exist"
```

## Manual Validation Steps

1. **Create test workbook** with sample data
2. **Run automated tests** to verify basic operations
3. **Manually inspect** Excel file after operations
4. **Verify** no unexpected changes
5. **Test edge cases** not covered by automation
6. **Document** any issues found
7. **Retest** after fixes

## Common Issues and Solutions

### Issue: Dates Read as Numbers
**Cause**: Excel stores dates as serial numbers
**Solution**: Convert using `datetime.fromordinal()`

### Issue: Formulas Not Calculated
**Cause**: Reading formula string, not value
**Solution**: Use `data_only=True` when loading workbook

### Issue: Formatting Lost
**Cause**: Not using openpyxl's style features
**Solution**: Copy styles explicitly when needed

### Issue: Large Files Slow
**Cause**: Loading entire workbook into memory
**Solution**: Use `read_only=True` mode for reading

### Issue: File Locked Error
**Cause**: File open in Excel
**Solution**: Close file or use different filename

## Reporting Issues

When reporting Excel I/O issues, include:
1. **Exact error message** and stack trace
2. **Sample file** that reproduces issue (if possible)
3. **Code snippet** that triggers issue
4. **Expected behavior** vs actual behavior
5. **Environment**: Python version, openpyxl version, OS

## References

- openpyxl documentation: https://openpyxl.readthedocs.io/
- Excel file formats: https://docs.microsoft.com/en-us/office/
- Python Excel libraries comparison: https://www.python-excel.org/
