---
title: Instagram Data Models
category: platform
platform: instagram
related:
  - ../README.md
  - ./api-guide.md
  - ./authentication.md
  - ./comment-moderation.md
---

# Instagram Data Models

## Overview

This document defines the data structures used throughout the Instagram integration. All data objects should conform to these specifications to ensure consistency and type safety.

## Core Data Models

### Media (Post)

The Media object represents an Instagram post (photo, video, carousel, story, or reel).

```python
from typing import Optional, List, Any, Dict
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Media:
    """
    Represents an Instagram media post.
    """
    id: str
    media_type: str
    media_url: str
    caption: Optional[str]
    thumbnail_url: Optional[str]
    timestamp: str
    like_count: int
    comments_count: int
    owner: 'User'
    is_video: bool
    is_carousel: bool
    is_story: bool
    is_reel: bool
    duration: Optional[float]
    location: Optional[str]
    location_id: Optional[str]
    media_product_type: Optional[str]
    tags: List[str]
    insights: Optional[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Media to dictionary.
        """
        return {
            'id': self.id,
            'media_type': self.media_type,
            'media_url': self.media_url,
            'caption': self.caption,
            'thumbnail_url': self.thumbnail_url,
            'timestamp': self.timestamp,
            'like_count': self.like_count,
            'comments_count': self.comments_count,
            'owner': self.owner,
            'is_video': self.is_video,
            'is_carousel': self.is_carousel,
            'is_story': self.is_story,
            'is_reel': self.is_reel,
            'duration': self.duration,
            'location': self.location,
            'location_id': self.location_id,
            'media_product_type': self.media_product_type,
            'tags': self.tags,
            'insights': self.insights,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Media':
        """
        Create Media from dictionary.
        """
        return cls(
            id=data.get('id'),
            media_type=data.get('media_type', 'image'),
            media_url=data.get('media_url'),
            caption=data.get('caption'),
            thumbnail_url=data.get('thumbnail_url'),
            timestamp=data.get('timestamp', datetime.fromisoformat(data.get('timestamp', '')),
            like_count=data.get('like_count', 0),
            comments_count=data.get('comments_count', 0),
            owner=data.get('owner', ''),
            is_video=data.get('is_video', False),
            is_carousel=data.get('is_carousel', False),
            is_story=data.get('is_story', False),
            is_reel=data.get('is_reel', False),
            duration=data.get('duration'),
            location=data.get('location', ''),
            location_id=data.get('location_id', ''),
            media_product_type=data.get('media_product_type'),
            tags=data.get('tags', []),
            insights=data.get('insights', {}),
        )
```

Media Types:

