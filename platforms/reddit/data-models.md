---
title: Reddit Data Models
category: platform
platform: reddit
related:
  - ./README.md
  - ./api-guide.md
  - ../../docs/api-reference/common-patterns.md
---

# Reddit Data Models

## Overview

This document describes the data structures used by Reddit API, including posts, comments, users, and metadata. All data is normalized by Moderation AI library for consistent cross-platform handling.

## Post Model

### Basic Post Structure

```python
{
    "id": "abc123",
    "title": "Post title",
    "selftext": "Post body text",
    "author_id": "user123",
    "author_username": "reddit_user",
    "author_name": "Reddit User",
    "subreddit_id": "sub456",
    "subreddit_name": "moderation_ai",
    "created_at": "2024-01-08T10:00:00.000Z",
    "platform": "reddit",
    "url": "https://reddit.com/r/moderation_ai/comments/abc123",
    "score": 150,
    "upvotes": 155,
    "downvotes": 5,
    "num_comments": 25,
    "over_18": false,
    "spoiler": false,
    "locked": false,
    "stickied": false
}
```

### Post Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique post ID |
| `title` | string | Post title |
| `selftext` | string | Post body text |
| `author_id` | string | Author's user ID |
| `author_username` | string | Author's username |
| `author_name` | string | Author's display name |
| `subreddit_id` | string | Subreddit ID |
| `subreddit_name` | string | Subreddit name |
| `created_at` | datetime | Post creation timestamp |
| `platform` | string | "reddit" |
| `url` | string | Post URL |
| `score` | int | Net upvotes (up - down) |
| `upvotes` | int | Number of upvotes |
| `downvotes` | int | Number of downvotes |
| `num_comments` | int | Number of comments |
| `over_18` | boolean | NSFW flag |
| `spoiler` | boolean | Spoiler flag |
| `locked` | boolean | Locked status |
| `stickied` | boolean | Stickied status |
| `flair_text` | string | Post flair |
| `awards` | array | Awards received |

## Comment Model

### Basic Comment Structure

```python
{
    "id": "def456",
    "post_id": "abc123",
    "author_id": "user456",
    "author_username": "commenter",
    "author_name": "Commenter User",
    "text": "This is a comment",
    "created_at": "2024-01-08T10:05:00.000Z",
    "platform": "reddit",
    "parent_id": "abc123",
    "subreddit_id": "sub456",
    "subreddit_name": "moderation_ai",
    "score": 5,
    "depth": 1,
    "is_root": false,
    "replies": [
        {
            "id": "ghi789",
            "author_id": "user789",
            "text": "Reply to comment",
            "depth": 2
        }
    ],
    "edited": false,
    "gilded": 0,
    "stickied": false,
    "distinguished": null
}
```

### Comment Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique comment ID |
| `post_id` | string | Parent post ID |
| `author_id` | string | Commenter's user ID |
| `author_username` | string | Commenter's username |
| `author_name` | string | Commenter's display name |
| `text` | string | Comment content |
| `created_at` | datetime | Comment creation timestamp |
| `platform` | string | "reddit" |
| `parent_id` | string | Parent comment or post ID |
| `subreddit_id` | string | Subreddit ID |
| `subreddit_name` | string | Subreddit name |
| `score` | int | Net upvotes |
| `depth` | int | Nesting depth |
| `is_root` | boolean | Top-level comment |
| `replies` | array | Nested replies |
| `edited` | boolean | Whether edited |
| `gilded` | int | Number of awards |
| `stickied` | boolean | Stickied status |
| `distinguished` | string | Mod/admin status |

## User Model

### Basic User Structure

```python
{
    "id": "user123",
    "username": "reddit_user",
    "name": "Reddit User",
    "created_at": "2010-01-01T00:00:00.000Z",
    "karma": 5000,
    "post_karma": 3000,
    "comment_karma": 2000,
    "awardee_karma": 10000,
    "has_verified_email": true,
    "is_gold": false,
    "is_mod": false,
    "total_posts": 500,
    "total_comments": 1500
}
```

### User Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique user ID |
| `username` | string | Username (u/username) |
| `name` | string | Display name |
| `created_at` | datetime | Account creation date |
| `karma` | int | Total karma |
| `post_karma` | int | Karma from posts |
| `comment_karma` | int | Karma from comments |
| `awardee_karma` | int | Karma received |
| `has_verified_email` | boolean | Verified email |
| `is_gold` | boolean | Gold subscriber |
| `is_mod` | boolean | Moderator status |
| `total_posts` | int | Total posts submitted |
| `total_comments` | int | Total comments |

## Subreddit Model

### Basic Subreddit Structure

```python
{
    "id": "sub456",
    "name": "moderation_ai",
    "display_name": "Moderation AI",
    "title": "Moderation AI Community",
    "description": "Discussion about comment moderation",
    "subscribers": 10000,
    "created_at": "2020-01-01T00:00:00.000Z",
    "over_18": false,
    "public_description": "Description here",
    "quarantine": false
    "lang": "en"
}
```

### Subreddit Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique subreddit ID |
| `name` | string | Subreddit name |
| `display_name` | string | Display name |
| `title` | string | Subreddit title |
| `description` | string | Subreddit description |
| `subscribers` | int | Subscriber count |
| `created_at` | datetime | Creation date |
| `over_18` | boolean | NSFW flag |
| `quarantine` | boolean | Quarantine status |
| `lang` | string | Primary language |

## Flair Model

### Post Flair

