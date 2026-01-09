# Pytest Configuration and Fixtures
# conftest.py - Test configuration and fixtures

import os
import pytest
import asyncio
import tempfile
from typing import Generator, Dict, Any
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta
import json

# Environment configuration
TEST_ENV = os.getenv("TEST_ENV", "local")
CI_ENV = os.getenv("CI", "false").lower() == "true"

# Test configuration
pytest_plugins = ["pytest_asyncio", "pytest_cov", "pytest_mock"]

# Async test configuration
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"


# Skip decorators
def skip_ci(reason: str):
    """Decorator to skip tests in CI"""
    return pytest.mark.skipif(CI_ENV, reason=reason)


def can_use_network() -> bool:
    """Check if network access is available"""
    return os.getenv("ALLOW_NETWORK_TESTS", "false").lower() == "true"


# Fixtures


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_time() -> Generator:
    """Mock time.time() for testing"""
    import time

    with unittest.mock.patch("time.time", return_value=1234567890):
        yield


@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Test configuration"""
    return {"test_mode": True, "log_level": "DEBUG", "max_retries": 3, "timeout": 30}


@pytest.fixture
def sample_comment_data() -> Dict[str, Any]:
    """Sample comment data for testing"""
    return {
        "id": "test_comment_1",
        "text": "This is a test comment",
        "user_id": "test_user_1",
        "username": "testuser",
        "created_at": "2025-01-08T10:00:00Z",
        "like_count": 10,
        "reply_count": 2,
    }


@pytest.fixture
def sample_post_data() -> Dict[str, Any]:
    """Sample post/article data for testing"""
    return {
        "id": "test_post_1",
        "title": "Test Post",
        "content": "This is a test post",
        "author_id": "test_user_1",
        "created_at": "2025-01-08T09:00:00Z",
        "tags": ["test", "moderation"],
    }


@pytest.fixture
def mock_response(status_code: int = 200, data: Dict = None) -> Mock:
    """Create mock response"""
    if data is None:
        data = {"data": {}}

    response = Mock()
    response.status_code = status_code
    response.json.return_value = data
    response.text = json.dumps(data)
    response.raise_for_status.return_value = None
    return response


@pytest.fixture
def mock_session() -> Generator:
    """Create mock requests session"""
    session = Mock()
    session.get.return_value = mock_response()
    session.post.return_value = mock_response()
    session.delete.return_value = mock_response()
    yield session


@pytest.fixture
def temp_config_file() -> Generator:
    """Create temporary config file for testing"""
    fd, path = tempfile.mkstemp(suffix=".json", text="{}")
    os.close(fd)

    yield path

    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def valid_auth_token() -> str:
    """Valid authentication token for testing"""
    return "valid_test_token_123456"


@pytest.fixture
def expired_auth_token() -> str:
    """Expired authentication token for testing"""
    return "expired_test_token_789012"


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """Authentication headers for testing"""
    return {
        "Authorization": "Bearer valid_test_token_123456",
        "Content-Type": "application/json",
    }


@pytest.fixture
def rate_limit_headers() -> Dict[str, str]:
    """Rate limit headers for testing"""
    return {
        "X-RateLimit-Limit": "100",
        "X-RateLimit-Remaining": "95",
        "X-RateLimit-Reset": "1234567890",
    }


@pytest.fixture
def rate_limit_response() -> Mock:
    """Rate limit error response"""
    response = Mock()
    response.status_code = 429
    response.headers = rate_limit_headers()
    response.text = json.dumps({"error": {"code": "rate_limit_exceeded"}})
    response.json.return_value = {"error": {"code": "rate_limit_exceeded"}}
    return response


@pytest.fixture
def webhook_event() -> Dict[str, Any]:
    """Sample webhook event for testing"""
    return {
        "event_type": "comment.created",
        "comment_id": "test_comment_1",
        "post_id": "test_post_1",
        "text": "New comment via webhook",
        "timestamp": datetime.now().isoformat(),
    }


@pytest.fixture
def error_response(error_code: str = "access_token_invalid") -> Mock:
    """Error response for testing"""
    response = Mock()
    response.status_code = 401
    response.json.return_value = {
        "error": {"code": error_code, "message": "The access token provided is invalid"}
    }
    return response
