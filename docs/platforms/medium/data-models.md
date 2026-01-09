# Medium Data Models

## Overview

This document defines the data models and schemas used for the Medium platform integration, including API response models, internal storage models, and moderation models.

## API Response Models

### User Model

```python
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MediumUser:
    id: str
    username: str
    name: str
    url: str
    image_url: Optional[str] = None
    bio: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'MediumUser':
        """Create from Medium API response"""
        return cls(
            id=data['id'],
            username=data['username'],
            name=data['name'],
            url=data['url'],
            image_url=data.get('imageUrl')
        )
```

### Publication Model

```python
@dataclass
class MediumPublication:
    id: str
    name: str
    description: str
    url: str
    image_url: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'MediumPublication':
        """Create from Medium API response"""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            url=data['url'],
            image_url=data.get('imageUrl')
        )
```

### Article Model

```python
@dataclass
class MediumArticle:
    id: str
    title: str
    author_id: str
    url: str
    tags: list[str]
    published_at: int
    content: Optional[str] = None
    content_format: Optional[str] = None
    image_url: Optional[str] = None
    word_count: Optional[int] = None
    reading_time: Optional[float] = None
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'MediumArticle':
        """Create from Medium API response"""
        return cls(
            id=data['id'],
            title=data['title'],
            author_id=data['authorId'],
            url=data['url'],
            tags=data.get('tags', []),
            published_at=data['publishedAt'],
            content=data.get('content'),
            content_format=data.get('contentFormat'),
            image_url=data.get('imageUrl')
        )
    
    @property
    def published_date(self) -> datetime:
        """Convert published_at to datetime"""
        return datetime.fromtimestamp(self.published_at / 1000)
```

### Comment (Response) Model

```python
@dataclass
class MediumComment:
    id: str
    creator_id: str
    content: str
    parent_id: str
    created_at: int
    content_format: str
    vote_count: Optional[int] = None
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'MediumComment':
        """Create from Medium API response"""
        return cls(
            id=data['id'],
            creator_id=data['creatorId'],
            content=data['content'],
            parent_id=data['parentId'],
            created_at=data['createdAt'],
            content_format=data.get('contentFormat', 'html'),
            vote_count=data.get('voteCount')
        )
    
    @property
    def created_date(self) -> datetime:
        """Convert created_at to datetime"""
        return datetime.fromtimestamp(self.created_at / 1000)
```

## Internal Storage Models

### Tracked Article Model

```python
from typing import Optional, Dict, Any
import json

@dataclass
class TrackedArticle:
    id: str
    title: str
    author_id: str
    url: str
    tags: list[str]
    published_at: int
    tracked_at: str
    last_updated: str
    last_comment_check: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TrackedArticle':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            title=data['title'],
            author_id=data['author_id'],
            url=data['url'],
            tags=data['tags'],
            published_at=data['published_at'],
            tracked_at=data['tracked_at'],
            last_updated=data['last_updated'],
            last_comment_check=data.get('last_comment_check'),
            metadata=data.get('metadata')
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'author_id': self.author_id,
            'url': self.url,
            'tags': self.tags,
            'published_at': self.published_at,
            'tracked_at': self.tracked_at,
            'last_updated': self.last_updated,
            'last_comment_check': self.last_comment_check,
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
    contains_link: bool
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
            contains_link=data['contains_link'],
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
            'contains_link': self.contains_link,
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
    HIDE = "hide"
    REVIEW = "review"

@dataclass
class ModerationAction:
    comment_id: str
    article_id: str
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
            article_id=data['article_id'],
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
            'article_id': self.article_id,
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

### Articles Table

```sql
CREATE TABLE tracked_articles (
    id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    author_id VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    tags JSON,
    published_at BIGINT NOT NULL,
    tracked_at VARCHAR(255) NOT NULL,
    last_updated VARCHAR(255) NOT NULL,
    last_comment_check VARCHAR(255),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_tracked_articles_author_id ON tracked_articles(author_id);
CREATE INDEX idx_tracked_articles_published_at ON tracked_articles(published_at);
```

### Comments Table

```sql
CREATE TABLE medium_comments (
    id VARCHAR(255) PRIMARY KEY,
    article_id VARCHAR(255) NOT NULL,
    creator_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    parent_id VARCHAR(255) NOT NULL,
    created_at BIGINT NOT NULL,
    content_format VARCHAR(50),
    vote_count INTEGER DEFAULT 0,
    moderated BOOLEAN DEFAULT FALSE,
    moderation_action VARCHAR(50),
    FOREIGN KEY (article_id) REFERENCES tracked_articles(id) ON DELETE CASCADE
);

CREATE INDEX idx_medium_comments_article_id ON medium_comments(article_id);
CREATE INDEX idx_medium_comments_creator_id ON medium_comments(creator_id);
CREATE INDEX idx_medium_comments_created_at ON medium_comments(created_at);
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
    contains_link BOOLEAN NOT NULL,
    severity VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    analyzed_at VARCHAR(255) NOT NULL,
    FOREIGN KEY (comment_id) REFERENCES medium_comments(id) ON DELETE CASCADE
);

