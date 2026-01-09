---
title: Instagram API Guide
category: platform
platform: instagram
related:
  - ../README.md
  - ./authentication.md
  - ./rate-limits.md
  - ./data-models.md
---

# Instagram API Guide

## Overview

This guide provides comprehensive documentation for interacting with the Instagram Graph API v18.0+ for comment moderation purposes.

## Authentication Setup

### OAuth 2.0 Bearer Token

Instagram requires a long-lived access token for API access.

```python
from moderation_ai.platforms import InstagramAPI

# Initialize with access token
instagram = InstagramAPI(
    access_token="your_access_token_here"
)

# Or use from environment
instagram = InstagramAPI.from_env()
```

### Required Permissions

| Permission | Description | Use Case |
|------------|-------------|----------|
| `instagram_basic` | Read posts and basic engagement metrics | Fetching posts and comments |
| `pages_read_engagement` | Read page-level metrics | Analytics and insights |
| `pages_manage_metadata` | Read and write page metadata | Post management |
| `pages_manage_engagement` | Moderate and manage comments | Comment moderation |

See `./authentication.md` for detailed setup instructions.

## Core API Operations

### 1. Fetch Media Posts

```python
# Fetch posts by hashtag
hashtag = "moderationai"
posts = await instagram.fetch_posts(
    query=hashtag,
    limit=25
)

# Fetch posts by user ID
user_id = "1234567890"
posts = await instagram.fetch_posts(
    query=user_id,
    limit=25
)
```

### 2. Fetch Comments

```python
# Fetch comments for a media post
media_id = "123456789_4567890"
comments = await instagram.fetch_comments(
    post_id=media_id,
    limit=50
)

# Iterate through comments
for comment in comments:
    print(f"{comment.username}: {comment.text}")
```

### 3. Moderate Comments

```python
# Hide a comment
comment_id = "17845678901234567"
success = await instagram.moderate_comment(
    comment_id=comment_id,
    action="hide"
)

# Delete own comment (available for account owners)
comment_id = "17845678901234567"
success = await instagram.moderate_comment(
    comment_id=comment_id,
    action="delete"
)
```

### 4. Reply to Comments

```python
# Reply to a comment
comment_id = "17845678901234567"
success = await instagram.reply_to_comment(
    comment_id=comment_id,
    text="Thank you for your feedback!"
)
```

## Pagination

Instagram uses cursor-based pagination for large result sets.

```python
# Fetch all comments with pagination
media_id = "123456789_4567890"
all_comments = []
after_cursor = None

while True:
    comments = await instagram.fetch_comments(
        post_id=media_id,
        limit=50,
        after=after_cursor
    )
    
    if not comments:
        break
    
    all_comments.extend(comments)
    after_cursor = comments[-1].id if comments else None
    
print(f"Total comments fetched: {len(all_comments)}")
```

## Rate Limits

Instagram enforces strict rate limits:

| Endpoint | Rate Limit | Time Window |
|----------|-------------|--------------|
| Media | 200 requests/hour | 1 hour |
| Comments | 5,000 requests/hour | 1 hour |
| User Timeline | 5,000 requests/hour | 1 hour |
| Search | 30 requests/hour | 1 hour |

See `./rate-limits.md` for detailed rate limit information and handling strategies.

## Error Handling

```python
from moderation_ai.utils import RateLimitError, AuthenticationError

try:
    comments = await instagram.fetch_comments(media_id)
except RateLimitError as e:
    print(f"Rate limit reached: {e}")
    # Wait and retry
    await asyncio.sleep(e.retry_after)
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Re-authenticate
    instagram = InstagramAPI.from_env()
```

## Best Practices

### 1. Caching Strategy

```python
# Cache media metadata to reduce API calls
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_media_info(media_id):
    return await instagram.get_media(media_id)
```

### 2. Batch Processing

