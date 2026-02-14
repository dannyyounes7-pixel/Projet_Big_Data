#!/bin/bash
# Run Datamart Job (GOLD Layer Creation)

# Get current date
RUN_DATE=$(date +%Y-%m-%d)

echo "=========================================="
echo "Running Datamart Job"
echo "Date: $RUN_DATE"
echo "=========================================="

# Run spark-submit
spark-submit \
    --master local[*] \
    --driver-memory 4g \
    --executor-memory 4g \
    --jars /path/to/postgresql-jdbc-driver.jar \
    src/jobs/datamart.py \
    --config config/app.yaml \
    --run_date $RUN_DATE

# Check exit code
if [ $? -eq 0 ]; then
    echo "=========================================="
    echo "Datamart job completed successfully"
    echo "=========================================="
else
    echo "=========================================="
    echo "Datamart job failed!"
    echo "=========================================="
    exit 1
fi
