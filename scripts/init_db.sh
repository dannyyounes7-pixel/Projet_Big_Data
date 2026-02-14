#!/bin/bash
# Initialize PostgreSQL Database

echo "=========================================="
echo "Initializing IAR Platform Database"
echo "=========================================="

# Database configuration (adjust as needed)
DB_NAME="iar_db"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"

# Create database if it doesn't exist
echo "Creating database $DB_NAME..."
psql -U $DB_USER -h $DB_HOST -p $DB_PORT -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
    psql -U $DB_USER -h $DB_HOST -p $DB_PORT -c "CREATE DATABASE $DB_NAME"

# Execute DDL script
echo "Creating tables..."
psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d $DB_NAME -f src/sql/create_tables.sql

# Check exit code
if [ $? -eq 0 ]; then
    echo "=========================================="
    echo "Database initialized successfully"
    echo "=========================================="
else
    echo "=========================================="
    echo "Database initialization failed!"
    echo "=========================================="
    exit 1
fi
