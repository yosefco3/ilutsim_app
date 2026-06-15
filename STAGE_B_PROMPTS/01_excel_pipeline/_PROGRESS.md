# _PROGRESS — 01 אקסל + פייפליין ייבוא

> ריק = טרם התחלנו. אחרי כל צעד שהושלם: הוסף שורה (מה נעשה · קבצים · הודעת commit) ומחק את קובץ
> הפרומפט שבוצע (לפי workflow ספריית הפרומפטים ב-CLAUDE.md). בסיום הכל: "✅ All prompts completed".

- **01** · פרסר טהור לאקסל אילוצים (bytes → `ParsedImport`, ללא DB). מאתר שורת כותרת, מקבץ 3 שורות/מאבטח,
  ממפה משמרות, מפענח תאים (חלון/זמין/לא-זמין, en-dash + מקף, חציית חצות), שבוע מהכותרת, שגיאות לא-חוסמות.
  · קבצים: `backend/app/services/constraints_import/{__init__,parser}.py`, `tests/test_constraints_parser.py`,
  `tests/fixtures/דוגמה_אילוצים_מאבטחים.xlsx` · 8 טסטים עוברים · commit `d6c3e02` `feat(import): pure parser for guard-constraints xlsx`
- **02** · מיזוג חפיפות → שעות מהאיחוד (`hours.py`, טהור). חלון/ALL_DAY→מקטעים, מיזוג חופף-או-נוגע, ספירה מהאיחוד
  (12≠13.5), לילה חוצה חצות +24ש' נספר ביום ההתחלה. **קונבנציית `זמין`=איחוד חלונות-משמרת הדיפולטיביים (24ש')** —
  ניתן להזרקה (`all_day_windows`). · קבצים: `constraints_import/hours.py`, `tests/test_constraints_hours.py` · 8 טסטים ·
  commit `feat(import): merge overlapping availability windows, count union hours`
- **03** · מסך תצוגה נקי (preview / dry-run). `POST /admin/import/constraints/preview` (multipart) → parser+hours →
  JSON נקי (שבוע, חלונות יומיים ממוזגים, שעות שבועיות מהאיחוד, הערות, `exists` חיווי בלבד, שגיאות). Frontend:
  `ImportConstraintsPage` (טבלה RTL נקייה + אזור שגיאות + תג חדש/קיים), קישור ניווט, route, upload helper, CSS.
  כפתור "אשר" מושבת (יופעל ב-04). · קבצים: `constraints_import_controller.py`, `schemas/constraints_import.py`,
  `services/constraints_import/preview.py`, `ImportConstraintsPage.jsx` + API/Navbar/App/messages/css · 4 טסטי backend +
  4 frontend · backend 239 / frontend 134 ירוקים · commit `feat(import): constraints import preview screen (dry-run)`
- **04** · commit למודל הזמינות. `POST /admin/import/constraints/commit` → מצאי-או-צור מאבטח לפי שם (חדש=`BASIC_GUARD`),
  איתור שבוע היעד מטווח הקובץ (או `week_id`), upsert דרך `submission_service.create_submission(override_lock=True)`,
  חלונות נשמרים as-is, `זמין`=חלון-משמרת דיפולטי, כשל פר-מאבטח נאסף ולא חוסם. Frontend: "אשר ייבוא" פעיל + בורר
  שבוע אופציונלי + כרטיס סיכום + Toast. · קבצים: `constraints_import/commit.py`, `constraints_import_controller.py`,
  `dependencies.py`, `ImportConstraintsPage.jsx`, `test_import_commit.py` (+frontend) · backend 243 / frontend 135 ·
  commit `feat(import): commit imported constraints into availability model`
