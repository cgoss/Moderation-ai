---
title: Twitter Data Models
category: platform
platform: twitter
related:
  - ./README.md
  - ./api-guide.md
  - ../../docs/api-reference/common-patterns.md
---

# Twitter Data Models

## Overview

This document describes the data structures used by Twitter API v2, including tweets, replies (comments), users, and metadata. All data is normalized by the Moderation AI library for consistent cross-platform handling.

## Tweet (Post) Model

### Basic Tweet Structure

```python
{
    "id": "1234567890",
    "text": "This is a tweet",
    "author_id": "9876543210",
    "created_at": "2024-01-08T10:00:00.000Z",
    "platform": "twitter",
    "language": "en",
    "source": "Twitter Web App",
    "reply_settings": {
        "allow_replies": True
    },
    "public_metrics": {
        "like_count": 150,
        "retweet_count": 30,
        "reply_count": 25,
        "quote_count": 10
    }
}
```

### Tweet Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique tweet ID |
| `text` | string | Tweet content (max 280 chars) |
| `author_id` | string | Author's user ID |
| `created_at` | datetime | Tweet creation timestamp |
| `language` | string | ISO language code |
| `source` | string | Application used to post |
| `public_metrics` | object | Engagement metrics |
| `reply_settings` | object | Reply configuration |
| `geo` | object | Location data (optional) |
| `entities` | object | Hashtags, URLs, mentions |
| `attachments` | object | Media attachments |
| `referenced_tweets` | array | Referenced tweets |
| `context_annotations` | array | Context annotations |

## Reply (Comment) Model

### Basic Reply Structure

```python
{
    "id": "9876543210",
    "text": "This is a reply",
    "post_id": "1234567890",
    "author_id": "4567890123",
    "author_username": "replier_user",
    "author_name": "Replier User",
    "created_at": "2024-01-08T10:05:00.000Z",
    "platform": "twitter",
    "language": "en",
    "in_reply_to_user_id": "9876543210",
    "in_reply_to_tweet_id": "1234567890",
    "conversation_id": "1234567890",
    "public_metrics": {
        "like_count": 5,
        "retweet_count": 2,
        "reply_count": 3,
        "quote_count": 0
    }
}
```

### Reply Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique reply ID |
| `text` | string | Reply content |
| `post_id` | string | Parent tweet ID |
| `author_id` | string | Replier's user ID |
| `author_username` | string | Replier's handle |
| `author_name` | string | Replier's display name |
| `created_at` | datetime | Reply creation timestamp |
| `platform` | string | "twitter" |
| `language` | string | ISO language code |
| `in_reply_to_user_id` | string | User being replied to |
| `in_reply_to_tweet_id` | string | Tweet being replied to |
| `conversation_id` | string | Conversation thread ID |
| `public_metrics` | object | Reply engagement metrics |
| `entities` | object | Mentions, hashtags, URLs |
| `attachments` | object | Media attachments |
| `referenced_tweets` | array | Referenced tweets |

## User Model

### Basic User Structure

```python
{
    "id": "9876543210",
    "username": "twitter_user",
    "name": "Twitter User",
    "created_at": "2010-01-01T00:00:00.000Z",
    "description": "Twitter user bio",
    "verified": true,
    "blue_verified": true,
    "public_metrics": {
        "followers_count": 10000,
        "following_count": 500,
        "tweet_count": 5000,
        "listed_count": 100
    }
}
```

### User Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique user ID |
| `username` | string | Twitter handle (@username) |
| `name` | string | Display name |
| `created_at` | datetime | Account creation date |
| `description` | string | User bio |
| `verified` | boolean | Verified status |
| `blue_verified` | boolean | Blue verification |
| `protected` | boolean | Protected account |
| `public_metrics` | object | User metrics |
| `profile_image_url` | string | Profile image URL |
| `url` | string | Profile URL |
| `location` | string | User location |

## Public Metrics

### Tweet Metrics

```python
{
    "like_count": 150,
    "retweet_count": 30,
    "reply_count": 25,
    "quote_count": 10,
    "impression_count": 5000,
    "bookmark_count": 5
}
```

### Reply Metrics

```python
{
    "like_count": 5,
    "retweet_count": 2,
    "reply_count": 3,
    "quote_count": 0
}
```

### User Metrics

```python
{
    "followers_count": 10000,
    "following_count": 500,
    "tweet_count": 5000,
    "listed_count": 100,
    "like_count": 2500
}
```

## Entities Model

### Hashtags

```python
{
    "hashtags": [
        {
            "tag": "moderation",
            "start": 10,
            "end": 21
        }
    ]
}
```

### Mentions

```python
{
    "mentions": [
        {
            "username": "twitter_user",
            "id": "9876543210",
            "start": 0,
            "end": 12
        }
    ]
}
```

### URLs

```python
{
    "urls": [
        {
            "url": "https://t.co/example",
            "expanded_url": "https://example.com/article",
            "display_url": "example.com/article",
            "unwound_url": "https://example.com/article",
            "start": 50,
            "end": 72
        }
    ]
}
```

## Attachments Model

### Media Attachments

```python
{
    "attachments": {
        "media_keys": [
            "3_12345678901234567890",
            "3_09876543210987654321"
        ],
        "media": [
            {
                "media_key": "3_12345678901234567890",
                "type": "photo",
                "url": "https://pbs.twimg.com/media/example.jpg",
                "preview_image_url": "https://pbs.twimg.com/media/example_thumb.jpg",
                "width": 1200,
                "height": 800,
                "alt_text": "Image description"
            },
            {
                "media_key": "3_09876543210987654321",
                "type": "video",
                "duration_ms": 15000,
                "url": "https://video.twimg.com/example.mp4",
                "width": 1920,
                "height": 1080,
                "alt_text": "Video description"
            }
        ]
    }
}
```

