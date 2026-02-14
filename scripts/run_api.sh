#!/bin/bash
# Run API Server

echo "=========================================="
echo "Starting IAR Platform API"
echo "=========================================="

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run uvicorn server
uvicorn api.app:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload

# Note: Use --reload only in development
# For production, remove --reload and add --workers 4
