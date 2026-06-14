# צעד 01 · פרסר טהור לאקסל אילוצים

## מטרה
לבנות **פונקציה טהורה** שמקבלת קובץ אקסל (bytes) ומחזירה מבנה נתונים מסודר — **בלי שום נגיעה ב-DB**.
זה הבסיס לכל השאר; הכל נבדק ב-unit tests מול קובץ הדוגמה האמיתי.

## קרא קודם
- `STAGE_B_PROMPTS/README.md` → "הכללים הנעולים" (סמנטיקה מלאה).
- קובץ הדוגמה: `דוגמה_אילוצים_מאבטחים.xlsx` (שורש הריפו). `openpyxl` כבר מותקן ב-`backend/.venv`.
- `app/constants.py::ShiftType` (`MORNING`/`AFTERNOON`/`NIGHT`).

## קבצים (2-4)
- חדש: `backend/app/services/constraints_import/__init__.py`
- חדש: `backend/app/services/constraints_import/parser.py`
- חדש: `backend/tests/fixtures/דוגמה_אילוצים_מאבטחים.xlsx` (העתק של קובץ הדוגמה — כך שהטסט לא תלוי בנתיב שורש)
- חדש: `backend/tests/test_constraints_parser.py`

## מבנה הנתונים המוחזר (הצעה — dataclasses)
```python
class CellKind(Enum): WINDOW; ALL_DAY; UNAVAILABLE   # WINDOW=טווח שעות, ALL_DAY="זמין", UNAVAILABLE="לא זמין"/ריק
@dataclass
class Cell: kind: CellKind; start: time|None; end: time|None; wraps_midnight: bool=False
@dataclass
class ParsedGuard:
    name: str
    phone: str | None
    notes: str | None
    # cells[day_index 0..6][shift] -> Cell   (shift ∈ ShiftType: MORNING/AFTERNOON/NIGHT)
    cells: dict[int, dict[ShiftType, Cell]]
@dataclass
class ParsedImport:
    week_start: date | None       # מתוך כותרת "אילוצים שהוגשו — YYYY-MM-DD עד YYYY-MM-DD"
    week_end: date | None
    guards: list[ParsedGuard]
    errors: list[str]             # שגיאות פרסור לא-חוסמות (שעה לא תקינה וכו'), עם הקשר (שם+יום+משמרת)
```

## דרישות הפרסר
1. אתר את שורת הכותרת (זו שמכילה `שם`,`טלפון`,`משמרת`) — אל תניח מספר שורה קבוע.
2. קבץ כל 3 שורות-נתונים למאבטח (שם בעמודה A = תחילת מאבטח חדש). שם+טלפון+הערות נלקחים משורת הבוקר.
3. מפה את עמודת המשמרת: `בוקר→MORNING`, `ערב→AFTERNOON`, `לילה→NIGHT` (טפל ברווחים/גרשיים).
4. פענוח תא ליום:
   - ריק או `לא זמין` → `Cell(UNAVAILABLE)`.
   - `זמין` (בלי שעות) → `Cell(ALL_DAY)`.
   - טווח `HH:MM<dash>HH:MM` → `Cell(WINDOW, start, end)`; קבל **גם** en-dash `–` **וגם** `-`.
     אם `end <= start` → `wraps_midnight=True` (לילה).
   - כל דבר אחר / שעה לא חוקית → הוסף ל-`errors` (עם שם+יום+משמרת) ושים `UNAVAILABLE`. **אל תזרוק חריגה.**
5. פענח את טווח התאריכים מהכותרת ל-`week_start`/`week_end` (אם לא נמצא — `None`, לא קריסה).
6. נרמל טלפון לשדה `phone` (אפשר nullable; לא קריטי לשלב זה).

## טסטים (מול קובץ הדוגמה)
- 5 מאבטחים; השמות נכונים ובסדר.
- אבי כהן: ראשון/`MORNING` = WINDOW 07:00–16:00; שלישי/`MORNING` = 07:00–13:00; שלישי/`AFTERNOON`=15:00–19:00; שישי/`MORNING`=UNAVAILABLE; הערה = "מעדיף משמרות בוקר".
- בני לוי: ראשון/`NIGHT` = WINDOW 23:00–07:00 עם `wraps_midnight=True`; שלישי/`MORNING`=UNAVAILABLE (לא זמין).
- גדי מזרחי: הערה = "מילואים בתחילת השבוע"; ראשון/`MORNING`=UNAVAILABLE.
- דנה אזולאי: שבת/`MORNING` = ALL_DAY ("זמין"); הערה = "זמינה בכל המשמרות".
- `week_start == date(2026,6,14)`, `week_end == date(2026,6,20)`.
- `errors == []` על הקובץ התקין.

הרץ: `cd backend && .venv/bin/python -m pytest tests/test_constraints_parser.py -q`

## קריטריון הצלחה
- ✅ הטסטים עוברים.
- ✅ (המשתמש) — אין UI עדיין; אישור ידני יגיע בצעד 04.

## סיום
קומיט: `feat(import): pure parser for guard-constraints xlsx`. push. עדכן `_PROGRESS.md` ומחק קובץ זה.
