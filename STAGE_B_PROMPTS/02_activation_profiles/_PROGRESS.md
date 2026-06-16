# _PROGRESS — 02 פרופילי הפעלה

> ריק = טרם התחלנו. הוסף שורת סיכום אחרי כל צעד שהושלם.

- **00** · הפרדת קוד חלק א'↔ב'. נוצרה חבילת דומיין `backend/app/schedule_builder/`
  (`__init__` עם כללי הגבול + `models/repositories/services/controllers/schemas/__init__` + `dependencies.py` ריק).
  הערת-מקום ב-`app/models/__init__.py` ל-Alembic. Frontend: `pages/builder/` (`.gitkeep`) +
  `api/builderApiClient.js` שמייצא-מחדש את `request` המשותף (יוצא ל-export מ-`adminApiClient.js`).
  עודכן `APP_OVERVIEW.md` (חלק ב' "בבנייה" + גבול קוד). תשתית בלבד — אפס שינוי התנהגות.
  · backend 243 / frontend 135 ירוקים · commit `chore(builder): scaffold part-B (schedule builder) code boundary`
