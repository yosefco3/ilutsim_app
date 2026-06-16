# 03 · API פרופילים — controller + schemas

**תלוי ב:** פרומפט 02 (service).

**מטרה:** לחשוף את שירות הפרופילים כ-REST תחת הגבול `/admin/builder/*`, מאחורי `require_admin_role`.

## Schemas — `app/schedule_builder/schemas/profile_schemas.py`

- `ProfileCreate`: `name: str` (חובה, לא ריק), `kind: str | None`, `description: str | None`.
- `ProfileUpdate` (PATCH/rename): `name: str | None`, `kind: str | None`, `description: str | None`
  (כל השדות אופציונליים; לפחות אחד נדרש).
- `ProfileDuplicate`: `new_name: str | None`.
- `ProfileResponse` (`from_attributes=True`): `id`, `name`, `kind`, `description`, `is_default`,
  `display_order`, `created_at`. (כשעמדות ייכנסו במשימה 03 נוסיף `position_count` — לא עכשיו.)

## Controller — `app/schedule_builder/controllers/profile_controller.py`

```python
router = APIRouter(
    prefix="/admin/builder/profiles",
    tags=["Admin – Builder – Profiles"],
    dependencies=[Depends(require_admin_role)],
)
```

endpoints (תבנית try/except + HTTPException כמו `admin_weeks_controller.py`):
- `GET  ""`                  → list (200) — `list[ProfileResponse]`.
- `POST ""`                  → create (201) — `ProfileResponse`.
- `GET  "/{profile_id}"`     → get (200 / 404).
- `PATCH "/{profile_id}"`    → rename/update (200 / 404).
- `POST "/{profile_id}/duplicate"` → duplicate (201) — `ProfileResponse`.
- `DELETE "/{profile_id}"`   → delete (204). חסימת מחיקה אסורה → 400/409 עם הודעה בעברית.

ה-controller מזריק `get_profile_service` מ-`app/schedule_builder/dependencies.py`,
ומשתמש ב-`require_admin_role` מחלק א' (תלות ב'→א' מותרת).

## רישום ה-router
ב-`app/main.py` הוסף `app.include_router(profile_router)` **בקבוצה מסומנת** עם הערה:
```python
# ── Part B — Schedule Builder routers ──
app.include_router(profile_router)
```
כדי שהגבול בין החלקים יהיה ברור גם ברשימת ה-routers.

## טסטים
`backend/tests/test_profile_api.py` (httpx/AsyncClient + admin auth כמו טסטי admin קיימים):
- POST יוצר → 201 + שדות; GET list מחזיר אותו.
- PATCH משנה שם/סוג → 200.
- POST duplicate → 201, פרופיל חדש, `is_default=False`.
- DELETE עובד (204); מחיקת הפרופיל היחיד → 400/409.
- ללא טוקן אדמין → 401/403.

## קבצים צפויים
`app/schedule_builder/schemas/profile_schemas.py`,
`app/schedule_builder/controllers/profile_controller.py`,
`app/main.py` (include_router), `tests/test_profile_api.py`.

## קריטריון הצלחה
- `pytest tests/test_profile_api.py -q` ירוק; כל הסוויטה ירוקה.
- בדיקה ידנית מהירה (curl/Swagger): `GET /admin/builder/profiles` מחזיר את "שגרה" הזרוע.

## commit
`feat(builder): profiles REST API (/admin/builder/profiles)`
