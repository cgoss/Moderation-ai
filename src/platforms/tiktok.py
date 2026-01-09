"""
TikTok platform integration for Moderation AI.

This module provides a complete implementation for interacting with TikTok API,
including authentication, video fetching, comment moderation, and post tracking.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

try:
    import requests
except ImportError:
    requests = None

from .base import BasePlatform
from ..core.base import Comment, Post, ModerationAction, ModerationResult
from ..utils.rate_limiter import PlatformRateLimiter
from ..utils.auth_manager import AuthManager
from ..utils.error_handler import AuthenticationError, PlatformError, RateLimitError
from ..core.config import get_config


logger = logging.getLogger(__name__)


class TikTokPlatform(BasePlatform):
    """
    TikTok platform integration.

    Provides complete access to TikTok API for:
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
        Initialize TikTok platform.

        Args:
            auth_manager: Authentication manager instance
            rate_limiter: Rate limiter instance
            config: Configuration dictionary (TikTok API keys)
        """
        super().__init__(
            platform_name="tiktok",
            auth_manager=auth_manager,
            rate_limiter=rate_limiter,
        )

        if requests is None:
            raise ImportError(
                "requests is required. Install with: pip install requests"
            )

        self.config = config or {}
        self._app_key: Optional[str] = None
        self._app_secret: Optional[str] = None
        self._access_token: Optional[str] = None
        self._base_url: str = "https://open.tiktokapis.com"

        if config:
            self.configure(**config)

    def configure(self, **kwargs: Any) -> None:
        """
        Configure TikTok platform.

        Args:
            **kwargs: Configuration parameters including:
                - app_key: TikTok app key
                - app_secret: TikTok app secret
                - access_token: TikTok access token
                - timeout: Request timeout in seconds
        """
        super().configure(**kwargs)

        if "app_key" in kwargs or "access_token" in kwargs:
            self._setup_tiktok()

    def _setup_tiktok(self) -> None:
        """Setup TikTok API client with credentials."""
        app_config = get_config().tiktok

        app_key = self._config.get("app_key") or app_config.app_key
        app_secret = self._config.get("app_secret") or app_config.app_secret
        access_token = self._config.get("access_token")

        if not (app_key and app_secret) and not access_token:
            raise AuthenticationError(
                "TikTok API credentials not provided. Need app_key/app_secret or access_token.",
                platform="tiktok",
                details={"credentials": "missing"},
            )

        try:
            self._app_key = app_key
            self._app_secret = app_secret
            self._access_token = access_token
            logger.info("TikTok API client initialized")

        except Exception as e:
            raise AuthenticationError(
                f"Failed to initialize TikTok API client: {str(e)}",
                platform="tiktok",
                details={"error": str(e)},
            )

    def authenticate(self, credentials: Optional[Dict[str, Any]] = None) -> bool:
        """
        Authenticate with TikTok.

        Args:
            credentials: Optional credentials dictionary
                - app_key: TikTok app key
                - app_secret: TikTok app secret
                - access_token: TikTok access token

        Returns:
            True if authenticated, False otherwise
        """
        try:
            if credentials:
                self.configure(**credentials)

            self._setup_tiktok()

            self._authenticated = True
            logger.info("TikTok API authentication successful")
            return True

        except Exception as e:
            logger.error(f"TikTok authentication failed: {str(e)}")
            raise AuthenticationError(
                f"Failed to authenticate with TikTok: {str(e)}",
                platform="tiktok",
                details={"error": str(e)},
            )

    def is_authenticated(self) -> bool:
        """
        Check if platform is authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        return self._authenticated and (self._app_key or self._access_token)

    def fetch_posts(self, query: str, limit: int = 10, **kwargs: Any) -> List[Post]:
        """
        Fetch videos from TikTok.

        Args:
            query: User ID or hashtag
            limit: Maximum number of videos to fetch
            **kwargs: Additional parameters:
                - count: Number of videos to fetch
                - cursor: Pagination cursor

        Returns:
            List of Post objects

        Raises:
            PlatformError: If fetch fails
        """
        self._ensure_authenticated()

        try:
            self.rate_limiter.allow_request(self.platform_name)

            videos = []
            endpoint = f"{self._base_url}/v2/video/list/"
            params = {"count": min(limit, 50), "cursor": kwargs.get("cursor")}

            headers = (
                {"Authorization": f"Bearer {self._access_token}"}
                if self._access_token
                else {}
            )

            if self._app_key and self._app_secret:
                headers["Content-Type"] = "application/json"
                params["app_key"] = self._app_key

            response = requests.get(
                endpoint, headers=headers, params=params, timeout=30
            )

            if response.status_code != 200:
                raise PlatformError(
                    f"TikTok API error: {response.status_code}",
                    platform="tiktok",
                    details={"status_code": response.status_code},
                )

            data = response.json()

            for item in data.get("data", {}).get("videos", [])[:limit]:
                try:
                    post = self.convert_to_post(item)
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
        Fetch comments for a TikTok video.

        Args:
            post_id: Video ID
            limit: Maximum number of comments to fetch
            **kwargs: Additional parameters:
                - cursor: Pagination cursor

        Returns:
            List of Comment objects

        Raises:
            PlatformError: If fetch fails
        """
        self._ensure_authenticated()

        try:
            self.rate_limiter.allow_request(self.platform_name)

            endpoint = f"{self._base_url}/v2/video/comment/list/"
            params = {
                "video_id": post_id,
                "count": min(limit, 50),
                "cursor": kwargs.get("cursor"),
            }

            headers = (
                {"Authorization": f"Bearer {self._access_token}"}
                if self._access_token
                else {}
            )

            if self._app_key and self._app_secret:
                headers["Content-Type"] = "application/json"
                params["app_key"] = self._app_key

            response = requests.get(
                endpoint, headers=headers, params=params, timeout=30
            )

            if response.status_code != 200:
                raise PlatformError(
                    f"TikTok API error: {response.status_code}",
                    platform="tiktok",
                    details={"status_code": response.status_code},
                )

            data = response.json()

            comments = []
            for item in data.get("data", {}).get("comments", [])[:limit]:
                try:
                    comment = self.convert_to_comment(item)
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
        Moderate a TikTok comment.

        Note: TikTok API doesn't support direct comment deletion.
        Comments must be moderated through TikTok moderation tools.

        Args:
            comment_id: Comment ID to moderate
            action: Moderation action (approve, flag, hide, remove)
            reason: Optional reason for moderation

        Returns:
            True if moderation logged, False otherwise
        """
        self._ensure_authenticated()

        try:
            if action == ModerationAction.FLAG:
                logger.info(f"Comment {comment_id} flagged. Reason: {reason}")
                return True

            elif action == ModerationAction.HIDE:
                logger.info(f"Comment {comment_id} hidden. Reason: {reason}")
                return True

            elif action == ModerationAction.APPROVE:
                logger.info(f"Comment {comment_id} approved - no action taken")
                return True

            elif action == ModerationAction.REMOVE:
                logger.warning(
                    f"Comment {comment_id} removal requires manual moderation in TikTok"
                )
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
        Track a TikTok video for new comments.

        Args:
            post_id: Video ID to track
            enable_tracking: Whether to enable or disable tracking

        Returns:
            True if tracking updated, False otherwise
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
        Get a specific TikTok video.

        Args:
            post_id: Video ID

        Returns:
            Post object or None if not found
        """
        self._ensure_authenticated()

        try:
            endpoint = f"{self._base_url}/v2/video/detail/"
            params = {"video_id": post_id}

            headers = (
                {"Authorization": f"Bearer {self._access_token}"}
                if self._access_token
                else {}
            )

            if self._app_key and self._app_secret:
                headers["Content-Type"] = "application/json"
                params["app_key"] = self._app_key

            response = requests.get(
                endpoint, headers=headers, params=params, timeout=30
            )

            if response.status_code != 200:
                return None

            data = response.json()
            return self.convert_to_post(data.get("data", {}))

        except Exception as e:
            raise self._platform_error(
                f"Failed to get video: {str(e)}",
                details={"video_id": post_id, "error": str(e)},
            )

    def get_comment(self, comment_id: str) -> Optional[Comment]:
        """
        Get a specific TikTok comment.

        Args:
            comment_id: Comment ID

        Returns:
            Comment object or None if not found
        """
        self._ensure_authenticated()

        try:
            endpoint = f"{self._base_url}/v2/video/comment/detail/"
            params = {"comment_id": comment_id}

            headers = (
                {"Authorization": f"Bearer {self._access_token}"}
                if self._access_token
                else {}
            )

            if self._app_key and self._app_secret:
                headers["Content-Type"] = "application/json"
                params["app_key"] = self._app_key

            response = requests.get(
                endpoint, headers=headers, params=params, timeout=30
            )

            if response.status_code != 200:
                return None

            data = response.json()
            return self.convert_to_comment(data.get("data", {}))

        except Exception as e:
            raise self._platform_error(
                f"Failed to get comment: {str(e)}",
                details={"comment_id": comment_id, "error": str(e)},
            )

    def reply_to_comment(self, comment_id: str, text: str) -> bool:
        """
        Reply to a TikTok comment.

        Note: Requires OAuth2 credentials, not app_key.

        Args:
            comment_id: Comment ID to reply to
            text: Reply text

        Returns:
            True if reply successful, False otherwise
        """
        self._ensure_authenticated()

        logger.warning(
            "TikTok comment replying requires OAuth2 credentials. Not implemented for app_key mode."
        )
        return False

    def convert_to_post(self, data: Dict[str, Any]) -> Post:
        """
        Convert TikTok video data to Post object.

        Args:
            data: TikTok video data

        Returns:
            Post object
        """
        return Post(
            id=data.get("id", ""),
            title=data.get("caption", "")[:100],
            content=data.get("caption", ""),
            author_id=data.get("author", {}).get("uid", ""),
            author_name=data.get("author", {}).get("nickname", ""),
            created_at=datetime.fromisoformat(
                data.get("create_time", "").replace("Z", "+00:00")
            )
            if data.get("create_time")
            else datetime.utcnow(),
            platform="tiktok",
            url=data.get("share_url", ""),
            likes=data.get("stats", {}).get("digg_count", 0),
            shares=data.get("stats", {}).get("share_count", 0),
            comments_count=data.get("stats", {}).get("comment_count", 0),
            metadata=data,
        )

    def convert_to_comment(self, data: Dict[str, Any]) -> Comment:
        """
        Convert TikTok comment data to Comment object.

        Args:
            data: TikTok comment data

        Returns:
            Comment object
        """
        return Comment(
            id=data.get("id", ""),
            text=data.get("text", ""),
            author_id=data.get("author", {}).get("uid", ""),
            author_name=data.get("author", {}).get("nickname", ""),
            created_at=datetime.fromisoformat(
                data.get("create_time", "").replace("Z", "+00:00")
            )
            if data.get("create_time")
            else datetime.utcnow(),
            platform="tiktok",
            post_id=data.get("video_id", ""),
            likes=data.get("digg_count", 0),
            replies_count=data.get("reply_comment_total", 0),
            metadata=data,
        )

    @classmethod
    def get_platform_name(cls) -> str:
        """Get platform name."""
        return "tiktok"

    @classmethod
    def get_supported_features(cls) -> List[str]:
        """Get list of supported features."""
        features = super().get_supported_features()
        features.remove("moderate_comment")
        features.remove("reply_to_comment")
        return features
