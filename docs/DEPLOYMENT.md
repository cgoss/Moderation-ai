# Deployment Guide

## Overview

This guide provides instructions for deploying Moderation Bot to staging and production environments.

## Prerequisites

- Docker and Docker Compose installed
- Access to target server (SSH)
- Environment variables configured
- Database credentials ready
- API keys for all platforms

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/moderation-bot.git
cd moderation-bot
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.template .env.production

# Edit with your values
nano .env.production
```

Required environment variables:
- `ENVIRONMENT` - Set to 'staging' or 'production'
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `INSTAGRAM_ACCESS_TOKEN` - Instagram API token
- `MEDIUM_ACCESS_TOKEN` - Medium API token
- `TIKTOK_ACCESS_TOKEN` - TikTok API token
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `SECRET_KEY` - Application secret key

### 3. Configure GitHub Secrets

Add the following secrets to GitHub repository:

**Staging:**
- `STAGING_HOST` - Staging server host
- `STAGING_USER` - SSH username
- `STAGING_SSH_KEY` - SSH private key
- `STAGING_URL` - Staging URL
- `SLACK_WEBHOOK` - Slack notification webhook

**Production:**
- `PRODUCTION_HOST` - Production server host
- `PRODUCTION_USER` - SSH username
- `PRODUCTION_SSH_KEY` - SSH private key
- `PRODUCTION_URL` - Production URL
- `SLACK_WEBHOOK` - Slack notification webhook
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub password

## Deployment Methods

### Method 1: Automated Deployment (Recommended)

#### Deploy to Staging

Staging deployments are automatic on push to `develop` branch:

```bash
git checkout develop
git push origin develop
```

Or manually trigger via GitHub Actions:
1. Go to Actions tab
2. Select "CD - Deploy to Staging"
3. Click "Run workflow"
4. Select environment: staging
5. Click "Run workflow"

#### Deploy to Production

Production deployments require manual trigger:

1. Create and push a tag:
```bash
git tag v1.0.0
git push origin v1.0.0
```

2. Or manually trigger via GitHub Actions:
- Go to Actions tab
- Select "CD - Deploy to Production"
- Click "Run workflow"
- Enter version number
- Type "PRODUCTION" to confirm
- Click "Run workflow"

### Method 2: Manual Deployment

Use the deployment script for manual control:

```bash
# Deploy to staging
./scripts/deploy.sh staging

# Deploy to production
./scripts/deploy.sh production
```

The script will:
1. Pull latest code
2. Create backup of data and database
3. Build Docker images
4. Stop existing containers
5. Start new containers
6. Run health checks
7. Rollback if health checks fail

## Monitoring

### Health Checks

```bash
# Run health check script
./scripts/health_check.py

# Or check manually
curl http://localhost:8000/health
```

### View Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f web

# View last 100 lines
docker-compose logs --tail=100 web
```

### Monitor Metrics

Access Grafana dashboard:
- URL: http://your-server:3000
- Default credentials: admin/admin

Access Prometheus:
- URL: http://your-server:9090

## Troubleshooting

### Container Won't Start

```bash
# Check container logs
docker-compose logs web

# Check if port is in use
lsof -i :8000

# Restart services
docker-compose restart
```

### Database Connection Issues

```bash
# Check database logs
docker-compose logs postgres

# Test database connection
docker-compose exec postgres psql -U moderation_user -d moderation_bot

# Restart database
docker-compose restart postgres
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Restart containers
docker-compose restart

# Scale down workers
# Edit docker-compose.yml and reduce WORKERS
```

### Rollback Deployment

```bash
# List available backups
ls -la backups/

# Rollback to specific backup
./scripts/rollback.sh 20240108_120000

# Or manually
docker-compose down
# Restore data from backup
docker-compose up -d
```

## Maintenance

### Backup Strategy

Automated backups are created during deployment:
- Data backups: `./backups/data_<timestamp>/`
- Database dumps: `./backups/db_<timestamp>.sql`

Manual backup:
```bash
# Backup data
cp -r ./data ./backups/data_manual_$(date +%Y%m%d_%H%M%S)

# Backup database
docker-compose exec -T postgres pg_dump -U moderation_user moderation_bot > backups/db_manual_$(date +%Y%m%d_%H%M%S).sql
```

### Cleanup

```bash
# Remove old Docker images
docker image prune -a

# Remove unused volumes
docker volume prune

# Clean up old backups (keep last 5)
cd backups
ls -t | tail -n +6 | xargs -I {} rm -rf {}
```

## Security

### SSL/TLS

For production, enable HTTPS:

1. Install Certbot:
```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
```

2. Obtain certificate:
```bash
sudo certbot --nginx -d your-domain.com
```

3. Update nginx configuration to use HTTPS

4. Auto-renew certificates:
```bash
sudo certbot renew --dry-run
```

### Firewall

Configure firewall rules:
```bash
# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Allow SSH
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

## Scaling

### Horizontal Scaling

Increase replicas in `docker-compose.yml`:

```yaml
web:
  deploy:
    replicas: 3
```

### Vertical Scaling

Increase resources in `docker-compose.yml`:

```yaml
web:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
      reservations:
        cpus: '1'
        memory: 1G
```

## Support

For deployment issues:
1. Check logs: `docker-compose logs`
2. Run health check: `./scripts/health_check.py`
3. Review GitHub Actions logs
4. Contact support team

## Checklist

Before deploying to production:

- [ ] All tests passing
- [ ] Staging deployment successful
- [ ] Database migrations tested
- [ ] Backups verified
- [ ] SSL certificate configured
- [ ] Firewall rules configured
- [ ] Monitoring dashboards configured
- [ ] Alert notifications set up
- [ ] Rollback procedure tested
- [ ] Team notified of deployment

---

**Last Updated**: January 8, 2026
