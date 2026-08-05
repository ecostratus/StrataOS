/*
  StrataOS Office Script
  Protect audit sheets while leaving an append-only unlocked buffer for connector writes.

  Sheets targeted: StatusHistory, FlowErrors, ChangeLog
  Buffer strategy: unlock N rows below current used range; lock everything else.

  Recommended usage:
  1) Run this script after workbook structural changes.
  2) Re-run periodically or after major data growth to move the unlocked append buffer.
*/

function main(workbook: ExcelScript.Workbook) {
  const auditSheets = ["StatusHistory", "FlowErrors", "ChangeLog"];
  const appendBufferRows = 500;
  const protectPassword = ""; // Optional: set a password if your automation can still write with protection enabled.

  for (const sheetName of auditSheets) {
    const ws = workbook.getWorksheet(sheetName);
    if (!ws) {
      console.log(`Sheet not found: ${sheetName}`);
      continue;
    }

    // Unprotect first so lock/unlock changes can be applied.
    const protection = ws.getProtection();
    if (protection.getProtected()) {
      protection.unprotect(protectPassword);
    }

    // Lock the full sheet.
    ws.getRange().getFormat().getProtection().setLocked(true);

    // Determine used range. Keep at least row 2 as data start.
    const used = ws.getUsedRange(true);
    let lastUsedRow = 1;
    let lastUsedCol = 1;

    if (used) {
      const rowIndexZeroBased = used.getRowIndex();
      const rowCount = used.getRowCount();
      const colIndexZeroBased = used.getColumnIndex();
      const colCount = used.getColumnCount();
      lastUsedRow = rowIndexZeroBased + rowCount; // 1-based equivalent
      lastUsedCol = colIndexZeroBased + colCount;
    }

    // Keep append range within sheet max rows.
    const startRow = Math.max(2, lastUsedRow + 1);
    const endRow = Math.min(1048576, startRow + appendBufferRows - 1);

    // Unlock only the append buffer across used columns.
    const unlockRange = ws.getRangeByIndexes(
      startRow - 1,
      0,
      endRow - startRow + 1,
      Math.max(lastUsedCol, ws.getRange("A1").getColumnCount())
    );
    unlockRange.getFormat().getProtection().setLocked(false);

    // Optional: unlock the table's data body range too, if present, for row-add flows.
    const table = ws.getTables().find(t => t.getName() === sheetName);
    if (table) {
      const body = table.getRangeBetweenHeaderAndTotal();
      if (body) {
        body.getFormat().getProtection().setLocked(false);
      }
    }

    // Re-protect with filter/sort allowed.
    protection.protect({
      allowAutoFilter: true,
      allowSort: true,
      allowFormatCells: false,
      allowInsertRows: true,
      allowDeleteRows: false,
      selectionMode: ExcelScript.ProtectionSelectionMode.normal
    }, protectPassword);

    console.log(`Protected ${sheetName}; unlocked append rows ${startRow}-${endRow}.`);
  }
}
