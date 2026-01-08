---
title: Twitter/X Platform Overview
category: platform
platform: twitter
related:
  - ../../docs/api-reference/README.md
  - ./api-guide.md
  - ./authentication.md
---

# Twitter/X Platform

## Overview

Twitter (now X) is a real-time microblogging platform with a mature API that provides comprehensive access to tweets, comments, and moderation capabilities. This document outlines how to integrate Twitter comment moderation with the Moderation AI system.

## Platform Characteristics

| Attribute | Value |
|-----------|--------|
| **API Version** | v2 (current) |
| **Auth Method** | OAuth 2.0 / Bearer Token |
| **Rate Limiting** | Tiered (15-minute windows) |
| **Comments Model** | Replies to tweets |
| **Webhooks** | Supported (Account Activity API) |
| **Real-time** | Supported (Streaming API) |

## Capabilities

### Supported Operations

| Operation | Status | Notes |
|------------|--------|-------|
| Fetch posts | ✅ Full | Includes tweet metadata |
| Fetch comments | ✅ Full | Replies to tweets |
| Moderate comments | ✅ Full | Hide/reply visibility |
| Delete comments | ✅ Full | User's own tweets |
| Track posts | ✅ Full | Real-time webhooks |

### Moderation Actions

- **Hide reply**: Make reply not publicly visible
- **Delete tweet**: Remove tweet (own tweets only)
- **Flag**: Mark for manual review (internal)

## Integration Benefits

### Advantages

- **Mature API**: Well-documented, stable API
- **Real-time support**: Webhooks for instant comment notifications
- **Rich metadata**: User profiles, engagement metrics
- **Comprehensive search**: Full-text search capabilities
- **High rate limits**: 900 requests/15min for premium

### Considerations

- **Platform volatility**: Twitter/X frequently changes API terms
- **Tiered pricing**: Rate limits depend on access level
- **Content limits**: Tweets limited to 280 characters (blue: 25,000)
- **Reply threading**: Complex reply hierarchy

## Use Cases

### Content Creator Dashboard
```python
from moderation_ai.platforms import TwitterAPI

twitter = TwitterAPI.from_env()

# Monitor tweet engagement
tweet_id = "1234567890"
comments = await twitter.fetch_comments(tweet_id)

# Analyze and moderate
for comment in comments:
    decision = standards.validate(comment.text)
    if decision.action != "approve":
        await twitter.moderate_comment(comment.id, "hide")
```

### Brand Monitoring
```python
# Track brand mentions
query = "moderation_ai"
tweets = await twitter.fetch_posts(query)

for tweet in tweets:
    comments = await twitter.fetch_comments(tweet.id)
    # Analyze sentiment
    sentiment = sentiment_analyzer.batch_analyze(comments)
```

### Crisis Response
```python
# Set up real-time monitoring
async def on_comment_created(event):
    comment = event.data.comment
    
    # Quick abuse detection
    abuse = abuse_detector.analyze(comment)
    if abuse.is_abuse and abuse.severity == "critical":
        await twitter.moderate_comment(comment.id, "remove")
```

## API Access Levels

| Level | Rate Limits | Cost | Features |
|-------|--------------|-------|----------|
| **Free** | 300/15min | Free | Basic read access |
| **Basic** | 10,000/15min | $100/mo | Write access, search |
| **Pro** | 1,000,000/15min | $5,000/mo | Full API access |

## Quick Start

### 1. Get Twitter API Credentials

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new app
3. Generate API key, secret, and bearer token
4. Set environment variables:
   ```bash
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_BEARER_TOKEN=your_bearer_token
   ```

### 2. Initialize TwitterAPI

```python
from moderation_ai.platforms import TwitterAPI

# From environment variables
twitter = TwitterAPI.from_env()

# Or with explicit credentials
twitter = TwitterAPI(
    api_key="your_key",
    api_secret="your_secret",
    bearer_token="your_token"
)
```

### 3. Fetch Comments

```python
# Fetch comments for a tweet
tweet_id = "1234567890"
comments = await twitter.fetch_comments(tweet_id)

for comment in comments:
    print(f"{comment.author_username}: {comment.text}")
```

### 4. Moderate Comments

