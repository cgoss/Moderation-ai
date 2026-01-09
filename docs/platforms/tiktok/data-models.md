# TikTok Data Models

## Overview

This document defines the data models and schemas used for the TikTok platform integration, including API response models, internal storage models, and moderation models.

## API Response Models

### User Model

```python
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TikTokUser:
    union_id: str
    display_name: str
    avatar_url: str
    username: str
    is_verified: bool
    avatar_url_100: Optional[str] = None
    avatar_large_url: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'TikTokUser':
        """Create from TikTok API response"""
        return cls(
            union_id=data['union_id'],
            display_name=data['display_name'],
            avatar_url=data['avatar_url'],
            username=data['username'],
            is_verified=data.get('is_verified', False),
            avatar_url_100=data.get('avatar_url_100'),
            avatar_large_url=data.get('avatar_large_url')
        )
```

### Video Model

```python
@dataclass
class TikTokVideo:
    id: str
    title: str
    video_description: str
    create_time: int
    cover_image_url: str
    share_url: str
    duration: int
    height: int
    width: int
    embed_html: Optional[str] = None
    embed_link: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'TikTokVideo':
        """Create from TikTok API response"""
        return cls(
            id=data['id'],
            title=data.get('title', ''),
            video_description=data.get('video_description', ''),
            create_time=data['create_time'],
            cover_image_url=data['cover_image_url'],
            share_url=data['share_url'],
            duration=data['duration'],
            height=data['height'],
            width=data['width'],
            embed_html=data.get('embed_html'),
            embed_link=data.get('embed_link')
        )
    
    @property
    def created_date(self) -> datetime:
        """Convert create_time to datetime"""
        return datetime.fromtimestamp(self.create_time)
```

### Comment Model

```python
@dataclass
class TikTokComment:
    id: str
    video_id: str
    text: str
    user: TikTokUser
    like_count: int
    reply_count: int
    create_time: int
    parent_comment_id: Optional[str] = None
    is_pinned: bool = False
    reply_to_comment_id: Optional[str] = None
    reply_to_user: Optional[TikTokUser] = None
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'TikTokComment':
        """Create from TikTok API response"""
        user_data = data.get('user', {})
        user = TikTokUser.from_api_response(user_data)
        
        reply_to_user_data = data.get('reply_to_user')
        reply_to_user = TikTokUser.from_api_response(
            reply_to_user_data) if reply_to_user_data else None
        
        return cls(
            id=data['id'],
            video_id=data['video_id'],
            text=data['text'],
            user=user,
            like_count=data.get('like_count', 0),
            reply_count=data.get('reply_count', 0),
            create_time=data['create_time'],
            parent_comment_id=data.get('parent_comment_id'),
            is_pinned=data.get('is_pinned', False),
            reply_to_comment_id=data.get('reply_to_comment_id'),
            reply_to_user=reply_to_user
        )
    
    @property
    def created_date(self) -> datetime:
        """Convert create_time to datetime"""
        return datetime.fromtimestamp(self.create_time)
```

## Internal Storage Models

### Tracked Video Model

```python
from typing import Optional, Dict, Any
import json

@dataclass
class TrackedVideo:
    id: str
    title: str
    description: str
    create_time: int
    share_url: str
    tracked_at: str
    last_updated: str
    last_comment_check: Optional[str] = None
    total_comments: int = 0
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TrackedVideo':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            create_time=data['create_time'],
            share_url=data['share_url'],
            tracked_at=data['tracked_at'],
            last_updated=data['last_updated'],
            last_comment_check=data.get('last_comment_check'),
            total_comments=data.get('total_comments', 0),
            metadata=data.get('metadata')
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'create_time': self.create_time,
            'share_url': self.share_url,
            'tracked_at': self.tracked_at,
            'last_updated': self.last_updated,
            'last_comment_check': self.last_comment_check,
            'total_comments': self.total_comments,
            'metadata': self.metadata
        }
```

### Comment Analysis Model

