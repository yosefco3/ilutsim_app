# הקשר מלא לצ'אט חדש — משימה 03: עמדות עם דרישות (Positions)

> **איך להשתמש:** פתח צ'אט חדש ב-`ilutzim_app` והדבק את הקובץ הזה (או כתוב:
> "קרא את `STAGE_B_PROMPTS/03_positions_with_requirements/_CONTEXT_FOR_NEW_CHAT.md`
> ופעל לפיו"). הוא נותן את כל ההקשר כדי להמשיך ישירות, בלי הצ'אט הקודם.

---

## מי אתה ומה הזרימה הרצויה

אתה ממשיך פרויקט קיים. **אל תתחיל לקודד מיד.** הזרימה (זהה לאיך שמשימה 02 בוצעה):
1. **קרא הקשר** — הקבצים ברשימה למטה, כדי להבין את המצב.
2. **כתוב את קבצי הפרומפט** ל-03 (צעדים קטנים, 2-4 קבצים כל אחד), בתוך
   `STAGE_B_PROMPTS/03_positions_with_requirements/`.
3. **שאל את המשתמש** את שאלות העיצוב הפתוחות (ראה למטה) — **וחכה לתשובה**, אל תרוץ.
4. רק אחרי אישור — **בצע צעד-צעד**: כל צעד = טסטים עוברים → קומיט קטן → push → עדכון
   `_PROGRESS.md` ומחיקת קובץ הפרומפט שבוצע.

---

## מה האפליקציה (תקציר)

מערכת ניהול משמרות מאבטחים. **שני חלקים:**
- **חלק א' (קיים): איסוף זמינות** — טלגרם + ייבוא אקסל → מודל הזמינות
  (`WeeklySubmission` / `DailyStatus` / `ShiftWindow`).
- **חלק ב' (בבנייה): בונה הסידור** — `STAGE_B_PROMPTS/` מגדיר 11 משימות:
  01 פייפליין אקסל ✅ · **02 פרופילי הפעלה ✅** · **03 עמדות ← אתה כאן** ·
  04 שלד לוח · 05 שיבוץ ידני · 06 צביעת זמינות+שעות · 07 אזהרות רכות ·
  08 גרירה · 09 חריגים פר-שבוע · 10 ייצוא אקסל · 11 הצעה אוטומטית (אופ').

## קבצים לקרוא קודם (סדר מומלץ)
1. `CLAUDE.md` — כללי העבודה (צעדים קטנים, טסטים, קומיט בסוף משימה, נתיבי כלים).
2. `APP_OVERVIEW.md` — מודלים, endpoints, מחזור-חיי-שבוע, היסטוריה. סעיף "🔭 בונה הסידור".
3. `STAGE_B_PROMPTS/README.md` — **הכללים הנעולים** (דאטא, עמדות, אזהרות) + טבלת המשימות.
4. `STAGE_B_PROMPTS/03_positions_with_requirements/README.md` — מטרת 03 + קריטריון הצלחה.
5. `backend/app/schedule_builder/` — **כל חלק ב' חי כאן** (ראה למטה).
6. `design-system/concepts/schedule-builder/data.js` — מבנה ה-`POSITIONS` וה-`ATTRS` מהקונספט.
7. `git log --oneline -7` — חמשת הקומיטים של 02 (מ-`beedcb4` עד `101f41a`).

---

## מה כבר נבנה במשימה 02 (הבסיס של 03)

**גבול הקוד (דרישה מהמשתמש — שמור עליו!):**
- כל קוד חלק ב' תחת `backend/app/schedule_builder/` (חבילת דומיין: `models/`,
  `repositories/`, `services/`, `controllers/`, `schemas/`, `dependencies.py`).
- פרונט: `frontend/admin/src/pages/builder/` + `frontend/admin/src/api/builderApiClient.js`.
- **תלות חד-כיוונית:** חלק ב' מותר לייבא מחלק א' (זמינות, `get_pool`, `require_admin_role`);
  חלק א' **אסור** לייבא מחלק ב' — היוצא היחיד: שורת ייבוא אחת ב-`app/models/__init__.py`
  (מתועדת) כדי ש-Alembic יראה את מודלי ב'.

