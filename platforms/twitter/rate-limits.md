---
title: Twitter Rate Limits
category: platform
platform: twitter
related:
  - ./README.md
  - ./api-guide.md
  - ../../docs/api-reference/rate-limiting.md
---

# Twitter Rate Limits

## Overview

Twitter API v2 uses tiered rate limits based on API access level. Rate limits reset in 15-minute windows and are tracked separately for different endpoints.

## Access Levels

| Level | Price | Rate Limits | Features |
|-------|-------|-------------|----------|
| **Free** | Free | 300/15min | Basic read access |
| **Basic** | $100/mo | 10,000/15min | Read + write access |
| **Pro** | $5,000/mo | 1,000,000/15min | Full API access |
| **Enterprise** | Custom | Unlimited | Custom solutions |

## Rate Limits by Endpoint

### Tweet Operations

| Endpoint | Free | Basic | Pro | Window |
|----------|-------|-------|-----|--------|
| Get Tweet | 300 | 900 | 1,000,000 | 15 min |
| User Timeline | 300 | 900 | 1,000,000 | 15 min |
| Tweet Replies | 300 | 900 | 1,000,000 | 15 min |
| Post Tweet | N/A | 100 | 100 | 24 hr |
| Delete Tweet | N/A | 200 | 200 | 15 min |

### Search Operations

| Endpoint | Free | Basic | Pro | Window |
|----------|-------|-------|-----|--------|
| Recent Search | 450 | 450 | 450 | 15 min |
| Full Search | N/A | N/A | 60 | 1 min |

### User Operations

| Endpoint | Free | Basic | Pro | Window |
|----------|-------|-------|-----|--------|
| Get User | 900 | 900 | 1,000,000 | 15 min |
| User Followers | 15 | 15 | 15 | 15 min |
| User Following | 15 | 15 | 15 | 15 min |

### Moderation Operations

| Endpoint | Free | Basic | Pro | Window |
|----------|-------|-------|-----|--------|
| Hide Reply | N/A | 900 | 1,000,000 | 15 min |
| Unhide Reply | N/A | 900 | 1,000,000 | 15 min |

## Rate Limit Headers

Twitter includes rate limit information in response headers:

```
x-rate-limit-limit: 900
x-rate-limit-remaining: 895
x-rate-limit-reset: 1704768000
```

### Header Fields

| Header | Description | Example |
|--------|-------------|---------|
| `x-rate-limit-limit` | Maximum requests | 900 |
| `x-rate-limit-remaining` | Remaining requests | 895 |
| `x-rate-limit-reset` | Reset timestamp (Unix) | 1704768000 |

## Parsing Rate Limit Headers

```python
from moderation_ai.platforms import TwitterAPI

twitter = TwitterAPI.from_env()

# Rate limit information is automatically parsed
status = twitter.get_rate_limit_status()

print(f"Remaining: {status.remaining}")
print(f"Limit: {status.limit}")
print(f"Reset at: {status.reset_at}")
print(f"Seconds until reset: {status.seconds_until_reset}")
```

## Rate Limiting Strategies

### 1. Fixed Window Rate Limiting

Respect the 15-minute window:

```python
from moderation_ai.utils import RateLimiter

limiter = RateLimiter(
    platform="twitter",
    limit=900,
    window=900  # 15 minutes in seconds
)

await limiter.wait()
comments = await twitter.fetch_comments(tweet_id)
```

### 2. Token Bucket Algorithm

Allow bursts within limits:

```python
limiter = RateLimiter(
    platform="twitter",
    algorithm="token_bucket",
    capacity=900,
    refill_rate=1  # 1 request per second
)
```

### 3. Exponential Backoff

Retry with increasing delays:

```python
import asyncio
from moderation_ai.utils import RateLimitExceeded

max_retries = 5
base_delay = 1

for attempt in range(max_retries):
    try:
        comments = await twitter.fetch_comments(tweet_id)
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
status = twitter.get_rate_limit_status()

# Alert when approaching limit
if status.remaining < status.limit * 0.1:
    print("Warning: Approaching rate limit")
```

### 2. Use Batch Operations

```python
# Good - batch fetch
tweet_ids = ["1", "2", "3", "4", "5"]
tweets = await twitter.fetch_tweets(tweet_ids)

# Bad - individual fetches
for tweet_id in tweet_ids:
    tweet = await twitter.fetch_tweet(tweet_id)
```

### 3. Implement Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
async def get_user_info(user_id):
    return await twitter.fetch_user(user_id=user_id)
