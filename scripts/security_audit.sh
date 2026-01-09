#!/bin/bash

# Security Audit Script

set -e

echo "=================================="
echo "Security Audit for Moderation Bot"
echo "=================================="
echo ""

# Check 1: Verify SSL/TLS certificates
echo "1. SSL/TLS Certificate Check"
echo "--------------------------------"
if curl -sSI https://localhost 2>&1 | grep -q "SSL"; then
    echo "✓ SSL is configured"
    
    # Check certificate expiration
    EXPIRY_DATE=$(echo | openssl s_client -connect localhost:443 -servername localhost 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep notAfter | cut -d= -f2)
    EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
    CURRENT_EPOCH=$(date +%s)
    DAYS_LEFT=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400 ))
    
    if [ $DAYS_LEFT -lt 30 ]; then
        echo "✗ WARNING: SSL certificate expires in $DAYS_LEFT days"
    else
        echo "✓ SSL certificate valid for $DAYS_LEFT days"
    fi
else
    echo "✗ SSL not configured"
fi
echo ""

# Check 2: Verify security headers
echo "2. Security Headers Check"
echo "--------------------------------"
HEADERS=$(curl -sI https://localhost 2>&1)

if echo "$HEADERS" | grep -q "X-Frame-Options"; then
    echo "✓ X-Frame-Options header present"
else
    echo "✗ X-Frame-Options header missing"
fi

if echo "$HEADERS" | grep -q "X-Content-Type-Options"; then
    echo "✓ X-Content-Type-Options header present"
else
    echo "✗ X-Content-Type-Options header missing"
fi

if echo "$HEADERS" | grep -q "Strict-Transport-Security"; then
    echo "✓ Strict-Transport-Security header present"
else
    echo "✗ Strict-Transport-Security header missing"
fi

if echo "$HEADERS" | grep -q "X-XSS-Protection"; then
    echo "✓ X-XSS-Protection header present"
else
    echo "✗ X-XSS-Protection header missing"
fi
echo ""

# Check 3: Verify rate limiting
echo "3. Rate Limiting Check"
echo "--------------------------------"
for i in {1..100}; do
    curl -s https://localhost/api/test > /dev/null &
done
wait

# Check if we're being rate limited
HTTP_429=$(curl -s -o /dev/null -w "%{http_code}" https://localhost/api/test)
if [ "$HTTP_429" = "429" ]; then
    echo "✓ Rate limiting is working"
else
    echo "✗ Rate limiting may not be working (HTTP $HTTP_429)"
fi
echo ""

# Check 4: Verify firewall rules
echo "4. Firewall Configuration Check"
echo "--------------------------------"
if command -v ufw &> /dev/null; then
    echo "✓ UFW firewall is installed"
    
    if ufw status | grep -q "Status: active"; then
        echo "✓ Firewall is active"
        ufw status | head -n 20
    else
        echo "✗ Firewall is not active"
    fi
elif command -v iptables &> /dev/null; then
    echo "✓ iptables is available"
    iptables -L -n | head -n 10
else
    echo "⚠ No firewall detected"
fi
echo ""

# Check 5: Verify API key security
echo "5. API Key Security Check"
echo "--------------------------------"
if [ -f ".env.production" ]; then
    if grep -q "API_KEY" .env.production; then
        if grep "API_KEY=" .env.production | grep -v "API_KEY=$" | grep -q "."; then
            echo "✗ WARNING: Hardcoded API keys found in .env.production"
        else
            echo "✓ No hardcoded API keys detected"
        fi
    fi
    
    if grep -q "SECRET_KEY" .env.production; then
        SECRET_LENGTH=$(grep "SECRET_KEY=" .env.production | cut -d= -f2 | wc -c)
        if [ $SECRET_LENGTH -lt 32 ]; then
            echo "✗ WARNING: SECRET_KEY is too short ($SECRET_LENGTH characters, minimum 32)"
        else
            echo "✓ SECRET_KEY length is adequate ($SECRET_LENGTH characters)"
        fi
    fi
else
    echo "⚠ .env.production file not found"
fi
echo ""

# Check 6: Verify dependencies
echo "6. Dependency Security Check"
echo "--------------------------------"
if command -v pip-audit &> /dev/null; then
    pip-audit | head -n 20
else
    echo "⚠ pip-audit not installed. Install with: pip install pip-audit"
    echo "   Run manually: pip-audit"
fi
echo ""

# Check 7: Verify file permissions
echo "7. File Permissions Check"
echo "--------------------------------"
if [ -d "./data" ]; then
    PERMS=$(stat -c %a ./data | cut -c 4-6)
    if [ "$PERMS" = "750" ]; then
        echo "✓ Data directory has correct permissions (750)"
    else
        echo "⚠ Data directory has permissions: $PERMS (recommended: 750)"
    fi
fi

if [ -f ".env.production" ]; then
    PERMS=$(stat -c %a .env.production | cut -c 4-6)
    if [ "$PERMS" = "600" ]; then
        echo "✓ .env.production has correct permissions (600)"
    else
        echo "⚠ .env.production has permissions: $PERMS (recommended: 600)"
    fi
fi
echo ""

# Check 8: Verify log security
echo "8. Log Security Check"
echo "--------------------------------"
if [ -d "./logs" ]; then
    LOG_PERMS=$(stat -c %a ./logs | cut -c 4-6)
    if [ "$LOG_PERMS" = "750" ]; then
        echo "✓ Logs directory has correct permissions (750)"
    else
        echo "⚠ Logs directory has permissions: $LOG_PERMS (recommended: 750)"
    fi
    
    # Check for sensitive data in logs
    if grep -r "password\|secret\|token" ./logs/ 2>/dev/null | head -n 5; then
        echo "✗ WARNING: Sensitive data may be logged"
    else
        echo "✓ No obvious sensitive data in logs"
    fi
fi
echo ""

# Check 9: Verify Docker security
echo "9. Docker Security Check"
echo "--------------------------------"
if command -v docker &> /dev/null; then
    # Check if running as root
    if docker ps --format "{{.User}}" | grep -q "root"; then
        echo "✗ WARNING: Some containers running as root"
    else
        echo "✓ No containers running as root"
    fi
    
    # Check for exposed ports
    EXPOSED_PORTS=$(docker ps --format "{{.Ports}}" | tr ',' '\n' | grep -o '0.0.0.0:[0-9]*' | wc -l)
    if [ $EXPOSED_PORTS -le 3 ]; then
        echo "✓ Minimal exposed ports ($EXPOSED_PORTS)"
    else
        echo "⚠ Many exposed ports ($EXPOSED_PORTS)"
    fi
    
    # Check for latest images
    OUTDATED=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep -v "<none>" | wc -l)
    echo "✓ Total Docker images: $OUTDATED"
fi
echo ""

echo "=================================="
echo "Security Audit Complete"
echo "=================================="
echo ""
echo "Review any warnings above and address security issues immediately."
echo "For detailed security analysis, consider using:"
echo "  - OWASP ZAP"
echo "  - Nessus"
echo "  - Burp Suite"
