---
title: Reddit Platform Overview
category: platform
platform: reddit
related:
  - ../../docs/api-reference/README.md
  - ./api-guide.md
  - ./authentication.md
---

# Reddit Platform

## Overview

Reddit is a community-driven platform with a rich API that provides comprehensive access to posts, comments, and moderation capabilities. This document outlines how to integrate Reddit comment moderation with Moderation AI system.

## Platform Characteristics

| Attribute | Value |
|-----------|--------|
| **API Version** | Latest (OAuth 2.0) |
| **Auth Method** | OAuth 2.0 / Personal Use Script |
| **Rate Limiting** | Token bucket (60 requests/min) |
| **Comments Model** | Nested comments on posts |
| **Webhooks** | Supported (Modmail, etc.) |
| **Real-time** | Limited (SSE for streams) |

## Capabilities

### Supported Operations

| Operation | Status | Notes |
|------------|--------|-------|
| Fetch posts | ✅ Full | Includes post metadata |
| Fetch comments | ✅ Full | Nested comment threads |
| Moderate comments | ✅ Full | Remove/approve as moderator |
| Delete comments | ✅ Full | Own comments only |
| Track posts | ✅ Partial | Webhooks for new posts |

### Moderation Actions

- **Remove comment**: Remove comment (requires mod permissions)
- **Approve comment**: Approve removed comment
- **Distinguish comment**: Mark as mod comment
- **Lock thread**: Prevent new comments
- **Ban user**: Ban user from subreddit

## Integration Benefits

### Advantages

- **Rich API**: Comprehensive moderation endpoints
- **Community-focused**: Designed for community moderation
- **Subreddit structure**: Clear organization
- **Webhooks available**: Modmail, post reports
- **Flexible auth**: OAuth or personal use script

### Considerations

- **Nested comments**: Complex comment tree structure
- **Rate limiting**: Strict rate limits (60/min)
- **Subreddit permissions**: Required for moderation actions
- **Content limits**: Longer form content than Twitter

## Use Cases

### Subreddit Moderation

```python
from moderation_ai.platforms import RedditAPI

reddit = RedditAPI.from_env()

# Monitor subreddit for new posts
subreddit_name = "moderation_ai"

# Fetch recent posts
posts = await reddit.fetch_posts(f"r/{subreddit_name}")

for post in posts:
    comments = await reddit.fetch_comments(post.id)
    for comment in comments:
        decision = standards.validate(comment.text)
        if decision.action != "approve":
            await reddit.moderate_comment(comment.id, "remove")
```

### User Monitoring

```python
# Track specific user's comments
username = "problematic_user"

comments = await reddit.fetch_user_comments(username)

for comment in comments:
    abuse_result = abuse_detector.analyze(comment)
    if abuse_result.is_abuse:
        await reddit.moderate_comment(comment.id, "remove")
```

### Multi-Subreddit Monitoring

```python
# Monitor multiple subreddits
subreddits = ["r/moderation_ai", "r/automation", "r/community"]

for subreddit in subreddits:
    posts = await reddit.fetch_posts(subreddit)
    for post in posts:
        comments = await reddit.fetch_comments(post.id)
        analyze_and_moderate(comments)
```

## API Access Levels

| Level | Rate Limits | Features |
|-------|-------------|----------|
| **Personal Use Script** | 60/min | Basic read, write as user |
| **OAuth 2.0** | 60/min | Read, write as app or user |
| **Mod Access** | 60/min | Plus moderation endpoints |

## Quick Start

### 1. Get Reddit API Credentials

1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Create script application
3. Generate credentials:
   - Client ID
   - Client Secret
   - User Agent string
4. Set environment variables:
   ```bash
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USER_AGENT=your_user_agent
   REDDIT_USERNAME=your_username
   REDDIT_PASSWORD=your_password
   ```

### 2. Initialize RedditAPI

```python
from moderation_ai.platforms import RedditAPI

# From environment variables
reddit = RedditAPI.from_env()

# Or with explicit credentials
reddit = RedditAPI(
    client_id="your_client_id",
    client_secret="your_client_secret",
    user_agent="your_user_agent",
    username="your_username",
    password="your_password"
)
```

### 3. Fetch Comments

```python
# Fetch comments for a post
post_id = "abc123"
comments = await reddit.fetch_comments(post_id)

for comment in comments:
    print(f"{comment.author}: {comment.text}")
```

