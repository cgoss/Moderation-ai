# Security Hardening Guide

## Overview

This guide provides security best practices for deploying Moderation Bot in production.

## Environment Security

### 1. Secrets Management

**Never commit secrets to repository:**
```bash
# Add to .gitignore
.env.*
secrets/
*.pem
*.key
*.crt
```

**Use environment variables:**
```bash
# Set secrets at runtime
export INSTAGRAM_ACCESS_TOKEN="your-token"
export SECRET_KEY=$(openssl rand -hex 32)
```

**Rotate secrets regularly:**
- API keys: Every 90 days
- Database passwords: Every 180 days
- Secret keys: Every 30 days
- SSL certificates: Before expiration

### 2. Network Security

**Firewall Configuration:**
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny all
sudo ufw enable
```

**IP Whitelisting:**
- Allow only platform webhook IPs
- Restrict metrics endpoint to internal networks
- Block known malicious IPs

## Application Security

### 1. Input Validation

**Validate all user inputs:**
```python
def sanitize_input(user_input: str) -> str:
    # Remove dangerous characters
    user_input = re.sub(r'[;<>&|]', '', user_input)
    # Limit length
    user_input = user_input[:1000]
    return user_input
```

**Prevent SQL Injection:**
- Use parameterized queries
- Never concatenate strings for SQL
- Use ORM (SQLAlchemy)

**Prevent XSS:**
- Escape HTML output
- Use Content-Security-Policy headers
- Validate and sanitize user content

### 2. Authentication

**Multi-factor authentication:**
- Enable for admin accounts
- Require for sensitive operations

**Session management:**
- Use secure, HTTP-only cookies
- Implement session timeout (15 minutes)
- Invalidate on logout

**Password policies:**
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- No common passwords
- Rotate every 90 days

### 3. Authorization

**Role-based access control (RBAC):**
- Admin: Full access
- Moderator: Moderate content only
- Viewer: Read-only access
- API: Limited to specific endpoints

**API key management:**
- Generate unique keys per user
- Set expiration dates
- Revoke when not needed
- Log all API key usage

## Platform API Security

### 1. API Key Storage

**Store securely:**
- Use AWS Secrets Manager / HashiCorp Vault
- Encrypt at rest
- Rotate automatically

**Never expose in:**
- Frontend code
- Logs
- Error messages
- API responses

### 2. Webhook Security

**Verify signatures:**
```python
def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)
```

**Rate limit webhook endpoints:**
- 10 requests per second
- Per platform IP range
- Burst limit of 20

### 3. Platform-Specific Security

**Instagram:**
- Use official Graph API
- Never store passwords
- Implement OAuth 2.0 flow

**Medium:**
- Use official API
- Validate all user content
- Respect rate limits

**TikTok:**
- Use official API
- Verify video ownership
- Implement strict content policies

## Data Security

### 1. Encryption

**At rest:**
- Database encryption: AES-256
- File storage: Encrypted volumes
- Backup encryption: GPG/AES

**In transit:**
- TLS 1.2+ for all connections
- HTTPS only
- Certificate pinning

### 2. Data Retention

**Define retention policies:**
- User data: 90 days after deletion
- Logs: 30 days
- Audit logs: 1 year
- Backups: 30 days

**Automated deletion:**
```python
# Delete old data
def delete_old_data():
    cutoff_date = datetime.now() - timedelta(days=90)
    db.query(Comment).filter(
        Comment.deleted_at < cutoff_date
    ).delete()
```

### 3. Anonymization

**Remove personal data:**
```python
def anonymize_comment(comment: Comment):
    comment.username = f"user_{hash(comment.username)}"
    comment.user_id = None
    comment.ip_address = None
    return comment
```

## Infrastructure Security

### 1. Docker Security

**Run as non-root:**
```dockerfile
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser
```

**Minimize attack surface:**
```dockerfile
# Use minimal base image
FROM python:3.10-slim

# Install only required packages
RUN pip install --no-cache-dir ...

