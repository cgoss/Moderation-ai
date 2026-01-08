---
title: Twitter Post Tracking
category: platform
platform: twitter
related:
  - ./README.md
  - ./api-guide.md
  - ../../docs/api-reference/webhooks.md
---

# Twitter Post Tracking

## Overview

Post tracking enables real-time monitoring of tweets and their replies through webhooks and streaming. This allows automatic moderation as comments are posted.

## Tracking Methods

### 1. Account Activity API (Webhooks)

**Use Case**: Monitor your own tweets for new replies

**Advantages**:
- Real-time notifications
- Low latency
- Efficient (no polling needed)

**Limitations**:
- Only tracks your own tweets
- Requires webhook server
- More complex setup

### 2. Filtered Stream API

**Use Case**: Monitor specific keywords, hashtags, or users

**Advantages**:
- Real-time streaming
- Flexible filtering
- Can track multiple tweets

**Limitations**:
- Counts against rate limits (streaming)
- Requires persistent connection
- Complex error handling

### 3. Polling (Manual)

**Use Case**: Simple monitoring without webhooks

**Advantages**:
- Simple to implement
- No infrastructure needed
- Works in any environment

**Limitations**:
- Not real-time
- Higher latency
- Wastes rate limits

## Account Activity Webhooks

### Setup Webhook URL

1. Go to Twitter Developer Portal
2. Navigate to your app settings
3. Add webhook URL:
   ```
   https://your-domain.com/webhooks/twitter
   ```
4. Verify webhook ownership
5. Subscribe to events

### Subscribe to Events

```python
from moderation_ai.platforms import TwitterAPI

twitter = TwitterAPI.from_env()

# Subscribe to comment.created events
await twitter.subscribe_webhook_events([
    "comment.created",
    "comment.updated"
])

# Or subscribe to specific tweet
await twitter.track_post(tweet_id)
```

### Webhook Handler

```python
from fastapi import FastAPI, Request
from moderation_ai.utils import WebhookHandler

app = FastAPI()
handler = WebhookHandler(secret="your_webhook_secret")

@app.post("/webhooks/twitter")
async def twitter_webhook(request: Request):
    # Verify signature
    signature = request.headers.get("x-twitter-webhooks-signature")
    payload = await request.body()
    
    if not handler.verify_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse event
    event = handler.parse_event(payload, platform="twitter")
    
    # Handle event
    await handle_twitter_event(event)
    
    return {"status": "ok"}
```

### Event Types

| Event | Description | Payload |
|-------|-------------|----------|
| `comment.created` | New reply to tweet | Comment object |
| `comment.updated` | Reply edited | Comment object |
| `comment.deleted` | Reply deleted | Comment ID |
| `tweet.created` | New tweet (user) | Tweet object |

## Filtered Streaming

### Create Stream Filter

```python
from moderation_ai.platforms import TwitterAPI

twitter = TwitterAPI.from_env()

# Define filter
stream_filter = {
    "track": ["moderation_ai", "content_moderation"],  # Keywords
    "follow": ["1234567890", "0987654321"],    # User IDs
    "locations": [-74.0060,40.7128,-73.9940,40.7794],  # NYC
    "language": "en"
}

# Create stream
stream = await twitter.create_stream(filter=stream_filter)

# Process tweets in real-time
async for tweet in stream:
    # Analyze tweet
    decision = standards.validate(tweet.text)
    
    # Moderate if needed
    if decision.action != "approve":
        print(f"Tweet needs moderation: {decision.action}")
```

### Track Specific Tweet Replies

```python
# Track replies to specific tweet
tweet_id = "1234567890"

stream = await twitter.create_stream(reply_to=tweet_id)

async for reply in stream:
    # Analyze reply
    comment = await twitter.fetch_comment(reply.id)
    result = analyzer.analyze(comment)
    
    # Moderate automatically
    if result.violation_detected:
        await twitter.moderate_comment(comment.id, result.recommended_action)
```

## Polling Approach

### Poll for New Comments

```python
import asyncio
from datetime import datetime, timedelta

async def poll_for_comments(tweet_id, interval_seconds=60):
    last_comment_count = 0
    
    while True:
        # Fetch current comments
        comments = await twitter.fetch_comments(tweet_id)
        current_count = len(comments)
        
        # Check for new comments
        if current_count > last_comment_count:
            new_comments = comments[last_comment_count:]
            
            for comment in new_comments:
                # Analyze and moderate
                result = analyzer.analyze(comment)
                
                if result.violation_detected:
                    await twitter.moderate_comment(comment.id, result.recommended_action)
        
        last_comment_count = current_count
        
        # Wait before next poll
        await asyncio.sleep(interval_seconds)

# Start polling
asyncio.create_task(poll_for_comments("1234567890"))
```

### Poll Multiple Tweets

