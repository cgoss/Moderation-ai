"""Sample Test Data Fixtures"""

from typing import Dict, Any, List
import pytest
from datetime import datetime, timedelta


@pytest.fixture
def sample_comment() -> Dict[str, Any]:
    """Sample comment data for testing"""
    return {
        "id": "comment_test_123",
        "text": "This is a test comment",
        "user_id": "user_test_456",
        "username": "testuser",
        "created_at": "2025-01-08T10:00:00Z",
        "like_count": 10,
        "reply_count": 2,
        "is_pinned": False,
    }


@pytest.fixture
def sample_post() -> Dict[str, Any]:
    """Sample post/article data for testing"""
    return {
        "id": "post_test_789",
        "title": "Test Post Title",
        "content": "<p>This is test post content</p>",
        "author_id": "user_test_456",
        "created_at": "2025-01-08T09:00:00Z",
        "tags": ["test", "moderation"],
        "like_count": 100,
        "comment_count": 25,
    }


@pytest.fixture
def sample_user() -> Dict[str, Any]:
    """Sample user data for testing"""
    return {
        "id": "user_test_456",
        "username": "testuser",
        "display_name": "Test User",
        "profile_picture": "https://example.com/avatar.jpg",
        "is_verified": True,
        "follower_count": 1000,
        "following_count": 500,
    }


@pytest.fixture
def sample_video() -> Dict[str, Any]:
    """Sample video data for testing"""
    return {
        "id": "video_test_012",
        "title": "Test Video Title",
        "description": "Test video description",
        "url": "https://example.com/video.mp4",
        "thumbnail": "https://example.com/thumb.jpg",
        "duration": 60,
        "view_count": 1000,
        "like_count": 500,
        "comment_count": 100,
        "created_at": "2025-01-08T08:00:00Z",
    }


@pytest.fixture
def sample_article() -> Dict[str, Any]:
    """Sample article data for testing (Medium specific)"""
    return {
        "id": "article_test_123",
        "title": "Test Article",
        "content": "<p>Test article content</p>",
        "contentFormat": "html",
        "authorId": "user_test_456",
        "tags": ["test", "moderation"],
        "publishedAt": 1234567890000,
        "url": "https://medium.com/p/test-article",
    }


@pytest.fixture
def sample_media() -> Dict[str, Any]:
    """Sample media data for testing (Instagram specific)"""
    return {
        "id": "media_test_456",
        "caption": "Test caption",
        "media_type": "CAROUSEL_ALBUM",
        "media_url": "https://instagram.com/test.jpg",
        "thumbnail_url": "https://instagram.com/thumb.jpg",
        "timestamp": 1234567890000,
    }


@pytest.fixture
def sample_comments_list(count: int = 5) -> List[Dict[str, Any]]:
    """Generate a list of sample comments"""
    comments = []
    for i in range(count):
        comments.append(
            {
                "id": f"comment_{i}",
                "text": f"Test comment {i}",
                "user_id": f"user_{i}",
                "username": f"testuser{i}",
                "created_at": datetime.now().isoformat(),
                "like_count": i * 10,
                "reply_count": i,
            }
        )
    return comments


@pytest.fixture
def sample_posts_list(count: int = 3) -> List[Dict[str, Any]]:
    """Generate a list of sample posts"""
    posts = []
    for i in range(count):
        posts.append(
            {
                "id": f"post_{i}",
                "title": f"Test Post {i}",
                "content": f"<p>Test content {i}</p>",
                "author_id": f"user_{i}",
                "created_at": datetime.now().isoformat(),
                "tags": ["test", f"tag{i}"],
                "like_count": i * 50,
                "comment_count": i * 10,
            }
        )
    return posts


@pytest.fixture
def sample_videos_list(count: int = 3) -> List[Dict[str, Any]]:
    """Generate a list of sample videos"""
    videos = []
    for i in range(count):
        videos.append(
            {
                "id": f"video_{i}",
                "title": f"Test Video {i}",
                "description": f"Test description {i}",
                "url": f"https://example.com/video{i}.mp4",
                "thumbnail": f"https://example.com/thumb{i}.jpg",
                "duration": 60 + i * 10,
                "view_count": (i + 1) * 500,
                "like_count": (i + 1) * 100,
                "comment_count": (i + 1) * 10,
                "created_at": (datetime.now() + timedelta(hours=i)).isoformat(),
            }
        )
    return videos


@pytest.fixture
def sample_articles_list(count: int = 3) -> List[Dict[str, Any]]:
    """Generate a list of sample articles (Medium specific)"""
    articles = []
    for i in range(count):
        articles.append(
            {
                "id": f"article_{i}",
                "title": f"Test Article {i}",
                "content": f"<p>Test content {i}</p>",
                "contentFormat": "html",
                "authorId": f"user_{i}",
                "tags": ["test", f"tag{i}"],
                "publishedAt": int(
                    (datetime.now() + timedelta(hours=i)).timestamp() * 1000
                ),
                "url": f"https://medium.com/p/test-article-{i}",
            }
        )
    return articles


@pytest.fixture
def sample_media_list(count: int = 3) -> List[Dict[str, Any]]:
    """Generate a list of sample media (Instagram specific)"""
    media_list = []
    for i in range(count):
        media_list.append(
            {
                "id": f"media_{i}",
                "caption": f"Test caption {i}",
                "media_type": "CAROUSEL_ALBUM",
                "media_url": f"https://instagram.com/test{i}.jpg",
                "thumbnail_url": f"https://instagram.com/thumb{i}.jpg",
                "timestamp": int(
                    (datetime.now() + timedelta(hours=i)).timestamp() * 1000
                ),
            }
        )
    return media_list


