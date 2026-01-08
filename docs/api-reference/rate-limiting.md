---
title: Rate Limiting
category: core
related:
  - ./README.md
  - ./error-handling.md
  - ../platforms/twitter/rate-limits.md
  - ../platforms/reddit/rate-limits.md
---

# Rate Limiting

## Overview

All platform APIs have rate limits to prevent abuse and ensure fair usage. The Moderation AI library provides a unified `RateLimiter` utility that automatically respects platform-specific rate limits, implements exponential backoff, and optimizes batch operations.

## Rate Limiting Architecture

```
Application Request
    ↓
RateLimiter (Unified Interface)
    ↓
Check Rate Limits
    ├─ Within limits → Proceed
    └─ Exceeded → Wait/Backoff
        ↓
Platform API Call
    ↓
Update Rate Limit State
```

## RateLimiter Interface

```python
from moderation_ai.utils import RateLimiter

# Create rate limiter for a platform
limiter = RateLimiter(
    platform="twitter",
    requests_per_minute=300,
    requests_per_hour=1500
)

# Use rate limiter
await limiter.wait()  # Wait if needed, then proceed

# Check rate limit status
status = limiter.get_status()
print(f"Remaining: {status.remaining}")
print(f"Reset at: {status.reset_at}")

# Check if can make request
if limiter.can_request():
    # Make request
    pass
```

## Platform-Specific Rate Limits

### Twitter/X

| Endpoint | Rate Limit | Window | Notes |
|----------|------------|--------|-------|
| GET /2/tweets/:id | 300 | 15 min | Retrieve single tweet |
| GET /2/tweets/search/recent | 450 | 15 min | Search tweets |
| GET /2/users/:id | 300 | 15 min | Retrieve user info |
| GET /2/tweets/:id/hidden_replies | 900 | 15 min | Retrieve replies |
| DELETE /2/tweets/:id/hidden | 900 | 15 min | Hide replies |

```python
from moderation_ai.utils import RateLimiter

# Twitter rate limits vary by endpoint
limiter = RateLimiter(
    platform="twitter",
    endpoints={
        "get_tweet": {"limit": 300, "window": 900},
        "search": {"limit": 450, "window": 900},
        "get_replies": {"limit": 900, "window": 900}
    }
)

# Use rate limiter for specific endpoint
await limiter.wait(endpoint="get_tweet")
```

### Reddit

| Type | Rate Limit | Window | Notes |
|------|------------|--------|-------|
| All requests | 60 | 60s | Per user |
| All requests | 600 | 600s | Per user |
| OAuth apps | Variable | - | Based on app reputation |

```python
from moderation_ai.utils import RateLimiter

# Reddit uses bucket-based rate limiting
limiter = RateLimiter(
    platform="reddit",
    algorithm="token_bucket",
    capacity=60,
    refill_rate=1,  # 1 request per second
    burst_capacity=30  # Allow up to 30 burst requests
)
```

### YouTube

| Method | Rate Limit | Quota | Notes |
|--------|------------|-------|-------|
| commentThreads.list | 10,000 | Daily | Per project |
| comments.list | 10,000 | Daily | Per project |

```python
from moderation_ai.utils import RateLimiter

# YouTube uses daily quota
limiter = RateLimiter(
    platform="youtube",
    algorithm="daily_quota",
    quota=10000,
    reset_at_midnight=True
)
```

### Instagram

| Type | Rate Limit | Window | Notes |
|------|------------|--------|-------|
| Graph API | 200 | Hour | Per user |
| Graph API | 4,800 | Day | Per user |

### Medium

| Type | Rate Limit | Window | Notes |
|------|------------|--------|-------|
| API | 100 | Day | Per user |
| API | 3 | Minute | Per user |

### TikTok

| Type | Rate Limit | Window | Notes |
|------|------------|--------|-------|
| API | Variable | - | Depends on app tier |

## Rate Limiting Algorithms

### 1. Token Bucket Algorithm

Used by Reddit and platforms with burst allowances:

