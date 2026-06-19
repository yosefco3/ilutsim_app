# ── Combined production image for Railway (single service) ──────────────────
# Builds the React frontend, then serves it from FastAPI (same origin).
# Build context MUST be the repo root.

# ── Stage 1: build the frontend ──
FROM node:20-slim AS frontend
WORKDIR /fe
COPY frontend/admin/package*.json ./
RUN npm ci
COPY frontend/admin/ ./
# Part B hidden in production; single-origin API base (no /api proxy in prod).
ARG VITE_SCHEDULE_BUILDER_ENABLED=false
ARG VITE_API_URL=
RUN VITE_SCHEDULE_BUILDER_ENABLED=$VITE_SCHEDULE_BUILDER_ENABLED \
    VITE_API_URL=$VITE_API_URL \
    npm run build

# ── Stage 2: python dependencies ──
FROM python:3.12-slim AS pybuild
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 3: runtime ──
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=pybuild /install /usr/local
COPY backend/ /app/
# Built frontend served by FastAPI (app/main.py looks for ../frontend_dist).
COPY --from=frontend /fe/dist /app/frontend_dist
COPY backend/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
# Bind to Railway's injected $PORT (default 8000 for local runs).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
