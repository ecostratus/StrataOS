# Excel I/O Validation

## Overview

This document outlines validation procedures for Excel file I/O operations in the personal operating system.

## Purpose

Ensure that:
1. Data is read correctly from Excel files
2. Data is written correctly to Excel files
3. Data integrity is maintained
4. No data corruption occurs
5. File format is preserved

## Tools Required

- Microsoft Excel (or compatible)
- Python with openpyxl library
- Test data files

## Validation Procedures

### 1. Read Operations Validation

#### Test: Read Single Cell
**Objective**: Verify reading a single cell value

**Steps**:
1. Open test Excel file with known data
2. Read specific cell (e.g., A1)
3. Verify value matches expected

**Expected**: Exact match of cell value

**Python Example**:
```python
from openpyxl import load_workbook

wb = load_workbook('test.xlsx')
ws = wb.active
value = ws['A1'].value
assert value == 'Expected Value'
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
**Objective**: Verify reading from different sheets

**Steps**:
1. Open workbook with multiple sheets
2. Read from each sheet
3. Verify correct sheet accessed

**Expected**: Data from correct sheets

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

#### Test: Numeric Values
**Objective**: Verify number handling

**Test Values**:
- Integer: 42
- Float: 3.14159
- Negative: -100
- Zero: 0
- Large number: 1000000000
- Scientific notation: 1.23e10

**Expected**: Numbers preserved with precision

#### Test: Date Values
**Objective**: Verify date handling

**Test Values**:
- Date: 2024-01-15
- DateTime: 2024-01-15 14:30:00
- Time: 14:30:00

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

### 7. Concurrent Access Validation

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

### 8. Integration Tests

#### Test: Job Discovery Integration
**Objective**: Verify job scraper can write to Excel

**Steps**:
1. Run job scraper script
2. Verify jobs written to Jobs sheet
3. Verify all required fields populated
4. Verify data types correct

**Expected**: Data written correctly

#### Test: Application Tracking Integration
**Objective**: Verify application logging works

**Steps**:
1. Log test application
2. Verify written to Applications sheet
3. Verify all fields correct
4. Verify foreign key (job_id) valid

**Expected**: Application logged correctly

#### Test: Dashboard Integration
**Objective**: Verify dashboard reads data correctly

**Steps**:
1. Populate source sheets with test data
2. Open dashboard
3. Verify metrics calculated correctly
4. Verify charts display correctly

**Expected**: Dashboard reflects data accurately

## Validation Checklist

Use this checklist for comprehensive validation:

### Read Operations
- [ ] Single cell read works
- [ ] Range read works
- [ ] Full sheet read works
- [ ] Multi-sheet read works
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

### Format Preservation
- [ ] Cell formatting preserved
- [ ] Column widths preserved
- [ ] Row heights preserved
- [ ] Merged cells preserved
- [ ] Sheet structure intact

### Error Handling
- [ ] File not found handled
- [ ] Invalid sheet handled
- [ ] Read-only file handled
- [ ] Corrupted file handled
- [ ] Invalid references handled

### Performance
- [ ] Large files handled efficiently
- [ ] Memory usage reasonable
- [ ] No memory leaks
- [ ] Operations complete in reasonable time

### Integration
- [ ] Scripts can read/write
- [ ] Data flows between sheets
- [ ] Foreign keys maintained
- [ ] Dashboard displays correctly

## Automated Testing

### Pytest Example
```python
import pytest
from openpyxl import load_workbook, Workbook

class TestExcelIO:
    """Test Excel I/O operations."""
    
    def test_read_cell(self, tmp_path):
        """Test reading single cell."""
        # Create test file
        wb = Workbook()
        ws = wb.active
        ws['A1'] = 'Test Value'
        file_path = tmp_path / "test.xlsx"
        wb.save(file_path)
        
        # Test read
        wb = load_workbook(file_path)
        assert wb.active['A1'].value == 'Test Value'
    
    def test_write_cell(self, tmp_path):
        """Test writing single cell."""
        # Create test file
        wb = Workbook()
        file_path = tmp_path / "test.xlsx"
        wb.save(file_path)
        
        # Test write
        wb = load_workbook(file_path)
        wb.active['A1'] = 'New Value'
        wb.save(file_path)
        
        # Verify
        wb = load_workbook(file_path)
        assert wb.active['A1'].value == 'New Value'
    
    def test_append_row(self, tmp_path):
        """Test appending row."""
        wb = Workbook()
        ws = wb.active
        ws.append(['Row', '1'])
        file_path = tmp_path / "test.xlsx"
        wb.save(file_path)
        
        # Append
        wb = load_workbook(file_path)
        ws = wb.active
        ws.append(['Row', '2'])
        wb.save(file_path)
        
        # Verify
        wb = load_workbook(file_path)
        assert wb.active.max_row == 2
        assert wb.active['A2'].value == 'Row'
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
