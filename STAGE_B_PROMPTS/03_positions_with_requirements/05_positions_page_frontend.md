# 03 · צעד 05 — מסך העמדות (Frontend) + תיעוד + גרף

> הצעד האחרון של 03. מסך שמגדירים בו **פעם אחת** את ~30 העמדות האמיתיות.
> תבנית מלאה: `pages/builder/ProfilesPage.jsx` + `api/builderApiClient.js`.

## מטרה
מסך `PositionsPage` תחת `/builder/positions`: בורר פרופיל למעלה, רשימת העמדות של הפרופיל
מקובצת לפי משמרת, טופס הוספה/עריכה עם **רשת שעות-פר-יום** ו**צ'קבוקסים לדרישות** (מתוך אוצר
המאפיינים), מחיקה עם אישור. בנוסף ניהול קל של אוצר-המאפיינים.

## החלטות עיצוב נעולות
- **בורר פרופיל בראש המסך** (`<select>` מ-`listProfiles`); כל הפעולות חלות על הפרופיל הנבחר.
  ברירת מחדל = הפרופיל ה-`is_default`.
- **עורך עמדה (מודל):** שם · משמרת (בוקר/ערב/לילה) · **רשת 7 ימים** — לכל יום צ'קבוקס "פעיל"
  + שדות `start`/`end` (`<input type="time">`), שמתקפלים ל-`day_schedules` (רק ימים פעילים) ·
  **צ'קבוקסים לדרישות** מתוך `listAttributes()` (label עברי, value=key) → `required_attributes`.
- **רשימת עמדות** מקובצת לפי משמרת (בוקר→ערב→לילה), כל עמדה מציגה שם, תקציר ימים+שעות, ותגיות הדרישות.
- **ניהול אוצר-מאפיינים** — קל (אזור/מודל נפרד: רשימה + הוספה/מחיקה). שמור פשוט; אפשר כפתור
  "נהל מאפיינים" שפותח מודל.
- שימוש ב-`useToast` + `ConfirmDialog` + `messages` כמו ב-`ProfilesPage`.

## קבצים
1. **`frontend/admin/src/api/builderApiClient.js`** (עריכה) — הוסף:
   `listPositions(profileId)`, `createPosition(profileId, body)`, `getPosition(id)`,
   `updatePosition(id, body)`, `deletePosition(id)`,
   `listAttributes()`, `createAttribute(body)`, `updateAttribute(id, body)`, `deleteAttribute(id)`.
2. **`frontend/admin/src/pages/builder/PositionsPage.jsx`** (חדש) — המסך לעיל.
3. **`frontend/admin/src/App.jsx`** (עריכה) — route `/builder/positions`.
4. **`frontend/admin/src/components/Navbar.jsx`** (עריכה) — קישור "עמדות" בקבוצת "בונה הסידור".
5. **`frontend/admin/src/utils/messages.js`** (עריכה) — מחרוזות `positions.*` + `nav.positions`.
6. **`frontend/admin/src/styles/admin.css`** (עריכה) — סגנון לרשת הימים/כרטיסי עמדות/תגיות.

## טסטים (`tests/builderPositionsPage.test.jsx`, תבנית `builderProfilesPage.test.jsx`)
- טעינה: בורר פרופיל מאוכלס; רשימת עמדות מוצגת מקובצת לפי משמרת.
- יצירת עמדה: מילוי שם + סימון יום + שעות + דרישה → קריאה ל-`createPosition` עם `day_schedules`
  ו-`required_attributes` נכונים.
- מחיקה עם `ConfirmDialog`.
- (mock ל-`builderApiClient`).

## תיעוד + גרף (חובה לפי CLAUDE.md)
- **`APP_OVERVIEW.md`** — הוסף מודלים `Position`/`RequirementAttribute`, ה-endpoints החדשים,
  הדף `PositionsPage`, המיגרציות, שורה ב"היסטוריית שינויים משמעותיים", ועדכן "עדכון אחרון".
- **גרף:** `/home/yosef/.local/bin/code-review-graph update`.

## הרצה
- `cd frontend/admin && npx vitest run` — ירוק · `npm run build` — עובר.
- `python3 scripts/test_graph.py` — ריצה מלאה (backend+frontend) לפני קומיט סופי.

## קריטריון הצלחה (המשתמש מריץ ידנית)
מוסיף עמדה אמיתית (למשל "ארנונה", א'-ה', שעות פר-יום, דרישות) → עורך → מוחק → מרענן → נשמר נכון.
מוסיף עמדות מכל משמרת ורואה את כולן ברשימה. שכפול פרופיל מעתיק גם את העמדות.

## קומיט
```
feat(builder): positions management page (per-day hours + requirements)
```
push · עדכן `_PROGRESS.md` → הוסף שורת צעד 05 + שורת **"✅ All prompts completed"** · מחק קובץ פרומפט זה.
