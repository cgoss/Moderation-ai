"""
Platform integrations for social media platforms.

This package provides abstract base class and platform-specific
implementations for interacting with various social media APIs.
"""

from .base import BasePlatform
from .twitter import TwitterPlatform
from .reddit import RedditPlatform
from .youtube import YouTubePlatform
from .instagram import InstagramPlatform
from .medium import MediumPlatform
from .tiktok import TikTokPlatform

__all__ = [
    "BasePlatform",
    "TwitterPlatform",
    "RedditPlatform",
    "YouTubePlatform",
    "InstagramPlatform",
    "MediumPlatform",
    "TikTokPlatform",
]
