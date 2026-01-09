"""
Base platform class for all platform integrations.

This module provides the abstract base class that all platform
integrations (Twitter, Reddit, YouTube, etc.) must implement.
"""

from typing import Any, Dict, List, Optional, Callable
from abc import ABC, abstractmethod
from datetime import datetime

from ..core.base import Comment, Post, ModerationResult, ModerationAction
from ..utils.rate_limiter import PlatformRateLimiter
from ..utils.auth_manager import AuthManager
from ..utils.error_handler import PlatformError, AuthenticationError


class BasePlatform(ABC):
    """
    Abstract base class for all platform integrations.

    All platform-specific implementations (Twitter, Reddit, YouTube, etc.)
    must inherit from this class and implement required methods.
    """

    def __init__(
        self,
        platform_name: str,
        auth_manager: Optional[AuthManager] = None,
        rate_limiter: Optional[PlatformRateLimiter] = None,
    ):
        """
        Initialize base platform.

        Args:
            platform_name: Name of the platform
            auth_manager: Authentication manager instance
            rate_limiter: Rate limiter instance
        """
        self.platform_name = platform_name
        self.auth_manager = auth_manager or AuthManager()
        self.rate_limiter = rate_limiter or PlatformRateLimiter()

        self._authenticated = False
        self._config: Dict[str, Any] = {}

    @abstractmethod
    def authenticate(self, credentials: Optional[Dict[str, Any]] = None) -> bool:
        """
        Authenticate with the platform.

        Args:
            credentials: Optional credentials dictionary

        Returns:
            True if authenticated, False otherwise

        Raises:
            AuthenticationError: If authentication fails
        """
        pass

    @abstractmethod
    def is_authenticated(self) -> bool:
        """
        Check if platform is authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        pass

    @abstractmethod
    def fetch_posts(self, query: str, limit: int = 10, **kwargs: Any) -> List[Post]:
        """
        Fetch posts from the platform.

        Args:
            query: Search query or post ID
            limit: Maximum number of posts to fetch
            **kwargs: Additional platform-specific parameters

        Returns:
            List of Post objects

        Raises:
            PlatformError: If fetch fails
        """
        pass

    @abstractmethod
    def fetch_comments(
        self, post_id: str, limit: int = 100, **kwargs: Any
    ) -> List[Comment]:
        """
        Fetch comments for a post.

        Args:
            post_id: ID of the post
            limit: Maximum number of comments to fetch
            **kwargs: Additional platform-specific parameters

        Returns:
            List of Comment objects

        Raises:
            PlatformError: If fetch fails
        """
        pass

    @abstractmethod
    def moderate_comment(
        self, comment_id: str, action: ModerationAction, reason: Optional[str] = None
    ) -> bool:
        """
        Moderate a comment.

        Args:
            comment_id: ID of the comment to moderate
            action: Moderation action to take
            reason: Optional reason for moderation

        Returns:
            True if moderation successful, False otherwise

        Raises:
            PlatformError: If moderation fails
        """
        pass

    @abstractmethod
    def track_post(self, post_id: str, enable_tracking: bool = True) -> bool:
        """
        Track a post for new comments.

        Args:
            post_id: ID of the post to track
            enable_tracking: Whether to enable or disable tracking

        Returns:
            True if tracking updated, False otherwise

        Raises:
            PlatformError: If tracking update fails
        """
        pass

    @abstractmethod
    def get_post(self, post_id: str) -> Optional[Post]:
        """
        Get a specific post.

        Args:
            post_id: ID of the post

        Returns:
            Post object or None if not found

        Raises:
            PlatformError: If get fails
        """
        pass

    @abstractmethod
    def get_comment(self, comment_id: str) -> Optional[Comment]:
        """
        Get a specific comment.

        Args:
            comment_id: ID of the comment

        Returns:
            Comment object or None if not found

        Raises:
            PlatformError: If get fails
        """
        pass

    @abstractmethod
    def reply_to_comment(self, comment_id: str, text: str) -> bool:
        """
        Reply to a comment.

        Args:
            comment_id: ID of the comment to reply to
            text: Reply text

        Returns:
            True if reply successful, False otherwise

        Raises:
            PlatformError: If reply fails
        """
        pass

    def moderate_comments(
        self, comments: List[Comment], engine: Any, dry_run: bool = False
    ) -> List[ModerationResult]:
        """
        Moderate multiple comments.

        Args:
            comments: List of comments to moderate
            engine: Moderation engine to use
            dry_run: If True, don't actually moderate

        Returns:
            List of ModerationResult objects
        """
        results = []

        for comment in comments:
            result = engine.moderate(comment)
            results.append(result)

            if not dry_run and result.action != ModerationAction.APPROVE:
                try:
                    self.moderate_comment(
                        comment_id=comment.id,
                        action=result.action,
                        reason=result.reasoning,
                    )
                except Exception as e:
                    result.error = str(e)

        return results

    def fetch_and_moderate(
        self, post_id: str, engine: Any, limit: int = 100, dry_run: bool = False
    ) -> tuple[List[Comment], List[ModerationResult]]:
        """
        Fetch comments and moderate them.

        Args:
            post_id: ID of the post
            engine: Moderation engine to use
            limit: Maximum number of comments to fetch
            dry_run: If True, don't actually moderate

        Returns:
            Tuple of (comments, moderation_results)
        """
        comments = self.fetch_comments(post_id, limit)
        results = self.moderate_comments(comments, engine, dry_run)
        return comments, results

    def configure(self, **kwargs: Any) -> None:
        """
        Configure the platform.

        Args:
            **kwargs: Configuration parameters
        """
        self._config.update(kwargs)

    def get_config(self) -> Dict[str, Any]:
        """
        Get platform configuration.

        Returns:
            Configuration dictionary
        """
        return self._config.copy()

    def reset(self) -> None:
        """Reset platform state."""
        self._authenticated = False
        self._config = {}
        self.rate_limiter.reset(self.platform_name)

    def _ensure_authenticated(self) -> None:
        """Ensure platform is authenticated."""
        if not self.is_authenticated():
            raise AuthenticationError(
                f"Platform {self.platform_name} is not authenticated",
                details={"platform": self.platform_name},
            )

    def _platform_error(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> PlatformError:
        """
        Create a platform error.

        Args:
            message: Error message
            details: Optional error details

        Returns:
            PlatformError instance
        """
        if details is None:
            details = {}
        details["platform"] = self.platform_name
        return PlatformError(message, platform=self.platform_name, details=details)

    def convert_to_post(self, data: Dict[str, Any]) -> Post:
        """
        Convert platform-specific data to Post object.

        Args:
            data: Platform-specific post data

        Returns:
            Post object
        """
        raise NotImplementedError(
            f"convert_to_post not implemented for {self.platform_name}"
        )

    def convert_to_comment(self, data: Dict[str, Any]) -> Comment:
        """
        Convert platform-specific data to Comment object.

        Args:
            data: Platform-specific comment data

        Returns:
            Comment object
        """
        raise NotImplementedError(
            f"convert_to_comment not implemented for {self.platform_name}"
        )

    @classmethod
    def get_platform_name(cls) -> str:
        """
        Get the platform name.

        Returns:
            Platform name
        """
        return cls.__name__.lower().replace("platform", "")

    @classmethod
    def get_supported_features(cls) -> List[str]:
        """
        Get list of supported features.

        Returns:
            List of feature names
        """
        return [
            "fetch_posts",
            "fetch_comments",
            "moderate_comment",
            "track_post",
            "get_post",
            "get_comment",
            "reply_to_comment",
        ]
