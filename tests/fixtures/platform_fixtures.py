"""Platform-Specific Test Fixtures"""

from typing import Dict, Any, Generator
import pytest
from unittest.mock import Mock, patch

from .api_mocks import (
    MockInstagramAPI,
    MockMediumAPI,
    MockTikTokAPI,
    create_mock_session,
)
from .auth_fixtures import (
    valid_auth_token,
    auth_headers,
    instagram_auth_config,
    medium_auth_config,
    tiktok_auth_config,
)


@pytest.fixture
def instagram_config() -> Dict[str, Any]:
    """Instagram configuration fixture"""
    return {
        "client_id": "test_instagram_client_id",
        "client_secret": "test_instagram_client_secret",
        "redirect_uri": "http://localhost:8080/callback",
        "access_token": "test_instagram_token",
        "api_base_url": "https://graph.instagram.com",
    }


@pytest.fixture
def medium_config() -> Dict[str, Any]:
    """Medium configuration fixture"""
    return {
        "client_id": "test_medium_client_id",
        "client_secret": "test_medium_client_secret",
        "redirect_uri": "http://localhost:8080/callback",
        "access_token": "test_medium_token",
        "api_base_url": "https://api.medium.com/v1",
    }


@pytest.fixture
def tiktok_config() -> Dict[str, Any]:
    """TikTok configuration fixture"""
    return {
        "client_key": "test_tiktok_client_key",
        "client_secret": "test_tiktok_client_secret",
        "redirect_uri": "http://localhost:8080/callback",
        "access_token": "test_tiktok_token",
        "api_base_url": "https://open.tiktokapis.com/v2",
    }


@pytest.fixture
def instagram_client(instagram_config: Dict[str, Any]) -> MockInstagramAPI:
    """Instagram client fixture"""
    client = MockInstagramAPI()
    client.config = instagram_config
    return client


@pytest.fixture
def medium_client(medium_config: Dict[str, Any]) -> MockMediumAPI:
    """Medium client fixture"""
    client = MockMediumAPI()
    client.config = medium_config
    return client


@pytest.fixture
def tiktok_client(tiktok_config: Dict[str, Any]) -> MockTikTokAPI:
    """TikTok client fixture"""
    client = MockTikTokAPI()
    client.config = tiktok_config
    return client


@pytest.fixture
def mock_rate_limiter():
    """Mock rate limiter for testing"""
    limiter = Mock()
    limiter.wait_if_needed.return_value = None
    limiter.check_rate_limit.return_value = True
    limiter.get_rate_limit_info.return_value = {
        "limit": 100,
        "remaining": 95,
        "reset": 1234567890,
    }
    limiter.record_request.return_value = None
    return limiter


@pytest.fixture
def mock_moderation_engine():
    """Mock moderation engine for testing"""
    engine = Mock()
    engine.analyze_comment.return_value = {
        "profanity": False,
        "spam": False,
        "harassment": False,
        "severity": "low",
    }
    engine.evaluate_rules.return_value = "allow"
    return engine


@pytest.fixture
def mock_action_executor():
    """Mock action executor for testing"""
    executor = Mock()
    executor.delete_comment.return_value = True
    executor.hide_comment.return_value = True
    executor.pin_comment.return_value = True
    executor.flag_comment.return_value = True
    executor.reply_to_comment.return_value = True
    return executor


@pytest.fixture
def mock_comment_tracker():
    """Mock comment tracker for testing"""
    tracker = Mock()
    tracker.get_new_comments.return_value = []
    tracker.track_comment.return_value = None
    tracker.is_comment_tracked.return_value = False
    return tracker


@pytest.fixture
def mock_post_tracker():
    """Mock post/article tracker for testing"""
    tracker = Mock()
    tracker.get_new_posts.return_value = []
    tracker.track_post.return_value = None
    tracker.is_post_tracked.return_value = False
    return tracker


@pytest.fixture
def mock_storage_manager():
    """Mock storage manager for testing"""
    manager = Mock()
    manager.save_post.return_value = None
    manager.save_comment.return_value = None
    manager.get_post.return_value = None
    manager.get_comment.return_value = None
    manager.delete_post.return_value = True
    manager.delete_comment.return_value = True
    return manager


@pytest.fixture
def mock_webhook_handler():
    """Mock webhook handler for testing"""
    handler = Mock()
    handler.verify_signature.return_value = True
    handler.handle_event.return_value = None
    handler.register_handler.return_value = None
    return handler


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    logger = Mock()
    logger.info.return_value = None
    logger.warning.return_value = None
    logger.error.return_value = None
    logger.debug.return_value = None
    return logger


@pytest.fixture
def mock_metrics_collector():
    """Mock metrics collector for testing"""
    collector = Mock()
    collector.increment_counter.return_value = None
    collector.record_gauge.return_value = None
    collector.record_histogram.return_value = None
    collector.record_timing.return_value = None
    return collector


@pytest.fixture(params=["instagram", "medium", "tiktok"])
def platform_client(request):
    """Parameterized fixture for different platform clients"""
    platform = request.param

    if platform == "instagram":
        from .api_mocks import MockInstagramAPI

        return MockInstagramAPI()
    elif platform == "medium":
        from .api_mocks import MockMediumAPI

        return MockMediumAPI()
    elif platform == "tiktok":
        from .api_mocks import MockTikTokAPI

        return MockTikTokAPI()

    return Mock()


