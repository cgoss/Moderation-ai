---
title: Common API Patterns
category: core
related:
  - ./README.md
  - ./rate-limiting.md
  - ../platforms/twitter/api-guide.md
---

# Common API Patterns

## Overview

This document describes common API patterns used across all platform integrations in the Moderation AI library. These patterns ensure consistent behavior, improve code reuse, and simplify multi-platform development.

## Pattern 1: Platform Abstraction

All platforms implement a common interface through `BasePlatform`:

```python
from moderation_ai.platforms import TwitterAPI, RedditAPI, YouTubeAPI

# All platforms have the same interface
platforms = [
    TwitterAPI.from_env(),
    RedditAPI.from_env(),
    YouTubeAPI.from_env()
]

for platform in platforms:
    # Same methods on all platforms
    await platform.authenticate()
    comments = await platform.fetch_comments(post_id)
    result = await platform.moderate_comment(comment_id, "hide")
```

### Base Platform Interface

```python
class BasePlatform(ABC):
    @abstractmethod
    async def authenticate(self) -> bool:
        pass

    @abstractmethod
    async def fetch_posts(self, query: str) -> List[Post]:
        pass

    @abstractmethod
    async def fetch_comments(self, post_id: str) -> List[Comment]:
        pass

    @abstractmethod
    async def moderate_comment(self, comment_id: str, action: str) -> bool:
        pass

    @abstractmethod
    async def track_post(self, post_id: str) -> PostMetadata:
        pass
```

## Pattern 2: Pagination

Most platforms use pagination for large result sets:

### Cursor-Based Pagination (Twitter, Reddit)

```python
from moderation_ai.platforms import TwitterAPI

twitter = TwitterAPI.from_env()

cursor = None
all_comments = []

while True:
    result = await twitter.fetch_comments(
        post_id,
        cursor=cursor,
        limit=100
    )

    all_comments.extend(result.comments)

    if not result.has_more:
        break

    cursor = result.next_cursor
```

### Page-Based Pagination (YouTube, Medium)

```python
from moderation_ai.platforms import YouTubeAPI

youtube = YouTubeAPI.from_env()

page_token = None
all_comments = []

while True:
    result = await youtube.fetch_comments(
        post_id,
        page_token=page_token,
        max_results=100
    )

    all_comments.extend(result.comments)

    if not result.next_page_token:
        break

    page_token = result.next_page_token
```

### Unified Pagination Helper

```python
from moderation_ai.utils import fetch_all_pages

async def get_all_comments(platform, post_id):
    return await fetch_all_pages(
        fetch_func=platform.fetch_comments,
        post_id=post_id,
        limit_per_page=100
    )

all_comments = await get_all_comments(twitter, post_id)
```

## Pattern 3: Caching

Cache frequently accessed data:

### Simple Memory Cache

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
async def get_post_info(post_id):
    return await platform.fetch_post(post_id)
```

### Persistent Cache

```python
from moderation_ai.utils import Cache

cache = Cache(cache_file=".cache.json")

@cache.cached(ttl=3600)  # Cache for 1 hour
async def get_post_info(post_id):
    return await platform.fetch_post(post_id)
```

### Cache Invalidation

```python
from moderation_ai.utils import Cache

cache = Cache()

async def get_post_info(post_id):
    # Check cache first
    cached = await cache.get(f"post:{post_id}")
    if cached:
        return cached

    # Fetch from platform
    post = await platform.fetch_post(post_id)

    # Store in cache
    await cache.set(f"post:{post_id}", post, ttl=3600)

    return post
```

## Pattern 4: Async Parallelism

Process multiple requests concurrently:

### Parallel Comment Fetching

```python
import asyncio
from moderation_ai.platforms import TwitterAPI

twitter = TwitterAPI.from_env()

async def fetch_post_comments(post_id):
    return await twitter.fetch_comments(post_id)

# Fetch comments from multiple posts in parallel
post_ids = ["1", "2", "3", "4", "5"]
results = await asyncio.gather(*[
    fetch_post_comments(post_id) for post_id in post_ids
])
```

### Parallel Multi-Platform Processing

```python
import asyncio
from moderation_ai.platforms import TwitterAPI, RedditAPI, YouTubeAPI

async def process_platform(platform, post_id):
    await platform.authenticate()
    return await platform.fetch_comments(post_id)

