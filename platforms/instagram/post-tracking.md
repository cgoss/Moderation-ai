---
title: Instagram Post Tracking
category: platform
platform: instagram
related:
  - ../README.md
  - ./api-guide.md
  - ./authentication.md
  - ./comment-moderation.md
---

# Instagram Post Tracking

## Overview

Post tracking in Instagram enables monitoring of specific media posts for new comments and engagement updates. This document covers how to set up and use post tracking for proactive comment moderation.

## Tracking Capabilities

| Feature | Status | Notes |
|----------|--------|-------|
| **Track New Comments** | ✅ Supported | Detect new comments on tracked posts |
| **Engagement Monitoring** | ✅ Supported | Monitor likes, comment count changes |
| **Polling-Based** | ✅ Primary Method | Check for updates (no native webhooks) |
| **Batch Tracking** | ✅ Supported | Track multiple posts efficiently |
| **Real-Time Alerts** | ⚠️ Limited | Polling required (no comment webhooks) |

## Tracking Methods

### 1. Single Post Tracking

Monitor a single media post for new comments:

```python
import asyncio
from datetime import datetime, timedelta
from moderation_ai.platforms import InstagramAPI
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

async def track_single_post(media_id: str):
    """
    Track a single Instagram post for new comments.
    """
    # Initialize
    instagram = InstagramAPI.from_env()
    standards = StandardsEngine(auto_moderate=True)
    abuse_detector = AbuseDetector(strict_mode=True)
    
    # Tracking configuration
    polling_interval = 60  # Check every 60 seconds
    max_comments = 1000  # Track last 100 comments
    tracked_comments = set()
    
    print(f"Starting to track post {media_id}")
    
    try:
        while True:
            # Fetch recent comments
            comments = await instagram.fetch_comments(
                media_id,
                limit=max_comments
            )
            
            # Get comment IDs
            current_comment_ids = {c.id for c in comments}
            
            # Find new comments
            new_comments = current_comment_ids - tracked_comments
            
            if new_comments:
                timestamp = datetime.utcnow().isoformat()
                print(f"\n[{timestamp}] Found {len(new_comments)} new comments")
                
                # Process new comments
                for comment_id in new_comments:
                    # Find full comment object
                    comment = next((c for c in comments if c.id == comment_id), None)
                    
                    if comment:
                        # Quick abuse check
                        abuse_result = abuse_detector.analyze(comment)
                        
                        # Apply moderation if severe abuse
                        if abuse_result.data.get('is_abusive'):
                            severity = abuse_result.data.get('severity')
                            print(f"  -> Severe abuse detected: {severity}")
                            
                            if severity in ['high', 'critical']:
                                try:
                                    await instagram.moderate_comment(comment_id, "hide")
                                    print(f"  -> Hidden comment {comment_id}")
                                except Exception as e:
                                    print(f"  -> Failed to hide: {e}")
                        else:
                            # Standard moderation
                            decision = standards.validate(comment.text)
                            
                            if decision.action != "approve":
                                print(f"  -> Action: {decision.action}")
                                print(f"  -> Reason: {decision.reasoning[:100]}...")
                
                # Update tracked comments
                tracked_comments = current_comment_ids
            
            # Wait before next poll
            await asyncio.sleep(polling_interval)
    
    except KeyboardInterrupt:
        print("\n\nTracking stopped by user")
    except Exception as e:
        print(f"\nError during tracking: {e}")
```

### 2. Batch Post Tracking

Track multiple posts in parallel:

```python
import asyncio
from moderation_ai.platforms import InstagramAPI
from moderation_ai.core import StandardsEngine

async def track_multiple_posts(media_ids: list[str]):
    """
    Track multiple Instagram posts in parallel.
    """
    instagram = InstagramAPI.from_env()
    standards = StandardsEngine()
    
    print(f"Tracking {len(media_ids)} posts")
    
    # Create tracking tasks
    tasks = [track_single_post(media_id) for media_id in media_ids]
    
    # Run in parallel
    await asyncio.gather(*tasks)
```

### 3. Engagement-Triggered Tracking

Track posts when engagement reaches certain thresholds:

```python
from moderation_ai.platforms import InstagramAPI

async def track_engagement_threshold(media_id: str, engagement_threshold: int = 50):
    """
    Track post when it reaches engagement threshold.
    """
    instagram = InstagramAPI.from_env()
    
    # Initial check
    media = await instagram.get_media(media_id)
    print(f"Initial engagement: {media.like_count} likes")
    
    if media.like_count < engagement_threshold:
        print(f"Waiting for {engagement_threshold} likes...")
        await asyncio.sleep(300)  # 5 minutes
    else:
        print(f"Engagement threshold reached!")
        # Start tracking
        await track_single_post(media_id)
```

## Configuration

### Tracking Parameters

