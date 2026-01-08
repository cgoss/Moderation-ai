---
title: YouTube API Guide
category: platform
platform: youtube
related:
  - ./README.md
  - ./authentication.md
  - ../../docs/api-reference/README.md
---

# YouTube API Guide

## Overview

This guide provides comprehensive instructions for using YouTube Data API v3 with Moderation AI library, including fetching videos, retrieving comments, and applying moderation actions.

## API Endpoints

### Core Endpoints

| Operation | HTTP Method | Endpoint | Purpose |
|-----------|--------------|---------|----------|
| Get Video | GET | `/youtube/v3/videos` | Retrieve single video |
| Get Comments | GET | `/youtube/v3/commentThreads` | Fetch video comments |
| Search Videos | GET | `/youtube/v3/search` | Search videos |
| Get Channel | GET | `/youtube/v3/channels` | Retrieve channel info |
| Delete Comment | DELETE | `/youtube/v3/comments/:id` | Delete comment (owner) |
| Moderate Comment | UPDATE | `/youtube/moderation/comments/setModerationStatus` | Moderate comment |

## Initialization

### From Environment Variables

```python
from moderation_ai.platforms import YouTubeAPI

# Load from environment
youtube = YouTubeAPI.from_env()

# Environment variables needed:
# YOUTUBE_API_KEY=your_api_key
```

### Explicit Credentials

```python
youtube = YouTubeAPI(
    api_key="your_api_key"
)

await youtube.authenticate()
```

## Fetching Videos

### Get Single Video

```python
video_id = "abc123"
video = await youtube.fetch_video(video_id)

print(f"Video: {video.title}")
print(f"Author: {video.channel_title}")
```

### Search Videos

```python
query = "moderation ai"
videos = await youtube.search_videos(query)

for video in videos:
    print(f"{video.title}")
```

### Get Channel Videos

```python
channel_id = "UC..."
videos = await youtube.fetch_channel_videos(channel_id)

for video in videos:
    print(f"{video.title}")
```

## Fetching Comments

### Get Video Comments

```python
video_id = "abc123"
comments = await youtube.fetch_comments(video_id)

for comment in comments:
    print(f"{comment.author_display_name}: {comment.text}")
```

### Pagination

```python
video_id = "abc123"
page_token = None
all_comments = []

while True:
    result = await youtube.fetch_comments(
        video_id,
        page_token=page_token,
        max_results=100
    )
    
    all_comments.extend(result.comments)
    
    if not result.next_page_token:
        break
    
    page_token = result.next_page_token
```

### With Metadata

```python
comments = await youtube.fetch_comments(
    video_id,
    part="snippet",  # Request snippet data
    max_results=100
)

for comment in comments:
    print(f"{comment.author_display_name}: {comment.text}")
    print(f"  Likes: {comment.like_count}")
    print(f"  Replies: {comment.total_reply_count}")
```

## Creating Comments

### Reply to Comment

```python
parent_comment_id = "def456"
reply_text = "This is a reply"

comment = await youtube.post_comment(parent_comment_id, reply_text)
```

### Update Comment

```python
comment_id = "def456"
new_text = "Updated comment text"

comment = await youtube.update_comment(comment_id, new_text)
```

## Moderating Comments

### Delete Comment

```python
comment_id = "def456"
deleted = await youtube.delete_comment(comment_id)

if deleted:
    print("Comment deleted successfully")
```

### Moderate Comment (Content Owner API)

```python
comment_id = "def456"

await youtube.moderate_comment(
    comment_id,
    moderation_status="heldForReview"
)
```

## Post Tracking

### Enable Comment Tracking

```python
video_id = "abc123"
await youtube.track_post(video_id)

# Monitor for new comments
```

### Check Post Status

```python
video_id = "abc123"
status = await youtube.get_post_status(video_id)

print(f"Comment count: {status.comment_count}")
print(f"Like count: {status.like_count}")
```

## Error Handling

### Rate Limit Error

```python
from moderation_ai.utils import RateLimitExceeded

try:
    comments = await youtube.fetch_comments(video_id)
except RateLimitExceeded as e:
    print(f"Rate limit exceeded. Quota: {e.quota}")
```

### Authentication Error

```python
from moderation_ai.utils import AuthenticationError

try:
    await youtube.authenticate()
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
```

## Advanced Operations

### Search with Filters

