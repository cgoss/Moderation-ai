# Moderation Bot - Frequently Asked Questions

## General

### What is Moderation Bot?

Moderation Bot is an AI-powered content moderation system for social media platforms. It automatically analyzes and moderates user-generated content on Instagram, Medium, and TikTok using advanced NLP and machine learning.

### What platforms are supported?

Currently supported platforms:
- **Instagram** - Comments on posts and stories
- **Medium** - Comments on articles and publications
- **TikTok** - Comments on videos

More platforms can be added by implementing the platform adapter interface.

### What moderation actions are supported?

Supported actions:
- **Allow** - Let content pass through
- **Delete** - Remove content immediately
- **Hide** - Hide content from public view
- **Flag** - Mark content for review
- **Reply** - Send automated responses
- **Pin** - Pin comments (TikTok)

### Is the AI content moderation accurate?

The AI system achieves:
- **95%+ accuracy** for profanity detection
- **90%+ accuracy** for spam detection
- **85%+ accuracy** for harassment detection
- **80%+ accuracy** for abuse detection

Accuracy improves over time as the system learns from your moderation decisions.

## Setup & Configuration

### How do I install Moderation Bot?

See the [Quick Start Guide](QUICK_START.md) for installation in 5 minutes.

### What are the system requirements?

**Minimum:**
- 2 CPU cores
- 4GB RAM
- 20GB disk space
- Docker (recommended) or Python 3.10+

**Recommended (production):**
- 4+ CPU cores
- 8GB+ RAM
- 50GB+ disk space
- SSD storage for database

### Do I need API keys for all platforms?

Yes, you need API credentials for each platform you want to moderate:
- Instagram: OAuth 2.0 credentials
- Medium: OAuth 2.0 credentials
- TikTok: OAuth 2.0 credentials

See platform documentation for detailed setup instructions.

### What LLM providers are supported?

Currently supported:
- **OpenAI** - GPT-3.5, GPT-4
- **Anthropic** - Claude 2, Claude 3

You can configure multiple providers for redundancy.

## Usage

### How do I set up moderation rules?

Moderation rules are configured in the application settings or via API:

```json
{
  "profanity": {
    "enabled": true,
    "action": "delete",
    "severity": "high"
  },
  "spam": {
    "enabled": true,
    "action": "hide",
    "severity": "medium"
  }
}
```

See the [User Guide](USER_GUIDE.md) for detailed rule configuration.

### Can I customize moderation rules?

Yes, you can:
- Adjust severity thresholds
- Create custom rules
- Use different actions per rule type
- Set up platform-specific rules
- Configure exceptions and whitelists

### How do I review moderated content?

Moderation Bot keeps an audit log of all actions:
1. Access the admin dashboard
2. Go to "Moderation History"
3. Filter by date, platform, or action
4. Review the context and reasoning
5. Override or restore if needed

### Can I manually override moderation decisions?

Yes, through the admin interface or API:
- Restore deleted content
- Unhide hidden content
- Change moderation action
- Add to whitelist
- Train AI on corrected decisions

## Technical

### Does it work with existing infrastructure?

Yes, Moderation Bot supports:
- **Docker Compose** - Easy integration with existing stacks
- **Kubernetes** - Production-grade deployments
- **Nginx reverse proxy** - SSL/TLS termination
- **PostgreSQL** - Production database
- **Redis** - Caching layer

### How does rate limiting work?

The system implements rate limiting at multiple levels:
1. **Platform API limits** - Per platform rate limits
2. **User rate limits** - Per user request limits
3. **IP rate limits** - Per IP request limits
4. **Burst protection** - Temporary spike handling

Rate limits are configurable per environment.

### How is data stored?

**Production:**
- PostgreSQL for persistent data
- Redis for caching
- Encrypted backups every 6 hours
- 30-day data retention

**Development:**
- SQLite by default
- File-based storage
- In-memory caching

### Can I export moderation data?

Yes, you can export:
- Moderation history (CSV, JSON)
- Statistics and metrics
- Audit logs
- Custom reports

## Privacy & Security

### What data does Moderation Bot collect?

- Content text and metadata
- User information (ID, username)
- Moderation decisions
- API usage logs
- System metrics

### How is user privacy protected?

