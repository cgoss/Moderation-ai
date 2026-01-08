---
title: Track YouTube Post Example
category: example
platform: youtube
related:
  - ../api-guide.md
  - ../post-tracking.md
---

# Example: Track YouTube Post

## Overview

This example demonstrates how to track a YouTube video for new comments using polling-based tracking.

## Prerequisites

- YouTube API credentials set up
- Python 3.9+ installed
- Moderation AI library installed

## Setup

### 1. Install Dependencies

```bash
pip install moderation-ai
```

### 2. Set Environment Variables

```bash
export YOUTUBE_API_KEY=your_api_key
```

Or create `.env` file:

```bash
YOUTUBE_API_KEY=your_api_key
```

## Example 1: Basic Polling

```python
import asyncio
from moderation_ai.platforms import YouTubeAPI

async def main():
    youtube = YouTubeAPI.from_env()
    
    video_id = "abc123"
    
    # Poll for new comments
    interval = 60  # Check every minute
    
    last_comment_count = 0
    
    while True:
        # Fetch comments
        comments = await youtube.fetch_comments(video_id)
        current_count = len(comments)
        
        # Check for new comments
        if current_count > last_comment_count:
            new_comments = comments[last_comment_count:]
            
            for comment in new_comments:
                print(f"\nNew comment from @{comment.author_display_name}:")
                print(f"  {comment.text[:100]}...")
                
                # Analyze comment
                from moderation_ai.analysis import AbuseDetector
                abuse = AbuseDetector()
                result = abuse.analyze(comment)
                
                if result.is_abuse:
                    print(f"  → Abuse detected: {result.abuse_type}")
                else:
                    print(f"  → Comment approved")
        
        last_comment_count = current_count
        
        # Wait before next poll
        await asyncio.sleep(interval)

asyncio.run(main())
```

## Example 2: Adaptive Polling

```python
import asyncio
from datetime import datetime
from moderation_ai.platforms import YouTubeAPI

async def adaptive_polling(video_id, base_interval=60):
    youtube = YouTubeAPI.from_env()
    
    last_comment_count = 0
    last_activity_time = datetime.now()
    
    while True:
        # Fetch comments
        comments = await youtube.fetch_comments(video_id)
        current_count = len(comments)
        
        # Check for new activity
        if current_count > last_comment_count:
            last_activity_time = datetime.now()
            new_comments = comments[last_comment_count:]
            
            for comment in new_comments:
                print(f"\n[{last_activity_time.strftime('%H:%M:%S')}] New comment from @{comment.author_display_name}")
                print(f"  {comment.text[:100]}...")
            
            # Adjust interval based on activity
            time_since_activity = (datetime.now() - last_activity_time).total_seconds()
            
            if time_since_activity < 60:
                # Recent activity, increase polling
                interval = base_interval / 2
            elif time_since_activity < 300:
                # Normal activity
                interval = base_interval
            else:
                # No activity, decrease polling
                interval = min(base_interval * 2, 300)  # Max 5 minutes
        
        last_comment_count = current_count
        print(f"\nNext check in {interval} seconds...")
        await asyncio.sleep(interval)

asyncio.run(adaptive_polling("abc123"))
```

## Example 3: Multi-Video Tracking

```python
import asyncio
from moderation_ai.platforms import YouTubeAPI

async def track_multiple_videos(video_ids):
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
                
                print(f"\n[{video_id}] {len(new_comments)} new comments:")
                
                for comment in new_comments:
                    print(f"@{comment.author_display_name}: {comment.text[:50]}...")
            
            # Update count
            video_data[video_id]["last_count"] = current_count
        
        # Wait before next check
        await asyncio.sleep(60)  # Check every minute

asyncio.run(track_multiple_videos(["abc123", "def456", "ghi789"]))
```

## Example 4: With Moderation

```python
import asyncio
from moderation_ai.platforms import YouTubeAPI
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

async def track_with_moderation(video_id):
    youtube = YouTubeAPI.from_env()
    standards = StandardsEngine()
    abuse = AbuseDetector()
    
    last_comment_count = 0
    
    while True:
        # Fetch comments
        comments = await youtube.fetch_comments(video_id)
        current_count = len(comments)
        
        # Check for new comments
        if current_count > last_comment_count:
            new_comments = comments[last_comment_count:]
            
            for comment in new_comments:
                # Analyze for abuse
                abuse_result = abuse.analyze(comment)
                decision = standards.validate(comment.text)
                
                print(f"@{comment.author_display_name}: {comment.text[:50]}...")
                
                # Apply moderation
                if abuse_result.is_abuse:
                    action = abuse_result.recommended_action
                    await youtube.moderate_comment(comment.id, action)
                    print(f"  → Moderated: {action} (abuse: {abuse_result.abuse_type})")
                elif decision.action != "approve":
                    action = decision.action
                    print(f"  → Moderated: {action} (reason: {decision.standard})")
                else:
                    print("  → Approved")
        
        last_comment_count = current_count
        
        # Wait before next poll
        await asyncio.sleep(60)

asyncio.run(track_with_moderation("abc123"))
```

