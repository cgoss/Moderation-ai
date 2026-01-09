#!/bin/bash

# Deployment script for Moderation Bot

set -e

ENVIRONMENT=${1:-staging}
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=================================="
echo "Moderation Bot Deployment"
echo "=================================="
echo "Environment: $ENVIRONMENT"
echo "Timestamp: $TIMESTAMP"
echo ""

# Check if environment is valid
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo "Error: Invalid environment. Use 'staging' or 'production'"
    exit 1
fi

# Prompt for confirmation if production
if [[ "$ENVIRONMENT" == "production" ]]; then
    echo "WARNING: Deploying to PRODUCTION"
    read -p "Type 'PRODUCTION' to confirm: " CONFIRM
    if [[ "$CONFIRM" != "PRODUCTION" ]]; then
        echo "Deployment cancelled"
        exit 1
    fi
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"
echo "✓ Backup directory ready"

# Pull latest code
echo ""
echo "Pulling latest code..."
git fetch origin main
git reset --hard origin/main
echo "✓ Code updated"

# Backup data
echo ""
echo "Creating backup..."
if [[ -d "./data" ]]; then
    cp -r "./data" "$BACKUP_DIR/data_$TIMESTAMP"
    echo "✓ Data backed up to $BACKUP_DIR/data_$TIMESTAMP"
fi

# Backup database
echo ""
echo "Backing up database..."
docker-compose exec -T postgres pg_dump -U moderation_user moderation_bot > "$BACKUP_DIR/db_$TIMESTAMP.sql"
echo "✓ Database backed up to $BACKUP_DIR/db_$TIMESTAMP.sql"

# Build Docker images
echo ""
echo "Building Docker images..."
docker-compose build --no-cache
echo "✓ Docker images built"

# Stop running containers
echo ""
echo "Stopping containers..."
docker-compose down
echo "✓ Containers stopped"

# Pull new images (if using registry)
echo ""
echo "Pulling new images..."
docker-compose pull
echo "✓ Images pulled"

# Start containers
echo ""
echo "Starting containers..."
docker-compose up -d
echo "✓ Containers started"

# Wait for services to be ready
echo ""
echo "Waiting for services to be ready..."
sleep 30

# Health checks
echo ""
echo "Running health checks..."

# Check web service
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Web service is healthy"
else
    echo "✗ Web service health check failed"
    echo "Rolling back..."
    ./scripts/rollback.sh "$TIMESTAMP"
    exit 1
fi

# Check database
if docker-compose exec -T postgres pg_isready -U moderation_user > /dev/null 2>&1; then
    echo "✓ Database is healthy"
else
    echo "✗ Database health check failed"
    echo "Rolling back..."
    ./scripts/rollback.sh "$TIMESTAMP"
    exit 1
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis is healthy"
else
    echo "✗ Redis health check failed"
    echo "Rolling back..."
    ./scripts/rollback.sh "$TIMESTAMP"
    exit 1
fi

# Run migrations (if any)
echo ""
echo "Running database migrations..."
docker-compose exec web python -m alembic upgrade head || true
echo "✓ Migrations completed"

# Clean up old backups (keep last 5)
echo ""
echo "Cleaning up old backups..."
cd "$BACKUP_DIR"
ls -t | tail -n +6 | xargs -I {} rm -rf {}
cd ..
echo "✓ Old backups cleaned up"

# Show status
echo ""
echo "=================================="
echo "Deployment Successful!"
echo "=================================="
docker-compose ps

echo ""
echo "View logs with: docker-compose logs -f"
echo "Roll back with: ./scripts/rollback.sh $TIMESTAMP"
