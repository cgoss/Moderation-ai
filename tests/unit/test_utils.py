"""Unit tests for utils modules."""

import os
import sys
import pytest
from datetime import datetime, timedelta

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from src.core.base import Comment, Severity, Violation, ModerationResult
from src.utils.error_handler import (
    ErrorHandler,
    ModerationError,
    AuthenticationError,
    RateLimitError,
    PlatformError,
    ValidationError,
    ConfigurationError,
)
from src.utils.rate_limiter import RateLimiter, PlatformRateLimiter
from src.utils import auth_manager


class TestErrorHandler:
    """Tests for ErrorHandler class."""

    @pytest.fixture
    def handler(self):
        """Create error handler instance."""
        return ErrorHandler()

    @pytest.fixture
    def sample_comment(self):
        """Create a sample comment."""
        return Comment(
            id="123",
            text="Test comment",
            author_id="user1",
            author_name="User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
        )

    def test_handler_creation(self, handler):
        """Test handler creation."""
        assert handler is not None

    def test_wrap_function(self, handler):
        """Test function wrapping."""

        def test_func():
            return "success"

        wrapped = handler.wrap(test_func)
        assert wrapped() == "success"

    def test_wrap_function_with_exception(self, handler):
        """Test wrapping function that raises exception."""

        def test_func():
            raise ValueError("Test error")

        wrapped = handler.wrap(test_func)
        result = wrapped()
        assert result is None

    def test_wrap_with_retry(self, handler):
        """Test wrapping with retry logic."""
        attempts = []

        def test_func():
            attempts.append(1)
            if len(attempts) < 3:
                raise ValueError("Retry error")
            return "success"

        wrapped = handler.wrap(test_func, max_retries=3)
        result = wrapped()
        assert result == "success"
        assert len(attempts) == 3

    def test_wrap_no_retry_on_success(self, handler):
        """Test no retry on successful execution."""
        attempts = []

        def test_func():
            attempts.append(1)
            return "success"

        wrapped = handler.wrap(test_func, max_retries=3)
        result = wrapped()
        assert result == "success"
        assert len(attempts) == 1

    def test_wrap_max_retries_exceeded(self, handler):
        """Test wrapping when max retries exceeded."""

        def test_func():
            raise ValueError("Always fails")

        wrapped = handler.wrap(test_func, max_retries=2)
        result = wrapped()
        assert result is None

    def test_log_error(self, handler, caplog):
        """Test error logging."""
        with caplog.at_level("ERROR"):
            handler.log_error("Test error message", ValueError("Test"))
        assert "Test error message" in caplog.text

    def test_get_last_error(self, handler):
        """Test getting last error."""
        handler.log_error("Test error", ValueError("Test"))
        last_error = handler.get_last_error()
        assert last_error is not None

    def test_clear_errors(self, handler):
        """Test clearing errors."""
        handler.log_error("Test error", ValueError("Test"))
        handler.clear_errors()
        last_error = handler.get_last_error()
        assert last_error is None


class TestCustomExceptions:
    """Tests for custom exception classes."""

    def test_moderation_error(self):
        """Test ModerationError."""
        with pytest.raises(ModerationError) as exc_info:
            raise ModerationError("Test error")
        assert str(exc_info.value) == "Test error"

    def test_authentication_error(self):
        """Test AuthenticationError."""
        with pytest.raises(AuthenticationError) as exc_info:
            raise AuthenticationError("Auth failed", platform="test")
        assert "Auth failed" in str(exc_info.value)

    def test_rate_limit_error(self):
        """Test RateLimitError."""
        with pytest.raises(RateLimitError) as exc_info:
            raise RateLimitError("Rate limited", limit=10, reset_in=60)
        assert "Rate limited" in str(exc_info.value)

    def test_platform_error(self):
        """Test PlatformError."""
        with pytest.raises(PlatformError) as exc_info:
            raise PlatformError("Platform error", platform="test", code=500)
        assert "Platform error" in str(exc_info.value)

    def test_validation_error(self):
        """Test ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("Invalid data", field="test_field")
        assert "Invalid data" in str(exc_info.value)

    def test_configuration_error(self):
        """Test ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError("Config error", key="test_key")
        assert "Config error" in str(exc_info.value)


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_limiter_creation(self):
        """Test rate limiter creation."""
        limiter = RateLimiter(requests=10, period=60)
        assert limiter.requests == 10
        assert limiter.period == 60

    def test_allow_within_limit(self):
        """Test allowing request within limit."""
        limiter = RateLimiter(requests=10, period=60)
        for _ in range(9):
            allowed = limiter.allow_request()
            assert allowed is True

    def test_block_when_limit_exceeded(self):
        """Test blocking when limit exceeded."""
        limiter = RateLimiter(requests=10, period=60)
        for _ in range(10):
            limiter.allow_request()
        allowed = limiter.allow_request()
        assert allowed is False

    def test_reset_after_period(self):
        """Test reset after period expires."""
        limiter = RateLimiter(requests=10, period=1)
        for _ in range(10):
            limiter.allow_request()
        assert limiter.allow_request() is False
        # Fast forward past period
        limiter._window_start = datetime.utcnow() - timedelta(seconds=2)
        allowed = limiter.allow_request()
        assert allowed is True

    def test_get_wait_time(self):
        """Test getting wait time."""
        limiter = RateLimiter(requests=10, period=60)
        for _ in range(10):
            limiter.allow_request()
        wait_time = limiter.get_wait_time()
        assert wait_time > 0

    def test_remaining_requests(self):
        """Test getting remaining requests."""
        limiter = RateLimiter(requests=10, period=60)
        for _ in range(5):
            limiter.allow_request()
        remaining = limiter.get_remaining_requests()
        assert remaining == 5


