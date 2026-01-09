# Moderation Bot - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Load Balancer (NGINX)          │
├─────────────────────────────────────────────────────────────┤
│              ┌──────────────────────┐         │
│              │    Moderation Bot    │         │
│              │  (3 instances)       │         │
│              │                      │         │
│              │  ┌─────────────────┐  │         │
│              │  │   Analytics   │  │         │
│              │  └─────────────────┘  │         │
│              └──────────────────────┘         │
├─────────────────────────────────────────────────────┤
│                 ┌─────────────────────┐         │
│                 │  PostgreSQL DB    │         │
│                 └─────────────────────┘         │
├─────────────────────────────────────────────────────┤
│                 ┌─────────────────────┐         │
│                 │  Redis Cache      │         │
│                 └─────────────────────┘         │
├─────────────────────────────────────────────────────┤
│                 ┌───────────────────────┐         │
│                 │  Prometheus      │         │
│                 │  (Metrics)        │         │
│                 └───────────────────────┘         │
└─────────────────────────────────────────────────────────┘

     ┌─────────────────────────────────┐
     │  Platform APIs (External)  │
     │  ┌────────────┬─────────┐ │
     │  │ Instagram  │  Medium   │ │
     │  └────────────┴─────────┘ │
     └─────────────────────────────────┘

     ┌─────────────────────────────────┐
     │   LLM Providers (External)  │
     │  ┌────────────┬─────────┐ │
     │  │  OpenAI   │ Anthropic │ │
     │  └────────────┴─────────┘ │
     └─────────────────────────────────┘
```

## Components

### 1. API Gateway

**Technology**: NGINX Reverse Proxy
**Purpose**: 
- Load balancing across 3 application instances
- SSL/TLS termination
- Rate limiting
- Security headers
- Static file serving

**Configuration**:
- Upstream load balancing (least connections)
- Rate limiting zones (API, general, per-server)
- IP whitelisting for webhooks
- Health checks every 30s

### 2. Application Layer

**Technology**: FastAPI (Python)
**Purpose**: REST API and WebSocket server
**Features**:
- RESTful API endpoints
- WebSocket for real-time updates
- Async request processing
- Automatic request validation
- Custom middleware for auth, logging, errors

### 3. Business Logic Layer

**Components**:
- **Moderation Engine**: AI-powered content analysis
- **Platform Adapters**: Instagram, Medium, TikTok integrations
- **Rule Engine**: Configurable moderation rules
- **Action Executor**: Execute moderation decisions
- **Webhook Handler**: Process platform webhooks

### 4. Data Layer

**PostgreSQL Database**:
- **Schema**: Normalized, indexed tables
- **Connection Pool**: 20 connections, max overflow 10
- **Migrations**: Alembic for version control
- **Backup**: Every 6 hours, retention 30 days

**Redis Cache**:
- **Purpose**: Response caching, session storage
- **TTL**: 1 hour for API responses, 24 hours for sessions
- **Eviction**: LRU (Least Recently Used)
- **Memory Limit**: 512MB

### 5. Analytics Layer

**Prometheus**:
- **Metrics Collection**: Application, database, cache, platform APIs
- **Alerting**: 10 configured rules
- **Retention**: 90 days of detailed metrics

**Grafana**:
- **Dashboards**: 4 dashboards (overview, performance, security)
- **Data Sources**: Prometheus integration
- **Alerting**: Integration with Prometheus alerts

### 6. External Integrations

**Platform APIs**:
- **Instagram**: Graph API v14.0
- **Medium**: API v2.0
- **TikTok**: API v2.0

**LLM Providers**:
- **OpenAI**: GPT-3.5/4.0 models
- **Anthropic**: Claude 2/3 models
- **Fallback**: Switch between providers based on availability

## Data Flow

### Comment Moderation Flow

```
User Comment
     │
     ▼
Webhook Event
     │
     ▼
Validate Payload
     │
     ▼
Check Rate Limit
     │
     ▼
Moderation Engine
     │
     ├───▶────┐
     │        │  Sentiment
     │        │  Spam Detection
     │        │  Harassment
     │        │  Profanity
     │        │  Abuse
     │        └───────────────┘
     │
     ▼
Evaluate Rules
     │
     ▼
Action Decision
     │
     ▼
Execute Action
     │
     ├───▶────┐
     │        │  Delete
     │        │  Hide
     │        │  Flag
     │        │  Allow
     │        └───────────────┘
     │
     ▼
Log Action
     │
     ▼
Return Result
     │
     ▼
Update Analytics
```

### Platform Integration Flow

```
Post Comment
     │
     ▼
Fetch Comment
     │
     ▼
Call Platform API
     │
     ├───▶────┐
     │        │  Instagram
     │        │  Medium
     │        └───────────────┘
     │
     ▼
Process Result
     │
     ▼
Cache Result
     │
     ▼
