"""
Rate limiting utilities for API requests.

This module provides rate limiting functionality to prevent exceeding
API rate limits for various social media platforms.
"""

from typing import Optional, Dict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import time
import threading

from ..core.config import get_config
from .error_handler import RateLimitError


class RateLimiter:
    """
    Token bucket rate limiter.

    Implements the token bucket algorithm for rate limiting requests
    across multiple platforms and endpoints.
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10,
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute
            requests_per_hour: Maximum requests per hour
            burst_size: Maximum burst size
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size

        self._tokens_minute: float = float(burst_size)
        self._tokens_hour: float = float(burst_size)
        self._last_update: datetime = datetime.utcnow()

        self._lock = threading.Lock()

    def acquire(self, tokens: int = 1) -> bool:
        """
        Acquire tokens from the bucket.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            True if tokens acquired, False otherwise
        """
        with self._lock:
            self._refill()

            if self._tokens_minute >= tokens and self._tokens_hour >= tokens:
                self._tokens_minute -= tokens
                self._tokens_hour -= tokens
                return True

            return False

    def wait_for_token(self, tokens: int = 1) -> None:
        """
        Wait until tokens are available.

        Args:
            tokens: Number of tokens to wait for

        Raises:
            RateLimitError: If wait time exceeds threshold
        """
        max_wait_time = 60.0  # Maximum wait time in seconds
        start_time = time.time()

        while not self.acquire(tokens):
            elapsed = time.time() - start_time
            if elapsed > max_wait_time:
                raise RateLimitError(
                    f"Rate limit exceeded, waited {elapsed:.2f}s", retry_after=30
                )

            time.sleep(0.1)

    def get_available_tokens(self) -> tuple[int, int]:
        """
        Get available tokens.

        Returns:
            Tuple of (minute_tokens, hour_tokens)
        """
        with self._lock:
            self._refill()
            return int(self._tokens_minute), int(self._tokens_hour)

    def reset(self) -> None:
        """Reset the rate limiter."""
        with self._lock:
            self._tokens_minute = float(self.burst_size)
            self._tokens_hour = float(self.burst_size)
            self._last_update = datetime.utcnow()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = datetime.utcnow()
        elapsed = now - self._last_update

        if elapsed.total_seconds() <= 0:
            return

        # Refill minute bucket
        minute_elapsed_seconds = elapsed.total_seconds()
        minute_tokens_to_add = (
            self.requests_per_minute * minute_elapsed_seconds
        ) / 60.0
        self._tokens_minute = min(
            self._tokens_minute + minute_tokens_to_add, float(self.burst_size)
        )

        # Refill hour bucket
        hour_elapsed_seconds = elapsed.total_seconds()
        hour_tokens_to_add = (self.requests_per_hour * hour_elapsed_seconds) / 3600.0
        self._tokens_hour = min(
            self._tokens_hour + hour_tokens_to_add, float(self.burst_size)
        )

        self._last_update = now


class PlatformRateLimiter:
    """
    Manages rate limiting for multiple platforms.

    Provides platform-specific rate limiting with separate
    limiters for each platform and endpoint.
    """

    def __init__(self):
        """Initialize platform rate limiter."""
        self._limiters: Dict[str, RateLimiter] = {}
        self._endpoint_limiters: Dict[str, Dict[str, RateLimiter]] = defaultdict(dict)
        self._config = get_config()

        self._initialize_platform_limiters()

    def _initialize_platform_limiters(self) -> None:
        """Initialize rate limiters for all configured platforms."""
        # Twitter
        self._limiters["twitter"] = RateLimiter(
            requests_per_minute=180, requests_per_hour=900, burst_size=10
        )

        # Reddit
        self._limiters["reddit"] = RateLimiter(
            requests_per_minute=60, requests_per_hour=600, burst_size=5
        )

        # YouTube
        self._limiters["youtube"] = RateLimiter(
            requests_per_minute=300, requests_per_hour=10000, burst_size=10
        )

        # Instagram
        self._limiters["instagram"] = RateLimiter(
            requests_per_minute=200, requests_per_hour=4800, burst_size=10
        )

        # Medium
        self._limiters["medium"] = RateLimiter(
            requests_per_minute=50, requests_per_hour=1000, burst_size=5
        )

        # TikTok
        self._limiters["tiktok"] = RateLimiter(
            requests_per_minute=50, requests_per_hour=1000, burst_size=5
        )

    def acquire(
        self, platform: str, endpoint: Optional[str] = None, tokens: int = 1
    ) -> bool:
        """
        Acquire tokens for a platform/endpoint.

        Args:
            platform: Platform name
            endpoint: Optional endpoint name
            tokens: Number of tokens to acquire

        Returns:
            True if tokens acquired, False otherwise
        """
        limiter = self._get_limiter(platform, endpoint)
        return limiter.acquire(tokens)

    def wait_for_token(
        self, platform: str, endpoint: Optional[str] = None, tokens: int = 1
    ) -> None:
        """
        Wait until tokens are available for a platform/endpoint.

        Args:
            platform: Platform name
            endpoint: Optional endpoint name
            tokens: Number of tokens to wait for

        Raises:
            RateLimitError: If wait time exceeds threshold
        """
        limiter = self._get_limiter(platform, endpoint)
        limiter.wait_for_token(tokens)

    def get_available_tokens(
        self, platform: str, endpoint: Optional[str] = None
    ) -> tuple[int, int]:
        """
        Get available tokens for a platform/endpoint.

        Args:
            platform: Platform name
            endpoint: Optional endpoint name

        Returns:
            Tuple of (minute_tokens, hour_tokens)
        """
        limiter = self._get_limiter(platform, endpoint)
        return limiter.get_available_tokens()

    def reset(
        self, platform: Optional[str] = None, endpoint: Optional[str] = None
    ) -> None:
        """
        Reset rate limiter(s).

        Args:
            platform: Optional platform name
            endpoint: Optional endpoint name
        """
        if platform is None:
            # Reset all limiters
            for limiter in self._limiters.values():
                limiter.reset()
            for endpoint_dict in self._endpoint_limiters.values():
                for limiter in endpoint_dict.values():
                    limiter.reset()
        elif endpoint is None:
            # Reset platform limiter
            if platform in self._limiters:
                self._limiters[platform].reset()
            # Reset all endpoint limiters for platform
            if platform in self._endpoint_limiters:
                for limiter in self._endpoint_limiters[platform].values():
                    limiter.reset()
        else:
            # Reset specific endpoint limiter
            limiter = self._get_limiter(platform, endpoint)
            limiter.reset()

    def add_platform_limiter(
        self,
        platform: str,
        requests_per_minute: int,
        requests_per_hour: int,
        burst_size: int = 10,
    ) -> None:
        """
        Add or update a platform rate limiter.

        Args:
            platform: Platform name
            requests_per_minute: Requests per minute limit
            requests_per_hour: Requests per hour limit
            burst_size: Maximum burst size
        """
        self._limiters[platform] = RateLimiter(
            requests_per_minute=requests_per_minute,
            requests_per_hour=requests_per_hour,
            burst_size=burst_size,
        )

    def add_endpoint_limiter(
        self,
        platform: str,
        endpoint: str,
        requests_per_minute: int,
        requests_per_hour: int,
        burst_size: int = 10,
    ) -> None:
        """
        Add or update an endpoint-specific rate limiter.

        Args:
            platform: Platform name
            endpoint: Endpoint name
            requests_per_minute: Requests per minute limit
            requests_per_hour: Requests per hour limit
            burst_size: Maximum burst size
        """
        self._endpoint_limiters[platform][endpoint] = RateLimiter(
            requests_per_minute=requests_per_minute,
            requests_per_hour=requests_per_hour,
            burst_size=burst_size,
        )

    def _get_limiter(
        self, platform: str, endpoint: Optional[str] = None
    ) -> RateLimiter:
        """
        Get the appropriate rate limiter.

        Args:
            platform: Platform name
            endpoint: Optional endpoint name

        Returns:
            RateLimiter instance
        """
        # Check for endpoint-specific limiter
        if endpoint and platform in self._endpoint_limiters:
            if endpoint in self._endpoint_limiters[platform]:
                return self._endpoint_limiters[platform][endpoint]

        # Fall back to platform limiter
        if platform in self._limiters:
            return self._limiters[platform]

        # Create default limiter for unknown platform
        return RateLimiter(
            requests_per_minute=60, requests_per_hour=1000, burst_size=10
        )


def rate_limit(platform: str, endpoint: Optional[str] = None, tokens: int = 1):
    """
    Decorator to apply rate limiting to functions.

    Args:
        platform: Platform name
        endpoint: Optional endpoint name
        tokens: Number of tokens to consume

    Returns:
        Decorator function
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            limiter = PlatformRateLimiter()
            limiter.wait_for_token(platform, endpoint, tokens)
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Global rate limiter instance
_global_rate_limiter: Optional[PlatformRateLimiter] = None


def get_global_rate_limiter() -> PlatformRateLimiter:
    """
    Get the global rate limiter instance.

    Returns:
        PlatformRateLimiter instance
    """
    global _global_rate_limiter

    if _global_rate_limiter is None:
        _global_rate_limiter = PlatformRateLimiter()

    return _global_rate_limiter