```python
async def poll_multiple_tweets(tweet_ids, interval_seconds=60):
    tweet_data = {}
    
    # Initialize tweet data
    for tweet_id in tweet_ids:
        tweet_data[tweet_id] = {"last_count": 0}
    
    while True:
        for tweet_id in tweet_ids:
            # Fetch comments
            comments = await twitter.fetch_comments(tweet_id)
            current_count = len(comments)
            last_count = tweet_data[tweet_id]["last_count"]
            
            # Process new comments
            if current_count > last_count:
                new_comments = comments[last_count:]
                
                for comment in new_comments:
                    result = analyzer.analyze(comment)
                    
                    if result.violation_detected:
                        await twitter.moderate_comment(comment.id, result.recommended_action)
            
            # Update count
            tweet_data[tweet_id]["last_count"] = current_count
        
        # Wait before next poll
        await asyncio.sleep(interval_seconds)
```

## Webhook Security

### Verify Signature

```python
from moderation_ai.utils import verify_webhook_signature

async def twitter_webhook(request):
    payload = await request.body()
    signature = request.headers.get("x-twitter-webhooks-signature")
    
    # Verify HMAC signature
    if verify_webhook_signature(
        payload=payload,
        signature=signature,
        secret="your_webhook_secret"
    ):
        return {"status": "ok"}
    else:
        return {"status": "error", "message": "Invalid signature"}
```

### CRC Challenge

Twitter requires CRC (Challenge-Response Check) verification:

```python
from hashlib import sha256
import hmac

def handle_crc_challenge(request):
    # Get challenge
    crc_token = request.args.get("crc_token")
    
    # Create response
    response_token = hmac.new(
        bytes("your_consumer_secret", "utf-8"),
        bytes(crc_token, "utf-8"),
        sha256
    ).hexdigest()
    
    return {
        "response_token": f"sha256={response_token}"
    }
```

## Event Handling

### Handle Comment Created

```python
async def handle_comment_created(event):
    comment = event.data.comment
    
    # Analyze comment
    result = analyzer.analyze(comment)
    
    # Log analysis
    logger.info(f"Comment {comment.id}: {result.sentiment}")
    
    # Moderate if needed
    if result.violation_detected:
        await twitter.moderate_comment(comment.id, result.recommended_action)
        logger.info(f"Moderated comment: {result.recommended_action}")
```

### Handle Comment Updated

```python
async def handle_comment_updated(event):
    comment = event.data.comment
    
    # Re-analyze updated comment
    result = analyzer.analyze(comment)
    
    # Re-apply moderation if needed
    if result.violation_detected and result.severity == "critical":
        await twitter.moderate_comment(comment.id, "remove")
```

## Best Practices

### 1. Use Webhooks When Possible

```python
# Good - real-time webhooks
await twitter.track_post(tweet_id)

# Acceptable - polling
await poll_for_comments(tweet_id, interval_seconds=60)
```

### 2. Implement Retry Logic

```python
# Retry failed webhook deliveries
async def handle_webhook_with_retry(event, max_retries=3):
    for attempt in range(max_retries):
        try:
            await handle_webhook_event(event)
            break
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                logger.error(f"Failed to handle event: {e}")
                raise
```

### 3. Track Processing State

```python
processed_comments = set()

async def handle_comment_created(event):
    comment = event.data.comment
    
    # Skip already processed
    if comment.id in processed_comments:
        return
    
    # Process comment
    await analyze_and_moderate(comment)
    
    # Mark as processed
    processed_comments.add(comment.id)
```

### 4. Monitor Webhook Health

```python
async def monitor_webhooks():
    while True:
        # Check webhook status
        status = await twitter.get_webhook_status()
        
        if not status.is_healthy:
            logger.warning(f"Webhook unhealthy: {status.message}")
            # Send alert
            await send_alert("Twitter webhook down")
        
        await asyncio.sleep(60)  # Check every minute
```

### 5. Graceful Shutdown

```python
async def shutdown():
    # Stop streaming
    await twitter.stop_stream()
    
    # Unsubscribe from webhooks
    await twitter.unsubscribe_webhook_events()
    
    # Save state
    save_processed_comments(processed_comments)
```

## Troubleshooting

### Issue: Webhooks Not Receiving Events

**Possible causes**:
- Webhook URL not reachable
- CRC verification failed
- Subscription not active

**Solution**:
- Verify webhook URL is publicly accessible
- Test CRC challenge handling
- Check subscription status in Twitter Developer Portal

### Issue: Streaming Connection Dropped

**Possible causes**:
- Network issues
- Rate limits
- Twitter API issues

**Solution**:
- Implement auto-reconnect
- Add exponential backoff
- Monitor connection health

### Issue: Duplicate Events

**Possible causes**:
- Webhook retries
- Multiple subscriptions

**Solution**:
- Track processed event IDs
- Implement idempotent handlers
- Check for duplicate deliveries

## Related Documentation

- **API Guide**: `./api-guide.md` - API usage
- **Authentication**: `./authentication.md` - Auth setup
- **Webhooks**: `../../docs/api-reference/webhooks.md` - Webhook patterns
- **Moderation**: `./comment-moderation.md` - Moderation guidelines

---

**Last Updated**: January 2024
**Status**: Phase 2 - Documentation Complete
