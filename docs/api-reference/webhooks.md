---
title: Webhook Patterns
category: core
related:
  - ./README.md
  - ./error-handling.md
---

# Webhook Patterns

## Overview

Webhooks allow platforms to push real-time event notifications to your application. This document describes webhook patterns used across platforms, event payload structures, and how to handle incoming webhook events.

## Webhook Architecture

```
Platform Event
    ↓
Platform Webhook Service
    ↓
Your Webhook Endpoint
    ↓
WebhookHandler (Unified Interface)
    ↓
Event Processing
    ├─ Comment Created
    ├─ Comment Updated
    ├─ Post Created
    └─ Moderation Action
```

## Webhook Handler Interface

```python
from moderation_ai.utils import WebhookHandler

# Create webhook handler
handler = WebhookHandler(
    secret="webhook_secret",
    endpoint="/webhook",
    allowed_ips=["0.0.0.0/0"]  # Allow all IPs
)

# Register event handlers
@handler.on("comment.created")
async def handle_comment_created(event):
    comment = event.data
    print(f"New comment: {comment.id}")

@handler.on("comment.updated")
async def handle_comment_updated(event):
    comment = event.data
    print(f"Updated comment: {comment.id}")

# Start webhook server
await handler.start(port=8080)
```

## Platform-Specific Webhooks

### Twitter/X

**Webhook Events**:
- `tweet.create` - New tweet created
- `tweet.delete` - Tweet deleted
- `favorite.create` - Tweet favorited

**Setup**:
1. Configure webhook URL in Twitter Developer Portal
2. Set up CRC (Challenge-Response Check) validation
3. Subscribe to events

**Example Payload**:
```json
{
  "tweet_create_events": [
    {
      "created_at": "Wed Oct 10 20:19:24 +0000 2018",
      "id": 1050118621198921728,
      "text": "Hello, world!",
      "user": {
        "id": 123456789,
        "screen_name": "username"
      }
    }
  ]
}
```

### Reddit

**Webhook Events**:
- `comment.post` - New comment posted
- `post.submit` - New post submitted
- `modaction` - Moderator action

**Setup**:
1. Use Reddit's webhook API
2. Set up subscription
3. Provide callback URL

**Example Payload**:
```json
{
  "data": {
    "author": {
      "name": "username"
    },
    "body": "Comment text",
    "id": "comment_id",
    "link_id": "post_id"
  },
  "type": "comment.post"
}
```

### YouTube

**Webhook Events**:
- `comment.insert` - New comment added
- `comment.update` - Comment updated
- `comment.delete` - Comment deleted

**Setup**:
1. Use Google Cloud Pub/Sub
2. Configure topic subscription
3. Set up push endpoint

**Example Payload**:
```json
{
  "comment": {
    "id": "comment_id",
    "snippet": {
      "textDisplay": "Comment text",
      "authorDisplayName": "username"
    }
  }
}
```

### Instagram

**Webhook Events**:
- `comments` - New comment added

**Setup**:
1. Configure webhook URL in Meta App Dashboard
2. Subscribe to webhook fields
3. Verify endpoint

**Example Payload**:
```json
{
  "entry": [
    {
      "changes": [
        {
          "field": "comments",
          "value": {
            "id": "comment_id",
            "text": "Comment text",
            "from": {
              "username": "username"
            }
          }
        }
      ]
    }
  ]
}
```

### Medium

Medium does not provide native webhooks. Use polling instead.

### TikTok

**Webhook Events**:
- `comment.post` - New comment added

**Setup**:
1. Configure webhook URL in TikTok Developer Portal
2. Verify endpoint
3. Subscribe to events

## Event Types

### comment.created
New comment created on a post.

**Payload Structure**:
```python
{
    "event_id": "evt_123456789",
    "event_type": "comment.created",
    "timestamp": "2024-01-08T10:30:00Z",
    "platform": "twitter",
    "data": {
        "comment": {
            "id": "comment_id",
            "post_id": "post_id",
            "author_id": "author_id",
            "author_username": "username",
            "text": "Comment text",
            "created_at": "2024-01-08T10:30:00Z"
        }
    }
}
```

### comment.updated
Existing comment was edited.

