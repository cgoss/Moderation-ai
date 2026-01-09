"""Authentication Test Fixtures"""

from typing import Dict, Any, Generator
import pytest
from unittest.mock import Mock, patch, MagicMock
import time


@pytest.fixture
def valid_auth_token() -> str:
    """Valid authentication token for testing"""
    return f"valid_test_token_{int(time.time())}"


@pytest.fixture
def expired_auth_token() -> str:
    """Expired authentication token for testing"""
    return f"expired_token_{int(time.time() - 100000)}"


@pytest.fixture
def auth_headers(auth_token: str) -> Dict[str, str]:
    """Authentication headers fixture"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


@pytest.fixture
def oauth_credentials() -> Dict[str, str]:
    """OAuth credentials for testing"""
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "redirect_uri": "http://localhost:8080/callback",
    }


@pytest.fixture
def mock_oauth_flow():
    """Mock OAuth 2.0 authentication flow"""
    auth_state = {}
    auth_code = "test_auth_code_123"
    access_token = f"valid_token_{int(time.time())}"
    refresh_token = f"refresh_token_{int(time.time())}"

    def flow_generator():
        # Initial authorization request
        yield {
            "state": "test_state_123",
            "auth_url": "https://auth.example.com/authorize",
            "client_id": "test_client_id",
            "redirect_uri": "http://localhost:8080/callback",
        }

        # Callback with authorization code
        yield {"code": auth_code, "state": "test_state_123"}

        # Token exchange
        yield {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": 3600,
            "token_type": "Bearer",
            "scope": "user.info.basic video.list comment.read",
        }

        # Token refresh
        yield {
            "access_token": f"new_token_{int(time.time())}",
            "refresh_token": f"new_refresh_{int(time.time())}",
            "expires_in": 3600,
        }

    return flow_generator


@pytest.fixture
def mock_token_manager():
    """Mock token manager for testing"""
    manager = Mock()
    manager.storage = {}

    def get_token(user_id: str) -> str:
        return manager.storage.get(user_id, {}).get("access_token")

    def save_token(user_id: str, token_data: Dict):
        manager.storage[user_id] = token_data

    def is_token_expired(user_id: str) -> bool:
        if user_id not in manager.storage:
            return True
        expires_at = manager.storage[user_id].get("expires_at", 0)
        return time.time() > expires_at

    def refresh_token(user_id: str) -> Dict:
        return {
            "access_token": f"new_token_{int(time.time())}",
            "refresh_token": f"new_refresh_{int(time.time())}",
            "expires_in": 3600,
        }

    manager.get_token = get_token
    manager.save_token = save_token
    manager.is_token_expired = is_token_expired
    manager.refresh_token = refresh_token
    manager.storage = {}

    return manager


@pytest.fixture
def instagram_auth_config() -> Dict[str, Any]:
    """Instagram authentication configuration"""
    return {
        "client_id": "test_instagram_client_id",
        "client_secret": "test_instagram_client_secret",
        "redirect_uri": "http://localhost:8080/callback",
        "scopes": ["user_profile", "comments", "likes"],
    }


@pytest.fixture
def medium_auth_config() -> Dict[str, Any]:
    """Medium authentication configuration"""
    return {
        "client_id": "test_medium_client_id",
        "client_secret": "test_medium_client_secret",
        "redirect_uri": "http://localhost:8080/callback",
        "scopes": ["basicProfile", "publishPost", "listPublications"],
    }


@pytest.fixture
def tiktok_auth_config() -> Dict[str, Any]:
    """TikTok authentication configuration"""
    return {
        "client_key": "test_tiktok_client_key",
        "client_secret": "test_tiktok_client_secret",
        "redirect_uri": "http://localhost:8080/callback",
        "scopes": ["user.info.basic", "video.list", "comment.read", "comment.manage"],
    }


@pytest.fixture
def mock_auth_response() -> Mock:
    """Mock successful authentication response"""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "access_token": "test_access_token_123",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "test_refresh_token_456",
    }
    response.text = '{"access_token": "test_access_token_123"}'
    response.raise_for_status.return_value = None
    return response


@pytest.fixture
def mock_auth_error(error_type: str = "invalid_token") -> Mock:
    """Mock authentication error response"""
    error_messages = {
        "invalid_token": "The access token provided is invalid",
        "expired_token": "The access token has expired",
        "invalid_client": "Client authentication failed",
        "invalid_grant": "Invalid grant type",
    }

    response = Mock()
    response.status_code = 401
    response.json.return_value = {
        "error": {
            "code": error_type,
            "message": error_messages.get(error_type, "Authentication failed"),
        }
    }
    error_msg = error_messages.get(error_type, "Authentication failed")
    response.text = (
        '{"error": {"code": "' + error_type + '", "message": "' + error_msg + '"}}'
    )
    response.raise_for_status.side_effect = Exception("Authentication failed")
    return response


@pytest.fixture
def auth_session() -> Generator:
    """Create a mock authentication session"""
    session = Mock()
    session.access_token = "test_token_123"
    session.token_expires_at = time.time() + 3600
    session.is_authenticated = True

    yield session

    session.cleanup()


@pytest.fixture(params=["instagram", "medium", "tiktok"])
def platform_auth_config(request):
    """Parameterized fixture for platform auth configs"""
    configs = {
        "instagram": instagram_auth_config,
        "medium": medium_auth_config,
        "tiktok": tiktok_auth_config,
    }
    return configs[request.param]


def create_auth_mock(
    platform: str, token: str = "test_token_123", expires_in: int = 3600
) -> Dict[str, Any]:
    """Create authentication mock for a platform"""
    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": expires_in,
        "refresh_token": f"refresh_token_{int(time.time())}",
        "platform": platform,
    }


@pytest.fixture
def user_session() -> Generator:
    """Create a mock user session"""
    session = Mock()
    session.user_id = "test_user_123"
    session.username = "testuser"
    session.display_name = "Test User"
    session.profile_picture = "https://example.com/avatar.jpg"
    session.is_verified = True

    yield session

    session.logout()
