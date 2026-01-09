"""Platform-Specific Unit Tests"""

from .test_instagram import (
    TestInstagramAPIClient,
    TestInstagramPostTracker,
    TestInstagramCommentModerator,
    TestInstagramRateLimiter,
    TestInstagramWebhookHandler,
    TestInstagramErrorHandling,
    TestInstagramIntegration,
)

from .test_medium import (
    TestMediumAPIClient,
    TestMediumPostTracker,
    TestMediumCommentModerator,
    TestMediumRateLimiter,
    TestMediumWebhookHandler,
    TestMediumErrorHandling,
    TestMediumIntegration,
)

from .test_tiktok import (
    TestTikTokAPIClient,
    TestTikTokPostTracker,
    TestTikTokCommentModerator,
    TestTikTokRateLimiter,
    TestTikTokWebhookHandler,
    TestTikTokErrorHandling,
    TestTikTokIntegration,
)

__all__ = [
    # Instagram tests
    "TestInstagramAPIClient",
    "TestInstagramPostTracker",
    "TestInstagramCommentModerator",
    "TestInstagramRateLimiter",
    "TestInstagramWebhookHandler",
    "TestInstagramErrorHandling",
    "TestInstagramIntegration",
    # Medium tests
    "TestMediumAPIClient",
    "TestMediumPostTracker",
    "TestMediumCommentModerator",
    "TestMediumRateLimiter",
    "TestMediumWebhookHandler",
    "TestMediumErrorHandling",
    "TestMediumIntegration",
    # TikTok tests
    "TestTikTokAPIClient",
    "TestTikTokPostTracker",
    "TestTikTokCommentModerator",
    "TestTikTokRateLimiter",
    "TestTikTokWebhookHandler",
    "TestTikTokErrorHandling",
    "TestTikTokIntegration",
]