## Example 5: Comment Analysis

```python
import asyncio
from moderation_ai.platforms import YouTubeAPI
from moderation_ai.analysis import SentimentAnalyzer

async def analyze_video_sentiment(video_id):
    youtube = YouTubeAPI.from_env()
    analyzer = SentimentAnalyzer()
    
    # Fetch comments
    comments = await youtube.fetch_comments(video_id)
    
    # Batch analyze sentiment
    results = analyzer.batch_analyze(comments)
    
    # Calculate sentiment breakdown
    positive = sum(1 for r in results if r.sentiment == "positive")
    negative = sum(1 for r in results if r.sentiment == "negative")
    neutral = sum(1 for r in results if r.sentiment == "neutral")
    
    print(f"Video: {video_id}")
    print(f"Total comments: {len(comments)}")
    print(f"Positive: {positive} ({positive/len(comments)*100:.1f}%)")
    print(f"Negative: {negative} ({negative/len(comments)*100:.1f}%)")
    print(f"Neutral: {neutral} ({neutral/len(comments)*100:.1f}%)")

asyncio.run(analyze_video_sentiment("abc123"))
```

## Example 6: Health Monitoring

```python
import asyncio
from datetime import datetime
from moderation_ai.platforms import YouTubeAPI

async def monitor_tracking_health(video_id):
    youtube = YouTubeAPI.from_env()
    
    last_check_time = datetime.now()
    comment_count = 0
    
    while True:
        # Fetch comments
        comments = await youtube.fetch_comments(video_id)
        current_count = len(comments)
        
        # Check health
        current_time = datetime.now()
        time_since_check = (current_time - last_check_time).total_seconds()
        
        # Alert if no activity
        if time_since_check > 600:  # 10 minutes without check
            print(f"Warning: No activity for {time_since_check} seconds")
        
        # Update check time
        last_check_time = current_time
        comment_count = current_count
        
        # Wait before next check
        await asyncio.sleep(60)  # Check every minute

asyncio.run(monitor_tracking_health("abc123"))
```

## Running Examples

### Run Basic Example

```bash
# Save as track_post.py
python track_post.py
```

### Run with Specific Video ID

```python
# Modify example to accept video ID as argument
import sys

video_id = sys.argv[1] if len(sys.argv) > 1 else "abc123"

# Use video_id in script
```

### Run with Moderation

```bash
# Run with moderation
python track_post.py --moderate
```

## Error Handling

### Rate Limit Error

```python
from moderation_ai.utils import RateLimitExceeded

try:
    comments = await youtube.fetch_comments(video_id)
except RateLimitExceeded as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
    await asyncio.sleep(e.retry_after)
    comments = await youtube.fetch_comments(video_id)
```

### Authentication Error

```python
from moderation_ai.utils import AuthenticationError

try:
    await youtube.authenticate()
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print("Please verify your API key")
```

### Video Not Found

```python
from moderation_ai.utils import PostNotFoundError

try:
    video = await youtube.fetch_video(video_id)
except PostNotFoundError:
    print(f"Video {video_id} not found")
```

## Tips

1. **Use appropriate polling interval**
   - Too frequent: Wastes quota
   - Too infrequent: High latency

2. **Implement adaptive polling**
   - Adjust based on activity
   - Reduce during inactive periods

3. **Cache video metadata**
   - Don't refetch video info

4. **Monitor quota usage**
   - Check remaining quota regularly
   - Alert when approaching limits

5. **Handle edge cases**
   - Videos with no comments
   - Private videos
   - Disabled comments

## Related Documentation

- **API Guide**: `../api-guide.md` - API usage
- **Data Models**: `../data-models.md` - Data structures
- **Fetch Comments**: `./fetch-comments.md` - Fetching examples
- **Moderation**: `./moderate-comment.md` - Moderation workflow

---

**Example Version**: 1.0
**Platform**: YouTube
**Status**: Working