```python
from enum import Enum

class ModerationSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class CommentAnalysis:
    comment_id: str
    text: str
    word_count: int
    char_count: int
    profanity_detected: bool
    spam_detected: bool
    harassment_detected: bool
    self_promo_detected: bool
    contains_link: bool
    contains_mention: bool
    contains_hashtag: bool
    severity: ModerationSeverity
    confidence: float
    analyzed_at: str
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CommentAnalysis':
        """Create from dictionary"""
        return cls(
            comment_id=data['comment_id'],
            text=data['text'],
            word_count=data['word_count'],
            char_count=data['char_count'],
            profanity_detected=data['profanity_detected'],
            spam_detected=data['spam_detected'],
            harassment_detected=data['harassment_detected'],
            self_promo_detected=data['self_promo_detected'],
            contains_link=data['contains_link'],
            contains_mention=data['contains_mention'],
            contains_hashtag=data['contains_hashtag'],
            severity=ModerationSeverity(data['severity']),
            confidence=data['confidence'],
            analyzed_at=data['analyzed_at']
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'comment_id': self.comment_id,
            'text': self.text,
            'word_count': self.word_count,
            'char_count': self.char_count,
            'profanity_detected': self.profanity_detected,
            'spam_detected': self.spam_detected,
            'harassment_detected': self.harassment_detected,
            'self_promo_detected': self.self_promo_detected,
            'contains_link': self.contains_link,
            'contains_mention': self.contains_mention,
            'contains_hashtag': self.contains_hashtag,
            'severity': self.severity.value,
            'confidence': self.confidence,
            'analyzed_at': self.analyzed_at
        }
```

## Moderation Models

### Moderation Action Model

```python
class ModerationActionType(Enum):
    ALLOW = "allow"
    FLAG = "flag"
    DELETE = "delete"
    PIN = "pin"
    REPLY = "reply"
    REVIEW = "review"

@dataclass
class ModerationAction:
    comment_id: str
    video_id: str
    action_type: ModerationActionType
    rule_triggered: str
    timestamp: str
    success: bool = True
    error_message: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ModerationAction':
        """Create from dictionary"""
        return cls(
            comment_id=data['comment_id'],
            video_id=data['video_id'],
            action_type=ModerationActionType(data['action_type']),
            rule_triggered=data['rule_triggered'],
            timestamp=data['timestamp'],
            success=data['success'],
            error_message=data.get('error_message')
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'comment_id': self.comment_id,
            'video_id': self.video_id,
            'action_type': self.action_type.value,
            'rule_triggered': self.rule_triggered,
            'timestamp': self.timestamp,
            'success': self.success,
            'error_message': self.error_message
        }
```

### Moderation Rule Model

```python
@dataclass
class ModerationRule:
    name: str
    priority: int
    condition: str
    action: ModerationActionType
    enabled: bool = True
    created_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ModerationRule':
        """Create from dictionary"""
        return cls(
            name=data['name'],
            priority=data['priority'],
            condition=data['condition'],
            action=ModerationActionType(data['action']),
            enabled=data.get('enabled', True),
            created_at=data.get('created_at')
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'priority': self.priority,
            'condition': self.condition,
            'action': self.action.value,
            'enabled': self.enabled,
            'created_at': self.created_at
        }
```

## Database Schemas

### Videos Table

```sql
CREATE TABLE tracked_videos (
    id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    create_time BIGINT NOT NULL,
    share_url VARCHAR(500) NOT NULL,
    tracked_at VARCHAR(255) NOT NULL,
    last_updated VARCHAR(255) NOT NULL,
    last_comment_check VARCHAR(255),
    total_comments INTEGER DEFAULT 0,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_tracked_videos_create_time ON tracked_videos(create_time);
```

### Comments Table

```sql
CREATE TABLE tiktok_comments (
    id VARCHAR(255) PRIMARY KEY,
    video_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    username VARCHAR(255),
    text TEXT NOT NULL,
    like_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    create_time BIGINT NOT NULL,
    parent_comment_id VARCHAR(255),
    is_pinned BOOLEAN DEFAULT FALSE,
    moderated BOOLEAN DEFAULT FALSE,
    moderation_action VARCHAR(50),
    FOREIGN KEY (video_id) REFERENCES tracked_videos(id) ON DELETE CASCADE
);

CREATE INDEX idx_tiktok_comments_video_id ON tiktok_comments(video_id);
CREATE INDEX idx_tiktok_comments_user_id ON tiktok_comments(user_id);
CREATE INDEX idx_tiktok_comments_create_time ON tiktok_comments(create_time);
```

### Comment Analyses Table

```sql
CREATE TABLE comment_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comment_id VARCHAR(255) NOT NULL UNIQUE,
    text TEXT NOT NULL,
    word_count INTEGER NOT NULL,
    char_count INTEGER NOT NULL,
    profanity_detected BOOLEAN NOT NULL,
    spam_detected BOOLEAN NOT NULL,
    harassment_detected BOOLEAN NOT NULL,
    self_promo_detected BOOLEAN NOT NULL,
    contains_link BOOLEAN NOT NULL,
    contains_mention BOOLEAN NOT NULL,
    contains_hashtag BOOLEAN NOT NULL,
    severity VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    analyzed_at VARCHAR(255) NOT NULL,
    FOREIGN KEY (comment_id) REFERENCES tiktok_comments(id) ON DELETE CASCADE
);

CREATE INDEX idx_comment_analyses_severity ON comment_analyses(severity);
```

