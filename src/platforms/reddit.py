"""
Reddit platform integration for Moderation AI.

This module provides a complete implementation for interacting with Reddit API,
including authentication, comment fetching, moderation, and post tracking.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

try:
    import praw
except ImportError:
    praw = None

from .base import BasePlatform
from ..core.base import Comment, Post, ModerationAction, ModerationResult
from ..utils.rate_limiter import PlatformRateLimiter
from ..utils.auth_manager import AuthManager
from ..utils.error_handler import AuthenticationError, PlatformError, RateLimitError
from ..core.config import get_config


logger = logging.getLogger(__name__)


class RedditPlatform(BasePlatform):
    """
    Reddit platform integration.

    Provides complete access to Reddit API for:
    - Fetching posts and comments
    - Moderating comments
    - Tracking posts for new comments
    - Replying to comments
    """

    def __init__(
        self,
        auth_manager: Optional[AuthManager] = None,
        rate_limiter: Optional[PlatformRateLimiter] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Reddit platform.

        Args:
            auth_manager: Authentication manager instance
            rate_limiter: Rate limiter instance
            config: Configuration dictionary (Reddit API keys)
        """
        super().__init__(
            platform_name="reddit",
            auth_manager=auth_manager,
            rate_limiter=rate_limiter,
        )

        if praw is None:
            raise ImportError(
                "praw is required for Reddit integration. Install with: pip install praw"
            )

        self.config = config or {}
        self._reddit: Optional[praw.Reddit] = None
        self._subreddit: Optional[praw.models.Subreddit] = None

        if config:
            self.configure(**config)

    def configure(self, **kwargs: Any) -> None:
        """
        Configure Reddit platform.

        Args:
            **kwargs: Configuration parameters including:
                - client_id: Reddit client ID
                - client_secret: Reddit client secret
                - username: Reddit username
                - password: Reddit password
                - user_agent: Custom user agent string
                - subreddit: Subreddit to work with
        """
        super().configure(**kwargs)

        if "client_id" in kwargs or "client_secret" in kwargs:
            self._setup_reddit()

    def _setup_reddit(self) -> None:
        """Setup Reddit API instance with credentials."""
        app_config = get_config().reddit

        client_id = self._config.get("client_id") or app_config.client_id
        client_secret = self._config.get("client_secret") or app_config.client_secret
        username = self._config.get("username") or app_config.username
        password = self._config.get("password") or app_config.password
        user_agent = self._config.get("user_agent") or app_config.user_agent

        if not client_id or not client_secret:
            raise AuthenticationError(
                "Reddit API credentials not provided. Need client_id and client_secret.",
                platform="reddit",
                details={"credentials": "missing"},
            )

        try:
            self._reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password,
                user_agent=user_agent,
                ratelimit_seconds=600,
                timeout=app_config.timeout,
            )

            if username and password:
                self._reddit.user.me()
                logger.info(f"Authenticated as Reddit user: {username}")
            else:
                logger.info("Reddit API initialized (read-only mode)")

        except Exception as e:
            raise AuthenticationError(
                f"Failed to initialize Reddit API: {str(e)}",
                platform="reddit",
                details={"error": str(e)},
            )

    def authenticate(self, credentials: Optional[Dict[str, Any]] = None) -> bool:
        """
        Authenticate with Reddit.

        Args:
            credentials: Optional credentials dictionary
                - client_id: Reddit client ID
                - client_secret: Reddit client secret
                - username: Reddit username
                - password: Reddit password
                - user_agent: User agent string

        Returns:
            True if authenticated, False otherwise

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            if credentials:
                self.configure(**credentials)

            self._setup_reddit()

            self._authenticated = True
            logger.info("Successfully authenticated with Reddit")
            return True

        except Exception as e:
            logger.error(f"Reddit authentication failed: {str(e)}")
            raise AuthenticationError(
                f"Failed to authenticate with Reddit: {str(e)}",
                platform="reddit",
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

        if self._reddit is None:
            return False

        try:
            self._reddit.user.me()
            return True
        except Exception:
            return False

    def fetch_posts(self, query: str, limit: int = 10, **kwargs: Any) -> List[Post]:
        """
        Fetch posts from Reddit.

        Args:
            query: Subreddit name or search query
            limit: Maximum number of posts to fetch
            **kwargs: Additional parameters:
                - sort: Sort method (hot, new, top, controversial)
                - time_filter: Time filter (hour, day, week, month, year, all)

        Returns:
            List of Post objects

        Raises:
            PlatformError: If fetch fails
        """
        self._ensure_authenticated()

        try:
            self.rate_limiter.allow_request(self.platform_name)

            posts = []
            sort_method = kwargs.get("sort", "hot")
            time_filter = kwargs.get("time_filter", "all")

            if query.startswith("r/"):
                subreddit_name = query[2:]
                subreddit = self._reddit.subreddit(subreddit_name)

                if sort_method == "hot":
                    submissions = subreddit.hot(limit=limit)
                elif sort_method == "new":
                    submissions = subreddit.new(limit=limit)
                elif sort_method == "top":
                    submissions = subreddit.top(time_filter=time_filter, limit=limit)
                elif sort_method == "controversial":
                    submissions = subreddit.controversial(
                        time_filter=time_filter, limit=limit
                    )
                else:
                    submissions = subreddit.hot(limit=limit)
            else:
                subreddit = self._reddit.subreddit("all")
                submissions = subreddit.search(
                    query, sort=sort_method, time_filter=time_filter, limit=limit
                )

            for submission in submissions:
                try:
                    post = self.convert_to_post(submission)
                    posts.append(post)
                except Exception as e:
                    logger.warning(
                        f"Failed to convert submission {submission.id}: {str(e)}"
                    )

            logger.info(f"Fetched {len(posts)} posts for query: {query}")
            return posts

        except praw.exceptions.RateLimit as e:
            raise RateLimitError(
                "Reddit rate limit exceeded",
                platform="reddit",
                limit=60,
                reset_in=600,
                details={"error": str(e)},
            )
        except Exception as e:
            raise self._platform_error(
                f"Failed to fetch posts: {str(e)}",
                details={"query": query, "limit": limit, "error": str(e)},
            )

    def fetch_comments(
        self, post_id: str, limit: int = 100, **kwargs: Any
    ) -> List[Comment]:
        """
        Fetch comments for a Reddit post.

        Args:
            post_id: Post ID
            limit: Maximum number of comments to fetch
            **kwargs: Additional parameters:
                - sort: Comment sort order (best, top, new, controversial)

        Returns:
            List of Comment objects

        Raises:
            PlatformError: If fetch fails
        """
        self._ensure_authenticated()

        try:
            self.rate_limiter.allow_request(self.platform_name)

            submission = self._reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)

            sort_method = kwargs.get("sort", "best")

            if sort_method == "top":
                comments_list = submission.comments.list()
            elif sort_method == "new":
                comments_list = submission.comments.list()
            elif sort_method == "controversial":
                comments_list = submission.comments.list()
            else:
                comments_list = submission.comments.list()

            def extract_replies(comment_list, comments, remaining):
                for comment in comment_list:
                    if isinstance(comment, praw.models.Comment):
                        comments.append(self.convert_to_comment(comment))
                        remaining -= 1
                        if remaining <= 0:
                            return
                        if hasattr(comment, "replies") and comment.replies:
                            extract_replies(comment.replies, comments, remaining)

            comments = []
            extract_replies(comments_list[:limit], comments, limit)

            logger.info(f"Fetched {len(comments)} comments for post {post_id}")
            return comments

        except praw.exceptions.RateLimit as e:
            raise RateLimitError(
                "Reddit rate limit exceeded",
                platform="reddit",
                limit=60,
                reset_in=600,
                details={"error": str(e)},
            )
        except Exception as e:
            raise self._platform_error(
                f"Failed to fetch comments: {str(e)}",
                details={"post_id": post_id, "limit": limit, "error": str(e)},
            )

    def moderate_comment(
        self, comment_id: str, action: ModerationAction, reason: Optional[str] = None
    ) -> bool:
        """
        Moderate a Reddit comment.

        Args:
            comment_id: Comment ID to moderate
            action: Moderation action (approve, flag, hide, remove)
            reason: Optional reason for moderation

        Returns:
            True if moderation successful, False otherwise

        Raises:
            PlatformError: If moderation fails
        """
        self._ensure_authenticated()

        try:
            self.rate_limiter.allow_request(self.platform_name)

            comment = self._reddit.comment(id=comment_id)

            if action == ModerationAction.REMOVE:
                comment.mod.remove(mod_note=reason)
                logger.info(f"Removed comment {comment_id}. Reason: {reason}")
                return True

            elif action == ModerationAction.FLAG:
                comment.mod.report(reason)
                logger.info(f"Reported comment {comment_id}. Reason: {reason}")
                return True

            elif action == ModerationAction.APPROVE:
                comment.mod.approve()
                logger.info(f"Approved comment {comment_id}")
                return True

            elif action == ModerationAction.HIDE:
                comment.mod.remove(spam=False)
                logger.info(f"Hid comment {comment_id}. Reason: {reason}")
                return True

            return False

        except praw.exceptions.RateLimit as e:
            raise RateLimitError(
                "Reddit rate limit exceeded",
                platform="reddit",
                limit=60,
                reset_in=600,
                details={"error": str(e)},
            )
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
        Track a Reddit post for new comments.

        Args:
            post_id: Post ID to track
            enable_tracking: Whether to enable or disable tracking

        Returns:
            True if tracking updated, False otherwise

        Raises:
            PlatformError: If tracking update fails
        """
        self._ensure_authenticated()

        try:
            if enable_tracking:
                logger.info(f"Tracking enabled for post {post_id}")
                self._config["tracked_posts"] = self._config.get("tracked_posts", set())
                self._config["tracked_posts"].add(post_id)
            else:
                logger.info(f"Tracking disabled for post {post_id}")
                if "tracked_posts" in self._config:
                    self._config["tracked_posts"].discard(post_id)

            return True

        except Exception as e:
            raise self._platform_error(
                f"Failed to update tracking: {str(e)}",
                details={
                    "post_id": post_id,
                    "enable": enable_tracking,
                    "error": str(e),
                },
            )

    def get_post(self, post_id: str) -> Optional[Post]:
        """
        Get a specific Reddit post.

        Args:
            post_id: Post ID

        Returns:
            Post object or None if not found

        Raises:
            PlatformError: If get fails
        """
        self._ensure_authenticated()

        try:
            submission = self._reddit.submission(id=post_id)

            if not submission:
                return None

            return self.convert_to_post(submission)

        except Exception as e:
            raise self._platform_error(
                f"Failed to get post: {str(e)}",
                details={"post_id": post_id, "error": str(e)},
            )

    def get_comment(self, comment_id: str) -> Optional[Comment]:
        """
        Get a specific Reddit comment.

        Args:
            comment_id: Comment ID

        Returns:
            Comment object or None if not found

        Raises:
            PlatformError: If get fails
        """
        self._ensure_authenticated()

        try:
            comment = self._reddit.comment(id=comment_id)

            if not comment or comment.id is None:
                return None

            return self.convert_to_comment(comment)

        except Exception as e:
            raise self._platform_error(
                f"Failed to get comment: {str(e)}",
                details={"comment_id": comment_id, "error": str(e)},
            )

    def reply_to_comment(self, comment_id: str, text: str) -> bool:
        """
        Reply to a Reddit comment.

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

            parent_comment = self._reddit.comment(id=comment_id)
            reply = parent_comment.reply(text)

            logger.info(f"Replied to comment {comment_id} with reply {reply.id}")
            return True

        except Exception as e:
            raise self._platform_error(
                f"Failed to reply to comment: {str(e)}",
                details={"comment_id": comment_id, "error": str(e)},
            )

    def convert_to_post(self, data: Any) -> Post:
        """
        Convert Reddit submission data to Post object.

        Args:
            data: Reddit submission object

        Returns:
            Post object
        """
        return Post(
            id=str(data.id),
            title=data.title,
            content=data.selftext if hasattr(data, "selftext") else "",
            author_id=str(data.author.id) if data.author else "",
            author_name=str(data.author.name) if data.author else "[deleted]",
            created_at=datetime.fromtimestamp(data.created_utc),
            platform="reddit",
            url=f"https://reddit.com{data.permalink}"
            if hasattr(data, "permalink")
            else "",
            likes=data.score if hasattr(data, "score") else 0,
            shares=data.num_crossposts if hasattr(data, "num_crossposts") else 0,
            comments_count=data.num_comments if hasattr(data, "num_comments") else 0,
            metadata={
                "subreddit": str(data.subreddit) if data.subreddit else None,
                "is_self": data.is_self if hasattr(data, "is_self") else False,
                "url": data.url if hasattr(data, "url") else None,
            },
        )

    def convert_to_comment(self, data: Any) -> Comment:
        """
        Convert Reddit comment data to Comment object.

        Args:
            data: Reddit comment object

        Returns:
            Comment object
        """
        return Comment(
            id=str(data.id),
            text=data.body if hasattr(data, "body") else "",
            author_id=str(data.author.id) if data.author else "",
            author_name=str(data.author.name) if data.author else "[deleted]",
            created_at=datetime.fromtimestamp(data.created_utc),
            platform="reddit",
            post_id=str(data.submission.id) if hasattr(data.submission, "id") else "",
            parent_id=str(data.parent_id) if hasattr(data, "parent_id") else None,
            likes=data.score if hasattr(data, "score") else 0,
            replies_count=len(data.replies) if hasattr(data, "replies") else 0,
            metadata={
                "subreddit": str(data.subreddit) if data.subreddit else None,
                "distinguished": data.distinguished
                if hasattr(data, "distinguished")
                else None,
            },
        )

    @classmethod
    def get_platform_name(cls) -> str:
        """Get platform name."""
        return "reddit"

    @classmethod
    def get_supported_features(cls) -> List[str]:
        """Get list of supported features."""
        return [
            "fetch_posts",
            "fetch_comments",
            "moderate_comment",
            "track_post",
            "get_post",
            "get_comment",
            "reply_to_comment",
        ]
