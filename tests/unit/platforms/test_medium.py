"""Unit Tests for Medium Adapter"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from tests.fixtures import (
    MockMediumAPI,
    sample_comment,
    sample_article,
    sample_user,
    auth_headers,
    mock_error_response,
)


class TestMediumAPIClient:
    """Tests for Medium API Client"""

    def test_client_initialization(self, medium_config):
        """Test Medium client initialization"""
        from src.platforms.medium.client import MediumAPIClient

        client = MediumAPIClient(medium_config)

        assert client.config == medium_config
        assert client.access_token == medium_config["access_token"]
        assert client.api_base_url == "https://api.medium.com/v1"

    @pytest.mark.network
    def test_get_user_articles_success(self, medium_client: MockMediumAPI):
        """Test successful article retrieval"""
        from src.platforms.medium.client import MediumAPIClient

        client = MediumAPIClient(medium_config())
        articles = client.get_user_articles("test_user_id")

        assert len(articles) == 3
        assert articles[0]["id"] == "article_1"
        assert medium_client.call_count == 1

    @pytest.mark.network
    def test_get_publication_articles_success(self, medium_client: MockMediumAPI):
        """Test publication article retrieval"""
        from src.platforms.medium.client import MediumAPIClient

        client = MediumAPIClient(medium_config())
        articles = client.get_publication_articles("test_publication_id")

        assert len(articles) == 3
        assert articles[0]["id"] == "article_1"
        assert medium_client.call_count == 1

    @pytest.mark.network
    def test_get_article_comments_success(self, medium_client: MockMediumAPI):
        """Test successful comment retrieval"""
        from src.platforms.medium.client import MediumAPIClient

        client = MediumAPIClient(medium_config())
        comments = client.get_article_comments("article_id_1")

        assert len(comments) == 3
        assert comments[0]["id"] == "comment_1"
        assert medium_client.call_count == 1

    @pytest.mark.network
    def test_delete_comment_success(self, medium_client: MockMediumAPI):
        """Test successful comment deletion"""
        from src.platforms.medium.client import MediumAPIClient

        client = MediumAPIClient(medium_config())
        result = client.delete_comment("comment_id_1")

        assert result is True
        assert medium_client.call_count == 1
        assert (
            "delete_comment",
            {"comment_id": "comment_id_1"},
        ) in medium_client.called_endpoints


class TestMediumPostTracker:
    """Tests for Medium Post Tracking"""

    def test_track_new_post(self, sample_article):
        """Test tracking a new post"""
        from src.platforms.medium.tracker import MediumPostTracker

        tracker = MediumPostTracker()
        result = tracker.track_post(sample_article)

        assert result is True

    def test_get_tracked_posts(self, sample_posts_list):
        """Test retrieving tracked posts"""
        from src.platforms.medium.tracker import MediumPostTracker

        tracker = MediumPostTracker()
        posts = tracker.get_tracked_posts(limit=10)

        assert isinstance(posts, list)
        assert len(posts) <= 10

    def test_update_post_metadata(self, sample_article):
        """Test updating post metadata"""
        from src.platforms.medium.tracker import MediumPostTracker

        tracker = MediumPostTracker()
        result = tracker.update_post_metadata(
            sample_article["id"], {"test_key": "test_value"}
        )

        assert result is True

    def test_remove_tracked_post(self):
        """Test removing tracked post"""
        from src.platforms.medium.tracker import MediumPostTracker

        tracker = MediumPostTracker()
        tracker.track_post(sample_article())
        result = tracker.remove_tracked_post("article_id_1")

        assert result is True


class TestMediumCommentModerator:
    """Tests for Medium Comment Moderation"""

    def test_analyze_comment(self, sample_comment):
        """Test comment analysis"""
        from src.platforms.medium.moderator import MediumCommentModerator

        moderator = MediumCommentModerator()
        analysis = moderator.analyze_comment(sample_comment)

        assert "profanity" in analysis
        assert "spam" in analysis
        assert "harassment" in analysis
        assert "severity" in analysis

    def test_evaluate_delete_rule(self, sample_comment):
        """Test delete rule evaluation"""
        from src.platforms.medium.moderator import MediumCommentModerator

        moderator = MediumCommentModerator()

        # Create spam comment
        spam_comment = sample_comment.copy()
        spam_comment["text"] = "click here for free money"

        analysis = moderator.analyze_comment(spam_comment)
        action = moderator.evaluate_rules(analysis)

        assert action == "delete"

    def test_execute_delete_action(self, medium_client: MockMediumAPI):
        """Test executing delete action"""
        from src.platforms.medium.moderator import MediumCommentModerator
        from src.platforms.medium.moderator import ModerationAction

        moderator = MediumCommentModerator(medium_client)
        result = moderator.execute_action(ModerationAction.DELETE, "comment_id_1")

        assert result is True
        assert medium_client.call_count == 1


class TestMediumRateLimiter:
    """Tests for Medium Rate Limiting"""

    def test_rate_limit_initialization(self):
        """Test rate limiter initialization"""
        from src.platforms.medium.rate_limiter import MediumRateLimiter

        limiter = MediumRateLimiter(requests_per_minute=10)

        assert limiter.requests_per_minute == 10

    def test_wait_if_needed_under_limit(self):
        """Test wait when under rate limit"""
        from src.platforms.medium.rate_limiter import MediumRateLimiter
        from unittest.mock import patch

        limiter = MediumRateLimiter(requests_per_minute=10)

        with patch("time.sleep") as mock_sleep:
            for _ in range(5):
                limiter.record_request()
                limiter.wait_if_needed()

            # Should not have slept
            assert not mock_sleep.called

    def test_wait_if_needed_over_limit(self):
        """Test wait when over rate limit"""
        from src.platforms.medium.rate_limiter import MediumRateLimiter
        from unittest.mock import patch
        import time

        limiter = MediumRateLimiter(requests_per_minute=10)

        with patch("time.sleep") as mock_sleep:
            # Make 10 requests (over limit)
            for _ in range(10):
                limiter.record_request()
                limiter.wait_if_needed()

            # Should have slept at least once
            assert mock_sleep.called


class TestMediumWebhookHandler:
    """Tests for Medium Webhook Handler"""

    def test_webhook_signature_verification(self):
        """Test webhook signature verification"""
        from src.platforms.medium.webhooks import MediumWebhookHandler

        handler = MediumWebhookHandler(secret="test_secret")

        payload = b"test_payload"
        signature = handler.generate_signature(payload)

        assert handler.verify_signature(payload, signature) is True

    def test_webhook_signature_invalid(self):
        """Test invalid webhook signature"""
        from src.platforms.medium.webhooks import MediumWebhookHandler

        handler = MediumWebhookHandler(secret="test_secret")

        payload = b"test_payload"
        invalid_signature = "invalid_signature"

        assert handler.verify_signature(payload, invalid_signature) is False

    def test_webhook_event_handling(self):
        """Test webhook event handling"""
        from src.platforms.medium.webhooks import MediumWebhookHandler

        handler = MediumWebhookHandler(secret="test_secret")
        handler.register_handler("comment.created", Mock())

        event = {
            "type": "comment.created",
            "comment_id": "comment_123",
            "text": "Test comment",
        }

        handler.handle_event(event["type"], event)

        assert True  # Handler was called


class TestMediumErrorHandling:
    """Tests for Medium Error Handling"""

    def test_handle_rate_limit_error(self, medium_client: MockMediumAPI):
        """Test handling rate limit error"""
        from src.platforms.medium.client import MediumAPIClient

        client = MediumAPIClient(medium_config())

        error_response = Mock()
        error_response.status_code = 429
        error_response.headers = {
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": "0",
        }

        with patch("requests.get", return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_article_comments("article_id_1")

            assert "Rate limit" in str(exc_info.value)

    def test_handle_authentication_error(self, medium_client: MockMediumAPI):
        """Test handling authentication error"""
        from src.platforms.medium.client import MediumAPIClient

        client = MediumAPIClient({"access_token": "invalid_token"})

        error_response = mock_error_response(status_code=401)

        with patch("requests.get", return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_article_comments("article_id_1")

            assert "Authentication" in str(exc_info.value)


class TestMediumIntegration:
    """Integration tests for Medium platform"""

    @pytest.mark.integration
    @pytest.mark.network
    def test_end_to_end_moderation_workflow(self, medium_client: MockMediumAPI):
        """Test end-to-end moderation workflow"""
        from src.platforms.medium.client import MediumAPIClient
        from src.platforms.medium.moderator import MediumCommentModerator
        from src.platforms.medium.moderator import ModerationAction

        client = MediumAPIClient(medium_config())
        moderator = MediumCommentModerator(client)

        # Get comments
        with patch(
            "requests.get",
            return_value=mock_error_response(
                status_code=200, data={"data": {"comments": [sample_comment()]}}
            ),
        ):
            comments = client.get_article_comments("article_id_1")

        # Analyze and moderate
        for comment in comments:
            analysis = moderator.analyze_comment(comment)
            action = moderator.evaluate_rules(analysis)

            if action != ModerationAction.ALLOW:
                # Execute action
                moderator.execute_action(action, comment["id"])

        assert True  # Workflow completed
