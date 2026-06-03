# Step 9 — Excel Export Engine (openpyxl) & Tests

## Context
You are continuing development of the Micro-SaaS security guard shift constraint management system. **Steps 0-8 (full backend + bot + both frontends) are complete. All previous tests pass.**

**Important:** All user-facing text (column headers, cell content, labels) is in **Hebrew only**, sourced from `messages.py`. Code comments in English.

## Objective
Implement the full `ExportService.generate_excel()` method using openpyxl, producing a professionally formatted Excel report with a matrix layout (guards × days × shifts), RTL support, styling, and frozen panes. Write comprehensive tests.

## Implementation: `app/services/export_service.py`

### Full `ExportService` Implementation

Replace the placeholder from Step 4 with the complete implementation.

Constructor receives: `SubmissionRepository`, `UserRepository`, `ScheduleWeekRepository`, `EventService`, `SystemSettingsRepository` via DI.

### `generate_excel(week_id: UUID) -> bytes`

**Step-by-step logic:**

1. **Fetch data:**
   - Get week by ID (start_date, end_date)
   - Get all active users
   - Get all submissions for the week (eager loaded with daily_statuses → shift_windows)
   - Build a lookup: `{user_id: submission}`

2. **Create workbook:**
   ```python
   wb = Workbook()
   ws = wb.active
   ws.title = "Shift Report"  # Internal name, not user-facing
   ws.sheet_view.rightToLeft = True  # RTL for Hebrew
   ```

3. **Row 1 — Report title (merged):**
   - Merge across all columns
   - Content: `Messages.EXCEL_REPORT_TITLE.format(start=start_date, end=end_date)`
   - Style: bold, size 14, center aligned

4. **Row 2 — Column headers:**
   Layout:
   ```
   | שם | טלפון | [יום ראשון 07/01] | | | [יום שני 08/01] | | | ... | הערות | סף מינימום | חריגה |
   ```
   
   Sub-headers per day (Row 3):
   ```
   |     |        | בוקר | צהריים | לילה | בוקר | צהריים | לילה | ... |       |            |       |
   ```
   
   - Column A: `Messages.EXCEL_HEADER_NAME`
   - Column B: `Messages.EXCEL_HEADER_PHONE`
   - For each day (Sunday→Saturday = 7 days): 3 sub-columns (morning, afternoon, night)
     - Day header: merged across 3 columns, shows Hebrew day name + date
     - Sub-headers: `Messages.LABEL_MORNING`, `Messages.LABEL_AFTERNOON`, `Messages.LABEL_NIGHT`
   - Second-to-last column: `Messages.EXCEL_HEADER_NOTES`
   - Third-to-last column: `Messages.EXCEL_HEADER_THRESHOLDS`
   - Last column: `Messages.EXCEL_HEADER_DEVIATION`

5. **Data rows (Row 4+) — One row per guard:**
   - Column A: `user.full_name`
   - Column B: `user.phone_number`
   - For each day × shift:
     - If user has submission for this day+shift: `"HH:MM-HH:MM"` (start_time-end_time)
     - If day is available but shift not selected: empty cell
     - If day is unavailable: `Messages.LABEL_UNAVAILABLE`
     - If day is blocked (event): `Messages.LABEL_BLOCKED`
     - If no submission at all: empty cell
   - Notes column: `submission.general_notes` or empty
   - Thresholds column: `"כללי: {total}, לילה: {night}, ערב: {evening}"` (from user settings)
   - Deviation column: `"⚠ חריגה"` if `has_deviation=True`, else `"✓"`

6. **Styling:**
   ```python
   # Header row (row 2): dark blue background, white bold text
   header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
   header_font = Font(color="FFFFFF", bold=True, size=11)
   
   # Day name headers: light blue background
   day_fill = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
   day_font = Font(bold=True, size=10)
   
   # Deviation cells: light red background, red text
   deviation_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
   deviation_font = Font(color="9C0006", bold=True)
   
   # Blocked cells: gray background, italic
   blocked_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
   blocked_font = Font(italic=True, color="666666")
   
   # Unavailable cells: light gray
   unavailable_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
   
   # All cells: thin borders
   thin_border = Border(
       left=Side(style='thin'),
       right=Side(style='thin'),
       top=Side(style='thin'),
       bottom=Side(style='thin')
   )
   ```

7. **Layout features:**
   - **Freeze panes:** `ws.freeze_panes = "C4"` — freeze first 2 columns + header rows
   - **Merged cells:** Day name headers span 3 columns each
   - **Column widths:** Auto-approximate based on content:
     - Name column: ~20
     - Phone column: ~15
     - Shift columns: ~12 each
     - Notes: ~25
     - Thresholds: ~20
     - Deviation: ~12
   - **Alignment:** Center for shift cells, right-to-left for text cells

8. **Return bytes:**
   ```python
   buffer = io.BytesIO()
   wb.save(buffer)
   buffer.seek(0)
   return buffer.getvalue()
   ```

### `get_filename(week: ScheduleWeek) -> str`
Returns: `shifts_report_{start_date}_{end_date}.xlsx`
Example: `shifts_report_2024-01-07_2024-01-13.xlsx`

### Update `admin_export_controller.py`
```python
@router.get("/{week_id}/excel")
async def export_excel(week_id: UUID, ...):
    excel_bytes = await export_service.generate_excel(week_id)
    filename = export_service.get_filename(week)
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

## Tests Required (`tests/test_export.py`)

### Setup
Create test fixtures:
- A week with known dates
- 3 users with different profiles (one with deviation, one fully absent, one normal)
- Submissions with various states
- Blockout events

### Tests

1. `test_generate_excel_returns_bytes` — Function returns non-empty `bytes` object
2. `test_excel_opens_as_workbook` — `openpyxl.load_workbook(BytesIO(result))` succeeds
3. `test_excel_has_correct_headers` — Row 2 contains expected header values (Name, Phone, day names)
4. `test_excel_has_correct_row_count` — Number of data rows == number of active users + header rows
5. `test_excel_cell_content_available` — Cell for available shift shows `"HH:MM-HH:MM"` format
6. `test_excel_cell_content_unavailable` — Cell for unavailable day shows `Messages.LABEL_UNAVAILABLE`
7. `test_excel_cell_content_blocked` — Cell for blocked day shows `Messages.LABEL_BLOCKED`
8. `test_excel_deviation_marking` — User with `has_deviation=True` has deviation column marked `"⚠ חריגה"`
9. `test_excel_no_deviation_marking` — User without deviation shows `"✓"`
10. `test_excel_rtl_enabled` — `ws.sheet_view.rightToLeft == True`
11. `test_excel_freeze_panes` — `ws.freeze_panes == "C4"`
12. `test_excel_empty_week` — Week with no submissions → workbook with headers only, no data rows (no crash)
13. `test_excel_filename_format` — Filename matches `shifts_report_YYYY-MM-DD_YYYY-MM-DD.xlsx` pattern
14. `test_excel_merged_day_headers` — Day headers span 3 columns (check merged_cells)

## Rules
- All text content (headers, labels, cell values) from `messages.py` — zero hard coding
- Error handling: if no submissions exist, return a valid Excel with headers only
- Logging: log start/end of generation, number of users/rows
- Full type hints
- All tests must pass with `pytest`
- Code comments in English