### Polls

```python
{
    "attachments": {
        "poll_ids": ["1234567890"],
        "polls": [
            {
                "id": "1234567890",
                "options": [
                    {"label": "Option A", "votes": 100},
                    {"label": "Option B", "votes": 50}
                ],
                "end_datetime": "2024-01-08T12:00:00.000Z",
                "voting_status": "open"
            }
        ]
    }
}
```

## Referenced Tweets Model

```python
{
    "referenced_tweets": [
        {
            "type": "replied_to",
            "id": "1234567890"
        },
        {
            "type": "quoted",
            "id": "0987654321"
        }
    ]
}
```

### Reference Types

| Type | Description |
|------|-------------|
| `replied_to` | Direct reply to tweet |
| `quoted` | Quoted tweet |
| `retweeted` | Retweeted tweet |

## Reply Settings Model

```python
{
    "reply_settings": {
        "allow_replies": true,
        "allow_replies_from": "following"
    }
}
```

## Extended Tweets (Blue Users)

### Long-Form Tweet

```python
{
    "id": "1234567890",
    "text": "First 280 characters...",
    "note_tweet": {
        "note_id": "1234567890",
        "text": "Full long-form content here...",
        "note_title": "Article Title",
        "note_text_url": "https://twitter.com/i/note/1234567890"
    }
}
```

## Normalized Data Model

The Moderation AI library normalizes all platform data to a common format:

### Normalized Comment

```python
{
    "id": "9876543210",
    "post_id": "1234567890",
    "author_id": "4567890123",
    "author_username": "replier_user",
    "author_name": "Replier User",
    "text": "This is a reply",
    "created_at": "2024-01-08T10:05:00.000Z",
    "platform": "twitter",
    "language": "en",
    "metadata": {
        "in_reply_to_user_id": "9876543210",
        "conversation_id": "1234567890",
        "public_metrics": {...},
        "entities": {...}
    }
}
```

### Normalized Post

```python
{
    "id": "1234567890",
    "author_id": "9876543210",
    "author_username": "twitter_user",
    "author_name": "Twitter User",
    "text": "This is a tweet",
    "media_urls": ["https://..."],
    "created_at": "2024-01-08T10:00:00.000Z",
    "platform": "twitter",
    "metadata": {
        "public_metrics": {...},
        "entities": {...},
        "attachments": {...}
    }
}
```

## API Request Parameters

### Tweet Fields

```python
tweet_fields = [
    "id",
    "text",
    "author_id",
    "created_at",
    "public_metrics",
    "reply_settings",
    "attachments",
    "geo",
    "entities",
    "referenced_tweets",
    "context_annotations"
]
```

### User Fields

```python
user_fields = [
    "id",
    "username",
    "name",
    "created_at",
    "description",
    "verified",
    "protected",
    "public_metrics",
    "profile_image_url"
]
```

### Media Fields

```python
media_fields = [
    "media_key",
    "type",
    "url",
    "preview_image_url",
    "width",
    "height",
    "alt_text",
    "duration_ms"
]
```

### Expansions

```python
expansions = [
    "author_id",
    "attachments.media_keys",
    "referenced_tweets.id"
]
```

## Usage Examples

### Fetch with Specific Fields

```python
# Request specific fields
comments = await twitter.fetch_comments(
    tweet_id,
    tweet_fields=["created_at", "public_metrics", "author_id"],
    user_fields=["username", "name", "verified"],
    expansions=["author_id"]
)

# Comments include requested data
for comment in comments:
    print(f"@{comment.author_username}: {comment.text}")
    if comment.verified:
        print("  ✓ Verified")
    print(f"  Likes: {comment.metrics.like_count}")
```

### Access Media

```python
comment = await twitter.fetch_comment(comment_id)

if comment.attachments:
    for media in comment.attachments:
        print(f"Media type: {media.type}")
        print(f"URL: {media.url}")
        
        # Moderate media
        if media.type == "image":
            await moderate_image(media.url)
        elif media.type == "video":
            await moderate_video(media.url)
```

### Access Referenced Tweets

```python
comment = await twitter.fetch_comment(comment_id)

if comment.referenced_tweets:
    for ref in comment.referenced_tweets:
        if ref.type == "quoted":
            quoted_tweet = await twitter.fetch_tweet(ref.id)
            print(f"Quoted: {quoted_tweet.text}")
```

## Best Practices

### 1. Request Only Needed Fields

```python
# Good - specific fields
comments = await twitter.fetch_comments(
    tweet_id,
    tweet_fields=["created_at", "public_metrics"]
)

# Bad - all fields
comments = await twitter.fetch_comments(tweet_id)
```

### 2. Use Expansions Efficiently

```python
# Good - include author expansion
comments = await twitter.fetch_comments(
    tweet_id,
    expansions=["author_id"],
    user_fields=["username", "name"]
)
```

### 3. Handle Missing Fields

```python
comment = await twitter.fetch_comment(comment_id)

# Always check if field exists
if hasattr(comment, "public_metrics"):
    likes = comment.public_metrics.like_count
else:
    likes = 0
```

## Related Documentation

- **API Guide**: `./api-guide.md` - API usage
- **Common Patterns**: `../../docs/api-reference/common-patterns.md` - Data normalization
- **Examples**: `./examples/` - Usage examples

---

**Last Updated**: January 2024
**Status**: Phase 2 - Documentation Complete
