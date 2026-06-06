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
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null
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