- **IMAGE**: Static photo post
- **VIDEO**: Video content
- **CAROUSEL**: Multiple media items in one post
- **STORY**: Ephemeral 24-hour content
- **REL**: Short-form video (60 seconds)
- **ALBUM**: Photo album with multiple images
```

### Comment

Represents a comment on Instagram media.

```python
@dataclass
class Comment:
    """
    Represents an Instagram comment.
    """
    id: str
    text: str
    parent_id: Optional[str]
    media_id: str
    author: 'User'
    author_id: str
    username: str
    profile_pic_url: Optional[str]
    timestamp: str
    like_count: int
    replies_count: int
    hidden: bool
    is_owner_comment: bool
    is_reply: bool
    reported: bool
    parent_author_id: Optional[str]
    parent_username: Optional[str]
    reported_reason: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Comment to dictionary.
        """
        return {
            'id': self.id,
            'text': self.text,
            'parent_id': self.parent_id,
            'media_id': self.media_id,
            'author': 'User',
            'author_id': self.author_id,
            'username': self.username,
            'profile_pic_url': self.profile_pic_url,
            'timestamp': self.timestamp,
            'like_count': self.like_count,
            'replies_count': self.replies_count,
            "hidden': self.hidden,
            'is_owner_comment': self.is_owner_comment,
            'is_reply': self.is_reply,
            'reported': self.reported,
            'reported_reason': self.reported_reason,
            'parent_author_id': self.parent_author_id,
            'parent_username': self.parent_username,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Comment':
        """
        Create Comment from dictionary.
        """
        return cls(
            id=data.get('id'),
            text=data.get('text'),
            parent_id=data.get('parent_id', ''),
            media_id=data.get('media_id', ''),
            author=data.get('author', ''),
            author_id=data.get('author_id', ''),
            username=data.get('username', ''),
            profile_pic_url=data.get('profile_pic_url', ''),
            timestamp=data.get('timestamp', datetime.fromisoformat(data.get('timestamp', '')),
            like_count=data.get('like_count', 0),
            replies_count=data.get('replies_count', 0),
            hidden=data.get('hidden', False),
            is_owner_comment=data.get('is_owner_comment', False),
            is_reply=data.get('is_reply', False),
            reported=data.get('reported', False),
            reported_reason=data.get('reported_reason', ''),
            parent_author_id=data.get('parent_author_id', ''),
            parent_username=data.get('parent_username', ''),
        )
```

### User

Represents an Instagram user profile.

```python
@dataclass
class User:
    """
    Represents an Instagram user.
    """
    id: str
    username: str
    full_name: str
    bio: Optional[str]
    profile_pic_url: Optional[str]
    followers_count: int
    following_count: int
    posts_count: int
    is_verified: bool
    is_business_account: bool
    is_private: bool
    media_count: int
    follows_request_count: int
    external_url: Optional[str]
    website: Optional[str]
    account_type: str
    biography: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert User to dictionary.
        """
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'bio': self.bio,
            'profile_pic_url': self.profile_pic_url,
            'followers_count': self.followers_count,
            'following_count': self.following_count,
            'posts_count': self.posts_count,
            'is_verified': self.is_verified,
            'is_business_account': self.is_business_account,
            'is_private': self.is_private,
            'media_count': self.media_count,
            'follows_request_count': self.follows_request_count,
            'external_url': self.external_url,
            'account_type': self.account_type,
            'biography': self.biography,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Create User from dictionary.
        """
        return cls(
            id=data.get('id'),
            username=data.get('username', ''),
            full_name=data.get('full_name', ''),
            bio=data.get('bio', ''),
            profile_pic_url=data.get('profile_pic_url', ''),
            followers_count=data.get('followers_count', 0),
            following_count=data.get('following_count', 0),
            posts_count=data.get('posts_count', 0),
            is_verified=data.get('is_verified', False),
            is_business_account=data.get('is_business_account', False),
            is_private=data.get('is_private', False),
            media_count=data.get('media_count', 0),
            follows_request_count=data.get('follows_request_count', 0),
            external_url=data.get('external_url', ''),
            account_type=data.get('account_type', ''),
            biography=data.get('biography', ''),
        )
```

### Hashtag

Represents a hashtag object.

```python
@dataclass
class Hashtag:
    """
    Represents an Instagram hashtag.
    """
    id: str
    name: str
    media_count: int
    follow_count: int
    is_following: bool
    is_topical: bool
    is_banned: bool
    created_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Hashtag to dictionary.
        """
        return {
            'id': self.id,
            'name': self.name,
            'media_count': self.media_count,
            'follow_count': self.follow_count,
            'is_following': self.is_following,
            'is_topical': self.is_topical,
            'is_banned': self.is_banned,
            'created_at': self.created_at,
        }
