# Track Post Example

This example demonstrates how to track an Instagram post for new comments.

```python
import asyncio
from datetime import datetime, timedelta
from moderation_ai.platforms import InstagramAPI
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

async def track_post_with_monitoring():
    """
    Continuously monitor an Instagram post for new comments.
    """
    # Initialize Instagram API
    instagram = InstagramAPI.from_env()
    
    # Initialize analyzers
    standards = StandardsEngine(auto_moderate=True)
    abuse_detector = AbuseDetector(strict_mode=True)
    
    # Media ID to track
    media_id = "123456789_456789"
    
    # Tracking configuration
    polling_interval = 60  # Check every 60 seconds
    max_comments = 1000
    tracked_comments = set()
    
    print(f"Starting to monitor post {media_id}")
    print("Press Ctrl+C to stop...")
    
    try:
        while True:
            # Fetch recent comments
            comments = await instagram.fetch_comments(
                media_id,
                limit=max_comments
            )
            
            # Get comment IDs
            current_comment_ids = {c.id for c in comments}
            
            # Find new comments
            new_comments = current_comment_ids - tracked_comments
            
            if new_comments:
                print(f"\n[{datetime.utcnow().isoformat()}] Found {len(new_comments)} new comments")
                
                # Process new comments
                for comment_id in new_comments:
                    # Find full comment object
                    comment = next((c for c in comments if c.id == comment_id), None)
                    
                    if comment:
                        # Quick abuse check
                        abuse_result = abuse_detector.analyze(comment)
                        
                        # Apply moderation if severe abuse
                        if abuse_result.data.get('is_abusive'):
                            severity = abuse_result.data.get('severity')
                            print(f"  -> Severe abuse detected: {severity}")
                            
                            if severity in ['high', 'critical']:
                                try:
                                    await instagram.moderate_comment(comment_id, "hide")
                                    print(f"  -> Hidden comment {comment_id}")
                                except Exception as e:
                                    print(f"  -> Failed to hide: {e}")
                            else:
                                # Flag for review
                                print(f"  -> Flagged for review")
                        
                        # Standard moderation
                        decision = standards.validate(comment.text)
                        
                        if decision.action != "approve":
                            print(f"  -> Action: {decision.action}")
                            print(f"  -> Reason: {decision.reasoning[:100]}...")
                
                # Update tracked comments
                tracked_comments = current_comment_ids
            
            # Wait before next poll
            await asyncio.sleep(polling_interval)
    
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
    except Exception as e:
        print(f"\nError during monitoring: {e}")

if __name__ == "__main__":
    asyncio.run(track_post_with_monitoring())
```

## Monitoring Strategies

### Polling
- **Interval**: Check every 60 seconds (adjustable)
- **Limit**: Fetch last 1000 comments
- **Efficiency**: Only process new comments

### Event-Based
Instagram doesn't provide real-time webhooks for comments. Polling is required.

## Configuration Options

```python
# High-frequency monitoring (not recommended)
polling_interval = 30  # 30 seconds

# Standard monitoring (recommended)
polling_interval = 60  # 60 seconds

# Low-frequency monitoring
polling_interval = 120  # 2 minutes
```

## Tracking Features

### Comment Tracking
- **New comment detection**: Identify comments since last check
- **Abuse alerts**: Immediate notification of severe abuse
- **Auto-moderation**: Automatic hiding of abusive content
- **Audit logging**: Track all moderation actions

### Statistics
```python
# Track moderation statistics
stats = {
    'total_processed': 0,
    'auto_hidden': 0,
    'flagged': 0,
    'approved': 0
}
```

## Rate Limit Considerations

1. **Polling frequency**: Balance responsiveness with rate limits
2. **Batch processing**: Process multiple comments efficiently
3. **Caching**: Cache media metadata to reduce API calls
4. **Error handling**: Implement backoff for rate limit errors

## Advanced: Webhook Integration

While Instagram doesn't provide comment webhooks, you can:
1. Use Instagram Webhooks for other events
2. Set up external webhook service
3. Trigger comment checks based on post events

## Related Examples

- `fetch-comments.md` - How to fetch comments
- `moderate-comment.md` - How to moderate comments
