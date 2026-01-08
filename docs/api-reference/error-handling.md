---
title: Error Handling
category: core
related:
  - ./README.md
  - ./authentication.md
  - ./rate-limiting.md
---

# Error Handling

## Overview

The Moderation AI library provides a comprehensive error handling system with standardized exceptions, automatic retry logic, and detailed error reporting. This document describes the error handling patterns used across all platform integrations.

## Exception Hierarchy

```
ModerationAIError (Base)
├── AuthenticationError
│   ├── InvalidCredentialsError
│   ├── TokenExpiredError
│   └── InsufficientPermissionsError
├── RateLimitError
│   ├── RateLimitExceeded
│   └── RateLimitResetError
├── PlatformError
│   ├── PlatformAPIError
│   ├── PostNotFoundError
│   ├── CommentNotFoundError
│   └── ModerationActionFailed
├── AnalysisError
│   ├── AnalyzerNotInitialized
│   └── InvalidAnalysisRequest
└── ConfigurationError
    ├── MissingConfigError
    └── InvalidConfigError
```

## Standard Exceptions

### Base Exception: ModerationAIError

```python
from moderation_ai.utils import ModerationAIError

try:
    comments = await platform.fetch_comments(post_id)
except ModerationAIError as e:
    print(f"Error: {e}")
    print(f"Code: {e.code}")
    print(f"Message: {e.message}")
    print(f"Platform: {e.platform}")
    print(f"Details: {e.details}")
```

### AuthenticationError

Raised when authentication fails:

```python
from moderation_ai.utils import AuthenticationError

try:
    await platform.authenticate()
except AuthenticationError as e:
    if e.code == 401:
        print("Invalid credentials")
    elif e.code == 403:
        print("Insufficient permissions")
```

**Subclasses**:
- `InvalidCredentialsError` - Invalid API key, token, or credentials
- `TokenExpiredError` - Access token has expired
- `InsufficientPermissionsError` - OAuth scopes insufficient

### RateLimitError

Raised when rate limit is exceeded:

```python
from moderation_ai.utils import RateLimitExceeded

try:
    comments = await platform.fetch_comments(post_id)
except RateLimitExceeded as e:
    print(f"Rate limit exceeded")
    print(f"Retry after: {e.retry_after} seconds")
    print(f"Reset at: {e.reset_at}")
```

**Subclasses**:
- `RateLimitExceeded` - Rate limit exceeded
- `RateLimitResetError` - Rate limit window reset needed

### PlatformError

Raised for platform-specific errors:

```python
from moderation_ai.utils import PlatformError

try:
    comments = await platform.fetch_comments(post_id)
except PlatformError as e:
    print(f"Platform error: {e.platform}")
    print(f"Error code: {e.code}")
    print(f"Message: {e.message}")
```

**Subclasses**:
- `PlatformAPIError` - Generic platform API error
- `PostNotFoundError` - Post does not exist or is private
- `CommentNotFoundError` - Comment does not exist
- `ModerationActionFailed` - Moderation action could not be performed

### AnalysisError

Raised during analysis operations:

```python
from moderation_ai.utils import AnalysisError

try:
    result = await analyzer.analyze(comment)
except AnalysisError as e:
    print(f"Analysis error: {e.message}")
```

**Subclasses**:
- `AnalyzerNotInitialized` - Analyzer not properly initialized
- `InvalidAnalysisRequest` - Invalid input for analysis

### ConfigurationError

Raised for configuration issues:

```python
from moderation_ai.utils import ConfigurationError

try:
    platform = TwitterAPI.from_env()
except ConfigurationError as e:
    print(f"Configuration error: {e.message}")
```

**Subclasses**:
- `MissingConfigError` - Required configuration missing
- `InvalidConfigError` - Invalid configuration value

## HTTP Status Codes

| Status Code | Meaning | Exception | Retry |
|-------------|---------|-----------|-------|
| 400 | Bad Request | PlatformAPIError | No |
| 401 | Unauthorized | InvalidCredentialsError | No |
| 403 | Forbidden | InsufficientPermissionsError | No |
| 404 | Not Found | PostNotFoundError | No |
| 429 | Too Many Requests | RateLimitExceeded | Yes |
| 500 | Internal Server Error | PlatformAPIError | Yes |
| 502 | Bad Gateway | PlatformAPIError | Yes |
| 503 | Service Unavailable | PlatformAPIError | Yes |

