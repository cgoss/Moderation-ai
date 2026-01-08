---
title: Reddit API Guide
category: platform
platform: reddit
related:
  - ./README.md
  - ./authentication.md
  - ../../docs/api-reference/README.md
---

# Reddit API Guide

## Overview

This guide provides comprehensive instructions for using Reddit API with Moderation AI library, including fetching posts, retrieving comments, and applying moderation actions.

## API Endpoints

### Core Endpoints

| Operation | HTTP Method | Endpoint | Purpose |
|-----------|--------------|---------|----------|
| Get Post | GET | `/r/subreddit/comments/post_id.json` | Retrieve single post |
| Get Comments | GET | `/comments/post_id.json` | Fetch post comments |
| User Timeline | GET | `/user/username/submitted` | User's post history |
| Subreddit Posts | GET | `/r/subreddit/new.json` | Subreddit new posts |
| Remove Comment | POST | `/api/moderate` | Remove comment (mod) |
| Approve Comment | POST | `/api/approve` | Approve removed comment (mod) |

## Initialization

### From Environment Variables

```python
from moderation_ai.platforms import RedditAPI

# Load from environment
reddit = RedditAPI.from_env()

# Environment variables needed:
# REDDIT_CLIENT_ID
# REDDIT_CLIENT_SECRET
# REDDIT_USER_AGENT
# REDDIT_USERNAME
# REDDIT_PASSWORD
```

### Explicit Credentials

```python
reddit = RedditAPI(
    client_id="your_client_id",
    client_secret="your_client_secret",
    user_agent="your_user_agent",
    username="your_username",
    password="your_password"
)

await reddit.authenticate()
```

### OAuth 2.0 (User Context)

```python
reddit = RedditAPI(
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="http://localhost:8080/callback",
    access_token="your_access_token",
    refresh_token="your_refresh_token"
)

await reddit.authenticate()
```

## Fetching Posts

### Get Single Post

```python
post_id = "abc123"
post = await reddit.fetch_post(post_id)

print(f"Post: {post.title}")
print(f"Author: {post.author_username}")
print(f"Upvotes: {post.score}")
```

### Get Subreddit Posts

```python
subreddit_name = "moderation_ai"
posts = await reddit.fetch_subreddit_posts(
    subreddit=subreddit_name,
    sort="new",
    limit=100
)

for post in posts:
    print(f"{post.title}")
```

### Get User Posts

```python
username = "reddit_user"
posts = await reddit.fetch_user_posts(
    username=username,
    sort="new",
    limit=100
)

for post in posts:
    print(f"{post.title}")
```

### Search Posts

```python
query = "moderation_ai"
posts = await reddit.search_posts(
    query=query,
    sort="relevance",
    limit=100
)

for post in posts:
    print(f"{post.title}")
```

## Fetching Comments

### Get Post Comments

```python
post_id = "abc123"
comments = await reddit.fetch_comments(post_id)

for comment in comments:
    print(f"{comment.author_username}: {comment.text}")
```

### Get User Comments

```python
username = "reddit_user"
comments = await reddit.fetch_user_comments(username, limit=100)

for comment in comments:
    print(f"{comment.text}")
```

### Get Specific Comment

```python
comment_id = "def456"
comment = await reddit.fetch_comment(comment_id)

print(f"Comment: {comment.text}")
print(f"Author: {comment.author_username}")
print(f"Score: {comment.score}")
```

### Pagination

```python
post_id = "abc123"
after = None
all_comments = []

while True:
    result = await reddit.fetch_comments(
        post_id,
        after=after,
        limit=100
    )
    
    all_comments.extend(result.comments)
    
    if not result.has_more:
        break
    
    after = result.after
```

### With Metadata

```python
comments = await reddit.fetch_comments(
    post_id,
    include_threaded=True,
    include_depth=True
)

for comment in comments:
    print(f"{comment.author_username}: {comment.text}")
    print(f"  Depth: {comment.depth}")
    print(f"  Replies: {len(comment.replies)}")
```

## Creating Comments

### Reply to Post

```python
post_id = "abc123"
reply_text = "This is a great point!"

comment = await reddit.post_comment(post_id, reply_text)
print(f"Comment posted: {comment.id}")
```

### Reply to Comment

```python
parent_comment_id = "def456"
reply_text = "I agree with this"

comment = await reddit.post_comment(
    parent_comment_id,
    reply_text
)

print(f"Reply posted: {comment.id}")
```

## Moderating Comments

### Remove Comment

```python
comment_id = "def456"
removed = await reddit.moderate_comment(comment_id, "remove")

if removed:
    print("Comment removed successfully")
else:
    print("Failed to remove comment")
```

### Approve Comment

```python
comment_id = "def456"
await reddit.moderate_comment(comment_id, "approve")
```

### Distinguish Comment

```python
comment_id = "def456"
await reddit.moderate_comment(comment_id, "distinguish")
```

### Batch Moderation

```python
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

standards = StandardsEngine()
abuse = AbuseDetector()

comments = await reddit.fetch_comments(post_id)

# Analyze and moderate
for comment in comments:
    # Check against standards
    decision = standards.validate(comment.text)
    
    # Check for abuse
    abuse_result = abuse.analyze(comment)
    
    # Apply appropriate action
    if abuse_result.is_abuse and abuse_result.severity == "critical":
        await reddit.moderate_comment(comment.id, "remove")
    elif decision.action == "flag":
        await reddit.moderate_comment(comment.id, "remove")
```

