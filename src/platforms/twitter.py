"""
Twitter/X platform integration for Moderation AI.

This module provides a complete implementation for interacting with the Twitter/X API,
including authentication, comment fetching, moderation, and post tracking.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

try:
    import tweepy
except ImportError:
    tweepy = None

from .base import BasePlatform
from ..core.base import Comment, Post, ModerationAction, ModerationResult
from ..utils.rate_limiter import PlatformRateLimiter
from ..utils.auth_manager import AuthManager
from ..utils.error_handler import AuthenticationError, PlatformError, RateLimitError
from ..core.config import get_config


logger = logging.getLogger(__name__)


class TwitterPlatform(BasePlatform):
    """
    Twitter/X platform integration.
    
    Provides complete access to Twitter API v2 for:
    - Fetching tweets and comments (replies)
    - Moderating comments
    - Tracking tweets for new replies
    - Replying to comments
    """

    def __init__(
        self,
        auth_manager: Optional[AuthManager] = None,
        rate_limiter: Optional[PlatformRateLimiter] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Twitter platform.
        
        Args:
            auth_manager: Authentication manager instance
            rate_limiter: Rate limiter instance
            config: Configuration dictionary (Twitter API keys)
        """
        super().__init__(
            platform_name="twitter",
            auth_manager=auth_manager,
            rate_limiter=rate_limiter,
        )
        
        if tweepy is None:
            raise ImportError("tweepy is required for Twitter integration. Install with: pip install tweepy")
        
        self.config = config or {}
        self._api_client: Optional[tweepy.Client] = None
        self._api: Optional[tweepy.API] = None
        self._user_id: Optional[str] = None
        
        if config:
            self.configure(**config)

    def configure(self, **kwargs: Any) -> None:
        """
        Configure Twitter platform.
        
        Args:
            **kwargs: Configuration parameters including:
                - api_key: Twitter API key
                - api_secret: Twitter API secret
                - access_token: Twitter access token
                - access_token_secret: Twitter access token secret
                - bearer_token: Twitter bearer token
                - timeout: Request timeout in seconds
        """
        super().configure(**kwargs)
        
        if "api_key" in kwargs or "consumer_key" in kwargs:
            self._setup_api_client()

    def _setup_api_client(self) -> None:
        """Setup Twitter API client with credentials."""
        app_config = get_config().twitter
        
        api_key = self._config.get("api_key") or app_config.api_key
        api_secret = self._config.get("api_secret") or app_config.api_secret
        access_token = self._config.get("access_token") or app_config.access_token
        access_token_secret = self._config.get("access_token_secret") or app_config.access_token_secret
        bearer_token = self._config.get("bearer_token") or app_config.bearer_token
        timeout = self._config.get("timeout", app_config.timeout)
        
        if not bearer_token and not (api_key and api_secret):
            raise AuthenticationError(
                "Twitter API credentials not provided. "
                "Need either bearer_token or api_key/api_secret pair.",
                platform="twitter",
                details={"credentials": "missing"}
            )
        
        try:
            if bearer_token:
                self._api_client = tweepy.Client(
                    bearer_token=bearer_token,
                    wait_on_rate_limit=True,
                    timeout=timeout,
                )
                logger.info("Twitter API client initialized with bearer token")
            
            if api_key and api_secret and access_token and access_token_secret:
                self._api = tweepy.API(
                    consumer_key=api_key,
                    consumer_secret=api_secret,
                    access_token=access_token,
                    access_token_secret=access_token_secret,
                    wait_on_rate_limit=True,
                    timeout=timeout,
                )
                logger.info("Twitter API v1.1 initialized for user auth")
                
        except Exception as e:
            raise AuthenticationError(
                f"Failed to initialize Twitter API client: {str(e)}",
                platform="twitter",
                details={"error": str(e)}
            )

    def authenticate(self, credentials: Optional[Dict[str, Any]] = None) -> bool:
        """
        Authenticate with Twitter.
        
        Args:
            credentials: Optional credentials dictionary
                - api_key: Twitter API key
                - api_secret: Twitter API secret
                - access_token: Twitter access token
                - access_token_secret: Twitter access token secret
                - bearer_token: Twitter bearer token
        
        Returns:
            True if authenticated, False otherwise
        
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            if credentials:
                self.configure(**credentials)
            
            self._setup_api_client()
            
            if self._api_client:
                self._user_id = str(self._api_client.get_me().data.id)
                logger.info(f"Authenticated as Twitter user ID: {self._user_id}")
            
            self._authenticated = True
            return True
            
        except Exception as e:
            logger.error(f"Twitter authentication failed: {str(e)}")
            raise AuthenticationError(
                f"Failed to authenticate with Twitter: {str(e)}",
                platform="twitter",
                details={"error": str(e)}
            )

    def is_authenticated(self) -> bool:
        """
        Check if platform is authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        if not self._authenticated:
            return False
        
        if self._api_client is None:
            return False
        
        try:
            self._api_client.get_me()
            return True
        except Exception:
            return False

    def fetch_posts(self, query: str, limit: int = 10, **kwargs: Any) -> List[Post]:
        """
        Fetch tweets from Twitter.
        
        Args:
            query: Search query or user handle
            limit: Maximum number of tweets to fetch
            **kwargs: Additional parameters:
                - user_id: Fetch tweets from specific user
                - exclude_replies: Exclude replies from results
        
        Returns:
            List of Post objects
        
        Raises:
            PlatformError: If fetch fails
        """
        self._ensure_authenticated()
        
        try:
            self.rate_limiter.allow_request(self.platform_name)
            
            tweets = []
            
            if query.startswith("@"):
                username = query.lstrip("@")
                user_tweets = self._api_client.get_users_tweets(
                    username=username,
                    max_results=min(limit, 100),
                    tweet_fields=["created_at", "author_id", "public_metrics"],
                    exclude=["retweets", "replies"] if kwargs.get("exclude_replies") else []
                )
                tweets = user_tweets.data or []
            else:
                search_results = self._api_client.search_recent_tweets(
                    query=query,
                    max_results=min(limit, 100),
                    tweet_fields=["created_at", "author_id", "public_metrics"]
                )
                tweets = search_results.data or []
            
            posts = []
            for tweet in tweets[:limit]:
                try:
                    post = self.convert_to_post(tweet)
                    posts.append(post)
                except Exception as e:
                    logger.warning(f"Failed to convert tweet {tweet.id}: {str(e)}")
            
            logger.info(f"Fetched {len(posts)} tweets for query: {query}")
            return posts
            
        except tweepy.RateLimitError as e:
            raise RateLimitError(
                "Twitter rate limit exceeded",
                platform="twitter",
                limit=15,
                reset_in=900,
                details={"error": str(e)}
            )
        except Exception as e:
            raise self._platform_error(
                f"Failed to fetch tweets: {str(e)}",
                details={"query": query, "limit": limit, "error": str(e)}
            )

    def fetch_comments(
        self, post_id: str, limit: int = 100, **kwargs: Any
    ) -> List[Comment]:
        """
        Fetch comments (replies) for a tweet.
        
        Args:
            post_id: Tweet ID
            limit: Maximum number of comments to fetch
            **kwargs: Additional parameters:
                - include_thread: Include full conversation thread
        
        Returns:
            List of Comment objects
        
        Raises:
            PlatformError: If fetch fails
        """
        self._ensure_authenticated()
        
        try:
            self.rate_limiter.allow_request(self.platform_name)
            
            tweet_id = post_id
            
            replies = self._api_client.get_users_mentions(
                max_results=min(limit, 100),
                tweet_fields=["created_at", "author_id", "in_reply_to_user_id", "public_metrics"],
                expansions=["referenced_tweets.id"]
            )
            
            comments = []
            for reply in replies.data:
                if reply.in_reply_to_user_id == self._user_id:
                    try:
                        comment = self.convert_to_comment(reply)
                        comments.append(comment)
                        
                        if len(comments) >= limit:
                            break
                    except Exception as e:
                        logger.warning(f"Failed to convert reply {reply.id}: {str(e)}")
            
            logger.info(f"Fetched {len(comments)} comments for tweet {tweet_id}")
            return comments
            
        except tweepy.RateLimitError as e:
            raise RateLimitError(
                "Twitter rate limit exceeded",
                platform="twitter",
                limit=15,
                reset_in=900,
                details={"error": str(e)}
            )
        except Exception as e:
            raise self._platform_error(
                f"Failed to fetch comments: {str(e)}",
                details={"tweet_id": tweet_id, "limit": limit, "error": str(e)}
            )

    def moderate_comment(
        self, comment_id: str, action: ModerationAction, reason: Optional[str] = None
    ) -> bool:
        """
        Moderate a tweet/reply.
        
        Args:
            comment_id: Tweet ID to moderate
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
            
            if action == ModerationAction.REMOVE:
                self._api.delete_status(comment_id)
                logger.info(f"Removed tweet {comment_id}. Reason: {reason}")
                return True
            
            elif action == ModerationAction.HIDE:
                Twitter doesn't have a native "hide" action, 
                so we log for manual review
                logger.warning(f"Tweet {comment_id} flagged for manual review. Reason: {reason}")
                return True
            
            elif action == ModerationAction.FLAG:
                Twitter doesn't have native flagging from API,
                so we log for manual review
                logger.info(f"Tweet {comment_id} flagged. Reason: {reason}")
                return True
            
            elif action == ModerationAction.APPROVE:
                logger.info(f"Tweet {comment_id} approved - no action taken")
                return True
            
            return False
            
        except tweepy.RateLimitError as e:
            raise RateLimitError(
                "Twitter rate limit exceeded",
                platform="twitter",
                limit=15,
                reset_in=900,
                details={"error": str(e)}
            )
        except Exception as e:
            logger.error(f"Failed to moderate comment {comment_id}: {str(e)}")
            raise self._platform_error(
                f"Failed to moderate tweet: {str(e)}",
                details={"tweet_id": comment_id, "action": action.value, "error": str(e)}
            )

    def track_post(self, post_id: str, enable_tracking: bool = True) -> bool:
        """
        Track a tweet for new comments.
        
        Args:
            post_id: Tweet ID to track
            enable_tracking: Whether to enable or disable tracking
        
        Returns:
            True if tracking updated, False otherwise
        
        Raises:
            PlatformError: If tracking update fails
        """
        self._ensure_authenticated()
        
        try:
            if enable_tracking:
                logger.info(f"Tracking enabled for tweet {post_id}")
                self._config["tracked_tweets"] = self._config.get("tracked_tweets", set())
                self._config["tracked_tweets"].add(post_id)
            else:
                logger.info(f"Tracking disabled for tweet {post_id}")
                if "tracked_tweets" in self._config:
                    self._config["tracked_tweets"].discard(post_id)
            
            return True
            
        except Exception as e:
            raise self._platform_error(
                f"Failed to update tracking: {str(e)}",
                details={"tweet_id": post_id, "enable": enable_tracking, "error": str(e)}
            )

    def get_post(self, post_id: str) -> Optional[Post]:
        """
        Get a specific tweet.
        
        Args:
            post_id: Tweet ID
        
        Returns:
            Post object or None if not found
        
        Raises:
            PlatformError: If get fails
        """
        self._ensure_authenticated()
        
        try:
            tweet = self._api_client.get_tweet(
                tweet_id,
                tweet_fields=["created_at", "author_id", "public_metrics", "text"]
            )
            
            if not tweet.data:
                return None
            
            return self.convert_to_post(tweet.data)
            
        except Exception as e:
            raise self._platform_error(
                f"Failed to get tweet: {str(e)}",
                details={"tweet_id": post_id, "error": str(e)}
            )

    def get_comment(self, comment_id: str) -> Optional[Comment]:
        """
        Get a specific comment (tweet reply).
        
        Args:
            comment_id: Tweet ID
        
        Returns:
            Comment object or None if not found
        
        Raises:
            PlatformError: If get fails
        """
        self._ensure_authenticated()
        
        try:
            tweet = self._api_client.get_tweet(
                comment_id,
                tweet_fields=["created_at", "author_id", "in_reply_to_user_id", "public_metrics", "text"]
            )
            
            if not tweet.data:
                return None
            
            return self.convert_to_comment(tweet.data)
            
        except Exception as e:
            raise self._platform_error(
                f"Failed to get comment: {str(e)}",
                details={"tweet_id": comment_id, "error": str(e)}
            )

    def reply_to_comment(self, comment_id: str, text: str) -> bool:
        """
        Reply to a tweet.
        
        Args:
            comment_id: Tweet ID to reply to
            text: Reply text
        
        Returns:
            True if reply successful, False otherwise
        
        Raises:
            PlatformError: If reply fails
        """
        self._ensure_authenticated()
        
        try:
            self.rate_limiter.allow_request(self.platform_name)
            
            response = self._api_client.create_tweet(
                text=text,
                in_reply_to_tweet_id=comment_id
            )
            
            logger.info(f"Replied to tweet {comment_id} with new tweet {response.data.id}")
            return True
            
        except Exception as e:
            raise self._platform_error(
                f"Failed to reply to tweet: {str(e)}",
                details={"tweet_id": comment_id, "error": str(e)}
            )

    def convert_to_post(self, data: Any) -> Post:
        """
        Convert Twitter tweet data to Post object.
        
        Args:
            data: Twitter tweet data (dict or object)
        
        Returns:
            Post object
        """
        tweet_data = data.data if hasattr(data, 'data') else data
        
            return Post(
                id=str(tweet_data.get("id", "")),
                title=tweet_data.get("text", "")[:100],
                content=tweet_data.get("text", ""),
                author_id=str(tweet_data.get("author_id", "")),
                author_name=f"@{tweet_data.get('author_id', '')}",
                created_at=datetime.fromisoformat(
                    tweet_data.get("created_at", "").replace("Z", "+00:00")
                ) if isinstance(tweet_data.get("created_at"), str) else datetime.utcnow(),
                platform="twitter",
                url=f"https://twitter.com/i/status/{tweet_data.get('id', '')}",
                likes=tweet_data.get("public_metrics", {}).get("like_count", 0),
                shares=tweet_data.get("public_metrics", {}).get("retweet_count", 0),
                comments_count=tweet_data.get("public_metrics", {}).get("reply_count", 0),
                metadata=tweet_data
            )

    def convert_to_comment(self, data: Any) -> Comment:
        """
        Convert Twitter tweet/reply data to Comment object.
        
        Args:
            data: Twitter tweet/reply data (dict or object)
        
        Returns:
            Comment object
        """
        tweet_data = data.data if hasattr(data, 'data') else data
        
        return Comment(
            id=str(tweet_data.get("id", "")),
            text=tweet_data.get("text", ""),
            author_id=str(tweet_data.get("author_id", "")),
            author_name=f"@{tweet_data.get('author_id', '')}",
            created_at=datetime.fromisoformat(
                tweet_data.get("created_at", "").replace("Z", "+00:00")
            ) if isinstance(tweet_data.get("created_at"), str) else datetime.utcnow(),
            platform="twitter",
            post_id=str(tweet_data.get("in_reply_to_user_id", "")),
            likes=tweet_data.get("public_metrics", {}).get("like_count", 0),
            replies_count=tweet_data.get("public_metrics", {}).get("reply_count", 0),
            metadata=tweet_data
        )

    @classmethod
    def get_platform_name(cls) -> str:
        """Get platform name."""
        return "twitter"

    @classmethod
    def get_supported_features(cls) -> List[str]:
        """Get list of supported features."""
        features = super().get_supported_features()
        features.remove("track_post")
        return features
