# TikTok Rate Limits

## Overview

TikTok API has specific rate limiting policies that must be respected to avoid being blocked. This guide details the rate limits and provides strategies for managing API calls efficiently.

## Rate Limit Structure

TikTok API enforces rate limits at multiple levels:

### Application Level
- Limit: 1,000 requests per hour per application
- Reset: Hourly

### Endpoint Level
Different endpoints have specific limits:

| Endpoint | Requests/Hour | Requests/Minute |
|----------|----------------|-----------------|
| `/user/info/` | 100 | 10 |
| `/video/list/` | 50 | 5 |
| `/video/query/` | 200 | 20 |
| `/video/comment/list/` | 100 | 10 |
| `/video/comment/create/` | 50 | 5 |
| `/video/comment/delete/` | 100 | 10 |
| `/video/comment/pin/` | 50 | 5 |

## Rate Limit Headers

TikTok returns rate limit information in response headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1234567890
```

## Handling Rate Limits

### 1. Detect Rate Limits

```python
import time
from typing import Optional
import requests

class RateLimiter:
    def __init__(self):
        self.last_request_time = 0
        self.min_interval = 2
        self.rate_limits = {}
    
    def check_rate_limit(self, response: requests.Response) -> bool:
        """Check if response indicates rate limit"""
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited. Retry after {retry_after} seconds")
            time.sleep(retry_after)
            return False
        return True
    
    def get_rate_limit_info(self, response: requests.Response) -> dict:
        """Extract rate limit information from headers"""
        return {
            'limit': response.headers.get('X-RateLimit-Limit'),
            'remaining': response.headers.get('X-RateLimit-Remaining'),
            'reset': response.headers.get('X-RateLimit-Reset')
        }
```

### 2. Implement Backoff Strategy

```python
import random

def make_request_with_backoff(url: str, headers: dict, max_retries: int = 3):
    """Make request with exponential backoff"""
    base_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 429:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limited. Waiting {delay:.2f} seconds...")
                time.sleep(delay)
                continue
            
            response.raise_for_status()
            return response
        
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
    
    raise Exception("Max retries exceeded")
