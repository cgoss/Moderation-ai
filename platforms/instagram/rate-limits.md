---
title: Instagram Rate Limits
category: platform
platform: instagram
related:
  - ../README.md
  - ./api-guide.md
  - ./authentication.md
---

# Instagram Rate Limits

## Overview

Instagram enforces strict rate limits across all API endpoints. Understanding and respecting these limits is crucial for sustainable comment moderation operations.

## Rate Limit Structure

Instagram uses time-windowed rate limiting:
- **Time Windows**: Hourly and daily limits
- **Endpoint Specific**: Different limits for different endpoints
- **Account Tiers**: Higher limits for approved business accounts
- **Dynamic Adjustments**: Limits can change based on system load

## Core Rate Limits

### Fetch Operations

| Endpoint | Rate Limit | Time Window | Notes |
|----------|-------------|--------------|-------|
| **Media** | 200 requests/hour | 1 hour | Get media by ID, hashtag, or user |
| **Comments** | 5,000 requests/hour | 1 hour | Fetch comments on media |
| **User Timeline** | 5,000 requests/hour | 1 hour | Get user's recent media |
| **Search** | 30 requests/hour | 1 hour | Hashtag and media search |

### Write Operations

| Endpoint | Rate Limit | Time Window | Notes |
|----------|-------------|--------------|-------|
| **Hide Comment** | 5,000 requests/hour | 1 hour | Moderate comments (page owner) |
| **Delete Comment** | 200 requests/hour | 1 hour | Delete own comments |
| **Reply to Comment** | 5,000 requests/hour | 1 hour | Reply to comments |
| **Report Comment** | 1,000 requests/hour | 1 hour | Report comments to Instagram |
| **Moderation Review** | 1,000 requests/hour | 1 hour | Internal review queue |

### Interactive Operations

| Endpoint | Rate Limit | Time Window | Notes |
|----------|-------------|--------------|-------|
| **Post Likes** | 500 requests/hour | 1 hour | Like media posts |
| **Follow User** | 60 requests/hour | 1 hour | Follow users |
| **Get User Info** | 200 requests/hour | 1 hour | Fetch user profile data |
| **Get Media Info** | 200 requests/hour | 1 hour | Get detailed media data |

## Limit Headers

Instagram includes rate limit information in HTTP response headers:

```http
HTTP/1.1 200 OK
x-ratelimit-limit: 5000
x-ratelimit-remaining: 4231
x-ratelimit-reset: 1372674800
```

### Header Fields

- **x-ratelimit-limit**: Total requests allowed in time window
- **x-ratelimit-remaining**: Requests remaining in current window
- **x-ratelimit-reset**: Unix timestamp when window resets
- **x-app-usage**: App-specific usage data (sometimes included)

## Calculating Reset Time

```python
from datetime import datetime, timedelta, timezone

def calculate_reset_timestamp(reset_header: str) -> datetime:
    """
    Convert Unix timestamp to datetime.
    """
    try:
        reset_ts = datetime.fromtimestamp(int(reset_header), tz=timezone.utc)
        return reset_ts
    except (ValueError, TypeError):
        return datetime.utcnow()
    
def time_until_reset(reset_header: str) -> timedelta:
    """
    Calculate time remaining until rate limit resets.
    """
    reset_ts = calculate_reset_timestamp(reset_header)
    now = datetime.utcnow(timezone.utc)
    
    if reset_ts > now:
        return reset_ts - now
    else:
        # Window has already reset
        return timedelta(hours=1)

# Example
reset_time = time_until_reset("1372674800")
print(f"Time until reset: {reset_time}")
```

## Rate Limiting Strategies

### 1. Exponential Backoff

Implement increasing delays when hitting rate limits:

```python
import asyncio
import random

async def fetch_with_backoff(instagram, endpoint, max_retries=5):
    """
    Fetch with exponential backoff on rate limit errors.
    """
    for attempt in range(max_retries):
        try:
            response = await endpoint()
            return response
        except RateLimitError as e:
            # Calculate backoff time
            backoff_seconds = 2 ** attempt + random.uniform(0, 1)
            
            print(f"Rate limited, waiting {backoff_seconds}s")
            await asyncio.sleep(backoff_seconds)
    
    raise Exception("Max retries exceeded")
```

### 2. Request Queuing

Queue requests to avoid bursting:

```python
from asyncio import Queue
import asyncio

class InstagramRateLimiter:
    """
    Rate limiter using a queue system.
    """
    
    def __init__(self, requests_per_hour=5000):
        self.queue = Queue(maxsize=100)
        self.requests_per_hour = requests_per_hour
        self.current_requests = 0
        self.reset_time = None
    
    async def acquire(self):
        """
        Wait for rate limit clearance.
        """
        while True:
            now = datetime.utcnow()
            hour_ago = now - timedelta(hours=1)
            
            # Reset counter if past hour
            if self.reset_time and self.reset_time < hour_ago:
                self.current_requests = 0
                self.reset_time = None
            
            # Check if under limit
            if self.current_requests < self.requests_per_hour:
                self.current_requests += 1
                return True
            
            # Wait for next hour or for space in queue
            wait_time = min(3600, 60)  # Up to 1 hour, but check every minute
            
            print(f"Rate limit reached, waiting {wait_time}s")
            await asyncio.sleep(wait_time)
```

### 3. Distributed Throttling

For multi-account or distributed systems:

```python
import hashlib
from collections import defaultdict

class DistributedRateLimiter:
    """
    Distribute rate limits across multiple accounts.
    """
    
    def __init__(self, accounts, total_limit=5000):
        self.accounts = accounts
        self.total_limit = total_limit
        self.account_usage = defaultdict(int)
        self.lock = asyncio.Lock()
    
    async def get_account(self, resource_id: str) -> str:
        """
        Get account with available capacity.
        """
        async with self.lock:
            for account_id in self.accounts:
                usage = self.account_usage[account_id]
                
                # Hash-based distribution
                hash_value = int(hashlib.sha256(resource_id.encode()).hexdigest(), 16)
                index = hash_value % len(self.accounts)
                
                if self.accounts[index] == account_id:
                    return account_id
                
                # Simple load balancing
                if usage < self.total_limit:
                    self.account_usage[account_id] += 1
                    return account_id
            
            return self.accounts[0]
    
    async def record_usage(self, account_id: str):
        """
        Record API usage for an account.
        """
        async with self.lock:
            self.account_usage[account_id] += 1
```

### 4. Caching Strategy

Reduce API calls by caching responses:

```python
from datetime import datetime, timedelta
from functools import lru_cache

# Simple in-memory cache
@lru_cache(maxsize=100)
async def get_media_cached(instagram, media_id: str):
    """
    Get media with caching.
    """
    try:
        return await instagram.fetch_media(media_id)
    except Exception as e:
        # On error, don't cache
        raise e

# Time-based cache (more sophisticated)
class TimeBasedCache:
    """
    Cache responses with expiry.
    """
    
    def __init__(self, ttl=3600):  # 1 hour TTL
        self.cache = {}
        self.ttl = ttl
    
    async def get(self, key: str):
        """
        Get cached value if available and fresh.
        """
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        now = datetime.utcnow()
        
        # Check if expired
        if now - entry['timestamp'] > timedelta(seconds=self.ttl):
            del self.cache[key]
            return None
        
        return entry['value']
    
    async def set(self, key: str, value):
        """
        Set value in cache.
        """
        self.cache[key] = {
            'value': value,
            'timestamp': datetime.utcnow()
        }
    
    async def clear(self, key: str = None):
        """
        Clear specific or all cache entries.
        """
        if key:
            del self.cache[key]
        else:
            self.cache.clear()
```

## Platform-Specific Limits

### Comment-Specific Limits

Comments have specific considerations:
- **Fetch Limits**: 5,000/hour applies to comment fetching
- **Pagination**: Use cursor-based pagination efficiently
- **Batch Processing**: Process comments in batches of 25-50
- **Hidden Comments**: Hidden comments don't count toward fetch limits
- **Comment Depth**: No hard limit on reply depth

### Media-Specific Limits

Media fetching has different limits:
- **Single Media**: 200/hour
- **Multiple Media**: 50/hour (batch fetching)
- **User Media**: 5,000/hour (fetching from user profile)
- **Search**: 30/hour (hashtag search)

### Account Tier Limits

| Account Type | Hourly Limit | Daily Limit | Notes |
|--------------|-------------|-------------|-------|
| **Personal** | 200/hour | 5,000/day | Basic usage |
| **Creator** | 500/hour | 12,500/day | Content creators |
| **Business** | 5,000/hour | 120,000/day | Approved businesses |
| **Enterprise** | Custom | Custom | Contact sales |

## Best Practices

### 1. Monitor Rate Limits