## Error Response Format

All errors include structured information:

```python
from moderation_ai.utils import PlatformError

try:
    comments = await platform.fetch_comments(post_id)
except PlatformError as e:
    # Error attributes
    print(f"Error: {e}")  # Human-readable message
    print(f"Code: {e.code}")  # Error code
    print(f"Message: {e.message}")  # Detailed message
    print(f"Platform: {e.platform}")  # Platform name
    print(f"Timestamp: {e.timestamp}")  # When error occurred
    print(f"Request ID: {e.request_id}")  # Request identifier

    # Additional details
    if e.details:
        print(f"Details: {e.details}")
```

## Retry Strategies

### Automatic Retry with Exponential Backoff

```python
from moderation_ai.utils import RateLimiter

limiter = RateLimiter(
    platform="twitter",
    max_retries=5,
    base_delay=1,
    max_delay=60,
    exponential_base=2
)

# Automatic retry with backoff
try:
    comments = await platform.fetch_comments(post_id)
except RateLimitExceeded:
    # RateLimiter handles retry automatically
    pass
```

### Manual Retry

```python
import asyncio
from moderation_ai.utils import PlatformError

max_retries = 3
retry_delay = 2

for attempt in range(max_retries):
    try:
        comments = await platform.fetch_comments(post_id)
        break
    except PlatformError as e:
        if e.code in [500, 502, 503] and attempt < max_retries - 1:
            print(f"Retry {attempt + 1}/{max_retries}")
            await asyncio.sleep(retry_delay * (2 ** attempt))
        else:
            raise
```

### Custom Retry Logic

```python
from moderation_ai.utils import is_transient_error

async def with_retry(func, *args, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if is_transient_error(e) and attempt < max_retries - 1:
                delay = 2 ** attempt
                print(f"Retry {attempt + 1}/{max_retries} after {delay}s")
                await asyncio.sleep(delay)
            else:
                raise

# Usage
comments = await with_retry(platform.fetch_comments, post_id)
```

## Error Logging

### Structured Logging

```python
import logging
from moderation_ai.utils import PlatformError

logger = logging.getLogger(__name__)

try:
    comments = await platform.fetch_comments(post_id)
except PlatformError as e:
    logger.error(
        "Platform error occurred",
        extra={
            "platform": e.platform,
            "code": e.code,
            "message": e.message,
            "request_id": e.request_id,
            "post_id": post_id
        }
    )
```

### Error Metrics

```python
from moderation_ai.utils import ErrorMetrics

metrics = ErrorMetrics()

try:
    comments = await platform.fetch_comments(post_id)
except PlatformError as e:
    metrics.record_error(
        platform="twitter",
        error_type=e.__class__.__name__,
        code=e.code
    )
```

## Error Handling Patterns

### Pattern 1: Graceful Degradation

```python
try:
    comments = await platform.fetch_comments(post_id)
except PlatformError as e:
    if e.code == 404:
        logger.warning(f"Post not found: {post_id}")
        return []
    else:
        logger.error(f"Failed to fetch comments: {e}")
        raise
```

### Pattern 2: Fallback Strategy

```python
from moderation_ai.platforms import TwitterAPI, RedditAPI

# Try primary platform, fallback to secondary
try:
    comments = await twitter.fetch_comments(post_id)
except PlatformError:
    try:
        comments = await reddit.fetch_comments(post_id)
    except PlatformError:
        comments = []
```

### Pattern 3: User-Friendly Messages

```python
from moderation_ai.utils import PlatformError, RateLimitExceeded

def handle_platform_error(error):
    if isinstance(error, RateLimitExceeded):
        return "Too many requests. Please try again later."
    elif isinstance(error, PlatformError):
        if error.code == 404:
            return "Post not found or deleted."
        else:
            return f"An error occurred: {error.message}"
    else:
        return "An unexpected error occurred."

try:
    comments = await platform.fetch_comments(post_id)
except Exception as e:
    user_message = handle_platform_error(e)
    print(user_message)
```

### Pattern 4: Error Context Preservation