@pytest.fixture
def mock_session(platform: str = "instagram") -> Mock:
    """Create a mock session for a specific platform"""
    return create_mock_session(platform)


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing"""
    client = Mock()
    client.get.return_value = Mock(status_code=200, json=lambda: {"data": {}})
    client.post.return_value = Mock(status_code=200, json=lambda: {"data": {}})
    client.delete.return_value = Mock(status_code=204, json=lambda: {})
    return client


@pytest.fixture
def mock_cache():
    """Mock cache for testing"""
    cache = Mock()
    cache.get.return_value = None
    cache.set.return_value = None
    cache.delete.return_value = None
    cache.clear.return_value = None
    return cache


@pytest.fixture
def mock_auth_manager():
    """Mock authentication manager for testing"""
    manager = Mock()
    manager.get_token.return_value = valid_auth_token()
    manager.save_token.return_value = None
    manager.is_token_expired.return_value = False
    manager.refresh_token.return_value = {
        "access_token": "new_token_456",
        "refresh_token": "new_refresh_789",
    }
    return manager


@pytest.fixture
def instagram_api_mocks(instagram_client: MockInstagramAPI) -> Generator:
    """Context manager for Instagram API mocks"""
    with patch("src.platforms.instagram.client.InstagramAPIClient") as mock_client:
        mock_client.return_value = instagram_client
        yield instagram_client


@pytest.fixture
def medium_api_mocks(medium_client: MockMediumAPI) -> Generator:
    """Context manager for Medium API mocks"""
    with patch("src.platforms.medium.client.MediumAPIClient") as mock_client:
        mock_client.return_value = medium_client
        yield medium_client


@pytest.fixture
def tiktok_api_mocks(tiktok_client: MockTikTokAPI) -> Generator:
    """Context manager for TikTok API mocks"""
    with patch("src.platforms.tiktok.client.TikTokAPIClient") as mock_client:
        mock_client.return_value = tiktok_client
        yield tiktok_client


@pytest.fixture
def mock_request_session():
    """Mock requests session for testing"""
    with patch("requests.Session") as mock_session:
        mock_session.return_value = Mock()
        yield mock_session.return_value


@pytest.fixture
def mock_async_http_client():
    """Mock async HTTP client for testing"""
    client = Mock()
    client.get.return_value = Mock()
    client.post.return_value = Mock()
    client.delete.return_value = Mock()
    return client


@pytest.fixture
def test_database():
    """In-memory test database"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, declarative_base

    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    yield SessionLocal

    engine.dispose()


@pytest.fixture
def mock_orm_session():
    """Mock ORM session for testing"""
    session = Mock()
    session.add.return_value = None
    session.commit.return_value = None
    session.rollback.return_value = None
    session.query.return_value = Mock()
    session.flush.return_value = None
    return session


@pytest.fixture
def sample_platform_configs():
    """Sample configurations for all platforms"""
    return {
        "instagram": instagram_auth_config(),
        "medium": medium_auth_config(),
        "tiktok": tiktok_auth_config(),
    }


@pytest.fixture
def mock_token_store():
    """Mock token store for testing"""
    store = Mock()
    store.get_token.return_value = valid_auth_token()
    store.set_token.return_value = None
    store.delete_token.return_value = None
    store.refresh_token.return_value = {
        "access_token": "new_token",
        "expires_at": 9999999999,
    }
    return store


@pytest.fixture
def mock_api_response(status_code: int = 200, data: Any = None):
    """Create mock API response"""
    from unittest.mock import Mock
    import json

    response = Mock()
    response.status_code = status_code

    if data:
        response.json.return_value = {"data": data}
        response.text = json.dumps({"data": data})
    else:
        response.json.return_value = {"data": {}}
        response.text = json.dumps({"data": {}})

    response.raise_for_status.return_value = None
    return response


@pytest.fixture
def mock_error_response(
    status_code: int = 401,
    error_code: str = "invalid_token",
    error_message: str = "Invalid token",
):
    """Create mock error response"""
    from unittest.mock import Mock
    import json

    response = Mock()
    response.status_code = status_code
    response.json.return_value = {
        "error": {"code": error_code, "message": error_message}
    }
    response.text = json.dumps(
        {"error": {"code": error_code, "message": error_message}}
    )
    return response


@pytest.fixture
def mock_pagination_result():
    """Mock pagination result"""
    return {
        "items": [],
        "next_page_token": "next_page_123",
        "has_more": True,
        "total_count": 100,
    }


@pytest.fixture(params=["instagram", "medium", "tiktok"])
def platform_specific_mock(request):
    """Parameterized fixture for platform-specific mocks"""
    platform = request.param

    if platform == "instagram":
        from .api_mocks import MockInstagramAPI

        return MockInstagramAPI()
    elif platform == "medium":
        from .api_mocks import MockMediumAPI

        return MockMediumAPI()
    elif platform == "tiktok":
        from .api_mocks import MockTikTokAPI

        return MockTikTokAPI()

    return Mock()


@pytest.fixture
def mock_webhook_event():
    """Mock webhook event for testing"""
    return {
        "type": "comment.created",
        "data": {
            "comment_id": "webhook_comment_123",
            "text": "Test webhook comment",
            "user_id": "webhook_user_456",
        },
        "timestamp": "2025-01-08T10:00:00Z",
    }


@pytest.fixture
def mock_batch_operation():
    """Mock batch operation for testing"""
    operation = Mock()
    operation.process.return_value = {"successful": 10, "failed": 0, "total": 10}
    operation.get_progress.return_value = 100
    return operation
