# Step 10 — Dockerization, Deployment Setup & End-to-End Tests

## Context
You are continuing development of the Micro-SaaS security guard shift constraint management system. **Steps 0-9 (entire application — backend, bot, both frontends, Excel export) are complete. All previous tests pass.**

**Important:** All user-facing text is in Hebrew. Code comments in English.

## Objective
Containerize the entire system with Docker, create docker-compose for local development and production-like environments, add a Makefile for convenience commands, and write End-to-End tests that exercise the full system lifecycle.

## Docker Files

### 1. `backend/Dockerfile`
```dockerfile
# Multi-stage build for minimal image size

# Stage 1: Dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Application
FROM python:3.11-slim
WORKDIR /app

# Create non-root user
RUN addgroup --system appgroup && adduser --system --group appuser

# Copy installed packages
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. `frontend/webapp/Dockerfile`
```dockerfile
# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Include `frontend/webapp/nginx.conf`:
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    # SPA routing: all paths → index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3. `frontend/admin/Dockerfile`
Same structure as webapp Dockerfile, with its own `nginx.conf`.
Additional build arg: `VITE_ADMIN_API_KEY`.

### 4. `.dockerignore` files
For each service directory:
```
node_modules/
__pycache__/
*.pyc
.env
.git
.pytest_cache
tests/
__tests__/
*.md
```

## Docker Compose

### 5. `docker-compose.yml` (Production-like)
```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-ilutzim}
      POSTGRES_USER: ${POSTGRES_USER:-ilutzim_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-ilutzim_user}"]
      interval: 5s
      timeout: 5s
      retries: 5
    ports:
      - "5432:5432"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    env_file: .env
    command: >
      sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 10s
      timeout: 5s
      retries: 3

  webapp:
    build:
      context: ./frontend/webapp
      args:
        VITE_API_URL: ${VITE_API_URL:-http://localhost:8000}
    restart: unless-stopped
    ports:
      - "3000:80"
    depends_on:
      - backend

  admin:
    build:
      context: ./frontend/admin
      args:
        VITE_API_URL: ${VITE_API_URL:-http://localhost:8000}
        VITE_ADMIN_API_KEY: ${ADMIN_API_KEY:-dev-admin-key}
    restart: unless-stopped
    ports:
      - "3001:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### 6. `docker-compose.dev.yml` (Development Override)
```yaml
version: "3.8"

services:
  backend:
    build:
      context: ./backend
    volumes:
      - ./backend:/app
    command: >
      sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    environment:
      - ENVIRONMENT=dev
      - LOG_LEVEL=DEBUG

  webapp:
    build:
      context: ./frontend/webapp
      target: builder
    volumes:
      - ./frontend/webapp/src:/app/src
    ports:
      - "3000:5173"
    command: npm run dev -- --host 0.0.0.0

  admin:
    build:
      context: ./frontend/admin
      target: builder
    volumes:
      - ./frontend/admin/src:/app/src
    ports:
      - "3001:5173"
    command: npm run dev -- --host 0.0.0.0
```

Usage: `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up`

### 7. Root `.env` File
```env
# Database
POSTGRES_DB=ilutzim
POSTGRES_USER=ilutzim_user
POSTGRES_PASSWORD=changeme
DATABASE_URL=postgresql+asyncpg://ilutzim_user:changeme@db:5432/ilutzim
DATABASE_URL_SYNC=postgresql://ilutzim_user:changeme@db:5432/ilutzim

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token-here

# URLs
WEBAPP_URL=http://localhost:3000
ADMIN_DASHBOARD_URL=http://localhost:3001
VITE_API_URL=http://localhost:8000

# Admin
ADMIN_API_KEY=dev-admin-key

# App
LOG_LEVEL=INFO
ENVIRONMENT=dev
CRON_WEEKLY_OPEN_DAY=sunday
CRON_WEEKLY_OPEN_HOUR=09:00
```

## Makefile

### 8. `Makefile`
```makefile
.PHONY: up down dev test test-backend test-frontend migrate logs build clean