| Parameter | Description | Default |
|-----------|-------------|----------|
| **polling_interval** | Polling frequency in seconds | 60 |
| **max_comments** | Maximum comments to fetch | 1000 |
| **enable_abuse_detection** | Enable automatic abuse detection | True |
| **auto_moderate_threshold** | Moderation score threshold | 0.7 |
| **engagement_threshold** | Engagement level to trigger tracking | 50 likes |

### Data Model

```python
{
    "media_id": "123456789_4567890",
    "tracking_config": {
        "polling_interval": 60,
        "max_comments": 1000,
        "enabled": true,
        "auto_moderate": true
    },
    "tracking_stats": {
        "started_at": "2024-01-08T10:00:00Z",
        "last_check": "2024-01-08T10:30:00Z",
        "new_comments_detected": 0,
        "total_comments_processed": 0,
        "engagement_events": []
    }
}
```

### Tracking States

```python
from enum import Enum

class TrackingStatus(str, Enum):
    """
    Possible tracking states.
    """
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
```

## Best Practices

### 1. Respect Rate Limits

```python
import asyncio

async def track_with_rate_limiting(media_id: str):
    """
    Track post while respecting rate limits.
    """
    instagram = InstagramAPI.from_env()
    
    # Calculate sleep time based on rate limit
    request_interval = 3600 / 200  # 18 seconds per request
    
    while True:
        # Fetch comments
        comments = await instagram.fetch_comments(media_id, limit=50)
        
        # Process comments
        for comment in comments:
            decision = standards.validate(comment.text)
        
        # Wait before next request
        await asyncio.sleep(request_interval)
```

### 2. Error Recovery

```python
async def resilient_tracking(media_id: str):
    """
    Track post with error recovery.
    """
    instagram = InstagramAPI.from_env()
    
    max_retries = 3
    base_delay = 10
    
    for attempt in range(max_retries):
        try:
            return await track_single_post(media_id)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = base_delay * (2 ** attempt)
            print(f"Retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)
```

### 3. Prioritize Critical Posts

```python
from collections import deque

class PriorityTracker:
    """
    Track and prioritize high-value posts.
    """
    
    def __init__(self):
        self.queue = deque()
        self.high_priority_threshold = 1000  # likes
    
    def add_post(self, media_id: str, priority: int = None):
        """
        Add post to tracking queue.
        """
        priority = priority if priority else self.calculate_priority(media_id)
        
        self.queue.append((priority, media_id))
    
    async def get_next_post(self):
        """
        Get next post from queue.
        """
        if not self.queue:
            return None
        
        # Sort by priority
        self.queue = sorted(self.queue, key=lambda x: x[0], reverse=True)
        
        priority, media_id = self.queue[0]
        return media_id
    
    def calculate_priority(self, media_id: str) -> int:
        """
        Calculate priority based on engagement.
        """
        # Fetch media to get engagement metrics
        media = await instagram.get_media(media_id)
        
        # Calculate priority score
        score = media.like_count * 10 + media.comments_count * 5
        
        return min(score, 1000)
```

### 4. Comment Deduplication

```python
async def track_with_deduplication(media_id: str):
    """
    Track post while avoiding duplicate comment processing.
    """
    instagram = InstagramAPI.from_env()
    seen_comment_ids = set()
    
    # Fetch comments in batches
    batch_size = 50
    after_cursor = None
    
    while True:
        comments = await instagram.fetch_comments(
            media_id,
            limit=batch_size,
            after=after_cursor
        )
        
        if not comments:
            break
        
        # Process only unseen comments
        for comment in comments:
            if comment.id not in seen_comment_ids:
                # Process comment
                print(f"Processing comment {comment.id}")
                
                # Mark as seen
                seen_comment_ids.add(comment.id)
                
                # Wait to respect rate limits
                await asyncio.sleep(1)  # 1 second per comment
        
        # Update cursor
        if comments:
            after_cursor = comments[-1].id
```

## Webhooks Integration

Instagram doesn't provide real-time comment webhooks. Use polling with:

```python
# External webhook service integration
import fastapi
from fastapi import FastAPI
from moderation_ai.platforms import InstagramAPI

app = FastAPI()
instagram = InstagramAPI.from_env()

@app.post("/webhooks/instagram/comment-created")
async def comment_webhook(event: dict):
    """
    Simulate Instagram webhook for new comments.
    """
    # Trigger tracking when comment is received
    media_id = event.get("media_id")
    
    # Fetch comments
    comments = await instagram.fetch_comments(media_id, limit=50)
    
    # Process new comments
    new_comment_count = sum(1 for c in comments if not c.get("seen"))
    
    if new_comment_count > 0:
        print(f"New comments detected: {new_comment_count}")
        # Trigger moderation
        await process_new_comments(comments)
```

## Metrics and Analytics

### Key Performance Metrics

| Metric | Description | Calculation |
|--------|-------------|------------|
| **Comment Response Time** | Time to moderate new comment | Average of moderation actions |
| **False Positive Rate** | Comments incorrectly hidden/approved | % of total |
| **Spam Detection Rate** | Spam comments removed / % of total |
| **Abuse Detection Rate** | Abuse comments hidden / % of total |
| **Tracking Accuracy** | New comments detected / % of actual |
| **Resource Efficiency** | API calls per comment | Total API usage |