# Process multiple platforms in parallel
results = await asyncio.gather(*[
    process_platform(TwitterAPI.from_env(), post_id),
    process_platform(RedditAPI.from_env(), post_id),
    process_platform(YouTubeAPI.from_env(), post_id)
])
```

### Controlled Concurrency

```python
import asyncio
from moderation_ai.utils import AsyncSemaphore

async def fetch_with_semaphore(semaphore, fetch_func, *args):
    async with semaphore:
        return await fetch_func(*args)

# Limit to 5 concurrent requests
semaphore = AsyncSemaphore(5)
post_ids = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

results = await asyncio.gather(*[
    fetch_with_semaphore(
        semaphore,
        twitter.fetch_comments,
        post_id
    )
    for post_id in post_ids
])
```

## Pattern 5: Batching

Process items in batches for efficiency:

### Batch Comment Analysis

```python
from moderation_ai.analysis import SentimentAnalyzer

analyzer = SentimentAnalyzer()
all_comments = await fetch_all_comments(twitter, post_id)

# Process in batches of 100
batch_size = 100
all_results = []

for i in range(0, len(all_comments), batch_size):
    batch = all_comments[i:i + batch_size]
    results = await analyzer.batch_analyze(batch)
    all_results.extend(results)
```

### Batch Moderation Actions

```python
async def moderate_batch(platform, comment_ids, action):
    batch_size = 50
    results = []

    for i in range(0, len(comment_ids), batch_size):
        batch = comment_ids[i:i + batch_size]
        batch_results = await asyncio.gather(*[
            platform.moderate_comment(cid, action)
            for cid in batch
        ])
        results.extend(batch_results)

    return results
```

### Batch Post Fetching

```python
async def fetch_posts_batch(platform, post_ids, batch_size=100):
    all_posts = []

    for i in range(0, len(post_ids), batch_size):
        batch = post_ids[i:i + batch_size]
        batch_posts = await asyncio.gather(*[
            platform.fetch_post(post_id)
            for post_id in batch
        ])
        all_posts.extend(batch_posts)

    return all_posts
```

## Pattern 6: Context Managers

Ensure resource cleanup:

### Platform Session Context

```python
from moderation_ai.platforms import TwitterAPI

async with TwitterAPI.from_env() as twitter:
    await twitter.authenticate()
    comments = await twitter.fetch_comments(post_id)

# Session automatically closed
```

### Rate Limiter Context

```python
from moderation_ai.utils import RateLimiter

async with RateLimiter(platform="twitter", requests_per_minute=300) as limiter:
    # All requests within context respect rate limits
    await limiter.wait()
    comments1 = await twitter.fetch_comments(post_id1)

    await limiter.wait()
    comments2 = await twitter.fetch_comments(post_id2)
```

## Pattern 7: Decorators

Add cross-cutting concerns:

### Retry Decorator

```python
from moderation_ai.utils import retry

@retry(max_retries=3, delay=1)
async def fetch_with_retry(platform, post_id):
    return await platform.fetch_comments(post_id)
```

### Logging Decorator

```python
from moderation_ai.utils import log_api_call

@log_api_call(platform="twitter", endpoint="fetch_comments")
async def fetch_comments_logged(post_id):
    return await twitter.fetch_comments(post_id)
```

### Cache Decorator

```python
from moderation_ai.utils import cached

@cached(ttl=3600)
async def get_post_cached(post_id):
    return await platform.fetch_post(post_id)
```

### Error Handling Decorator

```python
from moderation_ai.utils import handle_errors

@handle_errors(
    exceptions=[RateLimitExceeded],
    handler=lambda e: asyncio.sleep(e.retry_after)
)
async def fetch_with_error_handling(post_id):
    return await twitter.fetch_comments(post_id)
```

## Pattern 8: Data Transformation

Transform platform-specific data to common format:

### Comment Normalization

```python
from moderation_ai.utils import normalize_comment

# Platform-specific comment
twitter_comment = {
    "id": "123",
    "text": "Hello",
    "author_id": "456",
    "created_at": "2024-01-08T10:00:00Z"
}

# Normalize to common format
comment = normalize_comment(twitter_comment, platform="twitter")
# comment.id = "123"
# comment.text = "Hello"
# comment.platform = "twitter"
```

### Post Normalization

```python
from moderation_ai.utils import normalize_post

