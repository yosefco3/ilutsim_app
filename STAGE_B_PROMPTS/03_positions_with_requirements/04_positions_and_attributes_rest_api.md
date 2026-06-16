# 03 · צעד 04 — REST API: עמדות + אוצר-מאפיינים

> שכבת ה-API מאחורי `require_admin_role`, רשומה ב-`main.py` בקבוצת "Part B".
> תבנית מלאה: `profile_controller.py` + `profile_schemas.py`.

## מטרה
endpoints ל-CRUD עמדות (תחת פרופיל) ול-CRUD אוצר-המאפיינים, כולל ולידציית קלט.

## החלטות עיצוב נעולות
- **נתיב עמדות מקונן בפרופיל:** `/admin/builder/profiles/{profile_id}/positions`
  (list/create) + `/admin/builder/positions/{position_id}` (get/patch/delete).
  זה תואם ל"מסך עמדות בתוך פרופיל נבחר".
- **נתיב מאפיינים:** `/admin/builder/attributes` (list/create/patch/delete).
- מיפוי `AppBaseException` → `HTTPException` (תבנית ה-controller הקיים).

## ולידציית schemas (קריטי — כאן נאכפת תקינות ה-JSON)
- **`day_schedules`**: מילון; מפתחות חייבים להיות `"0".."6"`; ערך `{start,end}` בפורמט
  `HH:MM` (regex `^([01]\d|2[0-3]):[0-5]\d$`); **לפחות יום אחד**. `end <= start` מותר
  (לילה חוצה חצות). השתמש ב-`model_validator`/`field_validator`.
- **`required_attributes`**: רשימת מחרוזות; ייחודיות; (אופציונלי, אם פשוט) אזהרה רכה אם מפתח
  לא קיים באוצר — **אבל אל תחסום** (היחס רך; אל תשבור על מפתח לא-מוכר).
- **`shift`**: enum `ShiftType` (`morning`/`afternoon`/`night`).
- `PositionUpdate`: כל השדות אופציונליים, ולידציית "לפחות שדה אחד".
- `AttributeCreate`: `key` (slug, regex `^[a-z][a-z0-9_]*$`), `label` חובה.
  `AttributeUpdate`: לפחות שדה אחד.

## קבצים
1. **`backend/app/schedule_builder/schemas/position_schemas.py`** (חדש) —
   `DaySchedule`, `PositionCreate`, `PositionUpdate`, `PositionResponse`
   (`model_config = from_attributes`; כולל `profile_id`, `day_schedules`, `required_attributes`).
2. **`backend/app/schedule_builder/schemas/attribute_schemas.py`** (חדש) —
   `AttributeCreate`, `AttributeUpdate`, `AttributeResponse`.
3. **`backend/app/schedule_builder/controllers/position_controller.py`** (חדש) — הנתיבים לעיל.
4. **`backend/app/schedule_builder/controllers/attribute_controller.py`** (חדש) — `/admin/builder/attributes`.
5. **`backend/app/main.py`** (עריכה) — `include_router` לשני ה-routers בקבוצת "Part B".

## טסטים (fake service, תבנית `test_profile_api.py`)
- `tests/test_position_api.py` — list/create/get/patch/delete; **422 על `day_schedules` לא תקין**
  (יום מחוץ ל-0-6 / שעה לא בפורמט / מילון ריק); 404 על עמדה לא קיימת.
- `tests/test_attribute_api.py` — CRUD; 422 על `key` לא חוקי; 409/שגיאה על כפל-מפתח.

## הרצה
`cd backend && .venv/bin/python -m pytest tests/ -q` — הכל ירוק.

## קומיט
```
feat(builder): positions + attributes REST API
```
push · עדכן `_PROGRESS.md` · מחק קובץ פרומפט זה.