@pytest.fixture(params=["profanity", "spam", "harassment", "self_promo"])
def flagged_comment(request):
    """Sample flagged comment for testing moderation"""
    flag_type = request.param
    return {
        "id": f"comment_flagged_{flag_type}_123",
        "text": f"Test {flag_type} comment",
        "user_id": f"user_flagged_456",
        "username": f"flaggeduser_{flag_type}",
        "flag_type": flag_type,
        "created_at": datetime.now().isoformat(),
    }


@pytest.fixture(params=["delete", "hide", "flag", "allow"])
def moderation_action(request):
    """Sample moderation action for testing"""
    action_type = request.param
    return {
        "action": action_type,
        "reason": f"Test reason for {action_type}",
        "timestamp": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_analyzed_comment() -> Dict[str, Any]:
    """Sample analyzed comment data"""
    return {
        "comment_id": "comment_test_123",
        "text": "Test comment",
        "profanity": False,
        "spam": False,
        "harassment": False,
        "self_promo": False,
        "severity": "low",
        "confidence": 0.95,
        "analyzed_at": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_moderation_result() -> Dict[str, Any]:
    """Sample moderation result"""
    return {
        "comment_id": "comment_test_123",
        "action": "allow",
        "rule_triggered": None,
        "timestamp": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_rate_limit_info() -> Dict[str, Any]:
    """Sample rate limit information"""
    return {
        "limit": 100,
        "remaining": 95,
        "reset": 1234567890,
        "reset_time": datetime.fromtimestamp(1234567890).isoformat(),
    }


@pytest.fixture
def sample_webhook_event() -> Dict[str, Any]:
    """Sample webhook event"""
    return {
        "event_type": "comment.created",
        "comment_id": "comment_webhook_123",
        "post_id": "post_webhook_456",
        "text": "New comment via webhook",
        "user_id": "user_webhook_789",
        "timestamp": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_error_response(error_type: str = "access_token_invalid") -> Dict[str, Any]:
    """Sample error response"""
    error_messages = {
        "access_token_invalid": "The access token provided is invalid",
        "expired_token": "The access token has expired",
        "rate_limit_exceeded": "Rate limit exceeded",
        "invalid_grant": "Invalid grant type",
        "resource_not_found": "Resource not found",
        "forbidden": "Insufficient permissions",
    }

    return {
        "error": {
            "code": error_type,
            "message": error_messages.get(error_type, "Unknown error"),
        },
        "status_code": 400 if error_type == "invalid_grant" else 401,
    }


@pytest.fixture
def sample_pagination_info() -> Dict[str, Any]:
    """Sample pagination information"""
    return {
        "page": 1,
        "page_size": 20,
        "total_count": 100,
        "total_pages": 5,
        "next_page_token": "next_page_token_123",
        "has_next": True,
    }


@pytest.fixture(params=["short", "medium", "long"])
def comment_length_variations(request):
    """Parameterized fixture for testing comment length"""
    length_type = request.param
    lengths = {
        "short": "Hi",
        "medium": "This is a medium length comment",
        "long": "This is a very long comment with multiple sentences to test various moderation scenarios",
    }
    return {
        "type": length_type,
        "text": lengths[length_type],
        "word_count": len(lengths[length_type].split()),
    }


@pytest.fixture(params=["English", "Spanish", "French"])
def multilingual_comment(request):
    """Parameterized fixture for testing multilingual comments"""
    language = request.param
    comments = {
        "English": "This is a test comment",
        "Spanish": "Este es un comentario de prueba",
        "French": "Ceci est un commentaire de test",
    }
    return {"language": language, "text": comments[language]}


@pytest.fixture
def sample_user_profile() -> Dict[str, Any]:
    """Sample user profile data"""
    return {
        "id": "user_profile_123",
        "username": "testuser",
        "display_name": "Test User",
        "bio": "This is a test bio",
        "profile_picture": "https://example.com/avatar.jpg",
        "is_verified": True,
        "follower_count": 1000,
        "following_count": 500,
        "posts_count": 100,
    }


@pytest.fixture
def sample_post_metrics() -> Dict[str, Any]:
    """Sample post metrics"""
    return {
        "id": "post_metrics_123",
        "like_count": 1000,
        "comment_count": 100,
        "share_count": 50,
        "view_count": 10000,
        "engagement_rate": 0.15,
    }


@pytest.fixture
def sample_comment_thread() -> Dict[str, Any]:
    """Sample comment thread (replies)"""
    return {
        "parent_comment": {
            "id": "comment_parent_123",
            "text": "Parent comment",
            "user_id": "user_parent_456",
            "reply_count": 2,
        },
        "replies": [
            {
                "id": "comment_reply_1",
                "text": "Reply 1",
                "user_id": "user_reply_1",
                "parent_id": "comment_parent_123",
            },
            {
                "id": "comment_reply_2",
                "text": "Reply 2",
                "user_id": "user_reply_2",
                "parent_id": "comment_parent_123",
            },
        ],
        "total_replies": 2,
    }


@pytest.fixture
def sample_batch_results() -> Dict[str, Any]:
    """Sample batch operation results"""
    return {
        "total_processed": 25,
        "successful": 23,
        "failed": 2,
        "errors": [
            {"item_id": "item_5", "error": "Rate limit exceeded"},
            {"item_id": "item_12", "error": "Resource not found"},
        ],
    }
