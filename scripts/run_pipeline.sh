#!/bin/bash
# Run Complete Pipeline (RAW -> SILVER -> GOLD)

# Get current date
RUN_DATE=$(date +%Y-%m-%d)

echo "=========================================="
echo "Running Complete IAR Pipeline"
echo "Date: $RUN_DATE"
echo "=========================================="

# Step 1: Feeder
echo ""
echo "Step 1/3: Running Feeder (RAW Layer)..."
./scripts/run_feeder.sh
if [ $? -ne 0 ]; then
    echo "Pipeline failed at Feeder step"
    exit 1
fi

# Step 2: Processor
echo ""
echo "Step 2/3: Running Processor (SILVER Layer)..."
./scripts/run_processor.sh
if [ $? -ne 0 ]; then
    echo "Pipeline failed at Processor step"
    exit 1
fi

# Step 3: Datamart
echo ""
echo "Step 3/3: Running Datamart (GOLD Layer)..."
./scripts/run_datamart.sh
if [ $? -ne 0 ]; then
    echo "Pipeline failed at Datamart step"
    exit 1
fi

echo ""
echo "=========================================="
echo "Pipeline completed successfully!"
echo "=========================================="
