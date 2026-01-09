"""API Client Tests for All Platforms"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

from tests.fixtures import (
    MockInstagramAPI,
    MockMediumAPI,
    MockTikTokAPI,
    sample_comment,
    sample_post,
    sample_video,
    sample_article,
    mock_error_response,
    auth_headers,
    sample_rate_limit_info,
)


# Twitter imports
try:
    from src.platforms.twitter import TwitterPlatform

    TwitterClient = TwitterPlatform
except ImportError:
    TwitterClient = None

# Reddit imports
try:
    from src.platforms.reddit import RedditPlatform

    RedditClient = RedditPlatform
except ImportError:
    RedditClient = None

# YouTube imports
try:
    from src.platforms.youtube import YouTubePlatform

    YouTubeClient = YouTubePlatform
except ImportError:
    YouTubeClient = None

# Instagram imports (existing)
try:
    from src.platforms.instagram import InstagramPlatform

    InstagramClient = InstagramPlatform
except ImportError:
    InstagramClient = None

# Medium imports (existing)
try:
    from src.platforms.medium import MediumPlatform

    MediumClient = MediumPlatform
except ImportError:
    MediumClient = None

# TikTok imports (existing)
try:
    from src.platforms.tiktok import TikTokPlatform

    TikTokClient = TikTokPlatform
except ImportError:
    TikTokClient = None


@pytest.mark.unit
class TestCommonErrorHandling:
    """Common Error Handling Tests"""

    def test_timeout_handling(self):
        """Test timeout error handling"""
        import requests.exceptions

        error = requests.exceptions.Timeout("Request timeout")

        with pytest.raises(requests.exceptions.Timeout) as exc_info:
            assert "Request timeout" in str(exc_info.value)
            assert exc_info.value.__class__.__name__ == "Timeout"

    def test_connection_error_handling(self):
        """Test connection error handling"""
        import requests.exceptions

        error = requests.exceptions.ConnectionError("Connection failed")

        with pytest.raises(requests.exceptions.ConnectionError) as exc_info:
            assert "Connection failed" in str(exc_info.value)
            assert exc_info.value.__class__.__name__ == "ConnectionError"

    def test_json_error_handling(self):
        """Test JSON error handling"""
        import json

        error = json.JSONDecodeError("Invalid JSON")

        with pytest.raises(json.JSONDecodeError) as exc_info:
            assert "Invalid JSON" in str(exc_info.value)
            assert exc_info.value.__class__.__name__ == "JSONDecodeError"

    @pytest.mark.unit
    def test_retriable_error_messages(self):
        """Test error message reliability"""
        error_messages = {
            "rate_limit_exceeded": "Rate limit exceeded",
            "invalid_token": "The access token provided is invalid",
            "forbidden": "Insufficient permissions",
            "not_found": "Resource not found",
        }

        for key, expected_message in error_messages.items():
            # Check that error messages contain expected text
            # (This is a simplified check - in real scenario, would be more specific)
            assert "exceeded" in expected_message.lower()
            assert "invalid token" in expected_message.lower()
            assert "forbidden" in expected_message.lower()
            assert "not found" in expected_message.lower()


if __name__ == "__main__":
    pytest.main([__file__], "-v")