**Payload Structure**:
```python
{
    "event_id": "evt_123456789",
    "event_type": "comment.updated",
    "timestamp": "2024-01-08T10:30:00Z",
    "platform": "reddit",
    "data": {
        "comment": {
            "id": "comment_id",
            "post_id": "post_id",
            "author_id": "author_id",
            "author_username": "username",
            "text": "Updated comment text",
            "created_at": "2024-01-08T10:00:00Z",
            "updated_at": "2024-01-08T10:30:00Z"
        }
    }
}
```

### comment.deleted
Comment was removed.

**Payload Structure**:
```python
{
    "event_id": "evt_123456789",
    "event_type": "comment.deleted",
    "timestamp": "2024-01-08T10:30:00Z",
    "platform": "youtube",
    "data": {
        "comment_id": "comment_id",
        "post_id": "post_id"
    }
}
```

### post.created
New post created.

**Payload Structure**:
```python
{
    "event_id": "evt_123456789",
    "event_type": "post.created",
    "timestamp": "2024-01-08T10:30:00Z",
    "platform": "instagram",
    "data": {
        "post": {
            "id": "post_id",
            "author_id": "author_id",
            "author_username": "username",
            "caption": "Post caption",
            "media_urls": ["url1", "url2"],
            "created_at": "2024-01-08T10:30:00Z"
        }
    }
}
```

## Webhook Security

### HMAC Signature Verification

Verify webhook authenticity:

```python
from moderation_ai.utils import verify_webhook_signature

def webhook_endpoint(request):
    # Get signature from headers
    signature = request.headers.get("X-Signature")
    payload = request.body

    # Verify signature
    if verify_webhook_signature(
        payload=payload,
        signature=signature,
        secret="your_webhook_secret"
    ):
        # Signature is valid
        process_webhook(payload)
    else:
        # Invalid signature
        return "Invalid signature", 401
```

### IP Whitelisting

Restrict webhook sources:

```python
from moderation_ai.utils import WebhookHandler

handler = WebhookHandler(
    allowed_ips=[
        "192.0.2.0/24",  # Twitter IP range
        "198.51.100.0/24",  # Reddit IP range
    ]
)
```

### Timestamp Validation

Check for replay attacks:

```python
from moderation_ai.utils import validate_webhook_timestamp

def webhook_endpoint(request):
    timestamp = request.headers.get("X-Timestamp")

    # Reject if timestamp is too old
    if not validate_webhook_timestamp(timestamp, max_age=300):
        return "Invalid timestamp", 401

    process_webhook(request.body)
```

## Webhook Endpoint Implementation

### FastAPI Example

```python
from fastapi import FastAPI, Request, HTTPException
from moderation_ai.utils import WebhookHandler, verify_webhook_signature

app = FastAPI()
handler = WebhookHandler(secret="your_secret")

@app.post("/webhook/{platform}")
async def webhook(platform: str, request: Request):
    payload = await request.body()

    # Verify signature
    signature = request.headers.get("X-Signature")
    if not verify_webhook_signature(payload, signature, "your_secret"):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Process event
    event = handler.parse_event(payload, platform)

    # Trigger handlers
    await handler.handle(event)

    return {"status": "ok"}
```

### Flask Example

```python
from flask import Flask, request, jsonify
from moderation_ai.utils import WebhookHandler

app = Flask(__name__)
handler = WebhookHandler(secret="your_secret")

@app.route("/webhook/<platform>", methods=["POST"])
def webhook(platform):
    payload = request.get_data()

    # Verify signature
    signature = request.headers.get("X-Signature")
    if not handler.verify_signature(payload, signature):
        return jsonify({"error": "Invalid signature"}), 401

    # Process event
    event = handler.parse_event(payload, platform)
    handler.handle(event)

    return jsonify({"status": "ok"})
```

## Event Processing Patterns

### Pattern 1: Real-Time Moderation

```python
@handler.on("comment.created")
async def moderate_comment(event):
    comment = event.data.comment

    # Analyze comment
    decision = await standards_engine.validate(comment.text)

    # Apply moderation action
    if decision.action != "approve":
        platform = get_platform(event.platform)
        await platform.moderate_comment(
            comment.id,
            decision.action
        )
```