```

### 4. Optimize Requests

```python
# Request all needed fields in single call
comments = await twitter.fetch_comments(
    tweet_id,
    tweet_fields=["created_at", "public_metrics", "author_id"],
    user_fields=["username", "name", "verified"],
    expansions=["author_id"]
)
```

### 5. Use Parallel Processing

```python
import asyncio

# Fetch multiple tweets in parallel
tweet_ids = ["1", "2", "3", "4", "5"]
tweets = await asyncio.gather(*[
    twitter.fetch_tweet(tweet_id)
    for tweet_id in tweet_ids
])
```

## Rate Limit Errors

### 429 Rate Limit Exceeded

```python
from moderation_ai.utils import RateLimitExceeded

try:
    comments = await twitter.fetch_comments(tweet_id)
except RateLimitExceeded as e:
    print(f"Rate limit exceeded")
    print(f"Retry after: {e.retry_after} seconds")
    print(f"Reset at: {e.reset_at}")
    
    # Wait and retry
    await asyncio.sleep(e.retry_after)
    comments = await twitter.fetch_comments(tweet_id)
```

### Handling Rate Limit Errors

```python
async def safe_fetch_comments(tweet_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await twitter.fetch_comments(tweet_id)
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
    "get_tweet": 900,
    "tweet_replies": 900,
    "user_timeline": 900
})

# Use rate limiter for each endpoint
await limiter.wait("get_tweet")
tweet = await twitter.fetch_tweet(tweet_id)

await limiter.wait("tweet_replies")
comments = await twitter.fetch_comments(tweet_id)
```

### Adaptive Rate Limiting

```python
limiter = RateLimiter(
    platform="twitter",
    adaptive=True,
    safety_margin=0.1  # Use 90% of limit
)
```

### Distributed Rate Limiting

```python
from moderation_ai.utils import DistributedRateLimiter

limiter = DistributedRateLimiter(
    platform="twitter",
    redis_url="redis://localhost:6379",
    limit=900,
    window=900
)

# Works across multiple instances
await limiter.wait()
comments = await twitter.fetch_comments(tweet_id)
```

## Monitoring Rate Limits

### Track Usage Over Time

```python
from moderation_ai.utils import RateLimitMonitor

monitor = RateLimitMonitor(platform="twitter")

async def with_monitoring(func, *args):
    monitor.track_request()
    result = await func(*args)
    monitor.track_response()
    return result

# Use with monitoring
comments = await with_monitoring(
    twitter.fetch_comments,
    tweet_id
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
        status = twitter.get_rate_limit_status()
        
        if status.remaining < status.limit * 0.1:
            # Send alert
            await send_alert(
                "Twitter rate limit warning",
                f"Only {status.remaining} requests remaining"
            )
        
        await asyncio.sleep(60)  # Check every minute
```

## Rate Limit Optimization

### 1. Prioritize Requests

```python
# High priority: moderation actions
if needs_moderation:
    await twitter.moderate_comment(comment_id, "hide")

# Medium priority: fetch recent comments
await twitter.fetch_comments(tweet_id)

# Low priority: fetch historical data
await twitter.fetch_user_timeline(user_id)
```

### 2. Use Streaming for Real-Time

```python
# Streaming doesn't count against rate limits
stream = await twitter.create_stream()

async for tweet in stream:
    # Process in real-time
    await analyze_tweet(tweet)
```

### 3. Batch Moderation Actions

```python
# Apply moderation in batches
actions = [
    (comment_id1, "hide"),
    (comment_id2, "flag"),
    (comment_id3, "approve")
]

for comment_id, action in actions:
    await twitter.moderate_comment(comment_id, action)
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

### Issue: Inconsistent Rate Limits

**Possible causes**:
- Different endpoints have different limits
- API tier changed
- Header parsing issues

**Solution**:
- Check endpoint-specific limits
- Verify API access level
- Test header parsing

### Issue: Rate Limit Not Resetting

**Possible causes**:
- Wrong reset time calculation
- Timezone issues
- Not updating from headers

**Solution**:
- Parse reset time from headers
- Use UTC timezone
- Update rate limit status after each request

## Related Documentation

- **API Guide**: `./api-guide.md` - API usage
- **Authentication**: `./authentication.md` - Auth setup
- **General Rate Limiting**: `../../docs/api-reference/rate-limiting.md` - Cross-platform strategies

---

**Last Updated**: January 2024
**Status**: Phase 2 - Documentation Complete
