"""Webhook Tests for All Platforms"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import hmac
import hashlib

from tests.fixtures import (
    create_webhook_event,
    webhook_event,
    sample_comment,
    sample_post,
    platform_config,
    MockInstagramAPI,
    MockMediumAPI,
    MockTikTokAPI
)


@pytest.mark.unit
@pytest.mark.network
@pytest.mark.parametrize('platform', ['instagram', 'medium', 'tiktok'])
class TestWebhooks:
    """Test webhook handling for all platforms"""
    
    def test_webhook_signature_generation(self, platform):
        """Test webhook signature generation"""
        from tests.fixtures import (
            webhook_event,
            platform_config
        )
        
        event = webhook_event()
        
        if platform == 'instagram':
            secret = b'test_instagram_secret'
        elif platform == 'medium':
            secret = b'test_medium_secret'
        elif platform == 'tiktok':
            secret = b'test_tiktok_secret'
        else:
            pytest.skip(f"Unknown platform: {platform}")
        
        # Generate signature
        import hmac
        signature = hmac.new(secret, b'test_payload', hashlib.sha256).hexdigest()
        
        assert len(signature) == 64  # SHA256 is 32 bytes in hex
        assert isinstance(signature, str)
    
    def test_webhook_signature_verification(self, platform):
        """Test webhook signature verification"""
        from tests.fixtures import (
            create_webhook_event,
            platform_config,
            MockWebhookHandler
        )
        
        event = create_webhook_event()
        handler = MockWebhookHandler(secret='test_secret')
        
        # Generate signature
        signature = handler.generate_signature(b'test_payload')
        
        # Verify correct signature
        assert handler.verify_signature(b'test_payload', signature) is True
        
        # Verify incorrect signature
        assert handler.verify_signature(b'wrong_payload', 'wrong_signature') is False
    
    @pytest.mark.unit
    def test_webhook_event_parsing(self):
        """Test webhook event parsing"""
        from tests.fixtures import (
            create_webhook_event,
            platform_config,
            sample_comment
        )
        
        event = create_webhook_event()
        
        assert 'type' in event
        assert 'comment_id' in event
        assert 'timestamp' in event
        assert 'payload' in event
    
    @pytest.mark.unit
    def test_webhook_handler_initialization(self, platform, platform_config):
        """Test webhook handler initialization"""
        from tests.fixtures import (
            platform_config,
            MockWebhookHandler
        )
        
        handler = MockWebhookHandler(
            secret=platform_config['webhook_secret']
        )
        
        assert handler.secret == platform_config['webhook_secret']
        assert handler.handlers == {}
    
    def test_webhook_handler_registration(self, platform, platform_config):
        """Test webhook handler registration"""
        from tests.fixtures import (
            platform_config,
            MockWebhookHandler
            sample_comment
            sample_post
        )
        
        handler = MockWebhookHandler(secret='test_secret')
        
        handler.register_handler('comment.created', Mock())
        
        assert 'comment.created' in handler.handlers
    
    @pytest.mark.network
    def test_webhook_event_handling(self, platform, platform_config):
        """Test webhook event handling"""
        from tests.fixtures import (
            create_webhook_event,
            platform_config,
            MockWebhookHandler,
            mock_moderation_engine
        )
        
        handler = MockWebhookHandler(secret='test_secret')
        engine = mock_moderation_engine()
        event = create_webhook_event()
        
        # Register handler
        handler.register_handler('comment.created', Mock())
        
        # Handle event
        handler.handle_event('comment.created', event)
        
        # Verify handler was called
        assert handler.handle_comment_created.called_once()
    
    @pytest.mark.unit
    @pytest.mark.parametrize('platform', ['instagram', 'medium', 'tiktok'])
    def test_webhook_security_validation(self, platform):
        """Test webhook security validation"""
        from tests.fixtures import (
            platform_config,
            create_webhook_event
        )
        
        event = create_webhook_event()
        
        if platform == 'instagram':
            secret = b'test_instagram_secret'
        elif platform == 'medium':
            secret = b'test_medium_secret'
        elif platform == 'tiktok':
            secret = b'test_tiktok_secret'
        
        # Test various attack scenarios
        # Replay attack
        replay_event = create_webhook_event()
        
        # Valid signature but wrong payload
        signature = hmac.new(secret, b'test_payload', hashlib.sha256).hexdigest()
        handler = MockWebhookHandler(secret=secret)
        
        # Should verify correct signature, reject wrong payload
        assert handler.verify_signature(b'test_payload', signature) is True
        assert handler.verify_signature(b'different_payload', 'different_signature') is False
        
        # Timing attack (old signature)
        old_signature = hmac.new(secret, b'old_payload', hashlib.sha256).hexdigest()
        assert handler.verify_signature(b'old_payload', old_signature) is False
        
        # Missing signature
        assert handler.verify_signature(b'no_signature_payload', '') is False
    
    @pytest.mark.network
    @pytest.mark.parametrize('platform', ['instagram', 'medium', 'tiktok'])
    def test_webhook_delivery(self, platform):
        """Test webhook delivery reliability"""
        from tests.fixtures import (
            create_webhook_event,
            platform_config,
            MockWebhookHandler
            MockInstagramAPI
            MockMediumAPI
            MockTikTokAPI
        )
        
        handler = MockWebhookHandler(secret='test_secret')
        instagram = MockInstagramAPI()
        medium = MockMediumAPI()
        tiktok = MockTikTokAPI()
        
        event = create_webhook_event()
        
        if platform == 'instagram':
            handler.handle_event('comment.created', event)
        elif platform == 'medium':
            handler.handle_event('comment.created', event)
        elif platform == 'tiktok':
            handler.handle_event('comment.created', event)
        
        assert handler.handle_comment_created.call_count == 1
    
    @pytest.mark.integration
    @pytest.mark.network
    def test_webhook_with_moderation(self, platform, platform_config):
        """Test webhook integration with moderation"""
        from tests.fixtures import (
            create_webhook_event,
            platform_config,
            MockWebhookHandler,
            mock_moderation_engine,
            sample_comment
            )
        
        handler = MockWebhookHandler(secret='test_secret')
        engine = mock_moderation_engine()
        event = create_webhook_event()
        
        handler.register_handler('comment.created', Mock())
        
        # Handle event - moderation happens
        handler.handle_event('comment.created', event)
        
        # Verify analysis and action
        assert engine.analyze_comment.called
        assert engine.evaluate_rules.called
    
    @pytest.mark.unit
    def test_webhook_error_handling(self, platform):
        """Test webhook error handling"""
        from tests.fixtures import (
            platform_config,
            MockWebhookHandler,
            create_webhook_event
            sample_comment
        )
        
        handler = MockWebhookHandler(secret='test_secret')
        event = create_webhook_event()
        
        # Mock error in verification
        handler.verify_signature.return_value = False
        
        # Should reject event
        result = handler.handle_event('comment.created', event)
        
        assert result is False
        assert not handler.handle_comment_created.called
    
    @pytest.mark.unit
    @pytest.mark.parametrize('platform', ['instagram', 'medium', 'tiktok'])
    def test_webhook_payload_validation(self, platform):
        """Test webhook payload validation"""
        from tests.fixtures import (
            create_webhook_event
            platform_config
        )
        
        event = create_webhook_event()
        
        # Valid payload structure
        assert 'type' in event
        assert 'payload' in event
        assert 'timestamp' in event
        assert 'comment_id' in event
        assert 'text' in event
        
        # Missing required fields
        invalid_event = create_webhook_event()
        invalid_event.pop('comment_id')
        
        handler = MockWebhookHandler(secret='test_secret')
        
        with pytest.raises(ValueError) as exc_info:
            handler.handle_event('comment.created', invalid_event)
        
        assert 'required field missing' in str(exc_info.value).lower()
    
    @pytest.mark.unit
    def test_webhook_event_types(self, platform, platform_config):
        """Test webhook event type handling"""
        from tests.fixtures import (
            platform_config,
            MockWebhookHandler,
            create_webhook_event
        )
        
        handler = MockWebhookHandler(secret='test_secret')
        
        # Register handlers for different event types
        handler.register_handler('comment.created', Mock())
        handler.register_handler('comment.deleted', Mock())
        handler.register_handler('user.blocked', Mock())
        
        # Test registration
        assert len(handler.handlers) == 3
        assert 'comment.created' in handler.handlers
        assert 'comment.deleted' in handler.handlers
        assert 'user.blocked' in handler.handlers


if __name__ == '__main__':
    pytest.main([__file__], '-v')
