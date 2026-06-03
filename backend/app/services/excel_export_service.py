"""
ExcelExportService — generates Excel files from schedule data.
"""

import io
import logging
import uuid
from datetime import date

from app.repositories.submission_repository import SubmissionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.schedule_week_repository import ScheduleWeekRepository

logger = logging.getLogger("ilutzim")

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


class ExcelExportService:
    """Generates Excel schedule reports for download."""

    def __init__(
        self,
        submission_repo: SubmissionRepository,
        user_repo: UserRepository,
        week_repo: ScheduleWeekRepository,
    ) -> None:
        self._submission_repo = submission_repo
        self._user_repo = user_repo
        self._week_repo = week_repo

    async def export_weekly_schedule(self, week_id: uuid.UUID) -> bytes:
        """
        Generate an Excel file with the weekly schedule data.
        Returns the raw bytes of the .xlsx file.
        """
        if not HAS_OPENPYXL:
            raise RuntimeError("openpyxl is required for Excel export")

        # Fetch data
        week = await self._week_repo.get_by_id(week_id)
        if week is None:
            raise ValueError(f"Week {week_id} not found")

        submissions = await self._submission_repo.get_by_week(week_id)
        active_users = await self._user_repo.get_active_users()

        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Schedule"

        # Styles
        header_font = Font(bold=True, size=12)
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font_white = Font(bold=True, size=11, color="FFFFFF")
        thin_border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin"),
        )

        # Title row
        ws.merge_cells("A1:D1")
        title_cell = ws["A1"]
        title_cell.value = f"Weekly Schedule: {week.week_start} to {week.week_end}"
        title_cell.font = header_font
        title_cell.alignment = Alignment(horizontal="center")

        # Headers
        headers = ["Guard Name", "Phone", "Constraints", "Status"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col, value=header)
            cell.font = header_font_white
            cell.fill = header_fill
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center")

        # Build user lookup
        user_map = {u.id: u for u in active_users}

        # Data rows
        row_num = 4
        for sub in submissions:
            user = user_map.get(sub.user_id)
            name = user.full_name if user else "Unknown"
            phone = user.phone_number if user else ""

            import json
            try:
                constraints = json.loads(sub.constraints) if isinstance(sub.constraints, str) else sub.constraints
                constraints_str = str(constraints)
            except (json.JSONDecodeError, TypeError):
                constraints_str = str(sub.constraints)

            row_data = [name, phone, constraints_str, sub.status.value]
            for col, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_num, column=col, value=value)
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="center")
            row_num += 1

        # Auto-width columns
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].width = 20

        # Save to bytes
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        logger.info(f"Excel exported for week {week_id}: {row_num - 4} rows")
        return buffer.read()