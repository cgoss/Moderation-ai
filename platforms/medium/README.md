---
title: Medium Platform Overview
category: platform
platform: medium
related:
  - ../../docs/api-reference/README.md
  - ./api-guide.md
  - ./authentication.md
---

# Medium Platform

## Overview

Medium is a publishing platform focused on long-form written content. This document outlines how to integrate Medium comment moderation with the Moderation AI system.

## Platform Characteristics

| Attribute | Value |
|-----------|--------|
| **API Version** | v2 (MxGraph API) |
| **Auth Method** | OAuth 2.0 (OAuth) |
| **Rate Limiting** | Tiered (request-based) |
| **Comments Model** | Replies to published posts |
| **Webhooks** | Not supported |
| **Real-time** | Not supported (no webhooks) |
| **Publishing** | ✅ Full | Create articles, update existing content |

## Capabilities

### Supported Operations

| Operation | Status | Notes |
|------------|--------|-------|
| Fetch posts | ✅ Full | Article metadata and content |
| Fetch comments | ✅ Full | Comments on published posts |
| Moderate comments | ✅ Full | Hide/reply visibility |
| Publish comments | ✅ Full | Create new comments |
| Edit comments | ✅ Full | Update own comments |
| Track posts | ✅ Full | Monitor for comments |
| Like posts | ✅ Full | Like articles |

### Moderation Actions

- **Hide comment**: Make comment not publicly visible
- **Delete comment**: Remove comment completely
- **Edit comment**: Modify comment content
- **Publish comment**: Approve a hidden comment

## Integration Benefits

### Advantages

- **High-Quality Content**: Focus on long-form articles
- **Intellectual Audience**: Professional and engaged readers
- **Low Spam Volume**: Genuine comments with high bar to entry
- **Professional Content**: Thoughtful discussions
- **Moderate Comment Volume**: Manage comments on published posts
- **Post Management**: Full CRUD operations on posts

### Considerations

- **Platform Complexity**: Medium API is more complex than social APIs
- **Rate Limiting**: Request-based tier (not time-windowed)
- **Content Lifecycle**: Articles can be updated frequently
- **Comment Depth**: Threaded comments on articles
- **No Native Video Support**: Medium doesn't host comments

## Use Cases

### Article Moderation Dashboard

```python
from moderation_ai.platforms import MediumAPI

medium = MediumAPI.from_env()

# Monitor article engagement
post_id = "1234567890_4567890"
comments = await medium.fetch_comments(post_id)

# Analyze and moderate
for comment in comments:
    decision = standards.validate(comment.text)
    if decision.action != "approve":
        await medium.hide_comment(comment.id)
        print(f"Comment {comment.id}: {decision.action}")
```

### Content Strategy Tracking

```python
# Track comments by sentiment
from moderation_ai.analysis import SentimentAnalyzer

sentiment = SentimentAnalyzer()

async def track_comment_sentiment():
    post_id = "1234567890_4567890"
    comments = await medium.fetch_comments(post_id, limit=100)
    
    sentiments = sentiment.analyze_batch_analyze(comments)
    
    # Summarize sentiment
    positive_count = sum(1 for s in sentiments if s.sentiment == 'positive')
    negative_count = sum(1 for s in sentiments if s.sentiment == 'negative')
    total = len(comments)
    
    print(f"Positive: {positive_count}/{total} ({positive_count/total:.1%}%)")
    print(f"Negative: {negative_count}/{total} ({negative_count/total:.1f}%)")
```

### Bulk Comment Moderation

```python
async def bulk_moderate():
    """
    Moderate multiple comments at once.
    """
    medium = MediumAPI.from_env()
    standards = StandardsEngine(auto_moderate=True)
    
    # Fetch recent comments across multiple posts
    post_ids = ["post1", "post2", "post3"]
    all_comments = []
    
    for post_id in post_ids:
        comments = await medium.fetch_comments(post_id, limit=100)
        all_comments.extend(comments)
    
    print(f"Fetched {len(all_comments)} comments")
    
    # Bulk moderate
    for comment in all_comments:
        result = standards.validate(comment.text)
        
        if result.action == "remove":
            await medium.delete_comment(comment.id)
        elif result.action == "hide":
            await medium.hide_comment(comment.id)
        elif result.action == "flag":
            print(f"Flagged comment {comment.id}")
```

