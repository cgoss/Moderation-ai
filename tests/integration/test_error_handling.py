"""Error Handling Tests for All Platforms"""

import pytest
from unittest.mock import Mock, patch
import json

from tests.fixtures import (
    sample_comment,
    sample_post,
    sample_video,
    sample_article,
    mock_error_response,
    platform_auth_config,
)


@pytest.mark.unit
@pytest.mark.parametrize("platform", ["instagram", "medium", "tiktok"])
class TestPlatformErrorHandling:
    """Tests for platform-specific error handling"""

    def test_rate_limit_429_handling(self, platform):
        """Test rate limit error (429)"""
        if platform == "instagram":
            from tests.fixtures import MockInstagramAPI, mock_error_response

            client = MockInstagramAPI(platform_auth_config())
        else:
            pytest.skip(f"Unknown platform: {platform}")

        error_response = mock_error_response(status_code=429)

        with patch("requests.get", return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_media("test_id")

            assert "rate limit" in str(exc_info.value).lower()
            assert exc_info.value.status_code == 429

    def test_forbidden_403_handling(self, platform):
        """Test forbidden error (403)"""
        if platform == "instagram":
            from tests.fixtures import MockInstagramAPI, mock_error_response

            client = MockInstagramAPI(platform_auth_config())
        else:
            pytest.skip(f"Unknown platform: {platform}")

        error_response = mock_error_response(status_code=403)

        with patch("requests.get", return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_media("test_id")

            assert "forbidden" in str(exc_info.value).lower()
            assert exc_info.value.status_code == 403

    def test_not_found_404_handling(self, platform):
        """Test not found error (404)"""
        if platform == "instagram":
            from tests.fixtures import MockInstagramAPI, mock_error_response

            client = MockInstagramAPI(platform_auth_config())
        else:
            pytest.skip(f"Unknown platform: {platform}")

        error_response = mock_error_response(status_code=404)

        with patch("requests.get", return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_media("test_id")

            assert "not found" in str(exc_info.value).lower()
            assert exc_info.value.status_code == 404

    def test_invalid_grant_400_handling(self, platform):
        """Test invalid grant error (400)"""
        if platform == "instagram":
            from tests.fixtures import MockInstagramAPI, mock_error_response

            client = MockInstagramAPI(platform_auth_config())
        else:
            pytest.skip(f"Unknown platform: {platform}")

        error_response = mock_error_response(status_code=400)
        error_response.headers = {
            "Content-Type": "application/json",
            "X-Invalid-Grant": "invalid_grant_type",
        }

        with patch("requests.get", return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_media("test_id")

            assert "invalid grant" in str(exc_info.value).lower()
            assert exc_info.value.status_code == 400
            assert "X-Invalid-Grant" in exc_info.value.headers.get("X-Invalid-Grant")

    def test_unauthorized_401_handling(self, platform):
        """Test unauthorized error (401)"""
        if platform == "instagram":
            from tests.fixtures import MockInstagramAPI, mock_error_response

            client = MockInstagramAPI(platform_auth_config())
        else:
            pytest.skip(f"Unknown platform: {platform}")

        error_response = mock_error_response(status_code=401)

        with patch("requests.get", return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_media("test_id")

            assert "unauthorized" in str(exc_info.value).lower()
            assert exc_info.value.status_code == 401


@pytest.mark.unit
@pytest.mark.parametrize("platform", ["instagram", "medium", "tiktok"])
class TestGenericErrorHandling:
    """Generic error handling tests"""

    def test_timeout_recovery(self):
        """Test timeout error recovery"""
        import requests.exceptions

        from tests.fixtures import sample_comment

        # Mock timeout error
        error = requests.exceptions.Timeout("Request timeout")

        # Should handle and recover
        with pytest.raises(requests.exceptions.Timeout):
            raise error

        assert "Request timeout" in str(error).lower()

    def test_connection_recovery(self):
        """Test connection error recovery"""
        import requests.exceptions

        from tests.fixtures import sample_comment

        # Mock connection error
        error = requests.exceptions.ConnectionError("Connection failed")

        # Should handle and recover
        with pytest.raises(requests.exceptions.ConnectionError):
            raise error

        assert "Connection failed" in str(error).lower()

    def test_json_parsing_error(self):
        """Test JSON parsing error recovery"""
        import json

        # Mock JSON error
        error = json.JSONDecodeError("Invalid JSON")

        # Should handle and recover
        with pytest.raises(json.JSONDecodeError) as exc_info:
            json.loads("{invalid json}")

        assert "Invalid JSON" in str(exc_info.value).lower()

    def test_error_message_consistency(self):
        """Test error message consistency"""
        from tests.fixtures import mock_error_response

        # Test rate limit error messages
        error_response = mock_error_response(status_code=429)

        with patch("requests.get", return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                raise Exception(json.loads(error_response.text))

            assert "rate limit" in str(exc_info.value).lower()

    def test_retry_logic(self):
        """Test retry logic"""
        from tests.fixtures import (
            MockInstagramAPI,
            sample_comment,
            platform_auth_config,
        )

        client = MockInstagramAPI(platform_auth_config())

        # Mock initial failure
        client.get_media.side_effect = Exception("First attempt failed")

        # Mock success on retry
        client.get_media.side_effect = {
            "id": "test_media_id",
            "caption": "Test caption",
        }

        # Make 3 attempts
        for i in range(3):
            try:
                result = client.get_media("test_media_id")
            except:
                pass

        # Should succeed on attempt 3
        assert client.get_media.call_count == 3

    def test_error_logging(self):
        """Test error logging"""
        import logging

        from tests.fixtures import mock_error_response

        platform = "instagram"

        client = MockInstagramAPI(platform_auth_config())

        error_response = mock_error_response(
            status_code=500, error_message="Internal server error"
        )

        with patch("requests.get", return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_media("test_id")

            assert "Internal server error" in str(exc_info.value).lower()

        assert exc_info.value.status_code == 500

    @pytest.mark.parametrize("platform", ["instagram", "medium", "tiktok"])
    def test_platform_specific_errors(self, platform):
        """Test platform-specific error handling"""
        if platform == "instagram":
            self._test_instagram_errors()
        elif platform == "medium":
            self._test_medium_errors()
        elif platform == "tiktok":
            self._test_tiktok_errors()
        else:
            pytest.skip(f"Unknown platform: {platform}")

    def _test_instagram_errors(self):
        """Test Instagram-specific errors"""
        from tests.fixtures import (
            MockInstagramAPI,
            platform_auth_config,
            sample_comment,
        )

        client = MockInstagramAPI(platform_auth_config())

        # Test Graph API error (200 OK)
        client.get_media.return_value = {
            "id": "test_media_id",
            "caption": "Test caption",
            "error": {"message": "An unknown error occurred"},
        }

        with patch(
            "requests.get",
            return_value={"error": {"message": "An unknown error occurred"}},
            side_effect=Exception("API request failed"),
        ):
            with pytest.raises(Exception) as exc_info:
                client.get_media("test_media_id")

            assert "unknown error" in str(exc_info.value).lower()

    def _test_medium_errors(self):
        """Test Medium-specific errors"""
        from tests.fixtures import MockMediumAPI, platform_auth_config, sample_comment

        client = MockMediumAPI(platform_auth_config())

        # Test API error (200 OK)
        client.get_article_comments.return_value = {"comments": [sample_comment()]}

        with patch(
            "requests.get",
            return_value={"error": {"message": "API request failed"}},
            side_effect=Exception("API request failed"),
        ):
            with pytest.raises(Exception) as exc_info:
                client.get_article_comments("article_id")

            assert "API request failed" in str(exc_info.value).lower()

    def _test_tiktok_errors(self):
        """Test TikTok-specific errors"""
        from tests.fixtures import MockTikTokAPI, platform_auth_config, sample_comment

        client = MockTikTokAPI(platform_auth_config())

        # Test API error (200 OK)
        client.get_video_comments.return_value = {"comments": [sample_comment()]}

        with patch(
            "requests.get",
            return_value={"error": {"message": "API request failed"}},
            side_effect=Exception("API request failed"),
        ):
            with pytest.raises(Exception) as exc_info:
                client.get_video_comments("video_id")

            assert "API request failed" in str(exc_info.value).lower()


@pytest.mark.unit
class TestErrorRecovery:
    """Tests for error recovery mechanisms"""

    def test_exponential_backoff_strategy(self):
        """Test exponential backoff implementation"""
        from tests.fixtures import sample_comment

        backoff_times = [1, 2, 4]

        for i, expected_delay in enumerate(backoff_times):
            delay = i + 1  # Add 1 to simulate base

            # Simulate API call with backoff
            for _ in range(i):
                try:
                    raise Exception(f"Retry {_ + 1}")
                except:
                    time.sleep(delay)

            # Should make 3 total attempts
            assert i == 3

    def test_fibonacci_backoff_strategy(self):
        """Test Fibonacci backoff implementation"""
        from tests.fixtures import sample_comment

        # Fibonacci sequence
        delays = [1, 1, 2, 3, 5, 8, 13]

        for i, expected_delay in enumerate(delays):
            delay = i if i == 0 else delays[i - 1] + delays[i - 2]

            # Simulate API call with backoff
            for _ in range(len(delays)):
                try:
                    raise Exception(f"Retry {_ + 1}")
                except:
                    time.sleep(delay)

            # Should make all attempts
            assert i == len(delays)

    def test_jitter_strategy(self):
        """Test jitter-based backoff"""
        from tests.fixtures import sample_comment
        import random

        base_delay = 2

        for _ in range(5):
            jitter = random.uniform(-0.5, 0.5)
            delay = base_delay + jitter

            # Simulate API call
            try:
                raise Exception(f"Retry {_ + 1}")
            except:
                time.sleep(delay)


@pytest.mark.unit
class TestErrorReporting:
    """Tests for error reporting"""

    def test_error_context_capturing(self):
        """Test error context capturing"""
        from tests.fixtures import sample_comment, platform_auth_config

        client = MockInstagramAPI(platform_auth_config())

        # Create error with context
        error = Exception(
            "Failed to get media", response={"error": {"message": "API error"}}
        )
        error.response = Mock()
        error.response.headers = {"X-Request-ID": "test_request_id"}

        # Mock error context
        with patch("time.time", return_value=1234567890):
            with pytest.raises(Exception) as exc_info:
                client.get_media("test_media_id")

                assert "test_request_id" in exc_info.value.response.headers.get(
                    "X-Request-ID"
                )
                assert "1234567890" in exc_info.value.response.headers.get(
                    "X-Request-ID"
                )

    def test_error_message_parsing(self):
        """Test error message parsing"""
        error_messages = [
            "Rate limit exceeded",
            "Invalid token",
            "Forbidden",
            "Not found",
            "Internal server error",
        ]

        for message in error_messages:
            assert "rate limit" in message.lower()
            assert "invalid token" in message.lower()
            assert "forbidden" in message.lower()
            assert "not found" in message.lower()
            assert "internal server error" in message.lower()


if __name__ == "__main__":
    pytest.main([__file__], "-v")
