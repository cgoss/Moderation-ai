"""API Mock Objects for Testing"""

from typing import Dict, Any, Optional
from unittest.mock import Mock, AsyncMock
import json
import time


class MockInstagramAPI:
    """Mock Instagram API for testing"""

    def __init__(self):
        self.call_count = 0
        self.called_endpoints = []
        self._media_cache = {}
        self._comments_cache = {}

    def get_media(self, media_id: str) -> Dict[str, Any]:
        """Mock getting Instagram media"""
        self.call_count += 1
        self.called_endpoints.append(("get_media", {"media_id": media_id}))

        if media_id in self._media_cache:
            return self._media_cache[media_id]

        return {
            "id": media_id,
            "caption": "Test caption",
            "media_type": "CAROUSEL_ALBUM",
            "media_url": "https://instagram.com/test.jpg",
            "thumbnail_url": "https://instagram.com/thumb.jpg",
            "timestamp": str(int(time.time())),
            "like_count": 100,
            "comments_count": 50,
        }

    def get_media_comments(self, media_id: str, **kwargs) -> list:
        """Mock getting Instagram comments"""
        self.call_count += 1
        self.called_endpoints.append(("get_media_comments", {"media_id": media_id}))

        if media_id in self._comments_cache:
            return self._comments_cache[media_id]

        return [
            {
                "id": f"comment_{i}",
                "text": f"Test comment {i}",
                "user": {"username": f"testuser{i}", "id": f"user_{i}"},
                "timestamp": str(int(time.time())),
            }
            for i in range(5)
        ]

    def delete_comment(self, comment_id: str) -> bool:
        """Mock deleting Instagram comment"""
        self.call_count += 1
        self.called_endpoints.append(("delete_comment", {"comment_id": comment_id}))
        return True

    def hide_comment(self, comment_id: str) -> bool:
        """Mock hiding Instagram comment"""
        self.call_count += 1
        self.called_endpoints.append(("hide_comment", {"comment_id": comment_id}))
        return True

    def set_media_cache(self, media_id: str, data: Dict):
        """Cache media data"""
        self._media_cache[media_id] = data

    def set_comments_cache(self, media_id: str, comments: list):
        """Cache comments data"""
        self._comments_cache[media_id] = comments

    def reset(self):
        """Reset mock state"""
        self.call_count = 0
        self.called_endpoints = []
        self._media_cache = {}
        self._comments_cache = {}


class MockMediumAPI:
    """Mock Medium API for testing"""

    def __init__(self):
        self.call_count = 0
        self.called_endpoints = []
        self._article_cache = {}
        self._comments_cache = {}

    def get_user_articles(self, user_id: str) -> list:
        """Mock getting Medium user articles"""
        self.call_count += 1
        self.called_endpoints.append(("get_user_articles", {"user_id": user_id}))

        return [
            {
                "id": f"article_{i}",
                "title": f"Test Article {i}",
                "content": f"<p>Test content {i}</p>",
                "authorId": user_id,
                "tags": ["test", "moderation"],
                "publishedAt": int(time.time() * 1000),
                "url": f"https://medium.com/p/test-article-{i}",
            }
            for i in range(3)
        ]

    def get_article_comments(self, article_id: str) -> list:
        """Mock getting Medium article comments"""
        self.call_count += 1
        self.called_endpoints.append(
            ("get_article_comments", {"article_id": article_id})
        )

        if article_id in self._comments_cache:
            return self._comments_cache[article_id]

        return [
            {
                "id": f"comment_{i}",
                "content": f"<p>Test comment {i}</p>",
                "creatorId": f"user_{i}",
                "parentId": article_id,
                "createdAt": int(time.time() * 1000),
            }
            for i in range(3)
        ]

    def delete_comment(self, comment_id: str) -> bool:
        """Mock deleting Medium comment"""
        self.call_count += 1
        self.called_endpoints.append(("delete_comment", {"comment_id": comment_id}))
        return True

    def set_article_cache(self, article_id: str, data: Dict):
        """Cache article data"""
        self._article_cache[article_id] = data

    def set_comments_cache(self, article_id: str, comments: list):
        """Cache comments data"""
        self._comments_cache[article_id] = comments

    def reset(self):
        """Reset mock state"""
        self.call_count = 0
        self.called_endpoints = []
        self._article_cache = {}
        self._comments_cache = {}


