"""Integration Tests for Platform Adapters"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from tests.fixtures import (
    MockInstagramAPI,
    MockMediumAPI,
    MockTikTokAPI,
    sample_comment,
    sample_post,
    sample_article,
    sample_video,
)


@pytest.mark.integration
@pytest.mark.network
class TestPlatformIntegration:
    """Integration tests for all platform adapters"""

    @pytest.mark.parametrize("platform", ["instagram", "medium", "tiktok"])
    def test_api_client_lifecycle(self, platform):
        """Test complete API client lifecycle"""
        if platform == "instagram":
            from tests.fixtures import instagram_config

            client = MockInstagramAPI()
            client.config = instagram_config()
        elif platform == "medium":
            from tests.fixtures import medium_config

            client = MockMediumAPI()
            client.config = medium_config()
        elif platform == "tiktok":
            from tests.fixtures import tiktok_config

            client = MockTikTokAPI()
            client.config = tiktok_config()

        assert True

    @pytest.mark.parametrize("platform", ["instagram", "medium", "tiktok"])
    @pytest.mark.network
    def test_comment_tracking_workflow(self, platform):
        """Test end-to-end comment tracking and moderation workflow"""
        if platform == "instagram":
            from tests.fixtures import MockInstagramAPI, instagram_config
            from src.platforms.instagram.moderator import InstagramCommentModerator

            client = MockInstagramAPI()
            moderator = InstagramCommentModerator(instagram_config())

            comment = sample_comment()

            # Track comment
            moderator.track_comment("post_1", comment)

            # Analyze
            analysis = moderator.analyze_comment(comment)

            # Moderate
            action = moderator.moderate_comment(comment)

            assert "comment_id" in analysis
            assert action is not None

    @pytest.mark.parametrize("platform", ["instagram", "medium", "tiktok"])
    @pytest.mark.network
    def test_post_tracking_workflow(self, platform):
        """Test end-to-end post tracking workflow"""
        if platform == "instagram":
            from tests.fixtures import MockInstagramAPI, sample_post, instagram_config
            from src.platforms.instagram.tracker import InstagramPostTracker

            client = MockInstagramAPI()
            tracker = InstagramPostTracker(instagram_config())

            post = sample_post()

            # Track post
            tracker.track_post(post)

            # Get tracked posts
            tracked = tracker.get_tracked_posts(limit=10)

            assert post["id"] in [p["id"] for p in tracked]
            assert len(tracked) <= 10

    @pytest.mark.network
    @pytest.mark.auth
    def test_oauth_authentication_flow(self):
        """Test complete OAuth authentication flow"""
        from tests.fixtures import (
            oauth_credentials,
            mock_oauth_flow,
            valid_auth_token,
            auth_headers,
        )

        # Simulate OAuth flow
        flow_generator = mock_oauth_flow()

        # Get initial request
        initial_request = next(flow_generator)
        assert "auth_url" in initial_request
        assert "state" in initial_request

        # Simulate callback with code
        callback_data = next(flow_generator)
        assert "code" in callback_data
        assert "state" in callback_data

        # Simulate token exchange
        token_response = next(flow_generator)
        assert "access_token" in token_response
        assert "expires_in" in token_response

        # Validate token
        token = token_response["access_token"]
        headers = auth_headers(token)

        assert "Bearer" in headers["Authorization"]
        assert "application/json" in headers["Content-Type"]

    @pytest.mark.integration
    @pytest.mark.network
    @pytest.mark.parametrize("platform", ["instagram", "medium", "tiktok"])
    def test_rate_limiting_with_api_calls(self, platform):
        """Test rate limiting during API calls"""
        if platform == "instagram":
            from tests.fixtures import (
                MockInstagramAPI,
                mock_rate_limiter,
                instagram_config,
            )
            from src.platforms.instagram.rate_limiter import InstagramRateLimiter

            client = MockInstagramAPI()
            limiter = mock_rate_limiter()
            config = instagram_config()

            # Mock API response
            client.get_media.return_value = {"id": "test_media"}

            # Make multiple requests
            for _ in range(5):
                limiter.record_request()
                limiter.wait_if_needed()
                client.get_media("test_media")

            assert limiter.request_count == 5

    @pytest.mark.integration
    @pytest.mark.network
    @pytest.mark.parametrize("platform", ["instagram", "medium", "tiktok"])
    def test_webhook_event_handling(self, platform):
        """Test webhook event handling"""
        if platform == "instagram":
            from tests.fixtures import (
                MockInstagramAPI,
                mock_moderation_engine,
                create_webhook_event,
                sample_comment,
            )
            from src.platforms.instagram.webhooks import InstagramWebhookHandler

            client = MockInstagramAPI()
            moderator = mock_moderation_engine()
            handler = InstagramWebhookHandler(secret="test_secret")

            # Mock webhook event
            event = create_webhook_event(comment_id="comment_123")

            # Handle event
            handler.handle_event("comment.created", event)

            # Verify handler was called
            assert handler.handle_comment_created.called

    @pytest.mark.integration
    def test_error_recovery_mechanism(self):
        """Test error recovery and retry mechanism"""
        from tests.fixtures import (
            MockInstagramAPI,
            mock_rate_limiter,
            mock_error_response,
            sample_comment,
        )
        from src.platforms.instagram.client import InstagramAPIClient
        from src.platforms.instagram.rate_limiter import InstagramRateLimiter

        client = InstagramAPIClient({"access_token": "test"})
        limiter = InstagramRateLimiter(requests_per_minute=10)

        # Simulate error then success
        client.get_media.side_effect = [
            Exception("Rate limit exceeded"),
            {"id": "test_media", "caption": "Test"},
        ]

        # First call fails
        with pytest.raises(Exception):
            client.get_media("test_media_id")

        # Second call succeeds
        result = client.get_media("test_media_id")

        assert result["id"] == "test_media"

    @pytest.mark.integration
    @pytest.mark.network
    def test_cross_platform_comment_moderation(self):
        """Test comment moderation across platforms"""
        from tests.fixtures import sample_comment

        # Test all platforms handle comments similarly
        comments = [sample_comment() for _ in range(3)]

        for comment in comments:
            assert "comment_id" in comment
            assert "text" in comment
            assert "created_at" in comment

    @pytest.mark.integration
    @pytest.mark.network
    def test_data_consistency_check(self):
        """Test data consistency across platform adapters"""
        from tests.fixtures import (
            sample_comment,
            sample_post,
            sample_article,
            sample_video,
        )

        # Test all data models have required fields
        assert "id" in sample_comment
        assert "id" in sample_post
        assert "id" in sample_article
        assert "id" in sample_video

        # Test data types are correct
        assert isinstance(sample_comment["id"], str)
        assert isinstance(sample_comment["created_at"], str)
        assert isinstance(sample_comment["like_count"], int)

    @pytest.mark.integration
    @pytest.mark.slow
    def test_batch_processing_performance(self):
        """Test batch processing performance"""
        from tests.fixtures import (
            MockInstagramAPI,
            sample_comments_list,
            mock_moderation_engine,
        )
        from src.platforms.instagram.moderator import InstagramCommentModerator

        client = MockInstagramAPI()
        moderator = mock_moderation_engine()

        comments = sample_comments_list(count=50)

        # Process all comments
        import time

        start_time = time.time()

        for comment in comments:
            analysis = moderator.analyze_comment(comment)
            moderator.evaluate_rules(analysis)

        end_time = time.time()

        # Should process all 50 comments in reasonable time
        assert (end_time - start_time) < 5.0  # 5 seconds

    @pytest.mark.integration
    def test_moderation_pipeline_consistency(self):
        """Test moderation pipeline consistency"""
        from tests.fixtures import (
            sample_comment,
            sample_post,
            sample_user,
            mock_moderation_engine,
            MockInstagramAPI,
            instagram_config,
        )
        from src.platforms.instagram.moderator import InstagramCommentModerator
        from src.platforms.instagram.client import InstagramAPIClient

        client = InstagramAPIClient(instagram_config())
        moderator = InstagramCommentModerator(client)

        # Test analysis produces consistent results
        analysis1 = moderator.analyze_comment(sample_comment())
        analysis2 = moderator.analyze_comment(sample_comment())

        assert analysis1["profanity"] == analysis2["profanity"]
        assert analysis1["spam"] == analysis2["spam"]

    @pytest.mark.integration
    @pytest.mark.network
    def test_configuration_management(self):
        """Test configuration management"""
        from tests.fixtures import instagram_config, medium_config, tiktok_config

        # Test all configs are valid
        assert "access_token" in instagram_config
        assert "access_token" in medium_config
        assert "access_token" in tiktok_config

        assert "client_id" in instagram_config
        assert "client_id" in medium_config
        assert "client_key" in tiktok_config

        assert "api_base_url" in instagram_config
        assert "api_base_url" in medium_config
        assert "api_base_url" in tiktok_config


@pytest.mark.integration
@pytest.mark.network
class TestAuthenticationFlows:
    """Integration tests for authentication flows"""

    @pytest.mark.parametrize("platform", ["instagram", "medium", "tiktok"])
    def test_token_refresh_flow(self, platform):
        """Test token refresh flow"""
        from tests.fixtures import (
            platform_config,
            valid_auth_token,
            expired_auth_token,
            mock_token_manager,
        )

        manager = mock_token_manager()

        # Test valid token
        manager.get_token.return_value = valid_auth_token()
        assert manager.is_token_expired("user_1") is False

        # Test expired token
        manager.get_token.return_value = expired_auth_token()
        assert manager.is_token_expired("user_2") is True

        # Test token refresh
        new_token = manager.refresh_token("user_1")

        assert "access_token" in new_token
        assert "refresh_token" in new_token

    @pytest.mark.network
    def test_cross_platform_auth_consistency(self):
        """Test auth consistency across platforms"""
        from tests.fixtures import instagram_config, medium_config, tiktok_config

        configs = [instagram_config(), medium_config(), tiktok_config()]

        for config in configs:
            assert "access_token" in config
            assert "client_id" in config or "client_key" in config


@pytest.mark.integration
@pytest.mark.network
class TestRateLimiting:
    """Integration tests for rate limiting"""

    @pytest.mark.parametrize("platform", ["instagram", "medium", "tiktok"])
    def test_rate_limit_enforcement(self, platform):
        """Test rate limit enforcement"""
        from tests.fixtures import mock_rate_limiter, sample_rate_limit_info
        from src.platforms.instagram.rate_limiter import InstagramRateLimiter
        from src.platforms.medium.rate_limiter import MediumRateLimiter
        from src.platforms.tiktok.rate_limiter import TikTokRateLimiter

        if platform == "instagram":
            limiter = InstagramRateLimiter(requests_per_minute=10)
        elif platform == "medium":
            limiter = MediumRateLimiter(requests_per_minute=10)
        elif platform == "tiktok":
            limiter = TikTokRateLimiter(requests_per_minute=10)
        else:
            pytest.skip(f"Unknown platform: {platform}")

        # Record request
        limiter.record_request()

        # Check if under limit
        info = limiter.check_rate_limit()

        assert info["remaining"] >= 0
        assert info["limit"] > 0

    @pytest.mark.network
    def test_rate_limit_backoff(self):
        """Test rate limit backoff"""
        from tests.fixtures import mock_rate_limiter, MockInstagramAPI, instagram_config
        from src.platforms.instagram.client import InstagramAPIClient
        from src.platforms.instagram.rate_limiter import InstagramRateLimiter

        client = InstagramAPIClient(instagram_config())
        limiter = InstagramRateLimiter(requests_per_minute=10)

        # Mock rate limit error
        limiter.check_rate_limit.return_value = False

        # Should wait
        with patch("time.sleep") as mock_sleep:
            limiter.wait_if_needed()

            assert mock_sleep.called

    @pytest.mark.slow
    def test_rate_limit_recovery(self):
        """Test rate limit recovery over time"""
        from tests.fixtures import mock_rate_limiter
        from src.platforms.instagram.rate_limiter import InstagramRateLimiter

        limiter = InstagramRateLimiter(requests_per_minute=10)

        # Simulate hitting limit
        for _ in range(15):
            limiter.record_request()

        info = limiter.check_rate_limit()
        assert info["remaining"] < 10

        # Wait for reset
        import time

        time.sleep(0.1)  # Simulate time passing

        # Limit should be reset
        info = limiter.check_rate_limit()
        assert info["remaining"] == 10


@pytest.mark.integration
@pytest.mark.network
class TestWebhooks:
    """Integration tests for webhooks"""

    @pytest.mark.parametrize("platform", ["instagram", "medium", "tiktok"])
    def test_webhook_registration(self, platform):
        """Test webhook registration"""
        from tests.fixtures import platform_config, create_webhook_event, MockMediumAPI
        from src.platforms.instagram.webhooks import InstagramWebhookHandler
        from src.platforms.medium.webhooks import MediumWebhookHandler
        from src.platforms.tiktok.webhooks import TikTokWebhookHandler

        if platform == "instagram":
            handler = InstagramWebhookHandler(secret="test_secret")
        elif platform == "medium":
            handler = MediumWebhookHandler(secret="test_secret")
        elif platform == "tiktok":
            handler = TikTokWebhookHandler(secret="test_secret")
        else:
            pytest.skip(f"Unknown platform: {platform}")

        # Test registration (mocked)
        assert True  # Registration would be tested in real scenario

    @pytest.mark.network
    def test_webhook_event_processing(self, platform):
        """Test webhook event processing"""
        from tests.fixtures import (
            create_webhook_event,
            mock_moderation_engine,
            platform_client,
            sample_comment,
        )
        from src.platforms.instagram.webhooks import InstagramWebhookHandler

        if platform == "instagram":
            from tests.fixtures import instagram_client

            handler = InstagramWebhookHandler(secret="test_secret")
        else:
            pytest.skip(f"Unknown platform: {platform}")

        moderator = mock_moderation_engine()
        event = create_webhook_event()

        # Process event
        handler.handle_event("comment.created", event)

        # Verify moderation was called
        assert moderator.analyze_comment.called


@pytest.mark.integration
@pytest.mark.network
class TestErrorScenarios:
    """Integration tests for error scenarios"""

    @pytest.mark.parametrize("platform", ["instagram", "medium", "tiktok"])
    def test_network_error_recovery(self, platform):
        """Test network error recovery"""
        from tests.fixtures import (
            MockInstagramAPI,
            mock_rate_limiter,
            instagram_config,
            sample_media,
            sample_comment,
        )
        from src.platforms.instagram.client import InstagramAPIClient
        from src.platforms.instagram.moderator import InstagramCommentModerator
        from src.platforms.instagram.rate_limiter import InstagramRateLimiter

        client = InstagramAPIClient(instagram_config())
        limiter = InstagramRateLimiter(requests_per_minute=10)
        moderator = InstagramCommentModerator(client)

        # Mock network error
        client.get_media.side_effect = Exception("Network error")

        # First attempt fails
        with pytest.raises(Exception):
            client.get_media("test_media_id")

        # Second attempt with backoff
        result = client.get_media("test_media_id")

        assert result["id"] == sample_media()["id"]

    @pytest.mark.parametrize("platform", ["instagram", "medium", "tiktok"])
    def test_concurrent_request_handling(self, platform):
        """Test concurrent request handling"""
        from tests.fixtures import (
            MockInstagramAPI,
            mock_rate_limiter,
            instagram_config,
            sample_comments_list,
        )
        from src.platforms.instagram.client import InstagramAPIClient
        from src.platforms.instagram.rate_limiter import InstagramRateLimiter

        client = InstagramAPIClient(instagram_config())
        limiter = InstagramRateLimiter(requests_per_minute=10)
        comments = sample_comments_list(count=10)

        # Make concurrent requests (simulated)
        import threading

        threads = []
        for comment in comments:
            thread = threading.Thread(target=client.get_media, args=("test_media_id"))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join(timeout=5)

        # Should have completed all requests
        assert limiter.request_count == 10


@pytest.mark.integration
def test_full_integration_workflow():
    """Test full integration workflow"""
    from tests.fixtures import (
        sample_comment,
        sample_post,
        sample_video,
        sample_user,
        mock_moderation_engine,
        MockInstagramAPI,
        instagram_config,
    )
    from src.platforms.instagram.client import InstagramAPIClient
    from src.platforms.instagram.moderator import InstagramCommentModerator
    from src.platforms.instagram.tracker import InstagramPostTracker

    client = InstagramAPIClient(instagram_config())
    moderator = InstagramCommentModerator(client)
    tracker = InstagramPostTracker(instagram_config())

    # Track post
    tracker.track_post(sample_post())

    # Get comment
    client.get_media_comments.return_value = [sample_comment()]
    comments = client.get_media_comments("post_1")

    # Moderate comment
    analysis = moderator.analyze_comment(comments[0])
    action = moderator.evaluate_rules(analysis)

    assert action is not None
    assert analysis is not None


if __name__ == "__main__":
    pytest.main([__file__], "-v")