**מה קיים:**
- מודל `ActivationProfile` (`schedule_builder/models/activation_profile.py`):
  `name`, `kind` (nullable, **לא בשימוש ב-UI** — הוסר לבקשת המשתמש), `description`
  (nullable, לא בשימוש ב-UI), `is_default`, `display_order`. יורש מ-`app.models.base.BaseModel`
  (UUID PK + timestamps). מיגרציה `6abbd8e22af6`.
- `ProfileRepository` + `ProfileService`: CRUD, `duplicate_profile`, `seed_default_profile`
  (זורע "שגרה" idempotent ב-startup דרך `app/main.py` lifespan).
- API `/admin/builder/profiles` (list/create/get/patch/duplicate/delete), `require_admin_role`,
  רשום ב-`main.py` בקבוצת "Part B".
- מסך `pages/builder/ProfilesPage.jsx` ב-route `/builder/profiles` + קבוצת ניווט "בונה הסידור".
  **ה-UI כרגע שדה-שם-אחד** (סוג/תיאור הוסרו מהטופס לבקשת המשתמש; העמודות נשארו ב-DB, לא בשימוש).

**🔌 ווים שהושארו ב-02 שצריך לחבר ב-03 (חשוב!):**
המודל `ActivationProfile` מתעד בהערות (בתחתית הקובץ) את התכנון לעמדות — **ב-03 ממשים אותו**:
- מודל `Position` חדש עם `profile_id` FK → `activation_profiles.id`,
  `nullable=False` אך **ניתן לעדכון** (העברת עמדה בין פרופילים = שינוי ה-FK).
- יחס ב-`ActivationProfile`: `positions: Mapped[List["Position"]] = relationship(
  back_populates="profile", cascade="all, delete-orphan", passive_deletes=True)` →
  מחיקת פרופיל מוחקת עמדותיו.
- `ProfileService._copy_positions(src, dst)` כרגע **no-op** עם `# TODO(task 03)` —
  ב-03 ממשים בו **deep-copy** של עמדות, כך ש"שכפול פרופיל" יעתיק גם את העמדות.
  (זו הסיבה שהשכפול נבנה דרך הפונקציה הזו — החתימה הציבורית לא משתנה.)

---

## הכללים הנעולים לעמדות (מקור אמת — אל תמציא מחדש)