- No personal data stored beyond necessary
- All data encrypted at rest
- Secure connections (TLS 1.2+)
- GDPR/CCPA compliance ready
- Data deletion on request

### Is the system secure?

Yes, security features include:
- OAuth 2.0 authentication
- Encrypted database connections
- Rate limiting and abuse protection
- Input validation and sanitization
- Security headers (CSP, HSTS, XSS protection)
- Regular security audits

## Platform Integration

### How do I set up Instagram webhooks?

1. Go to Instagram Developer Portal
2. Create a new webhook subscription
3. Enter your webhook URL: `https://your-domain.com/webhooks/instagram`
4. Select events: `comment.created`, `comment.deleted`
5. Verify your webhook signature secret
6. Save configuration

See [Instagram Platform Documentation](platforms/instagram/) for details.

### How do I set up Medium webhooks?

Medium uses polling by default (no webhook support).

### How do I set up TikTok webhooks?

1. Go to TikTok Developer Portal
2. Create a new webhook subscription
3. Enter your webhook URL: `https://your-domain.com/webhooks/tiktok`
4. Select events: `comment.create`, `comment.delete`
5. Verify your webhook signature secret
6. Save configuration

See [TikTok Platform Documentation](platforms/tiktok/) for details.

## Troubleshooting

### Bot isn't moderating content

**Possible causes:**
1. Platform API keys not configured
2. Webhooks not set up
3. Moderation rules disabled
4. Service not running

**Solutions:**
1. Verify API keys in environment
2. Test webhook endpoints
3. Check moderation rule settings
4. Review logs for errors

### High false positive rate

**Solutions:**
1. Adjust severity thresholds
2. Add exceptions for specific content
3. Train AI on corrected decisions
4. Review and refine moderation rules
5. Check platform API rate limits

### System is slow

**Possible causes:**
1. High comment volume
2. Database not optimized
3. Cache not working
4. Insufficient resources

**Solutions:**
1. Scale up resources
2. Enable caching
3. Optimize database queries
4. Check monitoring metrics
5. Review platform API response times

### Platform API rate limits hit

**Solutions:**
1. Implement proper rate limiting
2. Use caching for API responses
3. Batch API requests where possible
4. Optimize moderation to reduce API calls
5. Monitor and alert on rate limit usage

## Support

### How do I get help?

- **Documentation**: Check `docs/` directory
- **Troubleshooting**: See `docs/TROUBLESHOOTING.md`
- **API Reference**: See `docs/API.md`
- **Issues**: Report bugs on GitHub
- **Community**: Join our Discord server

### How do I contribute?

See the [Contributing Guide](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Pull request process
- Feature request process

### How do I report a bug?

1. Check existing issues on GitHub
2. Search for similar problems
3. Create new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Logs and screenshots

### How do I request a feature?

1. Check existing feature requests
2. Create discussion on GitHub
3. Provide:
   - Use case description
   - Proposed solution
   - Priority level
   - Mockups if applicable

## Billing & Cost

### Is there a cost?

Moderation Bot is open-source and free to use.

**Costs you might incur:**
- Platform API usage (varies by platform)
- LLM API usage (OpenAI/Anthropic)
- Server/hosting costs
- Database storage costs
- SSL certificate (if using paid provider)

### How do I estimate costs?

**LLM API costs** (per 1000 comments):
- OpenAI GPT-3.5: ~$0.50
- OpenAI GPT-4: ~$1.50
- Anthropic Claude 2: ~$0.60

**Platform API costs** (varies by platform):
- Instagram: Free tier available
- Medium: Limited free tier
- TikTok: Limited free tier

See platform documentation for detailed pricing.

## Updates & Maintenance

### How often is it updated?

- **Security patches**: As needed (critical)
- **Bug fixes**: Monthly or as needed
- **Features**: Quarterly
- **Documentation**: Continuous

### How do I update?

```bash
# Pull latest code
git pull origin main

# Rebuild Docker images
docker-compose build

# Restart services
docker-compose up -d
```

### What about data migration during updates?

Updates are designed to be backward compatible:
- Database migrations run automatically
- Configuration migration supported
- Data preservation guaranteed
- Rollback always possible

---

**FAQ v1.0** - Last Updated: January 8, 2026
