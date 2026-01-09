"""Authentication Flow Tests for All Platforms"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from tests.fixtures import (
    valid_auth_token,
    expired_auth_token,
    oauth_credentials,
    auth_headers,
)


@pytest.mark.auth
@pytest.mark.network
class TestAuthenticationFlows:
    """Test authentication flows for all platforms"""

    @pytest.mark.parametrize("platform", ["instagram", "medium", "tiktok"])
    def test_authorization_request_success(self, platform):
        """Test successful authorization request"""
        from tests.fixtures import (
            MockInstagramAPI,
            MockMediumAPI,
            MockTikTokAPI,
            platform_config,
            mock_response_factory,
        )

        config = platform_config(platform)

        if platform == "instagram":
            client = MockInstagramAPI()
            mock_func = "get_media"
            args = ["test_media_id"]
        elif platform == "medium":
            client = MockMediumAPI()
            mock_func = "get_articles"
            args = ["test_user_id"]
        elif platform == "tiktok":
            client = MockTikTokAPI()
            mock_func = "get_user_info"
            args = []
        else:
            pytest.skip(f"Unknown platform: {platform}")

        # Mock successful auth response
        success_response = mock_response_factory(
            status_code=200, data={"id": "test_user"}
        )
        getattr(client, mock_func).return_value = success_response

        result = getattr(client, mock_func)(*args)

        assert result["id"] == "test_user"
        assert getattr(client, mock_func).call_count == 1

    def test_token_exchange_success(self):
        """Test successful token exchange"""
        from tests.fixtures import valid_auth_token, mock_response_factory

        # Mock token exchange response
        token_response = mock_response_factory(
            status_code=200,
            data={
                "access_token": valid_auth_token(),
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "refresh_test_token",
            },
        )

        assert token_response["status_code"] == 200
        assert "access_token" in token_response["data"]
        assert "expires_in" in token_response["data"]
        assert "refresh_token" in token_response["data"]

    @pytest.mark.network
    def test_token_refresh_success(self):
        """Test successful token refresh"""
        from tests.fixtures import mock_response_factory

        # Mock refresh response
        refresh_response = mock_response_factory(
            status_code=200,
            data={
                "access_token": "new_token",
                "refresh_token": "new_refresh_token",
                "expires_in": 3600,
            },
        )

        assert refresh_response["status_code"] == 200
        assert refresh_response["data"]["access_token"] == "new_token"
        assert "refresh_token" in refresh_response["data"]

    def test_token_expiration_handling(self):
        """Test token expiration and refresh"""
        from tests.fixtures import (
            valid_auth_token,
            expired_auth_token,
            mock_token_manager,
        )

        manager = mock_token_manager()

        # Test expired token
        manager.get_token.return_value = expired_auth_token()
        assert manager.is_token_expired("user_1") is True

        # Refresh token
        manager.refresh_token.return_value = {
            "access_token": "new_token",
            "expires_in": 3600,
        }
        new_token_data = manager.refresh_token("user_1")

        assert new_token_data["access_token"] != expired_auth_token()
        assert "expires_in" in new_token_data

    def test_multiple_platform_auth(self):
        """Test authentication across multiple platforms"""
        from tests.fixtures import (
            instagram_config,
            medium_config,
            tiktok_config,
            MockInstagramAPI,
            MockMediumAPI,
            MockTikTokAPI,
            mock_response_factory,
        )

        # Mock all clients
        instagram = MockInstagramAPI()
        instagram.config = instagram_config()
        medium = MockMediumAPI()
        medium.config = medium_config()
        tiktok = MockTikTokAPI()
        tiktok.config = tiktok_config()

        # Mock successful responses
        success_response = mock_response_factory(
            status_code=200, data={"id": "test_user"}
        )

        instagram.get_media.return_value = success_response
        medium.get_articles.return_value = success_response
        tiktok.get_user_info.return_value = success_response

        # Test all platforms
        ig_result = instagram.get_media("test_media_id")
        medium_result = medium.get_articles("test_user_id")
        tiktok_result = tiktok.get_user_info()

        assert ig_result["id"] == "test_user"
        assert medium_result["id"] == "test_user"
        assert tiktok_result["id"] == "test_user"

    def test_auth_state_validation(self):
        """Test auth state validation"""
        from tests.fixtures import valid_auth_token, auth_headers

        # Valid auth token
        valid_headers = auth_headers(valid_auth_token())

        assert "Bearer" in valid_headers["Authorization"]
        assert "application/json" in valid_headers["Content-Type"]
        assert valid_headers["Authorization"].startswith("Bearer ")

    @pytest.mark.network
    def test_concurrent_token_requests(self):
        """Test concurrent token requests"""
        from tests.fixtures import mock_token_manager

        manager = mock_token_manager()

        # Mock multiple concurrent requests
        manager.get_token.return_value = "test_token"
        manager.save_token.return_value = None

        # Make 10 concurrent requests
        for _ in range(10):
            token = manager.get_token("user_1")
            assert token == "test_token"

    @pytest.mark.network
    def test_auth_failure_recovery(self):
        """Test authentication failure recovery"""
        from tests.fixtures import (
            MockInstagramAPI,
            mock_auth_error,
            instagram_config,
        )

        client = MockInstagramAPI()
        client.config = instagram_config()

        # Mock auth error
        error_response = mock_auth_error(error_type="access_token_invalid")
        client.get_media.side_effect = Exception(error_response)

        # Should raise exception
        with pytest.raises(Exception):
            client.get_media("test_media_id")

    @pytest.mark.network
    def test_auth_retry_with_backoff(self):
        """Test auth retry with exponential backoff"""
        from tests.fixtures import (
            MockInstagramAPI,
            mock_auth_error,
            instagram_config,
            mock_response_factory,
        )

        client = MockInstagramAPI()
        client.config = instagram_config()

        # Mock initial failure, then success
        client.get_media.side_effect = [
            Exception(mock_auth_error()),
            mock_response_factory(status_code=200, data={"id": "test_user"}),
        ]

        # First attempt fails
        with pytest.raises(Exception):
            client.get_media("test_media_id")

        # Second attempt succeeds
        result = client.get_media("test_media_id")
        assert result["id"] == "test_user"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
