# _PROGRESS — 02 פרופילי הפעלה

> ריק = טרם התחלנו. הוסף שורת סיכום אחרי כל צעד שהושלם.

- **00** · הפרדת קוד חלק א'↔ב'. נוצרה חבילת דומיין `backend/app/schedule_builder/`
  (`__init__` עם כללי הגבול + `models/repositories/services/controllers/schemas/__init__` + `dependencies.py` ריק).
  הערת-מקום ב-`app/models/__init__.py` ל-Alembic. Frontend: `pages/builder/` (`.gitkeep`) +
  `api/builderApiClient.js` שמייצא-מחדש את `request` המשותף (יוצא ל-export מ-`adminApiClient.js`).
  עודכן `APP_OVERVIEW.md` (חלק ב' "בבנייה" + גבול קוד). תשתית בלבד — אפס שינוי התנהגות.
  · backend 243 / frontend 135 ירוקים · commit `chore(builder): scaffold part-B (schedule builder) code boundary`
- **01** · מודל `ActivationProfile` (name/kind חופשי/description/is_default/display_order) + הערות הכנה לעמדות עתידיות
  (FK ניתן לשיוך-מחדש, cascade, `_copy_positions`). נרשם ל-Alembic ב-`app/models/__init__.py`. מיגרציה
  `6abbd8e22af6_add_activation_profiles` (נוקתה מ-drop של `schedule_events` — drift קיים, מחוץ לסקופ); round-trip
  upgrade/downgrade נקי. · קבצים: `schedule_builder/models/activation_profile.py` (+`__init__`), `app/models/__init__.py`,
  `alembic/versions/6abbd8e22af6_*.py`, `tests/test_activation_profile_model.py` (4 טסטים) · backend 247 ·
  commit `feat(builder): ActivationProfile model + migration`
