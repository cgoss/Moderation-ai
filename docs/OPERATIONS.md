# Operations Guide

## Overview

This guide provides operational procedures for running and maintaining Moderation Bot in production.

## Monitoring

### Key Metrics

Monitor these metrics regularly:

1. **Application Metrics**
   - Request rate: `rate(http_requests_total[5m])`
   - Response time: `histogram_quantile(0.95, http_request_duration_seconds)`
   - Error rate: `rate(http_requests_total{status=~"5.."}[5m])`

2. **Database Metrics**
   - Connection count: `pg_stat_activity_count`
   - Query time: `pg_stat_statements_mean_time`
   - Cache hit ratio: `pg_stat_database_blks_hit / pg_stat_database_blks_read`

3. **Cache Metrics**
   - Memory usage: `redis_memory_used_bytes`
   - Hit ratio: `redis_keyspace_hits / (redis_keyspace_hits + redis_keyspace_misses)`
   - Connections: `redis_connected_clients`

4. **Queue Metrics**
   - Queue length: `redis_queue_length`
   - Processing rate: `rate(queue_processed_total[5m])`

### Dashboards

Access monitoring dashboards:
- **Grafana**: http://your-server:3000 (admin/admin)
- **Prometheus**: http://your-server:9090

Key dashboards:
- Overview - High-level system metrics
- Performance - Response times and throughput
- Errors - Error rates and types
- Platform Integration - API call success rates
- Moderation - Actions taken by bot

## Alerting

### Alert Levels

- **Critical**: Immediate action required (service down, database failure)
- **Warning**: Monitor closely, plan action (high resource usage)
- **Info**: For awareness only

### Alert Channels

