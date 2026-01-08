---
title: YouTube Comment Moderation
category: platform
platform: youtube
related:
  - ./README.md
  - ./api-guide.md
  - ../../docs/standards-and-metrics.md
---

# YouTube Comment Moderation

## Overview

This document describes moderation capabilities and best practices for YouTube video comments, including what actions are available and how to implement them.

## Available Moderation Actions

### Delete Comment

Remove a comment from a video.

```python
await youtube.moderate_comment(comment_id, "delete")
```

**Effect**:
- Comment is permanently removed
- Cannot be recovered
- Count against rate limits

**Use Cases**:
- Severe policy violations
- Critical abuse content
- Spam or harassment

### Flag Content

Flag content for review (not available via API, internal only).

**Effect**:
- Internal tracking for human review
- No public action

**Use Cases**:
- Ambiguous content
- Content needing review

### Block User

Block user from commenting (channel-level action).

```python
await youtube.block_user(user_id, channel_id)
```

**Effect**:
- User cannot post comments
- Existing comments remain visible
- Can be unblocked

**Use Cases**:
- Repeat offenders
- Severe policy violations
- Persistent harassment

## Moderation Workflow

### Basic Moderation Flow

```python
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

# Initialize components
youtube = YouTubeAPI.from_env()
standards = StandardsEngine()
abuse = AbuseDetector()

# Fetch comment
comment = await youtube.fetch_comment(comment_id)

# Analyze for abuse
abuse_result = abuse.analyze(comment)

# Validate against standards
decision = standards.validate(comment.text)

# Apply moderation action
if abuse_result.is_abuse:
    action = abuse_result.recommended_action
elif decision.action != "approve":
    action = decision.action

# Apply action
if action != "approve":
    await youtube.moderate_comment(comment_id, action)
```

### Automated Moderation Pipeline

```python
async def moderate_video_comments(video_id):
    # Fetch comments
    comments = await youtube.fetch_comments(video_id)
    
    # Analyze in batch
    results = abuse_detector.batch_analyze(comments)
    
    # Moderate each comment
    for comment, result in zip(comments, results):
        # Validate against standards
        decision = standards.validate(comment.text)
        
        # Determine action
        action = "approve"
        if result.is_abuse:
            action = result.recommended_action
        elif decision.action != "approve":
            action = decision.action
        
        # Apply action
        if action != "approve":
            await youtube.moderate_comment(comment.id, action)
```

### Severity-Based Actions

```python
def get_action_for_severity(severity):
    actions = {
        "critical": "delete",
        "high": "delete",
        "medium": "flag",
        "low": "monitor"
    }
    return actions.get(severity, "monitor")
```

## YouTube Platform Rules

### Spam

**Definition**: Unwanted or repetitive content

**Examples of Violations**:
- Self-promotion without disclosure
- Repetitive posting
- Automated behavior
- Link farming
- Unsolicited promotion

**Moderation Action**: Delete

### Harassment

**Definition**: Targeted negative behavior

**Examples of Violations**:
- Repeated targeted insults
- Encouraging others to harass
- Organized harassment campaigns
- Following users across videos

**Moderation Action**: Delete and block

### Hate Speech

**Definition**: Speech targeting protected characteristics

**Protected Characteristics**:
- Race, ethnicity, national origin
- Religion
- Sexual orientation
- Gender identity
- Disability

**Moderation Action**: Delete and block

### Misinformation

**Definition**: False or misleading information

**Note**: YouTube takes action on misinformation

**Moderation Action**: Flag for review or add context

### Sexual Content

**Definition**: Sexually explicit or suggestive content

**Note**: YouTube has strict enforcement

**Moderation Action**: Delete and possibly strike

## Best Practices

### 1. Context Matters

```python
# Analyze with video context
video = await youtube.fetch_video(video_id)

# Analyze comment in context
result = analyzer.analyze_with_video_context(comment, video)
```

### 2. Use Multiple Signals

```python
# Combine multiple analyzers
abuse_result = abuse_detector.analyze(comment)
sentiment_result = sentiment_analyzer.analyze(comment)
category_result = categorizer.analyze(comment)

# Combine results
if abuse_result.is_abuse:
    action = "delete"
elif sentiment_result.sentiment == "negative" and category_result.category == "harassment":
    action = "delete"
```

### 3. Review Edge Cases

```python
# Flag low confidence for human review
result = abuse_detector.analyze(comment)

if result.is_abuse and result.confidence < 0.8:
    # Flag instead of auto-delete
    flag_for_review(comment.id, result)
```

### 4. Provide Reasoning

```python
# Store moderation reasoning
moderation_record = {
    "comment_id": comment.id,
    "action": "delete",
    "reason": result.abuse_type,
    "confidence": result.confidence,
    "evidence": result.evidence
}
```

### 5. Audit Trail

```python
# Track all moderation actions
audit_log = []

async def track_moderation(comment_id, action, reason):
    record = {
        "timestamp": datetime.now().isoformat(),
        "comment_id": comment_id,
        "action": action,
        "reason": reason,
        "moderated_by": "automated"
    }
    audit_log.append(record)
```

## Integration with Moderation AI

### Automated Moderation Bot

```python
import asyncio
from moderation_ai.platforms import YouTubeAPI
from moderation_ai.core import StandardsEngine
from moderation_ai.analysis import AbuseDetector

async def moderation_bot():
    youtube = YouTubeAPI.from_env()
    standards = StandardsEngine()
    abuse = AbuseDetector()
    
    video_id = "abc123"
    
    # Fetch comments
    comments = await youtube.fetch_comments(video_id)
    
    # Analyze and moderate
    for comment in comments:
        abuse_result = abuse.analyze(comment)
        decision = standards.validate(comment.text)
        
        # Determine action
        action = "approve"
        
        if abuse_result.is_abuse:
            action = abuse_result.recommended_action
        elif decision.action != "approve":
            action = decision.action
        
        # Apply moderation
        if action != "approve":
            await youtube.moderate_comment(comment.id, action)
```

## Troubleshooting

### Issue: Cannot Delete Comment

**Possible causes**:
- Not authenticated as video owner
- Comment already removed
- Insufficient permissions

**Solution**:
- Verify you're authenticated as video owner
- Check permissions in Google Cloud Console
- Confirm comment still exists

### Issue: Quota Exceeded

**Possible causes**:
- Too many requests
- Multiple API calls

**Solution**:
- Implement rate limiting
- Use batch operations
- Increase polling interval

## Related Documentation

- **API Guide**: `./api-guide.md` - API usage
- **Standards**: `../../docs/standards-and-metrics.md` - Moderation rules
- **Abuse Detection**: `../../docs/comment-analysis/abuse-detection.md` - Abuse analysis

---

**Last Updated**: January 2024
**Status**: Phase 2 - Documentation Complete