```python
from moderation_ai.core import StandardsEngine

standards = StandardsEngine()

# Analyze comment
comment = await twitter.fetch_comment(comment_id)
decision = standards.validate(comment.text)

# Apply moderation action
if decision.action == "hide":
    await twitter.moderate_comment(comment_id, "hide")
```

## Data Model Overview

### Tweet (Post)
```python
{
    "id": "1234567890",
    "text": "Tweet content",
    "author": {
        "id": "987654321",
        "username": "twitter_user",
        "name": "Twitter User"
    },
    "created_at": "2024-01-08T10:00:00Z",
    "public_metrics": {
        "reply_count": 25,
        "like_count": 150,
        "retweet_count": 30
    }
}
```

### Reply (Comment)
```python
{
    "id": "9876543210",
    "text": "This is a reply",
    "author": {
        "id": "456789012",
        "username": "replier",
        "name": "Replier User"
    },
    "in_reply_to_user_id": "987654321",
    "created_at": "2024-01-08T10:05:00Z"
}
```

## Platform-Specific Features

### Reply Threading
Twitter uses reply threading to organize conversations:
- `conversation_id`: Groups related replies
- `in_reply_to_user_id`: Direct reply target
- `referenced_tweets`: Reply hierarchy

### Extended Tweets
Blue users can post extended tweets:
- Long-form text up to 25,000 characters
- Note cards for easier reading
- Different comment structure

### Quote Tweets
Replies can quote other tweets:
- Adds context to replies
- Requires special handling for moderation

### Media Attachments
Comments can include:
- Images (up to 4)
- Videos (up to 2:20)
- GIFs
- Requires media content moderation

## Rate Limits

### Fetch Operations
- **Get Tweet**: 300 requests / 15 min
- **Tweet Replies**: 900 requests / 15 min
- **User Timeline**: 900 requests / 15 min

### Write Operations
- **Hide Reply**: 900 requests / 15 min
- **Delete Tweet**: 200 requests / 15 min

### Search
- **Recent Search**: 450 requests / 15 min
- **Full Archive**: Requires Enterprise access

See `./rate-limits.md` for detailed rate limit information.

## Authentication

### OAuth 2.0 Bearer Token (Recommended)
- Read-only access
- No user context
- Higher rate limits
- Use for: Reading tweets, fetching comments

### OAuth 1.0a User Context
- Full read/write access
- User-specific actions
- Lower rate limits
- Use for: Deleting tweets, moderating own content

See `./authentication.md` for detailed authentication setup.

## Moderation Guidelines

### Platform Rules
- **Harassment**: No targeted attacks
- **Hate Speech**: No discrimination
- **Spam**: No unwanted promotion
- **Misinformation**: Platform takes action

### Moderation Capabilities
- **Hide Reply**: Make reply invisible to public
- **Delete Tweet**: Remove tweet completely
- **Report**: Flag for Twitter review

See `./comment-moderation.md` for detailed moderation guidelines.

## Troubleshooting

### Issue: Rate Limit Errors

**Symptom**: 429 errors when fetching comments

**Solution**:
1. Check rate limit headers
2. Implement exponential backoff
3. Upgrade API tier if needed

### Issue: Missing Comments

**Symptom**: Not all comments showing

**Solution**:
1. Check tweet is public
2. Verify pagination is working
3. Some replies may be hidden by Twitter

### Issue: Permission Errors

**Symptom**: 403 errors when moderating

**Solution**:
1. Verify correct OAuth flow
2. Check app permissions
3. Ensure user owns the tweet

## Related Documentation

- **API Guide**: `./api-guide.md` - Detailed API usage
- **Authentication**: `./authentication.md` - Auth setup
- **Rate Limits**: `./rate-limits.md` - Rate limit details
- **Post Tracking**: `./post-tracking.md` - Post monitoring
- **Comment Moderation**: `./comment-moderation.md` - Moderation guidelines
- **Data Models**: `./data-models.md` - Data structure details
- **Examples**: `./examples/` - Usage examples

## Platform Status

| Status | Value |
|---------|-------|
| **Last Updated** | January 2024 |
| **API Version** | v2 |
| **Documentation Status** | Complete |
| **Implementation Status** | Phase 2 - Documentation |

---

**Platform**: Twitter/X
**Documentation Version**: 1.0
**Status**: Phase 2 - Documentation Complete
