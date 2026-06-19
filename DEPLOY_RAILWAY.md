# 🚀 העלאת "אילוצים" לפרודקשן ב-Railway — רנבוק מלא

> **מטרה:** להעלות את **החצי הראשון** של האפליקציה (ניהול שומרים, שבועות, הגשות,
> ייצוא, הגדרות, בוט טלגרם, אוטומציית cron) לפרודקשן ב-Railway — **בלי בונה הסידור
> ובלי יבוא אילוצים**, שימשיכו בפיתוח בנפרד.
>
> עדכון אחרון: 19 יוני 2026

---

## 0. החלטות אדריכליות (נעולות)

| נושא | החלטה |
|------|--------|
| **שירות Frontend** | שירות Railway **יחיד** — FastAPI מגיש את ה-`dist` הבנוי (StaticFiles). אותו origin → אין CORS, אידיאלי ל-Telegram WebApp. |
| **דומיין** | להשאיר `app.safrasecure.uk` — CNAME ל-Railway. כתובת ה-WebApp ב-BotFather נשארת זהה. |
| **הסתרת בונה הסידור + יבוא** | **Feature flag** יחיד `SCHEDULE_BUILDER_ENABLED`. קוד אחד לכל ה-branches, הדגל בלבד שונה בין סביבות. |
| **מסד נתונים** | Postgres **חדש וריק** ב-Railway (alembic + seed admin). |
| **בוט טלגרם** | **בוט נפרד** לפרודקשן (טוקן ייעודי). dev משתמש בטוקן אחר או כבוי. |
| **Replicas** | **replica יחיד** בלבד — הבוט (polling), ה-APScheduler, וה-login-throttle (in-memory) דורשים תהליך אחד. |

---

## 1. אסטרטגיית ה-Branches (3 branches)

הדגל הוא ה-feature flag, **לא** ה-branch — כל ה-branches מכילים את כל הקוד; ההבדל הוא
רק בערך `SCHEDULE_BUILDER_ENABLED` שמוגדר בסביבת Railway. כך אין merge-hell בין
branch עם בונה הסידור ל-branch בלעדיו.

```
                    merge כשיציב
  development  ───────────────────────▶  production  ──▶ Railway (flag=false)
 (בונה הסידור,    ▲                          │
  flag=true)       │ forward-merge           │ branch
                   │                          ▼
                   └──────────────────────  hotfix
                                          (תיקוני באגים לפרודקשן, flag=false)
```

| Branch | תפקיד | `SCHEDULE_BUILDER_ENABLED` | נפרס ל-Railway? |
|--------|-------|----------------------------|------------------|
| `production` | קוד יציב שרץ בפרודקשן | `false` (ב-env של Railway) | ✅ כן — אוטו-דפלוי |
| `development` | פיתוח בונה הסידור + יבוא | `true` (מקומי / סביבת dev) | ❌ לא (או סביבת staging נפרדת) |
| `hotfix` | תיקוני באגים דחופים לפרודקשן | `false` | זמני — נמחק אחרי מיזוג |

**זרימת עבודה:**
1. עבודה שוטפת על בונה הסידור → ב-`development`.
2. כשהחצי-הראשון יציב → merge ל-`production`. Railway מזהה push ומפרס אוטומטית.
3. באג בפרודקשן → `git switch -c hotfix production` → תיקון → merge ל-`production` **וגם** ל-`development`.

**הקמה (לאחר מיזוג שינויי הקוד של שלב 2 לתוך `main`):**
```bash
git switch main
git pull
git switch -c production        # branch הפרודקשן
git push -u origin production
git switch -c development main   # המשך פיתוח בונה הסידור
git push -u origin development
# hotfix נוצר לפי צורך מ-production, לא מראש
```
> אם רוצים, אפשר לוותר על `main` ולעבוד ישירות עם `production`/`development`.

---

## 2. שינויי קוד נדרשים (לפני הדפלוי הראשון)

כל אלה ממוזגים ל-`production` (ול-`development`/`main`). ה-feature flag דיפולטיבית
`true`, כך ש-dev לא מושפע; הפרודקשן בלבד מקבל `false`.

### 2.1 Backend — דגל ב-`config.py`
הוספת שדה ל-`Settings`:
```python
# Feature flags
SCHEDULE_BUILDER_ENABLED: bool = True   # חלק ב' (בונה הסידור + יבוא אילוצים)
```

