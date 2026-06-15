# _PROGRESS — 01 אקסל + פייפליין ייבוא

> ריק = טרם התחלנו. אחרי כל צעד שהושלם: הוסף שורה (מה נעשה · קבצים · הודעת commit) ומחק את קובץ
> הפרומפט שבוצע (לפי workflow ספריית הפרומפטים ב-CLAUDE.md). בסיום הכל: "✅ All prompts completed".

- **01** · פרסר טהור לאקסל אילוצים (bytes → `ParsedImport`, ללא DB). מאתר שורת כותרת, מקבץ 3 שורות/מאבטח,
  ממפה משמרות, מפענח תאים (חלון/זמין/לא-זמין, en-dash + מקף, חציית חצות), שבוע מהכותרת, שגיאות לא-חוסמות.
  · קבצים: `backend/app/services/constraints_import/{__init__,parser}.py`, `tests/test_constraints_parser.py`,
  `tests/fixtures/דוגמה_אילוצים_מאבטחים.xlsx` · 8 טסטים עוברים · commit `d6c3e02` `feat(import): pure parser for guard-constraints xlsx`
