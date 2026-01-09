---
title: Instagram Platform Overview
category: platform
platform: instagram
related:
  - ../../docs/api-reference/README.md
  - ./api-guide.md
  - ./authentication.md
---

# Instagram Platform

## Overview

Instagram is a visual-first social media platform focused on photos, videos, and Stories. This document outlines how to integrate Instagram comment moderation with the Moderation AI system using the Instagram Graph API.

## Platform Characteristics

| Attribute | Value |
|-----------|--------|
| **API Version** | Graph API (v18.0+) |
| **Auth Method** | OAuth 2.0 / Long-lived Access Token |
| **Rate Limiting** | Strict (hourly and daily limits) |
| **Comments Model** | Direct replies to media posts |
| **Webhooks** | Supported (Webhooks API) |
| **Real-time** | Limited (polling required) |

## Capabilities

### Supported Operations

| Operation | Status | Notes |
|------------|--------|-------|
| Fetch posts | ✅ Full | Media metadata and caption |
| Fetch comments | ✅ Full | Comments on media posts |
| Moderate comments | ✅ Full | Hide comment visibility |
| Delete comments | ✅ Full | User's own comments |
| Track posts | ✅ Full | Polling-based monitoring |
| Reply to comments | ✅ Full | As comments |

### Moderation Actions