# Remove unnecessary files
RUN rm -rf /var/lib/apt/lists/*
```

**Scan images:**
```bash
# Use Trivy
trivy image moderation-bot:latest

# Use Docker Scout
docker scout cves moderation-bot:latest
```

### 2. Kubernetes Security

**Use NetworkPolicies:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

**Limit privileges:**
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 2000
  capabilities:
    drop:
    - ALL
```

**Resource limits:**
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

### 3. Monitoring Security

**Security monitoring:**
```yaml
# Alert on failed auth
- alert: FailedAuthentication
  expr: rate(auth_failures_total[5m]) > 10
  for: 2m
```

**Audit logging:**
- Log all admin actions
- Log all moderation actions
- Log all failed authentications
- Keep audit logs for 1 year

## Incident Response

### 1. Security Incident Procedure

**Immediate actions (P1):**
1. Isolate affected systems
2. Preserve evidence (logs, data, memory dumps)
3. Notify security team
4. Block malicious IPs
5. Rotate compromised credentials

**Investigation:**
1. Determine root cause
2. Assess impact and scope
3. Identify affected users
4. Document timeline

**Recovery:**
1. Patch vulnerabilities
2. Restore from clean backup
3. Verify no backdoors
4. Monitor for recurrence

### 2. Post-Incident

**Review:**
1. What went wrong?
2. How was it detected?
3. How long to respond?
4. What to improve?

**Update:**
1. Update incident response plan
2. Update security policies
3. Train team on lessons learned
4. Communicate with stakeholders

## Compliance

### 1. Data Protection (GDPR, CCPA)

**User rights:**
- Right to access
- Right to deletion
- Right to portability
- Right to opt-out

**Implementation:**
```python
def handle_deletion_request(user_id: str):
    # Delete user data
    delete_user_data(user_id)
    # Confirm deletion
    send_deletion_confirmation(user_id)
    # Log action
    log_deletion(user_id)
```

### 2. Auditing

**Regular audits:**
- Quarterly security audit
- Annual penetration test
- Monthly compliance review
- Continuous monitoring

**Audit checklist:**
- [ ] Secrets management
- [ ] Access controls
- [ ] Network security
- [ ] Application security
- [ ] Data encryption
- [ ] Logging and monitoring
- [ ] Incident response
- [ ] Compliance documentation

## Best Practices

### 1. Development

**Secure coding:**
- Never trust user input
- Use prepared statements
- Validate all inputs
- Implement rate limiting
- Use security headers

**Code review:**
- Security-focused code reviews
- Automated security scanning
- Dependency vulnerability checks
- OWASP Top 10 compliance

### 2. Deployment

**Secure deployment:**
- Use CI/CD with security gates
- Deploy to staging first
- Run security tests
- Monitor for issues

**Rollback plan:**
- Have rollback procedure ready
- Test rollback regularly
- Document rollback steps
- Set up monitoring alerts

### 3. Operations

**Secure operations:**
- Principle of least privilege
- Regular patch updates
- Security training
- Incident response drills

**Monitoring:**
- Security dashboards
- Alert on anomalies
- Log analysis
- Threat intelligence

## Resources

### Tools

**Security scanning:**
- OWASP ZAP: https://www.zaproxy.org/
- Nessus: https://www.tenable.com/products/nessus
- Trivy: https://github.com/aquasecurity/trivy
- Docker Scout: https://scout.docker.com/

**Penetration testing:**
- Burp Suite: https://portswigger.net/burp
- Metasploit: https://www.metasploit.com/
- Nmap: https://nmap.org/

**Compliance frameworks:**
- OWASP Top 10: https://owasp.org/www-project-top-ten
- CIS Benchmarks: https://www.cisecurity.org/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework

### Learning

**Training:**
- OWASP Security Knowledge: https://owasp.org/www-community-education
- SANS Institute: https://www.sans.org/
- Coursera Cybersecurity: https://www.coursera.org/browse/cybersecurity

**Certifications:**
- CompTIA Security+
- CEH (Certified Ethical Hacker)
- CISSP (Certified Information Systems Security Professional)

---

**Last Updated**: January 8, 2026
**Version**: 1.0
