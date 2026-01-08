---
title: Reddit Rate Limits
category: platform
platform: reddit
related:
  - ./README.md
  - ./api-guide.md
  - ../../docs/api-reference/rate-limiting.md
---

# Reddit Rate Limits

## Overview

Reddit API uses a token bucket rate limiting system with a maximum of 60 requests per minute for authenticated requests. Rate limits reset gradually over time as tokens refill.

## Rate Limit System

### Token Bucket Algorithm

Reddit's rate limiting works like a token bucket:
- **Bucket capacity**: 60 tokens
- **Refill rate**: 1 token per second
- **Request cost**: 1 token per request (typically)

### How It Works

```
Time: 0s    → Tokens: 60
Time: 1s    → Tokens: 59 (refilled 1, used 1)
Time: 2s    → Tokens: 58 (refilled 1, used 1)
...
Time: 60s   → Tokens: 60 (fully refilled)
```

### Rate Limit Headers

```
x-ratelimit-remaining: 59
x-ratelimit-used: 1
x-ratelimit-reset: 1704768000
```

## Rate Limits by Endpoint

### Read Operations

| Endpoint | Rate Limit | Notes |
|----------|-------------|-------|
| Get Post | ~1 req/min | 1 request per post |
| Get Comments | ~1 req/min | 1 request per post |
| User Timeline | ~1 req/min | Varies by user |
| Subreddit Posts | ~1 req/min | Varies by subreddit |
| Search | ~30 req/min | Special search limits |

### Write Operations

| Endpoint | Rate Limit | Notes |
|----------|-------------|-------|
| Submit Post | 1 req/min | Limited submission rate |
| Post Comment | ~1 req/min | 1 request per comment |
| Vote | ~30 req/min | Upvote/downvote |
| Remove Comment | ~1 req/min | Requires mod perms |
| Approve Comment | ~1 req/min | Requires mod perms |

### Moderation Operations

| Endpoint | Rate Limit | Notes |
|----------|-------------|-------|
| Remove Comment | 1 req/min | Requires mod permissions |
| Approve Comment | 1 req/min | Requires mod permissions |
| Distinguish Comment | 1 req/min | Mod-only action |
| Lock Thread | 1 req/min | Mod-only action |
| Ban User | 1 req/min | Mod-only action |

## Parsing Rate Limit Headers

### Check Remaining Requests

```python
from moderation_ai.platforms import RedditAPI

reddit = RedditAPI.from_env()

# Rate limit information is automatically parsed
status = reddit.get_rate_limit_status()

print(f"Remaining: {status.remaining}")
print(f"Used: {status.used}")
print(f"Reset at: {status.reset_at}")
print(f"Seconds until reset: {status.seconds_until_reset}")
```

### Check Rate Limit Reset

```python
# Get time until full reset
time_until_full = status.time_until_full_reset

if time_until_full > 60:
    print(f"Rate limit fully resets in {time_until_full // 60} minutes")
else:
    print(f"Rate limit fully resets in {time_until_full} seconds")
```

## Rate Limiting Strategies

### 1. Token Bucket Rate Limiting

```python
from moderation_ai.utils import RateLimiter

limiter = RateLimiter(
    platform="reddit",
    algorithm="token_bucket",
    capacity=60,
    refill_rate=1  # 1 token per second
)

await limiter.wait()
comments = await reddit.fetch_comments(post_id)
```

### 2. Fixed Window Rate Limiting

```python
limiter = RateLimiter(
    platform="reddit",
    algorithm="fixed_window",
    limit=60,
    window=60  # 60 seconds
)
```

### 3. Exponential Backoff

```python
import asyncio
from moderation_ai.utils import RateLimitExceeded

max_retries = 5
base_delay = 1

for attempt in range(max_retries):
    try:
        comments = await reddit.fetch_comments(post_id)
        break
    except RateLimitExceeded as e:
        if attempt < max_retries - 1:
            delay = base_delay * (2 ** attempt)
            print(f"Rate limited, waiting {delay}s...")
            await asyncio.sleep(delay)
        else:
            raise
```

## Best Practices

### 1. Monitor Rate Limits

```python
status = reddit.get_rate_limit_status()

# Alert when approaching limit
if status.remaining < 10:
    print("Warning: Approaching rate limit")
```

### 2. Use Batch Operations

```python
# Good - batch fetch
post_ids = ["1", "2", "3", "4", "5"]
posts = await reddit.fetch_posts(post_ids)

# Bad - individual fetches
for post_id in post_ids:
    post = await reddit.fetch_post(post_id)
```

### 3. Implement Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
async def get_post_info(post_id):
    return await reddit.fetch_post(post_id)
```

### 4. Optimize Requests

```python
# Request all needed data in single call
comments = await reddit.fetch_comments(
    post_id,
    include_threaded=True,
    include_depth=True
)
```

### 5. Use Parallel Processing

```python
import asyncio

