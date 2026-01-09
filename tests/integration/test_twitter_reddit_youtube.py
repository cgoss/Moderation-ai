"""Integration tests for Twitter, Reddit, and YouTube platforms."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.core.base import Comment, Post, ModerationAction


@pytest.fixture
def mock_twitter_response():
    """Create mock HTTP response for Twitter API."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "data": {
            "id": "1234567890",
            "text": "Test tweet",
            "created_at": "2024-01-09T00:00:00Z",
            "public_metrics": {"like_count": 10, "retweet_count": 5, "reply_count": 3},
            "author_id": "user123",
        }
    }
    response.text = '{"data": {"id": "1234567890"}}'
    return response


@pytest.fixture
def mock_reddit_response():
    """Create mock HTTP response for Reddit API."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "data": {
            "children": [
                {
                    "kind": "t1",
                    "data": {
                        "id": "abc123",
                        "author": "TestUser",
                        "author_id": "user456",
                        "created_utc": 1704796800.0,
                        "body": "Test comment",
                        "score": 5,
                        "subreddit": "test",
                    },
                }
            ]
        }
    }
    return response


@pytest.fixture
def mock_youtube_response():
    """Create mock HTTP response for YouTube Data API."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "items": [
            {
                "id": "video123",
                "snippet": {
                    "title": "Test Video",
                    "description": "Test description",
                    "channelTitle": "Test Channel",
                    "channelId": "UC123",
                    "publishedAt": "2024-01-09T00:00:00Z",
                },
                "statistics": {
                    "likeCount": "100",
                    "viewCount": "1000",
                    "commentCount": "25",
                },
            }
        ]
    }
    return response


class TestTwitterIntegration:
    """Integration tests for Twitter platform."""

    @pytest.mark.unit
    def test_twitter_authentication(self, mock_twitter_response):
        """Test Twitter authentication."""
        with patch("requests.get", return_value=mock_twitter_response()):
            from src.platforms.twitter import TwitterPlatform

            config = {"api_key": "test_key", "api_secret": "test_secret"}

            client = TwitterPlatform(config=config)

            assert client.authenticate(config) is True
            assert client.is_authenticated() is True

    @pytest.mark.unit
    def test_twitter_fetch_tweets(self, mock_twitter_response):
        """Test fetching tweets from Twitter."""
        with patch("requests.get", return_value=mock_twitter_response()):
            from src.platforms.twitter import TwitterPlatform

            client = TwitterPlatform(config={"bearer_token": "test_token"})
            client._authenticated = True

            posts = client.fetch_posts("@testuser", limit=5)

            assert len(posts) == 5
            assert all(post.platform == "twitter" for post in posts)

    @pytest.mark.unit
    def test_twitter_fetch_comments(self, mock_twitter_response):
        """Test fetching comments from Twitter."""
        with patch("requests.get", return_value=mock_twitter_response()):
            from src.platforms.twitter import TwitterPlatform

            client = TwitterPlatform(config={"bearer_token": "test_token"})
            client._authenticated = True

            comments = client.fetch_comments("1234567890", limit=10)

            assert len(comments) > 0
            assert all(comment.platform == "twitter" for comment in comments)

    @pytest.mark.unit
    def test_twitter_moderate_comment(self):
        """Test comment moderation on Twitter."""
        from src.platforms.twitter import TwitterPlatform

        client = TwitterPlatform(config={"bearer_token": "test_token"})
        client._authenticated = True

        result = client.moderate_comment(
            "comment123", ModerationAction.REMOVE, reason="Test moderation"
        )

        assert result is True

    @pytest.mark.unit
    def test_twitter_rate_limiting(self):
        """Test Twitter rate limiting."""
        from src.platforms.twitter import TwitterPlatform
        from src.utils.error_handler import RateLimitError

        client = TwitterPlatform(config={"bearer_token": "test_token"})
        client._authenticated = True

        with patch.object(client, "_api_client") as mock_api:
            from tweepy.errors import RateLimitError

            mock_api.get_mentions.side_effect = RateLimitError()

        with pytest.raises(RateLimitError):
            client.fetch_comments("tweet123")

    @pytest.mark.unit
    def test_twitter_error_handling(self):
        """Test Twitter error handling."""
        from src.platforms.twitter import TwitterPlatform
        from src.utils.error_handler import PlatformError
        import requests.exceptions

        client = TwitterPlatform(config={"bearer_token": "test_token"})
        client._authenticated = True

        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

            with pytest.raises(PlatformError):
                client.fetch_posts("test_query")