Alerts are sent to:
1. Slack (#ops-alerts)
2. Email (ops-team@example.com)
3. PagerDuty (for critical alerts only)

### Common Alerts

**High Error Rate**
- Impact: Users experiencing errors
- Action: Check logs, identify root cause, fix or rollback

**High Response Time**
- Impact: Slow moderation, poor UX
- Action: Check resource usage, scale up if needed

**Database Connection Failed**
- Impact: Application downtime
- Action: Check database status, restart if needed, check network

**Redis Connection Failed**
- Impact: Caching not working, possible slowdown
- Action: Check Redis status, restart if needed, clear cache

**Service Down**
- Impact: Full outage
- Action: Immediate rollback or restart

## Incident Response

### Incident Severity Levels

**P1 - Critical**
- Service completely down
- Data loss
- Security breach
- Response time: < 15 minutes

**P2 - High**
- Degraded performance
- Platform API failures
- Moderation not working
- Response time: < 1 hour

**P3 - Medium**
- Slow response times
- Occasional errors
- Feature not working
- Response time: < 4 hours

**P4 - Low**
- Minor issues
- Documentation errors
- Cosmetic issues
- Response time: < 1 business day

### Incident Procedure

1. **Detect** - Alert fires or user reports issue
2. **Assess** - Determine severity and impact
3. **Respond** - Implement workaround or fix
4. **Resolve** - Fix root cause
5. **Recover** - Restore service to normal
6. **Review** - Post-incident analysis

### Escalation

If not resolved within SLA:
- P1: Escalate to CTO after 10 minutes
- P2: Escalate to Tech Lead after 30 minutes
- P3: Escalate to Engineering Manager after 2 hours

## Maintenance

### Daily Tasks

- Review error logs for anomalies
- Check key metrics are within normal ranges
- Verify backup jobs completed
- Review recent alerts

### Weekly Tasks

- Review performance trends
- Check disk space and cleanup if needed
- Review and update moderation rules
- Test disaster recovery procedures
- Review security patches and updates

### Monthly Tasks

- Full system audit
- Review and update documentation
- Capacity planning and scaling review
- Security audit
- Backup restoration test
- Cost analysis and optimization

### Quarterly Tasks

- Architecture review
- Technology stack evaluation
- Disaster recovery drill
- Training and knowledge sharing

## Backups

### Backup Schedule

- **Database**: Every 6 hours (4 backups per day)
- **Data**: Every 24 hours (1 backup per day)
- **Configuration**: On every deployment

### Backup Retention

- Database: Keep 30 days (120 backups)
- Data: Keep 7 days (7 backups)
- Configuration: Keep all deployments

### Backup Verification

Test restoration quarterly:
1. Create test environment
2. Restore latest backup
3. Run health checks
4. Verify data integrity

## Scaling

### When to Scale Up

- CPU usage > 80% for 10+ minutes
- Memory usage > 90% for 10+ minutes
- Queue length > 1000 items for 5+ minutes
- Response time > 2 seconds for 95th percentile

### How to Scale Up

**Horizontal** (Add more instances):
```bash
# Edit docker-compose.yml
# Increase replicas
docker-compose up -d --scale web=4
```

**Vertical** (Increase resources):
```bash
# Edit docker-compose.yml
# Increase CPU/memory limits
docker-compose up -d --force-recreate
```

### When to Scale Down

- CPU usage < 20% for sustained period
- Memory usage < 30% for sustained period
- Queue length < 100 items consistently
- Cost optimization needed

## Security

### Daily Security Checks

- Review error logs for attack patterns
- Check authentication logs
- Verify rate limiting is working
- Review new user registrations

### Weekly Security Tasks

- Update dependencies: `pip install -U -r requirements.txt`
- Review and rotate API keys
- Check for security advisories
- Review access logs

### Monthly Security Tasks

- Security audit
- Penetration testing
- Review access controls
- Update SSL certificates
- Review moderation rules for bias

### Incident Response

**Security Incident Procedure**:
1. Immediately isolate affected systems
2. Preserve evidence (logs, data)
3. Notify security team
4. Investigate root cause
5. Patch vulnerabilities
6. Document lessons learned
7. Communicate with stakeholders

## Performance Optimization

### Caching Strategy

- Cache API responses for 5 minutes
- Cache moderation results for 1 hour
- Cache user sessions for 24 hours
- Use Redis for hot data, PostgreSQL for cold data

### Database Optimization

- Index frequently queried columns
- Partition large tables by date
- Archive old data (keep 90 days active)
- Use connection pooling (max 20 connections)

### Rate Limiting

- Per user: 100 requests/minute
- Per IP: 500 requests/minute
- Burst: 10 requests per second
- Back off on repeated violations

## Troubleshooting Guide

### Slow Performance

1. Check metrics: Is CPU/memory high?
2. Check database: Is query time high?
3. Check cache: Is hit ratio low?
4. Check queue: Is it backed up?
5. Check network: Is latency high?

### High Error Rate

1. Check logs: What error type?
2. Check database: Is it healthy?
3. Check APIs: Are they responding?
4. Check rate limits: Are they hitting limits?
5. Check config: Are environment variables correct?

### Service Won't Start

1. Check logs: What's the error?
2. Check ports: Is something using port 8000?
3. Check Docker: Is image built correctly?
4. Check config: Are all env vars set?
5. Check dependencies: Are DB and Redis running?

## Documentation

### Keep Updated

- Architecture diagrams
- API documentation
- Operational procedures
- Incident runbooks
- Configuration reference

### Knowledge Base

Document:
- Common issues and resolutions
- Platform API quirks
- Performance baselines
- Security incident responses

## Support

### Escalation Contacts

- **On-call Engineer**: +1-XXX-XXX-XXXXX
- **Tech Lead**: +1-XXX-XXX-XXXXX
- **CTO**: +1-XXX-XXX-XXXXX (P1 only)

### External Resources

- **Platform Support**: See docs/platforms/
- **LLM Support**: OpenAI/Anthropic documentation
- **Infrastructure Support**: AWS/GCP/Azure support

---

**Last Updated**: January 8, 2026
**Version**: 1.0