```

### 3. Request Throttling

```python
class RequestThrottler:
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
    
    def wait_if_needed(self):
        """Wait if we've exceeded the rate limit"""
        now = time.time()
        
        self.request_times = [
            t for t in self.request_times 
            if now - t < 60
        ]
        
        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                print(f"Rate limit reached. Waiting {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
        
        self.request_times.append(now)
    
    def make_request(self, url: str, headers: dict) -> requests.Response:
        """Make throttled request"""
        self.wait_if_needed()
        response = requests.get(url, headers=headers)
        return response
```

## Best Practices

### 1. Batch Requests

Group related operations to minimize API calls:

```python
def fetch_videos_batch(video_ids: list, access_token: str):
    """Fetch multiple videos efficiently"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    videos = []
    for i in range(0, len(video_ids), 20):
        batch = video_ids[i:i+20]
        url = f"https://open.tiktokapis.com/v2/video/query/?video_ids={','.join(batch)}"
        response = make_request_with_backoff(url, headers)
        videos.extend(response.json()['data']['videos'])
        
        time.sleep(1)
    
    return videos
```

### 2. Cache Responses

Cache API responses to reduce redundant calls:

```python
import json
from datetime import datetime, timedelta
import hashlib

class APICache:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_duration = timedelta(minutes=30)
    
    def get_cache_key(self, url: str, params: dict = None) -> str:
        """Generate cache key from URL and params"""
        key_data = url + json.dumps(params or {}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, url: str, params: dict = None) -> Optional[dict]:
        """Get cached response if available and not expired"""
        cache_key = self.get_cache_key(url, params)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        with open(cache_file, 'r') as f:
            cached_data = json.load(f)
        
        cached_at = datetime.fromisoformat(cached_data['cached_at'])
        if datetime.now() - cached_at > self.cache_duration:
            return None
        
        return cached_data['data']
    
    def set(self, url: str, data: dict, params: dict = None):
        """Cache response"""
        cache_key = self.get_cache_key(url, params)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        cached_data = {
            'cached_at': datetime.now().isoformat(),
            'data': data
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cached_data, f)
```

### 3. Use Cache with API Client

```python
class CachedTikTokClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.cache = APICache()
        self.throttler = RequestThrottler(requests_per_minute=10)
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def get_video(self, video_id: str, use_cache: bool = True) -> dict:
        """Get video with caching and throttling"""
        url = f"https://open.tiktokapis.com/v2/video/query/?video_ids={video_id}"
        
        if use_cache:
            cached = self.cache.get(url)
            if cached:
                print("Using cached response")
                return cached
        
        response = self.throttler.make_request(url, self.headers)
        data = response.json()['data']
        
        if use_cache:
            self.cache.set(url, data)
        
        return data
```

### 4. Monitor Usage

Track API usage to stay within limits:

```python
class APIUsageMonitor:
    def __init__(self):
        self.request_count = 0
        self.start_time = time.time()
        self.endpoint_counts = {}
    
    def record_request(self, endpoint: str):
        """Record an API request"""
        self.request_count += 1
        
        if endpoint not in self.endpoint_counts:
            self.endpoint_counts[endpoint] = 0
        self.endpoint_counts[endpoint] += 1
    
    def get_stats(self) -> dict:
        """Get usage statistics"""
        elapsed = time.time() - self.start_time
        requests_per_hour = (self.request_count / elapsed) * 3600
        
        return {
            'total_requests': self.request_count,
            'requests_per_hour': requests_per_hour,
            'endpoint_breakdown': self.endpoint_counts,
            'elapsed_time': elapsed
        }
    
    def print_stats(self):
        """Print usage statistics"""
        stats = self.get_stats()
        print("API Usage Statistics:")
        print(f"  Total Requests: {stats['total_requests']}")
        print(f"  Requests/Hour: {stats['requests_per_hour']:.2f}")
        print("  Endpoint Breakdown:")
        for endpoint, count in stats['endpoint_breakdown'].items():
            print(f"    {endpoint}: {count}")
```

## Configuration

Configure rate limiting in your application:

```python
# config.py
RATE_LIMIT_CONFIG = {
    'requests_per_minute': 10,
    'requests_per_hour': 1000,
    'max_retries': 3,
    'backoff_base_delay': 2,
    'cache_duration_minutes': 30
}
```

## Error Handling

Handle rate limit errors gracefully:

```python
def safe_api_call(func):
    """Decorator for safe API calls with rate limiting"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("Rate limit exceeded. Please try again later.")
                return None
            else:
                raise
        except Exception as e:
            print(f"API call failed: {e}")
            return None
    return wrapper
```

## Testing

Test your rate limiting implementation:

```python
def test_rate_limiting():
    """Test rate limiting functionality"""
    throttler = RequestThrottler(requests_per_minute=10)
    
    for i in range(15):
        print(f"Making request {i + 1}")
        throttler.wait_if_needed()
        time.sleep(0.1)
    
    print("Rate limiting test complete")
```

## Summary

1. **Respect rate limits** - Stay within documented limits
2. **Implement backoff** - Use exponential backoff for retries
3. **Cache responses** - Reduce redundant API calls
4. **Monitor usage** - Track API usage patterns
5. **Prioritize requests** - Handle important requests first
6. **Handle errors** - Gracefully handle rate limit errors

## Advanced Strategies

### Priority Queue

Use a priority queue for important requests:

```python
import queue
from enum import Enum

class RequestPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class PriorityRateLimiter:
    def __init__(self):
        self.queue = queue.PriorityQueue()
        self.current_rate = 0
        self.max_rate = 10
    
    def add_request(self, url: str, priority: RequestPriority, callback: callable):
        """Add request to queue with priority"""
        self.queue.put((priority.value, url, callback))
    
    def process_queue(self):
        """Process queued requests respecting rate limits"""
        while not self.queue.empty():
            if self.current_rate >= self.max_rate:
                time.sleep(60)
                self.current_rate = 0
            
            priority, url, callback = self.queue.get()
            callback(url)
            self.current_rate += 1
```

By following these practices, you can ensure reliable operation of the Moderation Bot while respecting TikTok's API rate limits.
