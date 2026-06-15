# צעד 03 · מסך תצוגה נקי (Preview / dry-run)

## מטרה
**זה ה-milestone שהמשתמש ביקש** — להעלות אקסל ו**לראות את כל הנתונים נקיים ומסודרים** (חלונות ממוזגים,
שעות נכונות, הערות) — **בלי לשמור עדיין** (dry-run). מחבר את צעדים 01-02 (parser + hours).

## קרא קודם
- צעדים 01-02 (parser / hours).
- `STAGE_B_PROMPTS/README.md` → "התאמת מאבטח" (זהות = שם; מצאי-או-צור; **בלי דחייה ובלי שמות כפולים**).
- אימות אדמין: `app/dependencies.py::require_admin_role`; ראוטים תחת `/admin`.
- frontend: `frontend/admin/src/api/adminApiClient.js`, דפים קיימים תחת `src/pages/`, ה-Navbar.

## קבצים (3-4)
- חדש: `backend/app/controllers/constraints_import_controller.py` —
  `POST /admin/import/constraints/preview` (קלט: קובץ xlsx, multipart). מריץ parser→hours
  ומחזיר JSON נקי (ללא שמירה).
- חדש: `backend/app/schemas/constraints_import.py` (סכמות תגובה).
- חדש: `frontend/admin/src/pages/ImportConstraintsPage.jsx` + קישור ב-Navbar + מתודה ב-adminApiClient.
- טסטים: `backend/tests/test_import_preview_endpoint.py`.

## תגובת ה-preview (JSON)
```jsonc
{
  "week_start": "2026-06-14", "week_end": "2026-06-20",
  "guards": [{
    "name": "אבי כהן",
    "exists": true,          // אינפורמטיבי בלבד: האם כבר יש מאבטח בשם הזה (אם לא — ייווצר ב-commit). לא חוסם.
    "notes": "מעדיף משמרות בוקר",
    "weekly_hours": 60.5,
    "days": [{ "day_index": 0, "day_name": "ראשון",
               "segments": ["07:00–16:00"], "hours": 9.0,
               "shifts": { "morning": "07:00–16:00", "afternoon": null, "night": null } }]
  }],
  "errors": []
}
```
> **בלי** `matched`/`unmatched`/`ambiguous` — אין דחיית שמות ואין טיפול בכפילויות. כל שם שבאקסל
> מוצג ויעבור לסידור. השדה `exists` הוא חיווי בלבד ("חדש"/"קיים"), לא מסנן.

## ה-UI (מסך נקי)
- כפתור העלאת קובץ → קריאה ל-preview.
- טבלה מסודרת RTL: שורה לכל מאבטח, עמודות לימים, כל תא מציג את **החלון הממוזג** + סימון משמרות;
  עמודת "שעות שבועיות", עמודת "הערות", וחיווי קטן "חדש/קיים" (אינפורמטיבי).
- אזור שגיאות פרסור בולט למעלה (כדי שטעות-שעה תצוף).
- כפתור "אשר ייבוא" — **מושבת בצעד הזה** (יופעל בצעד 04).

## טסטים
- POST עם קובץ הדוגמה → 200, 5 מאבטחים, דנה ראשון = "07:00–23:00" / 16ש', אבי עם חפיפה לפי האיחוד,
  הערות נכונות, `week_start` נכון.
- ללא הרשאת אדמין → 401/403.
- קובץ פגום → 4xx עם הודעה, לא 500.

הרץ: backend `pytest`, frontend `cd frontend/admin && npx vitest run`.

## קריטריון הצלחה
- ✅ טסטים עוברים.
- ✅ **(המשתמש מריץ):** מעלה את `דוגמה_אילוצים_מאבטחים.xlsx` במסך → רואה טבלה נקייה ומסודרת,
  כולל הערות וחלונות ממוזגים נכונים. **אישור ידני זה הוא תנאי המעבר לצעד 04.**

## סיום
קומיט: `feat(import): constraints import preview screen (dry-run)`. push. עדכן `_PROGRESS.md` ומחק קובץ זה.