```

## API Response Structure

### Fetch Comments Response

```python
{
    "data": [
        {
            "id": "17930746012345678",
            "text": "Great shot!",
            "timestamp": "2024-01-08T10:05:00Z",
            "media_id": "1234567890_4567890",
            "author": {
                "id": "1234567890",
                "username": "photographer_pro"
            },
            "like_count": 25,
            "replies_count": 3,
            "hidden": False
        }
    ],
    "paging": {
        "next_cursor": "QVFzSWVh9dHJ6...",
        "total": 50
    },
    "status": "ok"
}
```

### Get Media Response

```python
{
    "id": "1234567890_4567890",
    "media_type": "image",
    "media_url": "https://instagram.com/p/...",
    "caption": "Beautiful sunset! 📸",
    "thumbnail_url": "https://instagram.com/p/...",
    "timestamp": "2024-01-08T10:00:00Z",
    "like_count": 150,
    "comments_count": 25,
    "owner": {
        "id": "987654321",
        "username": "photographer_pro"
    },
    "is_video": false,
    "is_carousel": false,
    "is_story": false,
    "duration": null,
    "tags": ["sunset", "photography", "sunset"]
}
}
```

## Media Types in Detail

### IMAGE (Photo Post)

```json
{
  "media_type": "image",
  "caption": "Photo description",
  "url": "https://instagram.com/p/CxP1...",
  "thumbnail_url": "https://instagram.com/p/CxP1_thumb.jpg",
  "timestamp": "2024-01-08T10:00:00Z",
  "width": 1080,
  "height": 1080,
  "tags": []
}
```

### VIDEO (Video Post)

```json
{
  "media_type": "video",
  "caption": "Video description",
  "url": "https://instagram.com/p/CxP1...",
  "thumbnail_url": "https://instagram.com/p/CxP1_thumb.jpg",
  "timestamp": "2024-01-08T10:00:00Z",
  "duration": 45.6,
  "width": 720,
  "height": 1280,
  "cover_frame_timestamp": "2024-01-08T10:00:00Z"
  "tags": ["video", "tutorial"]
}
```

### CAROUSEL (Album)

```json
{
  "media_type": "carousel",
  "caption": "Multi-photo post",
  "children": [
    {
      "id": "1234567890_4567891",
      "media_url": "https://instagram.com/p/CxP1_1.jpg",
      "caption": "First photo description",
      "thumbnail_url": "https://instagram.com/p/CxP1_1_thumb.jpg"
      "timestamp": "2024-01-08T10:00:00Z",
      "tags": []
    },
    {
      "id": "1234567890_4567892",
      "media_url": "https://instagram.com/p/CxP1_2.jpg",
      "caption": "Second photo description",
      "thumbnail_url": "https://instagram.com/p/CxP1_2_thumb.jpg",
      "timestamp": "2024-01-08T10:01:00Z",
      "tags": []
    },
    # ... more carousel items
  ]
}
```

### STORY (Ephemeral)

```json
{
  "media_type": "story",
  "caption": "Story content",
  "url": "https://instagram.com/stories/...",
  "timestamp": "2024-01-08T10:00:00Z",
  "duration": 3600,
  "thumbnail_url": "https://instagram.com/stories/1234567890_thumb.jpg",
  "expires_at": "2024-01-09:00:00Z",
  "tags": []
}
```

### REL (Short-form Video)

```json
{
  "media_type": "reel",
  "caption": "Short video description",
  "url": "https://instagram.com/reels/...",
  "timestamp": "2024-01-08T10:00:00Z",
  "duration": 30.0,
  "width": 720,
  "height": 1280,
  "cover_frame_timestamp": "2024-01-08T10:00:00Z",
  "tags": ["shortform", "trending"]
}
```

## Platform-Specific Fields

### Comment Attributes

Instagram comments include these special attributes:

```python
{
    "id": "17845678901234567",
    "text": "This is a reply!",
    "media_id": "1234567890",
    "parent_id": "987654321",
    "author": {
        "id": "1234567890",
        "username": "replier_user"
    },
    "replies_count": 5,
    "hidden": false,
    "timestamp": "2024-01-08T10:05:00Z",
    "reported": false,
    "parent_author_id": "987654321"
    "parent_username": "replier_user"
}
}
```

### Moderation Fields

```python
@dataclass
class ModerationInfo:
    """
    Moderation metadata for comments.
    """
    is_hidden: bool
    hidden_at: Optional[str]
    hidden_by: Optional[str]
    moderation_reason: Optional[str]
    hidden_by: Optional[str]
    flagged_at: Optional[str]
    flagged_by: Optional[str]
    reviewed_at: Optional[str]
    reviewed_by: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ModerationInfo to dictionary.
        """
        return {
            'is_hidden': self.is_hidden,
            'hidden_at': self.hidden_at,
            'moderation_reason': self.moderation_reason,
            'hidden_by': self.hidden_by,
            'flagged_at': self.flagged_at,
            'flagged_by': self.flagged_by,
            'reviewed_at': self.reviewed_by,
        }
```

## Error Response Structures

### Rate Limit Error

```json
{
    "error": {
        "type": "RateLimitError",
        "message": "Rate limit exceeded",
        "code": 429,
        "retry_after": 300
    },
    "request": {
        "endpoint": "/v18/comments/{media_id}",
        "method": "GET",
        "url": "https://graph.instagram.com/v18/1234567890/comments/"
    }
}
```

### Authentication Error

```json
{
    "error": {
        "type": "OAuthError",
        "message": "Authentication failed",
        "code": 401,
    "details": {
            "error_description": "Invalid access token"
            "error_uri": "https://graph.instagram.com/oauth/authorize"
        }
    }
}
```

## Usage Examples

### Creating Media

```python
from moderation_ai.platforms import InstagramAPI

async def create_media_post(image_path: str, caption: str):
    """
    Create a media post.
    """
    instagram = InstagramAPI.from_env()
    
    # Upload image
    media_id = await instagram.create_media(
        image_path=image_path,
        caption=caption,
        tags=["photography", "sunset"]
    )
    
    print(f"Media posted with ID: {media_id}")
    return media_id
```

### Fetching Comments

```python
async def get_media_comments(media_id: str, limit: int = 50):
    """
    Fetch comments for a media post.
    """
    instagram = InstagramAPI.from_env()
    
    comments = await instagram.fetch_comments(media_id, limit=limit)
    
    for comment in comments:
        print(f"Comment by {comment.username}: {comment.text}")
    
    return comments
```

### Fetching User Info

```python
async def get_user_info(username: str):
    """
    Get user profile information.
    """
    Instagram = InstagramAPI.from_env()
    
    user = await instagram.get_user(username=username)
    
    print(f"User: {user.username}")
    print(f"Followers: {user.followers_count}")
    print(f"Verified: {user.is_verified}")
    
    return user
```

## Platform-Specific Considerations

### Comment Volume Handling

Instagram comments can be numerous. Consider:

**Batch Size**: Process in batches of 25-50 comments
**Thread Depth**: Consider reply thread complexity
**Rate Limiting**: 5,000 requests/hour for comment fetching
**Pagination**: Use cursor-based pagination
**Hidden Comments**: Don't count toward fetch limits
**Media Type**: Different content types have different comment patterns

### Data Validation

All Instagram data objects should include:
- Required fields filled
- Valid timestamp formats (ISO 8601)
- Proper type checking for media_type
- Valid integer counts for engagement metrics
- Valid boolean flags for state

## Related Documentation

- **API Guide**: `./api-guide.md` - API usage
- **Authentication**: `./authentication.md` - Auth setup
- **Platform Overview**: `../README.md` - Platform capabilities
- **Comment Moderation**: `./comment-moderation.md` - Moderation guidelines
- **Post Tracking**: `./post-tracking.md` - Post monitoring
- **Rate Limits**: `./rate-limits.md` - Rate limit details

## Platform Status

| Status | Value |
|---------|-------|
| **Last Updated** | January 2024 |
| **API Version** | v18.0+ |
| **Documentation Version** | 1.0 |
| **Implementation Status** | Phase 4 - In Progress |

---

**Platform**: Instagram
**Documentation Version**: 1.0
**Status**: Phase 4 - Documentation In Progress
