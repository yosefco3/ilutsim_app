# 04 · מסך ניהול פרופילים (Frontend Admin)

**תלוי ב:** פרומפט 03 (API).

**מטרה:** מסך ניהול פשוט ונקי לפרופילי הפעלה — הכניסה הראשונה של המשתמש לחלק ב'.
זה גם הצעד שבו ההפרדה ב-UI מתממשת בפועל.

## API client — `frontend/admin/src/api/builderApiClient.js`

הרחב את ה-client שנוצר בפרומפט 00 בפונקציות פרופילים (reuse של ה-axios instance/אימות מ-adminApiClient):
`listProfiles()`, `createProfile(body)`, `getProfile(id)`, `updateProfile(id, body)`,
`duplicateProfile(id, body?)`, `deleteProfile(id)`.

## העמוד — `frontend/admin/src/pages/builder/ProfilesPage.jsx`

מסך RTL נקי בסגנון העמודים הקיימים (`WeeksPage.jsx` כרפרנס לסגנון/CSS/Toast):
- רשימת כרטיסי/שורות פרופיל: **שם**, תווית **סוג** (אם קיים), תיאור, תג "ברירת מחדל" ל-`is_default`.
- פעולות לכל פרופיל: **שכפל** · **שנה שם/ערוך** (שם+סוג+תיאור) · **מחק** (עם אישור).
- כפתור **"פרופיל חדש"** (שם חובה, סוג/תיאור אופציונליים).
- מצב ריק/טעינה/שגיאה; Toast להצלחה ולכישלון (כולל הודעת חסימת-מחיקה מהשרת).
- **שכפול:** לחיצה → קריאה ל-`duplicateProfile` → הפרופיל החדש ("... (עותק)") מופיע ברשימה,
  מוכן לעריכה. זה התרחיש המרכזי (שכפל "שגרה" → ערוך → פרופיל לחג).

> הערה: בשלב זה הפרופיל ריק מעמדות — אין עדיין תצוגת עמדות בעמוד. זה תקין; העמדות
> והגרירה ביניהן יגיעו במשימות 03/08. עצב כך שיהיה מקום להציג עמדות בעתיד (אזור/לשונית פנימית).

## ניווט והפרדת UI
- route: `/builder/profiles` ב-`App.jsx` (תחת `ProtectedRoute`).
- ב-Navbar: הוסף **קבוצת ניווט חדשה ומובחנת "בונה הסידור"** (כותרת/מפריד) עם הפריט "פרופילים".
  זו ההפרדה הוויזואלית בין חלק א' (הגשות/שומרים/שבועות/ייצוא/ייבוא) לחלק ב'. שמור על עיצוב
  עקבי עם הקיים — בחר את המימוש הנקי ביותר (קבוצה/כותרת-קטע) לשיקולך.
- מחרוזות עברית ל-`messages` אם יש קובץ מרכזי; אחרת inline עקבי עם הדף.

## טסטים
`frontend/admin/src/pages/builder/ProfilesPage.test.jsx` (vitest + RTL, בסגנון טסטי העמודים הקיימים):
- רינדור רשימה (mock client) — מציג "שגרה".
- שכפול קורא ל-`duplicateProfile` ומרענן.
- יצירה/עריכה/מחיקה קוראים ל-endpoints הנכונים; אישור-מחיקה מוצג.

## קבצים צפויים
`frontend/admin/src/api/builderApiClient.js`, `frontend/admin/src/pages/builder/ProfilesPage.jsx`,
`frontend/admin/src/App.jsx` (route), רכיב ה-Navbar (קבוצה חדשה),
`ProfilesPage.test.jsx` (+ css/messages לפי הצורך).

## קריטריון הצלחה (המשתמש מריץ — מסיים את משימה 02)
נכנס למסך → רואה **"שגרה"** → יוצר **"חג"** → משכפל ל**"חג שני"** → משנה שם → מוחק →
**מרענן את הדף → הכל נשמר ומשתקף נכון.**

## אחרי שהכל ירוק
- `python3 scripts/test_graph.py` (backend+frontend ירוקים).
- `code-review-graph update`.
- עדכן `APP_OVERVIEW.md`: מודל `ActivationProfile`, endpoints `/admin/builder/profiles`,
  מסך הפרופילים, ושורה בטבלת "היסטוריית שינויים משמעותיים".
- עדכן `_PROGRESS.md` של 02 והוסף "✅ All prompts completed".

## commit
`feat(builder): activation profiles management page`
