#!/bin/bash
# Run Feeder Job (RAW Layer Ingestion)

# Get current date
RUN_DATE=$(date +%Y-%m-%d)

echo "=========================================="
echo "Running Feeder Job"
echo "Date: $RUN_DATE"
echo "=========================================="

# Run spark-submit
spark-submit \
    --master local[*] \
    --driver-memory 4g \
    --executor-memory 4g \
    src/jobs/feeder.py \
    --config config/app.yaml \
    --run_date $RUN_DATE

# Check exit code
if [ $? -eq 0 ]; then
    echo "=========================================="
    echo "Feeder job completed successfully"
    echo "=========================================="
else
    echo "=========================================="
    echo "Feeder job failed!"
    echo "=========================================="
    exit 1
fi
