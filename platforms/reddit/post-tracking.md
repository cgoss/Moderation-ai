---
title: Reddit Post Tracking
category: platform
platform: reddit
related:
  - ./README.md
  - ./api-guide.md
  - ../../docs/api-reference/webhooks.md
---

# Reddit Post Tracking

## Overview

Post tracking enables monitoring Reddit posts for new comments and activity. Reddit doesn't have native webhooks for individual posts, so tracking is typically done via polling or monitoring subreddit feeds.

## Tracking Methods

### 1. Polling-Based Tracking (Recommended)

**Use Case**: Monitor specific posts for new comments

**Advantages**:
- Simple to implement
- Works for any post
- No webhooks needed

**Limitations**:
- Not real-time
- Polling interval affects latency
- Wastes rate limits

### 2. Subreddit Feed Monitoring

**Use Case**: Monitor all posts in a subreddit

**Advantages**:
- Real-time feed updates
- Efficient (one feed per subreddit)
- Good for multi-subreddit monitoring

**Limitations**:
- Monitors entire subreddit
- May not get instant notifications
- Requires feed parsing

### 3. Modmail (Moderators Only)

**Use Case**: Receive mod reports and messages

**Advantages**:
- Real-time notifications
- Built-in to Reddit
- No polling needed

**Limitations**:
- Only for moderators
- Limited to modmail events
- Requires mod permissions

## Polling-Based Tracking

### Basic Polling

```python
import asyncio
from moderation_ai.platforms import RedditAPI

async def poll_post_comments(post_id, interval_seconds=60):
    reddit = RedditAPI.from_env()
    last_comment_count = 0
    
    while True:
        # Fetch current comments
        comments = await reddit.fetch_comments(post_id)
        current_count = len(comments)
        
        # Check for new comments
        if current_count > last_comment_count:
            new_comments = comments[last_comment_count:]
            
            for comment in new_comments:
                # Analyze comment
                result = analyzer.analyze(comment)
                
                # Moderate if needed
                if result.violation_detected:
                    await reddit.moderate_comment(comment.id, "remove")
            
            print(f"Processed {len(new_comments)} new comments")
        
        last_comment_count = current_count
        
        # Wait before next poll
        await asyncio.sleep(interval_seconds)

# Start polling
asyncio.create_task(poll_post_comments("abc123"))

# Keep running
asyncio.run(asyncio.sleep(3600))  # Run for 1 hour
```

### Poll Multiple Posts

```python
async def poll_multiple_posts(post_ids, interval_seconds=60):
    reddit = RedditAPI.from_env()
    post_data = {}
    
    # Initialize post data
    for post_id in post_ids:
        post_data[post_id] = {"last_count": 0}
    
    while True:
        for post_id in post_ids:
            # Fetch comments
            comments = await reddit.fetch_comments(post_id)
            current_count = len(comments)
            last_count = post_data[post_id]["last_count"]
            
            # Process new comments
            if current_count > last_count:
                new_comments = comments[last_count:]
                
                for comment in new_comments:
                    result = analyzer.analyze(comment)
                    
                    if result.violation_detected:
                        await reddit.moderate_comment(comment.id, "remove")
            
            # Update count
            post_data[post_id]["last_count"] = current_count
        
        # Wait before next poll
        await asyncio.sleep(interval_seconds)

# Start polling multiple posts
post_ids = ["abc123", "def456", "ghi789"]
asyncio.create_task(poll_multiple_posts(post_ids))
```

## Subreddit Feed Monitoring

### Monitor New Posts

```python
async def monitor_subreddit_feed(subreddit_name, limit=100):
    reddit = RedditAPI.from_env()
    
    # Get new posts
    posts = await reddit.fetch_subreddit_posts(
        subreddit=subreddit_name,
        sort="new",
        limit=limit
    )
    
    for post in posts:
        print(f"New post: {post.title}")
        
        # Track post for comments
        await reddit.track_post(post.id)
```

### Monitor with Automatic Tracking

```python
async def subreddit_tracker(subreddit_name):
    reddit = RedditAPI.from_env()
    
    # Track new posts
    tracked_posts = set()
    
    while True:
        # Fetch new posts
        posts = await reddit.fetch_subreddit_posts(
            subreddit=subreddit_name,
            sort="new",
            limit=10
        )
        
        # Process new posts
        for post in posts:
            if post.id not in tracked_posts:
                print(f"New post: {post.title}")
                
                # Start tracking post
                asyncio.create_task(poll_post_comments(post.id))
                
                tracked_posts.add(post.id)
        
        # Wait before next check
        await asyncio.sleep(60)  # Check every minute
```

## Modmail Monitoring

### Monitor Modmail

