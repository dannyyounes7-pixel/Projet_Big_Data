@echo off
REM Run Feeder Job (RAW Layer Ingestion) - Windows Version

REM Get current date
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)

echo ==========================================
echo Running Feeder Job
echo Date: %mydate%
echo ==========================================

REM Run spark-submit
spark-submit ^
    --master local[*] ^
    --driver-memory 4g ^
    --executor-memory 4g ^
    src/jobs/feeder.py ^
    --config config/app.yaml ^
    --run_date %mydate%

if %ERRORLEVEL% EQU 0 (
    echo ==========================================
    echo Feeder job completed successfully
    echo ==========================================
) else (
    echo ==========================================
    echo Feeder job failed!
    echo ==========================================
    exit /b 1
)
