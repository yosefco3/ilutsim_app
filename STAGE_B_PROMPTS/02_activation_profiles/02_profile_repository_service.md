# 02 · Repository + Service לפרופילים (כולל שכפול וזריעת "שגרה")

**תלוי ב:** פרומפט 01 (מודל + מיגרציה).

**מטרה:** שכבת הנתונים והלוגיקה של הפרופילים — CRUD + **שכפול** + **זריעת ברירת-מחדל**.
זו השכבה שה-API (פרומפט 03) יקרא לה. עדיין אין UI.

## Repository — `app/schedule_builder/repositories/profile_repository.py`

`ProfileRepository(BaseRepository[ActivationProfile])` (יורש מ-`app.repositories.base_repository`).
מתודות מעבר ל-CRUD הגנרי:
- `get_all_ordered()` → כל הפרופילים ממוינים לפי `display_order` ואז `created_at`.
- `get_default()` → הפרופיל עם `is_default=True` (או None).

## Service — `app/schedule_builder/services/profile_service.py`

`ProfileService(profile_repo)`. מתודות:

- `list_profiles()` → רשימה ממוינת (`get_all_ordered`).
- `get_profile(id)` → פרופיל יחיד או חריג not-found (השתמש בתבנית החריגים הקיימת
  ב-`app/exceptions.py`; אם אין מתאים — הוסף `ProfileNotFoundException` קטן שם, עם 404).
- `create_profile(data)` → יצירה. `display_order` = max קיים + 1 אם לא סופק.
- `rename_profile(id, name, kind?, description?)` → עדכון שדות מטא (PATCH). **לא** נוגע ב-`is_default`.
- `delete_profile(id)` → מחיקה. **כלל:** אסור למחוק את הפרופיל היחיד שנותר
  (תמיד חייב להישאר ≥1 פרופיל); אסור למחוק פרופיל עם `is_default=True` כל עוד קיים רק הוא.
  אחרת — מחיקה מותרת (העמדות יימחקו ב-cascade כשייכנסו במשימה 03).
- `duplicate_profile(id, new_name?)` → **הלב של הפיצ'ר.**
  - יוצר פרופיל חדש עם אותם `kind`/`description`, `is_default=False`,
    `name = new_name or f"{src.name} (עותק)"`, `display_order` בסוף.
  - **deep-copy של עמדות:** כרגע אין מודל `Position`, אז הפונקציה מעתיקה רק את שורת הפרופיל.
    **כתוב את הקוד כך שהרחבה ל-deep-copy תהיה מקומית** — למשל הוצא `_copy_positions(src, dst)`
    שכרגע הוא no-op עם הערה `# TODO(task 03): deep-copy positions here`. כך שכשהעמדות
    ייכנסו, רק הפונקציה הזו משתנה ולא חתימת ה-API.

- `seed_default_profile()` → **idempotent**. אם אין אף פרופיל — צור "שגרה" עם `is_default=True`.
  אם כבר קיים פרופיל כלשהו — no-op. אל תיצור כפילויות.

## זריעה ב-startup
חבר את `seed_default_profile()` ל-startup של האפליקציה, באותו מקום/דפוס שבו רוטציית
השבועות נזרעת (ראה `app/main.py` lifespan / `auto_advance_weeks`). חייב להיות idempotent
(ריצה חוזרת בכל עליית שרת לא מייצרת כפילות).

## Dependencies
הוסף factory ל-`app/schedule_builder/dependencies.py` (לא ל-`app/dependencies.py` — שמירת הגבול):

```python
async def get_profile_service(session = Depends(get_session)) -> ProfileService:
    return ProfileService(ProfileRepository(session))
```

(מותר לייבא `get_session` מחלק א' — תלות ב'→א' מותרת.)

## טסטים
`backend/tests/test_profile_service.py`:
- create → list מחזיר אותו, ממוין.
- duplicate → פרופיל חדש, `is_default=False`, שם "(עותק)", שדות מטא מועתקים.
- rename → שדות משתנים, `is_default` לא משתנה.
- delete → מחיקה רגילה עובדת; מחיקת הפרופיל היחיד נחסמת (חריג); מחיקת ברירת-המחדל היחידה נחסמת.
- `seed_default_profile` idempotent: ריצה ראשונה יוצרת "שגרה"; ריצה שנייה לא מוסיפה.

## קבצים צפויים
`app/schedule_builder/repositories/profile_repository.py`,
`app/schedule_builder/services/profile_service.py`,
`app/schedule_builder/dependencies.py`, ייצואים ב-`__init__.py` הרלוונטיים,
(אופציונלי) `app/exceptions.py` (`ProfileNotFoundException`),
`app/main.py` (קריאת seed ב-startup), `tests/test_profile_service.py`.

## קריטריון הצלחה
- `pytest tests/test_profile_service.py -q` ירוק; כל יתר הטסטים ירוקים.
- עליית שרת זורעת "שגרה" פעם אחת (לא כפול ברסטארט).

## commit
`feat(builder): profile repository + service (CRUD, duplicate, seed default)`