### 2.2 Backend — גידור ה-routers ב-`main.py`
ב-`create_app()`, להחליף את הרישום הבלתי-מותנה בגידור מאחורי הדגל:
```python
if settings.SCHEDULE_BUILDER_ENABLED:
    app.include_router(constraints_import_router)   # יבוא אילוצים
    app.include_router(profile_router)              # בונה הסידור — פרופילים
    app.include_router(position_router)             # בונה הסידור — עמדות
    app.include_router(attribute_router)            # בונה הסידור — מאפיינים
```
וכן לגדר ב-`lifespan` את זריעת ברירות-המחדל של בונה הסידור (`seed_default_profile`,
`seed_default_attributes`) מאחורי אותו דגל — כך שב-prod ה-DB לא ייזרע בנתוני חלק ב'.

> תוצאה: כש-`SCHEDULE_BUILDER_ENABLED=false`, ה-routers של בונה הסידור/יבוא
> **אינם נרשמים כלל** — אין endpoints פעילים לנתונים/פעולות (POST → 405/404).
> בקשת GET לנתיב כזה נופלת ל-SPA fallback ומחזירה את ה-`index.html` (התנהגות
> SPA רגילה, ללא חשיפת נתונים), וה-UI עצמו חסום (ה-route מפנה חזרה ל-`/guards`).

### 2.3 Backend — הגשת ה-Frontend הבנוי (StaticFiles + SPA fallback)
ב-`main.py`, אחרי רישום כל ה-routers וה-`/health`, להוסיף הגשת ה-`dist` **רק אם קיים**
(כדי לא לשבור dev מקומי שמריץ Vite בנפרד):
```python
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

_DIST = Path(__file__).resolve().parent.parent / "frontend_dist"
if _DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        # נתיבי API נתפסים ע"י ה-routers שנרשמו קודם; כאן רק נתיבי לקוח
        index = _DIST / "index.html"
        return FileResponse(
            index,
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
        )
```
> ה-`no-cache` חשוב — Telegram WebApp שומר את ה-WebView אגרסיבית; בלי זה שומרים
> מקבלים גרסה ישנה (תקלה מתועדת ב-`APP_OVERVIEW.md`). הנכסים תחת `/assets`
> מקבלים hash בשם הקובץ ולכן ניתנים ל-cache.

### 2.4 Frontend — גידור ה-routes (`App.jsx`)
דגל build-time של Vite. עוטפים את ה-routes של בונה הסידור + יבוא:
```jsx
const BUILDER_ENABLED = import.meta.env.VITE_SCHEDULE_BUILDER_ENABLED !== 'false';
...
{BUILDER_ENABLED && <>
  <Route path="/import" element={<ProtectedRoute><ImportConstraintsPage /></ProtectedRoute>} />
  <Route path="/builder/profiles" element={<ProtectedRoute><ProfilesPage /></ProtectedRoute>} />
  <Route path="/builder/positions" element={<ProtectedRoute><PositionsPage /></ProtectedRoute>} />
</>}
```

### 2.5 Frontend — גידור הקישורים ב-`Navbar.jsx`
לעטוף את הקישור `/import` ואת קבוצת "בונה הסידור" (label + 2 קישורים) באותו תנאי
`BUILDER_ENABLED`.

### 2.6 Frontend — base-URL של ה-API לסביבת origin-יחיד
היום `API_BASE = import.meta.env.VITE_API_URL || '/api'` ומסתמך על proxy של Vite
שמסיר `/api`. ב-Railway אין proxy — הבקאנד מגיש הכל מאותו origin בשורש. לכן בבנייה
לפרודקשן נגדיר `VITE_API_URL=''` (מחרוזת ריקה) → הבקשות יוצאות ל-`/auth/...`,
`/admin/...`, `/submissions/...` ישירות לבקאנד. **לאמת בצעד הבנייה** שהבקשות אכן
יוצאות לשורש ולא ל-`/api`.

---

## 3. בנייה משולבת — `Dockerfile` בשורש הריפו

הקיים `backend/Dockerfile` עם context=`./backend` לא רואה את ה-frontend. ניצור
**Dockerfile חדש בשורש** (context = שורש הריפו) שבונה את שני החלקים:

```dockerfile
# ── שלב 1: בניית ה-Frontend ──
FROM node:20-slim AS frontend
WORKDIR /fe
COPY frontend/admin/package*.json ./
RUN npm ci
COPY frontend/admin/ ./
ARG VITE_SCHEDULE_BUILDER_ENABLED=false
ARG VITE_API_URL=
RUN VITE_SCHEDULE_BUILDER_ENABLED=$VITE_SCHEDULE_BUILDER_ENABLED \
    VITE_API_URL=$VITE_API_URL \
    npm run build      # → /fe/dist

# ── שלב 2: תלויות Python ──
FROM python:3.12-slim AS pybuild
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── שלב 3: Runtime ──
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=pybuild /install /usr/local
COPY backend/ /app/
COPY --from=frontend /fe/dist /app/frontend_dist
COPY backend/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
# כיבוד $PORT של Railway (ברירת מחדל 8000 מקומית)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

> **שינוי ב-`docker-entrypoint.sh`:** ה-healthcheck/CMD המקוריים נעלו את הפורט ל-8000.
> ב-Railway uvicorn חייב להאזין ל-`$PORT`. ה-CMD למעלה כבר מטפל בזה. אם משאירים
> את ה-HEALTHCHECK של Docker — לעדכן גם אותו ל-`$PORT`, או להסתמך על healthcheck
> של Railway (`/health`).

### `railway.json` בשורש (להצמיד הגדרות דפלוי)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": { "builder": "DOCKERFILE", "dockerfilePath": "Dockerfile" },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10,
    "healthcheckPath": "/health"
  }
}
```
> `numReplicas: 1` קריטי — בוט polling + scheduler.