CREATE INDEX idx_comment_analyses_severity ON comment_analyses(severity);
```

### Moderation Actions Table

```sql
CREATE TABLE moderation_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comment_id VARCHAR(255) NOT NULL,
    article_id VARCHAR(255) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    rule_triggered VARCHAR(255) NOT NULL,
    timestamp VARCHAR(255) NOT NULL,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    FOREIGN KEY (comment_id) REFERENCES medium_comments(id) ON DELETE CASCADE,
    FOREIGN KEY (article_id) REFERENCES tracked_articles(id) ON DELETE CASCADE
);

CREATE INDEX idx_moderation_actions_article_id ON moderation_actions(article_id);
CREATE INDEX idx_moderation_actions_timestamp ON moderation_actions(timestamp);
```

## API Request/Response Schemas

### List Articles Request

```python
@dataclass
class ListArticlesRequest:
    author_id: Optional[str] = None
    publication_id: Optional[str] = None
    limit: Optional[int] = 10
    
    def validate(self) -> bool:
        """Validate request parameters"""
        if self.author_id and self.publication_id:
            return False
        return True
```

### List Articles Response

```python
@dataclass
class ListArticlesResponse:
    articles: list[MediumArticle]
    total: int
    next_page_token: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'ListArticlesResponse':
        """Create from Medium API response"""
        articles = [
            MediumArticle.from_api_response(article_data)
            for article_data in data.get('data', [])
        ]
        
        return cls(
            articles=articles,
            total=len(articles),
            next_page_token=data.get('nextPageToken')
        )
```

### List Comments Request

```python
@dataclass
class ListCommentsRequest:
    article_id: str
    limit: Optional[int] = 100
    since: Optional[int] = None
    
    def validate(self) -> bool:
        """Validate request parameters"""
        if not self.article_id:
            return False
        return True
```

### List Comments Response

```python
@dataclass
class ListCommentsResponse:
    comments: list[MediumComment]
    total: int
    next_page_token: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'ListCommentsResponse':
        """Create from Medium API response"""
        comments = [
            MediumComment.from_api_response(comment_data)
            for comment_data in data.get('data', [])
        ]
        
        return cls(
            comments=comments,
            total=len(comments),
            next_page_token=data.get('nextPageToken')
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
class MediumError:
    code: int
    message: str
    details: Optional[dict] = None
    
    @classmethod
    def from_api_response(cls, data: dict) -> 'MediumError':
        """Create from Medium API error response"""
        errors = data.get('errors', [])
        if errors:
            return cls(
                code=errors[0].get('code', 0),
                message=errors[0].get('message', 'Unknown error'),
                details=errors[0]
            )
        return cls(code=0, message='Unknown error')
```

## JSON Schema Examples

### Article JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "id": {"type": "string"},
    "title": {"type": "string"},
    "authorId": {"type": "string"},
    "url": {"type": "string"},
    "tags": {
      "type": "array",
      "items": {"type": "string"}
    },
    "publishedAt": {"type": "integer"},
    "content": {"type": "string"},
    "contentFormat": {"type": "string"},
    "imageUrl": {"type": "string"}
  },
  "required": ["id", "title", "authorId", "url", "publishedAt"]
}
```

### Comment JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "id": {"type": "string"},
    "creatorId": {"type": "string"},
    "content": {"type": "string"},
    "parentId": {"type": "string"},
    "createdAt": {"type": "integer"},
    "contentFormat": {"type": "string"},
    "voteCount": {"type": "integer"}
  },
  "required": ["id", "creatorId", "content", "parentId", "createdAt"]
}
```

## Summary

The Medium data models provide:
- API response models for user, publication, article, and comment data
- Internal storage models for tracked articles and comment analysis
- Moderation models for rules and actions
- Database schemas for persistence
- API request/response schemas
- Utility models for pagination and error handling
