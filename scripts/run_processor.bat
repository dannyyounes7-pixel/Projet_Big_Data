@echo off
REM Run Processor Job (SILVER Layer) - Windows Version

REM Get current date
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)

echo ==========================================
echo Running Processor Job
echo Date: %mydate%
echo ==========================================

REM Run spark-submit
spark-submit ^
    --master local[*] ^
    --driver-memory 4g ^
    --executor-memory 4g ^
    --conf spark.sql.shuffle.partitions=200 ^
    src/jobs/processor.py ^
    --config config/app.yaml ^
    --run_date %mydate%

if %ERRORLEVEL% EQU 0 (
    echo ==========================================
    echo Processor job completed successfully
    echo ==========================================
) else (
    echo ==========================================
    echo Processor job failed!
    echo ==========================================
    exit /b 1
)
