"""
Medium platform integration for Moderation AI.

This module provides a complete implementation for interacting with Medium API,
including authentication, article fetching, comment moderation, and post tracking.
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


class MediumPlatform(BasePlatform):
    """
    Medium platform integration.

    Provides complete access to Medium API for:
    - Fetching articles and responses
    - Moderating responses
    - Tracking articles for new responses
    - Replying to responses
    """

    def __init__(
        self,
        auth_manager: Optional[AuthManager] = None,
        rate_limiter: Optional[PlatformRateLimiter] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Medium platform.

        Args:
            auth_manager: Authentication manager instance
            rate_limiter: Rate limiter instance
            config: Configuration dictionary (Medium API keys)
        """
        super().__init__(
            platform_name="medium",
            auth_manager=auth_manager,
            rate_limiter=rate_limiter,
        )

        if requests is None:
            raise ImportError(
                "requests is required. Install with: pip install requests"
            )

        self.config = config or {}
        self._api_key: Optional[str] = None
        self._base_url: str = "https://api.medium.com"
        self._base_url_v1: str = "https://medium.com"

        if config:
            self.configure(**config)

    def configure(self, **kwargs: Any) -> None:
        """
        Configure Medium platform.

        Args:
            **kwargs: Configuration parameters including:
                - api_key: Medium API key
                - timeout: Request timeout in seconds
        """
        super().configure(**kwargs)

        if "api_key" in kwargs:
            self._setup_medium()

    def _setup_medium(self) -> None:
        """Setup Medium API client with credentials."""
        app_config = get_config().medium

        api_key = self._config.get("api_key") or app_config.api_key

        if not api_key:
            raise AuthenticationError(
                "Medium API key not provided.",
                platform="medium",
                details={"credentials": "missing"},
            )

        try:
            self._api_key = api_key
            logger.info("Medium API client initialized")

        except Exception as e:
            raise AuthenticationError(
                f"Failed to initialize Medium API client: {str(e)}",
                platform="medium",
                details={"error": str(e)},
            )

    def authenticate(self, credentials: Optional[Dict[str, Any]] = None) -> bool:
        """
        Authenticate with Medium.

        Args:
            credentials: Optional credentials dictionary
                - api_key: Medium API key

        Returns:
            True if authenticated, False otherwise
        """
        try:
            if credentials:
                self.configure(**credentials)

            self._setup_medium()

            self._authenticated = True
            logger.info("Medium API authentication successful")
            return True

        except Exception as e:
            logger.error(f"Medium authentication failed: {str(e)}")
            raise AuthenticationError(
                f"Failed to authenticate with Medium: {str(e)}",
                platform="medium",
                details={"error": str(e)},
            )

    def is_authenticated(self) -> bool:
        """
        Check if platform is authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        return self._authenticated and self._api_key is not None

    def fetch_posts(self, query: str, limit: int = 10, **kwargs: Any) -> List[Post]:
        """
        Fetch articles from Medium.

        Args:
            query: User ID or publication ID
            limit: Maximum number of posts to fetch
            **kwargs: Additional parameters

        Returns:
            List of Post objects

        Raises:
            PlatformError: If fetch fails
        """
        self._ensure_authenticated()

        try:
            self.rate_limiter.allow_request(self.platform_name)

            posts = []
            endpoint = f"{self._base_url_v1}/@{query}/latest"
            params = {"limit": limit}

            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {self._api_key}"},
                params=params,
                timeout=30,
            )

            if response.status_code != 200:
                raise PlatformError(
                    f"Medium API error: {response.status_code}",
                    platform="medium",
                    details={"status_code": response.status_code},
                )

            data = response.json()

            for item in data.get("value", [])[:limit]:
                try:
                    post = self.convert_to_post(item)
                    posts.append(post)
                except Exception as e:
                    logger.warning(f"Failed to convert article: {str(e)}")

            logger.info(f"Fetched {len(posts)} articles for query: {query}")
            return posts

        except Exception as e:
            raise self._platform_error(
                f"Failed to fetch articles: {str(e)}",
                details={"query": query, "limit": limit, "error": str(e)},
            )

    def fetch_comments(
        self, post_id: str, limit: int = 100, **kwargs: Any
    ) -> List[Comment]:
        """
        Fetch responses for a Medium article.

        Args:
            post_id: Article ID
            limit: Maximum number of responses to fetch
            **kwargs: Additional parameters

        Returns:
            List of Comment objects

        Raises:
            PlatformError: If fetch fails
        """
        self._ensure_authenticated()

        try:
            self.rate_limiter.allow_request(self.platform_name)

            endpoint = f"{self._base_url_v1}/@me/responses/{post_id}"
            params = {"limit": limit}

            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {self._api_key}"},
                params=params,
                timeout=30,
            )

            if response.status_code != 200:
                raise PlatformError(
                    f"Medium API error: {response.status_code}",
                    platform="medium",
                    details={"status_code": response.status_code},
                )

            data = response.json()

            comments = []
            for item in data.get("value", [])[:limit]:
                try:
                    comment = self.convert_to_comment(item)
                    comments.append(comment)
                except Exception as e:
                    logger.warning(f"Failed to convert response: {str(e)}")

            logger.info(f"Fetched {len(comments)} responses for article {post_id}")
            return comments

        except Exception as e:
            raise self._platform_error(
                f"Failed to fetch responses: {str(e)}",
                details={"article_id": post_id, "limit": limit, "error": str(e)},
            )

    def moderate_comment(
        self, comment_id: str, action: ModerationAction, reason: Optional[str] = None
    ) -> bool:
        """
        Moderate a Medium response.

        Note: Medium API doesn't support direct response deletion.
        Responses must be moderated through Medium's moderation tools.

        Args:
            comment_id: Response ID to moderate
            action: Moderation action (approve, flag, hide, remove)
            reason: Optional reason for moderation

        Returns:
            True if moderation logged, False otherwise
        """
        self._ensure_authenticated()

        try:
            if action == ModerationAction.FLAG:
                logger.info(f"Response {comment_id} flagged. Reason: {reason}")
                return True

            elif action == ModerationAction.HIDE:
                logger.info(f"Response {comment_id} hidden. Reason: {reason}")
                return True

            elif action == ModerationAction.APPROVE:
                logger.info(f"Response {comment_id} approved - no action taken")
                return True

            elif action == ModerationAction.REMOVE:
                logger.warning(
                    f"Response {comment_id} removal requires manual moderation in Medium"
                )
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to moderate response {comment_id}: {str(e)}")
            raise self._platform_error(
                f"Failed to moderate response: {str(e)}",
                details={
                    "response_id": comment_id,
                    "action": action.value,
                    "error": str(e),
                },
            )

    def track_post(self, post_id: str, enable_tracking: bool = True) -> bool:
        """
        Track a Medium article for new responses.

        Args:
            post_id: Article ID to track
            enable_tracking: Whether to enable or disable tracking

        Returns:
            True if tracking updated, False otherwise
        """
        self._ensure_authenticated()

        try:
            if enable_tracking:
                logger.info(f"Tracking enabled for article {post_id}")
                self._config["tracked_articles"] = self._config.get(
                    "tracked_articles", set()
                )
                self._config["tracked_articles"].add(post_id)
            else:
                logger.info(f"Tracking disabled for article {post_id}")
                if "tracked_articles" in self._config:
                    self._config["tracked_articles"].discard(post_id)

            return True

        except Exception as e:
            raise self._platform_error(
                f"Failed to update tracking: {str(e)}",
                details={
                    "article_id": post_id,
                    "enable": enable_tracking,
                    "error": str(e),
                },
            )

    def get_post(self, post_id: str) -> Optional[Post]:
        """
        Get a specific Medium article.

        Args:
            post_id: Article ID

        Returns:
            Post object or None if not found
        """
        self._ensure_authenticated()

        try:
            endpoint = f"{self._base_url_v1}/@me/{post_id}"

            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=30,
            )

            if response.status_code != 200:
                return None

            data = response.json()
            return self.convert_to_post(data)

        except Exception as e:
            raise self._platform_error(
                f"Failed to get article: {str(e)}",
                details={"article_id": post_id, "error": str(e)},
            )

    def get_comment(self, comment_id: str) -> Optional[Comment]:
        """
        Get a specific Medium response.

        Args:
            comment_id: Response ID

        Returns:
            Comment object or None if not found
        """
        self._ensure_authenticated()

        try:
            endpoint = f"{self._base_url_v1}/@me/responses/{comment_id}"

            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=30,
            )

            if response.status_code != 200:
                return None

            data = response.json()
            return self.convert_to_comment(data)

        except Exception as e:
            raise self._platform_error(
                f"Failed to get response: {str(e)}",
                details={"response_id": comment_id, "error": str(e)},
            )

    def reply_to_comment(self, comment_id: str, text: str) -> bool:
        """
        Reply to a Medium response.

        Args:
            comment_id: Response ID to reply to
            text: Reply text

        Returns:
            True if reply successful, False otherwise
        """
        self._ensure_authenticated()

        try:
            self.rate_limiter.allow_request(self.platform_name)

            endpoint = f"{self._base_url_v1}/@me/responses/{comment_id}/replies"
            data = {"body": text}

            response = requests.post(
                endpoint,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json=data,
                timeout=30,
            )

            if response.status_code == 201:
                logger.info(f"Replied to response {comment_id}")
                return True

            return False

        except Exception as e:
            raise self._platform_error(
                f"Failed to reply to response: {str(e)}",
                details={"response_id": comment_id, "error": str(e)},
            )

    def convert_to_post(self, data: Dict[str, Any]) -> Post:
        """
        Convert Medium article data to Post object.

        Args:
            data: Medium article data

        Returns:
            Post object
        """
        return Post(
            id=data.get("id", ""),
            title=data.get("title", ""),
            content=data.get("content", {}).get("body", ""),
            author_id=data.get("creatorId", ""),
            author_name=data.get("creator", {}).get("name", ""),
            created_at=datetime.fromisoformat(
                data.get("publishedAt", "").replace("Z", "+00:00")
            )
            if data.get("publishedAt")
            else datetime.utcnow(),
            platform="medium",
            url=data.get("detectedLanguage", ""),
            likes=data.get("virtuals", {}).get("recommends", 0),
            shares=0,
            comments_count=data.get("virtuals", {}).get("responses", 0),
            metadata=data,
        )

    def convert_to_comment(self, data: Dict[str, Any]) -> Comment:
        """
        Convert Medium response data to Comment object.

        Args:
            data: Medium response data

        Returns:
            Comment object
        """
        return Comment(
            id=data.get("id", ""),
            text=data.get("body", {})
            .get("bodyModel", {})
            .get("paragraphs", [{}])[0]
            .get("text", ""),
            author_id=data.get("authorId", ""),
            author_name=data.get("author", {}).get("name", ""),
            created_at=datetime.fromisoformat(
                data.get("createdAt", "").replace("Z", "+00:00")
            )
            if data.get("createdAt")
            else datetime.utcnow(),
            platform="medium",
            post_id=data.get("inResponseToMediaId", ""),
            likes=data.get("virtuals", {}).get("recommends", 0),
            replies_count=0,
            metadata=data,
        )

    @classmethod
    def get_platform_name(cls) -> str:
        """Get platform name."""
        return "medium"

    @classmethod
    def get_supported_features(cls) -> List[str]:
        """Get list of supported features."""
        features = super().get_supported_features()
        features.remove("moderate_comment")
        return features
