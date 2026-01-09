# Moderate Comment Example

This example demonstrates how to moderate Instagram comments using the moderation engine.

```python
import asyncio
from moderation_ai.platforms import InstagramAPI
from moderation_ai.core import StandardsEngine

async def moderate_comments():
    """
    Moderate Instagram comments with automatic actions.
    """
    # Initialize Instagram API
    instagram = InstagramAPI.from_env()
    
    # Initialize moderation engine with auto-moderation enabled
    standards = StandardsEngine(auto_moderate=True, threshold=0.7)
    
    # Media ID to moderate
    media_id = "123456789_456789"
    
    # Fetch comments
    comments = await instagram.fetch_comments(media_id, limit=100)
    
    results = {
        'approved': 0,
        'flagged': 0,
        'hidden': 0,
        'removed': 0
    }
    
    for comment in comments:
        # Analyze comment
        decision = standards.validate(comment.text)
        
        # Apply moderation action based on decision
        if decision.action == "approve":
            results['approved'] += 1
            
        elif decision.action == "flag":
            results['flagged'] += 1
            # Flag for review (internal)
            print(f"Flagged comment {comment.id}: {decision.reasoning}")
            
        elif decision.action == "hide":
            results['hidden'] += 1
            try:
                await instagram.moderate_comment(comment.id, "hide", reason=decision.reasoning)
                print(f"Hidden comment {comment.id}")
            except Exception as e:
                print(f"Failed to hide comment {comment.id}: {e}")
        
        elif decision.action == "remove":
            # Remove option available for own comments
            if comment.is_own_comment:
                results['removed'] += 1
                try:
                    await instagram.moderate_comment(comment.id, "delete", reason=decision.reasoning)
                    print(f"Removed comment {comment.id}")
                except Exception as e:
                    print(f"Failed to remove comment {comment.id}: {e}")
    
    # Print summary
    print("\n=== Moderation Summary ===")
    print(f"Total comments processed: {len(comments)}")
    print(f"Approved: {results['approved']}")
    print(f"Flagged for review: {results['flagged']}")
    print(f"Hidden: {results['hidden']}")
    print(f"Removed: {results['removed']}")

if __name__ == "__main__":
    asyncio.run(moderate_comments())
```

## Moderation Actions

| Action | When to Use | API Method |
|---------|--------------|------------|
| **approve** | No violations | No action needed |
| **flag** | Minor violations | Internal tracking only |
| **hide** | Moderate violations | `moderate_comment(id, "hide")` |
| **delete** | Severe violations (own comments) | `moderate_comment(id, "delete")` |

## Best Practices

1. **Review flagged comments**: Always review before taking action
2. **Provide reasons**: Document why action was taken
3. **Respect rate limits**: Don't exceed API limits
4. **Handle errors gracefully**: Log moderation failures
5. **Keep audit trail**: Track all moderation actions

## Error Handling

```python
try:
    await instagram.moderate_comment(comment_id, "hide")
except RateLimitError as e:
    # Wait and retry
    await asyncio.sleep(e.retry_after)
    await instagram.moderate_comment(comment_id, "hide")
except AuthenticationError as e:
    # Re-authenticate
    instagram = InstagramAPI.from_env()
except PlatformError as e:
    # Log and skip
    print(f"Platform error: {e}")
```

## Related Examples

- `fetch-comments.md` - How to fetch comments
- `track-post.md` - How to monitor for new comments
