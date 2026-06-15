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
