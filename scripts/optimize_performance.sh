#!/bin/bash

# Performance Optimization Script

set -e

echo "=================================="
echo "Performance Optimization"
echo "=================================="
echo ""

# Check 1: Database optimization
echo "1. Database Optimization"
echo "--------------------------------"
docker-compose exec -T postgres psql -U moderation_user -d moderation_bot <<EOF
-- Analyze table statistics
ANALYZE;

-- Update table statistics
VACUUM ANALYZE;

-- Reclaim storage
VACUUM FULL;

-- Reindex tables
REINDEX DATABASE moderation_bot;

-- Check for missing indexes
SELECT 
    schemaname,
    tablename,
    seq_scan,
    idx_scan,
    seq_scan / (seq_scan + idx_scan) AS seq_scan_ratio
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_scan_ratio DESC
LIMIT 10;
EOF
echo "✓ Database optimized"
echo ""

# Check 2: Redis optimization
echo "2. Redis Optimization"
echo "--------------------------------"
docker-compose exec -T redis redis-cli <<EOF
-- Check memory usage
INFO memory

-- Check eviction policy
CONFIG GET maxmemory-policy

-- Clear expired keys (if any)
-- FLUSHALL  # Uncomment carefully

-- Save data
SAVE
EOF
echo "✓ Redis optimized"
echo ""

# Check 3: Clear application cache
echo "3. Cache Clearing"
echo "--------------------------------"
if [ -d "./cache" ]; then
    # Remove cache files older than 1 hour
    find ./cache -type f -mmin +60 -delete
    CACHE_SIZE=$(du -sh ./cache | cut -f1)
    echo "✓ Cache cleared (current size: $CACHE_SIZE)"
else
    echo "⚠ Cache directory not found"
fi
echo ""

# Check 4: Compress logs
echo "4. Log Compression"
echo "--------------------------------"
if [ -d "./logs" ]; then
    # Compress logs older than 7 days
    find ./logs -name "*.log" -mtime +7 -exec gzip {} \;
    # Remove compressed logs older than 30 days
    find ./logs -name "*.gz" -mtime +30 -delete
    LOG_SIZE=$(du -sh ./logs | cut -f1)
    echo "✓ Logs compressed (current size: $LOG_SIZE)"
else
    echo "⚠ Logs directory not found"
fi
echo ""

# Check 5: Clear old backups
echo "5. Backup Cleanup"
echo "--------------------------------"
if [ -d "./backups" ]; then
    # Keep last 10 backups
    cd backups
    ls -t | tail -n +11 | xargs -I {} rm -rf {}
    cd ..
    BACKUP_SIZE=$(du -sh ./backups | cut -f1)
    echo "✓ Old backups removed (current size: $BACKUP_SIZE)"
else
    echo "⚠ Backups directory not found"
fi
echo ""

# Check 6: Docker image cleanup
echo "6. Docker Cleanup"
echo "--------------------------------"
# Remove dangling images
docker image prune -f
# Remove unused volumes
docker volume prune -f
# Remove unused containers
docker container prune -f
echo "✓ Docker resources cleaned"
echo ""

# Check 7: System resources check
echo "7. System Resources Check"
echo "--------------------------------"
if command -v free &> /dev/null; then
    FREE_MEM=$(free -h | awk '/Mem:/ {print $7}')
    TOTAL_MEM=$(free -h | awk '/Mem:/ {print $2}')
    echo "Memory: $FREE_MEM free of $TOTAL_MEM"
fi

if command -v df &> /dev/null; then
    DISK_USAGE=$(df -h /app | awk 'NR==2 {print $5}')
    echo "Disk: $DISK_USAGE used"
fi

if command -v nproc &> /dev/null; then
    CPUS=$(nproc)
    echo "CPU cores: $CPUS"
fi
echo ""

# Check 8: Network optimization check
echo "8. Network Optimization Check"
echo "--------------------------------"
if command -v docker &> /dev/null; then
    # Check for connection limits
    docker info | grep -A 3 "IPv4Forwarding"
    
    # Check MTU
    docker info | grep -A 3 "MTU"
fi
echo ""

# Check 9: Application restart
echo "9. Application Restart"
echo "--------------------------------"
docker-compose restart web
sleep 10
docker-compose ps web
echo "✓ Application restarted"
echo ""

# Check 10: Health verification
echo "10. Health Verification"
echo "--------------------------------"
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Web service is healthy"
else
    echo "✗ Web service health check failed"
fi

if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis is healthy"
else
    echo "✗ Redis health check failed"
fi

if docker-compose exec -T postgres pg_isready -U moderation_user -d moderation_bot > /dev/null 2>&1; then
    echo "✓ Database is healthy"
else
    echo "✗ Database health check failed"
fi
echo ""

echo "=================================="
echo "Performance Optimization Complete"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Monitor performance metrics for next 24 hours"
echo "2. Check Grafana dashboards: http://localhost:3000"
echo "3. Review logs: docker-compose logs -f --tail=100"
echo "4. Schedule next optimization in 1 week"
