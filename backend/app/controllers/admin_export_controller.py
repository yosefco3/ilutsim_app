"""
AdminExportController — admin endpoints for Excel export.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.dependencies import get_excel_export_service, require_admin_role
from app.services.excel_export_service import ExcelExportService

logger = logging.getLogger("ilutzim")

router = APIRouter(
    prefix="/admin/export",
    tags=["Admin – Export"],
    dependencies=[Depends(require_admin_role)],
)


@router.get("/week/{week_id}")
async def export_week_excel(
    week_id: uuid.UUID,
    export_service: ExcelExportService = Depends(get_excel_export_service),
):
    """
    Export a week's schedule as an Excel (.xlsx) file.

    Returns a streaming response with the Excel file.
    """
    try:
        buffer = await export_service.export_week_schedule(week_id)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=schedule_{week_id}.xlsx"
            },
        )
    except Exception as e:
        logger.error(f"Excel export failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )