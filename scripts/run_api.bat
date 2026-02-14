@echo off
REM Run API Server - Windows Version

echo ==========================================
echo Starting IAR Platform API
echo ==========================================

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run uvicorn server
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload

REM Note: Use --reload only in development
