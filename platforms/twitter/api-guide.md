---
title: Twitter API Guide
category: platform
platform: twitter
related:
  - ./README.md
  - ./authentication.md
  - ../../docs/api-reference/README.md
---

# Twitter API Guide

## Overview

This guide provides comprehensive instructions for using Twitter API v2 with the Moderation AI library, including fetching posts, retrieving comments, and applying moderation actions.

## API Endpoints

### Core Endpoints

| Operation | HTTP Method | Endpoint | Purpose |
|-----------|--------------|---------|----------|
| Get Tweet | GET | `/2/tweets/:id` | Retrieve single tweet |
| Get Replies | GET | `/2/tweets/:id/hidden_replies` | Fetch tweet replies |
| User Timeline | GET | `/2/users/:id/tweets` | User's tweet history |
| Search | GET | `/2/tweets/search/recent` | Search tweets |
| Hide Reply | PUT | `/2/tweets/:id/hidden` | Hide/unhide reply |
| Delete Tweet | DELETE | `/2/tweets/:id` | Delete tweet |

## Initialization

### From Environment Variables

```python
from moderation_ai.platforms import TwitterAPI

# Load from environment
twitter = TwitterAPI.from_env()

# Environment variables needed:
# TWITTER_API_KEY
# TWITTER_API_SECRET
# TWITTER_BEARER_TOKEN
```

### Explicit Credentials

```python
twitter = TwitterAPI(
    api_key="your_api_key",
    api_secret="your_api_secret",
    bearer_token="your_bearer_token"
)

await twitter.authenticate()
```

### OAuth 1.0a (User Context)

```python
twitter = TwitterAPI(
    api_key="your_api_key",
    api_secret="your_api_secret",
    access_token="your_access_token",
    access_token_secret="your_access_token_secret"
)

await twitter.authenticate()
```

## Fetching Posts

### Get Single Tweet

```python
tweet_id = "1234567890"
tweet = await twitter.fetch_post(tweet_id)

print(f"Tweet: {tweet.text}")
print(f"Author: {tweet.author_username}")
print(f"Likes: {tweet.metrics.like_count}")
```

### Get User Timeline

```python
user_id = "987654321"
tweets = await twitter.fetch_user_timeline(
    user_id=user_id,
    max_results=100,
    tweet_fields=["created_at", "public_metrics", "author_id"]
)

for tweet in tweets:
    print(f"{tweet.text}")
```

### Search Tweets

```python
query = "moderation_ai"
tweets = await twitter.search_tweets(
    query=query,
    max_results=100,
    tweet_fields=["created_at", "public_metrics"]
)

for tweet in tweets:
    print(f"{tweet.text}")
```

## Fetching Comments

### Get Tweet Replies

```python
tweet_id = "1234567890"
comments = await twitter.fetch_comments(tweet_id)

for comment in comments:
    print(f"{comment.author_username}: {comment.text}")
```

### Pagination

```python
tweet_id = "1234567890"
cursor = None
all_comments = []

while True:
    result = await twitter.fetch_comments(
        tweet_id,
        cursor=cursor,
        max_results=100
    )
    
    all_comments.extend(result.comments)
    
    if not result.has_more:
        break
    
    cursor = result.next_cursor
```

### With Metadata

```python
comments = await twitter.fetch_comments(
    tweet_id,
    tweet_fields=["created_at", "public_metrics", "author_id"],
    user_fields=["username", "name", "verified"],
    expansions=["author_id"]
)

for comment in comments:
    print(f"@{comment.author_username} ({comment.author_name}): {comment.text}")
    if comment.verified:
        print("  ✓ Verified")
```

## Creating Comments

### Reply to Tweet

```python
tweet_id = "1234567890"
reply_text = "This is a great point!"

comment = await twitter.post_comment(tweet_id, reply_text)
print(f"Reply posted: {comment.id}")
```

### Thread Reply

```python
parent_tweet_id = "1234567890"
reply_text = "I agree with this"

comment = await twitter.post_comment(
    parent_tweet_id,
    reply_text,
    reply_settings={"auto_populate_reply_metadata": True}
)
```

## Moderating Comments

### Hide Reply

```python
comment_id = "9876543210"
hidden = await twitter.moderate_comment(comment_id, "hide")

if hidden:
    print("Comment hidden successfully")
else:
    print("Failed to hide comment")
```

### Unhide Reply

```python
comment_id = "9876543210"
await twitter.moderate_comment(comment_id, "unhide")
```

### Delete Tweet

```python
tweet_id = "1234567890"
deleted = await twitter.delete_tweet(tweet_id)

if deleted:
    print("Tweet deleted successfully")
```

### Batch Moderation

```python
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

standards = StandardsEngine()
abuse = AbuseDetector()

comments = await twitter.fetch_comments(tweet_id)

# Analyze and moderate
for comment in comments:
    # Check against standards
    decision = standards.validate(comment.text)
    
    # Check for abuse
    abuse_result = abuse.analyze(comment)
    
    # Apply appropriate action
    if abuse_result.is_abuse and abuse_result.severity == "critical":
        await twitter.moderate_comment(comment.id, "hide")
    elif decision.action == "flag":
        await twitter.moderate_comment(comment.id, "flag")
```