class TestPlatformRateLimiter:
    """Tests for PlatformRateLimiter class."""

    @pytest.fixture
    def limiter(self):
        """Create platform rate limiter."""
        return PlatformRateLimiter()

    def test_limiter_creation(self, limiter):
        """Test platform limiter creation."""
        assert limiter.limiters is not None

    def test_allow_request_twitter(self, limiter):
        """Test allowing Twitter request."""
        for _ in range(5):
            allowed = limiter.allow_request("twitter")
            assert allowed is True

    def test_block_twitter_when_limited(self, limiter):
        """Test blocking Twitter when limit exceeded."""
        limiter.requests_per_period["twitter"] = (1, 1)
        allowed = limiter.allow_request("twitter")
        assert allowed is False

    def test_allow_request_reddit(self, limiter):
        """Test allowing Reddit request."""
        for _ in range(5):
            allowed = limiter.allow_request("reddit")
            assert allowed is True

    def test_get_wait_time(self, limiter):
        """Test getting wait time for platform."""
        limiter.requests_per_period["youtube"] = (1, 1)
        wait_time = limiter.get_wait_time("youtube")
        assert wait_time > 0

    def test_reset_limiter(self, limiter):
        """Test resetting limiter for platform."""
        limiter.requests_per_period["instagram"] = (1, 1)
        allowed = limiter.allow_request("instagram")
        assert allowed is False
        limiter.reset("instagram")
        allowed = limiter.allow_request("instagram")
        assert allowed is True


class TestAuthManager:
    """Tests for AuthManager class."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create auth manager instance."""
        return AuthManager(credential_file=str(tmp_path / "auth.json"))

    @pytest.fixture
    def tmp_path(self, tmpdir):
        """Create temporary path."""
        return tmpdir

    def test_manager_creation(self, manager):
        """Test auth manager creation."""
        assert manager is not None
        assert manager.credentials == {}

    def test_store_credentials(self, manager):
        """Test storing credentials."""
        config = AuthConfig(
            platform="test",
            access_token="test_token",
            refresh_token="test_refresh",
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        manager.store_credentials(config)
        assert "test" in manager.credentials

    def test_get_credentials(self, manager):
        """Test getting stored credentials."""
        config = AuthConfig(
            platform="test",
            access_token="test_token",
            refresh_token="test_refresh",
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        manager.store_credentials(config)
        retrieved = manager.get_credentials("test")
        assert retrieved is not None
        assert retrieved.access_token == "test_token"

    def test_get_nonexistent_credentials(self, manager):
        """Test getting credentials that don't exist."""
        retrieved = manager.get_credentials("nonexistent")
        assert retrieved is None

    def test_remove_credentials(self, manager):
        """Test removing credentials."""
        config = AuthConfig(
            platform="test",
            access_token="test_token",
            refresh_token="test_refresh",
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        manager.store_credentials(config)
        manager.remove_credentials("test")
        retrieved = manager.get_credentials("test")
        assert retrieved is None

    def test_is_token_expired_true(self, manager):
        """Test checking if expired token."""
        config = AuthConfig(
            platform="test",
            access_token="test_token",
            expires_at=datetime.utcnow() - timedelta(minutes=1),
        )
        assert manager.is_token_expired(config) is True

    def test_is_token_expired_false(self, manager):
        """Test checking if non-expired token."""
        config = AuthConfig(
            platform="test",
            access_token="test_token",
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        assert manager.is_token_expired(config) is False

    def test_import_credentials(self, manager, tmp_path):
        """Test importing credentials from file."""
        # Create test credential file
        test_file = tmp_path / "test_auth.json"
        test_file.write_text('{"test": {"access_token": "imported"}}')
        manager.import_credentials(str(test_file))
        retrieved = manager.get_credentials("test")
        assert retrieved is not None
        assert retrieved.access_token == "imported"

    def test_export_credentials(self, manager, tmp_path):
        """Test exporting credentials to file."""
        config = AuthConfig(
            platform="test",
            access_token="test_token",
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        manager.store_credentials(config)
        export_file = tmp_path / "export_auth.json"
        manager.export_credentials(str(export_file))
        assert export_file.exists()

    def test_clear_all_credentials(self, manager):
        """Test clearing all credentials."""
        config = AuthConfig(
            platform="test",
            access_token="test_token",
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        manager.store_credentials(config)
        manager.clear_all()
        assert len(manager.credentials) == 0
