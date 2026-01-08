---
title: Track Twitter Post Example
category: example
platform: twitter
related:
  - ../api-guide.md
  - ../post-tracking.md
---

# Example: Track Twitter Post

## Overview

This example demonstrates how to track a Twitter tweet for new comments (replies) using webhooks and real-time streaming.

## Prerequisites

- Twitter API credentials with webhook permissions
- Webhook server (publicly accessible)
- Python 3.9+ installed
- Moderation AI library installed

## Setup

### 1. Install Dependencies

```bash
pip install moderation-ai fastapi uvicorn
```

### 2. Set Environment Variables

```bash
# Twitter credentials
export TWITTER_API_KEY="your_api_key"
export TWITTER_API_SECRET="your_api_secret"
export TWITTER_ACCESS_TOKEN="your_access_token"
export TWITTER_ACCESS_TOKEN_SECRET="your_access_token_secret"

# Webhook secret (for signature verification)
export TWITTER_WEBHOOK_SECRET="your_webhook_secret"

# Webhook URL
export WEBHOOK_URL="https://your-domain.com/webhooks/twitter"
```

### 3. Create Webhook Server

## Example 1: Basic Webhook Server

```python
from fastapi import FastAPI, Request, HTTPException
from moderation_ai.platforms import TwitterAPI
from moderation_ai.utils import WebhookHandler
import os

app = FastAPI()

# Initialize Twitter API
twitter = TwitterAPI.from_env()

# Initialize webhook handler
handler = WebhookHandler(
    secret=os.getenv("TWITTER_WEBHOOK_SECRET")
)

@app.post("/webhooks/twitter")
async def twitter_webhook(request: Request):
    # Get payload
    payload = await request.body()
    
    # Verify signature
    signature = request.headers.get("x-twitter-webhooks-signature")
    if not handler.verify_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse event
    event = handler.parse_event(payload, platform="twitter")
    
    # Handle event
    await handle_twitter_event(event)
    
    return {"status": "ok"}

async def handle_twitter_event(event):
    if event.event_type == "comment.created":
        await handle_comment_created(event.data)
    elif event.event_type == "comment.updated":
        await handle_comment_updated(event.data)

async def handle_comment_created(data):
    comment = data.comment
    print(f"New reply from @{comment.author_username}: {comment.text}")
    
    # Analyze comment
    from moderation_ai.analysis import AbuseDetector
    abuse = AbuseDetector()
    result = abuse.analyze(comment)
    
    if result.is_abuse:
        print(f"Abuse detected: {result.abuse_type}")
        await twitter.moderate_comment(comment.id, "hide")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

## Example 2: Track Multiple Tweets

```python
import asyncio
from moderation_ai.platforms import TwitterAPI

async def track_multiple_tweets():
    twitter = TwitterAPI.from_env()
    
    # List of tweet IDs to track
    tweet_ids = [
        "1234567890",
        "0987654321",
        "5432109876"
    ]
    
    # Track each tweet
    for tweet_id in tweet_ids:
        try:
            await twitter.track_post(tweet_id)
            print(f"Tracking tweet: {tweet_id}")
        except Exception as e:
            print(f"Failed to track {tweet_id}: {e}")
    
    print(f"Tracking {len(tweet_ids)} tweets")

asyncio.run(track_multiple_tweets())
```

## Example 3: Real-Time Streaming

```python
import asyncio
from moderation_ai.platforms import TwitterAPI
from moderation_ai.analysis import AbuseDetector

async def stream_tweet_replies():
    twitter = TwitterAPI.from_env()
    abuse = AbuseDetector()
    
    # Tweet to track
    tweet_id = "1234567890"
    
    # Create stream
    print(f"Creating stream for tweet {tweet_id}...")
    stream = await twitter.create_stream(reply_to=tweet_id)
    
    # Process replies in real-time
    print("Streaming replies...")
    async for reply in stream:
        print(f"\nNew reply from @{reply.author_username}: {reply.text}")
        
        # Analyze for abuse
        result = abuse.analyze(reply)
        
        if result.is_abuse:
            print(f"Abuse detected: {result.abuse_type}")
            print(f"Severity: {result.severity}")
            print(f"Confidence: {result.confidence:.2f}")
            
            # Auto-moderate
            action = result.recommended_action
            await twitter.moderate_comment(reply.id, action)
            print(f"→ Action taken: {action}")

asyncio.run(stream_tweet_replies())
```

## Example 4: Polling-Based Tracking

```python
import asyncio
from datetime import datetime, timedelta
from moderation_ai.platforms import TwitterAPI
from moderation_ai.analysis import AbuseDetector

async def poll_for_replies(tweet_id, interval_seconds=60):
    twitter = TwitterAPI.from_env()
    abuse = AbuseDetector()
    
    # Track last comment count
    last_comment_count = 0
    
    while True:
        # Fetch current replies
        comments = await twitter.fetch_comments(tweet_id)
        current_count = len(comments)
        
        # Check for new comments
        if current_count > last_comment_count:
            new_comments = comments[last_comment_count:]
            
            print(f"\n{len(new_comments)} new replies:")
            
            for comment in new_comments:
                print(f"@{comment.author_username}: {comment.text}")
                print(f"  Posted: {comment.created_at}")
                
                # Analyze
                result = abuse.analyze(comment)
                
                if result.is_abuse:
                    action = result.recommended_action
                    await twitter.moderate_comment(comment.id, action)
                    print(f"  → Moderated: {action}")
        
        last_comment_count = current_count
        
        # Wait before next poll
        await asyncio.sleep(interval_seconds)

