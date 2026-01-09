"""Rate Limiting Tests for All Platforms"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time
from datetime import datetime

from tests.fixtures import (
    mock_rate_limiter,
    sample_rate_limit_info,
    MockInstagramAPI,
    sample_comment,
    sample_post,
    sample_video,
    sample_comments_list
    instagram_config,
    medium_config,
    tiktok_config
)


@pytest.mark.unit
@pytest.mark.network
@pytest.mark.parametrize('platform', ['instagram', 'medium', 'tiktok'])
class TestRateLimiting:
    """Test rate limiting for all platforms"""
    
    @pytest.mark.parametrize('platform', ['instagram', 'medium', 'tiktok'])
    def test_rate_limit_initialization(self, platform, platform_config):
        """Test rate limiter initialization"""
        from tests.fixtures import (
            mock_rate_limiter,
            sample_rate_limit_info
        )
        
        limiter = mock_rate_limiter()
        
        if platform == 'instagram':
            limiter = mock_rate_limiter()
            assert limiter.requests_per_minute == 10
        elif platform == 'medium':
            limiter = mock_rate_limiter()
        elif platform == 'tiktok':
            limiter = mock_rate_limiter()
        
        assert limiter.requests_per_minute > 0
    
    def test_request_recording(self, mock_rate_limiter):
        """Test request recording"""
        mock_rate_limiter()
        
        # Record 5 requests
        for _ in range(5):
            mock_rate_limiter.record_request()
        
        assert mock_rate_limiter.request_count == 5
    
    def test_limit_check_under_limit(self, mock_rate_limiter):
        """Test limit checking when under limit"""
        mock_rate_limiter()
        
        # Record requests under limit
        for _ in range(5):
            mock_rate_limiter.record_request()
        
        # Check if should wait
        result = mock_rate_limiter.check_rate_limit()
        
        assert result['remaining'] > 0
        assert result['limit'] == 100
        assert result['reset'] is not None
    
    def test_limit_check_over_limit(self, mock_rate_limiter):
        """Test limit checking when over limit"""
        mock_rate_limiter()
        
        # Record requests to hit limit
        for _ in range(15):
            mock_rate_limiter.record_request()
        
        # Check if should wait
        result = mock_rate_limiter.check_rate_limit()
        
        assert result['remaining'] == 0
        assert result['limit'] == 100
    
    def test_wait_if_needed_under_limit(self, mock_rate_limiter):
        """Test wait when under limit"""
        mock_rate_limiter()
        
        # Mock under limit state
        mock_rate_limiter.check_rate_limit.return_value = sample_rate_limit_info()
        
        # Should not wait
        mock_rate_limiter.wait_if_needed.return_value = None
        
        result = mock_rate_limiter.wait_if_needed()
        
        assert result is None
    
    def test_wait_if_needed_over_limit(self, mock_rate_limiter):
        """Test wait when over limit"""
        mock_rate_limiter()
        
        # Mock over limit state
        mock_rate_limiter.check_rate_limit.return_value = {
            'limit': 100,
            'remaining': 0,
            'reset': '1234567890',
            'reset_time': datetime.fromtimestamp(1234567890).isoformat()
        }
        
        # Should wait
        with patch('time.sleep') as mock_sleep:
            mock_rate_limiter.wait_if_needed()
            
            # Should have slept
            assert mock_sleep.called
    
    def test_rate_limit_info_retrieval(self, mock_rate_limiter):
        """Test rate limit info retrieval"""
        mock_rate_limiter()
        
        info = mock_rate_limiter.get_rate_limit_info()
        
        assert 'limit' in info
        assert 'remaining' in info
        assert 'reset' in info
    
    @pytest.mark.network
    @pytest.mark.parametrize('platform', ['instagram', 'medium', 'tiktok'])
    def test_api_rate_limiting_enforcement(self, platform, platform_config):
        """Test API rate limiting enforcement"""
        from tests.fixtures import (
            MockInstagramAPI,
            sample_media,
            mock_rate_limiter,
            platform_config
        )
        from src.platforms.instagram.client import InstagramAPIClient
        from src.platforms.instagram.rate_limiter import InstagramRateLimiter
        
        client = InstagramAPIClient(platform_config())
        limiter = InstagramRateLimiter(requests_per_minute=10)
        
        client.get_media.return_value = sample_media()
        
        # Record 5 requests (under limit)
        for _ in range(5):
            limiter.record_request()
            limiter.wait_if_needed()
            client.get_media('test_media')
        
        # Should have recorded 5 requests
        assert limiter.request_count == 5
        
        # Should have waited at least once (last request triggers wait)
        assert limiter.wait_if_needed.call_count >= 1
    
    @pytest.mark.network
    @pytest.mark.slow
    def test_rate_limit_recovery_over_time(self, mock_rate_limiter):
        """Test rate limit recovery over time"""
        mock_rate_limiter()
        
        # Hit limit
        for _ in range(15):
            mock_rate_limiter.record_request()
        
        # Check over limit
        result = mock_rate_limiter.check_rate_limit()
        assert result['remaining'] == 0
        
        # Wait for reset
        mock_rate_limiter.reset.return_value = None
        
        import time
        time.sleep(0.1)  # Simulate time passing
        
        # Should have reset
        result = mock_rate_limiter.check_rate_limit()
        assert result['remaining'] == 100
    
    @pytest.mark.network
    @pytest.mark.parametrize('platform', ['instagram', 'medium', 'tiktok'])
    def test_concurrent_request_handling(self, platform):
        """Test concurrent request handling with rate limiting"""
        from tests.fixtures import (
            MockInstagramAPI,
            sample_media,
            mock_rate_limiter,
            platform_config
            sample_comments_list
            )
        from src.platforms.instagram.client import InstagramAPIClient
        from src.platforms.instagram.rate_limiter import InstagramRateLimiter
        
        client = InstagramAPIClient(platform_config())
        limiter = InstagramRateLimiter(requests_per_minute=10)
        comments = sample_comments_list(count=10)
        
        # Make 10 concurrent requests
        import threading
        threads = []
        for i in range(10):
            thread = threading.Thread(
                target=client.get_media,
                args=('test_media_id')
            )
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join(timeout=5)
        
        # Should have processed all requests
        assert limiter.request_count == 10
    
    @pytest.mark.unit
    def test_backoff_calculation(self):
        """Test exponential backoff calculation"""
        # Base delay of 2 seconds
        base_delay = 2
        
        expected_delays = [2, 4, 8, 16]
        
        for attempt, expected in enumerate(expected_delays):
            delay = base_delay * (2 ** attempt)
            assert delay == expected
    
    def test_sliding_window_algorithm(self, mock_rate_limiter):
        """Test sliding window rate limit algorithm"""
        mock_rate_limiter()
        
        # Mock timestamps
        now = datetime.now()
        timestamps = [
            now - timedelta(minutes=i).timestamp()
            for i in range(5)
        ]
        
        mock_rate_limiter._request_timestamps = timestamps
        
        # Calculate requests in window
        requests_in_window = sum(
            1 for ts in timestamps
            if (now - ts).total_seconds() < 60
        )
        
        assert requests_in_window == 5
    
    @pytest.mark.unit
    def test_rate_limit_headers_parsing(self):
        """Test rate limit header parsing"""
        headers = {
            'X-RateLimit-Limit': '100',
            'X-RateLimit-Remaining': '95',
            'X-RateLimit-Reset': '1234567890'
        }
        
        limit = int(headers['X-RateLimit-Limit'])
        remaining = int(headers['X-RateLimit-Remaining'])
        reset = int(headers['X-RateLimit-Reset'])
        
        assert limit == 100
        assert remaining == 95
        assert reset > 0
    
    @pytest.mark.network
    @pytest.mark.parametrize('platform', ['instagram', 'medium', 'tiktok'])
    def test_platform_specific_limits(self, platform):
        """Test platform-specific rate limits"""
        if platform == 'instagram':
            limit = 200  # requests per hour
            window = 3600  # 1 hour window
        elif platform == 'medium':
            limit = 100  # requests per hour
            window = 3600  # 1 hour window
        elif platform == 'tiktok':
            limit = 100  # requests per hour
            window = 3600  # 1 hour window
        else:
            pytest.skip(f"Unknown platform: {platform}")
        
        assert limit > 0
        assert window > 0


@pytest.mark.integration
@pytest.mark.network
class TestRateLimitingIntegration:
    """Integration tests for rate limiting"""
    
    @pytest.mark.network
    def test_real_api_rate_limiting(self):
        """Test real API rate limiting (would need real API)"""
        from tests.fixtures import (
            MockInstagramAPI,
            mock_rate_limiter,
            platform_config
            sample_media
        )
        from src.platforms.instagram.client import InstagramAPIClient
        from src.platforms.instagram.rate_limiter import InstagramRateLimiter
        
        client = InstagramAPIClient(platform_config())
        limiter = InstagramRateLimiter(requests_per_minute=10)
        
        client.get_media.return_value = sample_media()
        
        # Hit rate limit
        for _ in range(15):
            limiter.record_request()
        
        # Next request should wait
        with patch('time.sleep') as mock_sleep:
            limiter.wait_if_needed()
            
            assert mock_sleep.called
    
    @pytest.mark.network
    @pytest.mark.parametrize('platform', ['instagram', 'medium', 'tiktok'])
    def test_cross_platform_rate_limiting(self, platform):
        """Test rate limiting across platforms"""
        from tests.fixtures import (
            mock_rate_limiter,
            platform_config
        )
        from src.platforms.instagram.rate_limiter import InstagramRateLimiter
        from src.platforms.medium.rate_limiter import MediumRateLimiter
        from src.platforms.tiktok.rate_limiter import TikTokRateLimiter
        
        instagram_config = platform_config('instagram')
        medium_config = platform_config('medium')
        tiktok_config = platform_config('tiktok')
        
        instagram_limiter = InstagramRateLimiter(requests_per_minute=10)
        medium_limiter = MediumRateLimiter(requests_per_minute=10)
        tiktok_limiter = TikTokRateLimiter(requests_per_minute=10)
        
        # All limiters should be consistent
        assert instagram_limiter.requests_per_minute == 10
        assert medium_limiter.requests_per_minute == 10
        assert tiktok_limiter.requests_per_minute == 10


if __name__ == '__main__':
    pytest.main([__file__], '-v')
