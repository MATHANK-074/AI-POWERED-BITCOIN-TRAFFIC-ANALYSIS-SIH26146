#!/usr/bin/env bash
# Start script for KRISHIGUARD Backend and Frontend

set -e

echo "========================================================"
echo " Starting KRISHIGUARD System (Offline Mode)"
echo "========================================================"

# Activate Virtual Environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Ensure directories exist
mkdir -p logs

# Start Backend
echo "Starting Backend API server on http://127.0.0.1:8000 ..."
cd backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo $BACKEND_PID > .backend.pid
echo "Backend started with PID: $BACKEND_PID"

# Start Frontend
echo "Starting Frontend Vite server on http://127.0.0.1:5173 ..."
cd frontend
nohup npm run dev -- --host 0.0.0.0 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo $FRONTEND_PID > .frontend.pid
echo "Frontend started with PID: $FRONTEND_PID"

echo "========================================================"
echo " KRISHIGUARD is running!"
echo " - Backend Swagger API: http://127.0.0.1:8000/docs"
echo " - Frontend Dashboard:   http://127.0.0.1:5173"
echo " Logs: logs/backend.log & logs/frontend.log"
echo " Stop using: ./stop.sh"
echo "========================================================"