class TestRedditIntegration:
    """Integration tests for Reddit platform."""

    @pytest.mark.unit
    def test_reddit_authentication(self, mock_reddit_response):
        """Test Reddit authentication."""
        with patch("praw.Reddit") as mock_reddit_class:
            from src.platforms.reddit import RedditPlatform

            mock_reddit = MagicMock()
            mock_reddit.user.me.return_value.id = "user123"

            with patch.object(mock_reddit_class, "__init__", return_value=mock_reddit):
                client = RedditPlatform(
                    config={"client_id": "test_id", "client_secret": "test_secret"}
                )

            assert client.is_authenticated() is True

    @pytest.mark.unit
    def test_reddit_fetch_posts(self, mock_reddit_response):
        """Test fetching posts from Reddit."""
        with patch("praw.Reddit") as mock_reddit_class:
            from src.platforms.reddit import RedditPlatform

            mock_reddit = MagicMock()
            mock_subreddit = MagicMock()
            mock_subreddit.hot.return_value = [
                Mock(id="post1", title="Post 1"),
                Mock(id="post2", title="Post 2"),
            ]
            mock_reddit.subreddit.return_value = mock_subreddit
            mock_reddit.subreddit.return_value = mock_reddit

            with patch.object(mock_reddit_class, "__init__", return_value=mock_reddit):
                client = RedditPlatform(
                    config={"client_id": "test_id", "client_secret": "test_secret"}
                )
                client._authenticated = True

            posts = client.fetch_posts("test_subreddit", limit=5)

            assert len(posts) == 5
            assert all(post.platform == "reddit" for post in posts)

    @pytest.mark.unit
    def test_reddit_fetch_comments(self, mock_reddit_response):
        """Test fetching comments from Reddit."""
        with patch("praw.Reddit") as mock_reddit_class:
            from src.platforms.reddit import RedditPlatform

            mock_submission = Mock(id="post1", subreddit_name="test")
            mock_submission.comments.replace_more.return_value = []

            mock_reddit = MagicMock()
            mock_reddit.submission.return_value = mock_submission

            with patch.object(mock_reddit_class, "__init__", return_value=mock_reddit):
                client = RedditPlatform(
                    config={"client_id": "test_id", "client_secret": "test_secret"}
                )
                client._authenticated = True

            comments = client.fetch_comments("post1", limit=10)

            assert len(comments) > 0
            assert all(comment.platform == "reddit" for comment in comments)

    @pytest.mark.unit
    def test_reddit_moderate_comment(self):
        """Test comment moderation on Reddit."""
        with patch("praw.Reddit") as mock_reddit_class:
            from src.platforms.reddit import RedditPlatform

            mock_comment = Mock(id="comment123")
            mock_reddit.comment.return_value = mock_comment

            with patch.object(mock_reddit_class, "__init__", return_value=mock_reddit):
                client = RedditPlatform(
                    config={"client_id": "test_id", "client_secret": "test_secret"}
                )
                client._authenticated = True

            result = client.moderate_comment(
                "comment123", ModerationAction.REMOVE, reason="Test moderation"
            )

            assert result is True

    @pytest.mark.unit
    def test_reddit_rate_limiting(self):
        """Test Reddit rate limiting."""
        from src.platforms.reddit import RedditPlatform
        from src.utils.error_handler import RateLimitError
        import praw.exceptions

        client = RedditPlatform(
            config={"client_id": "test_id", "client_secret": "test_secret"}
        )
        client._authenticated = True

        with patch.object(client, "_reddit") as mock_reddit:
            mock_reddit.subreddit.return_value.hot.side_effect = (
                praw.exceptions.RateLimit()
            )

            with pytest.raises(RateLimitError):
                client.fetch_posts("test_subreddit")


