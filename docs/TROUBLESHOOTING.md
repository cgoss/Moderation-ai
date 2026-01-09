# Moderation Bot - Troubleshooting Guide

## Common Issues

### Installation Problems

#### Issue: Docker Compose Won't Start

**Symptoms:**
- Error: "Cannot connect to Docker daemon"
- Services fail to start
- Port already in use errors

**Solutions:**

1. Check Docker status:
```bash
docker info
docker version
```

2. Restart Docker daemon:
```bash
# Linux
sudo systemctl restart docker

# macOS
open -a Docker

# Windows
Restart Docker Desktop
```

3. Check for port conflicts:
```bash
lsof -i :8000
lsof -i :5432
lsof -i :6379
```

4. Kill conflicting processes:
```bash
kill -9 <PID>
```

#### Issue: Module Import Errors

**Symptoms:**
- `ModuleNotFoundError: No module named 'pydantic'`
- `ImportError: cannot import name 'X'`

**Solutions:**

1. Install missing dependencies:
```bash
pip install -r requirements.txt
```

2. Verify Python version:
```bash
python --version  # Should be 3.9+
```

3. Reinstall in virtual environment:
```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

### API Connection Problems

#### Issue: Platform API Authentication Failed

**Symptoms:**
- "Invalid access token" errors
- 401 Unauthorized responses
- Token refresh failures

**Solutions:**

1. Verify API credentials:
```bash
# Check environment variables
docker-compose exec web env | grep API_KEY

# Test token manually
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://graph.instagram.com/me
```

2. Check token expiration:
```python
from src.core.auth import TokenManager

manager = TokenManager()
print(f"Token expires: {manager.get_token_expiration()}")
```

3. Regenerate tokens:
- Go to platform developer portal
- Generate new access token
- Update environment variables
- Restart application

#### Issue: Rate Limit Exceeded

**Symptoms:**
- 429 Too Many Requests errors
- API calls failing after working
- Rate limit errors in logs

**Solutions:**

1. Check rate limit status:
```bash
curl -H "X-RateLimit-Remaining" \
  https://api.example.com/endpoint
```

2. Implement proper rate limiting:
```python
from src.core.rate_limiter import RateLimiter

limiter = RateLimiter(requests_per_minute=60)
```

3. Use caching to reduce API calls:
```python
from src.core.cache import CacheManager

cache = CacheManager()

# Check cache first
result = cache.get('key')
if not result:
    result = api_call()
    cache.set('key', result, ttl=300)
```

4. Batch operations:
```python
# Instead of single requests
comments = []
for i in range(0, 100, 10):
    comments += fetch_comments(i, i+10)
```

### Database Problems

#### Issue: Database Connection Failed

**Symptoms:**
- "Could not connect to database"
- "Connection refused" errors
- Timeout errors

**Solutions:**

1. Check database is running:
```bash
docker-compose ps postgres

# Check logs
docker-compose logs postgres
```

2. Verify connection string:
```bash
# Check environment variable
docker-compose exec web env | grep DATABASE_URL

# Test connection
docker-compose exec -T postgres psql -U moderation_user -d moderation_bot -c "SELECT 1"
```

3. Check network connectivity:
```bash
# Test from application container
docker-compose exec web ping postgres

# Test network connection
telnet postgres 5432
```

4. Restart database:
```bash
docker-compose restart postgres