### Example: Collecting Metrics

```python
class TrackingMetrics:
    """
    Collect and report tracking metrics.
    """
    
    def __init__(self):
        self.total_posts_tracked = 0
        self.total_comments_processed = 0
        self.violations_detected = 0
        self.auto_moderations = 0
        self.manual_reviews = 0
        self.false_positives = 0
        self.response_times = []
    
    def record_post_tracked(self):
        """
        Record a post being tracked.
        """
        self.total_posts_tracked += 1
    
    def record_comment_processed(self, response_time: float):
        """
        Record comment processing time.
        """
        self.total_comments_processed += 1
        self.response_times.append(response_time)
    
    def record_violation_detected(self):
        """
        Record a violation was detected.
        """
        self.violations_detected += 1
    
    def get_summary_report(self) -> dict:
        """
        Generate tracking summary report.
        """
        return {
            'total_posts_tracked': self.total_posts_tracked,
            'total_comments_processed': self.total_comments_processed,
            'violations_detected': self.violations_detected,
            'auto_moderations': self.auto_moderations,
            'manual_reviews': self.manual_reviews,
            'false_positives': self.false_positives,
            'avg_response_time': sum(self.response_times) / len(self.response_times) if self.response_times else 0,
            'tracking_uptime': self._calculate_uptime()
        }
    
    def _calculate_uptime(self) -> float:
        """
        Calculate tracking service uptime.
        """
        # Implement your uptime calculation
        return 99.5
```

## Platform-Specific Features

### Instagram Stories

Stories are ephemeral (24 hours). Special tracking considerations:

```python
async def track_story(story_id: str):
    """
    Track an Instagram story for comments.
    """
    instagram = InstagramAPI.from_env()
    
    # Stories expire in 24 hours
    story_age_threshold = timedelta(hours=23)
    
    # Check if story is still active
    try:
        story = await instagram.get_media(story_id)
        
        if not story:
            print(f"Story {story_id} no longer available")
            return
        
        story_timestamp = datetime.fromisoformat(story.timestamp)
        story_age = datetime.utcnow() - story_timestamp
        
        if story_age > story_age_threshold:
            print(f"Story {story_id} expired, stopping tracking")
            return
        
        # Track comments only if story is recent
        comments = await instagram.fetch_comments(
            story_id,
            content_type="story"
        )
        
        for comment in comments:
            # Process comment
            decision = standards.validate(comment.text)
            
            if decision.action != "approve":
                await instagram.moderate_comment(comment.id, "hide")
    
    except Exception as e:
        print(f"Error tracking story {story_id}: {e}")
```

### Instagram Reels

Reels are short-form videos (60 seconds or less). High comment volume considerations:

```python
async def track_reel(reel_id: str):
    """
    Track an Instagram reel for comments.
    """
    instagram = InstagramAPI.from_env()
    
    # Reels often have high comment density
    # Use adaptive polling
    comments_per_fetch = 100  # Higher volume for reels
    
    try:
        comments = await instagram.fetch_comments(
            reel_id,
            content_type="reel"
        )
        
        # Fast processing due to high volume
        await process_comments_batch(comments, batch_size=50)
        
    except Exception as e:
        print(f"Error tracking reel {reel_id}: {e}")
```

## Troubleshooting

### Issue: No New Comments Detected

**Symptom**: Tracking post but no new comments appearing

**Solutions**:
1. Verify post is public (not private)
2. Check if comments are disabled on post
3. Verify post creation date (not too old)
4. Check if you're hitting rate limits

### Issue: Slow Comment Processing

**Symptom**: Taking too long to process comments

**Solutions**:
1. Optimize API call batching
2. Use efficient filtering
3. Implement parallel processing
4. Monitor system performance

### Issue: Tracking Not Persisting

**Symptom**: Tracked state lost between restarts

**Solutions**:
1. Use persistent storage for tracking state
2. Implement checkpoint/resume functionality
3. Store tracking state in database
4. Implement state recovery procedures

## Related Documentation

- **API Guide**: `./api-guide.md` - API usage
- **Authentication**: `./authentication.md` - Auth setup
- **Rate Limits**: `./rate-limits.md` - Rate limit handling
- **Comment Moderation**: `./comment-moderation.md` - Moderation guidelines
- **Data Models**: `./data-models.md` - Data structures
- **Examples**: `../examples/track-post.md` - Tracking examples
- **Platform Overview**: `../README.md` - Platform capabilities

## Platform Status

| Status | Value |
|---------|-------|
| **Last Updated** | January 2024 |
| **API Version** | v18.0+ |
| **Documentation Version** | 1.0 |
| **Implementation Status** | Phase 4 - In Progress |

---

**Platform**: Instagram
**Documentation Version**: 1.0
**Status**: Phase 4 - Documentation In Progress