### Moderation Actions Table

```sql
CREATE TABLE moderation_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comment_id VARCHAR(255) NOT NULL,
    video_id VARCHAR(255) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    rule_triggered VARCHAR(255) NOT NULL,
    timestamp VARCHAR(255) NOT NULL,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    FOREIGN KEY (comment_id) REFERENCES tiktok_comments(id) ON DELETE CASCADE,
    FOREIGN KEY (video_id) REFERENCES tracked_videos(id) ON DELETE CASCADE
);

CREATE INDEX idx_moderation_actions_video_id ON moderation_actions(video_id);
CREATE INDEX idx_moderation_actions_timestamp ON moderation_actions(timestamp);
```

## API Request/Response Schemas

### List Videos Request

```python
@dataclass
class ListVideosRequest:
    cursor: Optional[str] = None
    max_count: Optional[int] = 20
    
    def validate(self) -> bool:
        """Validate request parameters"""
        return self.max_count <= 20
```

### List Videos Response

```python
@dataclass
class ListVideosResponse:
    videos: list[TikTokVideo]
    has_more: bool
    cursor: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'ListVideosResponse':
        """Create from TikTok API response"""
        videos = [
            TikTokVideo.from_api_response(video_data)
            for video_data in data.get('videos', [])
        ]
        
        return cls(
            videos=videos,
            has_more=data.get('has_more', False),
            cursor=data.get('cursor')
        )
```

### List Comments Request

```python
@dataclass
class ListCommentsRequest:
    video_id: str
    cursor: Optional[str] = None
    max_count: Optional[int] = 100
    
    def validate(self) -> bool:
        """Validate request parameters"""
        if not self.video_id:
            return False
        return self.max_count <= 100
```

### List Comments Response

```python
@dataclass
class ListCommentsResponse:
    comments: list[TikTokComment]
    has_more: bool
    cursor: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'ListCommentsResponse':
        """Create from TikTok API response"""
        comments = [
            TikTokComment.from_api_response(comment_data)
            for comment_data in data.get('comments', [])
        ]
        
        return cls(
            comments=comments,
            has_more=data.get('has_more', False),
            cursor=data.get('cursor')
        )
```

## Utility Models

### Pagination Model

```python
@dataclass
class Pagination:
    page: int
    page_size: int
    total_count: int
    total_pages: int
    
    @classmethod
    def from_params(cls, page: int, page_size: int, total_count: int) -> 'Pagination':
        """Create from parameters"""
        total_pages = (total_count + page_size - 1) // page_size
        return cls(
            page=page,
            page_size=page_size,
            total_count=total_count,
            total_pages=total_pages
        )
```

### Error Model

```python
@dataclass
class TikTokError:
    code: str
    message: str
    log_id: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'TikTokError':
        """Create from TikTok API error response"""
        error_data = data.get('error', {})
        return cls(
            code=error_data.get('code', 'unknown_error'),
            message=error_data.get('message', 'Unknown error'),
            log_id=error_data.get('log_id')
        )
```

## JSON Schema Examples

### Video JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "id": {"type": "string"},
    "title": {"type": "string"},
    "video_description": {"type": "string"},
    "create_time": {"type": "integer"},
    "cover_image_url": {"type": "string"},
    "share_url": {"type": "string"},
    "duration": {"type": "integer"},
    "height": {"type": "integer"},
    "width": {"type": "integer"}
  },
  "required": ["id", "create_time", "cover_image_url", "share_url"]
}
```

### Comment JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "id": {"type": "string"},
    "video_id": {"type": "string"},
    "text": {"type": "string"},
    "like_count": {"type": "integer"},
    "reply_count": {"type": "integer"},
    "create_time": {"type": "integer"},
    "is_pinned": {"type": "boolean"},
    "user": {
      "type": "object",
      "properties": {
        "union_id": {"type": "string"},
        "display_name": {"type": "string"},
        "username": {"type": "string"}
      }
    }
  },
  "required": ["id", "video_id", "text", "create_time", "user"]
}
```

## Summary

The TikTok data models provide:
- API response models for user, video, and comment data
- Internal storage models for tracked videos and comment analysis
- Moderation models for rules and actions
- Database schemas for persistence
- API request/response schemas
- Utility models for pagination and error handling