## Post Tracking

### Enable Reply Tracking

```python
tweet_id = "1234567890"
await twitter.track_post(tweet_id)

# Now receive webhooks for new replies
```

### Check Post Status

```python
tweet_id = "1234567890"
status = await twitter.get_post_status(tweet_id)

print(f"Reply count: {status.reply_count}")
print(f"Like count: {status.like_count}")
```

See `./post-tracking.md` for detailed tracking setup.

## Error Handling

### Rate Limit Error

```python
from moderation_ai.utils import RateLimitExceeded

try:
    comments = await twitter.fetch_comments(tweet_id)
except RateLimitExceeded as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
    await asyncio.sleep(e.retry_after)
```

### Authentication Error

```python
from moderation_ai.utils import AuthenticationError

try:
    await twitter.authenticate()
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print(f"Error code: {e.code}")
```

### Tweet Not Found

```python
from moderation_ai.utils import PostNotFoundError

try:
    tweet = await twitter.fetch_post(tweet_id)
except PostNotFoundError:
    print(f"Tweet {tweet_id} not found")
```

## Advanced Operations

### Search with Filters

```python
query = "moderation_ai -is:retweet lang:en"
tweets = await twitter.search_tweets(
    query=query,
    max_results=100,
    start_time="2024-01-01T00:00:00Z",
    end_time="2024-01-31T23:59:59Z"
)
```

### Get Multiple Tweets

```python
tweet_ids = ["1234567890", "0987654321", "5432109876"]
tweets = await twitter.fetch_posts(tweet_ids)

for tweet in tweets:
    print(f"{tweet.text}")
```

### Get User Information

```python
username = "twitter_user"
user = await twitter.fetch_user(username=username)

print(f"User: @{user.username}")
print(f"Name: {user.name}")
print(f"Followers: {user.followers_count}")
```

## Best Practices

### 1. Use Appropriate Rate Limiting

```python
# Good - respects rate limits
limiter = RateLimiter(platform="twitter", requests_per_minute=300)
await limiter.wait()
comments = await twitter.fetch_comments(tweet_id)
```

### 2. Handle Pagination

```python
# Good - fetch all pages
all_comments = []
cursor = None

while True:
    result = await twitter.fetch_comments(tweet_id, cursor=cursor)
    all_comments.extend(result.comments)
    
    if not result.has_more:
        break
    
    cursor = result.next_cursor
```

### 3. Cache User Data

```python
# Good - cache user info
@lru_cache(maxsize=1000)
async def get_user_info(user_id):
    return await twitter.fetch_user(user_id=user_id)
```

### 4. Use Batch Operations

```python
# Good - batch fetch
tweet_ids = ["1", "2", "3", "4", "5"]
tweets = await twitter.fetch_posts(tweet_ids)

# Bad - individual fetches
for tweet_id in tweet_ids:
    tweet = await twitter.fetch_tweet(tweet_id)
```

### 5. Implement Retry Logic

```python
# Good - retry with backoff
max_retries = 3
for attempt in range(max_retries):
    try:
        comments = await twitter.fetch_comments(tweet_id)
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
# Request all needed fields in single call
comments = await twitter.fetch_comments(
    tweet_id,
    tweet_fields=["created_at", "public_metrics", "author_id"],
    user_fields=["username", "name", "verified"],
    expansions=["author_id"]
)
```

### Use Pagination Effectively

```python
# Fetch more per page
result = await twitter.fetch_comments(tweet_id, max_results=100)
```

### Parallel Fetching

```python
# Fetch multiple tweets in parallel
tweet_ids = ["1", "2", "3", "4", "5"]
tweets = await asyncio.gather(*[
    twitter.fetch_tweet(tweet_id)
    for tweet_id in tweet_ids
])
```

## Troubleshooting

### Issue: 401 Unauthorized

**Possible causes**:
- Invalid API credentials
- Expired bearer token
- Wrong OAuth flow

**Solution**:
- Verify credentials are correct
- Refresh bearer token
- Check OAuth setup

### Issue: 429 Rate Limit Exceeded

**Possible causes**:
- Exceeded rate limits
- Multiple API calls

**Solution**:
- Implement rate limiting
- Use exponential backoff
- Upgrade API tier

### Issue: Empty Comment List

**Possible causes**:
- Tweet has no replies
- Tweet is private
- Permissions issue

**Solution**:
- Verify tweet is public
- Check permissions
- Confirm tweet has replies

## Related Documentation

- **Authentication**: `./authentication.md` - Auth setup
- **Rate Limits**: `./rate-limits.md` - Rate limit details
- **Post Tracking**: `./post-tracking.md` - Post monitoring
- **Data Models**: `./data-models.md` - Data structures
- **Examples**: `./examples/` - Usage examples

---

**Last Updated**: January 2024
**Status**: Phase 2 - Documentation Complete
