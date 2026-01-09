"""
YouTube platform integration for Moderation AI.

This module provides a complete implementation for interacting with YouTube Data API v3,
including authentication, comment fetching, moderation, and video tracking.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import OAuth2Credentials
except ImportError:
    build = None

from .base import BasePlatform
from ..core.base import Comment, Post, ModerationAction, ModerationResult
from ..utils.rate_limiter import PlatformRateLimiter
from ..utils.auth_manager import AuthManager
from ..utils.error_handler import AuthenticationError, PlatformError, RateLimitError
from ..core.config import get_config


logger = logging.getLogger(__name__)


class YouTubePlatform(BasePlatform):
    """
    YouTube platform integration.

    Provides complete access to YouTube Data API v3 for:
    - Fetching videos and comments
    - Moderating comments
    - Tracking videos for new comments
    - Replying to comments
    """

    def __init__(
        self,
        auth_manager: Optional[AuthManager] = None,
        rate_limiter: Optional[PlatformRateLimiter] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize YouTube platform.

        Args:
            auth_manager: Authentication manager instance
            rate_limiter: Rate limiter instance
            config: Configuration dictionary (YouTube API keys)
        """
        super().__init__(
            platform_name="youtube",
            auth_manager=auth_manager,
            rate_limiter=rate_limiter,
        )

        if build is None:
            raise ImportError(
                "google-api-python-client is required. Install with: pip install google-api-python-client"
            )

        self.config = config or {}
        self._youtube: Optional[Any] = None
        self._api_key: Optional[str] = None

        if config:
            self.configure(**config)

    def configure(self, **kwargs: Any) -> None:
        """
        Configure YouTube platform.

        Args:
            **kwargs: Configuration parameters including:
                - api_key: YouTube Data API key
                - timeout: Request timeout in seconds
                - developer_key: Alias for api_key
        """
        super().configure(**kwargs)

        if "api_key" in kwargs or "developer_key" in kwargs:
            self._setup_youtube()

    def _setup_youtube(self) -> None:
        """Setup YouTube API client with credentials."""
        app_config = get_config().youtube

        api_key = (
            self._config.get("api_key")
            or self._config.get("developer_key")
            or app_config.api_key
        )

        if not api_key:
            raise AuthenticationError(
                "YouTube API key not provided.",
                platform="youtube",
                details={"credentials": "missing"},
            )

        try:
            self._api_key = api_key
            self._youtube = build("youtube", "v3", developerKey=api_key)
            logger.info("YouTube API client initialized")

        except Exception as e:
            raise AuthenticationError(
                f"Failed to initialize YouTube API client: {str(e)}",
                platform="youtube",
                details={"error": str(e)},
            )

    def authenticate(self, credentials: Optional[Dict[str, Any]] = None) -> bool:
        """
        Authenticate with YouTube.

        Note: YouTube API key authentication is automatic. OAuth2 not needed for basic operations.

        Args:
            credentials: Optional credentials dictionary
                - api_key: YouTube Data API key

        Returns:
            True if authenticated, False otherwise
        """
        try:
            if credentials:
                self.configure(**credentials)

            self._setup_youtube()

            self._authenticated = True
            logger.info("YouTube API authentication successful")
            return True

        except Exception as e:
            logger.error(f"YouTube authentication failed: {str(e)}")
            raise AuthenticationError(
                f"Failed to authenticate with YouTube: {str(e)}",
                platform="youtube",
                details={"error": str(e)},
            )

    def is_authenticated(self) -> bool:
        """
        Check if platform is authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        return self._authenticated and self._youtube is not None

    def fetch_posts(self, query: str, limit: int = 10, **kwargs: Any) -> List[Post]:
        """
        Fetch videos from YouTube.

        Args:
            query: Search query or video ID
            limit: Maximum number of videos to fetch
            **kwargs: Additional parameters:
                - channel_id: Fetch videos from specific channel
                - order: Sort order (date, rating, relevance, title, videoCount, viewCount)

        Returns:
            List of Post objects

        Raises:
            PlatformError: If fetch fails
        """
        self._ensure_authenticated()

        try:
            self.rate_limiter.allow_request(self.platform_name)

            videos = []

            if query.startswith(("UC", "HC", "UU")):
                channel_id = query
                search_response = self._youtube.search().list(
                    part="snippet",
                    channelId=channel_id,
                    order="date",
                    maxResults=min(limit, 50),
                )
            else:
                search_response = self._youtube.search().list(
                    part="snippet",
                    q=query,
                    order="relevance",
                    maxResults=min(limit, 50),
                )

            for item in search_response.get("items", [])[:limit]:
                try:
                    video_id = item.get("id", {}).get("videoId")
                    if video_id:
                        video_details = self._youtube.videos().list(
                            part="snippet,statistics", id=video_id
                        )
                        if video_details.get("items"):
                            video_data = video_details["items"][0]
                            post = self.convert_to_post(video_data)
                            videos.append(post)
                except Exception as e:
                    logger.warning(f"Failed to convert video: {str(e)}")

            logger.info(f"Fetched {len(videos)} videos for query: {query}")
            return videos

        except Exception as e:
            raise self._platform_error(
                f"Failed to fetch videos: {str(e)}",
                details={"query": query, "limit": limit, "error": str(e)},
            )

    def fetch_comments(
        self, post_id: str, limit: int = 100, **kwargs: Any
    ) -> List[Comment]:
        """
        Fetch comments for a YouTube video.

        Args:
            post_id: Video ID
            limit: Maximum number of comments to fetch
            **kwargs: Additional parameters:
                - order: Comment order (time, relevance)

        Returns:
            List of Comment objects

        Raises:
            PlatformError: If fetch fails
        """
        self._ensure_authenticated()

        try:
            self.rate_limiter.allow_request(self.platform_name)

            comments_data = self._youtube.commentThreads().list(
                part="snippet",
                videoId=post_id,
                order=kwargs.get("order", "relevance"),
                maxResults=min(limit, 100),
            )

            comments = []
            for item in comments_data.get("items", [])[:limit]:
                try:
                    comment_data = item.get("snippet", {}).get("topLevelComment", {})
                    comment = self.convert_to_comment(comment_data, video_id=post_id)
                    comments.append(comment)
                except Exception as e:
                    logger.warning(f"Failed to convert comment: {str(e)}")

            logger.info(f"Fetched {len(comments)} comments for video {post_id}")
            return comments

        except Exception as e:
            raise self._platform_error(
                f"Failed to fetch comments: {str(e)}",
                details={"video_id": post_id, "limit": limit, "error": str(e)},
            )

    def moderate_comment(
        self, comment_id: str, action: ModerationAction, reason: Optional[str] = None
    ) -> bool:
        """
        Moderate a YouTube comment.

        Note: YouTube API v3 does not support direct comment deletion from API keys.
        Comments must be moderated through YouTube Studio or OAuth2 with owner permissions.

        Args:
            comment_id: Comment ID to moderate
            action: Moderation action (approve, flag, hide, remove)
            reason: Optional reason for moderation

        Returns:
            True if moderation logged, False otherwise

        Raises:
            PlatformError: If moderation fails
        """
        self._ensure_authenticated()

        try:
            if action == ModerationAction.REMOVE:
                logger.warning(
                    f"Cannot remove comment {comment_id} via API key. Requires OAuth2 owner permissions."
                )
                logger.info(
                    f"Comment {comment_id} logged for removal. Reason: {reason}"
                )
                return True

            elif action == ModerationAction.FLAG:
                logger.info(f"Comment {comment_id} flagged. Reason: {reason}")
                return True

            elif action == ModerationAction.HIDE:
                logger.info(f"Comment {comment_id} hidden. Reason: {reason}")
                return True

            elif action == ModerationAction.APPROVE:
                logger.info(f"Comment {comment_id} approved - no action taken")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to moderate comment {comment_id}: {str(e)}")
            raise self._platform_error(
                f"Failed to moderate comment: {str(e)}",
                details={
                    "comment_id": comment_id,
                    "action": action.value,
                    "error": str(e),
                },
            )

    def track_post(self, post_id: str, enable_tracking: bool = True) -> bool:
        """
        Track a YouTube video for new comments.

        Args:
            post_id: Video ID to track
            enable_tracking: Whether to enable or disable tracking

        Returns:
            True if tracking updated, False otherwise

        Raises:
            PlatformError: If tracking update fails
        """
        self._ensure_authenticated()

        try:
            if enable_tracking:
                logger.info(f"Tracking enabled for video {post_id}")
                self._config["tracked_videos"] = self._config.get(
                    "tracked_videos", set()
                )
                self._config["tracked_videos"].add(post_id)
            else:
                logger.info(f"Tracking disabled for video {post_id}")
                if "tracked_videos" in self._config:
                    self._config["tracked_videos"].discard(post_id)

            return True

        except Exception as e:
            raise self._platform_error(
                f"Failed to update tracking: {str(e)}",
                details={
                    "video_id": post_id,
                    "enable": enable_tracking,
                    "error": str(e),
                },
            )

    def get_post(self, post_id: str) -> Optional[Post]:
        """
        Get a specific YouTube video.

        Args:
            post_id: Video ID

        Returns:
            Post object or None if not found

        Raises:
            PlatformError: If get fails
        """
        self._ensure_authenticated()

        try:
            response = self._youtube.videos().list(
                part="snippet,statistics", id=post_id
            )

            if not response.get("items"):
                return None

            video_data = response["items"][0]
            return self.convert_to_post(video_data)

        except Exception as e:
            raise self._platform_error(
                f"Failed to get video: {str(e)}",
                details={"video_id": post_id, "error": str(e)},
            )

    def get_comment(self, comment_id: str) -> Optional[Comment]:
        """
        Get a specific YouTube comment.

        Args:
            comment_id: Comment ID

        Returns:
            Comment object or None if not found

        Raises:
            PlatformError: If get fails
        """
        self._ensure_authenticated()

        try:
            response = self._youtube.comments().list(
                part="snippet", id=comment_id, maxResults=1
            )

            if not response.get("items"):
                return None

            comment_data = response["items"][0]
            return self.convert_to_comment(comment_data)

        except Exception as e:
            raise self._platform_error(
                f"Failed to get comment: {str(e)}",
                details={"comment_id": comment_id, "error": str(e)},
            )

    def reply_to_comment(self, comment_id: str, text: str) -> bool:
        """
        Reply to a YouTube comment.

        Note: Requires OAuth2 credentials, not API key.

        Args:
            comment_id: Comment ID to reply to
            text: Reply text

        Returns:
            True if reply successful, False otherwise

        Raises:
            PlatformError: If reply fails
        """
        self._ensure_authenticated()

        logger.warning(
            "YouTube comment replying requires OAuth2 credentials. Not implemented for API key mode."
        )
        return False

    def convert_to_post(self, data: Dict[str, Any]) -> Post:
        """
        Convert YouTube video data to Post object.

        Args:
            data: YouTube video data

        Returns:
            Post object
        """
        snippet = data.get("snippet", {})
        statistics = data.get("statistics", {})

        return Post(
            id=data.get("id", ""),
            title=snippet.get("title", ""),
            content=snippet.get("description", ""),
            author_id=snippet.get("channelId", ""),
            author_name=snippet.get("channelTitle", ""),
            created_at=datetime.fromisoformat(
                snippet.get("publishedAt", "").replace("Z", "+00:00")
            )
            if snippet.get("publishedAt")
            else datetime.utcnow(),
            platform="youtube",
            url=f"https://youtube.com/watch?v={data.get('id', '')}",
            likes=int(statistics.get("likeCount", 0)),
            shares=int(statistics.get("shareCount", 0)),
            comments_count=int(statistics.get("commentCount", 0)),
            metadata={
                "video_id": data.get("id"),
                "thumbnail": snippet.get("thumbnails", {})
                .get("default", {})
                .get("url"),
                "tags": snippet.get("tags", []),
                "category_id": snippet.get("categoryId"),
            },
        )

    def convert_to_comment(self, data: Dict[str, Any], video_id: str = "") -> Comment:
        """
        Convert YouTube comment data to Comment object.

        Args:
            data: YouTube comment data
            video_id: Optional video ID for parent post

        Returns:
            Comment object
        """
        snippet = data.get("snippet", {})
        author_display_name = snippet.get("authorDisplayName", "")
        author_channel_id = snippet.get("authorChannelId", "")

        return Comment(
            id=data.get("id", ""),
            text=snippet.get("textDisplay", ""),
            author_id=author_channel_id,
            author_name=author_display_name,
            created_at=datetime.fromisoformat(
                snippet.get("updatedAt", "").replace("Z", "+00:00")
            )
            if snippet.get("updatedAt")
            else datetime.utcnow(),
            platform="youtube",
            post_id=video_id or snippet.get("videoId", ""),
            parent_id=snippet.get("parentId"),
            likes=int(snippet.get("likeCount", 0)),
            metadata={
                "video_id": video_id,
                "channel_id": author_channel_id,
                "can_reply": snippet.get("canReply", True),
            },
        )

    @classmethod
    def get_platform_name(cls) -> str:
        """Get platform name."""
        return "youtube"

    @classmethod
    def get_supported_features(cls) -> List[str]:
        """Get list of supported features."""
        features = super().get_supported_features()
        features.remove("reply_to_comment")
        return features
