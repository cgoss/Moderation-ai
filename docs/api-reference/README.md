---
title: API Reference Index
category: core
related:
  - ../llm-context-guide.md
  - ../standards-and-metrics.md
  - ../comment-analysis/README.md
---

# API Reference

## Overview

This section provides unified API documentation for the Moderation AI system. All platforms follow a consistent interface pattern, making it easy to work with multiple social media platforms using the same code patterns.

## Platform Coverage

| Platform | Status | API Type | Primary Auth Method |
|----------|--------|----------|---------------------|
| Twitter/X | Phase 2 docs, Phase 5 code | REST API v2 | OAuth 2.0 Bearer Token |
| Reddit | Phase 2 docs, Phase 5 code | REST API | OAuth 2.0 Authorization Code |
| YouTube | Phase 2 docs, Phase 5 code | Data API v3 | OAuth 2.0 / API Key |
| Instagram | Phase 4 docs, Phase 6 code | Graph API | OAuth 2.0 |
| Medium | Phase 4 docs, Phase 6 code | REST API | OAuth 2.0 / API Key |
| TikTok | Phase 4 docs, Phase 6 code | REST API | OAuth 2.0 |

## Unified Platform Interface

All platform integrations implement the `BasePlatform` abstract class, ensuring consistent API patterns across platforms:

```python
from moderation_ai.platforms import TwitterAPI, RedditAPI

# All platforms have the same interface
twitter = TwitterAPI(credentials)
reddit = RedditAPI(credentials)

async def process_platform(platform, post_id):
    # These methods exist on ALL platforms
    comments = await platform.fetch_comments(post_id)
    for comment in comments:
        decision = await platform.moderate_comment(comment.id, "hide")
```

## Common API Methods

| Method | Purpose | Async |
|--------|---------|-------|
| `authenticate()` | Validate credentials | Yes |
| `fetch_posts(query)` | Retrieve posts | Yes |
| `fetch_comments(post_id)` | Get comments for post | Yes |
| `post_comment(post_id, text)` | Create comment | Yes |
| `moderate_comment(comment_id, action)` | Apply moderation action | Yes |
| `track_post(post_id)` | Enable comment tracking | Yes |

## Common Data Models

### Comment
```python
class Comment:
    id: str
    post_id: str
    author_id: str
    author_username: str
    text: str
    created_at: datetime
    platform: str
    metadata: Dict[str, Any]
```

### Post
```python
class Post:
    id: str
    author_id: str
    author_username: str
    text: str
    media_urls: List[str]
    created_at: datetime
    platform: str
    metadata: Dict[str, Any]
```

### ModerationAction
```python
class ModerationAction(Enum):
    APPROVE = "approve"
    FLAG = "flag"
    HIDE = "hide"
    REMOVE = "remove"
```

## Cross-Platform Patterns

### 1. Authentication Pattern
All platforms use the `AuthManager` utility for credential management:

```python
from moderation_ai.utils import AuthManager

auth = AuthManager()
credentials = await auth.get_credentials("twitter")
```

### 2. Rate Limiting Pattern
All platforms use the `RateLimiter` utility:

```python
from moderation_ai.utils import RateLimiter

limiter = RateLimiter(platform="twitter", requests_per_minute=300)
await limiter.wait()  # Automatically respects rate limits
```

### 3. Error Handling Pattern
All platforms use standardized exceptions:

```python
from moderation_ai.utils import PlatformAPIError, RateLimitExceeded

try:
    comments = await platform.fetch_comments(post_id)
except RateLimitExceeded:
    # Handle rate limit
except PlatformAPIError as e:
    # Handle platform-specific error
```

### 4. Batch Processing Pattern
All platforms support batch operations:

```python
# Batch comment analysis
comments = await platform.fetch_comments(post_id)
results = await analyzer.batch_analyze(comments)

# Batch moderation
for result in results:
    if result.violation_detected:
        await platform.moderate_comment(
            result.comment_id,
            result.recommended_action
        )
```

## Documentation Structure

This API reference is organized into the following sections:

### Core API Concepts

1. **Authentication** (`authentication.md`)
   - Cross-platform authentication patterns
   - OAuth 2.0 implementation details
   - Credential management strategies

2. **Rate Limiting** (`rate-limiting.md`)
   - Platform-specific rate limits
   - Backoff strategies
   - Batch optimization techniques

3. **Error Handling** (`error-handling.md`)
   - Exception hierarchy
   - Error codes and meanings
   - Retry strategies

4. **Webhooks** (`webhooks.md`)
   - Webhook event patterns
   - Event payload structures
   - Webhook security

5. **Common Patterns** (`common-patterns.md`)
   - Pagination patterns
   - Caching strategies
   - Async operation patterns

## Platform-Specific Guides

