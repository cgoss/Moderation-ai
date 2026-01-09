# Moderation Bot - User Manual

Comprehensive user guide for setting up and using Moderation Bot.

## Table of Contents

- [Getting Started](#getting-started)
- [Dashboard Overview](#dashboard-overview)
- [Platform Integration](#platform-integration)
- [Configuring Rules](#configuring-rules)
- [Managing Content](#managing-content)
- [Understanding Actions](#understanding-actions)
- [Monitoring Performance](#monitoring-performance)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Getting Started

### Installation

#### Quick Installation

For fastest setup, use Docker:

```bash
# Clone repository
git clone https://github.com/your-org/moderation-bot.git
cd moderation-bot

# Configure environment
cp .env.template .env.local

# Start services
docker-compose up -d
```

See [Quick Start Guide](QUICK_START.md) for detailed installation options.

### First Steps After Installation

1. **Access the Dashboard**
   - Open http://localhost:3000 (admin/admin)
   - Change your password immediately

2. **Add Your Platform Accounts**
   - Go to Settings → Platform Accounts
   - Click "Add Account" for each platform
   - Follow OAuth authorization flow

3. **Configure Webhooks**
   - Copy webhook URLs from Settings → Platform Accounts
   - Add them to your platform developer portal

4. **Review Default Rules**
   - Go to Moderation → Rules
   - Adjust severity thresholds
   - Enable/disable categories as needed

5. **Start Tracking**
   - Add your posts/articles/videos
   - Enable automatic tracking
   - Set tracking frequency

### Platform-Specific Setup

#### Instagram Setup

1. **Connect Account**
   - Go to Settings → Platform Accounts → Instagram
   - Click "Connect Account"
   - Authorize with Instagram

2. **Configure Webhooks**
   - Get webhook URL: `https://your-domain.com/webhooks/instagram`
   - Add to Instagram Developer Portal:
     - Go to [Meta for Developers](https://developers.facebook.com/)
     - Navigate to Apps → Your Apps → Create App
     - Set Webhook URL to your endpoint
     - Verify with webhook tester

3. **Start Tracking**
   - Add Instagram posts to track
   - Enable comment tracking
   - Set up post monitoring

#### Medium Setup

1. **Connect Account**
   - Go to Settings → Platform Accounts → Medium
   - Click "Connect Account"
   - Authorize with Medium

2. **Configure Tracking**
   - Add Medium publications to track
   - Enable comment tracking
   - Set tracking frequency (every 1 hour)

3. **Note**: Medium uses polling (no webhooks)

#### TikTok Setup

1. **Connect Account**
   - Go to Settings → Platform Accounts → TikTok
   - Click "Connect Account"
   - Authorize with TikTok

2. **Configure Webhooks**
   - Get webhook URL: `https://your-domain.com/webhooks/tiktok`
   - Add to TikTok Developer Portal:
     - Go to [TikTok for Developers](https://developers.tiktok.com/)
     - Navigate to Apps → Create App
     - Set Webhook URL to your endpoint
     - Select events: `comment.create`, `comment.delete`

3. **Start Tracking**
   - Add TikTok videos to track
   - Enable comment tracking
   - Monitor comment volume

---

## Dashboard Overview

### Main Navigation

Dashboard is organized into:

- **Dashboard**: System overview and alerts
- **Platforms**: Manage platform connections
- **Moderation**: Configure rules and review content
- **Analytics**: View performance metrics and statistics
- **Settings**: Configure bot behavior and notifications
- **History**: Review moderation actions and decisions

### Dashboard Widgets

**Overview Panel:**
- Comments moderated (last 24 hours)
- Actions taken (by type)
- Platform health status
- System performance metrics
- Active alerts

**Performance Panel:**
- Request rate (requests/second)
- Response time (P50, P95, P99)
- Error rate (percentage)
- API success rate (by platform)
- Cache hit rate

**Moderation Panel:**
- Rules configured (count)
- Rules triggered (last 24 hours)
- False positive rate (percentage)
- False negative rate (percentage)

### Accessing the Dashboard

```
URL: http://localhost:3000 (production)
URL: http://staging.your-domain.com (staging)
Credentials: admin/admin (change on first login)
```

---

## Platform Integration

### Connecting Instagram

**Step-by-step:**

1. **Navigate to Settings**
   - Click on "Settings" in left sidebar
   - Select "Platform Accounts"

2. **Add Instagram Account**
   - Click "Add Account" button
   - Click "Connect with Instagram"
   - Log in to Instagram (if not already)
   - Authorize the app

3. **Configure What to Track**
   - Choose from:
     - "All posts" - Track all your posts
     - "Specific posts" - Track selected posts
     - "Hashtag monitoring" - Track specific hashtags

4. **Set Tracking Frequency**
   - Select frequency: Real-time, Every 5 min, Every 15 min, Every 30 min

**Instagram Webhook Setup:**

1. Copy webhook URL from Settings → Instagram
2. Go to Instagram Developer Portal
3. Create app or select existing app
4. Add webhook URL: `https://your-domain.com/webhooks/instagram`
5. Subscribe to events: `comment.created`, `comment.deleted`
6. Verify webhook delivery (click "Test" button)

### Connecting Medium

**Step-by-step:**

1. **Navigate to Settings**
   - Click on "Settings" in left sidebar
   - Select "Platform Accounts"

2. **Add Medium Account**
   - Click "Add Account" button
   - Click "Connect with Medium"
   - Authorize the app

3. **Configure What to Track**
   - Choose from:
     - "All publications" - Track all your articles
     - "Specific publications" - Track selected articles
     - "Topic monitoring" - Track specific topics

4. **Set Tracking Frequency**
   - Select frequency: Every 1 hour, Every 6 hours, Every 24 hours

**Note**: Medium uses polling, not webhooks. Bot checks for new comments periodically.

### Connecting TikTok

**Step-by-step:**

1. **Navigate to Settings**
   - Click on "Settings" in left sidebar
   - Select "Platform Accounts"

2. **Add TikTok Account**
   - Click "Add Account" button
   - Click "Connect with TikTok"
   - Authorize the app

3. **Configure What to Track**
   - Choose from:
     - "All videos" - Track all your videos
     - "Specific videos" - Track selected videos
     - "Hashtag monitoring" - Track specific hashtags

4. **Set Tracking Frequency**
   - Select frequency: Real-time, Every 5 min, Every 15 min, Every 30 min

**TikTok Webhook Setup:**

1. Copy webhook URL from Settings → TikTok
2. Go to TikTok Developer Portal
3. Create app or select existing app
4. Add webhook URL: `https://your-domain.com/webhooks/tiktok`
5. Subscribe to events: `comment.create`, `comment.delete`
6. Verify webhook delivery (click "Test" button)

---

## Configuring Rules

### Default Rules

**Profanity Rule** (Severity: High)
- Detects: F-word and similar words
- Action: Delete comment
- Categories: English profanity, offensive language

**Spam Rule** (Severity: Medium)
- Detects: Repetitive content, suspicious links
- Action: Hide comment
- Categories: Marketing spam, excessive self-promotion, link spam

**Harassment Rule** (Severity: High)
- Detects: Personal attacks, threats, hate speech
- Action: Delete comment
- Categories: Personal insults, threats, hate speech, discrimination

**Abuse Rule** (Severity: High)
- Detects: Threats, self-harm, illegal activities
- Action: Delete comment, flag user
- Categories: Self-harm encouragement, threats

### Creating Custom Rules

1. **Navigate to Moderation → Rules**
2. Click "Create Rule" button
3. Fill in rule details:
   - Name: e.g., "No Spam Links"
   - Severity: Select from Low, Medium, High, Critical
   - Categories: Select from Spam, Profanity, Harassment, etc.
   - Action: Choose from Delete, Hide, Flag, Allow
   - Keywords: Add keywords or regex patterns
   - Platform: Apply to All, or specific platforms
4. Click "Save Rule"

### Rule Examples

**Example 1: No Personal Information**
```
Name: No Personal Information
Severity: Medium
Categories: Privacy
Action: Hide
Keywords: phone, email, address, social security number, ssn, credit card
```

**Example 2: Marketing Content**
```
Name: No Marketing
Severity: Low
Categories: Spam
Action: Allow (with warning)
Keywords: buy, discount, sale, coupon, offer, shop, store
```

**Example 3: Link Monitoring**
```
Name: No External Links
Severity: Medium
Categories: Spam
Action: Delete
Keywords: http, https, .com, .net, .org, link
Regex: (http|https)://\S+[^/]+
```

### Rule Hierarchy

Rules are evaluated in order:
1. Platform-specific rules (if configured)
2. Account-specific whitelist rules
3. Global rules (apply to all)
4. System-critical rules (cannot be overridden)

---

## Managing Content

### Viewing Moderation History

1. **Navigate to Moderation → History**
2. Filter by:
   - Platform (Instagram, Medium, TikTok)
   - Date range
   - Action type (Delete, Hide, Flag, Allow)
   - Rule triggered
   - User who performed action
3. Click on any action to view details
4. View context (surrounding comments)

### Reviewing Content

1. **Navigate to Moderation → Pending Review**
2. Select items from the queue
3. View analysis results
4. Choose action:
   - Approve: Let comment pass through
   - Delete: Remove comment
   - Hide: Hide from public view
   - Flag: Mark for manual review

### Overriding Moderation Decisions

**To Override a Decision:**

1. Find the content in History
2. Click "Override" button
3. Select new action
4. Add note explaining why
5. Confirm the change

**To Train the AI:**

1. Find false positive or false negative decisions in History
2. Mark them as "Incorrect Decision"
3. The system will learn from this
4. Improves accuracy over time

---

## Understanding Actions

### Delete Action

- **What it does**: Permanently removes content from platform
- **User visibility**: Gone (except if restored)
- **Platform API**: Calls delete endpoint
- **Reversible**: Only within platform's time limit
- **AI Learning**: Future comments from this user will be handled more strictly

### Hide Action

- **What it does**: Hides content from public view
- **User visibility**: Hidden from public (still visible to admins)
- **Platform support**: Available on Instagram only
- **Reversible**: Can unhide anytime
- **AI Learning**: Teaches that this content type should be hidden

### Flag Action

- **What it does**: Marks content for manual review
- **User visibility**: Still visible but flagged
- **Notification**: You receive alert
- **Review queue**: Appears in Pending Review
- **Action required**: You must decide within 48 hours
- **AI Learning**: Your decision becomes part of training data

### Allow Action

- **What it does**: Lets content pass through all rules
- **Default action**: Content is allowed unless it hits a critical rule
- **Final decision**: Based on most critical rule triggered

### Reply Action

- **What it does**: Sends automated response
- **Templates**: Pre-configured responses
- **Personalization**: Customize with user name
- **Platform support**: Available on all platforms
- **Usage**: Use for common questions, thank users

### Pin Action

- **What it does**: Highlights comment at top
- **Platform support**: TikTok only
- **Visibility**: Appears first in comments
- **Limit**: One pinned comment per post
- **Best practice**: Pin positive responses or helpful Q&A

---

## Monitoring Performance

### Key Metrics Dashboard

**Overview Panel Shows:**
- Comments moderated (last 24 hours)
- Actions by type (pie chart)
- False positive rate (goal: <2%)
- Accuracy by category (bar chart)
- Platform API health (status indicators)
- Response times (line graph)

### Understanding Metrics

**Request Rate**: Requests processed per second
- Higher is better (target: 100-200 req/s)
- Lower may indicate slowness

**Response Time**: Time to moderate a comment
- P50: Median response time (target: <500ms)
- P95: 95th percentile (target: <1s)
- P99: 99th percentile (target: <2s)

**Error Rate**: Percentage of failed API calls
- Target: <1%
- Higher may indicate platform issues

**API Success Rate**: Successful API calls / total API calls
- Target: >99%
- Higher is better

### Performance Optimization

To improve performance:
1. Enable caching (Settings → General)
2. Reduce tracking frequency for low-volume content
3. Adjust rule severity thresholds
4. Review platform API rate limits
5. Use batch operations where possible

---

## Troubleshooting

### Common Issues

**Issue: Bot isn't moderating content**

**Solutions:**
1. Check platform connections in Settings → Platform Accounts
2. Verify webhooks are active in platform developer portal
3. Check system status in Dashboard → System Health
4. Review error logs in Dashboard → Logs

**Issue: High false positive rate**

**Solutions:**
1. Adjust severity thresholds in Rules
2. Review flagged comments and override decisions
3. Add keywords for common false positives to whitelist
4. Train AI on incorrect decisions (mark as incorrect in History)

**Issue: High response time**

**Solutions:**
1. Check LLM provider status (Dashboard → System Health)
2. Review platform API response times in Analytics
3. Enable caching if disabled
4. Contact support if issue persists

**Issue: Missing moderation actions**

**Solutions:**
1. Check if rules are enabled in Rules
2. Verify category is not disabled
3. Check action type is supported for platform
4. Review platform permissions for actions

### Getting Help

**Documentation:**
- [Quick Start Guide](QUICK_START.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [API Documentation](API.md)
- [FAQ](FAQ.md)

**Support Channels:**
- GitHub Issues: Report bugs
- GitHub Discussions: Ask questions
- Email: support@example.com (security issues only)
- Community Discord: Join for community support

---

## Best Practices

### For Content Creators

**1. Know Your Rules**
- Review the rules configured for your account
- Understand what triggers moderation
- Adjust rules to match your content style
- Test rules with sample content before publishing

**2. Set Up Tracking**
- Add all your posts/videos before publishing
- Enable tracking at appropriate frequency
- Monitor moderation actions in real-time
- Adjust rules based on what gets flagged

**3. Use the Review Queue**
- Periodically check Pending Review
- Review AI decisions
- Override when needed
- Use correct decisions to train the AI

**4. Monitor Performance**
- Check metrics dashboard regularly
- Watch for high false positive rates
- Review response times
- Adjust caching and tracking settings

### For Moderators

**1. Batch Review**
- Process multiple items at once
- Use filters to prioritize
- Review flagged items first
- Use batch actions where available

**2. Consistent Enforcement**
- Apply rules consistently across all platforms
- Document any exceptions
- Communicate rule changes to team

**3. Continuous Improvement**
- Regularly review false positives
- Add to whitelist
- Adjust severity thresholds
- Train AI on decisions

**4. Monitor and Respond**
- Stay on top of urgent items in review queue
- Respond to user appeals quickly
- Document decisions for transparency

### Security Best Practices

**1. Account Security**
- Use strong, unique passwords
- Enable two-factor authentication
- Review access logs regularly
- Revoke access for former moderators

**2. Platform Security**
- Never share API keys
- Rotate access tokens regularly
- Use webhook secrets securely
- Keep platform developer portal secure

**3. Data Privacy**
- Never share user personal information
- Anonymize sensitive data before analysis
- Follow platform data retention policies

---

## Advanced Features

### Whitelisting

**Add Users to Whitelist:**

1. Navigate to Settings → Whitelist
2. Click "Add User" button
3. Enter username or user ID
4. Select platforms or "All"
5. Click "Add to Whitelist"

**Whitelist Effects:**
- Comments from whitelisted users skip spam detection
- Lower false positive rate
- Trusted users get more leeway
- Helps identify genuine engagement

### Bulk Operations

**Bulk Review:**
- Select multiple items
- Apply same action to all
- Useful for cleaning up spam attacks

**Bulk Tracking:**
- Add multiple posts/videos at once
- Apply same tracking settings
- Saves time on setup

**Bulk Import:**
- Import user whitelist
- Import moderation rules
- Import rule templates

### Analytics Exports

**Export Options:**
- CSV format for spreadsheet analysis
- JSON format for data processing
- PDF format for reports

**Available Reports:**
- Daily activity summary
- Weekly performance metrics
- Monthly compliance report
- Custom date range reports

---

**User Manual v1.0** - Last Updated: January 8, 2026
