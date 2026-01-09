# Fetch Comments Example

This example demonstrates how to fetch comments from an Instagram media post.

```python
import asyncio
from moderation_ai.platforms import InstagramAPI
from moderation_ai.core import StandardsEngine

async def fetch_and_analyze_comments():
    """
    Fetch and analyze comments from an Instagram post.
    """
    # Initialize Instagram API
    instagram = InstagramAPI.from_env()
    
    # Initialize moderation engine
    standards = StandardsEngine()
    
    # Media ID to fetch comments from
    media_id = "123456789_456789"
    
    try:
        # Fetch comments
        comments = await instagram.fetch_comments(media_id, limit=50)
        
        print(f"Found {len(comments)} comments")
        
        # Analyze each comment
        for comment in comments:
            # Get moderation decision
            decision = standards.validate(comment.text)
            
            print(f"\nComment by {comment.username}:")
            print(f"  Text: {comment.text}")
            print(f"  Action: {decision.action}")
            print(f"  Confidence: {decision.confidence:.2f}")
            
            if decision.violations:
                print(f"  Violations: {len(decision.violations)}")
                for violation in decision.violations:
                    print(f"    - {violation.standard}: {violation.description}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_and_analyze_comments())
```

## Key Points

1. **Media ID Format**: Instagram media IDs are in format `USERID_MEDIAID`
2. **Pagination**: Comments are paginated with `after` cursor
3. **Rate Limits**: Respect rate limits (5,000 requests/hour)
4. **Error Handling**: Handle network errors and rate limits gracefully

## Output Example

```
Found 25 comments

Comment by user123:
  Text: Great photo! Love the composition
  Action: approve
  Confidence: 0.95
  No violations

Comment by user456:
  Text: This is spam! Check my site spam.com
  Action: hide
  Confidence: 0.82
  Violations: 1
    - spam: Promotional content detected
```

## Related Examples

- `moderate-comment.md` - How to moderate comments
- `track-post.md` - How to track posts for new comments