# Start polling
tweet_id = "1234567890"
asyncio.create_task(poll_for_replies(tweet_id))

# Keep running
asyncio.run(asyncio.sleep(3600))  # Run for 1 hour
```

## Example 5: Combined Webhook + Streaming

```python
import asyncio
from moderation_ai.platforms import TwitterAPI

async def combined_tracking():
    twitter = TwitterAPI.from_env()
    
    # Use webhooks for real-time
    tweet_id = "1234567890"
    
    print("Setting up combined tracking...")
    print("1. Webhook: Receive instant comment notifications")
    print("2. Streaming: Catch any missed comments")
    print("3. Polling: Backup for edge cases")
    
    # Subscribe to webhooks
    await twitter.track_post(tweet_id)
    print("✓ Webhook tracking enabled")
    
    # Start streaming as backup
    stream = await twitter.create_stream(reply_to=tweet_id)
    
    print("✓ Streaming enabled")
    print("\nWaiting for comments...")
    
    # Process both sources
    async for reply in stream:
        print(f"@{reply.author_username}: {reply.text}")
        
        # Analyze and moderate
        from moderation_ai.analysis import AbuseDetector
        abuse = AbuseDetector()
        result = abuse.analyze(reply)
        
        if result.is_abuse:
            await twitter.moderate_comment(reply.id, result.recommended_action)

asyncio.run(combined_tracking())
```

## Example 6: Multi-Platform Tracking

```python
import asyncio
from moderation_ai.platforms import TwitterAPI, RedditAPI, YouTubeAPI

async def track_across_platforms():
    # Initialize platforms
    twitter = TwitterAPI.from_env()
    reddit = RedditAPI.from_env()
    youtube = YouTubeAPI.from_env()
    
    # Track posts across platforms
    posts = [
        {"platform": "twitter", "id": "1234567890"},
        {"platform": "reddit", "id": "abc123"},
        {"platform": "youtube", "id": "xyz456"}
    ]
    
    platforms = {
        "twitter": twitter,
        "reddit": reddit,
        "youtube": youtube
    }
    
    # Track all posts
    for post in posts:
        platform = platforms[post["platform"]]
        try:
            await platform.track_post(post["id"])
            print(f"✓ Tracking {post['platform']} post: {post['id']}")
        except Exception as e:
            print(f"✗ Failed to track {post['platform']} post: {e}")

asyncio.run(track_across_platforms())
```

## Example 7: Post Status Monitoring

```python
import asyncio
from moderation_ai.platforms import TwitterAPI

async def monitor_post_health(tweet_id):
    twitter = TwitterAPI.from_env()
    
    while True:
        # Fetch post status
        status = await twitter.get_post_status(tweet_id)
        
        print(f"\nPost Status: {tweet_id}")
        print(f"  Replies: {status.reply_count}")
        print(f"  Likes: {status.like_count}")
        print(f"  Retweets: {status.retweet_count}")
        print(f"  Quotes: {status.quote_count}")
        
        # Check for unusual activity
        if status.reply_count > 1000:
            print("  ⚠ High reply volume detected")
        
        # Wait before next check
        await asyncio.sleep(300)  # Check every 5 minutes

# Start monitoring
tweet_id = "1234567890"
asyncio.create_task(monitor_post_health(tweet_id))

# Keep running
asyncio.run(asyncio.sleep(3600))
```

## Deploying the Webhook Server

### Using ngrok (Local Development)

```bash
# Start ngrok
ngrok http 8080

# Use ngrok URL as webhook
# https://random-id.ngrok.io/webhooks/twitter
```

### Using Railway (Production)

1. Push code to GitHub
2. Connect GitHub repository to Railway
3. Set environment variables in Railway dashboard
4. Deploy automatically

### Using AWS EC2 (Production)

```bash
# Install dependencies
pip install moderation-ai fastapi uvicorn gunicorn

# Start with gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

## Testing the Webhook

### Test Webhook URL

```bash
# Test webhook endpoint
curl -X POST https://your-domain.com/webhooks/twitter \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

### Verify Webhook Subscription

```python
async def verify_webhook():
    twitter = TwitterAPI.from_env()
    
    # Check webhook status
    status = await twitter.get_webhook_status()
    
    print(f"Webhook URL: {status.url}")
    print(f"Status: {status.status}")
    print(f"Active: {status.active}")

asyncio.run(verify_webhook())
```

## Running the Examples

### Run Basic Example

```bash
# Save as webhook_server.py
python webhook_server.py
```

### Run with Specific Tweet

```python
# Modify examples to accept tweet ID as argument
import sys

tweet_id = sys.argv[1] if len(sys.argv) > 1 else "1234567890"

# Use tweet_id in script
```

### Run Multiple Examples

```bash
# Terminal 1: Start webhook server
python webhook_server.py

# Terminal 2: Start tracking
python track_post.py

# Terminal 3: Start monitoring
python monitor_post.py
```

## Tips

1. **Use ngrok for local development**: Easiest way to test webhooks
2. **Combine methods**: Webhooks + streaming + polling for reliability
3. **Monitor health**: Check webhook status regularly
4. **Handle errors**: Implement proper error handling and retry logic
5. **Log everything**: Maintain detailed logs for debugging

## Related Documentation

- **Post Tracking**: `../post-tracking.md` - Detailed tracking guide
- **API Guide**: `../api-guide.md` - API usage
- **Webhooks**: `../../docs/api-reference/webhooks.md` - Webhook patterns
- **Fetch Comments**: `./fetch-comments.md` - Fetching examples

---

**Example Version**: 1.0
**Platform**: Twitter/X
**Status**: Working