```python
from moderation_ai.utils import PlatformError

class ModerationContextError(PlatformError):
    def __init__(self, message, context=None, **kwargs):
        super().__init__(message, **kwargs)
        self.context = context or {}

# Usage
try:
    result = await moderate_comment(comment_id, action)
except PlatformError as e:
    raise ModerationContextError(
        "Failed to moderate comment",
        context={
            "comment_id": comment_id,
            "action": action,
            "platform": platform.name
        }
    )
```

## Platform-Specific Error Handling

### Twitter

```python
from moderation_ai.utils import TwitterError

try:
    comments = await twitter.fetch_comments(post_id)
except TwitterError as e:
    if e.code == 327:
        print("You have already retweeted this tweet")
    elif e.code == 34:
        print("Page does not exist")
    else:
        print(f"Twitter error: {e.message}")
```

### Reddit

```python
from moderation_ai.utils import RedditError

try:
    comments = await reddit.fetch_comments(post_id)
except RedditError as e:
    if e.code == "SUBREDDIT_NOT_FOUND":
        print("Subreddit not found")
    elif e.code == "THREAD_NOT_FOUND":
        print("Post not found")
    else:
        print(f"Reddit error: {e.message}")
```

### YouTube

```python
from moderation_ai.utils import YouTubeError

try:
    comments = await youtube.fetch_comments(post_id)
except YouTubeError as e:
    if e.code == "videoNotFound":
        print("Video not found")
    elif e.code == "commentsDisabled":
        print("Comments are disabled on this video")
    else:
        print(f"YouTube error: {e.message}")
```

## Testing Error Handling

### Mock Errors in Tests

```python
import pytest
from moderation_ai.utils import PlatformError
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_fetch_comments_handles_error():
    platform = TwitterAPI.from_env()

    # Mock error response
    with patch.object(
        platform,
        "fetch_comments",
        new_callable=AsyncMock,
        side_effect=PlatformError("Test error", code=500)
    ):
        with pytest.raises(PlatformError):
            await platform.fetch_comments(post_id)
```

### Test Retry Logic

```python
@pytest.mark.asyncio
async def test_retry_on_transient_error():
    call_count = 0

    async def failing_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise PlatformError("Transient error", code=500)
        return "success"

    result = await with_retry(failing_func, max_retries=3)
    assert result == "success"
    assert call_count == 3
```

## Best Practices

### 1. Always Handle Specific Exceptions

```python
# Good
try:
    comments = await platform.fetch_comments(post_id)
except RateLimitExceeded:
    await asyncio.sleep(60)
except PlatformError:
    logger.error("Platform error")

# Bad - catches too broadly
try:
    comments = await platform.fetch_comments(post_id)
except:
    pass
```

### 2. Log Errors with Context

```python
logger.error(
    "Failed to fetch comments",
    extra={
        "platform": platform.name,
        "post_id": post_id,
        "error_code": e.code,
        "error_message": e.message
    }
)
```

### 3. Provide User-Friendly Messages

```python
try:
    comments = await platform.fetch_comments(post_id)
except RateLimitExceeded:
    print("Please wait a moment and try again.")
except PlatformError:
    print("An error occurred. Please try again.")
```

### 4. Retry Transient Errors

```python
transient_codes = [429, 500, 502, 503]

if e.code in transient_codes:
    await asyncio.sleep(delay)
    # Retry
```

### 5. Preserve Error Context

```python
raise ModerationContextError(
    "Failed to moderate comment",
    context={"comment_id": comment_id, "action": action}
)
```

## Troubleshooting

### Issue: Rate limit errors persist

**Possible causes**:
- Rate limiter not configured correctly
- Multiple instances running
- Platform changed rate limits

**Resolution**:
- Verify RateLimiter configuration
- Ensure single instance used
- Check platform documentation

### Issue: Authentication errors on valid credentials

**Possible causes**:
- Token expired
- Wrong OAuth scopes
- App not approved

**Resolution**:
- Refresh token
- Verify OAuth scopes
- Check app status

### Issue: 404 errors for valid post IDs

**Possible causes**:
- Post deleted or private
- Wrong post ID format
- Permissions issue

**Resolution**:
- Verify post exists and is public
- Check post ID format
- Verify permissions

## Related Documentation

- **Authentication**: `./authentication.md`
- **Rate Limiting**: `./rate-limiting.md`
- **Platform-specific errors**: `../platforms/{platform}/api-guide.md`

---

**Last Updated**: January 2024
**Status**: Phase 1 - Documentation Phase