Trigger Webhook
     │
     ▼
Update Analytics
```

### Authentication Flow

```
User
     │
     ▼
Request Authorization
     │
     ▼
Platform Redirect
     │
     ▼
User Approves
     │
     ▼
Platform Callback
     │
     ▼
Exchange Code
     │
     ▼
Issue Token
     │
     ▼
Store Token
```

## Security Architecture

### Network Security
- **Firewall**: UFW configured with strict rules
- **Rate Limiting**: Multi-level (API, user, IP, burst)
- **IP Whitelisting**: Platform webhook IPs only
- **SSL/TLS**: All connections encrypted
- **Security Headers**: CSP, HSTS, XSS protection

### Application Security
- **OAuth 2.0**: Secure authorization flow
- **Token Encryption**: Tokens encrypted at rest
- **Input Validation**: All user inputs sanitized
- **SQL Injection Protection**: Parameterized queries
- **Rate Limiting**: Protection against abuse

### Data Security
- **Encryption at Rest**: TLS 1.2 for database
- **Encryption in Transit**: TLS 1.2 for all connections
- **Token Storage**: Encrypted in database
- **Backup Encryption**: GPG encryption for backups
- **Data Retention**: 90 days, then auto-delete

## Performance Architecture

### Caching Strategy
- **Level 1 Cache (Redis)**: API responses, user sessions
- **Level 2 Cache (Database)**: Frequent access patterns
- **Cache Invalidation**: TTL-based expiration
- **Cache Warming**: Pre-populate on startup
- **Cache Hit Ratio**: Target 85%+

### Load Balancing
- **Algorithm**: Least connections
- **Health Checks**: Remove unhealthy instances
- **Session Affinity**: Minimize database connections
- **Connection Pooling**: Reuse database connections

### Monitoring Strategy
- **Metrics Collection**: Every 15 seconds
- **Alert Thresholds**: Configurable per rule
- **Retention Period**: 90 days for detailed, 1 year for aggregated
- **Dashboard Refresh**: Every 30 seconds

## Scalability

### Horizontal Scaling
- **Minimum**: 3 application instances
- **Maximum**: 10 instances (Kubernetes HPA)
- **Auto-scaling**: CPU > 70% or memory > 80%
- **Database**: Connection pooling allows more concurrent users
- **Cache**: Redis can handle high concurrency

### Vertical Scaling
- **Minimum Resources**:
  - CPU: 500m
  - Memory: 512Mi
  - Disk: 10GB

- **Recommended Resources**:
  - CPU: 2 cores
  - Memory: 2Gi
  - Disk: 50GB SSD
  - Network: 1Gbps

- **Resource Limits**:
  - CPU: 1000m
  - Memory: 4Gi
  - Disk: 100GB

## High Availability

### Application Level
- **Instances**: 3 for redundancy
- **Health Checks**: Every 30 seconds
- **Auto-Restart**: On crash
- **Zero-Downtime Deployment**: Blue-green deployments

### Database Level
- **Replication**: Optional for production
- **Backups**: Every 6 hours
- **Connection Pooling**: Prevents connection exhaustion
- **Failover**: Automatic on primary failure

### Infrastructure Level
- **Load Balancer**: NGINX with health checks
- **Monitoring**: Prometheus and Grafana
- **Alerting**: Slack integration
- **Geographic Distribution**: Optional across regions

## Deployment Architecture

### Development Environment
- **Stack**: Docker Compose
- **Services**: Web, PostgreSQL, Redis
- **Hot Reload**: Code changes auto-reload
- **Debug Mode**: Enabled with detailed logging
- **Local Database**: SQLite for simplicity

### Staging Environment
- **Stack**: Docker Compose with monitoring
- **Services**: Web, PostgreSQL, Redis, Prometheus, Grafana
- **Testing**: Comprehensive before production
- **Access**: Team-only access
- **Data**: Copy of production subset

### Production Environment
- **Stack**: Kubernetes or Docker Swarm
- **Services**: All services + NGINX + SSL/TLS
- **Monitoring**: Full observability stack
- **Access**: Restricted based on role
- **Data**: Encrypted, backups verified
- **Updates**: Zero-downtime deployments

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| API Gateway | NGINX 1.25 | Load balancing, SSL |
| Application | FastAPI 0.104+ | REST API, WebSocket |
| Database | PostgreSQL 15 | Primary data store |
| Cache | Redis 7 | Caching layer |
| Monitoring | Prometheus 2.45+ | Metrics collection |
| Visualization | Grafana 10.1+ | Dashboards |
| Containerization | Docker 24.0+ | Container management |
| Language | Python 3.10+ | Backend language |
| LLM | OpenAI API, Anthropic | AI processing |
| CI/CD | GitHub Actions | Testing, deployment |

---

**Architecture Overview v1.0** - Last Updated: January 8, 2026
