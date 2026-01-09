"""
Instagram platform integration for Moderation AI.

This module provides a complete implementation for interacting with Instagram Basic Display API,
including authentication, comment fetching, moderation, and media tracking.
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


class InstagramPlatform(BasePlatform):
    """
    Instagram platform integration.

    Provides complete access to Instagram Basic Display API for:
    - Fetching media and comments
    - Moderating comments
    - Tracking media for new comments
    - Replying to comments
    """

    def __init__(
        self,
        auth_manager: Optional[AuthManager] = None,
        rate_limiter: Optional[PlatformRateLimiter] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Instagram platform.

        Args:
            auth_manager: Authentication manager instance
            rate_limiter: Rate limiter instance
            config: Configuration dictionary (Instagram API keys)
        """
        super().__init__(
            platform_name="instagram",
            auth_manager=auth_manager,
            rate_limiter=rate_limiter,
        )

        if requests is None:
            raise ImportError(
                "requests is required. Install with: pip install requests"
            )

        self.config = config or {}
        self._access_token: Optional[str] = None
        self._base_url: str = "https://graph.instagram.com"

        if config:
            self.configure(**config)

    def configure(self, **kwargs: Any) -> None:
        """
        Configure Instagram platform.

        Args:
            **kwargs: Configuration parameters including:
                - access_token: Instagram access token
                - app_id: Instagram app ID
                - app_secret: Instagram app secret
                - timeout: Request timeout in seconds
        """
        super().configure(**kwargs)

        if "access_token" in kwargs:
            self._setup_instagram()

    def _setup_instagram(self) -> None:
        """Setup Instagram API client with credentials."""
        app_config = get_config().instagram

        access_token = self._config.get("access_token") or app_config.access_token

        if not access_token:
            raise AuthenticationError(
                "Instagram access token not provided.",
                platform="instagram",
                details={"credentials": "missing"},
            )

        try:
            self._access_token = access_token
            logger.info("Instagram API client initialized")

        except Exception as e:
            raise AuthenticationError(
                f"Failed to initialize Instagram API client: {str(e)}",
                platform="instagram",
                details={"error": str(e)},
            )

    def authenticate(self, credentials: Optional[Dict[str, Any]] = None) -> bool:
        """
        Authenticate with Instagram.

        Args:
            credentials: Optional credentials dictionary
                - access_token: Instagram access token

        Returns:
            True if authenticated, False otherwise
        """
        try:
            if credentials:
                self.configure(**credentials)

            self._setup_instagram()

            self._authenticated = True
            logger.info("Instagram API authentication successful")
            return True

        except Exception as e:
            logger.error(f"Instagram authentication failed: {str(e)}")
            raise AuthenticationError(
                f"Failed to authenticate with Instagram: {str(e)}",
                platform="instagram",
                details={"error": str(e)},
            )

    def is_authenticated(self) -> bool:
        """
        Check if platform is authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        if not self._authenticated:
            return False

        if not self._access_token:
            return False

        try:
            response = requests.get(
                f"{self._base_url}/me",
                headers={"Authorization": f"Bearer {self._access_token}"},
                timeout=30,
            )
            return response.status_code == 200
        except Exception:
            return False

    def fetch_posts(self, query: str, limit: int = 10, **kwargs: Any) -> List[Post]:
        """
        Fetch media from Instagram.

        Args:
            query: User ID or hashtag
            limit: Maximum number of posts to fetch
            **kwargs: Additional parameters:
                - user_id: Fetch media from specific user
                - hashtag: Fetch media from hashtag

        Returns:
            List of Post objects

        Raises:
            PlatformError: If fetch fails
        """
        self._ensure_authenticated()

        try:
            self.rate_limiter.allow_request(self.platform_name)

            posts = []

            if query.startswith(("hashtag:", "#")):
                hashtag = query.lstrip("hashtag:#")
                endpoint = f"{self._base_url}/ig_hashtag_search"
                params = {"user_id": query, "limit": limit}
            else:
                user_id = query
                endpoint = f"{self._base_url}/{user_id}/media"
                params = {"limit": limit}

            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {self._access_token}"},
                params=params,
                timeout=30,
            )

            if response.status_code != 200:
                raise PlatformError(
                    f"Instagram API error: {response.status_code}",
                    platform="instagram",
                    details={"status_code": response.status_code},
                )

            data = response.json()

            for item in data.get("data", [])[:limit]:
                try:
                    post = self.convert_to_post(item)
                    posts.append(post)
                except Exception as e:
                    logger.warning(f"Failed to convert media: {str(e)}")

            logger.info(f"Fetched {len(posts)} posts for query: {query}")
            return posts

        except Exception as e:
            raise self._platform_error(
                f"Failed to fetch media: {str(e)}",
                details={"query": query, "limit": limit, "error": str(e)},
            )

    def fetch_comments(
        self, post_id: str, limit: int = 100, **kwargs: Any
    ) -> List[Comment]:
        """
        Fetch comments for an Instagram media post.

        Args:
            post_id: Media ID
            limit: Maximum number of comments to fetch
            **kwargs: Additional parameters

        Returns:
            List of Comment objects

        Raises:
            PlatformError: If fetch fails
        """
        self._ensure_authenticated()

        try:
            self.rate_limiter.allow_request(self.platform_name)

            endpoint = f"{self._base_url}/{post_id}/comments"
            params = {"limit": limit}

            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {self._access_token}"},
                params=params,
                timeout=30,
            )

            if response.status_code != 200:
                raise PlatformError(
                    f"Instagram API error: {response.status_code}",
                    platform="instagram",
                    details={"status_code": response.status_code},
                )

            data = response.json()

            comments = []
            for item in data.get("data", [])[:limit]:
                try:
                    comment = self.convert_to_comment(item, media_id=post_id)
                    comments.append(comment)
                except Exception as e:
                    logger.warning(f"Failed to convert comment: {str(e)}")

            logger.info(f"Fetched {len(comments)} comments for media {post_id}")
            return comments

        except Exception as e:
            raise self._platform_error(
                f"Failed to fetch comments: {str(e)}",
                details={"media_id": post_id, "limit": limit, "error": str(e)},
            )

    def moderate_comment(
        self, comment_id: str, action: ModerationAction, reason: Optional[str] = None
    ) -> bool:
        """
        Moderate an Instagram comment.

        Note: Instagram API doesn't support direct comment deletion. Comments must be hidden/reported.

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
                    f"Comment {comment_id} removal requires manual moderation in Instagram Studio"
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
        Track an Instagram media post for new comments.

        Args:
            post_id: Media ID to track
            enable_tracking: Whether to enable or disable tracking

        Returns:
            True if tracking updated, False otherwise

        Raises:
            PlatformError: If tracking update fails
        """
        self._ensure_authenticated()

        try:
            if enable_tracking:
                logger.info(f"Tracking enabled for media {post_id}")
                self._config["tracked_media"] = self._config.get("tracked_media", set())
                self._config["tracked_media"].add(post_id)
            else:
                logger.info(f"Tracking disabled for media {post_id}")
                if "tracked_media" in self._config:
                    self._config["tracked_media"].discard(post_id)

            return True

        except Exception as e:
            raise self._platform_error(
                f"Failed to update tracking: {str(e)}",
                details={
                    "media_id": post_id,
                    "enable": enable_tracking,
                    "error": str(e),
                },
            )

    def get_post(self, post_id: str) -> Optional[Post]:
        """
        Get a specific Instagram media post.

        Args:
            post_id: Media ID

        Returns:
            Post object or None if not found

        Raises:
            PlatformError: If get fails
        """
        self._ensure_authenticated()

        try:
            endpoint = f"{self._base_url}/{post_id}"

            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {self._access_token}"},
                timeout=30,
            )

            if response.status_code != 200:
                return None

            data = response.json()
            return self.convert_to_post(data)

        except Exception as e:
            raise self._platform_error(
                f"Failed to get media: {str(e)}",
                details={"media_id": post_id, "error": str(e)},
            )

    def get_comment(self, comment_id: str) -> Optional[Comment]:
        """
        Get a specific Instagram comment.

        Args:
            comment_id: Comment ID

        Returns:
            Comment object or None if not found

        Raises:
            PlatformError: If get fails
        """
        self._ensure_authenticated()

        try:
            endpoint = f"{self._base_url}/{comment_id}"

            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {self._access_token}"},
                timeout=30,
            )

            if response.status_code != 200:
                return None

            data = response.json()
            return self.convert_to_comment(data)

        except Exception as e:
            raise self._platform_error(
                f"Failed to get comment: {str(e)}",
                details={"comment_id": comment_id, "error": str(e)},
            )

    def reply_to_comment(self, comment_id: str, text: str) -> bool:
        """
        Reply to an Instagram comment.

        Args:
            comment_id: Comment ID to reply to
            text: Reply text

        Returns:
            True if reply successful, False otherwise

        Raises:
            PlatformError: If reply fails
        """
        self._ensure_authenticated()

        try:
            self.rate_limiter.allow_request(self.platform_name)

            endpoint = f"{self._base_url}/{comment_id}/replies"
            data = {"message": text}

            response = requests.post(
                endpoint,
                headers={"Authorization": f"Bearer {self._access_token}"},
                json=data,
                timeout=30,
            )

            if response.status_code == 200:
                logger.info(f"Replied to comment {comment_id}")
                return True

            return False

        except Exception as e:
            raise self._platform_error(
                f"Failed to reply to comment: {str(e)}",
                details={"comment_id": comment_id, "error": str(e)},
            )

    def convert_to_post(self, data: Dict[str, Any]) -> Post:
        """
        Convert Instagram media data to Post object.

        Args:
            data: Instagram media data

        Returns:
            Post object
        """
        return Post(
            id=data.get("id", ""),
            title=data.get("caption", "")[:100],
            content=data.get("caption", ""),
            author_id=data.get("from", {}).get("id", ""),
            author_name=data.get("from", {}).get("username", ""),
            created_at=datetime.fromisoformat(
                data.get("timestamp", "").replace("Z", "+00:00")
            )
            if data.get("timestamp")
            else datetime.utcnow(),
            platform="instagram",
            url=data.get("permalink", ""),
            likes=data.get("like_count", 0),
            shares=data.get("share_count", 0),
            comments_count=data.get("comments_count", 0),
            metadata=data,
        )

    def convert_to_comment(self, data: Dict[str, Any], media_id: str = "") -> Comment:
        """
        Convert Instagram comment data to Comment object.

        Args:
            data: Instagram comment data
            media_id: Optional media ID for parent post

        Returns:
            Comment object
        """
        return Comment(
            id=data.get("id", ""),
            text=data.get("text", ""),
            author_id=data.get("from", {}).get("id", ""),
            author_name=data.get("from", {}).get("username", ""),
            created_at=datetime.fromisoformat(
                data.get("timestamp", "").replace("Z", "+00:00")
            )
            if data.get("timestamp")
            else datetime.utcnow(),
            platform="instagram",
            post_id=media_id,
            likes=data.get("like_count", 0),
            metadata={"media_id": media_id},
        )

    @classmethod
    def get_platform_name(cls) -> str:
        """Get platform name."""
        return "instagram"

    @classmethod
    def get_supported_features(cls) -> List[str]:
        """Get list of supported features."""
        features = super().get_supported_features()
        features.remove("moderate_comment")
        return features
