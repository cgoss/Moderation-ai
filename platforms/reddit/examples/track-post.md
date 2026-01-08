---
title: Track Reddit Post Example
category: example
platform: reddit
related:
  - ../api-guide.md
  - ../post-tracking.md
---

# Example: Track Reddit Post

## Overview

This example demonstrates how to track Reddit posts for new comments using polling and monitoring strategies.

## Prerequisites

- Reddit API credentials set up
- Python 3.9+ installed
- Moderation AI library installed

## Setup

### 1. Install Dependencies

```bash
pip install moderation-ai
```

### 2. Set Environment Variables

```bash
# Reddit credentials
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USER_AGENT="python:moderation-ai:1.0 (by /u/your_username)"
export REDDIT_USERNAME="your_username"
export REDDIT_PASSWORD="your_password"
```

Or create `.env` file:

```bash
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=python:moderation-ai:1.0 (by /u/your_username)
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
```

## Example 1: Basic Polling

```python
import asyncio
from moderation_ai.platforms import RedditAPI

async def main():
    reddit = RedditAPI.from_env()
    
    # Post to track
    post_id = "abc123"
    
    # Polling configuration
    interval_seconds = 60  # Check every minute
    poll_duration = 3600  # Run for 1 hour
    
    print(f"Starting polling for post {post_id}")
    print(f"Interval: {interval_seconds} seconds")
    print(f"Duration: {poll_duration} seconds\n")
    
    start_time = asyncio.get_event_loop().time()
    elapsed = 0
    
    while elapsed < poll_duration:
        # Fetch comments
        comments = await reddit.fetch_comments(post_id)
        
        # Process new comments
        if comments:
            print(f"Check at {elapsed}s: {len(comments)} comments")
        
        # Wait for next poll
        await asyncio.sleep(interval_seconds)
        elapsed = asyncio.get_event_loop().time() - start_time
    
    print(f"\nPolling complete after {poll_duration} seconds")

asyncio.run(main())
```

## Example 2: Adaptive Polling

```python
import asyncio
from datetime import datetime
from moderation_ai.platforms import RedditAPI

async def adaptive_polling(post_id, base_interval=60):
    reddit = RedditAPI.from_env()
    
    last_comment_count = 0
    last_activity_time = datetime.now()
    current_interval = base_interval
    
    while True:
        # Fetch comments
        comments = await reddit.fetch_comments(post_id)
        current_count = len(comments)
        
        # Check for new comments
        if current_count > last_comment_count:
            new_comments = comments[last_comment_count:]
            last_activity_time = datetime.now()
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {len(new_comments)} new comments")
            
            for comment in new_comments:
                print(f"@{comment.author_username}: {comment.text[:60]}...")
        
        # Adaptive interval adjustment
        time_since_activity = (datetime.now() - last_activity_time).total_seconds()
        
        if time_since_activity > 300:  # No activity for 5 minutes
            current_interval = min(current_interval * 2, 300)  # Increase, cap at 5 min
        elif time_since_activity < 60:  # Recent activity
            current_interval = max(current_interval / 2, 30)  # Decrease, min at 30s
        
        last_comment_count = current_count
        
        # Wait with current interval
        print(f"Next check in {current_interval}s...")
        await asyncio.sleep(current_interval)

# Start adaptive polling
post_id = "abc123"
asyncio.create_task(adaptive_polling(post_id))

# Keep running
asyncio.run(asyncio.sleep(3600))
```

## Example 3: Multiple Post Tracking

```python
import asyncio
from moderation_ai.platforms import RedditAPI

async def track_multiple_posts(post_ids, interval_seconds=60):
    reddit = RedditAPI.from_env()
    
    # Track each post
    post_data = {}
    for post_id in post_ids:
        post_data[post_id] = {
            "last_count": 0,
            "last_check": datetime.now()
        }
    
    while True:
        for post_id in post_ids:
            # Fetch comments
            comments = await reddit.fetch_comments(post_id)
            current_count = len(comments)
            last_count = post_data[post_id]["last_count"]
            
            # Check for new comments
            if current_count > last_count:
                new_comments = comments[last_count:]
                last_check = post_data[post_id]["last_check"]
                
                print(f"\nPost {post_id}: {len(new_comments)} new comments")
                
                for comment in new_comments:
                    # Analyze and moderate
                    result = analyzer.analyze(comment)
                    
                    if result.violation_detected:
                        await reddit.moderate_comment(comment.id, "remove")
                        print(f"  → Moderated: {result.recommended_action}")
            
            # Update tracking data
            post_data[post_id]["last_count"] = current_count
            post_data[post_id]["last_check"] = datetime.now()
        
        # Wait before next cycle
        await asyncio.sleep(interval_seconds)

# Start tracking multiple posts
post_ids = ["abc123", "def456", "ghi789"]
asyncio.create_task(track_multiple_posts(post_ids))

# Keep running
asyncio.run(asyncio.sleep(3600))
```

## Example 4: Subreddit Feed Monitoring

```python
import asyncio
from moderation_ai.platforms import RedditAPI

async def subreddit_tracker(subreddit_name):
    reddit = RedditAPI.from_env()
    
    tracked_posts = set()
    
    while True:
        # Get new posts
        posts = await reddit.fetch_subreddit_posts(
            subreddit=subreddit_name,
            sort="new",
            limit=10
        )
        
        # Process new posts
        for post in posts:
            if post.id not in tracked_posts:
                print(f"\nNew post: {post.title}")
                print(f"  URL: {post.url}")
                print(f"  Comments: {post.num_comments}")
                
                # Start tracking post for comments
                asyncio.create_task(
                    poll_post_comments(post.id)
                )
                
                tracked_posts.add(post.id)
        
        # Wait before next check
        await asyncio.sleep(60)  # Check every minute

# Start subreddit tracker
subreddit_name = "moderation_ai"
asyncio.create_task(subreddit_tracker(subreddit_name))

# Keep running
asyncio.run(asyncio.sleep(3600))
```

