#!/usr/bin/env bash
# 1-Click Launcher for KrishiGuard Forensic Workstation (Linux / Ubuntu / Kali)

set -e

echo "=========================================================="
echo " Starting KrishiGuard Offline Forensic Platform... "
echo "=========================================================="

# 1. Setup Virtual Environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "First time setup detected! Installing dependencies..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r backend/requirements.txt
else
    source .venv/bin/activate
fi

# 2. Kill any existing instances on port 8000
echo "Starting backend server..."
fuser -k 8000/tcp 2>/dev/null || true

# 3. Start the FastAPI backend (which now also serves the React frontend)
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

echo "Server started successfully!"

# 4. Give the server a few seconds to boot up
sleep 3

# 5. Automatically open the browser to the application
echo "Opening KrishiGuard in your default web browser..."
if which xdg-open > /dev/null
then
  xdg-open http://127.0.0.1:8000/
elif which gnome-open > /dev/null
then
  gnome-open http://127.0.0.1:8000/
else
  echo "Could not detect web browser. Please manually open: http://127.0.0.1:8000/"
fi

# 6. Wait for the server process (keeps script alive)
wait $SERVER_PID
