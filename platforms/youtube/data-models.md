---
title: YouTube Data Models
category: platform
platform: youtube
related:
  - ./README.md
  - ./api-guide.md
  - ../../docs/api-reference/common-patterns.md
---

# YouTube Data Models

## Overview

This document describes the data structures used by YouTube API v3, including videos, comments, channels, and metadata. All data is normalized by Moderation AI library for consistent cross-platform handling.

## Video Model

### Basic Video Structure

```python
{
    "id": "abc123",
    "title": "Video Title",
    "description": "Video description",
    "channel_id": "UC...",
    "channel_title": "Channel Name",
    "created_at": "2024-01-08T10:00:00.000Z",
    "platform": "youtube",
    "url": "https://youtube.com/watch?v=abc123",
    "thumbnails": {
        "default": {
            "url": "https://i.ytimg.com/vi/...",
            "width": 1280,
            "height": 720
        }
    }
}
```

### Video Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique video ID (11 chars) |
| `title` | string | Video title |
| `description` | string | Video description |
| `channel_id` | string | Channel ID |
| `channel_title` | string | Channel display name |
| `created_at` | datetime | Creation timestamp |
| `platform` | string | "youtube" |
| `url` | string | Video URL |
| `thumbnails` | object | Thumbnail images |
| `tags` | array | Video tags |

## Comment Model

### Basic Comment Structure

```python
{
    "id": "def456",
    "video_id": "abc123",
    "author_id": "user789",
    "author_username": "commenter",
    "author_display_name": "Commenter Name",
    "text": "This is a comment",
    "parent_id": "abc123",
    "like_count": 5,
    "updated_at": "2024-01-08T10:05:00.000Z",
    "platform": "youtube"
}
```

### Comment Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique comment ID |
| `video_id` | string | Parent video ID |
| `author_id` | string | Commenter's user ID |
| `author_username` | string | Commenter's channel name |
| `author_display_name` | string | Commenter's display name |
| `text` | string | Comment content |
| `parent_id` | string | Parent comment ID or video ID |
| `like_count` | int | Number of likes |
| `created_at` | datetime | Comment creation timestamp |
| `platform` | string | "youtube" |

## Channel Model

### Basic Channel Structure

```python
{
    "id": "UC...",
    "name": "Channel Name",
    "custom_url": "https://youtube.com/@channelname",
    "subscriber_count": 10000,
    "video_count": 500,
    "view_count": 1000000,
    "created_at": "2010-01-01T00:00:00.000Z",
    "platform": "youtube"
}
```

### Channel Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique channel ID |
| `name` | string | Channel display name |
| `custom_url` | string | Channel URL |
| `subscriber_count` | int | Subscriber count |
| `video_count` | int | Total videos |
| `view_count` | int | Total views |
| `created_at` | datetime | Channel creation date |
| `platform` | string | "youtube" |

## Normalized Data Model

### Normalized Comment

```python
{
    "id": "def456",
    "post_id": "abc123",
    "author_id": "user789",
    "author_username": "commenter",
    "author_name": "Commenter Name",
    "text": "This is a comment",
    "created_at": "2024-01-08T10:05:00.000Z",
    "platform": "youtube",
    "metadata": {
        "like_count": 5,
        "parent_id": "abc123",
        "video_id": "abc123"
    }
}
```

### Normalized Video

```python
{
    "id": "abc123",
    "author_id": "user123",
    "author_username": "channel_name",
    "title": "Video Title",
    "media_urls": ["https://..."],
    "created_at": "2024-01-08T10:00:00.000Z",
    "platform": "youtube",
    "metadata": {
        "subscriber_count": 10000,
        "view_count": 1000000
    }
}
```

## Usage Examples

### Fetch with Specific Fields

```python
# Request specific fields
comments = await youtube.fetch_comments(
    video_id,
    part="snippet",
    fields=["author", "like_count", "created_at"]
)

for comment in comments:
    print(f"@{comment.author_username}: {comment.text}")
    print(f"  Likes: {comment.like_count}")
```

### Access Thumbnails

```python
video = await youtube.fetch_video(video_id)

if video.thumbnails:
    default_thumb = video.thumbnails.default
    print(f"Default: {default_thumb.url}")
    print(f"Size: {default_thumb.width}x{default_thumb.height}")
```

### Access Channel Info

```python
video = await youtube.fetch_video(video_id)

if video.channel_id:
    channel = await youtube.fetch_channel(video.channel_id)
    print(f"Channel: {channel.name}")
    print(f"Subscribers: {channel.subscriber_count}")
```

## Best Practices

### 1. Request Only Needed Fields

```python
# Good - specific fields
comments = await youtube.fetch_comments(
    video_id,
    part="snippet",
    fields=["author", "like_count"]
)

# Bad - all fields (slower)
comments = await youtube.fetch_comments(video_id)
```

### 2. Handle Missing Fields

```python
# Always check if field exists
comment = await youtube.fetch_comment(comment_id)

if hasattr(comment, "like_count"):
    likes = comment.like_count
else:
    likes = 0
```

### 3. Use Pagination

```python
# Good - fetch all pages
result = await youtube.fetch_comments(video_id)
all_comments = result.comments

# Bad - single page
comments = await youtube.fetch_comments(video_id, max_results=100)
```

## Related Documentation

- **API Guide**: `./api-guide.md` - API usage
- **Common Patterns**: `../../docs/api-reference/common-patterns.md` - Data normalization
- **Examples**: `./examples/` - Usage examples

---

**Last Updated**: January 2024
**Status**: Phase 2 - Documentation Complete