---

## 4. הקמת Railway — צעד אחר צעד

### 4.1 יצירת הפרויקט
1. Railway → **New Project** → **Deploy from GitHub repo** → לבחור `yosefco3/ilutsim_app`.
2. בהגדרות השירות → **Settings → Source** → לקבוע branch = **`production`**.
3. **Settings → Build** → לוודא שמשתמש ב-Dockerfile בשורש (`railway.json` כבר קובע זאת).

### 4.2 הוספת Postgres
1. בפרויקט → **New → Database → Add PostgreSQL**.
2. Railway יוצר משתני `PGUSER`, `PGPASSWORD`, `PGDATABASE`, `RAILWAY_PRIVATE_DOMAIN`, וכן `DATABASE_URL` (בפורמט `postgresql://` — **לא** מתאים ל-asyncpg).

### 4.3 משתני סביבה של השירות (Variables)
> ⚠️ האפליקציה דורשת `postgresql+asyncpg://`. לכן **לא** משתמשים ב-`DATABASE_URL`
> של הפלאגין כמו-שהוא, אלא מרכיבים אותו עם reference-variables:

| משתנה | ערך | הערה |
|-------|-----|------|
| `ENVIRONMENT` | `production` | מפעיל fail-fast על סודות + חוסם `__DEV_MODE__` |
| `DATABASE_URL` | `postgresql+asyncpg://${{Postgres.PGUSER}}:${{Postgres.PGPASSWORD}}@${{Postgres.RAILWAY_PRIVATE_DOMAIN}}:5432/${{Postgres.PGDATABASE}}` | async — לכל ה-app + alembic |
| `TELEGRAM_BOT_TOKEN` | `<טוקן הבוט החדש לפרודקשן>` | מ-BotFather, בוט נפרד |
| `APP_URL` | `https://app.safrasecure.uk` | origin יחיד ל-CORS |
| `JWT_SECRET_KEY` | `<64 תווי hex אקראיים>` | ראה `scripts/gen_secrets.sh` |
| `ADMIN_API_KEY` | `<מחרוזת אקראית>` | |
| `SCHEDULE_BUILDER_ENABLED` | `false` | **מסתיר בונה הסידור + יבוא** |
| `AUTO_ROLLOVER_ENABLED` | `true` | מפעיל את ה-scheduler (cron) |
| `SCHEDULER_TIMEZONE` | `Asia/Jerusalem` | DST-aware |
| `SEED_ADMIN_EMAIL` | `<אימייל אדמין>` | |
| `SEED_ADMIN_PASSWORD` | `<סיסמה חזקה: ≥10 תווים, אות+ספרה>` | אחרת השרת לא יעלה |
| `SEED_ADMIN_FULL_NAME` | `<שם האדמין>` | |
| `LOG_LEVEL` | `INFO` | |
| `RETENTION_ENABLED` | `true` | (ברירת מחדל; אופציונלי) |
| `RETENTION_WEEKS` | `60` | (ברירת מחדל; אופציונלי) |

> **הערה על `$PORT`:** Railway מזריק `PORT` אוטומטית — ה-CMD כבר מאזין לו. אין צורך
> להגדיר ידנית.
>
> **הערה על `VITE_*`:** משתני ה-Vite הם **build-time** ונקבעים כ-`ARG` ב-Dockerfile
> (כבר `false`/`''`). אם רוצים לשלוט בהם דרך Railway, להגדירם כ-Build Args בשירות.

### 4.4 דומיין מותאם
1. Railway → Service → **Settings → Networking → Custom Domain** → להזין `app.safrasecure.uk`.
2. Railway יחזיר יעד **CNAME** (כגון `xxxx.up.railway.app`).
3. ב-Cloudflare (או ספק ה-DNS): רשומת **CNAME** ל-`app` → היעד מ-Railway.
   - מומלץ **DNS-only (ענן אפור)** כדי ש-Railway ינהל את ה-TLS. אם משאירים proxy (כתום),
     לקבוע SSL mode = **Full (strict)**.