```python
async def monitor_modmail():
    reddit = RedditAPI.from_env()
    
    while True:
        # Fetch modmail messages
        messages = await reddit.fetch_modmail()
        
        for message in messages:
            print(f"Modmail from {message.author}")
            print(f"Subject: {message.subject}")
            print(f"Body: {message.body[:100]}...")
            
            # Handle reports
            if message.subject.lower().startswith("report"):
                # Process user report
                await handle_report(message)
        
        # Wait before next check
        await asyncio.sleep(300)  # Check every 5 minutes
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
        await reddit.moderate_comment(comment.id, action)
        
        logger.info(f"Moderated comment: {action}")
```

### Handle User Report

```python
async def handle_report(modmail_message):
    # Extract reported content
    report_data = parse_modmail_report(modmail_message)
    
    # Analyze reported content
    result = analyzer.analyze_text(report_data["content"])
    
    # Take action based on severity
    if result.violation_detected:
        severity = result.severity
        
        if severity == "critical":
            # Immediate action
            await reddit.remove_comment(report_data["comment_id"])
            await reddit.ban_user(report_data["user_id"])
        else:
            # Flag for review
            await reddit.flag_for_review(report_data["comment_id"])
```

## Best Practices

### 1. Use Appropriate Polling Interval

```python
# Good - reasonable interval
interval = 60  # 1 minute

# Bad - too frequent (wastes rate limits)
interval = 5  # 5 seconds
```

### 2. Batch Process Comments

```python
# Good - batch process
comments = await reddit.fetch_comments(post_id)
results = analyzer.batch_analyze(comments)

# Process batch
for comment, result in zip(comments, results):
    if result.violation_detected:
        await reddit.moderate_comment(comment.id, result.recommended_action)
```

### 3. Implement Caching

```python
from functools import lru_cache

# Good - cache post data
@lru_cache(maxsize=100)
async def get_post_info(post_id):
    return await reddit.fetch_post(post_id)
```

### 4. Track Processing State

```python
processed_comments = set()

async def handle_comment(comment):
    # Skip already processed
    if comment.id in processed_comments:
        return
    
    # Process comment
    await analyze_and_moderate(comment)
    
    # Mark as processed
    processed_comments.add(comment.id)
```

### 5. Monitor Tracking Health

```python
async def monitor_tracking_health():
    reddit = RedditAPI.from_env()
    
    while True:
        # Check rate limit status
        status = reddit.get_rate_limit_status()
        
        if not status.is_healthy:
            logger.warning(f"Rate limit unhealthy: {status.message}")
        
        # Check tracking status
        for post_id in tracked_posts:
            last_check = tracking_status.get(post_id, {}).get("last_check")
            if last_check and (datetime.now() - last_check).total_seconds() > 300:
                logger.warning(f"Post {post_id} not checked in 5 minutes")
        
        await asyncio.sleep(60)  # Check every minute
```

## Advanced Tracking

### Adaptive Polling

```python
async def adaptive_polling(post_id, base_interval=60):
    reddit = RedditAPI.from_env()
    last_activity = datetime.now()
    activity_count = 0
    
    while True:
        # Fetch comments
        comments = await reddit.fetch_comments(post_id)
        
        # Check for activity
        if len(comments) > activity_count:
            # New activity, reduce polling interval
            activity_count = len(comments)
            interval = base_interval / 2
        else:
            # No activity, increase polling interval
            interval = base_interval * 2
        
        # Clamp interval
        interval = max(interval, 30)  # Minimum 30 seconds
        interval = min(interval, 300)  # Maximum 5 minutes
        
        await asyncio.sleep(interval)
```

### Multi-Subreddit Tracking

```python
async def multi_subreddit_tracker(subreddits):
    reddit = RedditAPI.from_env()
    
    # Track multiple subreddits
    for subreddit in subreddits:
        asyncio.create_task(
            subreddit_tracker(subreddit)
        )
    
    # Keep running
    await asyncio.sleep(3600)
```

## Troubleshooting

### Issue: Polling Too Slow

**Possible causes**:
- Polling interval too long
- Network latency
- Rate limiting

**Solution**:
- Reduce polling interval
- Implement caching
- Check network connection
- Monitor rate limits

### Issue: Rate Limit Exceeded

**Possible causes**:
- Polling too frequently
- Multiple posts being tracked
- Other API calls in progress

**Solution**:
- Implement proper rate limiting
- Increase polling interval
- Batch operations
- Use efficient API calls

### Issue: Missing Comments

**Possible causes**:
- Post deleted or removed
- Private subreddit
- Comment tree depth issues

**Solution**:
- Verify post exists
- Check subreddit permissions
- Handle nested comments properly
- Account for removed content

### Issue: Duplicate Event Processing

**Possible causes**:
- Multiple poll instances
- State not being tracked
- Restart after crash

**Solution**:
- Track processed event IDs
- Implement idempotent handlers
- Persist state to disk
- Handle restarts gracefully

## Related Documentation

- **API Guide**: `./api-guide.md` - API usage
- **Authentication**: `./authentication.md` - Auth setup
- **Rate Limits**: `./rate-limits.md` - Rate limit details
- **Comment Moderation**: `./comment-moderation.md` - Moderation guidelines

---

**Last Updated**: January 2024
**Status**: Phase 2 - Documentation Complete