For platform-specific API details, see:
- `../platforms/twitter/api-guide.md`
- `../platforms/reddit/api-guide.md`
- `../platforms/youtube/api-guide.md`
- `../platforms/instagram/api-guide.md`
- `../platforms/medium/api-guide.md`
- `../platforms/tiktok/api-guide.md`

## Quick Start Examples

### Example 1: Basic Comment Fetching

```python
from moderation_ai.platforms import TwitterAPI

# Initialize platform
twitter = TwitterAPI.from_env()

# Fetch comments from a post
comments = await twitter.fetch_comments("1234567890")

for comment in comments:
    print(f"{comment.author_username}: {comment.text}")
```

### Example 2: Cross-Platform Analysis

```python
from moderation_ai.platforms import TwitterAPI, RedditAPI
from moderation_ai.analysis import SentimentAnalyzer

# Initialize platforms
platforms = [
    TwitterAPI.from_env(),
    RedditAPI.from_env()
]

# Initialize analyzer
analyzer = SentimentAnalyzer()

# Analyze comments from multiple platforms
for platform in platforms:
    comments = await platform.fetch_comments(some_post_id)
    results = analyzer.batch_analyze(comments)
    
    for result in results:
        print(f"{result.comment_id}: {result.sentiment}")
```

### Example 3: Moderation Workflow

```python
from moderation_ai.platforms import RedditAPI
from moderation_ai.core import StandardsEngine

# Initialize components
reddit = RedditAPI.from_env()
standards = StandardsEngine()

# Fetch and analyze comments
comments = await reddit.fetch_comments(post_id)
for comment in comments:
    # Check against standards
    decision = standards.validate(comment.text)
    
    # Apply moderation action
    if decision.action != "approve":
        await reddit.moderate_comment(
            comment.id,
            decision.action
        )
```

## Configuration

### Environment Variables
```bash
# Twitter
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_BEARER_TOKEN=your_token

# Reddit
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=your_user_agent

# YouTube
YOUTUBE_API_KEY=your_key

# Instagram
INSTAGRAM_CLIENT_ID=your_client_id
INSTAGRAM_CLIENT_SECRET=your_secret

# Medium
MEDIUM_TOKEN=your_token

# TikTok
TIKTOK_CLIENT_KEY=your_key
TIKTOK_CLIENT_SECRET=your_secret
```

### Configuration File
```python
# config.py
from moderation_ai.core import Config

config = Config.from_file("config.json")
```

## Performance Considerations

| Operation | Target Performance | Notes |
|-----------|-------------------|-------|
| Authentication | < 1s | One-time per session |
| Fetch comments (single post) | < 2s | Depends on comment count |
| Batch fetch (100 posts) | < 30s | Parallel requests |
| Comment analysis | < 500ms/comment | Single comment |
| Batch analysis (100 comments) | < 50s | Parallel processing |
| Moderation action | < 1s | Single action |

## Best Practices

### 1. Async Operations
Always use async/await for platform API calls:

```python
# Good
comments = await platform.fetch_comments(post_id)

# Bad (blocking)
comments = platform.fetch_comments(post_id)
```

### 2. Batch Processing
Use batch operations when possible:

```python
# Good - batch
results = await analyzer.batch_analyze(comments)

# Acceptable - single loop
results = [await analyzer.analyze(c) for c in comments]
```

### 3. Rate Limiting
Respect platform rate limits:

```python
# Rate limiter is built-in
await platform.fetch_comments(post_id)  # Automatically respects limits
```

### 4. Error Handling
Always handle exceptions appropriately:

```python
try:
    comments = await platform.fetch_comments(post_id)
except RateLimitExceeded:
    logger.warning("Rate limit exceeded, waiting...")
    await asyncio.sleep(60)
except PlatformAPIError as e:
    logger.error(f"Platform error: {e}")
```

### 5. Credential Management
Never commit credentials:

```python
# Good - use environment variables
platform = TwitterAPI.from_env()

# Bad - hardcoded credentials
platform = TwitterAPI(api_key="1234", ...)
```

## Related Documentation

- **Standards & Metrics**: `../standards-and-metrics.md` - Moderation rules
- **Comment Analysis**: `../comment-analysis/README.md` - Analysis techniques
- **Architecture**: `../ARCHITECTURE.md` - System design
- **LLM Context Guide**: `../llm-context-guide.md` - How LLMs use this library

## Troubleshooting

### Common Issues

**Issue: Authentication fails**
- Check credentials are correct
- Verify OAuth scopes
- Check token expiration

**Issue: Rate limit errors**
- Reduce request frequency
- Implement exponential backoff
- Use batch operations

**Issue: Empty comment list**
- Check post exists and is public
- Verify credentials have read permissions
- Check platform-specific API restrictions

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | January 2024 | Initial API reference |

---

**Last Updated**: January 2024
**Status**: Phase 1 - Documentation Phase
