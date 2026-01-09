# Moderation Bot - Quick Start Guide

Get up and running with Moderation Bot in 5 minutes.

## Prerequisites

- Docker installed
- Python 3.10+ (for local development)
- Platform API keys (Instagram, Medium, TikTok)
- LLM API keys (OpenAI, Anthropic)

## Option 1: Docker Quick Start (Recommended)

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/moderation-bot.git
cd moderation-bot
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.template .env.local

# Edit with your values
nano .env.local
```

Required configuration:
```env
ENVIRONMENT=development
LOG_LEVEL=info

# Platform API Keys
INSTAGRAM_ACCESS_TOKEN=your-instagram-token
MEDIUM_ACCESS_TOKEN=your-medium-token
TIKTOK_ACCESS_TOKEN=your-tiktok-token

# LLM API Keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Database (optional, defaults to SQLite)
# DATABASE_URL=sqlite:///data/moderation_bot.db
```

### Step 3: Start Services

```bash
# Development environment
docker-compose -f docker-compose.dev.yml up -d

# Production environment
docker-compose -f docker-compose.prod.yml up -d
```

### Step 4: Verify Installation

```bash
# Check health status
docker-compose ps

# Or check health endpoint
curl http://localhost:8000/health
```

Expected output:
```json
{
  "status": "healthy",
  "services": {
    "web": "ok",
    "database": "ok",
    "redis": "ok"
  },
  "timestamp": "2026-01-08T10:00:00Z"
}
```

### Step 5: Access Dashboard

Open your browser:
- Application: http://localhost:8000
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

## Option 2: Local Development Setup

### Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Create .env file
cat > .env << EOF
ENVIRONMENT=development
LOG_LEVEL=debug
DEBUG=true
DATABASE_URL=sqlite:///data/moderation_bot.db
EOF
```

### Step 3: Initialize Database

```bash
# Run migrations
python -m alembic upgrade head

# Or create tables
python -c "from src.core.database import init_db; init_db()"
```

### Step 4: Start Application

```bash
# Development server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or using the CLI
python -m src.cli start --environment development
```

### Step 5: Verify Installation

```bash
# Check health endpoint
curl http://localhost:8000/health
```

## Option 3: Production Deployment

### Step 1: Configure Production Environment

```bash
# Copy production template
cp .env.template .env.production

# Edit with production values
nano .env.production
```

Required production settings:
```env
ENVIRONMENT=production
LOG_LEVEL=info
DEBUG=false
SECRET_KEY=<generate-strong-secret-key>

# Production database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Production Redis
REDIS_URL=redis://host:6379/0

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

### Step 2: Deploy

**Automated deployment** (recommended):
```bash
# Push tag
git tag v1.0.0
git push origin v1.0.0

# Trigger deployment via GitHub Actions
# Or deploy manually
./scripts/deploy.sh production
```

**Manual deployment**:
```bash
# SSH to server
ssh user@server

# Pull latest code
cd /app/moderation-bot
git pull origin main

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Verify
./scripts/health_check.py
```

## Quick Test

### Test Basic Functionality

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test API
curl http://localhost:8000/api/v1/status

# Test metrics
curl http://localhost:8000/metrics
```

### Test Platform Integration

```bash
# Test Instagram integration
curl -X POST http://localhost:8000/api/v1/instagram/test \
  -H "Content-Type: application/json" \
  -d '{"media_id": "test_media_id"}'

# Test Medium integration
curl -X POST http://localhost:8000/api/v1/medium/test \
  -H "Content-Type: application/json" \
  -d '{"article_id": "test_article_id"}'

# Test TikTok integration
curl -X POST http://localhost:8000/api/v1/tiktok/test \
  -H "Content-Type: application/json" \
  -d '{"video_id": "test_video_id"}'
```

## Next Steps

After successful installation:

1. **Configure Platform APIs** - Set up webhooks and OAuth
2. **Customize Rules** - Adjust moderation rules to your needs
3. **Set Up Monitoring** - Configure alerts for your environment
4. **Test Moderation** - Run test scenarios
5. **Deploy to Production** - Follow production deployment guide

## Common Issues

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Connection Failed

```bash
# Check database status
docker-compose ps postgres

# View database logs
docker-compose logs postgres
```

### API Keys Not Working

```bash
# Verify API keys are set
docker-compose exec web env | grep API_KEY

# Test API connectivity
python -c "
from src.platforms.instagram.client import InstagramAPIClient
client = InstagramAPIClient({'access_token': 'YOUR_TOKEN'})
print(client.get_media('test_id'))
"
```

## Getting Help

- **Documentation**: See `docs/` directory
- **Troubleshooting**: See `docs/TROUBLESHOOTING.md`
- **API Reference**: See `docs/API.md`
- **User Guide**: See `docs/USER_GUIDE.md`

## What's Next?

- Configure platform webhooks
- Set up monitoring alerts
- Customize moderation rules
- Deploy to production
- Read full user guide

---

**Quick Start Guide v1.0** - January 8, 2026
