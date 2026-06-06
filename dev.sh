#!/usr/bin/env bash
# dev.sh — Run all services (backend + admin + webapp) in one command.
# Usage: ./dev.sh
# Press Ctrl+C to stop all services.

set -euo pipefail

# Colors for log prefixes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
PIDS=()

# --- Kill anything occupying our ports ---
kill_port() {
    local port=$1
    local pids
    pids=$(lsof -ti :"$port" 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}⚡ Killing processes on port $port: $pids${NC}"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 0.5
    fi
}

cleanup() {
    echo ""
    echo -e "${RED}🛑 Stopping all services...${NC}"

    # Send SIGTERM to tracked PIDs and their children
    for pid in "${PIDS[@]}"; do
        # Kill child processes first (uvicorn reload worker, vite dev server, etc.)
        pkill -P "$pid" 2>/dev/null || true
        kill "$pid" 2>/dev/null || true
    done

    # Give processes 2 seconds to shut down gracefully
    sleep 2

    # Force-kill anything still running on our ports (safety net)
    kill_port 8000
    kill_port 3001
    kill_port 5173

    # Force-kill any remaining tracked PIDs
    for pid in "${PIDS[@]}"; do
        kill -9 "$pid" 2>/dev/null || true
    done

    # Reap all children with a timeout so we never hang
    for pid in "${PIDS[@]}"; do
        timeout 2 bash -c "kill -0 $pid 2>/dev/null && wait $pid" 2>/dev/null || true
    done

    echo -e "${GREEN}✅ All services stopped.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Kill existing processes on our ports
echo -e "${CYAN}🔧 Checking for existing processes...${NC}"
kill_port 8000
kill_port 3001
kill_port 5173

# --- Start Backend ---
echo -e "${GREEN}🚀 Starting Backend (port 8000)...${NC}"
(
    cd "$PROJECT_ROOT/backend"
    source .venv/bin/activate
    exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) &
PIDS+=($!)

# --- Wait for Backend to be ready ---
echo -e "${CYAN}⏳ Waiting for backend to be ready...${NC}"
MAX_WAIT=30
WAITED=0
until curl -sf http://localhost:8000/health > /dev/null 2>&1; do
    sleep 1
    WAITED=$((WAITED + 1))
    if [ $WAITED -ge $MAX_WAIT ]; then
        echo -e "${RED}❌ Backend did not become ready within ${MAX_WAIT}s — aborting${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✅ Backend is ready (took ${WAITED}s)${NC}"

# --- Start Admin Frontend ---
echo -e "${GREEN}🚀 Starting Admin Dashboard (port 3001)...${NC}"
(
    cd "$PROJECT_ROOT/frontend/admin"
    exec npm run dev
) &
PIDS+=($!)

# --- Start Webapp Frontend ---
echo -e "${GREEN}🚀 Starting Webapp (port 5173)...${NC}"
(
    cd "$PROJECT_ROOT/frontend/webapp"
    exec npm run dev
) &
PIDS+=($!)

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ All services are running!${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
echo -e "  Backend API:  ${GREEN}http://localhost:8000${NC}"
echo -e "  Admin Dashboard: ${GREEN}http://localhost:3001${NC}"
echo -e "  Webapp:       ${GREEN}http://localhost:5173${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
echo -e "  Press ${RED}Ctrl+C${NC} to stop all services"
echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
echo ""

# Wait for all background processes
wait