# 📋 Prompt Library — Development Plan
## Micro-SaaS Security Guard Shift Constraint Management System

---

## How to Use

Each step is a self-contained prompt file. Copy the content of the relevant step file and paste it as a prompt to the AI assistant. Steps must be executed **in order**, as each builds upon the previous ones.

**Before starting each step**, confirm that all previous tests pass.

---

## Steps Overview

| # | File | Description | Tests | Dependencies |
|---|------|-------------|-------|--------------|
| 0 | [STEP_00_INFRASTRUCTURE.md](./STEP_00_INFRASTRUCTURE.md) | Project structure, config, logging, messages, exceptions, test infra | ~20 | — |
| 1 | [STEP_01_DATABASE_MODELS.md](./STEP_01_DATABASE_MODELS.md) | SQLAlchemy ORM models + Alembic migrations | 13 | Step 0 |
| 2 | [STEP_02_REPOSITORIES.md](./STEP_02_REPOSITORIES.md) | Data Access Layer (generic + specialized repos) | 24 | Step 1 |
| 3 | [STEP_03_SCHEMAS.md](./STEP_03_SCHEMAS.md) | Pydantic v2 validation schemas | 18 | Step 0 |
| 4 | [STEP_04_SERVICES.md](./STEP_04_SERVICES.md) | Business logic (deviation, upsert, smart skip) | 28 | Steps 2, 3 |
| 5 | [STEP_05_CONTROLLERS.md](./STEP_05_CONTROLLERS.md) | API routes + Telegram initData auth | 26 | Step 4 |
| 6 | [STEP_06_TELEGRAM_BOT.md](./STEP_06_TELEGRAM_BOT.md) | Telegram bot (aiogram v3) + cron jobs | 17 | Steps 4, 5 |
| 7 | [STEP_07_WEBAPP.md](./STEP_07_WEBAPP.md) | Telegram Web App (React constraint form) | 27 | Step 5 |
| 8 | [STEP_08_ADMIN_DASHBOARD.md](./STEP_08_ADMIN_DASHBOARD.md) | Admin Dashboard (React management UI) | 24 | Step 5 |
| 9 | [STEP_09_EXCEL_EXPORT.md](./STEP_09_EXCEL_EXPORT.md) | Excel export engine (openpyxl) | 14 | Step 4 |
| 10 | [STEP_10_DOCKER_E2E.md](./STEP_10_DOCKER_E2E.md) | Docker + docker-compose + E2E tests | 8 | All steps |

**Total: ~219 tests across 11 steps**

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Telegram Bot (aiogram v3)             │
│              (auth, notifications, cron jobs)            │
├─────────────────────────────────────────────────────────┤
│              Telegram Web App (React SPA)                │
│           (weekly constraint submission form)            │
├─────────────────────────────────────────────────────────┤
│              Admin Dashboard (React SPA)                 │
│         (manage guards, weeks, events, export)           │
├─────────────────────────────────────────────────────────┤
│                FastAPI Backend (Python)                  │
│     Controllers → Services → Repositories (OOP)         │
├─────────────────────────────────────────────────────────┤
│         PostgreSQL + SQLAlchemy 2.0 + Alembic            │
└─────────────────────────────────────────────────────────┘
```

---

## Key Principles (Enforced in Every Step)

1. **OOP & Separation of Concerns**: Controllers → Services → Repositories
2. **Zero Hard Coding**: All config from `.env`, all text from `messages.py` / `messages.js`
3. **Centralized Hebrew Text**: Single source of truth for all user-facing strings
4. **Error Handling & Logging**: From day one, in every layer
5. **Tests**: Every step includes comprehensive tests that must pass
6. **Full Type Hints**: Python type hints + PropTypes/TypeScript where applicable
7. **Async/Await**: Throughout the backend
8. **Dependency Injection**: All services and repositories injected via constructors

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Database | PostgreSQL 15, Alembic migrations |
| Bot | aiogram v3, APScheduler |
| Frontend (WebApp) | React 18, Vite |
| Frontend (Admin) | React 18, Vite, React Router v6 |
| Export | openpyxl |
| Testing | pytest, pytest-asyncio, Vitest, React Testing Library |
| DevOps | Docker, docker-compose, Makefile |
