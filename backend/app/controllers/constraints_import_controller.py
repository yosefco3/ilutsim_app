"""ConstraintsImportController — upload guard-constraints xlsx and import it.

Step 03 exposes a dry-run **preview** (parse + union-merge, no DB write).
Step 04 adds the **commit** that writes into the existing availability model.

All routes require admin auth and live under ``/admin/import/constraints``.
"""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.dependencies import get_user_service, require_admin_role
from app.schemas.constraints_import import ConstraintsPreviewResponse
from app.services.constraints_import.parser import parse_constraints_xlsx
from app.services.constraints_import.preview import build_preview
from app.services.user_service import UserService

logger = logging.getLogger("ilutzim")

router = APIRouter(
    prefix="/admin/import/constraints",
    tags=["Admin – Constraints Import"],
    dependencies=[Depends(require_admin_role)],
)

_XLSX_SUFFIX = ".xlsx"


async def _read_xlsx(file: UploadFile) -> bytes:
    """Validate and read an uploaded xlsx, raising a friendly 400 on bad input."""
    name = file.filename or ""
    if not name.lower().endswith(_XLSX_SUFFIX):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="יש להעלות קובץ אקסל בפורמט .xlsx",
        )
    data = await file.read()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="הקובץ ריק",
        )
    return data


async def _existing_names(user_service: UserService) -> set[str]:
    users = await user_service.get_all_users()
    return {u.full_name for u in users if getattr(u, "full_name", None)}


@router.post("/preview", response_model=ConstraintsPreviewResponse)
async def preview_constraints(
    file: UploadFile = File(...),
    user_service: UserService = Depends(get_user_service),
):
    """Parse an uploaded constraints xlsx and return a clean preview (no write)."""
    data = await _read_xlsx(file)
    try:
        parsed = parse_constraints_xlsx(data)
    except Exception as exc:  # malformed workbook → 400, never 500
        logger.warning("constraints preview parse failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="לא ניתן לקרוא את קובץ האקסל — ודא שהוא תקין ובפורמט הצפוי",
        )

    existing = await _existing_names(user_service)
    return build_preview(parsed, existing)
