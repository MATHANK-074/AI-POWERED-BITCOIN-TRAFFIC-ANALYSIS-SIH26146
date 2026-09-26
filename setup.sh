#!/usr/bin/env bash
# Setup script for Crypto Analytics on Linux / WSL2 / Debian / Kali

set -e

echo "========================================================"
echo " Setting up Offline Bitcoin Forensic Platform"
echo "========================================================"

# Create required project directories
mkdir -p data/raw data/processed data/external data/outputs models logs reports

# 1. Setup Python Virtual Environment
echo "[1/3] Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Created virtual environment in .venv"
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# 2. Setup Frontend Dependencies
echo "[2/3] Installing Frontend Node.js dependencies..."
if command -v npm &> /dev/null; then
    cd frontend
    npm install
    cd ..
else
    echo "WARNING: npm is not installed. Please install Node.js/npm to run the frontend."
fi

# 3. Generate Sample Synthetic Dataset for Testing
echo "[3/3] Preparing initial test dataset..."
python3 -m scripts.generate_dataset --records 5000 || echo "Dataset script skipped"

echo "========================================================"
echo " Setup complete! Start system using: ./start.sh"
echo "========================================================"
