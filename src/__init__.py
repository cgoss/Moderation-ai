"""
Moderation AI Library.

A comprehensive library for content moderation and analysis
across multiple social media platforms.
"""

__version__ = "0.1.0"
__author__ = "Colin Goss"

from .core import *
from .utils import *
from .analysis import *
from .platforms import *

__all__ = [
    # Core
    "Config",
    "get_config",
    "Comment",
    "Post",
    "Violation",
    "ModerationResult",
    "AnalysisResult",
    "ModerationEngine",
    "Analyzer",
    "MetricsValidator",
    "ModerationAction",
    "Severity",
    "Sentiment",
    "StandardsEngine",
    "Standard",
    "Metric",
    "TextAnalyzer",
    # Utils
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
    "RateLimiter",
    "PlatformRateLimiter",
    "rate_limit",
    "get_global_rate_limiter",
    "AuthManager",
    "TwitterAuth",
    "RedditAuth",
    "YouTubeAuth",
    "InstagramAuth",
    "MediumAuth",
    "TikTokAuth",
    "setup_platform_credentials",
    # Analysis
    "Analyzer",
    "CompositeAnalyzer",
    "SentimentAnalyzer",
    "Categorizer",
    "Summarizer",
    "AbuseDetector",
    "FAQExtractor",
    "ContentIdeator",
    "CommunityMetrics",
    # Platforms
    "BasePlatform",
]
