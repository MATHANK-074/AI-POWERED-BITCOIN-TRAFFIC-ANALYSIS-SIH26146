#!/usr/bin/env bash
# Stop script for KRISHIGUARD

echo "Stopping KRISHIGUARD services..."

if [ -f ".backend.pid" ]; then
    PID=$(cat .backend.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "Stopped Backend (PID: $PID)"
    fi
    rm -f .backend.pid
fi

if [ -f ".frontend.pid" ]; then
    PID=$(cat .frontend.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "Stopped Frontend (PID: $PID)"
    fi
    rm -f .frontend.pid
fi

# Fallback kill matching processes if pid files missing
pkill -f "uvicorn app.main:app" || true
pkill -f "vite" || true

echo "KRISHIGUARD services stopped successfully."