class TestYouTubeIntegration:
    """Integration tests for YouTube platform."""

    @pytest.mark.unit
    def test_youtube_authentication(self, mock_youtube_response):
        """Test YouTube authentication."""
        with patch("googleapiclient.discovery.build") as mock_build:
            from src.platforms.youtube import YouTubePlatform

            mock_youtube = MagicMock()
            mock_youtube.videos.return_value.list.return_value = [Mock()]

            with patch.object(mock_youtube, "__init__", return_value=mock_youtube):
                client = YouTubePlatform(config={"api_key": "test_key"})

            assert client.is_authenticated() is True

    @pytest.mark.unit
    def test_youtube_fetch_videos(self, mock_youtube_response):
        """Test fetching videos from YouTube."""
        with patch("googleapiclient.discovery.build") as mock_build:
            from src.platforms.youtube import YouTubePlatform

            client = YouTubePlatform(config={"api_key": "test_key"})
            client._authenticated = True

            videos = client.fetch_posts("test_query", limit=5)

            assert len(videos) == 5
            assert all(video.platform == "youtube" for video in videos)

    @pytest.mark.unit
    def test_youtube_fetch_comments(self, mock_youtube_response):
        """Test fetching comments from YouTube."""
        with patch("googleapiclient.discovery.build") as mock_build:
            from src.platforms.youtube import YouTubePlatform

            client = YouTubePlatform(config={"api_key": "test_key"})
            client._authenticated = True

            comments = client.fetch_comments("video123", limit=10)

            assert len(comments) > 0
            assert all(comment.platform == "youtube" for comment in comments)

    @pytest.mark.unit
    def test_youtube_moderate_comment(self):
        """Test comment moderation on YouTube."""
        with patch("googleapiclient.discovery.build") as mock_build:
            from src.platforms.youtube import YouTubePlatform

            client = YouTubePlatform(config={"api_key": "test_key"})
            client._authenticated = True

            result = client.moderate_comment(
                "comment123", ModerationAction.FLAG, reason="Test moderation"
            )

            assert result is True

    @pytest.mark.unit
    def test_youtube_rate_limiting(self):
        """Test YouTube rate limiting."""
        with patch("googleapiclient.discovery.build") as mock_build:
            from src.platforms.youtube import YouTubePlatform
            from src.utils.error_handler import RateLimitError

            client = YouTubePlatform(config={"api_key": "test_key"})
            client._authenticated = True

            mock_youtube = MagicMock()
            mock_youtube.commentThreads.return_value.list.side_effect = RateLimitError()

            with pytest.raises(RateLimitError):
                client.fetch_comments("video123")

    @pytest.mark.unit
    def test_youtube_error_handling(self):
        """Test YouTube error handling."""
        with patch("googleapiclient.discovery.build") as mock_build:
            from src.platforms.youtube import YouTubePlatform
            from src.utils.error_handler import PlatformError
            import googleapiclient.errors

            client = YouTubePlatform(config={"api_key": "test_key"})
            client._authenticated = True

            with patch.object(client, "_youtube") as mock_youtube:
                mock_youtube.videos.side_effect = googleapiclient.errors.HttpError(
                    "API error"
                )

                with pytest.raises(PlatformError):
                    client.fetch_posts("test_query")


class TestAllPlatforms:
    """Cross-platform integration tests."""

    @pytest.mark.unit
    def test_all_platforms_available(self):
        """Test that all platforms can be imported."""
        platforms = [
            ("Twitter", "src.platforms.twitter"),
            ("Reddit", "src.platforms.reddit"),
            ("YouTube", "src.platforms.youtube"),
            ("Instagram", "src.platforms.instagram"),
            ("Medium", "src.platforms.medium"),
            ("TikTok", "src.platforms.tiktok"),
        ]

        for name, module in platforms:
            try:
                __import__(module)
            except ImportError:
                pytest.fail(f"Cannot import {module}")

        assert True

    @pytest.mark.unit
    def test_cross_platform_comment_moderation(self):
        """Test that moderation logic is consistent across platforms."""
        from src.platforms.twitter import TwitterPlatform
        from src.platforms.reddit import RedditPlatform
        from src.platforms.youtube import YouTubePlatform

        test_comment = Comment(
            id="test_comment_1",
            text="This is a test comment with bad language",
            author_id="user1",
            author_name="Test User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="test_post",
        )

        for platform_class, config_name in [
            (TwitterPlatform, "twitter", {"bearer_token": "test_token"}),
            (
                RedditPlatform,
                "reddit",
                {"client_id": "test_id", "client_secret": "test_secret"},
            ),
            (YouTubePlatform, "youtube", {"api_key": "test_key"}),
        ]:
            client = platform_class(config=config_name)
            client._authenticated = True

            result = client.moderate_comment(
                "test_comment_1", ModerationAction.FLAG, reason="Inappropriate content"
            )

            assert result is True
            assert result.action == ModerationAction.FLAG


if __name__ == "__main__":
    pytest.main([__file__], "-v")
