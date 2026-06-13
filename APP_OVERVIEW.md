# אילוצים — סיכום תפקוד האפליקציה

> **⚠️ מסמך זה מתעדכן בכל שינוי משמעותי באפליקציה.**
> אם הנך מוסיף/משנה פיצ'ר — עדכן גם כאן.
>
> עדכון אחרון: 13 יוני 2026 (⚠️ אישור פרסום בלתי-הפיך + 🕛 נעילה/רוטציה אוטומטית במוצ"ש 00:00)

---

## סקירה כללית

**אילוצים** היא מערכת לניהול משמרות שומרים. המערכת מאפשרת לאדמינים לנהל שומרים, לפתוח שבועות להגשה, ולשבץ משמרות. השומרים מגישים את הזמינות השבועית שלהם דרך **Telegram Web App**.

---

## ארכיטקטורה

```
┌─────────────────┐     ┌────────────────────────┐
│  Telegram Bot    │     │  Frontend (React+Vite) │
│  (aiogram)       │     │  :3001                 │
│  התראות לשומרים  │     │  אדמין + הגשת שומרים   │
└────────┬─────────┘     └───────────┬────────────┘
         │                           │
         │   ┌───────────────────────┘
         │   │  REST API
         ▼   ▼
┌──────────────────────────────┐
│  Backend (FastAPI)           │
│  - Controllers (REST)        │
│  - Services (Business Logic) │
│  - Repositories (Data Access)│
│  - Models (SQLAlchemy)       │
│  - Alembic Migrations        │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  PostgreSQL Database         │
└──────────────────────────────┘
```

### טכנולוגיות

| רכיב          | טכנולוגיה                          |
|---------------|-------------------------------------|
| Backend       | Python 3.12, FastAPI, SQLAlchemy    |
| Database      | PostgreSQL + Alembic migrations     |
| Telegram Bot  | aiogram 3.x                        |
| Frontend      | React 19 + Vite (אדמין + שומרים, port 3001) |
| Testing       | pytest (backend), Vitest (frontend) |
| Deployment    | Docker + docker-compose             |

---

## ממשק השומר (Frontend Web App + Telegram Bot)

### הגשת זמינות שבועית
- השומר נכנס דרך **Telegram Web App** (כפתור בבוט או קישור ישיר)
- מוצגת טופס עם **7 ימים × 3 משמרות** (בוקר, ערב, לילה)
- **ריבוי משמרות**: השומר יכול לסמן כל שילוב — בוקר, ערב, לילה — עם שעות מותאמות אישית לכל אחת
- ברירת מחדל: כל המשמרות כבויות ("אין משמרת" באותו יום)
- ההגשה נשמרת כ-`weekly_submission` במסד הנתונים
- **שמירה על סדר ימים**: ראשון → שבת (ישראל)

### אילוצי הגשה
- ניתן להגיש **רק כאשר השבוע במצב `open`**
- אם השבוע **נעול** (`locked`) או **סגור** (`closed`) — מוצגת הודעת נעילה
- הגשה כפולה מעדכנת את ההגשה הקיימת (upsert)
- **אזהרות רכות (לא חוסמות)** — אם הזמינות שסומנה חורגת מספי הכללים (מינימום משמרות/לילות/ערבים,
  מקסימום ימים רצוף — נקבעים ע"י האדמין בהגדרות), מוצג באנר אזהרה מעל כפתור השליחה. השליחה
  **עדיין מותרת** — האזהרה אינפורמטיבית בלבד. הספים נמשכים מ-`GET /submissions/constraint-rules`.

### Telegram Bot — התראות לשומרים
- **הודעת פתיחת שבוע** — נשלחת לכל השומרים הפעילים כשהאדמין פותח שבוע
- **תזכורת** — נשלחת לשומרים שטרם הגישו (מופעלת ידנית ע"י האדמין)
- **הודעת קבלה** — נשלחת לשומר לאחר הגשה מוצלחת
- **הודעת "האדמין מילא עבורך"** — נשלחת לשומר כשהאדמין ממלא/שולח עבורו את האילוצים (`POST /submissions/admin`), אם יש לו `telegram_id`
- **הודעת Welcome** — נשלחת לשומר חדש אם יש לו `telegram_id`
- אימות שומרים — שומר ששולח `/start` לבוט מזוהה לפי `telegram_id`

---

## ממשק האדמין (Frontend Admin Dashboard)

### דפי האדמין

| דף              | תיאור                                          |
|-----------------|-------------------------------------------------|
| **שבועות**       | ניהול מחזור חיי שבוע (פתיחה, נעילה, פרסום)      |
| **שומרים**       | ניהול שומרים — הוספה, עריכה, מחיקה, השבתה        |
| **הגשות**        | צפייה בהגשות שומרים לפי שבוע                     |
| **ייצוא**        | ייצוא נתונים ל-Excel                            |
| **הגדרות**       | הגדרות מערכת — ברירות-מחדל למשמרות, ספי כללי-אילוץ, ושדות placeholder לאוטומציה (טוקן טלגרם הוא env-only, לא נערך מכאן) |

### ניהול שומרים

- **הוספת שומר** — שם פרטי, שם משפחה, טלפון, תפקיד, `telegram_id` (אופציונלי)
- **עריכת שומר** — עדכון פרטים אישיים ותפקיד
- **השבתת שומר** — שינוי סטטוס ללא-פעיל (soft delete). השומר לא יקבל התראות
- **מחיקה קבועה** — מחיקת שומר לצמיתות ממסד הנתונים (hard delete)
- **מילוי / עריכת אילוצים ע"י האדמין** — כפתור "מילוי אילוצים" בכל שורה פותח דף `/guards/:id/constraints` שבו האדמין בוחר שבוע, מסמן משמרות (בוקר/ערב/לילה) עם שעות לכל יום, ושומר עבור **כל** מאבטח (גם כזה שאין לו טלגרם). נשמר כ-`weekly_submission` רגיל; מותר בכל סטטוס שבוע (`override_lock=True` — כולל **נעול** ו**פורסם**, בורר השבוע מציג את הסטטוס). **הגשה קיימת נטענת מראש לעריכה** — כולל הגשות שהמאבטח עצמו שלח דרך טלגרם — דרך `GET /submissions/admin?user_id=&week_id=`.

### תפקידי שומרים

| תפקיד         | קוד              |
|---------------|------------------|
| אחמ\"ש        | `AHMASH`         |
| שומר בסיסי    | `BASIC_GUARD`    |
| שלב ב'        | `LEVEL_B`        |
| 9 שעות        | `NINE_HOURS`     |
| לא חמוש       | `UNARMED`        |
| בודק          | `CHECKER`        |

### תפקידי אדמין

| תפקיד         | הרשאות                                    |
|---------------|-------------------------------------------|
| `super_admin` | גישה מלאה להכל + ניהול אדמינים           |
| `admin`       | ניהול שומרים, שבועות                      |
| `viewer`      | קריאה בלבד                                |

---

## מחזור חיי שבוע (Week Lifecycle)

```
┌─────────┐    אדמין פותח     ┌──────┐    אדמין נועל    ┌────────┐   אדמין מפרסם   ┌───────────┐
│ CLOSED  │ ───────────────▶ │ OPEN │ ──────────────▶ │ LOCKED │ ──────────────▶ │ PUBLISHED │
│ (סגור)  │                  │(פתוח)│                 │ (נעול) │                  │ (פורסם)   │
└─────────┘                  └──────┘                  └────────┘                   └───────────┘
                                  │                        │
                                  ▼                        ▼
                           שומרים מגישים            חישוב סטיות
                           זמינות שבועית             וסידור משמרות
```

| סטטוס       | משמעות                                       | מי יכול לשנות |
|-------------|-----------------------------------------------|---------------|
| `closed`    | שבוע חדש שנוצר, עדיין לא פתוח להגשה           | אדמין         |
| `open`      | פתוח להגשת זמינות — שומרים יכולים להגיש        | אדמין         |
| `locked`    | נעול — לא ניתן להגיש יותר. **הפיך** — האדמין יכול לפתוח שוב (`locked → open`) | אדמין |
| `published` | פורסם — הסידור הסופי הושלם. **סופי ובלתי-הפיך** — אי-אפשר לפתוח מחדש | אדמין / אוטומטי |

> **אישור פרסום (Frontend)**: לחיצה על "פרסם" מציגה דיאלוג אישור (`ConfirmDialog`) שמזהיר שהפעולה **בלתי-הפיכה**
> (בניגוד ל"נעל" שאותו אפשר לפתוח שוב) — למניעת התנגשויות. האכיפה האמיתית היא ב-backend: `ALLOWED_TRANSITIONS["published"] = []`
> (מכוסה ב-`test_published_to_open_rejected`).

### יצירת שבוע חדש
- **כל שבוע חדש נוצר בסטטוס `closed`** — בין אם ידנית (`create_week`), בזריעה (`ensure_initial_week`),
  ביצירה האוטומטית (`auto_rotate_weeks`), או אחרי פרסום (`_ensure_next_week`)
- האדמין מעביר אותו ל-`open` ידנית כשהוא מוכן — מה ששולח התראת פתיחה לכל השומרים

### רוטציה אוטומטית של שבועות
- **מתי**: בכל טעינה של דף השבועות (`GET /admin/weeks`), בעליית השרת, ובטריגר מתוזמן כל **מוצאי שבת (ראשון 00:00, שעון ישראל)**
- **מה קורה** (`WeekService.auto_advance_weeks` — אידמפוטנטי, מרפא-עצמי):
  1. **נעילה אוטומטית של השבוע הפעיל** — כל שבוע במצב `open` שה-`start_date` שלו כבר הגיע (`start_date <= today`)
     ננעל אוטומטית (`open → locked`), כי שבוע פתוח אמור תמיד להיות **עתידי** ושבוע שכבר התחיל אינו רלוונטי להגשה.
     הנעילה **שקטה** (`notify=False`) — אין ברודקאסט טלגרם בחצות; נעילה ידנית של האדמין כן מתריעה כרגיל.
  2. **יצירת השבוע הבא** — אם עדיין לא קיים שבוע לטווח הקרוב (ראשון–שבת) → נוצר במצב **`closed`**
     (לפי טווח תאריכים, כך שאין כפילות מול `_ensure_next_week`), ומופיע כשבוע הבא שהאדמין יכול לפתוח.
- **תזמון** (`app/scheduler.py`, APScheduler): `AsyncIOScheduler` עם cron שבועי `sun 00:00` ב-`SCHEDULER_TIMEZONE`
  (ברירת מחדל `Asia/Jerusalem`, מטפל ב-DST). ניתן לכבות עם `AUTO_ROLLOVER_ENABLED=false`. בעליית השרת רצה
  **השלמה חד-פעמית** (catch-up) של אותו רולאובר — מכסה שרת שהיה כבוי בחצות מוצ"ש.
- **"לא משנה מה יקרה"**: גם אם האדמין לא נעל/פרסם ידנית — מרגע שנכנס השבוע, הוא ננעל אוטומטית. אם האדמין כן
  פעל ידנית — הכלל לא משנה כלום (אין שבוע פתוח שהתחיל). השבועות הישנים נשארים ברשימה כהיסטוריה.
- **מחיקת שבוע**: אפשרית רק לשבועות שלא פורסמו (שומר היסטוריה); כפתור המחיקה מוסתר לשבוע שפורסם

---

## ייצוא נתונים

- **ייצוא אילוצים (Excel)** — דף "ייצוא" מייצר קובץ Excel מעוצב (RTL) של **כל מי ששלח אילוצים** לשבוע נבחר
- שורה לכל שומר שהגיש: שם, טלפון, זמינות לכל יום (ראשון–שבת) עם **שעות המשמרות בפועל** (`בוקר 06:00–14:00`), והערות כלליות
- ימים ללא זמינות מסומנים "לא זמין"; השורות ממוינות לפי שם
- Endpoint: `GET /admin/export/constraints/{week_id}` → `export_constraints_report` ב-`ExcelExportService`
- קיימים גם דוחות נוספים ב-`ExcelExportService`: גריד שבועי, דוח חריגות, היסטוריית שומר

---

## מודלים עיקריים (Database Models)

| מודל                | תיאור                                    |
|---------------------|-------------------------------------------|
| `User`              | שומרים — שם, טלפון, telegram_id, תפקיד, סטטוס |
| `Admin`             | אדמינים — שם משתמש, סיסמה (hashed), תפקיד |
| `ScheduleWeek`      | שבוע לוח — תאריך התחלה, סטטוס             |
| `WeeklySubmission`  | הגשה שבועית — שומר + שבוע + סטטוס הגשה   |
| `DailyStatus`       | סטטוס יומי — משמרת + זמינות + סוג פטור   |
| `ShiftWindow`       | חלונות משמרות — הגדרות שעות              |
| `SystemSetting`     | הגדרות מערכת — key/value                  |

---

## מיגרציות (Alembic)

- `e070f2f048c6` — יצירת טבלאות ראשוניות
- `68d1f37c2543` — פיצול `full_name` ל-`first_name` + `last_name`
- `a1b2c3d4e5f6` — הוספת `CLOSED` ל-enum `week_status` ב-PostgreSQL

---

## 🎨 Design System (`design-system/`)

מערכת עיצוב ממותגת מלאה של האפליקציה, שנבנתה מקריאת קוד ה-`frontend` האמיתי. נמצאת בתיקייה
`design-system/` בשורש הריפו (תחת version control). מיועדת לשמש כ**מקור אמת לעיצוב** לכל מסך/פיצ'ר
עתידי, וכן כבסיס מוכן למימוש שלב **בונה הסידור** (ראו "תכנון לעתיד" למטה).

| תיקייה / קובץ                       | תוכן                                                                 |
|-------------------------------------|----------------------------------------------------------------------|
| `tokens/*.css` + `styles.css`       | טוקני עיצוב (צבעים, טיפוגרפיה, מרווחים, פונט Heebo) — תואמים ל-`admin.css` החי |
| `components/**`                     | קומפוננטות React (Button, Badge, Card, Alert, Field, inputs, Toast, Dialog) + `.prompt.md` לכל אחת |
| `ui_kits/admin/**`, `ui_kits/guard/**` | שחזור אינטראקטיבי של מסכי האדמין (כהה-אינדיגו) ואזור המאבטח (טלגרם בהיר) |
| `concepts/schedule-builder/**`      | **קונספט עובד של בונה הסידור** (drag & drop) — ראו "תכנון לעתיד"      |
| `SKILL.md` (`ilutsim-design`)       | ניתן להתקנה כ-skill של Claude לעבודת עיצוב ממותגת                     |
| `README.md`                         | הקשר מוצר, יסודות תוכן, יסודות חזותיים, אייקונוגרפיה (אמוג'י)         |

---

## 🔭 תכנון לעתיד — בונה הסידור (Schedule Builder)

> השלב הבא המתוכנן, כמתואר ב-`מערכת_ניהול_משמרות_סקירה_ותכנון.pdf` ו-`SCHEDULING_FOR_MANAGERS.md`.
> **עדיין לא נבנה כפיצ'ר אמיתי** — אבל קיים **קונספט frontend עובד** ב-`design-system/concepts/schedule-builder/`.
> **כשמגיעים לשלב הזה — מתחילים מהקונספט, לא בונים מאפס.**

היום המערכת **אוספת זמינות** בלבד (כל מאבטח מדווח שעות פנויות). מה שחסר הוא **הסידור עצמו** — שיבוץ
כל מאבטח לעמדה מסוימת, ביום מסוים, בשעות מסוימות, על בסיס הזמינות שנאספה.

### שלושת החלקים המתוכננים (מה-PDF)
1. **פרופילי הפעלה** (שגרה / חג / אירוע) — אוסף עמדות + שעות שמשתנה לפי סוג השבוע.
2. **עמדות** — `עמדה = דרישה למאבטח אחד` (שורה בסידור: חמ"ל, סייר 1, ארנונה…). לכל עמדה: ימים/שעות
   פעילות + מאפיינים נדרשים (חמוש, רוני, רכב עירייה, הליכה מרובה).
3. **בניית הסידור** — לוח עמדות × ימים, גרירת מאבטחים לתאים, מיון אוטומטי לפי שעות פנויות,
   **אזהרות רכות לא-חוסמות** (חריגה מזמינות / שיבוץ כפול / חוסר מאפיין), ייצוא לאקסל.

### מה כבר קיים בקונספט (`design-system/concepts/schedule-builder/`)
- `index.html` — לוח עמדות×ימים, טאבי בוקר/ערב/לילה, רשימת מאבטחים ממוינת לפי שעות פנויות עם מד תקציב,
  שתי זרימות עבודה: בחירת מאבטח → צביעת זמינות, **או** לחיצה על תא ריק → רשימת מועמדים זמינים.
- `logic.js` — לוגיקת שיבוץ טהורה: חישוב כיסוי שעות (כולל לילה החוצה חצות), תקציב שבועי,
  ואזהרות רכות (מחוץ-לזמינות / חלקי / שיבוץ-כפול / חוסר-מאפיין). מיישם את עקרון "מזהיר ולא חוסם".
- `data.js` — נתוני דמו (עמדות/מאבטחים/ימים) מבוססי "סידור עבודה שבועי" אמיתי.

### הפער למימוש אמיתי (Backend + חיבור)
הקונספט הוא frontend עם נתוני דמו. למימוש פיצ'ר אמיתי נדרש:
- מודלים ל**עמדות** ול**פרופילי הפעלה** (positions / activation profiles) + מיגרציות.
- חיבור ל**זמינויות האמיתיות** (`WeeklySubmission` / `DailyStatus`) במקום `data.js`.
- **שמירת הסידור** (assignment של מאבטח↔עמדה↔יום) ו-endpoints ל-CRUD.
- **ייצוא הסידור לאקסל** (להרחיב את `ExcelExportService`).
- שילוב במחזור חיי השבוע — בניית הסידור שייכת לשלב `locked` → `published`.

---

## מבנה תיקיות

```
ilutzim_app/
├── backend/
│   ├── app/
│   │   ├── controllers/    # REST API endpoints
│   │   ├── services/       # Business logic
│   │   ├── repositories/   # Database access
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── bot/            # Telegram bot (aiogram)
│   │   │   ├── handlers/   # Bot command handlers
│   │   │   ├── keyboards/  # Inline keyboards
│   │   │   └── middlewares/ # Auth middleware
│   │   ├── utils/          # Utilities (date_utils, telegram_auth)
│   │   └── config.py       # Settings & env vars
│   ├── alembic/            # Database migrations
│   └── tests/              # pytest tests
├── frontend/
│   └── admin/              # אפליקציה מאוחדת — אדמינים + שומרים
│       └── src/
│           ├── pages/      # WeeksPage, GuardsPage, SubmitPage, etc.
│           ├── components/ # GuardTable, WeekStatusControl, etc.
│           │   └── guard/  # LockBanner, DayRow, SubmissionForm (ממשק שומר)
│           ├── hooks/      # useWeeks, useGuards, useSettings, useTelegram, useSubmission
│           └── api/        # adminApiClient, guardApiClient
├── design-system/         # 🎨 מערכת עיצוב ממותגת + קונספט בונה הסידור (ראו סקשן Design System)
│   ├── tokens/, components/, ui_kits/   # טוקנים, קומפוננטות, ערכות מסכים
│   └── concepts/schedule-builder/        # קונספט עובד של בונה הסידור (frontend בלבד)
├── docker-compose.yml
├── SETUP.md               # הוראות התקנה והרצה
├── מערכת_ניהול_משמרות_סקירה_ותכנון.pdf  # מסמך תכנון בונה הסידור (לעתיד)
└── APP_OVERVIEW.md         # ** המסמך הזה **
```

---

## CORS & אבטחה

- **Origin יחיד ב-production**: `APP_URL` (למשל `https://app.safrasecure.uk`)
- **ב-dev**: נוסף `http://localhost:3001` אוטומטית
- **ללא wildcard** — `allow_origins` לעולם לא `*`
- **`allow_credentials=True`** — תומך ב-cookies / Authorization headers

### הרשאות גישה (Authorization)

- **אדמין** — כל `/admin/*` מוגן ברמת ה-router ב-`Depends(require_admin_role)`: דורש JWT חתום (HS256) + תפקיד `admin`/`super_admin`. ניהול אדמינים דורש `require_super_admin`.
- **שומר** — מילוי/קריאת אילוצים (`POST /submissions`, `GET /submissions/my`) דורש `get_current_user`: אימות Telegram WebApp `init_data` ב-HMAC-SHA256 + השומר חייב להתקיים ב-DB לפי `telegram_id`.
- **בקרת רעננות (replay protection)** — `init_data` עם `auth_date` ישן מ-24 שעות נדחה גם אם ה-HMAC תקין (`telegram_auth.py`, `DEFAULT_MAX_AGE_SECONDS`).
- **`__DEV_MODE__`** — עקיפת אימות השומר פעילה **רק** כש-`ENVIRONMENT == "dev"`; בכל סביבה אחרת היא נדחית כ-401 (אין דלת אחורית בפרודקשן).
- **קריאות הגשות מרובות** (`GET /submissions/week/{id}`, `GET /submissions/user/{id}`) — **אדמין בלבד** (`require_admin_role`), מונע דליפת זמינות שומרים ו-IDOR.

---

## API Endpoints (עיקריים)

### שומרים (Guard Web App)
| Method | Path                      | תיאור                     |
|--------|---------------------------|---------------------------|
| GET    | `/api/submissions/current`| קבלת הגשה נוכחית          |
| POST   | `/api/submissions`        | הגשת/עדכון זמינות         |
| GET    | `/api/submissions/admin`  | **אדמין** קורא הגשה קיימת של מאבטח לשבוע (לעריכה) |
| POST   | `/api/submissions/admin`  | **אדמין** ממלא אילוצים עבור מאבטח (override_lock) |
| GET    | `/api/submissions/constraint-rules` | ספי כללי-אילוץ לטופס (אזהרות רכות) — ציבורי |

### אדמין
| Method | Path                      | תיאור                     |
|--------|---------------------------|---------------------------|
| GET    | `/admin/weeks`            | רשימת שבועות              |
| POST   | `/admin/weeks/{id}/open`  | פתיחת שבוע                |
| POST   | `/admin/weeks/{id}/lock`  | נעילת שבוע                |
| POST   | `/admin/weeks/{id}/publish`| פרסום שבוע               |
| GET    | `/admin/users`            | רשימת שומרים              |
| POST   | `/admin/users`            | הוספת שומר                |
| PATCH  | `/admin/users/{id}`       | עדכון שומר                |
| DELETE | `/admin/users/{id}`       | **מחיקה קבועה** של שומר    |
| DELETE | `/admin/weeks/{id}`       | **מחיקת שבוע** (לא פורסם)  |
| GET    | `/admin/submissions`      | רשימת הגשות               |
| GET    | `/admin/export/constraints/{week_id}` | ייצוא אילוצים ל-Excel |
| GET    | `/admin/settings`         | הגדרות מערכת (רשימת `{key,value,description}`) |
| PUT    | `/admin/settings`         | עדכון הגדרות (`{settings:{k:v}}`)  |

---

## היסטוריית שינויים משמעותיים

| תאריך     | שינוי                                                |
|-----------|-------------------------------------------------------|
| 13 יוני 2026 | ⚠️ **אישור פרסום בלתי-הפיך** — למניעת התנגשויות, לחיצה על "פרסם" ב-`WeekStatusControl` מציגה כעת `ConfirmDialog` שמזהיר שלאחר פרסום **אי-אפשר לפתוח את השבוע מחדש** (סטטוס סופי), בניגוד ל"נעל" שאותו אפשר לפתוח שוב. הפרסום מתבצע רק לאחר אישור ("כן, פרסם"). זוהי שכבת-UX בלבד — **האכיפה כבר קיימת ב-backend** (`ALLOWED_TRANSITIONS["published"] = []`, מכוסה ב-`test_published_to_open_rejected`); המחיקה כבר השתמשה באותו דיאלוג. נוספו מחרוזות `publishConfirm*` ב-`messages.js` ו-3 טסטים ל-`weekStatusControl.test.jsx` (לא מפרסם בלחיצה ישירה / מפרסם אחרי אישור / ביטול לא מפרסם); frontend 115 (0 כשלים). |
| 13 יוני 2026 | 🕛 **נעילה + רוטציה אוטומטית של שבוע במוצאי שבת (ראשון 00:00, שעון ישראל)** — עד כה מחזור חיי השבוע היה ידני לגמרי (אין scheduler פעיל; `apscheduler` היה ב-requirements אך לא מחובר, `bot/cron.py` placeholder). כעת, **לא משנה אם האדמין נעל/פרסם** — מרגע שנכנס השבוע הפעיל (`start_date` הגיע) הוא **ננעל אוטומטית להגשה** (`open → locked`) כי הוא כבר לא רלוונטי, והשבוע הבא מופיע כ-`closed` שהאדמין יכול לפתוח. מימוש: (1) `ScheduleWeekRepository.get_open_weeks_started_on_or_before(today)` — שבועות `open` עם `start_date <= today`. (2) `WeekService.lock_expired_open_weeks` (נעילה **שקטה**, `notify=False` — אין ברודקאסט טלגרם בחצות) + `auto_advance_weeks` (=נעילה + `auto_rotate_weeks` הקיים); `change_week_status` קיבל פרמטר `notify`. (3) `app/scheduler.py` — `AsyncIOScheduler` (APScheduler) עם cron שבועי `sun 00:00` ב-`SCHEDULER_TIMEZONE` (ברירת מחדל `Asia/Jerusalem`, מטפל ב-DST), מחובר ב-`main.py` lifespan עם **השלמה חד-פעמית בעלייה** (catch-up לשרת שהיה כבוי) וכיבוי ב-shutdown. (4) config: `AUTO_ROLLOVER_ENABLED` + `SCHEDULER_TIMEZONE`. הלוגיקה **אידמפוטנטית ומרפאת-עצמה** — רצה גם בכל טעינת `GET /admin/weeks`, כך שריצה שהוחמצה מתוקנת מיד. כיסוי: 8 טסטים חדשים (`test_auto_advance.py` service+repo+DB מלא, `test_scheduler.py` תצורת job+disabled+delegation); backend 203 (0 כשלים). |
| 13 יוני 2026 | 🔔 **כפתור תזכורת + הפרדת מאבטחים פעילים/לא-פעילים בדף הדיווחים** — (1) **כפתור "שלח תזכורת"** ב-`SubmissionsPage` שמפעיל את `POST /admin/notifications/remind/{week_id}` ושולח תזכורת טלגרם (`notify_closing_reminder`) **רק למאבטחים פעילים שטרם הגישו** ויש להם `telegram_id`. ה-endpoint היה שבור — קרא למתודות לא-קיימות (`WeekService.get_by_id`, `UserService.get_active_users`, `SubmissionService.get_user_submission`) ולשדות שבוע לא-קיימים → `AttributeError` בלחיצה; תוקן מול ה-API האמיתי (`get_week`/`get_all_active_users`/`get_submission`) עם גישת Pydantic ו-`int(telegram_id)`. אותו באג `get_by_id` תוקן גם ב-endpoint של `publish`. הכפתור מוצג בסרגל-פעולה בגוון אזהרה עם מונה "כמה טרם הגישו". (2) **הפרדת פעילים/לא-פעילים** — `get_week_submissions_grid` ו-`get_week_submissions_detailed` עברו מ-`get_active_users` ל-`get_all_users`, ו-`SubmissionStatusGrid` קיבל שדה `is_active`. הדף מציג כברירת-מחדל **רק מאבטחים פעילים**, עם כפתור מתקפל "הצג מאבטחים לא פעילים (N)" לרשימה נפרדת. מונה התזכורת סופר רק פעילים. כיסוי: 2 טסטים חדשים (endpoint תזכורת מאומת ב-`test_controllers.py`, גריד כולל לא-פעילים ב-`test_submission_persistence.py`); backend 195, frontend 112 (0 כשלים). |
| 13 יוני 2026 | 📨 **התראת טלגרם כשהאדמין ממלא אילוצים עבור מאבטח** — כשהאדמין שולח אילוצים בשם מאבטח (`POST /submissions/admin`) ולמאבטח יש `telegram_id`, הוא מקבל כעת הודעת טלגרם "📝 האדמין מילא עבורך את האילוצים" (פונקציה חדשה `notify_admin_filled_constraints` ב-`bot/notifications.py`, מקבילה ל-`notify_submission_success`). הקונטרולר טוען את המאבטח דרך `get_user_service` ושולח לאחר שמירה מוצלחת; ההתראה **לא-קריטית** — כשל בשליחה נרשם ללוג בלבד ולא מפיל את ה-201. **אישור התנהגות קיימת:** טפסי האילוצים (`useSubmission`/`useAdminConstraints`) שומרים הכל ב-React state בלבד — **אין** localStorage/אוטו-שמירה/טיוטה, ושום דבר לא נכתב ל-DB עד לחיצת "שלח". כיסוי: 3 טסטים חדשים ב-`test_admin_submission.py` (מתריע עם טלגרם / מדלג בלעדיו / כשל לא מפיל הגשה); backend 193 (0 כשלים). |
| 13 יוני 2026 | 🗑️ **הסרת פיצ'ר האירועים (Events) — אדמין + באקאנד** — הפיצ'ר לא היה בשימוש. **Frontend:** הוסרו הראוט `/events`, הקישור ב-`Navbar`, `EventsPage`, `EventForm`, פונקציות ה-API (`fetchEvents/createEvent/updateEvent/deleteEvent`) ומחרוזות `events` ב-`messages.js`. **Backend:** נמחקו `admin_events_controller`, `event_service`, מודל `ScheduleEvent`, `event_schemas`, `schedule_event_repository`; נוקו הרישומים (`controllers/services/repositories/models __init__`), `dependencies.py` (`get_event_service`/`_get_event_repo`), רישום ה-router ב-`main.py`, יחס `User.schedule_events`, ה-enum `EventType` וההודעות `EVENT_*`. **ייצוא Excel:** הוסרה תצוגת האירועים מ-`export_weekly_schedule` ומ-`export_guard_history` (לא ניתן היה ליצור אירועים יותר → קוד מת). **DB:** טבלת `schedule_events` נשארת ב-DB/מיגרציה (לא הוסרה — להימנע מסיכון מיגרציה; אין לה יותר מודל). כיסוי: backend 190, frontend 111 (0 כשלים). |
| 13 יוני 2026 | 🅷 **פונט Heebo בצד האדמין** — האפליקציה רינדרה עברית בפונט מערכת (`'Segoe UI', Tahoma`), שלא קיים בלינוקס/אנדרואיד וגרם לרינדור לא-עקבי בין מכשירים. אומץ **Heebo** (Google Fonts, מהמלצת ה-Design System) לרינדור עברי נקי ועקבי בכל מכשיר: `<link>` עם preconnect ב-`frontend/admin/index.html`, ושורת `font-family` ב-`admin.css` (`'Heebo'` בראש ה-stack, עם נפילה ל-Segoe UI). **צד המאבטח (`guard.css`) נשאר על ה-stack הנייטיב של טלגרם** — כך קובע ה-Design System (צד המאבטח עוקב אחרי theme הטלגרם). שינוי ויזואלי בלבד; 112 טסטי frontend עוברים. |
| 13 יוני 2026 | 🎨 **תיעוד Design System + תכנון בונה הסידור** — ידיד מסר Design System ממותג מלא של האפליקציה (טוקנים, קומפוננטות React, ערכות מסכים, `SKILL.md`), ובתוכו **קונספט frontend עובד של בונה הסידור (drag & drop)** — בדיוק השלב הבא המתואר ב-`מערכת_ניהול_משמרות_סקירה_ותכנון.pdf`. החבילה חולצה לריפו ב-`design-system/` (תחת version control, במקום ZIP זמני). נוספו ל-APP_OVERVIEW שני סקשנים: **🎨 Design System** (מיפוי כל הנכסים) ו-**🔭 תכנון לעתיד — בונה הסידור** (שלושת החלקים מה-PDF, מה כבר קיים בקונספט, והפער ל-backend/חיבור). מטרה: כשנגיע לשלב — להתחיל מהקונספט, לא לבנות מאפס. שינוי תיעודי בלבד (אין קוד מקור). |
| 13 יוני 2026 | 📊 **קו עבה בין מאבטחים בדוח אילוצים Excel** — בדוח האילוצים (`export_constraints_report`) כל מאבטח תופס שלוש שורות (בוקר/ערב/לילה), והיה קשה להבחין היכן מסתיים מאבטח אחד ומתחיל הבא. נוסף **קו תחתון עבה** (`Side(style="thick")`, קבוע `_GUARD_SEPARATOR_SIDE`) בתחתית כל בלוק-מאבטח. לתאי-רגיל מצויר ע"י `_draw_guard_separator`; לתאים ממוזגים (שם/טלפון/הערות/"לא זמין"/"זמין") `_merge_vertical` קיבל פרמטר `thick_bottom` ומציב את הקו על **תא העוגן (top-left)** של המיזוג — כי openpyxl גוזר את גבולות-החוץ של טווח ממוזג מתא העוגן (הצבה ישירה על תא ה-MergedCell התחתון נדרסת בשמירה). גם הקובץ-לדוגמה `דוגמה_אילוצים_מאבטחים.xlsx` נוצר מחדש כך, באמצעות `scripts/generate_constraints_example.py`. כיסוי: `test_constraints_excel_has_thick_separator_between_guards`. |
| 13 יוני 2026 | 🔑 **טוקן טלגרם הפך ל-env-only** — בעבר ניתן היה לעדכן את טוקן הבוט מדף ההגדרות (נשמר ב-DB + ולידציית `getMe` + אתחול בוט חי). לפי בקשת המשתמש הטוקן מגיע כעת **אך ורק** ממשתנה הסביבה `TELEGRAM_BOT_TOKEN`: (1) `get_effective_bot_token` קורא ישירות מ-env (ללא DB); הוסר `telegram_bot_token` מ-`SETTINGS_DEFAULTS`. (2) הוסר `POST /admin/settings/telegram/apply` + מודל `TelegramTokenApply`. (3) הוסר קוד ה-hot-swap המת (`rebuild_bot`, `restart_bot_with_token`). (4) מיגרציה `b2c3d4e5f6a7` מוחקת את שורת הטוקן מ-`system_settings` (ניקוי סוד). (5) Frontend: הוסר סקשן הטלגרם מ-`SettingsPage`, `applyTelegramToken`, ובלוק ההודעות. עדכון טוקן מצריך כעת restart לשרת. כיסוי: backend 23, frontend 21 קבצי-טסט (0 כשלים). |
| 12 יוני 2026 | 🎛️ **פירוט אילוצים פר-מאבטח בדף הדיווחים** — עד כה בדף `/submissions` היה כפתור יחיד "צפה בפירוט" שניווט לעמוד נפרד (`/submissions/:weekId`) שפתח את כל המאבטחים ביחד. כעת `SubmissionsPage` טוען נתונים מפורטים (`useSubmissions(week, {detailed:true})`) ובונה מפת `detailsByUser`; ל-`StatusGrid` נוספה עמודת "צפה בפירוט" עם כפתור הצג/הסתר **בשורה של כל מאבטח** שהגיש — מרחיב אינליין את הזמינות/משמרות/הערות שלו בלבד. הקישור היחיד הישן הוסר. עמוד הפירוט המלא והראוט נשארו זמינים. |
| 12 יוני 2026 | ⚙️ **דף הגדרות + ספי כללי-אילוץ + אזהרות רכות + טוקן טלגרם חי** (ספריית פרומפטים `settings_and_constraint_rules`, 9 צעדים): (1) **דף ההגדרות היה שבור מקצה-לקצה** — ה-service קרא למתודות repo לא-קיימות (`get_all`/`upsert`/`get_by_key`) ולשדות (`row.key/value`), הקונטרולר קרא ל-`get_settings`/`update_settings` שלא היו, והסכמה הייתה הגדרה-בודדת → כל `/admin/settings` נתן 500. יושר לחוזה `[{key,value,description}]` + `PUT {settings:{k:v}}`; הפרונט (`useSettings` עם draft, `SettingsPage` עם תוויות עברית + שמירה) שוקם. (2) **ספי כללי-אילוץ** (`min_shifts_per_guard=5`, `min_nights=2`, `min_evenings=2`, `max_consecutive_days=6`) נוספו כהגדרות + `GET /submissions/constraint-rules`. (3) **אזהרות רכות בטופס השומר** — `useSubmission.computeWarnings` מציג באנר כשהזמינות חורגת מהספים (afternoon=ערב, ימים-רצוף=רצף זמינות), אך **לא חוסם** שליחה. (4) **טוקן טלגרם עם החלה חיה** — `get_effective_bot_token` (DB→env) שנתיבי ה-auth קוראים per-request (תוקף מיידי), ו-`POST /admin/settings/telegram/apply` שמאמת `getMe` לפני שנוגע בבוט, שומר ל-DB ומאתחל את הבוט (`rebuild_bot`+`restart_bot_with_token`) בלי restart לשרת; כפתור "החל טוקן" בדף. (5) שדות placeholder `auto_open_*`/`auto_lock_*` (ללא scheduler). כיסוי: backend 201 טסטים, frontend 110 טסטים. |
| 12 יוני 2026 | 🐛 **תיקון טעינת-מראש + עריכת הגשה ע"י אדמין** — (1) טעינת ההגשה הקיימת לדף מילוי-האדמין הסתמכה על `GET /submissions/user/{id}` שקרא ל-`get_submissions_for_user` **שלא קיים** ב-`SubmissionService` (500), כך שהטעינה-מראש נבלעה בשקט ואף פעם לא עבדה. נוסף `GET /submissions/admin?user_id=&week_id=` (`require_admin_role`) המחזיר את ההגשה היחידה דרך `get_submission` הקיים — כעת האדמין רואה ועורך את מה שכבר הוגש, **כולל הגשות טלגרם של המאבטח עצמו**. (2) הובהר ש-`override_lock` מאפשר עריכה בכל סטטוס — בורר השבוע מציג את הסטטוס (פתוח/סגור/נעול/פורסם) עם רמז שניתן לערוך תמיד. API client: `fetchUserSubmissions`→`fetchGuardSubmission`. (3) לאחר שמירה מוצלחת הדף נותן `alert` אישור וחוזר ל-`/guards` (לפני כן באנר ההצלחה היה ממוקם מחוץ ל-`.guard-layout` ולכן לא היה מעוצב/נראה — נראה כאילו "לא נסגר"); באנר השגיאה הועבר פנימה. כיסוי: backend 187, frontend 95. |
| 12 יוני 2026 | 👤 **מילוי אילוצים ע"י אדמין עבור מאבטח ללא טלגרם** — לא לכל מאבטח יש טלגרם, אז נוסף לאדמין כלי למלא עבורו. כפתור "מילוי אילוצים" בכל שורה ב-`GuardTable` → דף חדש `/guards/:guardId/constraints` (`AdminConstraintsPage` + hook `useAdminConstraints`, ממחזר את `DayRow`+`guard.css` מצד השומר): בורר שבוע, 7 ימים × 3 משמרות עם שעות, טעינת-מראש של הגשה קיימת, שמירה. Backend: `POST /submissions/admin` (`require_admin_role`, `AdminSubmissionRequest`=שומר+`user_id`) ממחזר את `_convert_guard_request` וקורא ל-`create_submission(override_lock=True)` — מותר בכל סטטוס שבוע. API client: `createGuardSubmission`+`fetchUserSubmissions`. כיסוי: backend 185 (+`test_admin_submission.py`), frontend 94 (+`useAdminConstraints.test.js`). |
| 12 יוני 2026 | 🔒 **הקשחת אבטחה (3 חורים)**: (1) **דלת אחורית `__DEV_MODE__`** ב-`get_current_user` הייתה ללא תנאי — כל זר יכול היה להגיש אילוצים בהתחזות לשומר הראשון; כעת מגודרת ל-`ENVIRONMENT == "dev"` בלבד, אחרת 401. (2) `GET /submissions/week/{id}` ו-`/user/{id}` היו **ללא אימות** וחשפו את כל זמינות השומרים (כולל IDOR); נוסף `Depends(require_admin_role)`. (3) `validate_telegram_web_app_data` לא בדק `auth_date` — `init_data` שנדלף היה תקף לנצח; נוספה תפוגת 24 שעות (`DEFAULT_MAX_AGE_SECONDS`). נוסף `test_telegram_auth.py` + טסטי חסימה ב-`test_submission_guard.py`. כיסוי backend: 183. |
| 12 יוני 2026 | 🐛 **תיקון Workflow מחזור חיי שבוע** (ספריית פרומפטים `week_workflow_fixes`, 6 צעדים): (1) כל יצירת שבוע → `closed` (`create_week`/`seed` היו `open`/`locked`); (2) `auto_rotate_weeks` יוצר שבוע קרוב `closed` בלבד לפי טווח (היה `open`), והוסר פרסום-בשקט של שבועות שפגו + באג כפילות מול `_ensure_next_week`; (3) `GET /submissions/current-week` מחזיר את השבוע הרלוונטי גם כשנעול/סגור/פורסם (`get_relevant_week_with_days`, fallback תלת-שלבי: שבוע פתוח → השבוע הנוכחי שטרם הסתיים `get_current_or_upcoming_week` → השבוע האחרון) — השומר רואה באנר מצב מדויק (נעול נוכחי גובר על שבוע-הבא הסגור) במקום "אין שבוע"; (4) שומר חדש בזמן שבוע פתוח מקבל התראת פתיחה עם כפתור + תיקון באג welcome כפול; (5) הוסר נתיב הפתיחה הכפול `POST /admin/weeks/open` — נותר `{id}/open` יחיד; (6) ליטוש UI: הסתרת "מחק" לשבוע שפורסם, הסרת `draft` מת, באדג' `closed` ניטרלי. כיסוי: backend 171, frontend 91. |
| 8 יוני 2026 | ✅ **רוטציה אוטומטית + מחיקת שבועות + תיקון enum** — `auto_rotate_weeks()` בכל טעינה, `DELETE /admin/weeks/{id}`, הוספת `CLOSED` ל-enum ב-DB, תיקון `useWeeks` rename bug |
| יוני 2026 | ✅ **מחיקה קבופה של שומרים** — endpoint `DELETE /admin/users/{id}` |
| יוני 2026 | ✅ **הסרת Cron Job** — ניהול שבועות ידני ע"י האדמין בלבד     |
| יוני 2026 | פיצול `full_name` ל-`first_name` + `last_name` (מיגרציה)  |
| יוני 2026 | הוספת מחזור חיי שבוע (closed → open → locked → published) |
| יוני 2026 | הוספת Telegram Bot עם התראות                            |
| יוני 2026 | הוספת ניהול אירועים וייצוא Excel                       |
| 8 יוני 2026 | **איחוד Frontends** — מעבר לאפליקציה מאוחדת (admin :3001) — דף `/submit` ציבורי לשומרים, `guardApiClient` לטלגרם Auth, קומפוננטות guard בתוך admin |
| 8 יוני 2026 | **איחוד CORS** — החלפת `WEBAPP_URL`+`ADMIN_DASHBOARD_URL` ב-`APP_URL` יחיד + `cors_origins` property |
| 8 יוני 2026 | **מחיקת webapp** — מחיקת `frontend/webapp/` סופית. אפליקציה אחת בלבד (`frontend/admin/`) עם אזור שומרים (`/submit`) + אדמינים (`/guards`). ניקוי `dev.sh`, `dev-stop.sh`, `test_graph.py` משירות webapp. |
| 8 יוני 2026 | **תיקון קישורים ל-/submit** — הוספת `/submit` ב-`notify_week_opened()`, תיקון cloudflared tunnel מ-port 5173 ל-3001, הוספת `allowedHosts` ב-vite.config.js, תיקון `webapp_url` בכפתור Telegram Web App ב-core.py |
| 8 יוני 2026 | 🐛 **תיקון "שבוע undefined"** — תוקן באג בדף ההגשה: `week_label` נוסף כ-property ב-`WeekResponse`, הוסרה קריאת API מיותרת ל-`/weeks/current` (נתיב שלא קיים), תוקן `week_id`←`id` ב-`useSubmission.js` ו-`SubmissionForm.jsx` |
| 8 יוני 2026 | ✅ **ריבוי משמרות בטופס ההגשה** — שומר יכול לסמן בוקר+ערב+לילה במקביל (במקום בורר יחיד). צהריים→ערב. הסרת כפתורי אירועים (חופשה/מילואים/רענון). נוסף `GET /submissions/my` + `GuardSubmissionRequest` + `get_current_user` dependency ל-Telegram auth. |
| 8 יוני 2026 | ✅ **שעות ברירת מחדל למשמרות** — בוקר 07:00-16:30, ערב 15:00-23:00, לילה 23:00-07:00. שעות מוזנות אוטומטית בטופס, השומר יכול לערוך. אדמין יכול לשנות דרך דף ההגדרות (`shift_default_morning/afternoon/night`). נוסף `GET /submissions/shift-defaults`. |
| 12 יוני 2026 | ✅ **דף הצלחה + התראת הגשה + פירוט הגשות לאדמין** — דף `/submit/success` אחרי הגשה (ללא Navbar); התראת טלגרם `notify_submission_success` נשלחת לאחר הגשה (לא-קריטית, מותנית ב-`telegram_id`); endpoint `GET /admin/weeks/{id}/submissions/detailed` (`WeekSubmissionsDetailed`: submitted/missing/week_label) + `SubmissionDetailPage` + `SubmissionsTable` עם פירוט משמרות נפתח. כיסוי טסטים: backend 160, frontend 78. |
| 12 יוני 2026 | ✅ **כפתור WebApp בהתראת "שבוע חדש"** — `notify_week_opened` שולח כעת כפתור Telegram WebApp "📅 הגשת אילוצים" (`submit_constraints_kb`) במקום קישור טקסט ל-`/submit`. `send_notification`/`broadcast_notifications` תומכים ב-`reply_markup`. |
| 12 יוני 2026 | 🐛 **תיקון: מילוי-מראש של הגשה קיימת בטופס** — `useSubmission.js` התאים הגשה קיימת לפי `s.day_index`/`existingDay.shifts`, אבל התשובה בנויה לפי `date`/`shift_windows` (שעות `HH:MM:SS`). עכשיו ממפה יום לפי `date` מול `start_date`, קורא `shift_windows` (`start_time`/`end_time`) וגוזר ל-`HH:MM`. כך שעריכת הגשה קיימת ממלאת שוב את הבחירות הקודמות. נוסף טסט ל-`useSubmission.test.js`. |
| 12 יוני 2026 | 🐛 **תיקון: הגשות לא נשמרו במלואן** — `SubmissionService.create_submission` התעלם מ-`data.days` ושמר רק את שורת ההגשה (general_notes), כך שהימים/המשמרות/השעות מעולם לא נכתבו ל-DB. עכשיו קורא ל-`upsert_submission` ושומר הכול. בנוסף: `SubmissionResponse.days` ממופה כעת מ-`daily_statuses` (alias) ו-`get_week_submissions_detailed` תוקן מ-`sub.days` ל-`sub.daily_statuses` (שגרם ל-500 ולכך שההגשה לא הופיעה בדף הפירוט). נוסף `test_submission_persistence.py` (טסט אינטגרציה אמיתי). |
| 12 יוני 2026 | 🐛 **תיקון: דף הדיווחים לא היה נגיש מהאדמין** — הראוט `/submissions` היה קיים ועבד אך **לא היה אליו קישור ב-`Navbar`** (וגם "אירועים"/"ייצוא" חסרו) — נגיש רק בהקלדת URL ידנית. נוספו קישורי ניווט. כן הושלמו מפתחות טקסט חסרים ב-`messages.js` (`chooseWeek`, `selectWeekPrompt`, `empty`, `submitted`, `missing`, `viewDetails`) שגרמו ל-`undefined` בבאדג'ים, ונוסף כפתור "צפה בפירוט" מ-`SubmissionsPage` אל `/submissions/:weekId`. נוסף `navbarLinks.test.jsx`. |
| 12 יוני 2026 | 🐛 **תיקון דף הייצוא + ייצוא אילוצים מעוצב** — הכפתור היה "שבור" כי `ExportPage` השתמש במפתחות `messages.export.download/exporting/chooseWeek` שלא היו קיימים (טקסט `undefined`), והקריאה פנתה ל-`/admin/export/excel?week_id=` שלא קיים בבק (הראוט `/admin/export/week/{id}`) — כך שלא נוצר קובץ. נוסף Endpoint חדש `GET /admin/export/constraints/{week_id}` + `ExcelExportService.export_constraints_report` שמייצר אקסל RTL מעוצב של כל מי ששלח אילוצים (זמינות + שעות משמרות + הערות, ממוין לפי שם). תוקנו מפתחות הטקסט, ה-URL ב-`adminApiClient`, וזיהוי ה-blob (`/export/`). נוספו `exportPage.test.jsx` + טסטים ל-`export_constraints_report`. |
| 12 יוני 2026 | 🐛 **תיקון 3 ה-Excel exports הישנים** — `export_weekly_schedule`/`export_deviation_report`/`export_guard_history` קראו לשדות `week.week_start`/`week_end` (האמיתיים: `start_date`/`end_date`) ולמתודות repo לא-קיימות (`get_by_week`→`get_submissions_for_week`, `event_repo.get_by_user`→`get_events_for_user`). היו קורסים ב-500 בכל קריאה אמיתית; הבדיקות לא תפסו כי `MagicMock` מחזיר כל attribute. נוסף `SubmissionRepository.get_by_user`. ה-mock של השבוע בטסטים מגדיר עכשיו `start_date`/`end_date`. |
| 12 יוני 2026 | 🎨 **עיצוב מחדש — Dark Indigo** — בנייה מחדש של `admin.css` כ-design system כהה ומינימליסטי: משטחים כהים בשכבות, מבטא Indigo, badges/alerts בגרסת soft, ליטוש Navbar/כרטיסים/טבלאות/scrollbar. הושלמו classes שהיו בשימוש ב-JSX בלי הגדרה (`alert`, `btn-block/outline/ghost/success`, `badge-success/secondary/warning/danger`, `form-actions`, `actions-cell`) — מה שתיקן בפרט את **דף ניהול השומרים**. צד המאבטחים (`guard.css`) ממשיך לעקוב אחרי theme של טלגרם. |
| 12 יוני 2026 | ✅ **מערכת Toast במקום `alert()` נייטיבי** — `ToastProvider`/`useToast` ללא תלויות (variants: success/error/warning/info, auto-dismiss + סגירה בלחיצה), עטיפה ב-`App` root. הוחלפו כל 6 קריאות ה-`alert()` ב-`GuardsPage` ו-`AdminConstraintsPage`; שמירת שומר מציגה כעת Toast הצלחה מפורש. נוסף `toast.test.jsx`. |
| 13 יוני 2026 | 🕐 **בורר שעות בכפולות חצי שעה** — שדות השעה בטופס האילוצים (`DayRow.jsx`, משותף לטופס המאבטח ולטופס האדמין) הוחלפו מ-`<input>` טקסט חופשי (`HH:MM`) ל-`<select>` עם 48 ערכים קבועים (`00:00`–`23:30`). אין צורך להקליד `:`, וניתן לבחור רק כפולות של חצי שעה. נוסף `HALF_HOUR_OPTIONS` ב-`guardMessages.js`. הערך הנשמר נשאר מחרוזת `HH:MM` — אין שינוי ב-backend/API/מודלים. נוסף טסט ל-`guardComponents.test.jsx`. |