```python
{
    "flair_text": "Discussion",
    "flair_template_id": "template123",
    "flair_css_class": "flair-blue",
    "flair_position": "right",
    "richtext": false,
    "text_editable": false
}
```

### User Flair

```python
{
    "user_flair_text": "Expert",
    "user_flair_css_class": "flair-gold",
    "user_flair_richtext": false,
    "user_flair_background_color": "#f5f5f5",
    "user_flair_text_color": "#000000"
}
```

## Award Model

### Comment Awards

```python
{
    "id": "award123",
    "name": "Silver",
    "name_lower": "silver",
    "description": "Award for great comments",
    "coin_price": 100,
    "coin_reward": 0,
    "icon_url": "https://www.redditstatic.com/award/...",
    "days_of_drip_extension": 0,
    "is_subcriber_only": false,
    "count": 1
}
```

### Award Types

| Type | Name | Coin Cost |
|------|------|-----------|
| `platinum` | Platinum | 1800 |
| `gold` | Gold | 500 |
| `silver` | Silver | 100 |
| `argon` | Argon | 50 |
| `tissue` | Tissue | 25 |

## Normalized Data Model

The Moderation AI library normalizes all platform data to a common format:

### Normalized Comment

```python
{
    "id": "def456",
    "post_id": "abc123",
    "author_id": "user456",
    "author_username": "commenter",
    "author_name": "Commenter User",
    "text": "This is a comment",
    "created_at": "2024-01-08T10:05:00.000Z",
    "platform": "reddit",
    "metadata": {
        "parent_id": "abc123",
        "depth": 1,
        "is_root": false,
        "subreddit": "moderation_ai",
        "score": 5,
        "gilded": 0,
        "distinguished": null
    }
}
```

### Normalized Post

```python
{
    "id": "abc123",
    "author_id": "user123",
    "author_username": "reddit_user",
    "author_name": "Reddit User",
    "text": "Post title",
    "media_urls": ["url1", "url2"],
    "created_at": "2024-01-08T10:00:00.000Z",
    "platform": "reddit",
    "metadata": {
        "score": 150,
        "num_comments": 25,
        "subreddit": "moderation_ai",
        "flair": "Discussion",
        "stickied": false,
        "locked": false
    }
}
```

## API Request Parameters

### Post Fields

```python
post_fields = [
    "id",
    "title",
    "selftext",
    "author",
    "created",
    "num_comments",
    "score",
    "over_18",
    "spoiler",
    "stickied",
    "locked"
]
```

### Comment Fields

```python
comment_fields = [
    "id",
    "author",
    "body",
    "created",
    "score",
    "edited",
    "gilded",
    "stickied",
    "distinguished"
]
```

### Subreddit Fields

```python
subreddit_fields = [
    "id",
    "display_name",
    "title",
    "description",
    "subscribers",
    "over_18",
    "lang"
]
```

## Usage Examples

### Fetch with Specific Fields

```python
# Request specific fields
comments = await reddit.fetch_comments(
    post_id,
    include_threaded=True,
    include_depth=True
)

# Comments include requested data
for comment in comments:
    print(f"@{comment.author_username}: {comment.text}")
    print(f"  Depth: {comment.depth}")
    print(f"  Score: {comment.score}")
    print(f"  Replies: {len(comment.replies)}")
```

### Access Nested Comments

```python
comment = await reddit.fetch_comment(comment_id)

# Process nested structure
def process_comment(comment):
    print(f"{'  ' * comment.depth}{comment.author_username}: {comment.text[:50]}...")
    
    # Process replies recursively
    if comment.replies:
        for reply in comment.replies:
            process_comment(reply)

process_comment(comment)
```

### Access Awards

```python
comment = await reddit.fetch_comment(comment_id)

# Check for awards
if comment.awards:
    for award in comment.awards:
        print(f"Award: {award.name} (x{award.count})")
        print(f"  Description: {award.description}")
```

### Access Flair

```python
post = await reddit.fetch_post(post_id)

# Check post flair
if post.flair_text:
    print(f"Flair: {post.flair_text}")

# Check user flair
if comment.author_flair_text:
    print(f"User flair: {comment.author_flair_text}")
```

## Best Practices

### 1. Request Only Needed Fields

```python
# Good - specific fields
comments = await reddit.fetch_comments(
    post_id,
    include_threaded=True
)

# Bad - all fields (may be slower)
comments = await reddit.fetch_comments(post_id)
```

### 2. Use Pagination Effectively

```python
# Good - fetch more per page
result = await reddit.fetch_comments(
    post_id,
    limit=100
)
```

### 3. Handle Nested Comments

```python
# Good - process nested structure
def process_comment_tree(comments):
    for comment in comments:
        process_single_comment(comment)
        if comment.replies:
            process_comment_tree(comment.replies)
```

### 4. Cache User Data

```python
# Good - cache user info
@lru_cache(maxsize=1000)
async def get_user_info(username):
    return await reddit.fetch_user(username=username)
```

### 5. Handle Missing Fields

```python
# Always check if field exists
comment = await reddit.fetch_comment(comment_id)

if hasattr(comment, "score"):
    score = comment.score
else:
    score = 0
```

## Related Documentation

- **API Guide**: `./api-guide.md` - API usage
- **Common Patterns**: `../../docs/api-reference/common-patterns.md` - Data normalization
- **Examples**: `./examples/` - Usage examples

---

**Last Updated**: January 2024
**Status**: Phase 2 - Documentation Complete