4. כתובת ה-WebApp ב-BotFather נשארת `https://app.safrasecure.uk/submit` — **אין שינוי**.

---

## 5. בוט הטלגרם לפרודקשן

1. ב-BotFather → ליצור **בוט חדש** (או להשתמש בקיים אם מיועד לפרודקשן) → לקבל token.
2. להגדיר `TELEGRAM_BOT_TOKEN` ב-Railway לטוקן זה.
3. **BotFather → /setmenubutton** (או /mybots → Bot Settings → Menu Button) →
   להפנות ל-`https://app.safrasecure.uk/submit`.
4. ⚠️ **לא** להריץ את אותו טוקן בו-זמנית ב-dev וב-prod — polling יחיד לכל טוקן.
   בסביבת dev: טוקן בוט **אחר**, או להשאיר `TELEGRAM_BOT_TOKEN` ריק (הבוט מושבת אוטומטית).

---

## 6. ה-CRON / האוטומציה (כבר מובנה ב-app)

אין צורך ב-Railway Cron נפרד — האוטומציה רצה **בתוך התהליך** ב-APScheduler:

1. **רולאובר שבועי** (מוצ"ש, ראשון 00:00) + **catch-up** בעליית השרת — פועל אוטומטית
   כש-`AUTO_ROLLOVER_ENABLED=true`.
2. **auto-open / auto-lock** — מתוזמנים מתוך **הגדרות המערכת ב-DB** (לא env). אחרי
   הדפלוי, להיכנס לדף **הגדרות** באדמין ולהפעיל את המתגים + לקבוע יום/שעה. השינוי
   מסתנכרן מיידית (`sync_automation_jobs`) בלי restart.
3. **תנאי הכרחי:** השירות חייב לרוץ **תמיד** (replica יחיד, ללא sleep). בתוכנית Railway
   שאינה מרדימה את השירות זה מובטח. לוודא ש-`numReplicas=1` (גם בגלל polling).

---

## 7. רצף הדפלוי הראשון

1. למזג את שינויי הקוד (סעיף 2) + `Dockerfile` + `railway.json` ל-`production`.
2. `git push origin production` → Railway בונה ומפרס אוטומטית.
3. בעליית הקונטיינר, `docker-entrypoint.sh` מריץ:
   - המתנה ל-DB,
   - `alembic upgrade head` (יוצר את כל הטבלאות ב-DB הריק),
   - `python -m app.seed` (יוצר את האדמין הראשוני + שבוע ראשוני — אידמפוטנטי),
   - מפעיל את uvicorn.
4. לעקוב בלוגים של Railway: לוודא "Migrations complete", "Seed complete",
   "Telegram bot started", "rollover scheduler".

---

## 8. בדיקות אחרי דפלוי (Checklist)

- [ ] `https://app.safrasecure.uk/health` מחזיר `{"status":"ok"}`.
- [ ] התחברות אדמין עם `SEED_ADMIN_*` עובדת.
- [ ] דפי האדמין: שומרים / שבועות / הגשות / ייצוא / הגדרות — נטענים.
- [ ] **בונה הסידור + "יבוא אילוצים" לא מופיעים** ב-Navbar; גישה ישירה ל-`/import`
      או `/builder/profiles` מפנה חזרה ל-`/guards` (route חסום); אין endpoints
      פעילים של בונה הסידור (POST → 405/404, ה-routers לא נרשמו).
- [ ] בוט הטלגרם מגיב ל-`/start`; כפתור ה-WebApp פותח את `/submit`.
- [ ] שומר מגיש זמינות בשבוע פתוח → ההגשה נשמרת ומופיעה באדמין.
- [ ] ייצוא Excel עובד.
- [ ] בדף הגדרות — הפעלת auto-open/auto-lock נשמרת (אם רוצים אוטומציה).
- [ ] בלוגים אין שגיאת `validate_production_secrets`.

---

## 9. סקריפטים נלווים

- `scripts/gen_secrets.sh` — מייצר `JWT_SECRET_KEY` + `ADMIN_API_KEY` אקראיים להדבקה ב-Railway.
- `.env.production.example` — תבנית כל משתני הסביבה לפרודקשן (placeholders בלבד, לא ב-git עם ערכים אמיתיים).

---

## 10. סביבת Development (אופציונלי — staging ב-Railway)

אם רוצים גם סביבת dev ענן לבדיקת בונה הסידור:
- שירות Railway שני (או Environment שני באותו פרויקט) מ-branch `development`.
- `SCHEDULE_BUILDER_ENABLED=true`, `ENVIRONMENT=staging`, **טוקן בוט נפרד**, DB נפרד.
- דומיין נפרד (למשל `dev.safrasecure.uk` או דומיין Railway).
