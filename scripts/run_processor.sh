#!/bin/bash
# Run Processor Job (SILVER Layer Processing)

# Get current date
RUN_DATE=$(date +%Y-%m-%d)

echo "=========================================="
echo "Running Processor Job"
echo "Date: $RUN_DATE"
echo "=========================================="

# Run spark-submit
spark-submit \
    --master local[*] \
    --driver-memory 4g \
    --executor-memory 4g \
    --conf spark.sql.shuffle.partitions=200 \
    src/jobs/processor.py \
    --config config/app.yaml \
    --run_date $RUN_DATE

# Check exit code
if [ $? -eq 0 ]; then
    echo "=========================================="
    echo "Processor job completed successfully"
    echo "=========================================="
else
    echo "=========================================="
    echo "Processor job failed!"
    echo "=========================================="
    exit 1
fi