reddit_post = {
    "id": "abc",
    "title": "Post title",
    "selftext": "Post content",
    "author": "username",
    "created_utc": 1704700800
}

post = normalize_post(reddit_post, platform="reddit")
```

## Pattern 9: Streaming

Handle streaming responses:

### Stream Comments

```python
from moderation_ai.utils import stream_comments

async for comment in stream_comments(twitter, post_id):
    # Process each comment as it arrives
    result = await analyzer.analyze(comment)
    print(f"{comment.id}: {result.sentiment}")
```

### Stream Moderation Actions

```python
from moderation_ai.utils import stream_moderation

async for decision in stream_moderation(
    analyzer,
    comments,
    batch_size=10
):
    # Apply moderation decisions in batches
    if decision.violation_detected:
        await platform.moderate_comment(
            decision.comment_id,
            decision.recommended_action
        )
```

## Pattern 10: Event-Driven Processing

React to events:

### Event Emitter

```python
from moderation_ai.utils import EventEmitter

emitter = EventEmitter()

@emitter.on("comment.created")
async def handle_new_comment(event):
    comment = event.data
    print(f"New comment: {comment.id}")

# Emit event
await emitter.emit("comment.created", {"comment": comment})
```

### Observer Pattern

```python
from moderation_ai.utils import Observable

class CommentObserver:
    def on_comment_created(self, comment):
        print(f"Comment created: {comment.id}")

observable = Observable()
observer = CommentObserver()
observable.subscribe(observer)
```

## Pattern 11: Multi-Tenant Processing

Handle multiple tenants:

### Tenant-Specific Configuration

```python
from moderation_ai.utils import TenantManager

manager = TenantManager()

# Register tenant
await manager.register_tenant(
    tenant_id="tenant1",
    config={
        "twitter": {"api_key": "..."},
        "reddit": {"client_id": "..."}
    }
)

# Get tenant-specific platform
twitter = await manager.get_platform("tenant1", "twitter")
```

### Tenant Isolation

```python
async def process_tenant_comments(tenant_id):
    # Use tenant-specific configuration
    platform = await manager.get_platform(tenant_id, "twitter")

    # Process comments for tenant
    comments = await platform.fetch_comments(post_id)
    results = await analyzer.analyze_batch(comments)

    # Store results with tenant context
    await storage.save_results(tenant_id, results)
```

## Pattern 12: Progress Tracking

Track progress of long-running operations:

### Progress Callback

```python
from moderation_ai.utils import ProgressTracker

tracker = ProgressTracker(total=1000)

async def process_all_comments(comments):
    for i, comment in enumerate(comments):
        await process_comment(comment)

        # Update progress
        tracker.update(1)
        print(f"Progress: {tracker.progress}%")
```

### Progress Bars

```python
from tqdm import tqdm

async def process_with_progress(items):
    with tqdm(total=len(items)) as pbar:
        for item in items:
            await process_item(item)
            pbar.update(1)
```

## Best Practices

### 1. Always Use Async

```python
# Good
comments = await platform.fetch_comments(post_id)

# Bad - blocking
comments = platform.fetch_comments(post_id)
```

### 2. Respect Rate Limits

```python
# Good
limiter = RateLimiter(platform="twitter")
await limiter.wait()
comments = await platform.fetch_comments(post_id)

# Bad - no rate limiting
comments = await platform.fetch_comments(post_id)
```

### 3. Handle Errors

```python
# Good
try:
    comments = await platform.fetch_comments(post_id)
except PlatformError as e:
    logger.error(f"Error: {e}")

# Bad - no error handling
comments = await platform.fetch_comments(post_id)
```

### 4. Use Batch Operations

```python
# Good
results = await analyzer.batch_analyze(comments)

# Acceptable - sequential loop
results = []
for comment in comments:
    result = await analyzer.analyze(comment)
    results.append(result)
```

### 5. Cache When Appropriate

```python
# Good - cache post info
@cached(ttl=3600)
async def get_post(post_id):
    return await platform.fetch_post(post_id)

# Acceptable - no cache for comments
async def get_comments(post_id):
    return await platform.fetch_comments(post_id)
```

## Related Documentation

- **Rate Limiting**: `./rate-limiting.md`
- **Error Handling**: `./error-handling.md`
- **Authentication**: `./authentication.md`

---

**Last Updated**: January 2024
**Status**: Phase 1 - Documentation Phase