```python
# Process comments in batches
batch_size = 25
comments = await instagram.fetch_comments(media_id, limit=batch_size)

for i in range(0, len(comments), batch_size):
    batch = comments[i:i+batch_size]
    # Process batch
    await process_batch(batch)
```

### 3. Error Recovery

```python
# Implement exponential backoff
import asyncio

async def fetch_with_retry(media_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await instagram.fetch_comments(media_id)
        except RateLimitError:
            wait_time = 2 ** attempt  # 2s, 4s, 8s
            await asyncio.sleep(wait_time)
        except Exception:
            raise
    
    raise Exception("Max retries exceeded")
```

## Webhooks Integration

Instagram doesn't provide real-time comment webhooks. Use polling for monitoring:

```python
import asyncio

async def monitor_post(media_id):
    while True:
        comments = await instagram.fetch_comments(media_id, limit=50)
        
        # Process new comments
        for comment in comments:
            await analyze_and_moderate(comment)
        
        # Wait before next check
        await asyncio.sleep(60)  # Check every minute
```

## Data Models

See `./data-models.md` for detailed structure of Instagram objects:

- **Media (Post)**: Photos, videos, carousels
- **Comment**: User comments on media
- **User**: Instagram user profiles
- **Hashtag**: Hashtag objects

## Platform-Specific Features

### Instagram Stories

```python
# Fetch story comments (limited)
story_id = "123456789_4567890"
comments = await instagram.fetch_comments(
    post_id=story_id,
    content_type="story"
)
```

### Instagram Reels

```python
# Reel comments follow standard media format
reel_id = "123456789_4567890"
comments = await instagram.fetch_comments(
    post_id=reel_id,
    content_type="reel"
)
```

### Media Types Handling

```python
# Instagram supports multiple media types
media_types = {
    "IMAGE": "Static photo",
    "VIDEO": "Video content",
    "CAROUSEL": "Multiple media items",
    "ALBUM": "Photo album",
    "STORY": "Ephemeral content",
    "REEL": "Short-form video"
}

async def handle_media(media):
    media_type = media.get("media_type", "IMAGE")
    handler = media_types.get(media_type)
    
    if handler:
        await process_by_type(media, handler)
```

## Testing and Development

### Sandbox Environment

Use Instagram Basic Display API for development:
1. Create test app in Meta for Developers
2. Generate test access token
3. Test with non-production accounts

### Testing Tools

```bash
# Use curl for API testing
curl -X GET "https://graph.instagram.com/me/media" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Migration from Deprecated APIs

Instagram has deprecated several APIs:
- ❌ Basic Display API (legacy)
- ❌ IG Hashtag API
- ✅ Graph API (current)

Ensure you're using the latest Graph API endpoints.

## Troubleshooting

### Issue: 401 Unauthorized

**Cause**: Invalid or expired access token

**Solution**:
1. Verify token is valid and not expired
2. Regenerate token if needed
3. Check token permissions

### Issue: 429 Too Many Requests

**Cause**: Exceeded rate limit

**Solution**:
1. Implement rate limiting in your application
2. Use caching to reduce API calls
3. Monitor rate limit headers

### Issue: Empty Comment Lists

**Cause**: Comments disabled or restricted access

**Solution**:
1. Verify account has access to media
2. Check if comments are enabled for post
3. Verify permissions include `instagram_basic`

## Related Documentation

- **Authentication**: `./authentication.md` - Detailed auth setup
- **Rate Limits**: `./rate-limits.md` - Rate limit details
- **Data Models**: `./data-models.md` - Object structures
- **Examples**: `./examples/` - Code examples

## Platform Status

| Status | Value |
|---------|-------|
| **API Version** | v18.0+ |
| **Last Updated** | January 2024 |
| **Documentation Version** | 1.0 |
| **Implementation Status** | Phase 4 - In Progress |

---

**Platform**: Instagram
**Documentation Version**: 1.0
**Status**: Phase 4 - Documentation In Progress
