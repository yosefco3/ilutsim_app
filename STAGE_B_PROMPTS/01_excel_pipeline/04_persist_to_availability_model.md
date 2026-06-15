# צעד 04 · שמירה למודל הזמינות הקיים (Commit)

## מטרה
להפוך את ה-preview לכתיבה אמיתית: לשמור את האילוצים שיובאו ל**מודל הזמינות הקיים** —
`WeeklySubmission` / `DailyStatus` / `ShiftWindow` — לשבוע היעד, כך שהכל מופיע במסך "הגשות" הקיים
ומשמש את בונה הסידור. **מקור אמת אחד** עם טלגרם.

## קרא קודם
- `STAGE_B_PROMPTS/README.md` → "מקור אמת אחד" + "שבוע היעד" + "התאמת מאבטח" (מצאי-או-צור לפי שם).
- מודלים: `app/models/weekly_submission.py` (unique `user_id`+`week_id`), `daily_status.py`
  (`date`,`is_available`), `shift_window.py` (`shift_type`,`start_time`,`end_time`).
- `app/services/submission_service.py::create_submission` + `repo.upsert_submission(user_id, week_id, payload)` —
  **השתמש מחדש** בנתיב ה-upsert הקיים במקום כתיבה ידנית ל-ORM (עקביות + אותם כללים).
- `app/repositories/user_repository.py` (יצירת מאבטח), `schedule_week_repository.py` (איתור שבוע).

## דרישות
1. **זהות = שם (מצאי-או-צור):** לכל `ParsedGuard` חפש מאבטח קיים **לפי שם**; אם אין — **צור** מאבטח חדש
   (שם מהאקסל, טלפון אם קיים, תפקיד ברירת-מחדל `BASIC_GUARD`, `is_active=True`). כך גם רשומה שהאדמין
   כתב ידנית באקסל נכנסת לסידור. **אין דחייה, אין טיפול בשמות כפולים** (מובטחת ייחודיות במדיניות).
2. **בחירת שבוע היעד:** אתר שבוע שה-`start_date` שלו = `week_start` מהכותרת. אם לא קיים — החזר שגיאה
   ברורה (אל תיצור שבוע בשקט). אפשר fallback של בחירת שבוע ידנית (פרמטר `week_id`).
3. לכל מאבטח בנה payload של 7 ימים × משמרות:
   - מיפוי משמרת: `morning→MORNING`, `evening→AFTERNOON`, `night→NIGHT`.
   - `WINDOW` → `ShiftWindow(start_time,end_time)` (שמור את החלונות **כפי שהם**, לא ממוזגים — המיזוג הוא
     חישוב תצוגה/בונה, לא אחסון).
   - `ALL_DAY` → לפי הקונבנציה שנקבעה בצעד 02 (תעד).
   - `UNAVAILABLE`/ריק → אין `ShiftWindow`; `DailyStatus.is_available=False` ליום בלי אף חלון.
   - `general_notes` ← ההערות.
4. **upsert** (כמו טלגרם) — ייבוא חוזר מעדכן ולא מכפיל. כבד את כללי הנעילה הקיימים
   (`override_lock` לפי הצורך — אדמין מייבא; החלט במפורש והתאם להתנהגות `POST /submissions/admin`).

## טסטים
- commit עם קובץ הדוגמה (אחרי זריעת השבוע) → לכל מאבטח נוצרת `WeeklySubmission` עם
  `DailyStatus`/`ShiftWindow` נכונים (אבי ראשון בוקר 07:00–16:00; בני ראשון לילה 23:00–07:00).
- **מאבטח שלא קיים בשם → נוצר** ואז נכתבת לו הגשה.
- ייבוא חוזר → אותו מספר רשומות (upsert, לא כפילות; ולא יוצר את אותו מאבטח פעמיים).
- שבוע לא קיים → שגיאה ברורה, ללא כתיבה.

הרץ: `cd backend && .venv/bin/python -m pytest tests/test_import_commit.py -q`

## קריטריון הצלחה
- ✅ טסטים עוברים.
- ✅ **(המשתמש מריץ):** אחרי "אשר ייבוא" → נכנס למסך **"הגשות"** הקיים לשבוע הבא → רואה את כל
  המאבטחים שיובאו (כולל מי שנכתב ידנית באקסל ולא היה קיים) עם הזמינות הנכונה.

## סיום
קומיט: `feat(import): commit imported constraints into availability model`. push. עדכן `_PROGRESS.md` ומחק קובץ זה.