### Pattern 2: Event Queue

```python
import asyncio
from collections import deque

event_queue = deque()

@handler.on("comment.created")
async def queue_comment(event):
    # Add to queue for batch processing
    event_queue.append(event)

async def process_queue():
    while True:
        if event_queue:
            event = event_queue.popleft()
            await process_event(event)
        await asyncio.sleep(1)

# Start queue processor
asyncio.create_task(process_queue())
```

### Pattern 3: Multi-Platform Aggregation

```python
all_events = []

@handler.on("comment.created")
async def aggregate_comments(event):
    all_events.append(event)
    print(f"Total comments: {len(all_events)}")
```

### Pattern 4: Conditional Processing

```python
@handler.on("comment.created")
async def conditional_moderation(event):
    comment = event.data.comment

    # Only process certain authors
    if comment.author_username in ["spammer1", "spammer2"]:
        await hide_comment(comment)
```

## Webhook Testing

### Local Testing with ngrok

```bash
# Start ngrok
ngrok http 8080

# Use ngrok URL as webhook endpoint
# https://random-id.ngrok.io/webhook
```

### Mock Webhook Events

```python
from moderation_ai.utils import WebhookEvent

# Create mock event
event = WebhookEvent(
    event_id="evt_123",
    event_type="comment.created",
    platform="twitter",
    data={
        "comment": {
            "id": "comment_id",
            "text": "Test comment",
            "author_username": "test_user"
        }
    }
)

# Test handler
await handler.handle(event)
```

### Webhook Replay

```python
from moderation_ai.utils import WebhookReplay

# Replay saved webhook events
replay = WebhookReplay()
await replay.replay_from_file("webhooks.json")
```

## Webhook Management

### Registering Webhooks

```python
from moderation_ai.utils import register_webhook

await register_webhook(
    platform="twitter",
    url="https://your-domain.com/webhook/twitter",
    secret="your_secret"
)
```

### Listing Webhooks

```python
from moderation_ai.utils import list_webhooks

webhooks = await list_webhooks(platform="twitter")
for webhook in webhooks:
    print(f"{webhook.id}: {webhook.url}")
```

### Deleting Webhooks

```python
from moderation_ai.utils import delete_webhook

await delete_webhook(
    platform="twitter",
    webhook_id="webhook_id"
)
```

## Best Practices

### 1. Always Verify Signatures

```python
if not verify_webhook_signature(payload, signature, secret):
    return "Invalid signature", 401
```

### 2. Respond Quickly

```python
@app.post("/webhook")
async def webhook(request):
    # Process event asynchronously
    asyncio.create_task(process_event(request.json()))
    return {"status": "ok"}  # Respond immediately
```

### 3. Retry Failed Events

```python
from moderation_ai.utils import WebhookRetry

retry = WebhookRetry(max_retries=3)
await retry.process_event(event)
```

### 4. Log Events

```python
import logging

logger = logging.getLogger(__name__)

@handler.on("comment.created")
async def log_event(event):
    logger.info(f"Comment created: {event.data.comment.id}")
```

### 5. Monitor Webhook Health

```python
from moderation_ai.utils import WebhookMonitor

monitor = WebhookMonitor()
monitor.start_health_checks()
```

## Troubleshooting

### Issue: Webhook not receiving events

**Possible causes**:
- Webhook URL not reachable
- Signature verification failing
- Platform not configured correctly

**Resolution**:
- Verify webhook URL is publicly accessible
- Check signature verification logic
- Verify platform configuration

### Issue: Duplicate events

**Possible causes**:
- Multiple webhook registrations
- Platform retry logic
- Event replay

**Resolution**:
- Use event deduplication (event_id)
- Check for existing event_id before processing
- Monitor webhook registrations

### Issue: Events not processed

**Possible causes**:
- Event handler not registered
- Event type not recognized
- Handler exception

**Resolution**:
- Verify event handler is registered
- Check event type matches handler
- Check error logs

## Related Documentation

- **Error Handling**: `./error-handling.md`
- **Authentication**: `./authentication.md`
- **Platform-specific webhooks**: `../platforms/{platform}/api-guide.md`

---

**Last Updated**: January 2024
**Status**: Phase 1 - Documentation Phase