- **Hide comment**: Make comment not publicly visible
- **Delete comment**: Remove comment completely (user's own comments)
- **Flag**: Mark for manual review (internal)

## Integration Benefits

### Advantages

- **Visual content**: Image and video posts with strong engagement
- **Growing audience**: Young, engaged user base
- **Story format**: Ephemeral content for quick engagement
- **Reels feature**: Short-form video content
- **Influencer focus**: Strong creator ecosystem

### Considerations

- **API restrictions**: Instagram API is more restricted than other platforms
- **Approval required**: Special permissions needed for comment operations
- **Rate limiting**: Strict limits may affect large-scale operations
- **Polling only**: No real-time comment webhooks
- **Content focus**: Primarily visual content (photos/videos)

## Use Cases

### Visual Content Moderation

```python
from moderation_ai.platforms import InstagramAPI

instagram = InstagramAPI.from_env()

# Monitor post engagement
media_id = "123456789_456789"
comments = await instagram.fetch_comments(media_id)

# Analyze and moderate
for comment in comments:
    decision = standards.validate(comment.text)
    if decision.action != "approve":
        await instagram.moderate_comment(comment.id, "hide")
```

### Hashtag Campaign Monitoring

```python
# Track hashtag campaign
hashtag = "moderationai"
media = await instagram.fetch_posts(hashtag=hashtag)

# Monitor comment sentiment
for post in media[:50]:
    comments = await instagram.fetch_comments(post.id)
    sentiment = sentiment_analyzer.batch_analyze(comments)
    
    if sentiment['average_sentiment'] < 0.3:
        print(f"Negative sentiment on post {post.id}")
```

### Influencer Post Monitoring

```python
# Monitor specific influencer
user_id = "123456789"
posts = await instagram.fetch_user_posts(user_id, limit=20)

for post in posts:
    comments = await instagram.fetch_comments(post.id)
    
    # Check for spam
    spam_score = spam_detector.analyze(comments)
    if spam_score['is_spam']:
        await instagram.hide_comments(post.id)
```

## API Access Levels

| Level | Rate Limits | Cost | Features |
|-------|--------------|-------|----------|
| **Sandbox** | 200/hour | Free | Development access |
| **Standard** | 5,000/hour | Business approval | Basic read/write |
| **Premium** | Custom | Contact sales | Higher limits, webhooks |

## Quick Start

### 1. Get Instagram API Credentials

1. Go to [Instagram Basic Display API](https://developers.facebook.com/docs/instagram-basic-display-api/)
2. Create a new app
3. Generate access token
4. Set environment variables:

```bash
INSTAGRAM_ACCESS_TOKEN=your_access_token
INSTAGRAM_APP_ID=your_app_id
INSTAGRAM_APP_SECRET=your_app_secret
```

### 2. Initialize InstagramAPI

```python
from moderation_ai.platforms import InstagramAPI

# From environment variables
instagram = InstagramAPI.from_env()

# Or with explicit credentials
instagram = InstagramAPI(
    access_token="your_token",
    app_id="your_app_id",
    app_secret="your_app_secret"
)
```

### 3. Fetch Comments

```python
# Fetch comments for a media post
media_id = "123456789_456789"
comments = await instagram.fetch_comments(media_id)

for comment in comments:
    print(f"{comment.username}: {comment.text}")
```

### 4. Moderate Comments

```python
from moderation_ai.core import StandardsEngine

standards = StandardsEngine()

# Analyze comment
comment = await instagram.fetch_comment(comment_id)
decision = standards.validate(comment.text)

# Apply moderation action
if decision.action == "hide":
    await instagram.moderate_comment(comment_id, "hide")
```

## Data Model Overview

### Media (Post)

```python
{
    "id": "123456789_456789",
    "media_type": "IMAGE",
    "media_url": "https://instagram.com/p/...",
    "caption": "Post caption text",
    "timestamp": "2024-01-08T10:00:00Z",
    "like_count": 150,
    "comments_count": 25,
    "owner": {
        "id": "123456789",
        "username": "instagram_user"
    },
    "is_video": false
}
```

### Comment

```python
{
    "id": "17845678901234567",
    "text": "Great photo! Love the composition",
    "timestamp": "2024-01-08T10:05:00Z",
    "media_id": "123456789_456789",
    "owner": {
        "id": "987654321",
        "username": "commenter_user",
        "profile_pic": "https://instagram.com/..."
    },
    "like_count": 12,
    "hidden": false
}
```

## Platform-Specific Features

### Media Types

Instagram supports multiple media types:
- **Image**: Static photo posts
- **Video**: Video content (up to 60 minutes)
- **Carousel**: Multiple images/videos in one post
- **Story**: Ephemeral content (24 hours)
- **Reel**: Short-form video (up to 60 seconds)

### Comment Visibility

Comments can be in different visibility states:
- **Visible**: Publicly viewable
- **Hidden**: Hidden by moderation or user
- **Restricted**: Limited visibility (e.g., private accounts)

### User Types

Different user types on Instagram:
- **Regular users**: Standard accounts
- **Business accounts**: Verified business profiles
- **Creator accounts**: Influencers and content creators
- **Bot accounts**: Automated profiles

## Rate Limits

### Fetch Operations

- **Media**: 200 requests/hour
- **Comments**: 5,000 requests/hour
- **User Timeline**: 5,000 requests/hour

### Write Operations

- **Moderate Comment**: 5,000 requests/hour
- **Delete Comment**: 200 requests/hour
- **Reply**: 5,000 requests/hour

### Search

- **Hashtag Search**: 30 requests/hour
- **User Search**: 60 requests/hour

See `./rate-limits.md` for detailed rate limit information.

## Authentication

### OAuth 2.0 Bearer Token (Recommended)

- **Permissions needed**: `instagram_basic`, `pages_read_engagement`
- **Token type**: Long-lived access token
- **Use for**: Reading posts, fetching comments
- **Rate limits**: Standard limits

### Basic Display API with User Context

- **Permissions needed**: `instagram_basic`, `pages_manage_metadata`
- **Token type**: Long-lived access token with user context
- **Use for**: Moderating comments, deleting content
- **Rate limits**: Lower limits for write operations

See `./authentication.md` for detailed authentication setup.

## Moderation Guidelines

### Platform Rules

- **Harassment**: No targeted attacks or bullying
- **Hate Speech**: No discriminatory language
- **Spam**: No unwanted promotion or repetitive content
- **Nudity/Sexual**: No inappropriate content
- **Violence**: No violent or harmful content

### Moderation Capabilities

- **Hide comment**: Make comment invisible
- **Delete comment**: Remove comment (owner only)
- **Restrict**: Limit comment visibility
- **Report**: Flag for Instagram review

See `./comment-moderation.md` for detailed moderation guidelines.

## Troubleshooting

### Issue: Rate Limit Errors

**Symptom**: 429 errors when fetching comments

**Solution**:
1. Check rate limit headers
2. Implement caching strategies
3. Use pagination properly
4. Respect retry-after headers

### Issue: Permission Errors

**Symptom**: 403 errors when moderating comments

**Solution**:
1. Verify OAuth flow
2. Check app permissions
3. Ensure token is valid
4. Request correct permission scope

### Issue: Missing Comments

**Symptom**: Not all comments showing

**Solution**:
1. Check pagination parameters
2. Verify post is public
3. Some comments may be restricted
4. Check for rate limiting

### Issue: Media Not Found

**Symptom**: 404 errors when fetching media

**Solution**:
1. Verify media ID format
2. Check if media was deleted
3. Ensure account has access
4. Check if account is private

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
| **API Version** | v18.0+ |
| **Documentation Status** | Phase 4 - In Progress |
| **Implementation Status** | Phase 6 - Scheduled |

---

**Platform**: Instagram
**Documentation Version**: 1.0
**Status**: Phase 4 - Documentation In Progress