```python
from moderation_ai.utils import get_global_rate_limiter

async def safe_api_call(instagram, endpoint, *args, **kwargs):
    """
    Make API call with rate limit protection.
    """
    limiter = get_global_rate_limiter()
    
    # Check and acquire rate limit token
    platform = "instagram"
    await limiter.wait_for_token(platform)
    
    try:
        # Make API call
        result = await endpoint(*args, **kwargs)
        return result
    except RateLimitError as e:
        # Log rate limit hit
        print(f"Rate limit hit: {e}")
        raise
```

### 2. Graceful Degradation

```python
import asyncio
from datetime import datetime, timedelta

class InstagramRateMonitor:
    """
    Monitor and adapt to rate limits.
    """
    
    def __init__(self):
        self.request_count = 0
        self.rate_limit_hits = 0
        self.adaptive_delay = 0
        self.window_start = datetime.utcnow()
    
    async def make_request(self, api_call):
        """
        Make request with adaptive rate limiting.
        """
        # Check if we're hitting limits frequently
        if self.rate_limit_hits > 5:
            # Increase delay
            self.adaptive_delay = min(self.adaptive_delay * 1.5, 10)
        else:
            # Gradually reduce delay
            self.adaptive_delay = max(self.adaptive_delay * 0.9, 1)
        
        # Wait before request
        if self.adaptive_delay > 0:
            await asyncio.sleep(self.adaptive_delay)
        
        try:
            result = await api_call()
            self.request_count += 1
            return result
        except RateLimitError:
            self.rate_limit_hits += 1
            
            # Check if we need to reset window
            time_in_window = datetime.utcnow() - self.window_start
            if time_in_window > timedelta(minutes=5):
                # Reset for new window
                self.request_count = 0
                self.rate_limit_hits = 0
                self.window_start = datetime.utcnow()
        
        raise
```

### 3. Prioritize Critical Operations

```python
class PriorityQueue:
    """
    Queue API calls by priority.
    """
    
    def __init__(self):
        from asyncio import PriorityQueue
        self.queue = PriorityQueue()
    
    async def enqueue(self, priority, api_call):
        """
        Add API call to queue with priority.
        """
        await self.queue.put((priority, api_call))
    
    async def process(self):
        """
        Process queue in priority order.
        """
        while True:
            priority, api_call = await self.queue.get()
            await api_call()
```

## Error Handling

### Rate Limit Error Response

```python
from moderation_ai.utils import RateLimitError

async def handle_rate_limit(error):
    """
    Handle 429 Too Many Requests error.
    """
    print(f"Rate limit error: {error}")
    
    # Extract rate limit info from error
    retry_after = getattr(error, 'retry_after', None)
    limit = getattr(error, 'limit', None)
    remaining = getattr(error, 'remaining', None)
    
    print(f"  Retry after: {retry_after}s")
    print(f"  Limit: {limit}")
    print(f"  Remaining: {remaining}")
    
    # Calculate when to retry
    if retry_after:
        await asyncio.sleep(retry_after)
    
    # Retry the request
    return True
```

## Troubleshooting

### Issue: Consistent 429 Errors

**Symptom**: Continuously hitting rate limits

**Solutions**:
1. Implement request queuing
2. Add exponential backoff
3. Use caching to reduce redundant calls
4. Check if multiple instances are running
5. Verify you're using the correct API tier

### Issue: Sudden Rate Limit Changes

**Symptom**: Rate limits change unexpectedly

**Solutions**:
1. Monitor x-ratelimit-limit header
2. Dynamically adjust request rates
3. Implement adaptive throttling
4. Stay within conservative limits (75% of reported max)

### Issue: Long Wait Times

**Symptom**: Waiting too long between requests

**Solutions**:
1. Verify your time zone handling
2. Check if you're hitting hourly vs daily limits
3. Consider upgrading account tier
4. Optimize API calls to reduce frequency

## Related Documentation

- **API Guide**: `./api-guide.md` - API usage patterns
- **Authentication**: `./authentication.md` - Auth setup
- **Platform Overview**: `../README.md` - Capabilities

## Platform Status

| Status | Value |
|---------|-------|
| **Last Updated** | January 2024 |
| **API Version** | v18.0+ |
| **Documentation Version** | 1.0 |
| **Implementation Status** | Phase 4 - In Progress |

---

**Platform**: Instagram
**Documentation Version**: 1.0
**Status**: Phase 4 - Documentation In Progress
