@echo off
setlocal

rem ------------------------------------------------------------
rem 1️⃣ Start the backend (FastAPI) – try the packaged .exe first
rem ------------------------------------------------------------
if exist "%~dp0dist\krishiguard_backend.exe" (
    echo Starting backend (executable)...
    start "" "%~dp0dist\krishiguard_backend.exe"
) else (
    echo Backend executable not found – falling back to Python interpreter.
    if exist "%~dp0\.venv\Scripts\python.exe" (
        echo Using virtual‑env Python to launch FastAPI
        start "" "%~dp0\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
    ) else (
        echo [ERROR] No Python interpreter or backend executable found. Please run `pyinstaller` or activate the venv.
    )
)

rem ------------------------------------------------------------
rem 2️⃣ Start the frontend (Vite dev server)
rem ------------------------------------------------------------
pushd "%~dp0frontend"
if not exist node_modules (
    echo Installing frontend dependencies...
    npm install
)
echo Starting frontend dev server...
npm run dev
popd

endlocal