מתוך `STAGE_B_PROMPTS/README.md` ו-`03/README.md`:
- **שורה בסידור = עמדה = דרישה למאבטח אחד.** שני אנשים בנקודה אחת = **שתי עמדות**.
- לכל עמדה: **שם**, **משמרת** (enum `ShiftType` ב-`app/constants.py`:
  בוקר=`MORNING`, **ערב=`AFTERNOON`**, לילה=`NIGHT`), **ימים פעילים**, **שעות פר-יום**,
  ו**מאפיינים נדרשים** (אחמ"ש / חמוש / רכב עירייה / רוני / הליכה מרובה...).
- **אוצר-הדרישות חייב להיות גמיש/קונפיגורבילי** — אפיון המאבטחים עדיין לא נסגר אצל המשתמש,
  אז **אל תקודד נוקשה** רשימת מאפיינים. שיהיה ניתן להוסיף/לשנות בלי מיגרציה/דיפלוי.
- מטרת 03: מסך שמגדירים בו **פעם אחת** את ~30 העמדות האמיתיות
  (ע.אחמ"ש, חש"י, ארנונה, קומה 6, סייר-1, ב-4, מבקרת, רכב סיור...).

**רפרנס מבנה (קונספט `data.js`):** עמדה = `{ id, name, hours:"07:00-15:00",
requires:["armed",...], activeDays:[0..6] }`; `ATTRS = {armed:'חמוש', roni:'רוני',
vehicle:'רכב עירייה', walking:'הליכה מרובה'}`. שים לב: בקונספט `hours` אחיד לכל הימים —
אבל הכלל הנעול דורש **שעות פר-יום**, אז המודל האמיתי צריך להכליל.

---

## שאלות עיצוב פתוחות — שאל את המשתמש לפני שכותבים מודל

1. **שעות פר-יום — איך למדל?** אופציות: (א) עמודת JSON על `Position` שממפה
   יום→`{start,end}`; (ב) טבלת-בת `PositionDaySchedule` (שורה ליום פעיל עם שעות);
   (ג) שעות ברירת-מחדל לעמדה + חריגות פר-יום. (יש tradeoff פשטות מול גמישות/שאילתות.)
2. **אוצר הדרישות (מאפיינים) — איך לאחסן ולנהל?** אופציות: (א) רשימת מפתחות-תגיות
   חופשית כ-JSON על העמדה + מילון תוויות נפרד הניתן לעריכה; (ב) טבלת `Attribute`
   קונפיגורבילית + טבלת-קשר עמדה↔מאפיין; (ג) טקסט חופשי. (המשתמש ביקש גמישות מקסימלית
   — סביר שלא enum נעול.)
3. **שיוך לפרופיל בטופס:** האם בוחרים פרופיל בעת יצירת עמדה, או שמסך העמדות הוא
   "בתוך פרופיל נבחר"? (משפיע על ה-UI וה-API — `/admin/builder/profiles/{id}/positions`
   מול `/admin/builder/positions?profile_id=`.)
4. **היקף 03:** רק CRUD עמדות + deep-copy בשכפול? או גם **גרירת עמדה בין פרופילים**
   (משימה 08 בתכנון המקורי)? המלצה: CRUD + deep-copy עכשיו, גרירה בהמשך.

---

## קונבנציות ביצוע (זהות ל-02)

- **Python:** אין `python` ב-PATH. backend venv: `backend/.venv/bin/python`.
- **טסטים backend:** `cd backend && .venv/bin/python -m pytest tests/ -q` (כרגע 265 ירוקים).
- **טסטים frontend:** `cd frontend/admin && npx vitest run` (כרגע 140 ירוקים) + `npm run build`.
- **הכל יחד:** `python3 scripts/test_graph.py`.
- **גרף קוד:** `/home/yosef/.local/bin/code-review-graph update` אחרי כל משימה.
- **APP_OVERVIEW.md:** עדכן מודלים/endpoints/דפים/מיגרציות/היסטוריה/תאריך.
- **קומיט:** Conventional Commits (`feat(builder): ...`), בסוף כל צעד, ענף `main` ישירות,
  **push אחרי כל קומיט**. סיים הודעות קומיט ב-`Co-Authored-By: Claude ...`.
- **DB למיגרציות:** PostgreSQL ב-`localhost:5432` (ראה `.env`). לפני `alembic revision
  --autogenerate`: `alembic upgrade head` (ודא `alembic current`/`heads` תואמים).
  ⚠️ **gotcha:** ה-autogenerate עלול לסמן `op.drop_table('schedule_events')` — זו טבלה
  ישנה ללא מודל (DB drift). **הסר את זה** מהמיגרציה; היא מחוץ לסקופ.
- **ספריית הפרומפטים:** קרא/צור `_PROGRESS.md`; בצע לפי מספר; אחרי כל צעד הוסף שורת
  סיכום ומחק את קובץ הפרומפט; בסוף "✅ All prompts completed".

---

## משימה 03 בקצרה
מודל `Position` (שייך ל-`ActivationProfile`, שם/משמרת/ימים/שעות-פר-יום/דרישות) + מיגרציה +
מימוש `_copy_positions` (deep-copy בשכפול) + repo/service/controller + schemas + מסך
`PositionsPage`. **קריטריון הצלחה (המשתמש מריץ):** מוסיף עמדה אמיתית (למשל "ארנונה",
א'-ה', שעות פר-יום, דרישות) → עורך → מוחק → מרענן → נשמר; מוסיף עמדות מכל משמרת ורואה את כולן.
