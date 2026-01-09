"""
Utility modules for Moderation AI.

This package provides utility functions including error handling,
rate limiting, and authentication management.
"""

from .error_handler import (
    ModerationError,
    ConfigurationError,
    ValidationError,
    AuthenticationError,
    RateLimitError,
    APIError,
    PlatformError,
    AnalysisError,
    ErrorHandler,
    create_error_response,
    wrap_errors,
)
from .rate_limiter import (
    RateLimiter,
    PlatformRateLimiter,
    rate_limit,
    get_global_rate_limiter,
)
from .auth_manager import (
    AuthManager,
    TwitterAuth,
    RedditAuth,
    YouTubeAuth,
    InstagramAuth,
    MediumAuth,
    TikTokAuth,
    setup_platform_credentials,
)

__all__ = [
    # Error handling
    "ModerationError",
    "ConfigurationError",
    "ValidationError",
    "AuthenticationError",
    "RateLimitError",
    "APIError",
    "PlatformError",
    "AnalysisError",
    "ErrorHandler",
    "create_error_response",
    "wrap_errors",
    # Rate limiting
    "RateLimiter",
    "PlatformRateLimiter",
    "rate_limit",
    "get_global_rate_limiter",
    # Authentication
    "AuthManager",
    "TwitterAuth",
    "RedditAuth",
    "YouTubeAuth",
    "InstagramAuth",
    "MediumAuth",
    "TikTokAuth",
    "setup_platform_credentials",
]
