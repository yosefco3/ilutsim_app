# 03 · צעד 02 — אוצר-מאפיינים קונפיגורבילי (`RequirementAttribute`)

> ממש את הדרישה הנעולה: **אוצר-הדרישות חייב להיות גמיש/קונפיגורבילי** — ניתן להוסיף/לשנות
> מאפיינים **בלי מיגרציה/דיפלוי**. הפתרון: טבלת קונפיג (שורות-דאטה, לא סכימה) הניתנת לעריכה מה-UI.

## מטרה
מודל `RequirementAttribute` — מילון מפתח→תווית של המאפיינים (חמוש / רוני / רכב עירייה /
הליכה מרובה / אחמ"ש...). עמדות מאחסנות **מפתחות** בלבד (`required_attributes` מצעד 01),
והמילון הזה נותן להם תוויות תצוגה וניהול מרכזי. הוספת מאפיין = שורה חדשה (לא מיגרציה).

## החלטות עיצוב נעולות
- שדות: `key: str` (ייחודי, slug באנגלית, `String(50)`, `unique=True, index=True`),
  `label: str` (תווית עברית לתצוגה, `String(100)`), `display_order: int`.
  יורש מ-`BaseModel` (UUID PK + timestamps).
- **לא** FK קשיח בין `Position.required_attributes` למילון — היחס "רך" (מפתחות מחרוזת).
  כך מחיקת מאפיין לא שוברת עמדה; אזהרות-תקינות יטופלו בהמשך (משימות 06/07).
- **זריעה idempotent ב-startup** של אוצר ברירת-מחדל מתוך הקונספט
  (`design-system/concepts/schedule-builder/data.js` → `ATTRS`):
  `armed→חמוש`, `roni→רוני`, `vehicle→רכב עירייה`, `walking→הליכה מרובה`.
  אם כבר קיימת שורה כלשהי — no-op (כמו `seed_default_profile`).

## קבצים
1. **`backend/app/schedule_builder/models/requirement_attribute.py`** (חדש) — המודל.
2. **`backend/app/schedule_builder/models/__init__.py`** (עריכה) — ייצא `RequirementAttribute`.
3. **`backend/app/models/__init__.py`** (עריכה) — שורת ייבוא ל-Alembic (היוצא היחיד מהגבול, מתועד).
4. **`backend/app/schedule_builder/repositories/attribute_repository.py`** (חדש) —
   `get_all_ordered`, `get_by_key`, `count`, `max_display_order`. (תבנית `ProfileRepository`.)
5. **`backend/app/schedule_builder/services/attribute_service.py`** (חדש) —
   `list/create/rename/delete` + `seed_default_attributes`. כפל-מפתח → חריג ברור.
6. **`backend/app/schedule_builder/dependencies.py`** (עריכה) — `get_attribute_service`.
7. **`backend/app/exceptions.py`** (עריכה) — `AttributeKeyConflictException`,
   `AttributeNotFoundException` (בתבנית חריגי הפרופיל).
8. **`backend/app/main.py`** (עריכה) — קרא ל-`seed_default_attributes()` ב-lifespan,
   ליד `seed_default_profile()`.
9. **מיגרציה** `<hash>_add_requirement_attributes.py` — `create_table("requirement_attributes", ...)`.
   ⚠️ הסר `drop_table('schedule_events')` אם מופיע. round-trip נקי.

## טסטים
- `tests/test_requirement_attribute_model.py` — יצירה/ייחודיות `key`/ברירות מחדל.
- `tests/test_attribute_service.py` — list/create/rename/delete, כפל-מפתח חוסם,
  `seed_default_attributes` זורע 4 ורץ פעמיים בלי כפילות (idempotent).

## הרצה
`cd backend && .venv/bin/python -m pytest tests/ -q` — הכל ירוק.

## קומיט
```
feat(builder): configurable requirement-attributes vocabulary + seed
```
push · עדכן `_PROGRESS.md` · מחק קובץ פרומפט זה.
