# 01 · מודל `ActivationProfile` + מיגרציית Alembic

**תלוי ב:** פרומפט 00 (חבילת `app/schedule_builder/` קיימת).

**מטרה:** הישות הבסיסית של חלק ב'. פרופיל הפעלה = **תבנית לשימוש חוזר** שמחזיקה עמדות
(העמדות עצמן נכנסות בפרומפט נפרד / משימה 03 — כאן הפרופיל נשאר ריק מעמדות).

## עקרון המוצר (נעול מול המשתמש)

- פרופיל = **תבנית**, לא מופע פר-שבוע. דוגמה: יש פרופיל "שגרה"; בשבוע עם חג באמצע
  המשתמש **משכפל** את "שגרה", **משנה יום אחד**, ושומר כפרופיל חדש ("חג X").
- שיוך פרופיל↔שבוע **לא נכנס כאן** — הוא יגיע עם הלוח (משימה 04).
- **שכפול + עריכה הם הלב** של הפיצ'ר → המודל ושכבת השירות חייבים לתמוך ב-deep-copy.

## המודל — `app/schedule_builder/models/activation_profile.py`

יורש מ-`app.models.base.BaseModel` (UUID PK + timestamps). שדות:

| שדה | טיפוס | הערות |
|-----|-------|-------|
| `name` | `str` (לא null) | שם הפרופיל, חופשי. למשל "שגרה", "חג סוכות". |
| `kind` | `str` nullable | **סוג חופשי** — תווית קטגוריה (שגרה/חג/אירוע/כל דבר). **לא enum** — גמישות מקסימלית (החלטת המשתמש). |
| `description` | `str` nullable | תיאור חופשי אופציונלי. |
| `is_default` | `bool` default False | מסמן את פרופיל "שגרה" הזרוע. בדיוק אחד אמור להיות `True`. |
| `display_order` | `int` default 0 | סדר תצוגה במסך הניהול. |

**הכנה לעתיד — חובה לתעד בהערה במודל (אבל לא לממש עכשיו):**
- במשימה 03 ייכנס מודל `Position` עם `profile_id` FK → `activation_profiles.id`.
- היחס יהיה `positions: Mapped[List["Position"]]` עם `cascade="all, delete-orphan"`,
  כך ש**מחיקת פרופיל מוחקת את עמדותיו**.
- **העברת עמדה בין פרופילים** = שינוי ה-FK `Position.profile_id` (reassign), ולכן ה-FK
  חייב להיות nullable=False אך **ניתן לעדכון**. כתוב את ההערה הזו ליד מקום היחס העתידי.
- **שכפול פרופיל** יבצע deep-copy של העמדות — ראה פרומפט 02 (`duplicate`).

## רישום ל-Alembic (שמירת הגבול)
הוסף ל-`app/models/__init__.py`, **בתחתית**, את שורת הייבוא המפורשת (השלמה של הערת-המקום מפרומפט 00):

```python
# Part B (schedule builder) models — imported ONLY so Alembic autogenerate sees
# them in Base.metadata. The code lives under app/schedule_builder/.
from app.schedule_builder.models.activation_profile import ActivationProfile  # noqa: E402,F401
```

(התלות א'→ב' כאן היא ל-Alembic בלבד ומתועדת ככזו; לוגיקת חלק א' לא נוגעת בפרופילים.)

## מיגרציה
`cd backend && .venv/bin/python -m alembic revision --autogenerate -m "add activation_profiles"`
ואז ביקורת ידנית של הקובץ ב-`alembic/versions/` (טבלה `activation_profiles`, עמודות נכונות,
`down_revision` תקין). הרץ `alembic upgrade head` ואמת.

## טסטים
`backend/tests/test_activation_profile_model.py`:
- יצירת פרופיל עם שדות מינימליים (name בלבד) — נשמר, ברירות-מחדל נכונות (`is_default=False`, `display_order=0`).
- `kind`/`description` nullable — אפשר None.
- round-trip מה-DB.

## קבצים צפויים
`app/schedule_builder/models/activation_profile.py`, `app/schedule_builder/models/__init__.py` (ייצוא),
`app/models/__init__.py` (שורת ייבוא), `alembic/versions/<hash>_add_activation_profiles.py`,
`tests/test_activation_profile_model.py`.

## קריטריון הצלחה
- `alembic upgrade head` עובר; טבלה קיימת.
- טסטים עוברים: `cd backend && .venv/bin/python -m pytest tests/test_activation_profile_model.py -q`.
- כל יתר הטסטים ירוקים.

## commit
`feat(builder): ActivationProfile model + migration`
