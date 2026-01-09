"""API Client Tests for All Platforms"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from tests.fixtures import (
    MockInstagramAPI,
    MockMediumAPI,
    MockTikTokAPI,
    sample_comment,
    sample_post,
    sample_video,
    sample_article,
    mock_error_response,
    auth_headers,
    sample_rate_limit_info
)


@pytest.mark.unit
@pytest.mark.network
@pytest.mark.parametrize('platform', ['instagram', 'medium', 'tiktok'])
class TestAPIClients:
    """Tests for API Clients"""
    
    def test_api_client_timeout(self, platform):
        """Test API client timeout handling"""
        if platform == 'instagram':
            client = MockInstagramAPI()
        elif platform == 'medium':
            from tests.fixtures import MockMediumAPI
            client = MockMediumAPI()
        elif platform == 'tiktok':
            from tests.fixtures import MockTikTokAPI
            client = MockTikTokAPI()
        else:
            pytest.skip(f"Unknown platform: {platform}")
        
        # Mock timeout
        import requests
        client.get_media.side_effect = requests.exceptions.Timeout('Request timeout')
        
        # Should handle timeout
        with pytest.raises(requests.exceptions.Timeout):
            client.get_media('test_id')
    
    def test_api_client_connection_error(self, platform):
        """Test API client connection errors"""
        if platform == 'instagram':
            client = MockInstagramAPI()
        elif platform == 'medium':
            from tests.fixtures import MockMediumAPI
            client = MockMediumAPI()
        elif platform == 'tiktok':
            from tests.fixtures import MockTikTokAPI
            client = MockTikTokAPI()
        else:
            pytest.skip(f"Unknown platform: {platform}")
        
        # Mock connection error
        import requests.exceptions
        client.get_media.side_effect = requests.exceptions.ConnectionError('Connection failed')
        
        # Should handle connection error
        with pytest.raises(requests.exceptions.ConnectionError):
            client.get_media('test_id')
    
    def test_api_client_json_parsing_error(self, platform):
        """Test API client JSON parsing errors"""
        if platform == 'instagram':
            client = MockInstagramAPI()
        elif platform == 'medium':
            from tests.fixtures import MockMediumAPI
            client = MockMediumAPI()
        elif platform == 'tiktok':
            from tests.fixtures import MockTikTokAPI
            client = MockTikTokAPI()
        else:
            pytest.skip(f"Unknown platform: {platform}")
        
        # Mock JSON parsing error
        response = Mock()
        response.json.side_effect = json.JSONDecodeError('Invalid JSON')
        
        # Should handle JSON error
        with pytest.raises(json.JSONDecodeError):
            client.get_media('test_id')
    
    @pytest.mark.unit
    @pytest.mark.parametrize('platform', ['instagram', 'medium', 'tiktok'])
    def test_api_client_retries(self, platform):
        """Test API client retry logic"""
        if platform == 'instagram':
            client = MockInstagramAPI()
        elif platform == 'medium':
            from tests.fixtures import MockMediumAPI
            client = MockMediumAPI()
        elif platform == 'tiktok':
            from tests.fixtures import MockTikTokAPI
            client = MockTikTokAPI()
        else:
            pytest.skip(f"Unknown platform: {platform}")
        
        # Mock retry behavior
        client.get_media.side_effect = [
            requests.exceptions.ConnectionError('Connection failed'),
            requests.exceptions.Timeout('Request timeout'),
            requests.exceptions.HTTPError('HTTP error')
        ]
        
        # Should succeed on third try
        result = client.get_media('test_id')
        
        assert result['id'] == 'test_media_id'
        assert client.get_media.call_count == 3
    
    def test_api_client_response_caching(self, platform):
        """Test API client response caching"""
        if platform == 'instagram':
            client = MockInstagramAPI()
        elif platform == 'medium':
            from tests.fixtures import MockMediumAPI
            client = MockMediumAPI()
        elif platform == 'tiktok':
            from tests.fixtures import MockTikTokAPI
            client = MockTikTokAPI()
        else:
            pytest.skip(f"Unknown platform: {platform}")
        
        # Call twice, should return cached result
        response1 = {'id': 'test_media_1', 'caption': 'Test'}
        response2 = {'id': 'test_media_2', 'caption': 'Test'}
        
        client.get_media.return_value = response1
        
        result1 = client.get_media('test_media_1')
        result2 = client.get_media('test_media_2')
        
        assert result1['id'] == result2['id']
        assert client.get_media.call_count == 2


class TestInstagramAPIClientErrors:
    """Tests for Instagram API Client Error Handling"""
    
    @pytest.mark.unit
    def test_handle_rate_limit_429(self):
        """Test rate limit error handling"""
        from tests.fixtures import (
            MockInstagramAPI,
            sample_rate_limit_info
            mock_error_response
        )
        
        client = MockInstagramAPI()
        
        error_response = mock_error_response(status_code=429)
        
        with patch('requests.get', return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_media('test_id')
            
            assert 'Rate limit' in str(exc_info.value).lower()
            assert exc_info.value.status_code == 429
    
    @pytest.mark.unit
    def test_handle_forbidden_403(self):
        """Test forbidden error handling"""
        from tests.fixtures import MockInstagramAPI, mock_error_response
        
        client = MockInstagramAPI()
        error_response = mock_error_response(status_code=403)
        
        with patch('requests.get', return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_media('test_id')
            
            assert 'Forbidden' in str(exc_info.value).lower()
            assert exc_info.value.status_code == 403
    
    @pytest.mark.unit
    def test_handle_not_found_404(self):
        """Test not found error handling"""
        from tests.fixtures import MockInstagramAPI, mock_error_response
        
        client = MockInstagramAPI()
        error_response = mock_error_response(status_code=404)
        
        with patch('requests.get', return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_media('test_id')
            
            assert 'not found' in str(exc_info.value).lower()
            assert exc_info.value.status_code == 404
    
    @pytest.mark.unit
    def test_handle_unauthorized_401(self):
        """Test unauthorized error handling"""
        from tests.fixtures import MockInstagramAPI, mock_error_response
        
        client = MockInstagramAPI()
        error_response = mock_error_response(status_code=401)
        
        with patch('requests.get', return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_media('test_id')
            
            assert 'unauthorized' in str(exc_info.value).lower()
            assert exc_info.value.status_code == 401


class TestMediumAPIClientErrors:
    """Tests for Medium API Client Error Handling"""
    
    @pytest.mark.unit
    def test_handle_rate_limit_429(self):
        """Test rate limit error handling"""
        from tests.fixtures import (
            MockMediumAPI,
            sample_rate_limit_info,
            mock_error_response
        )
        
        client = MockMediumAPI()
        
        error_response = mock_error_response(status_code=429)
        
        with patch('requests.get', return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_article_comments('article_id')
            
            assert 'Rate limit' in str(exc_info.value).lower()
            assert exc_info.value.status_code == 429
    
    @pytest.mark.unit
    def test_handle_forbidden_403(self):
        """Test forbidden error handling"""
        from tests.fixtures import MockMediumAPI, mock_error_response
        
        client = MockMediumAPI()
        error_response = mock_error_response(status_code=403)
        
        with patch('requests.get', return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_article_comments('article_id')
            
            assert 'Forbidden' in str(exc_info.value).lower()
            assert exc_info.value.status_code == 403
    
    @pytest.mark.unit
    def test_handle_invalid_grant_400(self):
        """Test invalid grant error handling"""
        from tests.fixtures import MockMediumAPI, mock_error_response
        
        client = MockMediumAPI()
        error_response = mock_error_response(status_code=400)
        
        error_response.headers = {
            'Content-Type': 'application/json',
            'X-Invalid-Grant': 'invalid_grant_type'
        }
        
        with patch('requests.get', return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_article_comments('article_id')
            
            assert 'invalid grant' in str(exc_info.value).lower()
            assert exc_info.value.status_code == 400
    
    @pytest.mark.unit
    def test_handle_not_found_404(self):
        """Test not found error handling"""
        from tests.fixtures import MockMediumAPI, mock_error_response
        
        client = MockMediumAPI()
        error_response = mock_error_response(status_code=404)
        
        with patch('requests.get', return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_article_comments('article_id')
            
            assert 'not found' in str(exc_info.value).lower()
            assert exc_info.value.status_code == 404


class TestTikTokAPIClientErrors:
    """Tests for TikTok API Client Error Handling"""
    
    @pytest.mark.unit
    def test_handle_rate_limit_429(self):
        """Test rate limit error handling"""
        from tests.fixtures import (
            MockTikTokAPI,
            sample_rate_limit_info,
            mock_error_response
        )
        
        client = MockTikTokAPI()
        
        error_response = mock_error_response(status_code=429)
        
        with patch('requests.get', return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_video_comments('video_id')
            
            assert 'Rate limit' in str(exc_info.value).lower()
            assert exc_info.value.status_code == 429
    
    @pytest.mark.unit
    def test_handle_forbidden_403(self):
        """Test forbidden error handling"""
        from tests.fixtures import MockTikTokAPI, mock_error_response
        
        client = MockTikTokAPI()
        error_response = mock_error_response(status_code=403)
        
        with patch('requests.get', return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_video_comments('video_id')
            
            assert 'Forbidden' in str(exc_info.value).lower()
            assert exc_info.value.status_code == 403
    
    @pytest.mark.unit
    def test_handle_unauthorized_401(self):
        """Test unauthorized error handling"""
        from tests.fixtures import MockTikTokAPI, mock_error_response
        
        client = MockTikTokAPI()
        error_response = mock_error_response(status_code=401)
        
        with patch('requests.get', return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_video_comments('video_id')
            
            assert 'unauthorized' in str(exc_info.value).lower()
            assert exc_info.value.status_code == 401
    
    @pytest.mark.unit
    def test_handle_not_found_404(self):
        """Test not found error handling"""
        from tests.fixtures import MockTikTokAPI, mock_error_response
        
        client = MockTikTokAPI()
        error_response = mock_error_response(status_code=404)
        
        with patch('requests.get', return_value=error_response):
            with pytest.raises(Exception) as exc_info:
                client.get_video_comments('video_id')
            
            assert 'not found' in str(exc_info.value).lower()
            assert exc_info.value.status_code == 404


@pytest.mark.unit
@pytest.mark.network
class TestCommonErrorHandling:
    """Common Error Handling Tests"""
    
    def test_timeout_handling(self):
        """Test timeout error handling"""
        import requests.exceptions
        
        error = requests.exceptions.Timeout('Request timeout')
        
        with pytest.raises(requests.exceptions.Timeout) as exc_info:
            assert 'Request timeout' in str(exc_info.value)
            assert exc_info.value.__class__.__name__ == 'Timeout'
    
    def test_connection_error_handling(self):
        """Test connection error handling"""
        import requests.exceptions
        
        error = requests.exceptions.ConnectionError('Connection failed')
        
        with pytest.raises(requests.exceptions.ConnectionError) as exc_info:
            assert 'Connection failed' in str(exc_info.value)
            assert exc_info.value.__class__.__name__ == 'ConnectionError'
    
    def test_json_error_handling(self):
        """Test JSON error handling"""
        import json
        
        error = json.JSONDecodeError('Invalid JSON')
        
        with pytest.raises(json.JSONDecodeError) as exc_info:
            assert 'Invalid JSON' in str(exc_info.value)
            assert exc_info.value.__class__.__name__ == 'JSONDecodeError'
    
    @pytest.mark.unit
    def test_retriable_error_messages(self):
        """Test error message reliability"""
        error_messages = {
            'rate_limit_exceeded': 'Rate limit exceeded',
            'invalid_token': 'The access token provided is invalid',
            'forbidden': 'Insufficient permissions',
            'not_found': 'Resource not found'
        }
        
        for key, expected_message in error_messages.items():
            # Check that error messages contain expected text
            # (This is a simplified check - in real scenario, would be more specific)
            assert 'exceeded' in expected_message.lower()
            assert 'invalid token' in expected_message.lower()
            assert 'forbidden' in expected_message.lower()
            assert 'not found' in expected_message.lower()


if __name__ == '__main__':
    pytest.main([__file__], '-v')
