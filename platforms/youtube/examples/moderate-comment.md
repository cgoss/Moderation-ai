# YouTube: Moderate Comment Example

This example demonstrates how to moderate a YouTube comment using the Moderation Bot platform adapter.

## Overview

Shows the complete workflow for moderating individual comments on YouTube videos, including:

- Comment analysis
- Violation detection
- Action determination (approve, hide, remove)
- Moderation decision logging

## Prerequisites

- YouTube Data API v3 credentials
- Moderation Bot installed and configured
- Appropriate API permissions for comment management

## Example Code

```python
from moderation_ai import Config, StandardsEngine
from moderation_ai.platforms.youtube import YouTubeAPI
from datetime import datetime

# Initialize configuration
config = Config()

# Set up YouTube credentials
config.youtube.api_key = "your-youtube-api-key"

# Create YouTube API client
youtube_client = YouTubeAPI(config=config.youtube)

# Create moderation engine
moderation_engine = StandardsEngine()

# Example: Moderate a comment
def moderate_youtube_comment():
    """
    Moderate a specific YouTube comment.
    
    Returns:
        ModerationResult with decision and reasoning
    """
    
    # Comment ID from YouTube
    comment_id = "UgxKAnm5s5g6h4a5g466g4"
    
    # Fetch the comment
    comment = youtube_client.fetch_comment(comment_id)
    
    if not comment:
        print(f"Comment {comment_id} not found")
        return None
    
    # Analyze the comment
    moderation_result = moderation_engine.moderate(comment)
    
    # Display results
    print(f"Comment ID: {comment.id}")
    print(f"Comment Text: {comment.text[:100]}...")
    print(f"Author: {comment.author_name}")
    print(f"\n--- Moderation Decision ---")
    print(f"Action: {moderation_result.action.value}")
    print(f"Score: {moderation_result.score:.2f}")
    print(f"Confidence: {moderation_result.confidence:.2f}")
    
    if moderation_result.has_violations:
        print(f"\nViolations Found: {len(moderation_result.violations)}")
        for violation in moderation_result.violations:
            print(f"  - {violation.standard}: {violation.description}")
            print(f"    Severity: {violation.severity.value}")
            print(f"    Confidence: {violation.confidence:.2f}")
    else:
        print("No violations found")
    
    print(f"\nReasoning: {moderation_result.reasoning}")
    
    # Execute moderation action
    if moderation_result.action != "approve":
        youtube_client.moderate_comment(
            comment_id=comment.id,
            action=moderation_result.action.value
        )
        print(f"\nAction executed: {moderation_result.action.value}")
    
    return moderation_result

# Example usage with different comment types
def examples():
    """Examples of moderating different types of comments."""
    
    # Clean comment
    clean_comment = Comment(
        id="1",
        text="This is a helpful and constructive comment.",
        author_id="user123",
        author_name="HelpfulUser",
        created_at=datetime.utcnow(),
        platform="youtube",
        post_id="video123"
    )
    
    result = moderation_engine.moderate(clean_comment)
    print(f"Clean comment action: {result.action.value}")
    
    # Violation comment (profanity)
    violation_comment = Comment(
        id="2",
        text="This is stupid and worthless content!",
        author_id="user456",
        author_name="AbusiveUser",
        created_at=datetime.utcnow(),
        platform="youtube",
        post_id="video123"
    )
    
    result = moderation_engine.moderate(violation_comment)
    print(f"\nViolation comment action: {result.action.value}")
    print(f"Violations: {[v.standard for v in result.violations]}")

if __name__ == "__main__":
    # Run the example
    moderate_youtube_comment()
    
    # Show examples
    print("\n" + "="*50)
    print("Examples of different comment types:")
    print("="*50)
    examples()
```

## Workflow

1. **Initialize** - Configure YouTube API credentials
2. **Fetch** - Retrieve the comment from YouTube
3. **Analyze** - Run comment through moderation engine
4. **Decide** - Get recommended action based on violations
5. **Execute** - Apply moderation action to YouTube
6. **Log** - Record decision and reasoning

## Moderation Actions

| Action | Description | When Used |
|--------|-------------|-----------|
| `approve` | Comment passes all standards | No violations found |
| `flag` | Mark for human review | Low-medium severity, uncertain |
| `hide` | Hide from public view | Medium-high severity |
| `remove` | Delete comment | High severity, clear violations |

## Moderation Standards

The moderation engine evaluates against these standards:

1. **Safety** - Harmful, dangerous, or illegal content
2. **Quality** - Spam, low-quality, or irrelevant
3. **Policy** - Platform policy violations
4. **Engagement** - Constructive vs. destructive
5. **Abuse** - Personal attacks, harassment, bullying

## YouTube API Limitations

- Comment moderation requires `moderator` permissions on the channel
- Cannot modify comments on other creators' videos
- Rate limits apply to API calls (10,000 units/day default)
- Deleted comments cannot be restored

## Error Handling

```python
from moderation_ai.utils.error_handler import (
    RateLimitError,
    AuthenticationError,
    PlatformError
)

try:
    result = moderate_youtube_comment()
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except PlatformError as e:
    print(f"YouTube API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

1. **Review before removing** - Use `flag` action for uncertain cases
2. **Document decisions** - Keep moderation log for accountability
3. **Appeal process** - Allow users to contest moderation
4. **Consistency** - Apply standards uniformly across all comments
5. **Transparency** - Provide clear reasoning for moderation actions

## Related Examples

- [Fetch Comments](fetch-comments.md) - Getting comments from YouTube
- [Track Post](track-post.md) - Monitoring new comments on videos

## Next Steps

- Batch moderation of multiple comments
- Automate moderation workflows
- Integrate with content review queue
- Add analytics and reporting

---

**Platform**: YouTube  
**Example**: Moderate Comment  
**Phase**: 2 - Tier 1 Platform Documentation  
**Status**: ✅ Complete