```python
query = "moderation ai"
videos = await youtube.search_videos(
    query=query,
    max_results=100,
    order="relevance",
    published_after="2024-01-01T00:00:00Z"
)
```

### Get Multiple Videos

```python
video_ids = ["abc123", "def456", "ghi789"]
videos = await youtube.fetch_videos(video_ids)

for video in videos:
    print(f"{video.title}")
```

### Get Channel Information

```python
channel_id = "UC..."
channel = await youtube.fetch_channel(channel_id)

print(f"Channel: {channel.snippet.title}")
print(f"Subscribers: {channel.statistics.subscriber_count}")
```

## Usage Examples

### Fetch and Analyze

```python
import asyncio
from moderation_ai.platforms import YouTubeAPI
from moderation_ai.analysis import SentimentAnalyzer

async def main():
    youtube = YouTubeAPI.from_env()
    analyzer = SentimentAnalyzer()
    
    # Fetch video
    video_id = "abc123"
    video = await youtube.fetch_video(video_id)
    
    # Fetch comments
    comments = await youtube.fetch_comments(video_id)
    
    # Analyze sentiment
    results = analyzer.batch_analyze(comments)
    
    for comment, result in zip(comments, results):
        print(f"@{comment.author_display_name}: {result.sentiment} ({result.score:.2f})")

asyncio.run(main())
```

### Moderate Comments

```python
import asyncio
from moderation_ai.platforms import YouTubeAPI
from moderation_ai.core import StandardsEngine

async def main():
    youtube = YouTubeAPI.from_env()
    standards = StandardsEngine()
    
    video_id = "abc123"
    
    # Fetch comments
    comments = await youtube.fetch_comments(video_id)
    
    # Analyze and moderate
    for comment in comments:
        decision = standards.validate(comment.text)
        
        if decision.action != "approve":
            await youtube.moderate_comment(
                comment.id,
                decision.action
            )
            print(f"Moderated: {decision.action}")

asyncio.run(main())
```

## Best Practices

### 1. Use API Key

```python
# Good - from environment
youtube = YouTubeAPI.from_env()

# Bad - hardcoded key
youtube = YouTubeAPI(api_key="your_api_key")
```

### 2. Respect Rate Limits

```python
# Check quota
status = youtube.get_rate_limit_status()

if status.remaining < 100:
    print("Warning: Approaching rate limit")
```

### 3. Use Pagination

```python
# Good - fetch all pages
all_comments = []
page_token = None

while True:
    result = await youtube.fetch_comments(video_id, page_token=page_token)
    all_comments.extend(result.comments)
    if not result.next_page_token:
        break
    page_token = result.next_page_token
```

### 4. Request Only Needed Fields

```python
# Good - specific fields
comments = await youtube.fetch_comments(
    video_id,
    part="snippet",
    max_results=100
)

# Bad - all fields (slower)
comments = await youtube.fetch_comments(video_id)
```

### 5. Handle Errors Gracefully

```python
# Good - proper error handling
try:
    comments = await youtube.fetch_comments(video_id)
except RateLimitExceeded:
    print("Rate limit exceeded")
except Exception as e:
    print(f"Error: {e}")

# Bad - no error handling
comments = await youtube.fetch_comments(video_id)
```

## Troubleshooting

### Issue: 403 Forbidden

**Possible causes**:
- Invalid API key
- API quota exceeded
- Wrong auth method

**Solution**:
1. Verify API key is correct
2. Check quota in Google Cloud Console
3. Ensure correct auth setup

### Issue: 404 Not Found

**Possible causes**:
- Video doesn't exist
- Video is private
- Video ID is invalid

**Solution**:
1. Verify video exists and is public
2. Check video ID format
3. Confirm account has access

### Issue: Empty Comment List

**Possible causes**:
- Comments disabled on video
- Video has no comments
- Private video

**Solution**:
1. Verify video exists
2. Check comment settings
3. Confirm video is public

## Related Documentation

- **Authentication**: `./authentication.md` - Auth setup
- **Rate Limits**: `./rate-limits.md` - Rate limit details
- **Post Tracking**: `./post-tracking.md` - Post monitoring
- **Data Models**: `./data-models.md` - Data structures
- **Examples**: `./examples/` - Usage examples

---

**Last Updated**: January 2024
**Status**: Phase 2 - Documentation Complete
