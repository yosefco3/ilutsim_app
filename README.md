# אילוצים (ilutzim_app)

מערכת לניהול משמרות שומרים. אדמינים מנהלים שומרים, פותחים שבועות להגשה ומשבצים
משמרות; השומרים מגישים את הזמינות השבועית שלהם דרך **Telegram Web App**.

> 📖 לתיעוד מלא ומעודכן — מודלים, endpoints, מחזור חיי שבוע, אבטחה והיסטוריית
> שינויים — ראו **[APP_OVERVIEW.md](APP_OVERVIEW.md)**.

---

## ארכיטקטורה

```
Telegram Bot (aiogram) ──┐                ┌── Frontend (React + Vite, :3001)
   התראות לשומרים         │                │      אדמין + הגשת שומרים
                          ▼                ▼
                   ┌──────────────────────────────┐
                   │  Backend (FastAPI)           │
                   │  Controllers → Services →    │
                   │  Repositories → Models       │
                   │  + Alembic migrations        │
                   └──────────────┬───────────────┘
                                  ▼
                          PostgreSQL Database
```

| רכיב         | טכנולוגיה                                   |
|--------------|---------------------------------------------|
| Backend      | Python 3.12, FastAPI, SQLAlchemy            |
| Database     | PostgreSQL + Alembic migrations             |
| Telegram Bot | aiogram 3.x                                 |
| Frontend     | React 18 + Vite (אדמין + שומרים, port 3001) |
| Testing      | pytest (backend), Vitest (frontend)         |
| Deployment   | Docker + docker-compose                     |

---

## הרצה מהירה (פיתוח)

הסקריפט `dev.sh` מפעיל את כל השירותים (backend + frontend + tunnel) בחלונות נפרדים:

```bash
./dev.sh        # הפעלת כל השירותים
./dev.sh stop   # עצירת כל השירותים
```

### הרצה ידנית

**Backend** (יש להשתמש ב-virtualenv של הפרויקט — אין `python` ב-PATH, רק `python3`):

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend** (אדמין + שומרים, על port 3001):

```bash
cd frontend/admin
npm install
npm run dev
```

### Docker

```bash
cp .env.docker .env   # ערוך את הסודות (SECRET_KEY, JWT, TELEGRAM_BOT_TOKEN, APP_URL)
docker compose up --build
```

---

## משתני סביבה עיקריים

| משתנה                | תיאור                                                   |
|----------------------|---------------------------------------------------------|
| `DATABASE_URL`       | חיבור ל-PostgreSQL (`postgresql+asyncpg://...`)         |
| `ENVIRONMENT`        | `dev` / `production` (עוקף-אימות לשומר פעיל ב-`dev` בלבד) |
| `SECRET_KEY`         | מפתח סוד לאפליקציה                                       |
| `JWT_SECRET_KEY`     | חתימת JWT לאדמינים (HS256)                               |
| `TELEGRAM_BOT_TOKEN` | טוקן הבוט — **env-only**; ריק = הבוט מושבת               |
| `APP_URL`            | Origin יחיד ל-CORS ב-production (ללא wildcard)           |

---

## בדיקות

הרצה מאוחדת של כל מערך הבדיקות (backend + frontend + כיסוי), עם דוח ל-`TEST_GRAPH.md`:

```bash
python3 scripts/test_graph.py
```

הרצה נפרדת:

```bash
cd backend && .venv/bin/python -m pytest tests/ -q   # backend
cd frontend/admin && npx vitest run                   # frontend
```

---

## מבנה תיקיות

```
ilutzim_app/
├── backend/             # FastAPI — controllers, services, repositories, models, bot, alembic, tests
├── frontend/admin/      # אפליקציה מאוחדת — אדמינים (/guards) + שומרים (/submit)
├── design-system/       # 🎨 מערכת עיצוב ממותגת + קונספט "בונה הסידור" (drag & drop)
├── scripts/             # כלי עזר (test_graph.py ועוד)
├── docker-compose.yml
├── dev.sh / dev-stop.sh # הרצת/עצירת סביבת הפיתוח
└── APP_OVERVIEW.md      # 📖 התיעוד המלא של האפליקציה
```

---

## תיעוד נוסף

- **[APP_OVERVIEW.md](APP_OVERVIEW.md)** — סקירת תפקוד מלאה (מתעדכן בכל שינוי משמעותי).
- **[design-system/README.md](design-system/README.md)** — מערכת העיצוב וקונספט בונה הסידור.
- **`מערכת_ניהול_משמרות_סקירה_ותכנון.pdf`** — מסמך תכנון בונה הסידור (השלב הבא).
</content>
</invoke>