```python
from moderation_ai.utils import RateLimiter

limiter = RateLimiter(
    platform="reddit",
    algorithm="token_bucket",
    capacity=60,  # Maximum tokens
    refill_rate=1,  # Tokens added per second
    initial_tokens=30  # Initial burst capacity
)

# Allow burst requests up to initial_tokens
# Then steady state at refill_rate
```

### 2. Fixed Window Algorithm

Used by platforms with strict time windows:

```python
from moderation_ai.utils import RateLimiter

limiter = RateLimiter(
    platform="twitter",
    algorithm="fixed_window",
    limit=300,
    window=900  # 15 minutes in seconds
)
```

### 3. Sliding Window Algorithm

More accurate rate limiting:

```python
from moderation_ai.utils import RateLimiter

limiter = RateLimiter(
    platform="youtube",
    algorithm="sliding_window",
    limit=10000,
    window=86400  # 24 hours in seconds
)
```

### 4. Daily Quota Algorithm

For platforms with daily quotas:

```python
from moderation_ai.utils import RateLimiter

limiter = RateLimiter(
    platform="youtube",
    algorithm="daily_quota",
    quota=10000,
    timezone="UTC"
)
```

## Exponential Backoff

Automatically retry with exponential backoff on rate limit errors:

```python
from moderation_ai.utils import RateLimiter

limiter = RateLimiter(
    platform="twitter",
    max_retries=5,
    base_delay=1,  # Initial delay in seconds
    max_delay=60,  # Maximum delay in seconds
    exponential_base=2  # Double delay each retry
)

# Automatic retry with backoff:
# Retry 1: wait 1s
# Retry 2: wait 2s
# Retry 3: wait 4s
# Retry 4: wait 8s
# Retry 5: wait 16s
```

## Platform-Specific Headers

Some platforms provide rate limit information in response headers:

### Twitter
```
x-rate-limit-limit: 300
x-rate-limit-remaining: 295
x-rate-limit-reset: 1704768000
```

### Reddit
```
x-ratelimit-remaining: 59.99
x-ratelimit-used: 60
x-ratelimit-reset: 1704768000
```

```python
from moderation_ai.utils import RateLimiter

limiter = RateLimiter(platform="twitter")

# Automatically parse rate limit headers from response
limiter.update_from_headers(response_headers)
```

## Batch Optimization

Process multiple requests efficiently:

### Sequential Batching

```python
from moderation_ai.utils import RateLimiter

limiter = RateLimiter(platform="twitter", requests_per_minute=300)

post_ids = ["1", "2", "3", "4", "5"]

# Process sequentially with rate limiting
for post_id in post_ids:
    await limiter.wait()
    comments = await twitter.fetch_comments(post_id)
```

### Parallel Batching

```python
import asyncio
from moderation_ai.utils import RateLimiter

limiter = RateLimiter(platform="twitter", requests_per_minute=300)

async def fetch_post(post_id):
    await limiter.wait()
    return await twitter.fetch_comments(post_id)

# Process in parallel (rate limiter controls concurrency)
post_ids = ["1", "2", "3", "4", "5"]
results = await asyncio.gather(*[
    fetch_post(post_id) for post_id in post_ids
])
```

### Batch Size Optimization

```python
from moderation_ai.utils import RateLimiter

# Calculate optimal batch size based on rate limit
limiter = RateLimiter(platform="twitter", requests_per_minute=300)

# Allow up to 5 concurrent requests
max_concurrent = 5
batch_size = min(len(post_ids), max_concurrent)

for i in range(0, len(post_ids), batch_size):
    batch = post_ids[i:i + batch_size]
    results = await asyncio.gather(*[
        twitter.fetch_comments(post_id) for post_id in batch
    ])
```

## Priority Queuing

Prioritize important requests:

```python
from moderation_ai.utils import RateLimiter, PriorityRateLimiter

limiter = PriorityRateLimiter(
    platform="twitter",
    requests_per_minute=300
)

# High priority request
await limiter.wait(priority="high")
critical_comment = await twitter.fetch_comments(critical_post_id)

# Low priority request
await limiter.wait(priority="low")
background_comment = await twitter.fetch_comments(background_post_id)
```

## Rate Limit Monitoring

### Real-time Monitoring

```python
from moderation_ai.utils import RateLimiter

limiter = RateLimiter(platform="twitter")

# Get current status
status = limiter.get_status()
print(f"Requests remaining: {status.remaining}")
print(f"Reset at: {status.reset_at}")
print(f"Time until reset: {status.time_until_reset} seconds")
```

### Historical Monitoring

```python
from moderation_ai.utils import RateLimiter

limiter = RateLimiter(platform="twitter")

# Log rate limit usage over time
for i in range(10):
    await limiter.wait()
    # Make request
    print(f"Request {i}: {limiter.get_status()}")
```

### Alerting

```python
from moderation_ai.utils import RateLimiter

limiter = RateLimiter(platform="twitter")

# Alert when approaching rate limit
if limiter.get_status().remaining < 50:
    send_alert("Approaching rate limit")
```

## Multi-Platform Rate Limiting

Manage rate limits across multiple platforms:

```python
from moderation_ai.utils import MultiPlatformRateLimiter

# Manage multiple platforms with one interface
limiter = MultiPlatformRateLimiter({
    "twitter": {"requests_per_minute": 300},
    "reddit": {"requests_per_minute": 60},
    "youtube": {"quota": 10000, "algorithm": "daily_quota"}
})

# Wait across all platforms
await limiter.wait("twitter")
await limiter.wait("reddit")
```

## Best Practices

### 1. Always Use Rate Limiter

```python
# Good
limiter = RateLimiter(platform="twitter")
await limiter.wait()
comments = await twitter.fetch_comments(post_id)

# Bad - no rate limiting
comments = await twitter.fetch_comments(post_id)
```

### 2. Handle Rate Limit Errors

```python
from moderation_ai.utils import RateLimitExceeded

try:
    comments = await twitter.fetch_comments(post_id)
except RateLimitExceeded as e:
    print(f"Rate limit exceeded: {e}")
    await asyncio.sleep(e.retry_after)
```

### 3. Use Batch Operations

```python
# Good - batch
post_ids = ["1", "2", "3", "4", "5"]
results = await asyncio.gather(*[
    twitter.fetch_comments(post_id) for post_id in post_ids
])

# Acceptable - sequential
results = []
for post_id in post_ids:
    result = await twitter.fetch_comments(post_id)
    results.append(result)
```

### 4. Monitor Rate Limits

```python
status = limiter.get_status()
if status.remaining < status.limit * 0.1:
    print("Warning: Approaching rate limit")
```

### 5. Respect Platform Headers

```python
limiter.update_from_headers(response.headers)
```

## Troubleshooting

### Issue: "Rate limit exceeded" despite using RateLimiter

**Possible causes**:
- Multiple instances of RateLimiter
- Rate limits shared across multiple apps
- Platform changed rate limits

**Resolution**:
- Use shared RateLimiter instance
- Check platform documentation for current limits
- Monitor rate limit headers

### Issue: Requests too slow

**Possible causes**:
- Excessive backoff delay
- Too conservative rate limits
- Sequential instead of parallel requests

**Resolution**:
- Reduce backoff delay
- Increase parallelism within limits
- Use batch operations

### Issue: Rate limit not accurate

**Possible causes**:
- Wrong rate limit configuration
- Platform-specific headers not parsed
- Timezone issues for daily quotas

**Resolution**:
- Verify rate limit configuration
- Enable header parsing
- Check timezone settings

## Related Documentation

- **Platform-specific rate limits**: `../platforms/{platform}/rate-limits.md`
- **Error handling**: `./error-handling.md`
- **Common patterns**: `./common-patterns.md`

---

**Last Updated**: January 2024
**Status**: Phase 1 - Documentation Phase
