"""Unit Tests for Instagram Adapter"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
import json

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from tests.fixtures import (
    MockInstagramAPI,
    sample_comment,
    sample_post,
    sample_user,
    auth_headers,
    mock_error_response,
)


class TestInstagramAPIClient:
    """Tests for Instagram API Client"""

    def test_client_initialization(self, instagram_config):
        """Test Instagram client initialization"""
        from src.platforms.instagram import InstagramPlatform

        client = InstagramAPIClient(instagram_config)

        assert client.config == instagram_config
        assert client.access_token == instagram_config["access_token"]
        assert client.api_base_url == instagram_config["api_base_url"]

    @pytest.mark.network
    def test_get_media_success(self, instagram_client: MockInstagramAPI):
        """Test successful media retrieval"""
        media_id = "test_media_123"

        result = instagram_client.get_media(media_id)

        assert result["id"] == media_id
        assert "caption" in result
        assert instagram_client.call_count == 1

    @pytest.mark.network
    def test_get_media_comments_success(self, instagram_client: MockInstagramAPI):
        """Test successful comment retrieval"""
        media_id = "test_media_123"

        comments = instagram_client.get_media_comments(media_id)

        assert len(comments) == 5
        assert instagram_client.call_count == 1

    @pytest.mark.network
    def test_delete_comment_success(self, instagram_client: MockInstagramAPI):
        """Test successful comment deletion"""
        comment_id = "comment_test_123"

        result = instagram_client.delete_comment(comment_id)

        assert result is True
        assert instagram_client.call_count == 1
        assert (
            "delete_comment",
            {"comment_id": comment_id},
        ) in instagram_client.called_endpoints

    @pytest.mark.network
    def test_hide_comment_success(self, instagram_client: MockInstagramAPI):
        """Test successful comment hiding"""
        comment_id = "comment_test_123"

        result = instagram_client.hide_comment(comment_id)

        assert result is True
        assert instagram_client.call_count == 1
        assert (
            "hide_comment",
            {"comment_id": comment_id},
        ) in instagram_client.called_endpoints

    @pytest.mark.unit
    def test_pagination_support(self, instagram_client: MockInstagramAPI):
        """Test pagination support"""
        media_id = "test_media_123"

        # First page
        comments_page1 = instagram_client.get_media_comments(media_id)
        assert len(comments_page1) == 5

        # Second page
        comments_page2 = instagram_client.get_media_comments(media_id, cursor="page_2")
        assert len(comments_page2) == 5

        assert instagram_client.call_count == 2


class TestInstagramPostTracker:
    """Tests for Instagram Post Tracking"""

    def test_track_new_post(self, sample_post):
        """Test tracking a new post"""
        from src.platforms.instagram.tracker import InstagramPostTracker

        tracker = InstagramPostTracker()
        result = tracker.track_post(sample_post)

        assert result is True

    def test_get_tracked_posts(self):
        """Test retrieving tracked posts"""
        from src.platforms.instagram.tracker import InstagramPostTracker

        tracker = InstagramPostTracker()
        posts = tracker.get_tracked_posts(limit=10)

        assert isinstance(posts, list)
        assert len(posts) <= 10

    def test_update_post_metadata(self, sample_post):
        """Test updating post metadata"""
        from src.platforms.instagram.tracker import InstagramPostTracker

        tracker = InstagramPostTracker()
        result = tracker.update_post_metadata(
            sample_post["id"], {"test_key": "test_value"}
        )

        assert result is True


class TestInstagramCommentModerator:
    """Tests for Instagram Comment Moderation"""

    def test_analyze_comment(self, sample_comment):
        """Test comment analysis"""
        from src.platforms.instagram.moderator import InstagramCommentModerator

        moderator = InstagramCommentModerator()
        analysis = moderator.analyze_comment(sample_comment)

        assert "profanity" in analysis
        assert "spam" in analysis
        assert "harassment" in analysis
        assert "severity" in analysis

    def test_evaluate_delete_rule(self, sample_comment):
        """Test delete rule evaluation"""
        from src.platforms.instagram.moderator import InstagramCommentModerator

        moderator = InstagramCommentModerator()

        # Analyze comment
        analysis = moderator.analyze_comment(sample_comment)
        analysis["profanity"] = True

        # Evaluate rules
        action = moderator.evaluate_rules(analysis)

        assert action == "delete"

    def test_evaluate_allow_rule(self, sample_comment):
        """Test allow rule evaluation"""
        from src.platforms.instagram.moderator import InstagramCommentModerator

        moderator = InstagramCommentModerator()

        # Analyze clean comment
        analysis = moderator.analyze_comment(sample_comment)

        # Evaluate rules
        action = moderator.evaluate_rules(analysis)

        assert action == "allow"

    def test_execute_delete_action(self, sample_comment):
        """Test executing delete action"""
        from src.platforms.instagram.moderator import InstagramCommentModerator

        moderator = InstagramCommentModerator()
        result = moderator.execute_action("delete", sample_comment)

        assert result is True

    @pytest.mark.unit
    def test_moderation_workflow(self, sample_comment):
        """Test complete moderation workflow"""
        from src.platforms.instagram.moderator import InstagramCommentModerator

        moderator = InstagramCommentModerator()

        # Analyze
        analysis = moderator.analyze_comment(sample_comment)

        # Evaluate
        action = moderator.evaluate_rules(analysis)

        # Execute
        result = moderator.execute_action(action, sample_comment)

        assert result is True


class TestInstagramRateLimiter:
    """Tests for Instagram Rate Limiting"""

    def test_rate_limit_initialization(self):
        """Test rate limiter initialization"""
        from src.platforms.instagram.rate_limiter import InstagramRateLimiter

        limiter = InstagramRateLimiter(requests_per_minute=10)

        assert limiter.requests_per_minute == 10

    def test_wait_if_needed_under_limit(self):
        """Test wait when under rate limit"""
        from src.platforms.instagram.rate_limiter import InstagramRateLimiter
        from unittest.mock import patch

        limiter = InstagramRateLimiter(requests_per_minute=10)

        # Make 5 requests (under limit)
        for _ in range(5):
            limiter.record_request()
            limiter.wait_if_needed()

        assert limiter.request_count == 5

    def test_wait_if_needed_over_limit(self):
        """Test wait when over rate limit"""
        from src.platforms.instagram.rate_limiter import InstagramRateLimiter
        from unittest.mock import patch
        import time

        limiter = InstagramRateLimiter(requests_per_minute=10)

        # Make 15 requests (over limit)
        with patch("time.sleep") as mock_sleep:
            for _ in range(15):
                limiter.record_request()
                limiter.wait_if_needed()

            # Should have slept at least once
            assert mock_sleep.called

    @pytest.mark.unit
    def test_backoff_strategy(self):
        """Test exponential backoff strategy"""
        from src.platforms.instagram.rate_limiter import InstagramRateLimiter

        limiter = InstagramRateLimiter(requests_per_minute=10)

        with patch("time.sleep") as mock_sleep:
            for attempt in range(3):
                limiter.wait_with_backoff(attempt, max_retries=3)

            # Exponential backoff: 2^attempt seconds
            expected_sleep_times = [1, 2, 4]
            for i, call in enumerate(mock_sleep.call_args_list):
                assert call[0][0] == expected_sleep_times[i]


class TestInstagramWebhookHandler:
    """Tests for Instagram Webhook Handler"""

    def test_webhook_signature_verification(self):
        """Test webhook signature verification"""
        from src.platforms.instagram.webhooks import InstagramWebhookHandler

        handler = InstagramWebhookHandler(secret="test_secret")

        payload = b"test_payload"
        signature = handler.generate_signature(payload)

        assert handler.verify_signature(payload, signature) is True

    def test_webhook_signature_invalid(self):
        """Test invalid webhook signature"""
        from src.platforms.instagram.webhooks import InstagramWebhookHandler

        handler = InstagramWebhookHandler(secret="test_secret")

        payload = b"test_payload"
        invalid_signature = "invalid_signature"

        assert handler.verify_signature(payload, invalid_signature) is False

    def test_webhook_event_handling(self):
        """Test webhook event handling"""
        from src.platforms.instagram.webhooks import InstagramWebhookHandler

        handler = InstagramWebhookHandler(secret="test_secret")

        event = {"type": "comment.created", "data": {"comment_id": "test_123"}}

        with patch.object(handler, "handle_comment_created") as mock_handler:
            handler.handle_event(event)
            mock_handler.assert_called_once()


class TestInstagramErrorHandling:
    """Tests for Instagram Error Handling"""

    def test_handle_rate_limit_error(self):
        """Test handling rate limit error"""
        from src.platforms.instagram.client import InstagramAPIClient

        client = InstagramAPIClient({"access_token": "test"})

        error_response = mock_error_response(
            status_code=429,
            error_code="rate_limit_exceeded",
            error_message="Rate limit exceeded",
        )

        with patch("requests.get", return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_media("test_media_id")

            assert "Rate limit" in str(exc_info.value)

    def test_handle_authentication_error(self):
        """Test handling authentication error"""
        from src.platforms.instagram.client import InstagramAPIClient

        client = InstagramAPIClient({"access_token": "test"})

        error_response = mock_error_response(
            status_code=401,
            error_code="access_token_invalid",
            error_message="Invalid access token",
        )

        with patch("requests.get", return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_media("test_media_id")

            assert "Invalid access token" in str(exc_info.value)

    def test_handle_not_found_error(self):
        """Test handling not found error"""
        from src.platforms.instagram.client import InstagramAPIClient

        client = InstagramAPIClient({"access_token": "test"})

        error_response = mock_error_response(
            status_code=404,
            error_code="resource_not_found",
            error_message="Resource not found",
        )

        with patch("requests.get", return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_media("nonexistent_media_id")

            assert "not found" in str(exc_info.value).lower()


class TestInstagramIntegration:
    """Integration tests for Instagram platform"""

    @pytest.mark.integration
    @pytest.mark.network
    def test_end_to_end_moderation_workflow(self, sample_comment):
        """Test end-to-end moderation workflow"""
        from src.platforms.instagram.client import InstagramAPIClient
        from src.platforms.instagram.moderator import InstagramCommentModerator

        client = InstagramAPIClient({"access_token": "test_token"})
        moderator = InstagramCommentModerator()

        # Analyze comment
        analysis = moderator.analyze_comment(sample_comment)

        # Check if should be moderated
        if analysis["profanity"]:
            # Execute action
            with patch("requests.delete") as mock_delete:
                moderator.execute_action("delete", sample_comment)

                assert mock_delete.called
        else:
            # Allow comment
            assert moderator.execute_action("allow", sample_comment) is True

    @pytest.mark.integration
    @pytest.mark.network
    def test_batch_comment_processing(self, sample_comments_list):
        """Test batch comment processing"""
        from src.platforms.instagram.client import InstagramAPIClient
        from src.platforms.instagram.moderator import InstagramCommentModerator

        client = InstagramAPIClient({"access_token": "test_token"})
        moderator = InstagramCommentModerator()

        # Process multiple comments
        results = []
        for comment in sample_comments_list(count=10):
            analysis = moderator.analyze_comment(comment)
            action = moderator.evaluate_rules(analysis)
            result = moderator.execute_action(action, comment)
            results.append(result)

        # All should succeed
        assert all(results)

    @pytest.mark.integration
    def test_pagination_across_multiple_pages(self, instagram_client: MockInstagramAPI):
        """Test pagination across multiple pages"""
        media_id = "test_media_123"
        all_comments = []

        for _ in range(3):
            comments = instagram_client.get_media_comments(media_id)
            all_comments.extend(comments)

        # Should have made 3 calls
        assert instagram_client.call_count == 3
        # Should have collected all comments
        assert len(all_comments) == 15