### 4. Moderate Comments

```python
from moderation_ai.core import StandardsEngine

standards = StandardsEngine()

# Analyze comment
comment = await reddit.fetch_comment(comment_id)
decision = standards.validate(comment.text)

# Apply moderation action
if decision.action == "remove":
    await reddit.moderate_comment(comment_id, "remove")
```

## Data Model Overview

### Post

```python
{
    "id": "abc123",
    "title": "Post title",
    "selftext": "Post body text",
    "author": {
        "id": "user123",
        "name": "username"
    },
    "subreddit": {
        "id": "sub123",
        "name": "subreddit"
    },
    "created_at": "2024-01-08T10:00:00Z",
    "score": 150,
    "num_comments": 25
}
```

### Comment

```python
{
    "id": "def456",
    "post_id": "abc123",
    "author": {
        "id": "user456",
        "name": "commenter"
    },
    "body": "This is a comment",
    "parent_id": "abc123",
    "created_at": "2024-01-08T10:05:00Z",
    "score": 5
}
```

## Platform-Specific Features

### Nested Comments

Reddit uses a tree structure for comments:
- `parent_id`: Direct parent comment or post
- `replies`: Nested replies to comment
- `depth`: Nesting level
- `root`: Top-level comment for a thread

### Flair

Posts and comments can have flair:
- `link_flair_text`: Post flair
- `author_flair_text`: User flair
- `link_flair_css_class`: Flair styling

### Awards

Comments can receive awards:
- Gold, Silver, Platinum
- Special community awards
- Awards affect visibility

### NSFW Content

NSFW content is marked:
- `over_18`: NSFW flag
- Subreddit can be NSFW
- Requires special handling

## Rate Limits

### Fetch Operations

- **Get Post**: ~1 request
- **Get Comments**: ~1 request per post
- **User Timeline**: 60 requests / minute
- **Subreddit Posts**: 60 requests / minute

### Write Operations

- **Comment**: 60 requests / minute
- **Vote**: 60 requests / minute
- **Moderate**: Varies by subreddit

See `./rate-limits.md` for detailed rate limit information.

## Authentication

### OAuth 2.0 Authorization Code

For applications requiring user authentication:
- Requires user approval
- Access tokens with refresh
- User-specific actions

### Personal Use Script

For scripts/bots:
- Username/password authentication
- No OAuth required
- Easier setup

See `./authentication.md` for detailed authentication setup.

## Moderation Guidelines

### Platform Rules

- **Spam**: No excessive self-promotion
- **Harassment**: No targeted abuse
- **Hate Speech**: No discrimination
- **Doxxing**: No personal info sharing
- **Misinformation**: Platform takes action

### Moderation Capabilities

- **Remove comment**: Remove comment from thread
- **Approve comment**: Restore removed comment
- **Distinguish**: Mark as moderator action
- **Lock thread**: Prevent new comments
- **Ban user**: Ban from subreddit
- **Mute user**: Shadow ban

See `./comment-moderation.md` for detailed moderation guidelines.

## Troubleshooting

### Issue: Rate Limit Errors

**Symptom**: 429 errors when fetching comments

**Solution**:
1. Check rate limit headers
2. Implement exponential backoff
3. Use batch operations

### Issue: Permission Errors

**Symptom**: 403 errors when moderating

**Solution**:
1. Verify you're a moderator
2. Check subreddit permissions
3. Ensure correct auth flow

### Issue: Missing Comments

**Symptom**: Not all comments showing

**Solution**:
1. Check post is in public subreddit
2. Verify comment tree depth
3. Some comments may be removed or hidden

## Related Documentation

- **API Guide**: `./api-guide.md` - Detailed API usage
- **Authentication**: `./authentication.md` - Auth setup
- **Rate Limits**: `./rate-limits.md` - Rate limit details
- **Post Tracking**: `./post-tracking.md` - Post monitoring
- **Comment Moderation**: `./comment-moderation.md` - Moderation guidelines
- **Data Models**: `./data-models.md` - Data structure details
- **Examples**: `./examples/` - Usage examples

## Platform Status

| Status | Value |
|---------|-------|
| **Last Updated** | January 2024 |
| **API Version** | Latest |
| **Documentation Status** | In Progress |
| **Implementation Status** | Phase 2 - Documentation |

---

**Platform**: Reddit
**Documentation Version**: 1.0
**Status**: Phase 2 - Documentation In Progress
