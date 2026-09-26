#!/usr/bin/env bash
# --------------------------------------------------------------
# Linux launcher for the KRISHIGUARD offline system
# --------------------------------------------------------------
set -e                                   # abort on any error
cd "$(dirname "$0")"                     # ensure we are in the repo root

# ---------- 1️⃣ Activate the Python virtual‑env (if present) ----------
if [ -d ".venv" ]; then
  echo "Activating Python venv …"
  source .venv/bin/activate
else
  echo "[WARN] No .venv found – make sure Python dependencies are installed."
fi

# ---------- 2️⃣ Start the FastAPI backend ----------
echo "Starting backend (uvicorn) …"
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "  → Backend PID $BACKEND_PID"

# ---------- 3️⃣ Start the Vite dev server ----------
cd frontend

if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies …"
  npm install
fi

echo "Starting frontend (Vite) …"
npm run dev -- --host 0.0.0.0 &
FRONTEND_PID=$!
echo "  → Frontend PID $FRONTEND_PID"

# --------------------------------------------------------------
# Keep the script alive while both processes run.
# Press Ctrl‑C to stop everything.
# --------------------------------------------------------------
trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null' SIGINT SIGTERM

wait $BACKEND_PID
wait $FRONTEND_PID
