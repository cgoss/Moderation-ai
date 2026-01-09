"""Unit Tests for TikTok Adapter"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from tests.fixtures import (
    MockTikTokAPI,
    sample_comment,
    sample_video,
    sample_user,
    auth_headers,
    mock_error_response,
)


class TestTikTokAPIClient:
    """Tests for TikTok API Client"""

    def test_client_initialization(self, tiktok_config):
        """Test TikTok client initialization"""
        from src.platforms.tiktok.client import TikTokAPIClient

        client = TikTokAPIClient(tiktok_config)

        assert client.config == tiktok_config
        assert client.access_token == tiktok_config["access_token"]
        assert client.api_base_url == tiktok_config["api_base_url"]

    @pytest.mark.network
    def test_get_user_info_success(self, tiktok_client: MockTikTokAPI):
        """Test successful user info retrieval"""
        tiktok_client.get_user_info.return_value = {
            "data": {
                "user": {
                    "union_id": "test_user_123",
                    "display_name": "Test User",
                    "username": "testuser",
                    "is_verified": True,
                }
            }
        }

        response = tiktok_client.get_user_info()

        assert response["user"]["union_id"] == "test_user_123"
        assert response["user"]["display_name"] == "Test User"
        assert tiktok_client.call_count == 1

    @pytest.mark.network
    def test_get_user_videos_success(self, tiktok_client: MockTikTokAPI):
        """Test successful video retrieval"""
        tiktok_client.get_user_videos.return_value = {
            "data": {"videos": [sample_video()], "has_more": False}
        }

        response = tiktok_client.get_user_videos()

        assert len(response["videos"]) == 1
        assert tiktok_client.call_count == 1

    @pytest.mark.network
    def test_get_video_details_success(self, tiktok_client: MockTikTokAPI):
        """Test successful video details retrieval"""
        tiktok_client.get_video_details.return_value = {
            "data": {"videos": [sample_video()]}
        }

        video_id = "video_test_012"
        response = tiktok_client.get_video_details(video_id)

        assert len(response["videos"]) == 1
        assert tiktok_client.call_count == 1

    @pytest.mark.network
    def test_get_video_comments_success(self, tiktok_client: MockTikTokAPI):
        """Test successful comment retrieval"""
        tiktok_client.get_video_comments.return_value = {
            "data": {"comments": [sample_comment()], "has_more": False}
        }

        video_id = "video_test_012"
        response = tiktok_client.get_video_comments(video_id)

        assert len(response["comments"]) == 1
        assert tiktok_client.call_count == 1

    @pytest.mark.network
    def test_delete_comment_success(self, tiktok_client: MockTikTokAPI):
        """Test successful comment deletion"""
        tiktok_client.delete_comment.return_value = {"data": {}}

        comment_id = "comment_test_123"
        result = tiktok_client.delete_comment(comment_id)

        assert result is True
        assert tiktok_client.call_count == 1
        assert (
            "delete_comment",
            {"comment_id": comment_id},
        ) in tiktok_client.called_endpoints

    @pytest.mark.network
    def test_pin_comment_success(self, tiktok_client: MockTikTokAPI):
        """Test successful comment pinning"""
        tiktok_client.pin_comment.return_value = {"data": {}}

        comment_id = "comment_test_123"
        result = tiktok_client.pin_comment(comment_id)

        assert result is True
        assert tiktok_client.call_count == 1
        assert (
            "pin_comment",
            {"comment_id": comment_id},
        ) in tiktok_client.called_endpoints


class TestTikTokVideoTracker:
    """Tests for TikTok Video Tracking"""

    def test_track_new_video(self, sample_video):
        """Test tracking a new video"""
        from src.platforms.tiktok.tracker import TikTokVideoTracker

        tracker = TikTokVideoTracker()
        result = tracker.track_video(sample_video)

        assert result is True

    def test_get_tracked_videos(self, sample_videos_list):
        """Test retrieving tracked videos"""
        from src.platforms.tiktok.tracker import TikTokVideoTracker

        tracker = TikTokVideoTracker()
        for video in sample_videos_list(count=3):
            tracker.track_video(video)

        videos = tracker.get_tracked_videos(limit=10)

        assert len(videos) <= 3

    def test_update_video_metadata(self, sample_video):
        """Test updating video metadata"""
        from src.platforms.tiktok.tracker import TikTokVideoTracker

        tracker = TikTokVideoTracker()
        tracker.track_video(sample_video)
        result = tracker.update_video_metadata(
            sample_video["id"], {"test_key": "test_value"}
        )

        assert result is True


class TestTikTokCommentModerator:
    """Tests for TikTok Comment Moderation"""

    def test_analyze_comment(self, sample_comment):
        """Test comment analysis"""
        from src.platforms.tiktok.moderator import TikTokCommentModerator

        moderator = TikTokCommentModerator()
        analysis = moderator.analyze_comment(sample_comment)

        assert "comment_id" in analysis
        assert "text" in analysis
        assert "spam" in analysis
        assert "profanity" in analysis
        assert "harassment" in analysis
        assert "word_count" in analysis
        assert "severity" in analysis

    def test_evaluate_delete_rule(self, sample_comment):
        """Test delete rule evaluation"""
        from src.platforms.tiktok.moderator import TikTokCommentModerator

        moderator = TikTokCommentModerator()

        # Set up spam comment
        spam_comment = sample_comment.copy()
        spam_comment["text"] = "click here for free money"

        analysis = moderator.analyze_comment(spam_comment)
        action = moderator.evaluate_rules(analysis)

        assert action == "delete"

    def test_evaluate_allow_rule(self, sample_comment):
        """Test allow rule evaluation"""
        from src.platforms.tiktok.moderator import TikTokCommentModerator

        moderator = TikTokCommentModerator()
        analysis = moderator.analyze_comment(sample_comment)
        action = moderator.evaluate_rules(analysis)

        assert action == "allow"

    def test_execute_delete_action(self, tiktok_client: MockTikTokAPI, sample_comment):
        """Test executing delete action"""
        from src.platforms.tiktok.moderator import TikTokCommentModerator

        moderator = TikTokCommentModerator(tiktok_client)
        result = moderator.execute_action("delete", sample_comment)

        assert result is True
        assert tiktok_client.call_count == 1


class TestTikTokRateLimiter:
    """Tests for TikTok Rate Limiting"""

    def test_rate_limit_initialization(self):
        """Test rate limiter initialization"""
        from src.platforms.tiktok.rate_limiter import TikTokRateLimiter

        limiter = TikTokRateLimiter(requests_per_minute=10)

        assert limiter.requests_per_minute == 10

    def test_record_request(self):
        """Test recording requests"""
        from src.platforms.tiktok.rate_limiter import TikTokRateLimiter

        limiter = TikTokRateLimiter(requests_per_minute=10)

        for _ in range(5):
            limiter.record_request()

        assert limiter.request_count == 5

    def test_wait_if_needed_under_limit(self):
        """Test wait when under rate limit"""
        from src.platforms.tiktok.rate_limiter import TikTokRateLimiter
        from unittest.mock import patch

        limiter = TikTokRateLimiter(requests_per_minute=10)

        with patch("time.sleep") as mock_sleep:
            for _ in range(5):
                limiter.record_request()
                limiter.wait_if_needed()

            # Should not have slept
            assert not mock_sleep.called


class TestTikTokWebhookHandler:
    """Tests for TikTok Webhook Handler"""

    def test_webhook_signature_verification(self):
        """Test webhook signature verification"""
        from src.platforms.tiktok.webhooks import TikTokWebhookHandler

        handler = TikTokWebhookHandler(secret="test_secret")

        payload = b"test_payload"
        signature = handler.generate_signature(payload)

        assert handler.verify_signature(payload, signature) is True

    def test_webhook_signature_invalid(self):
        """Test invalid webhook signature"""
        from src.platforms.tiktok.webhooks import TikTokWebhookHandler

        handler = TikTokWebhookHandler(secret="test_secret")

        payload = b"test_payload"
        invalid_signature = "invalid_signature"

        assert handler.verify_signature(payload, invalid_signature) is False

    def test_webhook_event_handling(self):
        """Test webhook event handling"""
        from src.platforms.tiktok.webhooks import TikTokWebhookHandler

        handler = TikTokWebhookHandler(secret="test_secret")
        handler.register_handler("comment.created", Mock())

        event = {
            "type": "comment.created",
            "comment_id": "comment_123",
            "video_id": "video_123",
        }

        with patch.object(handler, "handle_comment_created") as mock_handler:
            handler.handle_event("comment.created", event)

        mock_handler.assert_called_once()


class TestTikTokErrorHandling:
    """Tests for TikTok Error Handling"""

    def test_handle_rate_limit_error(self, tiktok_client: MockTikTokAPI):
        """Test handling rate limit error"""
        from src.platforms.tiktok.client import TikTokAPIClient

        client = TikTokAPIClient(tiktok_config={"access_token": "test"})

        error_response = mock_error_response(
            status_code=429, error_code="rate_limit_exceeded"
        )

        with patch("requests.get", return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_user_videos()

            assert "Rate limit" in str(exc_info.value)


class TestTikTokIntegration:
    """Integration tests for TikTok platform"""

    @pytest.mark.integration
    @pytest.mark.network
    def test_end_to_end_moderation_workflow(
        self, tiktok_client: MockTikTokAPI, sample_comment
    ):
        """Test end-to-end moderation workflow"""
        from src.platforms.tiktok.moderator import TikTokCommentModerator

        client = TikTokAPIClient(tiktok_config={"access_token": "test"})
        moderator = TikTokCommentModerator(client)

        # Analyze comment
        analysis = moderator.analyze_comment(sample_comment)

        # Check if should moderate
        if analysis["spam"]:
            # Execute delete
            with patch.object(tiktok_client, "delete_comment", return_value=True):
                result = moderator.execute_action("delete", sample_comment)

            assert result is True
        else:
            # Allow
            result = moderator.execute_action("allow", sample_comment)
            assert result is True

    @pytest.mark.integration
    @pytest.mark.network
    def test_batch_comment_processing(
        self, tiktok_client: MockTikTokAPI, sample_comments_list
    ):
        """Test batch comment processing"""
        from src.platforms.tiktok.moderator import TikTokCommentModerator

        client = TikTokAPIClient(tiktok_config={"access_token": "test"})
        moderator = TikTokCommentModerator(client)

        # Set up mock response with 5 comments
        mock_response = {"data": {"comments": sample_comments_list(count=5)}}

        with patch("requests.get", return_value=mock_response):
            comments = tiktok_client.get_video_comments("video_123")

        # Moderate all comments
        results = []
        for comment in comments:
            analysis = moderator.analyze_comment(comment)
            action = moderator.evaluate_rules(analysis)
            if action != "allow":
                with patch.object(tiktok_client, "delete_comment", return_value=True):
                    result = moderator.execute_action(action, comment)
                    results.append(result)

        # All should succeed
        assert all(results)
