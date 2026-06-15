"""Build a clean, DB-free preview structure from a ``ParsedImport``.

Combines the parser (step 01) and the union-merge hours (step 02) into the
shape the preview/commit endpoints return. No DB access — the caller supplies
``existing_names`` (the set of guard names already in the system) purely so the
``exists`` flag can be set. ``exists`` is **informational** ("חדש"/"קיים");
it never filters or rejects — identity is the name, find-or-create.
"""

from __future__ import annotations

from app.constants import ShiftType
from app.schemas.constraints_import import (
    ConstraintsPreviewResponse,
    DayPreview,
    GuardPreview,
    ShiftCellsOut,
)

from .hours import day_hours, format_day, merge_day, weekly_hours
from .parser import Cell, CellKind, ParsedGuard, ParsedImport

# day_index 0..6 → Hebrew weekday name.
DAY_NAMES = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]

_AVAILABLE_TOKEN = "זמין"


def _cell_text(cell: Cell | None) -> str | None:
    """Render a single shift cell as display text (None = unavailable)."""
    if cell is None or cell.kind == CellKind.UNAVAILABLE:
        return None
    if cell.kind == CellKind.ALL_DAY:
        return _AVAILABLE_TOKEN
    if cell.kind == CellKind.WINDOW and cell.start and cell.end:
        return f"{cell.start:%H:%M}–{cell.end:%H:%M}"
    return None


def _guard_preview(guard: ParsedGuard, existing_names: set[str]) -> GuardPreview:
    days: list[DayPreview] = []
    for day_index in range(7):
        day_cells = guard.cells.get(day_index, {})
        segments = merge_day(day_cells)
        days.append(
            DayPreview(
                day_index=day_index,
                day_name=DAY_NAMES[day_index],
                segments=format_day(segments),
                hours=day_hours(segments),
                shifts=ShiftCellsOut(
                    morning=_cell_text(day_cells.get(ShiftType.MORNING)),
                    afternoon=_cell_text(day_cells.get(ShiftType.AFTERNOON)),
                    night=_cell_text(day_cells.get(ShiftType.NIGHT)),
                ),
            )
        )
    return GuardPreview(
        name=guard.name,
        exists=guard.name in existing_names,
        notes=guard.notes,
        weekly_hours=weekly_hours(guard.cells),
        days=days,
    )


def build_preview(
    parsed: ParsedImport,
    existing_names: set[str],
) -> ConstraintsPreviewResponse:
    """Turn a ``ParsedImport`` into the clean preview response."""
    return ConstraintsPreviewResponse(
        week_start=parsed.week_start,
        week_end=parsed.week_end,
        guards=[_guard_preview(g, existing_names) for g in parsed.guards],
        errors=list(parsed.errors),
    )
