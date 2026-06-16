# 03 · צעד 03 — `PositionRepository` + `PositionService` + deep-copy בשכפול

> שכבת הדאטה והלוגיקה לעמדות, **וחיבור הוו** שהושאר ב-02: מימוש `_copy_positions`
> כך ש"שכפול פרופיל" יעתיק גם את העמדות.

## מטרה
CRUD לעמדות (תחת פרופיל), מיון/הוספה-בסוף, deep-copy של עמדות בשכפול פרופיל.

## החלטות עיצוב נעולות
- **מסך העמדות הוא "בתוך פרופיל נבחר".** לכן ה-service עובד לפי `profile_id`:
  - `list_positions(profile_id)` — עמדות הפרופיל בלבד, ממוין לפי `display_order`.
  - `create_position(profile_id, ...)` — `display_order` = max-בתוך-הפרופיל + 1.
  - `update_position(position_id, ...)` — עדכון שדות שסופקו בלבד (תבנית `rename_profile`).
  - `delete_position(position_id)`.
  - **אין** מגבלת "עמדה אחרונה" (בניגוד לפרופילים — פרופיל יכול להיות ריק).
- `_copy_positions(src, dst)` (ב-`ProfileService`) — **deep-copy אמיתי**: לכל עמדה ב-`src`
  צור `Position` חדשה תחת `dst` עם אותם `name/shift/day_schedules/required_attributes/display_order`
  (העתק עמוק של ה-JSON — `dict(...)`/`list(...)` כדי לא לחלוק רפרנס). שמור דרך ה-repo.
- ולידציית `day_schedules`/`required_attributes` קורית ב-schemas (צעד 04), לא כאן.

## קבצים
1. **`backend/app/schedule_builder/repositories/position_repository.py`** (חדש) —
   `get_by_profile(profile_id)` (ממוין), `get_by_id`, `max_display_order_in_profile(profile_id)`.
2. **`backend/app/schedule_builder/services/position_service.py`** (חדש) —
   CRUD כנ"ל + חריג `PositionNotFoundException`. flush בלבד (ה-request commit-ים).
3. **`backend/app/schedule_builder/services/profile_service.py`** (עריכה) — מלא את
   `_copy_positions` (הסר את `# TODO(task 03)`). השתמש ב-`PositionRepository` על אותו
   session (`self._repo.session`) או הזרק repo עמדות לבנאי — **העדף הזרקה** כדי לשמור על טסטביליות.
4. **`backend/app/schedule_builder/dependencies.py`** (עריכה) — `get_position_service`;
   עדכן `get_profile_service` כך ש-`ProfileService` יקבל גם `PositionRepository`
   (לצורך `_copy_positions`).
5. **`backend/app/exceptions.py`** (עריכה) — `PositionNotFoundException`.

## טסטים (`tests/test_position_service.py`)
- list/create/update/delete — נתיב מאושר.
- `create_position` מצרף `display_order` עוקב **בתוך הפרופיל** (פרופילים שונים מתחילים מ-1).
- `update_position` משנה רק שדות שסופקו (JSON של ימים מתעדכן, השאר נשמר).
- **deep-copy:** עדכן `tests/test_profile_service.py` — שכפול פרופיל עם 2 עמדות יוצר 2 עמדות
  **חדשות** תחת היעד (id שונה), עם אותו תוכן; שינוי `day_schedules` של עותק לא משפיע על המקור.

## הרצה
`cd backend && .venv/bin/python -m pytest tests/ -q` — הכל ירוק.

## קומיט
```
feat(builder): position repository + service + deep-copy on profile duplicate
```
push · עדכן `_PROGRESS.md` · מחק קובץ פרומפט זה.
