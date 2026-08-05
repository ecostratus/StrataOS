Attribute VB_Name = "ProtectAuditSheetsAppendBuffer"
Option Explicit

' StrataOS VBA macro
' Protect audit sheets while leaving an append-only unlocked buffer for connector writes.
' Sheets: StatusHistory, FlowErrors, ChangeLog

Public Sub ProtectAuditSheetsWithAppendBuffer()
    Dim auditSheets As Variant
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim lastCol As Long
    Dim startRow As Long
    Dim endRow As Long
    Dim appendBufferRows As Long
    Dim pw As String

    auditSheets = Array("StatusHistory", "FlowErrors", "ChangeLog")
    appendBufferRows = 500
    pw = ""  ' Optional password

    Application.ScreenUpdating = False
    Application.EnableEvents = False

    On Error GoTo CleanFail

    Dim i As Long
    For i = LBound(auditSheets) To UBound(auditSheets)
        Set ws = ThisWorkbook.Worksheets(CStr(auditSheets(i)))

        If ws.ProtectContents Then
            ws.Unprotect Password:=pw
        End If

        ' Lock entire sheet first.
        ws.Cells.Locked = True

        ' Identify used boundaries.
        lastRow = LastUsedRow(ws)
        lastCol = LastUsedCol(ws)

        If lastRow < 1 Then lastRow = 1
        If lastCol < 1 Then lastCol = 1

        startRow = WorksheetFunction.Max(2, lastRow + 1)
        endRow = WorksheetFunction.Min(1048576, startRow + appendBufferRows - 1)

        ' Unlock append buffer across active schema columns.
        ws.Range(ws.Cells(startRow, 1), ws.Cells(endRow, lastCol)).Locked = False

        ' Also unlock current table body rows if table exists and is named as sheet.
        On Error Resume Next
        Dim lo As ListObject
        Set lo = ws.ListObjects(ws.Name)
        On Error GoTo CleanFail

        If Not lo Is Nothing Then
            If Not lo.DataBodyRange Is Nothing Then
                lo.DataBodyRange.Locked = False
            End If
        End If

        ' Reprotect with targeted allowances.
        ws.Protect Password:=pw, DrawingObjects:=True, Contents:=True, Scenarios:=True, _
                   AllowFiltering:=True, AllowSorting:=True, AllowInsertingRows:=True
    Next i

CleanExit:
    Application.EnableEvents = True
    Application.ScreenUpdating = True
    Exit Sub

CleanFail:
    MsgBox "Protection macro failed: " & Err.Description, vbExclamation
    Resume CleanExit
End Sub

Private Function LastUsedRow(ByVal ws As Worksheet) As Long
    On Error Resume Next
    LastUsedRow = ws.Cells.Find(What:="*", After:=ws.Range("A1"), LookAt:=xlPart, _
                                LookIn:=xlFormulas, SearchOrder:=xlByRows, _
                                SearchDirection:=xlPrevious, MatchCase:=False).Row
    If Err.Number <> 0 Then
        LastUsedRow = 1
        Err.Clear
    End If
    On Error GoTo 0
End Function

Private Function LastUsedCol(ByVal ws As Worksheet) As Long
    On Error Resume Next
    LastUsedCol = ws.Cells.Find(What:="*", After:=ws.Range("A1"), LookAt:=xlPart, _
                                LookIn:=xlFormulas, SearchOrder:=xlByColumns, _
                                SearchDirection:=xlPrevious, MatchCase:=False).Column
    If Err.Number <> 0 Then
        LastUsedCol = 1
        Err.Clear
    End If
    On Error GoTo 0
End Function
