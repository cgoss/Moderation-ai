---
title: YouTube Post Tracking
category: platform
platform: youtube
related:
  - ./README.md
  - ./api-guide.md
  - ../../docs/api-reference/webhooks.md
---

# YouTube Post Tracking

## Overview

YouTube uses polling-based tracking for post comments, as real-time webhooks are limited to Pub/Sub events. This document describes how to track YouTube videos for new comments.

## Tracking Methods

### 1. Polling-Based Tracking (Recommended)

**Use Case**: Monitor specific videos for new comments

**Advantages**:
- Simple to implement
- Works for any public video
- No webhooks needed

**Limitations**:
- Not real-time
- Polling interval affects latency
- Wastes quota on frequent polling

### 2. Pub/Sub Events

**Use Case**: Monitor channel for new videos

**Advantages**:
- Real-time notifications
- Efficient for channel monitoring
- No polling needed

**Limitations**:
- Limited to Pub/Sub subscriptions
- No individual video tracking

## Polling-Based Tracking

### Basic Polling

```python
import asyncio
from moderation_ai.platforms import YouTubeAPI

async def poll_video_comments(video_id, interval_seconds=60):
    youtube = YouTubeAPI.from_env()
    
    last_comment_count = 0
    
    while True:
        comments = await youtube.fetch_comments(video_id)
        current_count = len(comments)
        
        # Check for new comments
        if current_count > last_comment_count:
            new_comments = comments[last_comment_count:]
            
            for comment in new_comments:
                print(f"New comment from {comment.author_display_name}: {comment.text}")
                
                # Analyze and moderate
                result = analyzer.analyze(comment)
                if result.violation_detected:
                    action = result.recommended_action
                    await youtube.moderate_comment(comment.id, action)
            
            last_comment_count = current_count
        
        await asyncio.sleep(interval_seconds)

# Start polling
asyncio.create_task(poll_video_comments("video_id"))
```

### Track Multiple Videos

```python
async def track_multiple_videos(video_ids, interval_seconds=60):
    youtube = YouTubeAPI.from_env()
    
    video_data = {}
    
    for video_id in video_ids:
        video_data[video_id] = {"last_count": 0}
    
    while True:
        for video_id in video_ids:
            # Fetch comments
            comments = await youtube.fetch_comments(video_id)
            current_count = len(comments)
            
            last_count = video_data[video_id]["last_count"]
            
            # Check for new comments
            if current_count > last_count:
                new_comments = comments[last_count:]
                
                for comment in new_comments:
                    result = analyzer.analyze(comment)
                    if result.violation_detected:
                        await youtube.moderate_comment(comment.id, "remove")
                
                # Update count
                video_data[video_id]["last_count"] = current_count
            
        # Wait before next cycle
        await asyncio.sleep(interval_seconds)
```

## Pub/Sub Tracking

### Subscribe to Channel

```python
from moderation_ai.platforms import YouTubeAPI

async def subscribe_channel(channel_id):
    youtube = YouTubeAPI.from_env()
    
    # Subscribe to Pub/Sub feed
    await youtube.subscribe_channel(channel_id)
    
    print(f"Subscribed to channel: {channel_id}")
```

### Monitor Channel

```python
async def monitor_channel(channel_id):
    youtube = YouTubeAPI.from_env()
    
    # Get channel videos
    videos = await youtube.fetch_channel_videos(channel_id, limit=50)
    
    for video in videos:
        # Track each video
        asyncio.create_task(
            poll_video_comments(video.id)
        )
    
    # Keep monitoring
    await asyncio.sleep(3600)  # Run for 1 hour
```

## Event Handling

### Handle New Comment

```python
async def handle_new_comment(comment):
    # Analyze comment
    result = analyzer.analyze(comment)
    
    # Log analysis
    logger.info(f"Comment {comment.id}: {result.sentiment}")
    
    # Moderate if needed
    if result.violation_detected:
        action = result.recommended_action
        await youtube.moderate_comment(comment.id, action)
```

### Handle Comment Updated

```python
async def handle_comment_updated(comment):
    # Re-analyze updated comment
    result = analyzer.analyze(comment)
    
    # Check if moderation action needed
    if result.violation_detected and result.severity == "critical":
        await youtube.moderate_comment(comment.id, "remove")
```

## Best Practices

### 1. Use Appropriate Polling Interval

```python
# Good - reasonable interval
interval = 60  # 1 minute

# Bad - too frequent (wastes quota)
interval = 10  # 10 seconds
```

### 2. Track Processing State

```python
processed_comments = set()

async def handle_comment(comment):
    # Skip already processed
    if comment.id in processed_comments:
        return
    
    # Process comment
    await analyze_and_moderate(comment)
    processed_comments.add(comment.id)
```

### 3. Monitor Quota

```python
async def with_quota_monitoring():
    youtube = YouTubeAPI.from_env()
    
    while True:
        # Check quota
        status = youtube.get_quota_status()
        
        if status.remaining < 100:
            # Alert on low quota
            await send_alert("YouTube quota warning")
        
        await asyncio.sleep(300)  # Check every 5 minutes
```

### 4. Implement Retry Logic

```python
async def fetch_with_retry(video_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            comments = await youtube.fetch_comments(video_id)
            return comments
        except Exception as e:
            if attempt < max_retries - 1:
                delay = 2 ** attempt
                await asyncio.sleep(delay)
            else:
                raise
```

## Troubleshooting

### Issue: Quota Errors

**Possible causes**:
- Exceeded daily quota
- Too many requests
- Multiple API calls in parallel

**Solution**:
- Reduce polling frequency
- Increase polling interval
- Use batch operations

### Issue: Missing Comments

**Possible causes**:
- Video has no comments
- Comments are disabled
- Video is private
- Video removed

**Solution**:
- Verify video exists and is public
- Check comment settings
- Confirm video has comments

### Issue: Rate Limit Errors

**Possible causes**:
- Polling too frequently
- Multiple tracking instances
- Concurrent API calls

**Solution**:
- Implement proper rate limiting
- Reduce polling frequency
- Ensure single instance

## Related Documentation

- **API Guide**: `./api-guide.md` - API usage
- **Authentication**: `./authentication.md` - Auth setup
- **Rate Limits**: `./rate-limits.md` - Rate limit details
- **Comment Moderation**: `./comment-moderation.md` - Moderation guidelines
- **Data Models**: `./data-models.md` - Data structures

---

**Last Updated**: January 2024
**Status**: Phase 2 - Documentation Complete