# Fetch multiple posts in parallel
post_ids = ["1", "2", "3", "4", "5"]
posts = await asyncio.gather(*[
    reddit.fetch_post(post_id)
    for post_id in post_ids
])
```

## Rate Limit Errors

### 429 Too Many Requests

```python
from moderation_ai.utils import RateLimitExceeded

try:
    comments = await reddit.fetch_comments(post_id)
except RateLimitExceeded as e:
    print(f"Rate limit exceeded")
    print(f"Retry after: {e.retry_after} seconds")
    print(f"Reset at: {e.reset_at}")
    
    # Wait and retry
    await asyncio.sleep(e.retry_after)
    comments = await reddit.fetch_comments(post_id)
```

### Handling Rate Limit Errors

```python
async def safe_fetch_comments(post_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            comments = await reddit.fetch_comments(post_id)
            return comments
        except RateLimitExceeded as e:
            if attempt < max_retries - 1:
                print(f"Rate limited, attempt {attempt + 1}/{max_retries}")
                await asyncio.sleep(e.retry_after)
            else:
                raise
```

## Advanced Rate Limiting

### Multi-Endpoint Rate Limiting

```python
from moderation_ai.utils import MultiEndpointRateLimiter

limiter = MultiEndpointRateLimiter({
    "get_post": 60,
    "get_comments": 60,
    "user_timeline": 60
})

# Use rate limiter for each endpoint
await limiter.wait("get_post")
post = await reddit.fetch_post(post_id)

await limiter.wait("get_comments")
comments = await reddit.fetch_comments(post_id)
```

### Adaptive Rate Limiting

```python
limiter = RateLimiter(
    platform="reddit",
    adaptive=True,
    safety_margin=0.1  # Use 90% of limit
)
```

### Distributed Rate Limiting

```python
from moderation_ai.utils import DistributedRateLimiter

limiter = DistributedRateLimiter(
    platform="reddit",
    redis_url="redis://localhost:6379",
    limit=60,
    window=60
)

# Works across multiple instances
await limiter.wait()
comments = await reddit.fetch_comments(post_id)
```

## Monitoring Rate Limits

### Track Usage Over Time

```python
from moderation_ai.utils import RateLimitMonitor

monitor = RateLimitMonitor(platform="reddit")

async def with_monitoring(func, *args):
    monitor.track_request()
    result = await func(*args)
    monitor.track_response()
    return result

# Use with monitoring
comments = await with_monitoring(
    reddit.fetch_comments,
    post_id
)

# Get usage report
report = monitor.get_report()
print(f"Requests made: {report.requests_made}")
print(f"Rate limit hits: {report.rate_limit_hits}")
```

### Alert on Rate Limit

```python
async def rate_limit_alert():
    while True:
        status = reddit.get_rate_limit_status()
        
        if status.remaining < 5:
            # Send alert
            await send_alert(
                "Reddit rate limit warning",
                f"Only {status.remaining} requests remaining"
            )
        
        await asyncio.sleep(10)  # Check every 10 seconds
```

## Rate Limit Optimization

### 1. Prioritize Requests

```python
# High priority: moderation actions
if needs_moderation:
    await reddit.moderate_comment(comment_id, "remove")

# Medium priority: fetch recent comments
await reddit.fetch_comments(post_id)

# Low priority: fetch historical data
await reddit.fetch_user_timeline(username)
```

### 2. Use Pagination Effectively

```python
# Fetch more per page
result = await reddit.fetch_comments(post_id, limit=100)
```

### 3. Batch Moderation Actions

```python
# Apply moderation in batches
actions = [
    (comment_id1, "remove"),
    (comment_id2, "flag"),
    (comment_id3, "approve")
]

for comment_id, action in actions:
    await reddit.moderate_comment(comment_id, action)
```

## Troubleshooting

### Issue: Frequent Rate Limit Errors

**Possible causes**:
- Not respecting rate limits
- Making too many requests
- Multiple instances running

**Solution**:
- Implement proper rate limiting
- Reduce request frequency
- Ensure single instance or use distributed limiting

### Issue: Rate Limit Not Resetting

**Possible causes**:
- Wrong reset time calculation
- Token bucket not refilling
- Headers not being parsed

**Solution**:
- Parse remaining tokens from headers
- Calculate reset time accurately
- Update rate limit status after each request

### Issue: Different Rate Limits

**Possible causes**:
- Different endpoints have different limits
- OAuth vs script auth
- Subreddit-specific limits

**Solution**:
- Check endpoint-specific limits
- Verify auth type matches expected limits
- Account for subreddit variations

## Related Documentation

- **API Guide**: `./api-guide.md` - API usage
- **Authentication**: `./authentication.md` - Auth setup
- **General Rate Limiting**: `../../docs/api-reference/rate-limiting.md` - Cross-platform strategies

---

**Last Updated**: January 2024
**Status**: Phase 2 - Documentation Complete