# Force restart
docker-compose down
docker-compose up -d
```

#### Issue: Database Performance Slow

**Symptoms:**
- Queries taking >5 seconds
- Timeouts during peak usage
- High CPU usage

**Solutions:**

1. Check slow queries:
```sql
EXPLAIN ANALYZE SELECT * FROM comments WHERE created_at > NOW() - INTERVAL '1 day';
```

2. Add missing indexes:
```sql
CREATE INDEX idx_comments_created_at ON comments(created_at);
CREATE INDEX idx_comments_user_id ON comments(user_id);
```

3. Optimize queries:
```python
# Use select_related in Django/ORM
# Use join instead of subqueries
# Use EXISTS instead of IN
```

4. Increase connection pool:
```python
DATABASE_CONFIG = {
    'pool_size': 20,
    'max_overflow': 10,
    'pool_timeout': 30
}
```

### Cache Problems

#### Issue: Redis Connection Failed

**Symptoms:**
- "Could not connect to Redis"
- Cache not working
- Errors in cache operations

**Solutions:**

1. Check Redis is running:
```bash
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping
```

2. Verify connection string:
```bash
# Check environment variable
docker-compose exec web env | grep REDIS_URL
```

3. Check Redis logs:
```bash
docker-compose logs redis --tail=50
```

4. Clear corrupted cache:
```bash
docker-compose exec redis redis-cli FLUSHALL
```

### Monitoring Problems

#### Issue: Metrics Not Showing in Grafana

**Symptoms:**
- No data in dashboards
- "No data" errors
- Metrics not being collected

**Solutions:**

1. Check Prometheus is scraping:
```bash
# Check Prometheus logs
docker-compose logs prometheus

# Test scrape
curl http://localhost:9090/api/v1/targets
```

2. Verify Prometheus configuration:
```bash
# Check config
cat prometheus.yml

# Check rules
cat prometheus/rules.yml
```

3. Check application metrics endpoint:
```bash
curl http://localhost:8000/metrics
```

4. Restart Prometheus:
```bash
docker-compose restart prometheus
```

#### Issue: Alerts Not Firing

**Symptoms:**
- Expected alert doesn't trigger
- No Slack notifications
- Alert not in Prometheus

**Solutions:**

1. Check alert rules:
```bash
# Test expression
curl http://localhost:9090/api/v1/query?query=rate(http_requests_total[5m])
```

2. Verify alertmanager config:
```bash
# Check Alertmanager logs
docker-compose logs alertmanager
```

3. Test alert firing:
```python
# Trigger alert condition
# Wait for alert
# Check notifications
```

### Deployment Problems

#### Issue: Deployment Fails Health Check

**Symptoms:**
- Health check returns unhealthy
- Deployment rolls back automatically
- Services won't start

**Solutions:**

1. Check application logs:
```bash
docker-compose logs web --tail=100
```

2. Check all services health:
```bash
docker-compose ps

# Check each service
docker-compose exec web curl -f http://localhost:8000/health
docker-compose exec postgres pg_isready -U moderation_user
docker-compose exec redis redis-cli ping
```

3. Check resource limits:
```bash
docker stats
```

4. Manual health check:
```bash
./scripts/health_check.py
```

5. Rollback if needed:
```bash
# Find previous backup
ls -la backups/

# Rollback
./scripts/rollback.sh <TIMESTAMP>
```

### Security Problems

#### Issue: Webhook Signature Verification Failed

**Symptoms:**
- "Invalid signature" errors
- Webhook events rejected
- Platform errors in logs

**Solutions:**

1. Verify webhook secret:
```bash
# Check environment variable
docker-compose exec web env | grep WEBHOOK_SECRET
```

2. Test webhook signature:
```python
import hmac
import hashlib

secret = b'your-secret'
payload = b'test-payload'
signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
print(f"Signature: {signature}")
```

3. Verify platform IP whitelist:
```bash
# Check if webhook IP is whitelisted
# Go to platform developer portal
# Check webhook settings
```

#### Issue: SSL/TLS Certificate Expired

**Symptoms:**
- "Certificate has expired" errors
- Browser warnings
- Connections rejected

**Solutions:**

1. Check certificate expiration:
```bash
echo | openssl s_client -connect localhost:443 -servername localhost 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep notAfter
```

2. Renew certificate (if using Let's Encrypt):
```bash
sudo certbot renew --force-renewal
```

3. Update configuration:
```bash
# Copy new certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /etc/nginx/ssl/

# Restart nginx
sudo systemctl restart nginx
```

4. Test new certificate:
```bash
curl -I https://your-domain.com/health
```

### Performance Problems

#### Issue: High Memory Usage

**Symptoms:**
- Container killed for OOM
- System running slow
- Swap usage high

**Solutions:**

1. Check memory usage:
```bash
docker stats --no-stream
```

2. Identify memory-intensive operations:
```python
# Check for large datasets in memory
# Check for memory leaks
# Monitor garbage collection
```

3. Optimize memory usage:
```python
# Use generators instead of lists
# Process data in batches
# Clear cache regularly
```

4. Increase memory limits:
```yaml
# docker-compose.yml
web:
  deploy:
    resources:
      limits:
        memory: 2G
      reservations:
        memory: 1G