## Example 5: Moderation with Tracking

```python
import asyncio
from moderation_ai.platforms import RedditAPI
from moderation_ai.analysis import AbuseDetector

async def tracked_moderation(post_id):
    reddit = RedditAPI.from_env()
    abuse = AbuseDetector()
    
    # Start tracking
    await reddit.track_post(post_id)
    
    # Polling loop
    processed_comments = set()
    
    while True:
        # Fetch comments
        comments = await reddit.fetch_comments(post_id)
        
        # Analyze and moderate
        for comment in comments:
            # Skip already processed
            if comment.id in processed_comments:
                continue
            
            # Analyze
            result = abuse.analyze(comment)
            
            # Display
            print(f"@{comment.author_username}: {comment.text[:60]}...")
            print(f"  Abuse: {result.is_abuse}")
            
            # Moderate if needed
            if result.is_abuse:
                action = result.recommended_action
                await reddit.moderate_comment(comment.id, action)
                print(f"  → {action}")
            
            # Mark as processed
            processed_comments.add(comment.id)
        
        print(f"Processed {len(comments)} comments\n")
        
        # Wait before next poll
        await asyncio.sleep(60)

# Start tracked moderation
post_id = "abc123"
asyncio.create_task(tracked_moderation(post_id))

# Keep running
asyncio.run(asyncio.sleep(3600))
```

## Example 6: Multi-Subreddit Tracking

```python
import asyncio
from moderation_ai.platforms import RedditAPI

async def multi_subreddit_tracker(subreddits):
    reddit = RedditAPI.from_env()
    
    # Track multiple subreddits
    for subreddit in subreddits:
        asyncio.create_task(
            subreddit_tracker(subreddit)
        )
    
    # Keep running
    await asyncio.sleep(3600)

async def subreddit_tracker(subreddit_name):
    tracked_posts = set()
    
    while True:
        # Get new posts
        posts = await reddit.fetch_subreddit_posts(
            subreddit=subreddit_name,
            sort="new",
            limit=10
        )
        
        # Process new posts
        for post in posts:
            if post.id not in tracked_posts:
                print(f"r/{subreddit_name}: {post.title[:50]}...")
                
                # Start tracking
                asyncio.create_task(
                    poll_post_comments(post.id)
                )
                
                tracked_posts.add(post.id)
        
        # Wait
        await asyncio.sleep(60)

# Start multi-subreddit tracker
subreddits = ["r/moderation_ai", "r/automation", "r/community"]
asyncio.create_task(multi_subreddit_tracker(subreddits))
```

## Example 7: Health Monitoring

```python
import asyncio
from datetime import datetime
from moderation_ai.platforms import RedditAPI

async def monitor_tracking_health(tracked_posts):
    reddit = RedditAPI.from_env()
    
    while True:
        # Check rate limit status
        status = reddit.get_rate_limit_status()
        
        if status.remaining < 10:
            print(f"\n⚠  Warning: Approaching rate limit ({status.remaining} remaining)")
        
        # Check tracking health
        current_time = datetime.now()
        stale_posts = []
        
        for post_id, data in tracked_posts.items():
            last_check = data["last_check"]
            time_since_check = (current_time - last_check).total_seconds()
            
            if time_since_check > 600:  # No check in 10 minutes
                stale_posts.append(post_id)
        
        if stale_posts:
            print(f"\n⚠  Warning: {len(stale_posts)} posts not checked recently")
            for post_id in stale_posts:
                print(f"  {post_id}")
        
        # Wait before next check
        await asyncio.sleep(60)

# Start health monitoring
asyncio.create_task(monitor_tracking_health({}))

# Keep running
asyncio.run(asyncio.sleep(3600))
```

## Running Examples

### Run Basic Polling

```bash
# Save as track_post.py
python track_post.py
```

### Run with Specific Post ID

```python
# Modify example to accept post ID as argument
import sys

post_id = sys.argv[1] if len(sys.argv) > 1 else "abc123"

# Use post_id in script
```

### Run Adaptive Polling

```bash
python track_post.py --adaptive
```

## Error Handling

### Handle Rate Limits

```python
from moderation_ai.utils import RateLimitExceeded

try:
    comments = await reddit.fetch_comments(post_id)
except RateLimitExceeded as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
    await asyncio.sleep(e.retry_after)
```

### Handle Connection Errors

```python
import asyncio

max_retries = 3
for attempt in range(max_retries):
    try:
        comments = await reddit.fetch_comments(post_id)
        break
    except Exception as e:
        if attempt < max_retries - 1:
            print(f"Connection error, retrying...")
            await asyncio.sleep(2 ** attempt)
        else:
            print(f"Failed after {max_retries} attempts")
            raise
```

## Tips

1. **Use Appropriate Polling Intervals**: Balance between real-time and rate limits
2. **Track Processing State**: Avoid duplicate processing
3. **Handle Errors Gracefully**: Implement retry logic and error handling
4. **Monitor Health**: Check rate limits and tracking status
5. **Log Everything**: Maintain detailed logs for debugging

## Related Documentation

- **Post Tracking**: `../post-tracking.md` - Detailed tracking guide
- **API Guide**: `../api-guide.md` - API usage
- **Fetch Comments**: `./fetch-comments.md` - Fetching examples
- **Moderation**: `./moderate-comment.md` - Moderation workflow

---

**Example Version**: 1.0
**Platform**: Reddit
**Status**: Working
