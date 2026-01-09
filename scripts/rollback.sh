#!/bin/bash

# Rollback script for Moderation Bot

set -e

TIMESTAMP=$1
BACKUP_DIR="./backups"

if [[ -z "$TIMESTAMP" ]]; then
    echo "Error: No timestamp provided"
    echo "Usage: ./rollback.sh <timestamp>"
    echo "Example: ./rollback.sh 20240108_120000"
    exit 1
fi

echo "=================================="
echo "Moderation Bot Rollback"
echo "=================================="
echo "Backup Timestamp: $TIMESTAMP"
echo ""

# Check if backup exists
if [[ ! -d "$BACKUP_DIR/data_$TIMESTAMP" ]]; then
    echo "Error: Backup not found at $BACKUP_DIR/data_$TIMESTAMP"
    exit 1
fi

# Confirm rollback
read -p "Are you sure you want to rollback to $TIMESTAMP? (yes/no): " CONFIRM
if [[ "$CONFIRM" != "yes" ]]; then
    echo "Rollback cancelled"
    exit 0
fi

# Stop containers
echo "Stopping containers..."
docker-compose down
echo "✓ Containers stopped"

# Restore data
echo "Restoring data from backup..."
if [[ -d "./data" ]]; then
    mv "./data" "./data.failed"
fi
cp -r "$BACKUP_DIR/data_$TIMESTAMP" "./data"
echo "✓ Data restored"

# Restore database
if [[ -f "$BACKUP_DIR/db_$TIMESTAMP.sql" ]]; then
    echo "Restoring database from backup..."
    docker-compose up -d postgres
    sleep 10
    docker-compose exec -T postgres psql -U moderation_user -d moderation_bot < "$BACKUP_DIR/db_$TIMESTAMP.sql"
    echo "✓ Database restored"
fi

# Start containers
echo "Starting containers..."
docker-compose up -d
echo "✓ Containers started"

# Wait for services
echo "Waiting for services..."
sleep 30

# Health checks
echo "Running health checks..."

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Web service is healthy"
else
    echo "✗ Web service health check failed"
    exit 1
fi

echo ""
echo "=================================="
echo "Rollback Successful!"
echo "=================================="
docker-compose ps

echo ""
echo "To undo rollback, you may need to restore from a more recent backup"