## Post Tracking

### Enable Comment Tracking

```python
post_id = "abc123"
await reddit.track_post(post_id)

# Monitor for new comments via polling
```

### Check Post Status

```python
post_id = "abc123"
status = await reddit.get_post_status(post_id)

print(f"Comment count: {status.comment_count}")
print(f"Upvotes: {status.upvotes}")
```

See `./post-tracking.md` for detailed tracking setup.

## Error Handling

### Rate Limit Error

```python
from moderation_ai.utils import RateLimitExceeded

try:
    comments = await reddit.fetch_comments(post_id)
except RateLimitExceeded as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
    await asyncio.sleep(e.retry_after)
```

### Authentication Error

```python
from moderation_ai.utils import AuthenticationError

try:
    await reddit.authenticate()
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print(f"Error code: {e.code}")
```

### Post Not Found

```python
from moderation_ai.utils import PostNotFoundError

try:
    post = await reddit.fetch_post(post_id)
except PostNotFoundError:
    print(f"Post {post_id} not found")
```

## Advanced Operations

### Search with Filters

```python
query = "moderation_ai nsfw:no"
posts = await reddit.search_posts(
    query=query,
    sort="relevance",
    limit=100,
    time_filter="week"
)
```

### Get Multiple Posts

```python
post_ids = ["abc123", "def456", "ghi789"]
posts = await reddit.fetch_posts(post_ids)

for post in posts:
    print(f"{post.title}")
```

### Get Subreddit Info

```python
subreddit_name = "moderation_ai"
subreddit = await reddit.fetch_subreddit(subreddit_name)

print(f"Subreddit: {subreddit.display_name}")
print(f"Subscribers: {subreddit.subscribers}")
```

### Get User Information

```python
username = "reddit_user"
user = await reddit.fetch_user(username=username)

print(f"User: @{user.username}")
print(f"Karma: {user.karma}")
print(f"Account age: {user.account_age}")
```

## Best Practices

### 1. Use Appropriate Rate Limiting

```python
# Good - respects rate limits
limiter = RateLimiter(platform="reddit", requests_per_minute=60)
await limiter.wait()
comments = await reddit.fetch_comments(post_id)
```

### 2. Handle Nested Comments

```python
# Good - process nested structure
def process_comments(comments):
    for comment in comments:
        process_single_comment(comment)
        if comment.replies:
            process_comments(comment.replies)
```

### 3. Cache User Data

```python
# Good - cache user info
@lru_cache(maxsize=1000)
async def get_user_info(username):
    return await reddit.fetch_user(username=username)
```

### 4. Use Batch Operations

```python
# Good - batch fetch
post_ids = ["1", "2", "3", "4", "5"]
posts = await reddit.fetch_posts(post_ids)

# Bad - individual fetches
for post_id in post_ids:
    post = await reddit.fetch_post(post_id)
```

### 5. Implement Retry Logic

```python
# Good - retry with backoff
max_retries = 3
for attempt in range(max_retries):
    try:
        comments = await reddit.fetch_comments(post_id)
        break
    except RateLimitExceeded:
        if attempt < max_retries - 1:
            await asyncio.sleep(60 * (2 ** attempt))
        else:
            raise
```

## Performance Tips

### Reduce API Calls

```python
# Request all needed data in single call
comments = await reddit.fetch_comments(
    post_id,
    include_threaded=True,
    include_depth=True
)
```

### Use Pagination Effectively

```python
# Fetch more per page
result = await reddit.fetch_comments(post_id, limit=100)
```

### Parallel Fetching

```python
# Fetch multiple posts in parallel
post_ids = ["1", "2", "3", "4", "5"]
posts = await asyncio.gather(*[
    reddit.fetch_post(post_id)
    for post_id in post_ids
])
```

## Troubleshooting

### Issue: 401 Unauthorized

**Possible causes**:
- Invalid credentials
- Expired session
- Wrong auth method

**Solution**:
- Verify credentials are correct
- Refresh OAuth token
- Check auth setup

### Issue: 403 Forbidden

**Possible causes**:
- Not a moderator
- Insufficient permissions
- Private subreddit

**Solution**:
- Verify you're a moderator
- Check subreddit permissions
- Ensure subreddit is public

### Issue: 429 Rate Limit Exceeded

**Possible causes**:
- Exceeded rate limits
- Multiple API calls

**Solution**:
- Implement rate limiting
- Use exponential backoff
- Reduce request frequency

### Issue: Empty Comment List

**Possible causes**:
- Post has no comments
- Post is private
- Post deleted

**Solution**:
- Verify post exists and is public
- Check comment tree depth
- Confirm post is in public subreddit

## Related Documentation

- **Authentication**: `./authentication.md` - Auth setup
- **Rate Limits**: `./rate-limits.md` - Rate limit details
- **Post Tracking**: `./post-tracking.md` - Post monitoring
- **Data Models**: `./data-models.md` - Data structures
- **Examples**: `./examples/` - Usage examples

---

**Last Updated**: January 2024
**Status**: Phase 2 - Documentation Complete