## API Access Levels

| Level | Rate Limits | Cost | Features |
|-------|--------------|-------|----------|
| **Free** | 200 requests/day | Free | Read access only |
| **Basic** | 1,000 requests/day | $25/mo | Full read/write access |
| **Pro** | 5,000 requests/day | $100/mo | Priority support |
| **Enterprise** | Custom | Contact sales | Custom limits |

## Quick Start

### 1. Get Medium API Credentials

1. Go to [Medium Partner Program](https://developers.facebook.com/docs/)
2. Create a new app
3. Generate OAuth client credentials
4. Set environment variables:

```bash
MEDIUM_CLIENT_ID=your_client_id
MEDIUM_CLIENT_SECRET=your_client_secret
MEDIUM_ACCESS_TOKEN=your_access_token
```

### 2. Initialize MediumAPI

```python
from moderation_ai.platforms import MediumAPI

# From environment variables
medium = MediumAPI.from_env()

# Or with explicit credentials
medium = MediumAPI(
    client_id="your_client_id",
    client_secret="your_client_secret",
    access_token="your_access_token"
)
```

### 3. Fetch Comments

```python
# Fetch comments for a post
post_id = "1234567890_4567890"

comments = await medium.fetch_comments(post_id, limit=50)

for comment in comments:
    print(f"{comment.author}: {comment.text}")
```

### 4. Moderate Comments

```python
from moderation_ai.core import StandardsEngine

# Analyze comment
standards = StandardsEngine()

comment = await medium.fetch_comment(comment_id)
decision = standards.validate(comment.text)

# Apply moderation action
if decision.action == "hide":
    await medium.hide_comment(comment_id)
```

## Data Model Overview

### Post (Article)

```python
{
    "id": "1234567890_4567890",
    "title": "Article Title",
    "content": "Article content text...",
    "author": {
        "id": "987654321",
        "username": "medium_author",
        "name": "Medium Author"
    },
    "created_at": "2024-01-08T10:00:00Z",
    "updated_at": "2024-01-10:05:00Z",
    "published": true,
    "like_count": 150,
    "clap_count": 25,
    "comment_count": 42,
    "status": "public",
    "canonical_url": "https://medium.com/@medium_author/slug"
}
```

### Comment (Reply to Article)

```python
{
    "id": "17845678901234567",
    "text": "This is a reply",
    "author": {
        "id": "1234567890_4567890",
        "username": "medium_replier"
    },
    "parent_id": "1234567890_4567890",
    "parent_author_id": "987654321",
    "created_at": "2024-01-08T10:05:00Z",
    "like_count": 5,
    "replies_count": 2,
    "parent_username": "medium_author",
    "status": "public",
    "canonical_url": "https://medium.com/@medium_author/slug#comment-1784567890"
}
```

## Platform-Specific Features

### Post Types

Medium supports these post types:

- **Article**: Long-form written content (blog posts)
- **Response Post**: Comments responding to published posts
- **Story**: Medium-Only post (temporary) - comments have different structure
- **Series**: Grouped articles with tags

### Comment Structure

Comments follow a threaded structure:

- **Root comments**: Top-level comments on articles
- **Reply chains**: Threaded responses
- **Nested comments**: Replies to replies
- **Indirect replies**: Responses to existing replies

### Content Moderation

Medium content is typically more formal and intellectual:

**Examples of content requiring different moderation**:
- **Personal attacks**: More frequent on Twitter, less on Medium
- **Spam**: Less common due to content barriers
- **Self-promotion**: Rare on Medium due to editorial norms
- **Political content**: Requires careful context-aware moderation

## Rate Limits

### Request-Based Limits

| Operation | Rate Limit | Time Window | Notes |
|----------|-------------|--------------|-------|
| **Read Operations** | 200 requests/day | Request-based |
| **Write Operations** | 1,000 requests/day | Request-based |

### Tier Details

Free Plan**: 200 requests/day (read only)
Basic Plan: 1,000 requests/day (read + write)
Pro Plan: 5,000 requests/day (priority)
Enterprise: Custom limits

## Authentication

### OAuth 2.0 Flow (Recommended)

Medium uses OAuth 2.0 with these steps:

1. User authorization
2. App authorization
3. Access token generation

```python
from oauthlib import OAuth2Session

def get_medium_credentials():
    """
    Get Medium OAuth 2.0 credentials.
    """
    # Step 1: User authorization
    auth_url = "https://www.medium.com/oauth2/authorize"
    params = {
        "response_type": "code",
        "client_id": "MEDIUM_CLIENT_ID",
        "redirect_uri": "https://medium.com/oauth2/auth",
        "scope": "basic",
    }
    
    auth = OAuth2Session()
    auth_url = f"{auth_url}?client_id={params['client_id']}&redirect_uri={params['redirect_uri']}"
    
    # Step 2: App authorization
    data = {
        "grant_type": "authorization_code",
        "code": "AUTHORIZATION_CODE",
        "redirect_uri": params['redirect_uri'],
        "scope": params["scope"],
    }
    
    response = requests.post("https://graph.facebook.com/oauth2/access_token", data=data)
    token_data = response.json()
    
    return token_data["access_token"]
```

## Authentication Setup

```python
from moderation_ai.platforms import MediumAPI

# Use environment configuration
medium = MediumAPI.from_env()

# Or configure explicitly
medium = MediumAPI(
    client_id="your_client_id",
    client_secret="your_client_secret",
    access_token="your_access_token"
)
```

## Moderation Guidelines

### Platform Rules

- **Intellectual Property**: Respect copyrights and authorship
- **Constructive Feedback**: Allow for disagreement
- **Civility Required**: Maintain civil discourse
- **No Plagiarism**: Check for original content sources
- **Quality Standards**: Medium readers expect high-quality discussions
- **Editorial Content**: Factual reporting and corrections

### Moderation Capabilities

- **Hide comment**: Remove comment from public visibility
- **Delete comment**: Remove comment entirely
- **Edit comment**: Modify comment text to remove violations
- **Publish comment**: Approve hidden comments
- **Report**: Flag for internal review

See `./comment-moderation.md` for detailed moderation guidelines.

## Troubleshooting

### Issue: Rate Limit Errors

**Symptom**: 429 Too Many Requests errors

**Solution**:
1. Implement request queuing
2. Use caching strategies
3. Monitor request counts
4. Upgrade API tier if needed

### Issue: Permission Errors

**Symptom**: 403 Forbidden errors

**Solution**:
1. Verify OAuth 2.0 flow is correct
2. Check app permissions
3. Verify access token is valid
4. Request additional permissions if needed

### Issue: Comment Not Found

**Symptom**: 404 errors when fetching comments

**Solution**:
1. Verify post exists and is public
2. Check post ID format
3. Ensure you're using correct API version
4. Check if comments are enabled on post

## Related Documentation

- **API Guide**: `./api-guide.md` - Detailed API usage
- **Authentication**: `./authentication.md` - Auth setup
- **Rate Limits**: `./rate-limits.md` - Rate limit handling
- **Comment Moderation**: `./comment-moderation.md` - Moderation guidelines
- **Post Tracking**: `./post-tracking.md` - Post monitoring
- **Data Models**: `./data-models.md` - Data structure

## Platform Status

| Status | Value |
|---------|-------|
| **Last Updated** | January 2024 |
| **API Version** | v2 (MxGraph) |
| **Documentation Status** | Phase 4 - In Progress |
| **Implementation Status** | Phase 6 - Scheduled |

---

**Platform**: Medium
**Documentation Version**: 1.0
**Status**: Phase 4 - Documentation In Progress
