# צעד 05 · שמירה למודל הזמינות הקיים (Commit)

## מטרה
להפוך את ה-preview לכתיבה אמיתית: לשמור את האילוצים שיובאו ל**מודל הזמינות הקיים** —
`WeeklySubmission` / `DailyStatus` / `ShiftWindow` — לשבוע היעד, כך שהכל מופיע במסך "הגשות" הקיים
ומשמש את בונה הסידור. **מקור אמת אחד** עם טלגרם.

## קרא קודם
- `STAGE_B_PROMPTS/README.md` → "מקור אמת אחד" + "שבוע היעד".
- מודלים: `app/models/weekly_submission.py` (unique `user_id`+`week_id`), `daily_status.py`
  (`date`,`is_available`), `shift_window.py` (`shift_type`,`start_time`,`end_time`).
- `app/services/submission_service.py::create_submission` + `repo.upsert_submission(user_id, week_id, payload)` —
  **השתמש מחדש** בנתיב ה-upsert הקיים במקום לכתוב כתיבה ידנית ל-ORM (עקביות + מכבד את אותם כללים).
- `app/repositories/schedule_week_repository.py` — איתור שבוע לפי טווח תאריכים.

## קבצים (2-4)
- הרחבת `constraints_import_controller.py`: `POST /admin/import/constraints/commit`.
- חדש/הרחבה: `app/services/constraints_import/importer.py` — ממיר `ParsedImport`+`MatchResult` →
  קריאות `create_submission`/`upsert_submission` (לכל מאבטח שזוהה).
- טסטים: `backend/tests/test_import_commit.py`.

## דרישות
1. **בחירת שבוע היעד:** אתר שבוע שה-`start_date` שלו = `week_start` מהכותרת. אם לא קיים — החזר שגיאה
   ברורה (אל תיצור שבוע בשקט). אפשר לאפשר למשתמש לבחור שבוע ידנית כ-fallback (פרמטר `week_id`).
2. לכל מאבטח **שזוהה**: בנה payload של 7 ימים × משמרות:
   - מיפוי משמרת: `morning→MORNING`, `evening→AFTERNOON`, `night→NIGHT`.
   - `WINDOW` → `ShiftWindow(start_time,end_time)` (שמור את החלונות **כפי שהם**, לא ממוזגים — המיזוג הוא
     חישוב תצוגה/בונה, לא אחסון).
   - `ALL_DAY` → לפי הקונבנציה שנקבעה בצעד 03 (תעד).
   - `UNAVAILABLE`/ריק → אין `ShiftWindow`; `DailyStatus.is_available=False` ליום בלי אף חלון.
   - `general_notes` ← ההערות.
3. **upsert** (כמו טלגרם) — ייבוא חוזר מעדכן ולא מכפיל. כבד את כללי הנעילה הקיימים
   (`override_lock` לפי הצורך — אדמין מייבא; החלט במפורש והתאם להתנהגות `POST /submissions/admin`).
4. מאבטחים לא-מזוהים → לא נכתבים; חוזרים בדוח (צעד 06).

## טסטים
- commit עם קובץ הדוגמה (אחרי זריעת השבוע + המאבטחים) → נוצרות `WeeklySubmission` לכל מאבטח שזוהה,
  עם `DailyStatus`/`ShiftWindow` נכונים (אבי ראשון בוקר 07:00–16:00; בני ראשון לילה 23:00–07:00).
- ייבוא חוזר → אותו מספר רשומות (upsert, לא כפילות).
- שבוע לא קיים → שגיאה ברורה, ללא כתיבה.

הרץ: `cd backend && .venv/bin/python -m pytest tests/test_import_commit.py -q`

## קריטריון הצלחה
- ✅ טסטים עוברים.
- ✅ **(המשתמש מריץ):** אחרי "אשר ייבוא" → נכנס למסך **"הגשות"** הקיים לשבוע הבא → רואה את כל
  המאבטחים שיובאו עם הזמינות הנכונה (וגם נטען לעריכה דרך `GET /submissions/admin`).

## סיום
קומיט: `feat(import): commit imported constraints into availability model`. push. עדכן `_PROGRESS.md` ומחק קובץ זה.