# Production-like
up:
	docker-compose up -d --build

down:
	docker-compose down

# Development with hot reload
dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Run all tests
test: test-backend test-frontend

# Backend tests
test-backend:
	cd backend && pip install -r requirements-dev.txt && pytest -v --cov=app

# Frontend tests
test-frontend:
	cd frontend/webapp && npm test
	cd frontend/admin && npm test

# Run database migrations
migrate:
	cd backend && alembic upgrade head

# View logs
logs:
	docker-compose logs -f

# Build images without starting
build:
	docker-compose build

# Clean up everything
clean:
	docker-compose down -v --rmi local
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

# Run E2E tests (requires running services)
e2e:
	cd backend && pytest tests/test_e2e.py -v

# Shell into backend container
shell:
	docker-compose exec backend /bin/sh

# Database shell
db-shell:
	docker-compose exec db psql -U ilutzim_user -d ilutzim
```

## End-to-End Tests (`backend/tests/test_e2e.py`)

These tests exercise the full application lifecycle through the API. They use `httpx.AsyncClient` against the test app with a real test database.

### Test Setup
- Create a fresh test database for each test session
- Apply all migrations
- Seed system settings
- Use a single `httpx.AsyncClient` instance

### Tests

1. **`test_health_check`**
   - `GET /health` → 200 `{"status": "ok"}`

2. **`test_full_guard_lifecycle`**
   Full flow:
   - Admin: Create guard (POST /api/admin/users) → 201
   - Admin: Verify guard appears in list (GET /api/admin/users) → 200, guard present
   - Simulate: Link telegram_id to guard (via service, since we can't do real Telegram)
   - Guard: Submit constraints for an open week (POST /api/submissions) → 201
   - Guard: Verify submission exists (GET /api/submissions/{week_id}) → 200, data present
   - Admin: Verify status grid shows "submitted" for this guard

3. **`test_admin_week_lifecycle`**
   - Create week (POST /api/admin/weeks) → 201, status=open
   - Guard: Submit constraints → 201 (succeeds)
   - Lock week (PATCH /api/admin/weeks/{id}/status) → 200, status=locked
   - Guard: Attempt to submit → 403 (WeekLockedException)
   - Publish week (PATCH status → published) → 200

4. **`test_submission_upsert_flow`**
   - Submit constraints (first time) → 201
   - Submit constraints again (same user + week, different data) → 201
   - Get submission → verify only latest data exists (not duplicated)

5. **`test_blocked_date_respected`**
   - Create blockout event for guard (Monday-Wednesday)
   - Submit constraints including Monday → Monday is filtered out
   - Get submission → Monday not in daily_statuses

6. **`test_deviation_detection_e2e`**
   - Create guard with min_total_shifts=5, min_night_shifts=2
   - Submit with only 3 total shifts and 1 night shift
   - Verify: has_deviation=True in response
   - Verify: deviation_details contain both rule violations

7. **`test_export_excel_e2e`**
   - Create guard + week + submission with full data
   - GET /api/admin/export/{week_id}/excel → 200
   - Verify: response content-type is xlsx
   - Verify: load with openpyxl succeeds
   - Verify: at least header rows exist

8. **`test_status_grid_accuracy`**
   - Create 4 guards:
     - Guard A: submitted normally
     - Guard B: submitted with deviation
     - Guard C: not submitted
     - Guard D: fully absent (full-week event)
   - GET /api/admin/weeks/{week_id}/status-grid
   - Verify: Guard A = "submitted", Guard B = "submitted_with_variance", Guard C = "pending", Guard D = "auto_absence"

## Rules
- Docker images must be minimal (alpine/slim base)
- Health checks on all critical services
- Non-root user in all containers
- `.dockerignore` files to minimize build context
- Environment variables from `.env` (never hard-coded in Dockerfiles)
- Makefile provides all common commands
- E2E tests use real API calls through httpx (not mocks)
- All tests must pass with `pytest` / `npm test`
- Code comments in English