class MockTikTokAPI:
    """Mock TikTok API for testing"""

    def __init__(self):
        self.call_count = 0
        self.called_endpoints = []
        self._video_cache = {}
        self._comments_cache = {}

    def get_user_videos(self, cursor: Optional[str] = None) -> list:
        """Mock getting TikTok user videos"""
        self.call_count += 1
        self.called_endpoints.append(("get_user_videos", {"cursor": cursor}))

        return [
            {
                "id": f"video_{i}",
                "title": f"Test Video {i}",
                "video_description": f"Test description {i}",
                "create_time": int(time.time()),
                "cover_image_url": f"https://tiktok.com/thumb_{i}.jpg",
                "share_url": f"https://tiktok.com/@user/video/test-{i}",
                "duration": 60,
            }
            for i in range(3)
        ]

    def get_video_comments(self, video_id: str, cursor: Optional[str] = None) -> list:
        """Mock getting TikTok video comments"""
        self.call_count += 1
        self.called_endpoints.append(("get_video_comments", {"video_id": video_id}))

        if video_id in self._comments_cache:
            return self._comments_cache[video_id]

        return [
            {
                "id": f"comment_{i}",
                "text": f"Test comment {i}",
                "user": {
                    "union_id": f"user_{i}",
                    "display_name": f"Test User {i}",
                    "username": f"testuser{i}",
                    "avatar_url": f"https://tiktok.com/avatar_{i}.jpg",
                    "is_verified": False,
                },
                "video_id": video_id,
                "like_count": i * 10,
                "reply_count": i,
                "create_time": int(time.time()),
            }
            for i in range(3)
        ]

    def delete_comment(self, comment_id: str) -> bool:
        """Mock deleting TikTok comment"""
        self.call_count += 1
        self.called_endpoints.append(("delete_comment", {"comment_id": comment_id}))
        return True

    def pin_comment(self, comment_id: str) -> bool:
        """Mock pinning TikTok comment"""
        self.call_count += 1
        self.called_endpoints.append(("pin_comment", {"comment_id": comment_id}))
        return True

    def set_video_cache(self, video_id: str, data: Dict):
        """Cache video data"""
        self._video_cache[video_id] = data

    def set_comments_cache(self, video_id: str, comments: list):
        """Cache comments data"""
        self._comments_cache[video_id] = comments

    def reset(self):
        """Reset mock state"""
        self.call_count = 0
        self.called_endpoints = []
        self._video_cache = {}
        self._comments_cache = {}


def mock_response_factory(
    status_code: int = 200, data: Optional[Dict] = None, error: Optional[str] = None
) -> Mock:
    """Factory function to create mock API responses"""
    response = Mock()
    response.status_code = status_code

    if error:
        response.json.return_value = {"error": {"code": "error_code", "message": error}}
        response.text = json.dumps({"error": {"code": "error_code", "message": error}})
    else:
        response.json.return_value = {"data": data if data is not None else {}}
        response.text = json.dumps({"data": data if data is not None else {}})

    if status_code >= 400:
        import requests

        response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=Mock(status_code=status_code, text=response.text)
        )
    else:
        response.raise_for_status.side_effect = None

    return response


def create_mock_session(platform: str) -> Mock:
    """Create a mock session for a specific platform"""
    session = Mock()

    if platform == "instagram":
        session.get.return_value = mock_response_factory(
            status_code=200, data={"id": "test_user"}
        )
    elif platform == "medium":
        session.get.return_value = mock_response_factory(
            status_code=200, data={"user": {"id": "test_user"}}
        )
    elif platform == "tiktok":
        session.get.return_value = mock_response_factory(
            status_code=200, data={"user": {"union_id": "test_user"}}
        )

    return session


class MockWebhookEvent:
    """Mock webhook event for testing"""

    def __init__(self, event_type: str, payload: Dict):
        self.event_type = event_type
        self.payload = payload
        self.timestamp = int(time.time())

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "type": self.event_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }


def create_webhook_event(
    event_type: str = "comment.created",
    comment_id: str = "test_comment",
    post_id: str = "test_post",
    text: str = "Test comment",
) -> MockWebhookEvent:
    """Create a mock webhook event"""
    return MockWebhookEvent(
        event_type=event_type,
        payload={
            "comment_id": comment_id,
            "post_id": post_id,
            "text": text,
            "user_id": "test_user",
            "timestamp": int(time.time()),
        },
    )