```

#### Issue: High CPU Usage

**Symptoms:**
- 100% CPU usage
- Slow response times
- Timeouts

**Solutions:**

1. Check CPU usage:
```bash
docker stats --no-stream
```

2. Identify CPU-intensive operations:
```python
# Check for tight loops
# Monitor LLM API calls
# Check database query performance
```

3. Optimize CPU usage:
```python
# Add caching
# Use async operations
# Implement pagination
```

4. Add more workers:
```yaml
# docker-compose.yml
web:
  deploy:
    replicas: 3
```

## Error Codes Reference

### Application Errors

| Code | Description | HTTP Status | Solution |
|-------|-------------|--------------|----------|
| 1001 | Invalid API key | 401 | Regenerate API key |
| 1002 | Rate limit exceeded | 429 | Wait and retry |
| 1003 | Invalid request | 400 | Check request format |
| 1004 | Authentication failed | 401 | Refresh token |
| 1005 | Platform API error | 502 | Check platform status |
| 1006 | Database error | 500 | Check database logs |
| 1007 | Cache error | 500 | Restart Redis |
| 1008 | LLM API error | 502 | Check LLM status |

### Platform API Errors

| Platform | Code | Description | Solution |
|----------|-------|-------------|----------|
| Instagram | 190 | Subscribtion rate limit | Wait and retry |
| Instagram | 429 | Rate limit exceeded | Use caching |
| Instagram | 400 | Invalid request | Check request body |
| Medium | 401 | Unauthorized | Refresh OAuth token |
| Medium | 403 | Forbidden | Check permissions |
| TikTok | 429 | Rate limit exceeded | Use caching |
| TikTok | 401 | Invalid token | Refresh OAuth token |

## Debugging

### Enable Debug Logging

```bash
# Set debug level
export LOG_LEVEL=debug

# Or in .env
echo "LOG_LEVEL=debug" >> .env

# Restart application
docker-compose restart web
```

### View Application Logs

```bash
# All logs
docker-compose logs -f --tail=100

# Specific service
docker-compose logs web --tail=50

# Last 1000 lines
docker-compose logs web | tail -n 1000

# Follow logs
docker-compose logs -f web
```

### Use Debug Mode

```python
# Enable debug mode in config
app.run(debug=True)

# Add debug prints
import logging
logging.basicConfig(level=logging.DEBUG)

# Use pdb for debugging
import pdb; pdb.set_trace()
```

### Test API Endpoints Manually

```bash
# Health check
curl http://localhost:8000/health

# Metrics
curl http://localhost:8000/metrics

# API endpoint
curl -X POST http://localhost:8000/api/v1/test \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## Getting Help

### Check Documentation

- [Quick Start Guide](QUICK_START.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Operations Guide](OPERATIONS.md)
- [Security Guide](SECURITY.md)
- [API Documentation](API.md)
- [Platform Documentation](platforms/)

### Search Issues

1. Check existing GitHub issues:
   ```bash
   gh issue list
   ```

2. Search for similar problems:
   ```bash
   gh issue search "error message"
   ```

3. Check closed issues for solutions:
   ```bash
   gh issue list --state closed | grep "similar"
   ```

### Create New Issue

Include in your issue:
1. Clear description
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Environment details
6. Logs or screenshots
7. Error messages

Issue template:
```markdown
## Description
Brief description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.10]
- Docker version: [e.g., 24.0.0]
- Browser: [e.g., Chrome 120]

## Logs
```
ERROR: error message here
```

## Screenshots
If applicable, add screenshots

## Additional Context
Any other relevant information
```

## Contact Support

- **GitHub Issues**: Create new issue for bugs
- **GitHub Discussions**: For questions and help
- **Email**: security@example.com (for security issues only)
- **Documentation**: Check existing docs first

---

**Troubleshooting Guide v1.0** - Last Updated: January 8, 2026
