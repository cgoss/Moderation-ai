---
title: YouTube Rate Limits
category: platform
platform: youtube
related:
  - ./README.md
  - ./api-guide.md
  - ../../docs/api-reference/rate-limiting.md
---

# YouTube Rate Limits

## Overview

YouTube Data API v3 uses a quota-based rate limiting system. Daily quota resets at midnight Pacific Time (PT). Different operations consume different quota amounts.

## Quota System

### Daily Quota

| Operation | Quota Cost | Notes |
|-----------|------------|-------|
| Video Search | 100 | Per day |
| Comment Threads List | 100 | Per day |
| Comment Thread Replies | 1 per reply | 50 per day |
| Delete Comment | 1 per comment | 100 per day |
| Update Comment | 1 per comment | 100 per day |

### Quota Reset

- **Reset Time**: Midnight Pacific Time (PT)
- **Timezone**: UTC-8 (Pacific)
- **Behavior**: All quotas reset simultaneously
- **Incremental**: New daily quota begins at midnight

## Request Costs

### Read Operations

| Operation | Cost | Description |
|-----------|------|-------------|
| Get Video | 1 | Retrieve video metadata |
| Search Videos | 100 | Search request |
| List Comments | 100 | List comment threads |
| Get Comment Thread | 1 | Get thread with replies |
| Get Comment Replies | 1 per reply | Get nested replies |

### Write Operations

| Operation | Cost | Description |
|-----------|------|-------------|
| Insert Comment | 1 | Post new comment |
| Update Comment | 1 | Edit existing comment |
| Delete Comment | 1 | Remove comment |

## Quota Monitoring

### Check Quota Status

```python
from moderation_ai.platforms import YouTubeAPI

youtube = YouTubeAPI.from_env()

# Get quota information
quota = await youtube.get_quota_status()

print(f"Quota used: {quota.quota_used}")
print(f"Quota remaining: {quota.quota_remaining}")
print(f"Resets at: {quota.reset_time}")
```

### Quota Status Fields

```python
{
    "quota_used": 1500,
    "quota_limit": 10000,
    "quota_remaining": 8500,
    "reset_time": "2024-01-09T08:00:00.000Z",
    "seconds_until_reset": 3600
}
```

## Rate Limiting Strategies

### 1. Daily Quota Monitoring

```python
from moderation_ai.utils import RateLimiter

limiter = RateLimiter(
    platform="youtube",
    algorithm="daily_quota",
    limit=10000
)

await limiter.wait()
videos = await youtube.search_videos(query)
```

### 2. Request Cost Tracking

```python
async def track_quota_usage():
    youtube = YouTubeAPI.from_env()
    
    quota_used = 0
    quota_limit = 10000
    
    while quota_used < quota_limit:
        # Check if next request would exceed quota
        if quota_used + 100 > quota_limit:
            print(f"Approaching quota limit ({quota_used}/10000)")
            await asyncio.sleep(3600)  # Wait for next day
            quota_used = 0  # Reset
        else:
            # Make request
            videos = await youtube.search_videos(query)
            quota_used += 100
```

### 3. Exponential Backoff

```python
import asyncio
from moderation_ai.utils import QuotaExceeded

max_retries = 5
base_delay = 60  # seconds

for attempt in range(max_retries):
    try:
        comments = await youtube.fetch_comments(video_id)
        break
    except QuotaExceeded as e:
        if attempt < max_retries - 1:
            delay = base_delay * (2 ** attempt)
            print(f"Quota exceeded, waiting {delay}s...")
            await asyncio.sleep(delay)
        else:
            raise
```

## Best Practices

### 1. Check Quota Before Requests

```python
status = youtube.get_quota_status()

if status.quota_remaining < 100:
    print("Warning: Approaching quota limit")
    await asyncio.sleep(3600)  # Wait for reset
```

### 2. Use Batch Operations

```python
# Good - batch fetch
video_ids = ["1", "2", "3", "4", "5"]
videos = await youtube.fetch_videos(video_ids)

# Bad - individual fetches
for video_id in video_ids:
    video = await youtube.fetch_video(video_id)
```

### 3. Implement Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
async def get_video_cached(video_id):
    return await youtube.fetch_video(video_id)
```

### 4. Use Parallel Requests

```python
import asyncio

# Good - parallel fetch
video_ids = ["1", "2", "3", "4", "5"]
videos = await asyncio.gather(*[
    youtube.fetch_video(video_id)
    for video_id in video_ids
])
```

### 5. Monitor Quota Usage

```python
async def monitor_quota():
    youtube = YouTubeAPI.from_env()
    
    while True:
        status = youtube.get_quota_status()
        
        if status.quota_remaining < status.quota_limit * 0.1:
            # Alert when approaching limit
            print(f"Warning: {status.quota_remaining} remaining")
        
        await asyncio.sleep(60)  # Check every minute
```

## Rate Limit Errors

### 403 Quota Exceeded

```python
from moderation_ai.utils import QuotaExceeded

try:
    comments = await youtube.fetch_comments(video_id)
except QuotaExceeded as e:
    print(f"Quota exceeded")
    print(f"Reset time: {e.reset_time}")
    print(f"Time until reset: {e.seconds_until_reset}")
```

### 401 Invalid Credentials

```python
from moderation_ai.utils import AuthenticationError

try:
    await youtube.authenticate()
except AuthenticationError as e:
    print(f"Invalid credentials: {e.message}")
```

## Related Documentation

- **API Guide**: `./api-guide.md` - API usage
- **Authentication**: `./authentication.md` - Auth setup
- **General Rate Limiting**: `../../docs/api-reference/rate-limiting.md` - Cross-platform strategies

---

**Last Updated**: January 2024
**Status**: Phase 2 - Documentation Complete
